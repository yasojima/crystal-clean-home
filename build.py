from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from bs4 import BeautifulSoup, Comment
import json, re, shutil, base64, html, sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source'
OUT = ROOT / 'docs'
BASE = '/crystal-clean-home/'
brand = json.loads((ROOT / 'brand/site.json').read_text(encoding='utf-8-sig'))
manifest = json.loads((ROOT / 'capture.json').read_text(encoding='utf-8'))
files = [f for f in manifest['files'] if 'path' in f]
def published_path(f):
    return f['path'] + ('.css' if 'css' in f['type'] and not f['path'].endswith('.css') else '')

mapping = {f['url']: published_path(f) for f in files}
for f in files:
    mapping.setdefault(f.get('resolved', f['url']), published_path(f))

def local_url(value, origin):
    if not value or value.startswith(('#', 'data:', 'javascript:', 'mailto:')):
        return value
    if value.startswith('tel:'):
        return 'tel:' + brand['phone']
    parsed = urlsplit(urljoin(origin, value))
    host = parsed.netloc.replace('www.iekire.com', 'iekire.com')
    key = urlunsplit(('https' if host == 'iekire.com' else parsed.scheme, host, parsed.path or '/', parsed.query, ''))
    target = mapping.get(key)
    if target:
        if target.endswith('/index.html'):
            target = target[:-10]
        elif target == 'index.html':
            target = ''
        return BASE + target + ('#' + parsed.fragment if parsed.fragment else '')
    return value

def css_urls(text, origin):
    return re.sub(r'url\(\s*([\"\']?)([^\)\"\']+)\1\s*\)', lambda m: 'url("' + local_url(m[2].strip(), origin) + '")', text)

def absolute_urls(text):
    return re.sub(r'https?://[^\s\"\'<>\\)]+', lambda m: local_url(m[0], 'https://iekire.com/'), text)

def identity(text):
    text = text.replace('イエキレ', brand['nameJa']).replace('株式会社康栄クリーンアップ', brand['nameJa'])
    text = text.replace('0120-155-082', brand['phone']).replace('0120155082', brand['phone'])
    text = re.sub(r'受付時間\s*平日\s*8:30[～〜~]17:30', brand['hours'], text)
    text = re.sub(r'平日\s*8:30[～〜~]17:30', '8：00～17:00(年中無休) ※年末年始を除く', text)
    return text

def tab_identity(markup):
    def update_head(match):
        head = match[2]
        title = '<title>' + html.escape(brand['name']) + '</title>'
        if re.search(r'<title\b', head, re.I):
            head = re.sub(r'<title\b[^>]*>.*?</title>', lambda _: title, head, flags=re.I | re.S)
        else:
            head += title
        def remove_icon(match):
            link = BeautifulSoup(match[0], 'html.parser').find('link')
            rel = link.get('rel', []) if link else []
            return '' if any('icon' in value.lower() for value in rel) else match[0]
        head = re.sub(r'<link\b[^>]*>', remove_icon, head, flags=re.I)
        icon = BASE + 'brand/crystal-clean-home.png'
        head += f'<link rel="icon" type="image/png" href="{icon}"><link rel="apple-touch-icon" href="{icon}">\n'
        return match[1] + head + match[3]
    return re.sub(r'(<head\b[^>]*>)(.*?)(</head>)', update_head, markup, count=1, flags=re.I | re.S)

if '--tabs-only' in sys.argv:
    count = 0
    for f in files:
        if not f.get('html'):
            continue
        dest = OUT / published_path(f)
        markup = dest.read_text(encoding='utf-8')
        updated = tab_identity(markup)
        if updated != markup:
            dest.write_text(updated, encoding='utf-8')
            count += 1
    print(json.dumps({'tabPagesUpdated': count}))
    sys.exit(0)

