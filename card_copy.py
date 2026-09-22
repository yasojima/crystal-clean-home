"""Apply reviewed wording only to imported explanatory card text nodes."""
from pathlib import Path
import json
import re
from bs4 import NavigableString, Comment

ROOT = Path(__file__).resolve().parent
RULES = json.loads((ROOT / 'brand/reference/card-copy.json').read_text(encoding='utf-8'))
EXCLUDED = ('voice', 'doctor-recommendation', 'product-card-list', 'category-simple', 'price')
NAME_HEADINGS = ('option-card', 'product-card', 'service-menu-card', 'category-card', 'set-plan-card', 'lineup-card', 'plan-card')

def eligible(element):
    classes = ' '.join(element.get('class', []))
    if 'card' not in classes or not any(role in classes for role in ('__description', '__text', '__heading')):
        return False
    if any(part in classes for part in EXCLUDED):
        return False
    if '__heading' in classes and any(part in classes for part in NAME_HEADINGS):
        return False
    return True

def rewrite(text):
    # Notes, qualifications and amounts are not copy-editing targets.
    if text.lstrip().startswith(('※', '＊', '*')):
        return text
    original = text.strip()
    replacement = RULES['replacements'].get(original)
    if replacement is None:
        return text
    start = len(text) - len(text.lstrip())
    updated = text[:start] + replacement + text[start + len(original):]
    if re.findall(r'\d+(?:[,.]\d+)*', text) != re.findall(r'\d+(?:[,.]\d+)*', updated):
        raise ValueError('Numeric condition changed during card editing')
    return updated

def apply_card_copy(main):
    changes = []
    for text in list(main.descendants):
        if not isinstance(text, NavigableString) or isinstance(text, Comment):
            continue
        parents = list(text.parents)
        if any(any(x in ' '.join(p.get('class', [])) for x in EXCLUDED) for p in parents):
            continue
        if not any(eligible(p) for p in parents):
            continue
        before = str(text)
        after = rewrite(before)
        if before != after:
            text.replace_with(after)
            changes.append((before, after))
    return changes
