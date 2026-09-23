"""Publish the homepage-only reference hero, keeping all other page markup intact."""
from pathlib import Path
import html
import json
import re
import shutil


def publish_hero(root):
    component = root / 'brand/hero'
    video = json.loads((component / 'video.json').read_text(encoding='utf-8'))
    src = ' src="' + html.escape(video['src'], quote=True) + '"' if video['src'] else ''
    hidden = ' hidden' if src else ''
    markup = '<section id="cch-hero" aria-label="サービスイメージ動画">'
    markup += '<video class="cch-hero-video" muted loop playsinline preload="metadata" poster="' + html.escape(video['poster'], quote=True) + '"' + src + ' aria-label="サービスイメージ"></video>'
    markup += '<div class="cch-video-caption"' + hidden + '><span>' + html.escape(video['label']) + '</span><small>IMAGE VIDEO</small></div>'
    markup += '<button class="cch-video-toggle" type="button" hidden>動画を再生</button><a class="cch-hero-scroll" href="#cch-estimate-cta">SCROLL DOWN</a></section>'
    target = root / 'docs/index.html'
    text = target.read_text(encoding='utf-8')
    pattern = r'<!-- cch-hero:start -->.*?<!-- cch-hero:end -->|<div class="hero">.*?</div>'
    text, count = re.subn(pattern, lambda _: '<!-- cch-hero:start -->\n' + markup + '\n<!-- cch-hero:end -->', text, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Homepage hero boundary not found')
    text = re.sub(r'<(?:link|script)\b[^>]*data-home-hero="[^"]*"[^>]*>(?:</script>)?\s*', '', text)
    tags = '<link rel="stylesheet" href="/crystal-clean-home/brand/hero/video.css?v=frame1" data-home-hero="style">\n'
    tags += '<script defer src="/crystal-clean-home/brand/hero/script.js?v=frame1" data-home-hero="script"></script>\n'
    text = text.replace('</head>', tags + '</head>', 1)
    target.write_text(text, encoding='utf-8')
    shutil.copytree(component, root / 'docs/brand/hero', dirs_exist_ok=True)
    return 1
