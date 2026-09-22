"""Publish the homepage-only reference hero, keeping all other page markup intact."""
from pathlib import Path
import html
import json
import re
import shutil


def publish_hero(root):
    component = root / 'brand/hero'
    slides = json.loads((component / 'slides.json').read_text(encoding='utf-8'))
    markup = '<div id="cch-hero" class="main_visual" aria-label="サービスイメージ">\n'
    for index, slide in enumerate(slides):
        priority = ' fetchpriority="high"' if index == 0 else ''
        markup += '<div class="main_visual_item js-imgScale"><div class="main_visual_image"><picture><img src="' + html.escape(slide['image'], quote=True) + '" alt="' + html.escape(slide['alt'], quote=True) + '" decoding="async"' + priority + '></picture></div></div>\n'
    markup += '</div>'
    target = root / 'docs/index.html'
    text = target.read_text(encoding='utf-8')
    pattern = r'<!-- cch-hero:start -->.*?<!-- cch-hero:end -->|<div class="hero">.*?</div>'
    text, count = re.subn(pattern, lambda _: '<!-- cch-hero:start -->\n' + markup + '\n<!-- cch-hero:end -->', text, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Homepage hero boundary not found')
    text = re.sub(r'<(?:link|script)\b[^>]*data-home-hero="[^"]*"[^>]*>(?:</script>)?\s*', '', text)
    tags = ''
    for device, media in [('desktop', '(min-width:993px)'), ('mobile', '(max-width:992px)')]:
        tags += f'<link rel="stylesheet" href="/crystal-clean-home/brand/hero/{device}.css?v=6" media="{media}" data-home-hero="{device}">\n'
    for asset in ['vendor/lenis.min.js', 'vendor/gsap.min.js', 'vendor/scrolltrigger.min.js', 'script.js']:
        tags += f'<script defer src="/crystal-clean-home/brand/hero/{asset}?v=6" data-home-hero="script"></script>\n'
    text = text.replace('</head>', tags + '</head>', 1)
    target.write_text(text, encoding='utf-8')
    shutil.copytree(component, root / 'docs/brand/hero', dirs_exist_ok=True)
    return 1
