"""Build estimate input/review pages from the reused form and shared site shell."""
import argparse
import re
from pathlib import Path
from build_shared_ui import transform

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'


def step_navigation(current):
    steps = ['見積り確認', '情報入力', '入力確認', '完了']
    return '<ol class="c-step-nav" aria-label="お見積りのステップ">' + ''.join(
        '<li class="c-step-nav__item"' + (' aria-current="step"' if i == current else '') + '>' + label + '</li>'
        for i, label in enumerate(steps)) + '</ol>'


def build(check=False):
    shell = (SITE / 'cart/index.html').read_bytes().decode('utf-8')
    form = (ROOT / 'source/cart-estimate/form.html').read_text(encoding='utf-8')
    changed = []
    for route, title, current, body in [
        ('cart/estimate', 'お客様情報のご入力', 1, form),
        ('cart/estimate/confirm', 'ご入力内容のご確認', 2,
         '<section class="l-section l-section--limited" style="--bg-color:#e3f1fc;"><div class="l-section-inner l-section-inner--limited"><div class="u-width-pc-640" data-estimate-confirm></div></div></section>'),
    ]:
        main = f'<main class="cch-estimate"><h1 class="c-page-heading" style="--bg-color:#f5f8fa;">{title}</h1>{step_navigation(current)}<p class="cch-estimate-notice">確認用画面です。お申し込みは送信されません。</p>{body}</main>'
        output = re.sub(r'<main\b.*?</main>', lambda _: main, shell, flags=re.S)
        output = re.sub(r'<title>.*?</title>', '<title>Crystal Clean Home</title>', output)
        output = re.sub(r'(<meta[^>]+property="og:url"[^>]+content=")[^"]*', rf'\g<1>https://yasojima.github.io/{route}/', output)
        output = output.replace('</head>', '<link rel="stylesheet" href="/assets/css/form/common.css">\n<script src="/assets/js/cart-estimate.js?v=2026100601" defer></script>\n</head>')
        output = transform(output)
        path = SITE / route / 'index.html'
        if not path.exists() or path.read_bytes().decode('utf-8') != output:
            changed.append(route)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(output.encode('utf-8'))
    print({'estimate_pages': 2, 'changed': changed, 'check': check})
    if check and changed:
        raise SystemExit('Estimate pages are out of date')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
