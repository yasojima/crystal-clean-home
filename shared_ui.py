"""Publish the shared footer and page-specific header visibility."""
from pathlib import Path
import re
import shutil
import subprocess
from io_retry import write_text


LEGACY_ORIGIN = re.compile(r'iekire\.com|osoujihonpo\.com|おそうじ本舗|お掃除本舗|イエキレ|家キレ', re.I)


def remove_legacy_head_metadata(text):
    """Drop copied SEO/contact metadata without changing the visible page tree."""
    def clean_head(match):
        head = match.group(0)
        head = re.sub(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>',
                      lambda item: '' if LEGACY_ORIGIN.search(item[0].replace('\\/', '/')) else item[0],
                      head, flags=re.S | re.I)
        head = re.sub(r'<(?:meta|link)\b[^>]*>',
                      lambda item: '' if LEGACY_ORIGIN.search(item[0]) else item[0], head, flags=re.I)
        return head
    text = re.sub(r'<head\b[^>]*>.*?</head>', clean_head, text, count=1, flags=re.S | re.I)
    text = re.sub(r'<!--.*?-->',
                  lambda item: '' if LEGACY_ORIGIN.search(item[0]) else item[0],
                  text, flags=re.S)
    return re.sub(r'<script\b(?![^>]*\bsrc=)[^>]*>.*?</script>',
                  lambda item: '' if 'wp-emoji' in item[0] and LEGACY_ORIGIN.search(item[0]) else item[0],
                  text, flags=re.S | re.I)


def remove_unset_phone_links(text):
    """Do not expose captured or placeholder telephone actions before a number is set."""
    return re.sub(r'<a\b(?=[^>]*(?:href=["\']tel:|data-demo-action=["\']phone))[^>]*>.*?</a>',
                  '', text, flags=re.S | re.I)


