"""Add the shared viewport HUD without changing page markup or layout."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, re, shutil

def publish_hud(root):
    manifest = json.loads((root/'capture.json').read_text(encoding='utf-8'))
    paths = sorted({Path(f['path']).as_posix() for f in manifest['files'] if f.get('html') and not f['path'].startswith('vendor/')})
    shutil.copy2(root/'brand/viewport-hud.js', root/'docs/brand/viewport-hud.js')
    tag = '<script defer src="/crystal-clean-home/brand/viewport-hud.js?v=1" data-viewport-hud="true"></script>'
    def update(path):
        target = root/'docs'/path
        text = target.read_text(encoding='utf-8')
        text = re.sub(r'<script\b[^>]*\bdata-viewport-hud=["\'][^"\']*["\'][^>]*>.*?</script>\s*', '', text, flags=re.I|re.S)
        text = re.sub(r'</head>', lambda _: tag+'\n</head>', text, count=1, flags=re.I)
        target.write_text(text, encoding='utf-8')
    with ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(update, paths))
    return len(paths)
