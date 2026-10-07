"""Apply the HOME background sequence after shared component rendering."""
import re


HOME_SECTIONS = (
    ('home-pickup--banner', '#fff', None, None),
    ('home-cleaning-list', '#fff', None, None),
    ('home-first-guide-section', '#e3f1fc', 'down', '#fff'),
    ('home-reasons', '#fff', 'up', '#e3f1fc'),
    ('home-concerns', '#e3f1fc', 'down', '#fff'),
    ('home-pickup--features', '#fff', 'up', '#e3f1fc'),
    ('c-featured-cleaning', '#fff', None, None),
)


def apply_home_section_backgrounds(html):
    if '<body class="c-home"' not in html:
        return html
    found = set()

    def decorate(match):
        opening, content = match[1], match[2]
        classes = re.search(r'\bclass="([^"]*)"', opening)
        section_id = re.search(r'\bid="([^"]*)"', opening)
        tokens = classes[1].split() if classes else []
        for key, color, direction, previous in HOME_SECTIONS:
            if key not in tokens and (not section_id or section_id[1] != key):
                continue
            found.add(key)
            tokens = [c for c in tokens if c not in (
                'l-section--blue-wave', 'c-curved-section',
                'c-curved-section--up', 'c-curved-section--down')]
            if direction:
                tokens += ['c-curved-section', f'c-curved-section--{direction}']
            opening = re.sub(r'\bclass="[^"]*"', 'class="' + ' '.join(tokens) + '"', opening)
            style = re.search(r'\bstyle="([^"]*)"', opening)
            value = re.sub(r'--bg-color\s*:[^;]*;?', '', style[1]).strip() if style else ''
            value = (value + ' ' if value else '') + f'--bg-color: {color};'
            opening = re.sub(r'\bstyle="[^"]*"', f'style="{value}"', opening) if style else opening[:-1] + f' style="{value}">'
            content = re.sub(r'^\s*<span\b[^>]*class="c-section-curve\b[^>]*></span>', '', content, count=1)
            if direction:
                content = (f'<span aria-hidden="true" class="c-section-curve c-section-curve--{direction}" '
                           f'style="--curve-color: {previous};"></span>' + content)
            return opening + content + '</section>'
        return match[0]

    html = re.sub(r'(<section\b[^>]*>)(.*?)</section>', decorate, html, flags=re.S)
    if found != {s[0] for s in HOME_SECTIONS}:
        raise ValueError('Missing HOME background sections: ' + str({s[0] for s in HOME_SECTIONS} - found))
    return html