OUT.mkdir(exist_ok=True)
stats = {'pages': 0, 'resources': 0, 'forms': 0, 'referenceErrors': manifest['errors']}
for f in ([] if '--assets-only' in sys.argv else files):
    src = SOURCE / f['path']
    dest = OUT / published_path(f)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if f.get('html'):
        soup = BeautifulSoup(src.read_text(encoding='utf-8-sig'), 'html.parser')
        for n in soup.find_all(['script', 'iframe']):
            if re.search(r'googletagmanager|google-analytics|gtag\(', str(n)):
                n.decompose()
        for n in soup.find_all(True):
            for attr in ['href', 'src', 'poster', 'data-src', 'data-original', 'data-lazy-src', 'action']:
                if n.get(attr):
                    n[attr] = local_url(n[attr], f['url'])
            for attr in ['srcset', 'data-srcset']:
                value = n.get(attr, '')
                if value and not value.startswith('data:'):
                    n[attr] = ', '.join(local_url(p.split()[0], f['url']) + (' ' + ' '.join(p.split()[1:]) if len(p.split()) > 1 else '') for p in value.split(',') if p.strip())
            if n.get('style'):
                n['style'] = css_urls(n['style'], f['url'])
            for attr in ['alt', 'title', 'aria-label', 'content']:
                if isinstance(n.get(attr), str):
                    n[attr] = identity(absolute_urls(n[attr]))
            if n.name == 'style' and n.string:
                n.string = css_urls(n.string, f['url'])
            if n.name == 'script' and n.string:
                n.string = absolute_urls(n.string)
        for t in list(soup.find_all(string=True)):
            if not isinstance(t, Comment) and t.parent.name not in ['script', 'style']:
                changed = identity(str(t))
                if changed != str(t):
                    t.replace_with(changed)
        for form in soup.find_all('form'):
            if str(form.get('method', 'get')).lower() == 'post':
                form['data-original-action'] = form.get('action', '')
                form['action'] = '#'
                form['data-contact-unconfigured'] = 'true'
                stats['forms'] += 1
        if soup.head:
            script = soup.new_tag('script', src=BASE + 'brand/contact-guard.js', defer=True)
            soup.head.append(script)
        dest.write_text(tab_identity(str(soup)), encoding='utf-8')
        stats['pages'] += 1
    elif 'css' in f['type'] or src.suffix == '.css':
        dest.write_text(css_urls(src.read_text(encoding='utf-8'), f['url']), encoding='utf-8')
        stats['resources'] += 1
    elif src.suffix == '.js':
        dest.write_text(absolute_urls(src.read_text(encoding='utf-8-sig')), encoding='utf-8')
        stats['resources'] += 1
    else:
        shutil.copy2(src, dest)
        stats['resources'] += 1

shutil.copytree(ROOT / 'brand', OUT / 'brand', dirs_exist_ok=True)
(OUT / 'brand/contact-guard.js').write_text('''document.addEventListener('submit', function(event) {
  if (event.target.matches('[data-contact-unconfigured]')) {
    event.preventDefault();
    event.stopImmediatePropagation();
    alert('お問い合わせの送信先は準備中です。現在、このフォームからは送信できません。');
  }
}, true);
const nativeSubmit = HTMLFormElement.prototype.submit;
HTMLFormElement.prototype.submit = function() {
  if (this.matches('[data-contact-unconfigured]')) {
    alert('お問い合わせの送信先は準備中です。現在、このフォームからは送信できません。');
    return;
  }
  return nativeSubmit.call(this);
};
''', encoding='utf-8')
assets = OUT / 'wp/wp-content/themes/original_theme/img'
encoded = base64.b64encode((ROOT / 'brand/crystal-clean-home.png').read_bytes()).decode()
(assets / 'logo.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 234.74 65.57"><image width="234.74" height="65.57" preserveAspectRatio="xMinYMid meet" href="data:image/png;base64,' + encoded + '"/></svg>', encoding='utf-8')

for name, width, height, x, y, size, length in [('h_tel.svg',326.43,54.16,39,33,32,285), ('cv_tel.svg',549.05,94.34,61,91,58,485), ('cv_tel02.svg',554.35,108,85,101,55,465)]:
    original = (SOURCE / 'wp/wp-content/themes/original_theme/img' / name).read_text(encoding='utf-8')
    if name == 'h_tel.svg':
        svg = BeautifulSoup(original, 'xml')
        icon = str(svg.find('path', {'class':'cls-1'}))
        content = '<defs><style>.cls-1{fill:none;stroke:#8fc31f;stroke-width:2px;fill-rule:evenodd}</style></defs>' + icon
        content += '<text x="0" y="51" fill="#4d4d4d" font-size="11" font-family="sans-serif" textLength="326" lengthAdjust="spacingAndGlyphs">' + html.escape(brand['hours']) + '</text>'
    else:
        svg = BeautifulSoup(original, 'xml')
        root = svg.find('svg')
        viewbox = root.get('viewBox', '').split()
        if len(viewbox) == 4:
            width, height = float(viewbox[2]), float(viewbox[3])
        top = 42 if name == 'cv_tel.svg' else 38
        content = f'<defs><clipPath id="keep-art"><rect width="{width}" height="{top}"/><rect width="{x - 2}" height="{height}"/></clipPath></defs><g clip-path="url(#keep-art)">' + ''.join(str(c) for c in root.contents) + '</g>'
    content += f'<text x="{x}" y="{y}" fill="#8fc31f" font-family="Arial,sans-serif" font-size="{size}" textLength="{length}" lengthAdjust="spacingAndGlyphs">{brand["phone"]}</text>'
    (assets / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{content}</svg>', encoding='utf-8')
(OUT / '.nojekyll').touch()
if '--assets-only' not in sys.argv:
    (ROOT / 'build-report.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(stats, ensure_ascii=False))
