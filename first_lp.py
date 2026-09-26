"""Publish the first-visit manga LP; text remains visible static HTML."""
from pathlib import Path
import hashlib
import re
import shutil
from io_retry import write_text

BASE = '/crystal-clean-home/'
PUBLIC = 'https://yasojima.github.io' + BASE


def publish_first_lp(root):
    root = Path(root)
    template = root / 'brand/first-lp/template.html'
    if not template.exists():
        return
    main = template.read_text(encoding='utf-8').strip()
    cta = (root / 'brand/estimate-cta/template.html').read_text(encoding='utf-8').strip()
    for index in range(1, 5):
        instance = cta.replace('id="cch-estimate-cta"', f'id="first-estimate-{index}" class="cch-lp-cta"')
        main = main.replace(f'{{{{CTA_{index}}}}}', instance)
    out = root / 'docs/brand/first-lp'
    out.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root / 'brand/first-lp/images', out / 'images', dirs_exist_ok=True)
    links = []
    for platform in ('desktop', 'mobile'):
        # Share the accepted CTA source rather than creating another button design.
        css = (root / f'source/device/{platform}/css/brand/estimate-cta/style.css').read_text(encoding='utf-8')
        css = css.replace(':is(#cch-estimate-cta,#cch-estimate-cta-bottom)', '#cch-first-lp .cch-lp-cta')
        css += '\n' + (root / f'source/device/{platform}/css/first-lp.css').read_text(encoding='utf-8')
        revision = hashlib.sha256(css.encode()).hexdigest()[:12]
        write_text(out / f'{platform}.css', css)
        media = '(min-width: 993px)' if platform == 'desktop' else '(max-width: 992px)'
        links.append(f'<link rel="stylesheet" href="{BASE}brand/first-lp/{platform}.css?v={revision}" media="{media}" data-cch-first-lp>')
    for relative in ('source/first/index.html', 'docs/first/index.html'):
        page = root / relative
        text = page.read_text(encoding='utf-8')
        text, count = re.subn(r'<main class="main_contents">.*?</main>', lambda _: main, text, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f'Missing first main in {relative}')
        text = re.sub(r'(class="page_container)(?![^"\n]*\bcch-first-lp-page\b)', r'\1 cch-first-lp-page', text, count=1)
        text = re.sub(r'<link\b[^>]*data-cch-first-lp[^>]*>', '', text)
        text = re.sub(r'<title>.*?</title>', '<title>初めての方へ｜安心して相談できるハウスクリーニング｜クリスタルクリーンホーム</title>', text, count=1, flags=re.S)
        text = re.sub(r'<meta\b[^>]*(?:name=["\']description["\']|property=["\']og:[^"\']+["\'])[^>]*>', '', text)
        text = re.sub(r'<link\b[^>]*rel=["\']canonical["\'][^>]*>', '', text)
        desc = '初めてのハウスクリーニングを漫画でご案内。清掃方法の選定、作業前の説明、住まいの保護、衛生管理と仕上がり確認への取り組みをご紹介します。'
        metadata = f'<meta name="description" content="{desc}"><link rel="canonical" href="{PUBLIC}first/"><meta property="og:title" content="初めての方へ｜クリスタルクリーンホーム"><meta property="og:description" content="{desc}"><meta property="og:type" content="website"><meta property="og:url" content="{PUBLIC}first/"><meta property="og:image" content="{PUBLIC}brand/first-lp/images/hero.webp">'
        text = re.sub(r'\s*</head>', lambda _: '\n' + metadata + '\n'.join(links) + '\n</head>', text, count=1)
        if relative.startswith('source/'):
            # source/** is stored verbatim by Git; preserve its LF line endings.
            page.write_bytes(re.sub(r'[ \t]+$', '', text, flags=re.M).encode('utf-8'))
        else:
            write_text(page, text)


if __name__ == '__main__':
    from shared_ui import publish_shared_ui
    publish_shared_ui(Path(__file__).resolve().parent)
