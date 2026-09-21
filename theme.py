import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
THEME = json.loads((ROOT / 'brand/theme.json').read_text(encoding='utf-8'))
MINCHO = '"Yu Mincho","游明朝",YuMincho,"Hiragino Mincho ProN",serif'
GOTHIC = '"Yu Gothic","游ゴシック",YuGothic,"Hiragino Kaku Gothic ProN",Meiryo,sans-serif'

def colors(text):
    return re.sub(r'#[0-9a-fA-F]{3,8}\b', lambda m: THEME['replace'].get(m[0].lower(), m[0]), text)

def stylesheet(text):
    def declaration(m):
        parts = re.split(r'(url\([^)]*\))', m['v'])
        return m['p'] + ''.join(part if part.startswith('url(') else colors(part) for part in parts)
    text = re.sub(r'(?P<p>(?:[\w-]+)\s*:)(?P<v>[^;{}]+)', declaration, text)
    return text

def vector(text):
    text = re.sub(r'(<style\b[^>]*>)(.*?)(</style>)', lambda m: m[1] + stylesheet(m[2]) + m[3], text, flags=re.S)
    return re.sub(r'((?:fill|stroke|stop-color|style)=["\'])(.*?)(["\'])', lambda m: m[1] + colors(m[2]) + m[3], text)

def typography():
    return '\n' + f'''body, input, textarea, select, button, .mincho {{font-family:{GOTHIC};}}
body {{color:{THEME['colors']['text']};}}
main h1, main h2, .subvisual h1 {{font-family:{MINCHO};}}
main h1, main h2 {{color:{THEME['colors']['navy']};}}
.subvisual h1 {{color:#fff;}}
header, nav, .btn, .btn_cv, .btn_flat, table, input, textarea, select, button {{font-family:{GOTHIC};}}
.require, .error, .wpcf7-not-valid-tip {{color:{THEME['colors']['notice']};}}
.side .side_menu h3, .side .first a {{background-color:{THEME['colors']['blue']};background-blend-mode:luminosity;}}
'''
