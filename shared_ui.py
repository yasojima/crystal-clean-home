"""Publish the shared footer and page-specific header visibility."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import re
import shutil
import subprocess


def publish_shared_ui(root):
    root = Path(root)
    component = root / 'brand/shared-ui'
    shutil.copytree(component, root / 'docs/brand/shared-ui', dirs_exist_ok=True)
    shutil.copy2(root / 'brand/header/floating.js', root / 'docs/brand/header/floating.js')
    footer = (component / 'footer.html').read_text(encoding='utf-8')
    header = (root / 'brand/header/template.html').read_text(encoding='utf-8')
    area_label = re.search(r'<li class="area"><a[^>]*>([^<]+)</a>', header)[1]
    service_pattern = r'<li class="service">.*?</div>\s*</li>'
    service_menu = re.search(service_pattern, header, flags=re.S)[0]
    files = subprocess.check_output(['git', 'ls-files', 'docs/*.html', 'docs/**/*.html'], cwd=root, text=True).splitlines()
    def publish(name):
        path = root / name
        text = path.read_text(encoding='utf-8')
        if 'cch-header' not in text:
            return None
        old = text
        if name in {'docs/reason/index.html', 'docs/first/index.html', 'docs/qa/index.html', 'docs/area/index.html'}:
            text = re.sub(r'<aside\b[^>]*class="side"[^>]*>.*?</aside>', '', text, flags=re.S)
            text = re.sub(r'(class="page_container)(?![^"\n]*\bcch-single-column\b)',
                          r'\1 cch-single-column', text, count=1)
        text = re.sub(service_pattern, lambda _: service_menu, text, count=1, flags=re.S)
        text = re.sub(r'(<a\b[^>]*href="/crystal-clean-home/area/"[^>]*>)対応地域(</a>)',
                      lambda m: m[1] + area_label + m[2], text)
        if name == 'docs/area/index.html':
            text = text.replace('対応地域', area_label).replace('ご対応エリア', area_label)
        if name != 'docs/index.html':
            text = re.sub(r'<div\b[^>]*\bid="breadcrumb"[^>]*>.*?</div>', '', text, flags=re.S)
            text = re.sub(r'<ol\b[^>]*\bclass="c-breadcrumbs"[^>]*>.*?</ol>', '', text, flags=re.S)
        text = re.sub(r'h_tel\.svg(?:\?[^\"\s<>]*)?', 'h_tel.svg?v=solid1', text)
        page = 'home' if name == 'docs/index.html' else 'inner'
        if page == 'home':
            from home_cleanup import clean_home
            text = clean_home(text)
        text = re.sub(r'\sdata-cch-page="[^"]*"', '', text)
        text = re.sub(r'<html\b', '<html data-cch-page="'+page+'"', text, count=1)
        text = re.sub(r'<footer\b[^>]*>.*?</footer>', lambda m: footer, text, count=1, flags=re.S)
        text = re.sub(r'<link\b[^>]*data-shared-ui="style"[^>]*>', '', text)
        text = text.replace('</head>', '<link rel="stylesheet" href="/crystal-clean-home/brand/shared-ui/style.css?v=single-column1" data-shared-ui="style"></head>')
        text = re.sub(r'floating.js\?v=[^"\s]+', 'floating.js?v=bar-solid-links1', text)
        if text != old:
            path.write_text(text, encoding='utf-8')
            return name
    with ThreadPoolExecutor(max_workers=16) as pool:
        changed = [name for name in pool.map(publish, files) if name]
    from device_ui import publish_device_ui
    publish_device_ui(root)
    return changed


if __name__ == '__main__':
    print(len(publish_shared_ui(Path(__file__).parent)))
