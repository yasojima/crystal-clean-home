"""Publish one shared header, with optional per-page extension assets."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import html, json, re, shutil

def publish_header(root):
    config = json.loads((root/'brand/site.json').read_text(encoding='utf-8-sig'))
    component = root/'brand/header'
    output = root/'docs/brand/header'
    output.mkdir(parents=True, exist_ok=True)
    template = (component/'template.html').read_text(encoding='utf-8')
    extensions = json.loads((component/'pages.json').read_text(encoding='utf-8'))
    manifest = json.loads((root/'capture.json').read_text(encoding='utf-8'))
    paths = sorted({Path(f['path']).as_posix() for f in manifest['files'] if f.get('html') and not f['path'].startswith('vendor/')})
    for name in ('style.css', 'desktop.css', 'mobile.css', 'script.js', 'typography.css', 'section-triangles.svg', 'category-cards.css'):
        shutil.copy2(component/name, output/name)
    for asset in {a for entry in extensions.values() for a in entry.get('styles', [])+entry.get('scripts', [])}:
        source = (component/asset).resolve()
        if not source.is_relative_to(component.resolve()):
            raise ValueError('Header extension must remain within brand/header/')
        dest = output/asset
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    for common in (root/'docs/wp/wp-content/themes/original_theme/js').glob('common*.js'):
        text = common.read_text(encoding='utf-8')
        text = re.sub(r'\A// header.*?(?=//animetion)', '', text, count=1, flags=re.S)
        text = re.sub(r'// gnav\s.*?(?=// scroll)', '', text, count=1, flags=re.S)
        common.write_text(text, encoding='utf-8')
    def update(path):
        target = root/'docs'/path
        text = target.read_text(encoding='utf-8')
        header = template.replace('{{logo_tag}}', 'h1' if path == 'index.html' else 'div')
        for key in ('nameJa', 'phone', 'hours'):
            header = header.replace('{{'+key+'}}', html.escape(config[key], quote=True))
        text, count = re.subn(r'<header\b[^>]*>.*?</header>', lambda _: header, text, count=1, flags=re.S|re.I)
        if count != 1:
            raise ValueError('Missing header: '+path)
        text = re.sub(r'<(?:link|script)\b[^>]*\bdata-shared-header=["\'][^"\']*["\'][^>]*>(?:</script>)?\s*', '', text, flags=re.I)
        tags = '<link rel="stylesheet" href="/crystal-clean-home/brand/header/style.css?v=20260923-3" data-shared-header="style">\n<link rel="stylesheet" href="/crystal-clean-home/brand/header/desktop.css?v=1" media="(min-width:993px)" data-shared-header="desktop">\n<link rel="stylesheet" href="/crystal-clean-home/brand/header/mobile.css?v=1" media="(max-width:992px)" data-shared-header="mobile">\n<script defer src="/crystal-clean-home/brand/header/script.js?v=1" data-shared-header="script"></script>\n'
        entry = extensions.get(path, {})
        for asset in entry.get('styles', []):
            tags += '<link rel="stylesheet" href="/crystal-clean-home/brand/header/'+html.escape(asset, quote=True)+'" data-shared-header="extension">\n'
        for asset in entry.get('scripts', []):
            tags += '<script defer src="/crystal-clean-home/brand/header/'+html.escape(asset, quote=True)+'" data-shared-header="extension"></script>\n'
        text = re.sub(r'</head>', lambda _: tags+'</head>', text, count=1, flags=re.I)
        text = re.sub(r'(href=["\'][^"\']*/(?:style--[^/"\'?]+|mitsumori--[^/"\'?]+)\.css)(?:\?[^"\']*)?', r'\1?layout=1', text)
        text = re.sub(r'<div id="breadcrumb"[^>]*>.*?</div>', '<div id="breadcrumb" class="cch-header-band" aria-hidden="true"></div>', text, flags=re.S)
        text = re.sub(r'(src=["\'][^"\']*/js/common[^"\'?]*\.js)(?:\?[^"\']*)?', r'\1?header=1', text)
        target.write_text(text, encoding='utf-8')
    with ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(update, paths))
    return len(paths)
