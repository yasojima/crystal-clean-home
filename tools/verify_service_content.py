"""Audit cross-page review variety and the photographs actually used by services."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'source/service-pages'
SITE = ROOT / 'source/site'
catalogue = json.loads((DATA / 'catalogue.json').read_text(encoding='utf-8'))
copy = json.loads((DATA / 'copy.json').read_text(encoding='utf-8'))
voices = json.loads((DATA / 'voices.json').read_text(encoding='utf-8'))
assets = json.loads((DATA / 'scene-assets.json').read_text(encoding='utf-8'))
comparisons = json.loads((DATA / 'aircon-comparisons.json').read_text(encoding='utf-8'))
comparisons.update(json.loads((DATA / 'service-comparisons.json').read_text(encoding='utf-8')))
errors, records = [], []
image_uses = defaultdict(list)
longest_positions, rating_distributions, demographic_orders = Counter(), Counter(), Counter()
first_long_positions, avatar_orders, rating_orders = Counter(), Counter(), Counter()
all_reviews = [review for page in voices['pages'].values() for review in page]
long_counts, age_counts, gender_counts = Counter(), Counter(), Counter()
low_reviews = []

if voices.get('purpose') != 'fictional-client-demo':
    errors.append('review purpose is not the approved client demonstration')
for field in ('nickname', 'title', 'body'):
    if len({r[field] for r in all_reviews}) != len(all_reviews):
        errors.append(f'duplicate review {field}')
if set(copy['details']) != {r for r in catalogue['pages'] if '/' in r}:
    errors.append('detail-specific concern coverage')

known_images = {v['asset']: v for v in assets.values()}
comparison_images = {v[state] for v in comparisons.values() for state in ('before', 'after')}
for route, page in catalogue['pages'].items():
    reviews = voices['pages'][route]
    if len(reviews) != 6 or any(r['rating'] not in (1, 2, 3, 4, 5) for r in reviews):
        errors.append(f'{route}: review count or rating')
    lengths = [len(r['body']) for r in reviews]
    first_long = next((i + 1 for i, length in enumerate(lengths) if length >= 120), None)
    long_counts[sum(length >= 120 for length in lengths)] += 1
    age_counts[len({r['demographic'][:2] for r in reviews})] += 1
    gender_counts[sum('男性' in r['demographic'] for r in reviews)] += 1
    low_reviews.extend({'route': route, 'position': i + 1, 'rating': r['rating'], 'title': r['title'], 'body': r['body']}
                       for i, r in enumerate(reviews) if r['rating'] < 3)
    if not any(length >= 120 for length in lengths) or not any(length < 90 for length in lengths):
        errors.append(f'{route}: missing contrast between substantial and short/medium reviews')
    first_long_positions[str(first_long) if first_long is not None else 'none'] += 1
    avatar_orders[tuple(r['avatar'] for r in reviews)] += 1
    longest = max(range(len(lengths)), key=lengths.__getitem__) + 1
    longest_positions[longest] += 1
    ratings = [r['rating'] for r in reviews]
    rating_orders[tuple(ratings)] += 1
    rating_distributions[tuple(sorted(ratings))] += 1
    demographic_orders[tuple(r['demographic'] for r in reviews)] += 1
    for review in reviews:
        if not review['avatar'].startswith('woman-' if '女性' in review['demographic'] else 'man-'):
            errors.append(f'{route}: avatar does not match review demographic')
    doc = BeautifulSoup((SITE / 'house-cleaning' / route / 'index.html').read_text(encoding='utf-8'), 'html.parser')
    main = doc.select_one('main[data-service-layout="shared-v2"]')
    photos = sorted({i['src'] for i in main.select('img[src*="/service-scenes/"]')})
    for photo in photos:
        image_uses[photo].append(route)
        file = SITE / photo.lstrip('/')
        if not file.is_file():
            errors.append(f'{route}: missing photograph {photo}')
        elif photo in known_images and hashlib.sha256(file.read_bytes()).hexdigest() != known_images[photo]['sha256']:
            errors.append(f'{route}: photograph metadata mismatch {photo}')
        elif photo not in known_images and photo not in comparison_images:
            errors.append(f'{route}: unregistered photograph {photo}')
    concerns = copy['details'][route]['concerns'] if '/' in route else copy['categories'][page['category']]['concerns']
    actual_concerns = [n.get_text(strip=True) for n in main.select('.c-issue-card__text')]
    if actual_concerns != [''.join(pair) for pair in concerns]:
        errors.append(f'{route}: concern copy does not match the service')
    if '/' in route:
        heading = copy['details'][route].get('heading')
        expected = ''.join([*heading[:-1], heading[-1].rstrip('！!') + '！']) if heading else ''
        if not heading or len(heading) != 2 or main.select_one('.p-content-box__heading').get_text(strip=True) != expected:
            errors.append(f'{route}: missing or mismatched service-specific photo heading')
    primary = page['groups'][0]['products'][0]
    subjects = [primary] if '/' in route else copy['categories'][page['category']]['subjects']
    if [n.get_text(strip=True) for n in main.select('#service-introduction .c-tab__button')] != [copy['products'][key]['short'] for key in subjects]:
        errors.append(f'{route}: photo tab omits part of the service name')
    records.append({
        'route': route, 'title': page['title'], 'concerns': concerns,
        'nickname_order': [r['nickname'] for r in reviews],
        'demographic_order': [r['demographic'] for r in reviews],
        'ratings': ratings, 'body_lengths': lengths, 'longest_position': longest,
        'first_120_character_review_position': first_long,
        'avatar_order': [r['avatar'] for r in reviews],
        'review_titles': [r['title'] for r in reviews], 'photos': photos,
        'product_scenes': [{
            'product_id': key, 'subject': copy['products'][key]['short'],
            'scene': copy['products'][key]['scene'], 'focus': copy['products'][key]['focus']
        } for group in page['groups'] for key in group['products']]
    })

if len(longest_positions) != 6 or max(longest_positions.values()) > len(records) / 3:
    errors.append('long reviews are concentrated in the same position')
if len(rating_distributions) < 3 or max(rating_distributions.values()) > len(records) / 2:
    errors.append('star distributions are concentrated in the same pattern')
if max(demographic_orders.values()) > 1:
    errors.append('repeated demographic sequence')
if not 1 <= len(low_reviews) <= 3:
    errors.append('one to three low-rated demo examples required across the whole site')
if len(long_counts) < 3 or len(age_counts) < 3 or len(gender_counts) < 3:
    errors.append('review length counts or demographic mixes remain uniform')

report = {
    'checked_at': datetime.now(timezone.utc).isoformat(), 'pages': len(records),
    'reviews': len(all_reviews), 'purpose': voices['purpose'],
    'longest_positions': dict(sorted(longest_positions.items())),
    'first_long_review_positions': dict(sorted(first_long_positions.items())),
    'long_review_threshold_characters': 120,
    'long_reviews_per_page_distribution': dict(sorted(long_counts.items())),
    'distinct_age_groups_per_page_distribution': dict(sorted(age_counts.items())),
    'male_reviews_per_page_distribution': dict(sorted(gender_counts.items())),
    'low_rated_examples': low_reviews,
    'unique_avatar_orders': len(avatar_orders),
    'unique_rating_orders': len(rating_orders),
    'rating_distributions': [{'ratings': list(k), 'pages': v} for k, v in sorted(rating_distributions.items())],
    'demographics': dict(sorted(Counter(r['demographic'] for r in all_reviews).items())),
    'body_length_range': [min(len(r['body']) for r in all_reviews), max(len(r['body']) for r in all_reviews)],
    'active_scene_photos': len(set(image_uses) - comparison_images),
    'preserved_comparison_photos': len(set(image_uses) & comparison_images),
    'photo_uses': dict(sorted(image_uses.items())), 'pages_detail': records,
    'errors': errors, 'passed': not errors,
    'limits': 'Numbers and source agreement are checked here; visual relevance and review tone are checked in saved browser screens.'
}
out = ROOT / 'evidence/2026-10-04/local/service-content-balance.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
print(json.dumps({key: report[key] for key in ('pages', 'reviews', 'longest_positions', 'rating_distributions', 'active_scene_photos', 'preserved_comparison_photos', 'errors', 'passed')}, ensure_ascii=False))
raise SystemExit(bool(errors))
