"""Publish isolated homepage components from their shared source templates."""
from pathlib import Path
import re
import shutil
import hashlib
import json
from bs4 import BeautifulSoup
from card_copy import apply_card_copy
from copywriting import text_id

def homepage_questions(root):
    source = BeautifulSoup((root / 'source/qa/index.html').read_text(encoding='utf-8'), 'html.parser')
    copy = json.loads((root / 'copy/ja.json').read_text(encoding='utf-8'))
    section = BeautifulSoup('<section id="cch-faq" aria-labelledby="cch-faq-heading"><div class="cch-faq-inner"><h2 id="cch-faq-heading">よくあるご質問</h2><div class="cch-faq-list"></div></div></section>', 'html.parser')
    for number, item in enumerate(source.select('.sec_qa .area_qa-list dl'), 1):
        details = section.new_tag('details')
        summary = section.new_tag('summary')
        label = section.new_tag('span', attrs={'class': 'cch-faq-number'})
        label.string = f'Q{number}.'
        summary.append(label)
        for tag, target in [('dt', summary), ('dd', section.new_tag('div', attrs={'class': 'cch-faq-answer'}))]:
            original = item.find(tag).get_text(' ', strip=True)
            value = copy.get(text_id(original), original).replace('イエキレ', 'クリスタルクリーンホーム')
            text = section.new_tag('span')
            text.string = value
            target.append(text)
            details.append(target)
        section.select_one('.cch-faq-list').append(details)
    if len(section.select('details')) != 11:
        raise ValueError('Expected 11 homepage questions')
    return str(section)

def publish_home_sections(root):
    target = root / 'docs/index.html'
    text = target.read_text(encoding='utf-8')
    for name, old in [('estimate-cta', 'sec_corona'), ('service-cards', 'sec_service'), ('reasons', 'unused_reasons'), ('prevention', 'unused_prevention'), ('service-directory', 'unused_directory')]:
        if name == 'reasons' and '<!-- cch-reasons' not in text:
            text = text.replace('<section class="sec_area">', '<!-- cch-reasons -->\n<section class="sec_area">', 1)
        if name in ('prevention', 'service-directory') and f'<!-- cch-{name}' not in text:
            text = text.replace('</main>', f'<!-- cch-{name} -->\n</main>', 1)
        component = root / 'brand' / name
        markup = (component / 'template.html').read_text(encoding='utf-8')
        if name == 'prevention':
            markup = homepage_questions(root)
        fragment = BeautifulSoup(markup, 'html.parser')
        apply_card_copy(fragment)
        markup = str(fragment)
        pattern = rf'<!-- cch-{name}:start -->.*?<!-- cch-{name}:end -->|<!-- cch-{name} -->|<section class="{old}">.*?</section>'
        text, count = re.subn(pattern, lambda _: f'<!-- cch-{name}:start -->{markup}<!-- cch-{name}:end -->', text, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f'Missing homepage component {name}')
        text = re.sub(rf'<link[^>]*data-home-component="{name}"[^>]*>\s*', '', text)
        style_source = ''.join((root / 'source/device' / device / 'css/brand' / name / 'style.css').read_text(encoding='utf-8') for device in ('desktop', 'mobile'))
        version = hashlib.sha256(style_source.encode()).hexdigest()[:12]
        text = text.replace('</head>', f'<link rel="stylesheet" href="/crystal-clean-home/brand/{name}/style.css?v={version}" data-home-component="{name}">\n</head>')
        shutil.copytree(component, root / 'docs/brand' / name, dirs_exist_ok=True)
    text = re.sub(r'<link[^>]*data-home-font="true"[^>]*>\s*', '', text)
    for cls in ['sec_info', 'sec_point']:
        text = re.sub(rf'<section class="{cls}">.*?</section>\s*', '', text, flags=re.S)
    # Reuse the exact same estimate CTA at the lower service-directory entry.
    text = re.sub(r'<!-- cch-estimate-bottom:start -->.*?<!-- cch-estimate-bottom:end -->', '', text, flags=re.S)
    lower_cta = (root / 'brand/estimate-cta/template.html').read_text(encoding='utf-8').replace('id="cch-estimate-cta"', 'id="cch-estimate-cta-bottom"')
    text = text.replace('<!-- cch-service-directory:start -->', '<!-- cch-estimate-bottom:start -->' + lower_cta + '<!-- cch-estimate-bottom:end --><!-- cch-service-directory:start -->', 1)
    target.write_text(text, encoding='utf-8')

if __name__ == '__main__':
    publish_home_sections(Path(__file__).resolve().parent)
