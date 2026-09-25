"""Shared editorial copy; layout and non-text attributes remain untouched."""
from pathlib import Path
from lxml import html
import hashlib, json, re
from io_retry import write_text

ROOT = Path(__file__).resolve().parent

def normalize(text):
    text = text.replace('クリスタルクリーンホーム', 'イエキレ')
    return re.sub(r'\s+', ' ', text).strip()

def text_id(text):
    return hashlib.sha256(normalize(text).encode('utf-8')).hexdigest()[:20]

def publish_copy(root):
    catalog = json.loads((root/'copy/ja.json').read_text(encoding='utf-8'))
    manifest = json.loads((root/'capture.json').read_text(encoding='utf-8'))
    pages = sorted({Path(f['path']).as_posix() for f in manifest['files'] if f.get('html') and not f['path'].startswith('vendor/')})
    changes = []
    for path in pages:
        dest = root/'docs'/path
        doc = html.document_fromstring(dest.read_text(encoding='utf-8'))
        page_changes = []
        def rewrite(value):
            if not value or not value.strip():
                return value
            replacement = catalog.get(text_id(value))
            if replacement is None:
                return value
            replacement = replacement.replace('イエキレ', 'クリスタルクリーンホーム')
            if replacement == normalize(value):
                return value
            page_changes.append({'before':value.strip(), 'after':replacement})
            return value[:len(value)-len(value.lstrip())] + replacement + value[len(value.rstrip()):]
        for node in doc.iter():
            if not isinstance(node.tag, str) or node.tag in ('script', 'style', 'title'):
                continue
            if any(a.tag in ('script', 'style', 'svg') for a in node.iterancestors()):
                continue
            node.text = rewrite(node.text)
            node.tail = rewrite(node.tail)
            for attr in ['alt', 'title', 'aria-label', 'placeholder']:
                if node.get(attr):
                    node.set(attr, rewrite(node.get(attr)))
        if page_changes:
            write_text(dest, '<!DOCTYPE html>\n'+html.tostring(doc, encoding='unicode', method='html'))
            changes.append({'path':path, 'changes':page_changes})
    return changes
