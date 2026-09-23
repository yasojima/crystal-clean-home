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
    files = subprocess.check_output(['git', 'ls-files', 'docs/*.html', 'docs/**/*.html'], cwd=root, text=True).splitlines()
    def publish(name):
        path = root / name
        text = path.read_text(encoding='utf-8')
        if 'cch-header' not in text:
            return None
        old = text
        text = re.sub(r'h_tel\.svg(?:\?[^\"\s<>]*)?', 'h_tel.svg?v=solid1', text)
        page = 'home' if name == 'docs/index.html' else 'inner'
        if page == 'home':
            from home_cleanup import clean_home
            text = clean_home(text)
        text = re.sub(r'\sdata-cch-page="[^"]*"', '', text)
        text = re.sub(r'<html\b', '<html data-cch-page="'+page+'"', text, count=1)
        text = re.sub(r'<footer\b[^>]*>.*?</footer>', lambda m: footer, text, count=1, flags=re.S)
        text = re.sub(r'<link\b[^>]*data-shared-ui="style"[^>]*>', '', text)
        text = text.replace('</head>', '<link rel="stylesheet" href="/crystal-clean-home/brand/shared-ui/style.css?v=menu-fit1" data-shared-ui="style"></head>')
        text = re.sub(r'floating.js\?v=[^"\s]+', 'floating.js?v=menu-fit1', text)
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
