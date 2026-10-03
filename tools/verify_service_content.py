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
errors, records = [], []
image_uses = defaultdict(list)
longest_positions, rating_distributions, demographic_orders = Counter(), Counter(), Counter()
all_reviews = [review for page in voices['pages'].values() for review in page]

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
    if len(reviews) != 6 or any(r['rating'] not in (3, 4, 5) for r in reviews):
        errors.append(f'{route}: review count or rating')
    lengths = [len(r['body']) for r in reviews]
    longest = max(range(len(lengths)), key=lengths.__getitem__) + 1
    longest_positions[longest] += 1
    ratings = [r['rating'] for r in reviews]
    rating_distributions[tuple(sorted(ratings))] += 1
    demographic_orders[tuple(r['demographic'] for r in reviews)] += 1
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
    records.append({
        'route': route, 'title': page['title'], 'concerns': concerns,
        'nickname_order': [r['nickname'] for r in reviews],
        'demographic_order': [r['demographic'] for r in reviews],
        'ratings': ratings, 'body_lengths': lengths, 'longest_position': longest,
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

report = {
    'checked_at': datetime.now(timezone.utc).isoformat(), 'pages': len(records),
    'reviews': len(all_reviews), 'purpose': voices['purpose'],
    'longest_positions': dict(sorted(longest_positions.items())),
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
