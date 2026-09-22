"""Compile independently editable desktop/mobile layouts with shared content."""
from pathlib import Path
import json


def layout_source(root, relative):
    relative = Path(relative).as_posix()
    folder = root / 'source/layout'
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    name = manifest.get(relative)
    if name is None:
        return (root / 'source' / relative).read_text(encoding='utf-8')
    desktop = (folder / 'desktop' / name).read_text(encoding='utf-8')
    mobile = (folder / 'mobile' / name).read_text(encoding='utf-8')
    return '@media (min-width:993px), print {\n' + desktop + '\n}\n@media screen and (max-width:992px) {\n' + mobile + '\n}\n'
