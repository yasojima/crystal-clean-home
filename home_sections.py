"""Publish isolated homepage components from their shared source templates."""
from pathlib import Path
import re
import shutil
import hashlib

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
        pattern = rf'<!-- cch-{name}:start -->.*?<!-- cch-{name}:end -->|<!-- cch-{name} -->|<section class="{old}">.*?</section>'
        text, count = re.subn(pattern, lambda _: f'<!-- cch-{name}:start -->{markup}<!-- cch-{name}:end -->', text, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f'Missing homepage component {name}')
        text = re.sub(rf'<link[^>]*data-home-component="{name}"[^>]*>\s*', '', text)
        version = hashlib.sha256((component / 'style.css').read_bytes()).hexdigest()[:12]
        text = text.replace('</head>', f'<link rel="stylesheet" href="/crystal-clean-home/brand/{name}/style.css?v={version}" data-home-component="{name}">\n</head>')
        shutil.copytree(component, root / 'docs/brand' / name, dirs_exist_ok=True)
    if 'data-home-font' not in text:
        text = text.replace('</head>', '<link data-home-font="true" rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&amp;display=swap">\n</head>')
    for cls in ['sec_info', 'sec_point']:
        text = re.sub(rf'<section class="{cls}">.*?</section>\s*', '', text, flags=re.S)
    target.write_text(text, encoding='utf-8')

if __name__ == '__main__':
    publish_home_sections(Path(__file__).resolve().parent)
