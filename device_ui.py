"""Publish independently owned PC/SP styles and image selections."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import hashlib
import json
import re
import subprocess

BASE = '/crystal-clean-home/'
DEVICES = {'desktop': '(min-width:993px)', 'mobile': '(max-width:992px)'}


def bootstrap(root):
    root = Path(root)
    folder = root / 'source/device'
    css_paths = subprocess.check_output(['git','ls-files','docs/*.css','docs/**/*.css'], cwd=root, text=True).splitlines()
    css_paths = [p[5:] for p in css_paths if not p.startswith('docs/device/')]
    (folder / 'manifest.json').parent.mkdir(parents=True, exist_ok=True)
    (folder / 'manifest.json').write_text(json.dumps(css_paths, indent=2), encoding='utf-8')
    for device in DEVICES:
        for relative in css_paths:
            css = (root / 'docs' / relative).read_text(encoding='utf-8')
            def absolute(match):
                value = match[2]
                if value.startswith(('data:', '#', 'http:', 'https:', '//', '/')):
                    return match[0]
                return 'url("'+urljoin(BASE+relative, value)+'")'
            css = re.sub(r'url\(\s*([\"\']?)([^\)\"\']+)\1\s*\)', absolute, css)
            target = folder / device / 'css' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(css, encoding='utf-8')


def publish_device_ui(root):
    root = Path(root)
    folder = root / 'source/device'
    if not (folder / 'manifest.json').exists():
        return
    css_paths = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    revisions = {d: hashlib.sha256(''.join((folder / d / 'css' / p).read_text(encoding='utf-8') for p in css_paths).encode()).hexdigest()[:12] for d in DEVICES}
    for relative in css_paths:
        imports = []
        for device, media in DEVICES.items():
            source = folder / device / 'css' / relative
            css = source.read_text(encoding='utf-8')
            # Imported styles must stay in the same device ownership tree.
            css = re.sub(r'url\([\"\']?('+re.escape(BASE)+r'[^\)\"\']+\.css)(?:\?[^\)\"\']*)?[\"\']?\)',
                         lambda m: 'url("'+BASE+'device/'+device+'/css/'+m[1][len(BASE):]+'?v='+revisions[device]+'")', css)
            target = root / 'docs/device' / device / 'css' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(css, encoding='utf-8')
            digest = hashlib.sha256(css.encode()).hexdigest()[:12]
            imports.append('@import url("'+BASE+'device/'+device+'/css/'+relative+'?v='+digest+'") screen and '+media+';')
        (root / 'docs' / relative).write_text('\n'.join(imports)+'\n', encoding='utf-8')
    config = {d: json.loads((folder / d / 'images.json').read_text(encoding='utf-8')) for d in DEVICES}
    ui = {d: json.loads((folder / d / 'ui.json').read_text(encoding='utf-8')) for d in DEVICES}
    output = root / 'docs/device'
    script = (root / 'brand/shared-ui/device-images.js').read_text(encoding='utf-8')
    (output / 'images.js').write_text('window.CCHDeviceUI='+json.dumps(ui)+';window.CCHDeviceImages='+json.dumps(config, ensure_ascii=False)+';\n'+script, encoding='utf-8')
    for device in DEVICES:
        for source in (folder/device/'css/inline').glob('*.css'):
            output=root/'docs/device'/device/'css/inline'/source.name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
    files = subprocess.check_output(['git','ls-files','docs/*.html','docs/**/*.html'], cwd=root, text=True).splitlines()
    def patch(name):
        path = root / name
        text = path.read_text(encoding='utf-8')
        if 'cch-header' not in text:
            return
        def inline_style(match):
            css = match[1]
            key = hashlib.sha256(css.encode()).hexdigest()[:16]
            links = []
            for device, media in DEVICES.items():
                source = folder / device / 'css/inline' / (key+'.css')
                if not source.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_text(css, encoding='utf-8')
                content = source.read_text(encoding='utf-8')
                output = root / 'docs/device' / device / 'css/inline' / (key+'.css')
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(content, encoding='utf-8')
                links.append('<link rel="stylesheet" media="'+media+'" href="'+BASE+'device/'+device+'/css/inline/'+key+'.css" data-device-inline>')
            return ''.join(links)
        text = re.sub(r'<style\b[^>]*>(.*?)</style>', inline_style, text, flags=re.S|re.I)
        text = re.sub(r'<script[^>]*data-device-images[^>]*></script>', '', text)
        text = text.replace('</head>', '<script defer src="'+BASE+'device/images.js?v=1" data-device-images></script></head>')
        path.write_text(text, encoding='utf-8')
    with ThreadPoolExecutor(max_workers=16) as pool:
        list(pool.map(patch, files))


if __name__ == '__main__':
    publish_device_ui(Path(__file__).parent)
