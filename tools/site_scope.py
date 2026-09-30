import json
import re
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SCOPE = json.loads((ROOT / 'source/scope.json').read_text(encoding='utf-8'))
ORIGIN = 'https://www.osoujihonpo.com'
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())


def excluded_url(value, base=ORIGIN):
    parts = urlsplit(urljoin(base, unescape(value)))
    if parts.hostname in SCOPE['excluded_hosts']:
        return True
    if parts.hostname in {'www.osoujihonpo.com', 'osoujihonpo.com'}:
        return any(parts.path == p.rstrip('/') or parts.path.startswith(p) for p in SCOPE['excluded_path_prefixes'])
    return False


@dataclass(eq=False)
class Node:
    tag: str
    attrs: dict
    start: int
    start_end: int
    end: int = 0
    parent: object = None
    children: list = field(default_factory=list)


class Spans(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0]
        self.lines.extend(m.end() for m in re.finditer('\n', source))
        self.root = Node('root', {}, 0, 0, len(source))
        self.stack = [self.root]
        self.nodes = []
        self.feed(source)
        self.close()
        for node in self.stack[1:]:
            node.end = len(source)

    def source_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.source_offset()
        stop = start + len(self.get_starttag_text())
        node = Node(tag, dict(attrs), start, stop, stop if tag in VOID else 0, self.stack[-1])
        self.stack[-1].children.append(node)
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop().end = self.source_offset() + len(self.get_starttag_text())

    def handle_endtag(self, tag):
        start = self.source_offset()
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                for child in self.stack[i + 1:]:
                    child.end = start
                self.stack[i].end = self.source.find('>', start) + 1
                del self.stack[i:]
                return


def text_of(source, node):
    return unescape(re.sub(r'<[^>]*>', '', re.sub(r'<!--.*?-->', '', source[node.start:node.end], flags=re.S))).strip()


def ancestors(node):
    while node.parent and node.parent.tag != 'root':
        node = node.parent
        yield node


def descendants(node):
    for child in node.children:
        yield child
        yield from descendants(child)


def prune_html(data):
    source = data.decode('utf-8')
    tree = Spans(source)
    removed = set()
    groups = set(SCOPE['excluded_navigation_groups'])
    for node in tree.nodes:
        if node.tag not in {'p', 'span', 'button', 'h1', 'h2', 'h3', 'h4'}:
            continue
        label = re.sub(r'\s+', '', text_of(source, node))
        if label in groups or (node.tag in {'h1', 'h2', 'h3', 'h4'} and 'お役立ち情報' in label):
            if node.tag in {'h1', 'h2', 'h3', 'h4'}:
                section = next((a for a in ancestors(node) if a.tag == 'section' or 'p-content-box' in a.attrs.get('class', '').split()), None)
                if section:
                    removed.add(section)
                    continue
            group_heading = next((a for a in [node, *ancestors(node)] if 'c-footer-item-heading' in a.attrs.get('class', '').split()), node)
            removed.add(group_heading)
            siblings = group_heading.parent.children
            index = siblings.index(group_heading)
            if index + 1 < len(siblings):
                sibling = siblings[index + 1]
                if sibling.tag == 'ul' or 'c-footer-accordion__content' in sibling.attrs.get('class', '').split():
                    removed.add(sibling)
        if node.tag in {'h1', 'h2', 'h3', 'h4'} and ('お近くの店舗を探す' in label or 'フランチャイズ加盟に関する' in label):
            section = next((a for a in ancestors(node) if a.tag == 'section'), None)
            if section:
                removed.add(section)

    for node in tree.nodes:
        if node.tag == 'a' and excluded_url(node.attrs.get('href', '')):
            target = node
            for parent in ancestors(node):
                if parent.tag == 'li' or set(parent.attrs.get('class', '').split()) & {'c-footer-item-heading', 'swiper-slide'}:
                    links = [n for n in descendants(parent) if n.tag == 'a']
                    if all(excluded_url(n.attrs.get('href', '')) for n in links):
                        target = parent
                    break
                if parent.tag in {'section', 'nav', 'header', 'footer'}:
                    break
            removed.add(target)

    def covered(node):
        return node in removed or any(a in removed for a in ancestors(node))

    for node in reversed(tree.nodes):
        if node.tag not in {'div', 'ul', 'li', 'p', 'section', 'nav', 'span'} or covered(node):
            continue
        if node.children and all(covered(c) for c in node.children):
            inner = source[node.start_end:node.end]
            for child in sorted(node.children, key=lambda x: x.start, reverse=True):
                a, b = child.start - node.start_end, child.end - node.start_end
                inner = inner[:a] + inner[b:]
            if not re.sub(r'<[^>]*>|<!--.*?-->|\s+', '', inner, flags=re.S):
                removed.add(node)

    spans = sorted((n.start, n.end) for n in removed)
    merged = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    result = source
    for start, end in reversed(merged):
        result = result[:start] + result[end:]
    return result.encode('utf-8'), len(merged)
