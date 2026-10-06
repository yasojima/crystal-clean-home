"""Share original cleaning artwork across category selectors and product options."""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
DATA = json.loads((ROOT / 'source/cleaning-artwork.json').read_text(encoding='utf-8'))


def image_path(key):
    return f'/assets/images/cleaning-illustrations/{key}.png'


def transform_references(text):
    for original, key in DATA['replacement_images'].items():
        replacement = image_path(key)
        text = text.replace('https://yasojima.github.io' + original, replacement)
        text = text.replace(original, replacement)
    return text


def artwork_css():
    rules = ['''.c-illust {
  --width: 130px;
  display: inline-flex;
  width: var(--width);
  height: calc(.7692307692 * var(--width));
  background-color: transparent;
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
}
''']
    for name, key in DATA['illustrations'].items():
        rules.append(f'.c-illust--{name} {{ background-image: url("{image_path(key)}"); }}\n')
    rules.append('''
:is(.c-product-additional-card__image, .c-option-card__image img)[src*="/cleaning-illustrations/"] {
  background-color: #edf7fd;
  padding: 4px;
  border-radius: 8px;
  object-fit: contain;
}
''')
    return '\n'.join(rules) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    changed = []
    paths = [*SITE.rglob('*.html'), * (ROOT / 'source/service-pages').rglob('*.json'),
             * (ROOT / 'source/service-pages').rglob('*.html')]
    for path in paths:
        before = path.read_bytes().decode('utf-8')
        after = transform_references(before)
        if before != after:
            changed.append(path.relative_to(ROOT).as_posix())
            if not args.check:
                path.write_bytes(after.encode('utf-8'))
    css = SITE / 'assets/css/common.css'
    before = css.read_bytes().decode('utf-8')
    after, count = re.subn(r'\.c-illust \{.*?(?=\.c-label-tag \{)', lambda _: artwork_css(), before, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Shared illustration CSS block missing')
    if after != before:
        changed.append(css.relative_to(ROOT).as_posix())
        if not args.check:
            css.write_bytes(after.encode('utf-8'))
    keys = set(DATA['illustrations'].values()) | set(DATA['replacement_images'].values())
    missing = [key for key in sorted(keys) if not (SITE / image_path(key).lstrip('/')).is_file()]
    print(json.dumps(dict(changed=changed, assets=len(keys), missing=missing, check=args.check)))
    if args.check and (changed or missing):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