def publish_shared_ui(root):
    root = Path(root)
    from first_lp import publish_first_lp
    publish_first_lp(root)
    first = root / 'docs/first/index.html'
    if first.exists():
        source = (root / 'source/first/index.html').read_text(encoding='utf-8')
        content = re.search(r'<main class="main_contents">.*?</main>', source, re.S)
        if content is None:
            raise ValueError('Missing canonical first-page content')
        markup, count = re.subn(r'<main class="main_contents">.*?</main>',
                                lambda _: content[0], first.read_text(encoding='utf-8'), count=1, flags=re.S)
        if count != 1:
            raise ValueError('Missing first-page main')
        write_text(first, markup)
    component = root / 'brand/shared-ui'
    shutil.copytree(component, root / 'docs/brand/shared-ui', dirs_exist_ok=True)
    shutil.copy2(root / 'brand/header/floating.js', root / 'docs/brand/header/floating.js')
    shutil.copy2(root / 'brand/header/cart-mark.svg', root / 'docs/brand/header/cart-mark.svg')
    footer = (component / 'footer.html').read_text(encoding='utf-8').rstrip()
    header = (root / 'brand/header/template.html').read_text(encoding='utf-8')
    area_label = re.search(r'<li class="area"><a[^>]*>([^<]+)</a>', header)[1]
    service_pattern = r'<li class="service">.*?</div>\s*</li>'
    service_menu = re.search(service_pattern, header, flags=re.S)[0]
    files = subprocess.check_output(['git', 'ls-files', 'docs/*.html', 'docs/**/*.html'], cwd=root, text=True).splitlines()
    def publish(name):
        path = root / name
        if not path.exists():
            return None
        text = path.read_text(encoding='utf-8')
        if 'cch-header' not in text:
            return None
        old = text
        text = remove_legacy_head_metadata(text)
        text = remove_unset_phone_links(text)
        text = re.sub(r'<!--\s*<div class="movie-area">.*?</div>\s*-->',
                      '', text, flags=re.S)
        # Captured area pages include unrelated repair-company directories.
        text = re.sub(r'<section>\s*<h2>[^<]*</h2>\s*<div class="gyosha">.*?</section>',
                      '', text, flags=re.S)
        text = re.sub(r'<section>\s*<div class="gaiyo">.*?</section>',
                      '', text, flags=re.S)
        text = re.sub(r'<iframe\b[^>]*data-src="https://www\.youtube\.com/embed/"[^>]*>\s*</iframe>',
                      '', text, flags=re.S | re.I)
        if name in {'docs/reason/index.html', 'docs/first/index.html', 'docs/qa/index.html', 'docs/area/index.html', 'docs/service/corporation/index.html', 'docs/contact/index.html'}:
            text = re.sub(r'<aside\b[^>]*class="side"[^>]*>.*?</aside>', '', text, flags=re.S)
            text = re.sub(r'(class="page_container)(?![^"\n]*\bcch-single-column\b)',
                          r'\1 cch-single-column', text, count=1)
        text = re.sub(service_pattern, lambda _: service_menu, text, count=1, flags=re.S)
        text = re.sub(r'<li class="reason">.*?</li>', '', text, flags=re.S)
        text = text.replace('href="/crystal-clean-home/reason/"',
                            'href="/crystal-clean-home/first/#cleaning-approach"')
        text = re.sub(r'<li class="faq"><a[^>]*>.*?</a></li>', '', text)
        text = re.sub(r'(<a\b[^>]*href="/crystal-clean-home/area/"[^>]*>)対応地域(</a>)',
                      lambda m: m[1] + area_label + m[2], text)
        if name == 'docs/contact/index.html':
            text = re.sub(r'(class="page_container)(?![^"\n]*\bcch-contact-page\b)',
                          r'\1 cch-contact-page', text, count=1)
            text = re.sub(r'<script\b[^>]*src=["\'][^"\']*mw-wp-form/js/[^"\']*["\'][^>]*>\s*</script>', '', text, flags=re.S)
            text = re.sub(r'<tr\b[^>]*>.*?</tr>', lambda m: '' if any(label in m[0] for label in ['エアコンの型番・型式', '第三希望']) else m[0], text, flags=re.S)
            text = text.replace('ご依頼内容', 'お問い合わせ項目')
            text = text.replace('例) xxx@example.com', 'メールアドレス')
            text = text.replace('<p>ご予約は余裕をもってお申し込みください。日程が近い場合は、お電話やメールで調整のご相談をすることがあります。</p>', '')
            text = text.replace('お見積もり・ご相談フォーム', 'お問い合わせ窓口').replace('お見積もり・ご相談', 'お問い合わせ窓口')
            text = text.replace('<h1>お問い合わせ窓口</h1>', '<h1 class="cch-contact-title-band">お問い合わせ窓口</h1>')
            text = text.replace('<h2>お問い合わせ窓口</h2>', '<h2 class="cch-contact-heading">お問い合わせ窓口</h2>')
        if name == 'docs/simulation-contact/index.html':
            text = text.replace('例) xxx@example.com', 'メールアドレス')
        if name == 'docs/sitemap/index.html':
            text = text.replace('康栄クリーンアップ', 'クリスタルクリーンホーム')
        if name in {'docs/company/index.html', 'docs/privacy-policy/index.html'}:
            title = '会社概要' if name == 'docs/company/index.html' else 'プライバシーポリシー'
            notice = ('事業者情報を確認中です。確定後に掲載します。' if name == 'docs/company/index.html'
                      else '事業者情報に合わせて内容を整備中です。このサイトのフォームから送信はできません。')
            replacement = f'<main class="main_contents"><h1>{title}</h1><section class="cch-info-pending"><p>{notice}</p></section></main>'
            text, found = re.subn(r'<main class="main_contents">.*?</main>',
                                  lambda _: replacement, text, count=1, flags=re.S)
            if found != 1:
                raise ValueError('Expected information page main: ' + name)
        if name == 'docs/area/index.html':
            # Approved removal: the legacy regional map, including its lazy-load fallback.
            text = re.sub(r'<div>\s*<img\b[^>]*data-src="[^"]*/area001\.svg"[^>]*>\s*<noscript>.*?</noscript>\s*</div>', '', text, flags=re.S)
            text = text.replace('対応地域', area_label).replace('ご対応エリア', area_label)
        if name != 'docs/index.html':
            text = re.sub(r'<div\b[^>]*\bid="breadcrumb"[^>]*>.*?</div>', '', text, flags=re.S)
            text = re.sub(r'<ol\b[^>]*\bclass="c-breadcrumbs"[^>]*>.*?</ol>', '', text, flags=re.S)
        text = re.sub(r'h_tel\.svg(?:\?[^\"\s<>]*)?', 'h_tel.svg?v=solid1', text)
        page = 'home' if name == 'docs/index.html' else 'inner'
        if page == 'home':
            from home_cleanup import clean_home
            text = clean_home(text)
        text = re.sub(r'\sdata-cch-page="[^"]*"', '', text)
        text = re.sub(r'<html\b', '<html data-cch-page="'+page+'"', text, count=1)
        text = re.sub(r'<footer\b[^>]*>.*?</footer>', lambda m: footer, text, count=1, flags=re.S)
        text = text.replace('href="/crystal-clean-home/qa/"', 'href="/crystal-clean-home/#cch-faq"')
        text = re.sub(r'(brand/header/style.css)\?v=[^"\s]+', r'\1?v=nav-four1', text)
        text = re.sub(r'<link\b[^>]*data-shared-ui="style"[^>]*>', '', text)
        text = text.replace('</head>', '<link rel="stylesheet" href="/crystal-clean-home/brand/shared-ui/style.css?v=single-column1" data-shared-ui="style"></head>')
        text = re.sub(r'floating.js\?v=[^"\s]+', 'floating.js?v=single-product-cart1', text)
        if text != old:
            write_text(path, text)
            return name
    changed = [name for name in map(publish, files) if name]
    from device_ui import publish_device_ui
    publish_device_ui(root)
    (root / 'docs/qa/index.html').unlink(missing_ok=True)
    (root / 'docs/reason/index.html').unlink(missing_ok=True)
    return changed


if __name__ == '__main__':
    print(len(publish_shared_ui(Path(__file__).parent)))
