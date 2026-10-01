"""Apply the site's shared identity and demo-only contact behavior to every page.

Run this after adding or importing HTML pages. --check makes the same rules a
read-only publishing gate, so a newly added page cannot silently keep old tab
branding or live contact destinations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

from apply_site_typography import add_typography_links

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "source/site"
MANIFEST = ROOT / "source/manifest.json"
PUBLIC = "https://yasojima.github.io"
BRAND = "クリスタルクリーンホーム"
TAB_BRAND = "Crystal Clean Home"
ICON = '<link rel="icon" type="image/svg+xml" sizes="any" href="/favicon/crystal-clean-home.svg">'
DEMO_SCRIPT = '<script src="/assets/js/demo-contact.js" defer></script>'
TRANSLATION_SCRIPT = '<script type="module" src="/assets/js/shared-translation-control.js"></script>'
BRAND_BANNER = ('<span class="c-brand-banner c-brand-banner--{kind}">'
                '<img class="c-brand-banner__logo" src="/assets/images/crystal-clean-home.png" alt="クリスタルクリーンホーム">'
                '<span class="c-brand-banner__copy"><span class="c-brand-banner__eyebrow">{eyebrow}</span>'
                '<span class="c-brand-banner__label">{label}</span></span>'
                '<span class="c-brand-banner__arrow" aria-hidden="true">›</span></span>')
OLD_NAMES = ("おそうじ本舗", "お掃除本舗", "オソウジホンポ")
CONTACT_URL = re.compile(
    r"^(?:tel:|mailto:|/?(?:contact|business/contact|campaign/180223-01)(?:/|\?|$)|"
    r"https?://(?:form\.osoujihonpo\.com|reg18\.smp\.ne\.jp)/|"
    r"https?://www\.osoujihonpo\.com/(?:contact|business/contact)(?:/|\?|$)|"
    r"https?://yasojima\.github\.io/(?:contact|business/contact)(?:/|\?|$))", re.I
)
FORMER_BRAND_URL = re.compile(
    r"^https?://(?:[^/]*\.)?(?:osoujihonpo\.com|osoujihonpo-fc\.com|"
    r"hitowa\.com)(?:[/:?]|$)|^https?://lin\.ee/|"
    r"^https?://line\.me/R/ti/p/|"
    r"^https?://play\.google\.com/store/apps/details\?id=com\.osoujihonpo\.customer", re.I
)
OLD_SOCIAL = re.compile(
    r"^https?://(?:twitter\.com/osoujihonpo|x\.com/osoujihonpo|"
    r"(?:www\.)?facebook\.com/osoujihonpo|(?:www\.)?instagram\.com/osoujihonpo|"
    r"(?:www\.)?youtube\.com/@osoujihonpo)", re.I
)
LINK = re.compile(r'<a\b[^>]*\bhref="([^"]*)"[^>]*>', re.I | re.S)
ICON_LINKS = re.compile(r'\s*<link\b[^>]*\brel="(?:icon|shortcut icon|apple-touch-icon)"[^>]*>', re.I)
MANIFEST_LINK = re.compile(r'\s*<link\b[^>]*\brel="manifest"[^>]*>', re.I)
OLD_SOCIAL_ITEM = re.compile(
    r'<li\b[^>]*>\s*<a\b[^>]*\bhref="(?:https?://)?(?:twitter\.com/osoujihonpo|'
    r'x\.com/osoujihonpo|(?:www\.)?facebook\.com/osoujihonpo|'
    r'(?:www\.)?instagram\.com/osoujihonpo|(?:www\.)?youtube\.com/@osoujihonpo|'
    r'lin\.ee/4PFvSTR|(?:www\.)?hitowa\.com/life-partner/company)'
    r'[^\"]*".*?</a>\s*</li>\s*', re.I | re.S
)
def footer_sns(index: int) -> str:
    items = ''.join(
        f'<li class="c-footer-sns__item"><button class="c-footer-sns__link" '
        f'type="button" data-demo-dialog="" aria-label="{label}（デモ）">'
        f'<img class="c-flex-image c-flex-image--stretched c-footer-sns__image" '
        f'src="/assets/images/common-parts/sns-icon/icon-{name}.png" '
        f'alt="" width="40" height="40" loading="lazy"></button></li>'
        for name, label in (("x", "X"), ("instagram", "Instagram"),
                            ("tiktok", "TikTok"), ("youtube", "YouTube"))
    )
    menu_id = f'translate-menu-footer-{index}'
    items += (
        '<li class="c-footer-sns__item"><div class="translate-control">'
        f'<button class="c-footer-sns__link translate-toggle" type="button" '
        f'aria-expanded="false" aria-controls="{menu_id}" aria-label="表示言語を選択">'
        '<img class="c-flex-image c-flex-image--stretched c-footer-sns__image" '
        'src="/assets/images/common-parts/sns-icon/icon-translate.png" '
        'alt="" width="40" height="40" loading="lazy"></button>'
        f'<div id="{menu_id}" class="translate-menu" aria-hidden="true" inert>'
        '<p>言語を選択</p>'
        f'<div id="google-translate-footer-{index}" class="google-translate-widget" '
        'data-google-translate></div>'
        '<small>Google 翻訳でページ本文を切り替えます。</small>'
        '</div></div></li>'
    )
    return '<ul class="c-footer-sns">' + items + '</ul>'
FOOTER_PHONE_MARKUP = ('<span class="c-demo-phone">'
                       '<img src="/assets/images/footer/footer-phone-demo-{size}.svg" '
                       'alt="仮の電話番号 00-0000-0000。受付時間 9:00〜18:00">'
                       '<button class="c-demo-phone__number" type="button" '
                       'data-demo-dialog="" aria-label="仮の電話番号 00-0000-0000"></button>'
                       '</span>')


def tab_title(_raw_title: str) -> str:
    """Show only the shared site name beside the logo in browser tabs."""
    return TAB_BRAND


def replace_link(match: re.Match[str]) -> str:
    tag, href = match.group(), match.group(1)
    if not (CONTACT_URL.match(href) or OLD_SOCIAL.match(href) or FORMER_BRAND_URL.match(href)
            or "osoujihonpo" in href.lower()
            or "via=osoujihonpo" in href.lower()):
        return tag
    tag = tag.replace(f'href="{href}"', 'href="#" data-demo-dialog=""', 1)
    tag = re.sub(r'\s+target="[^"]*"', '', tag, flags=re.I)
    tag = re.sub(r'\s+rel="[^"]*"', '', tag, flags=re.I)
    return tag


def transform(text: str, is_html: bool) -> str:
    for old_name in OLD_NAMES:
        text = text.replace(old_name, BRAND)
    text = text.replace("/assets/images/logo.webp", "/assets/images/crystal-clean-home.png")
    text = text.replace('<span class="c-brand-banner__label">ハウスクリーニングについて</span>',
                        '<span class="c-brand-banner__label">お掃除サービスのご案内</span>')
    text = text.replace('<span class="c-brand-banner__label">ハウスクリーニングのご案内</span>',
                        '<span class="c-brand-banner__label">お掃除サービスのご案内</span>')
    text = re.sub(r'(<img class="c-flex-image" )src="/assets/images/crystal-clean-home\.png"(?: style="[^"]*")?',
                  r'\1src="/assets/images/crystal-clean-home.png" style="width:160px;height:82px;object-fit:contain;object-position:left center"', text)
    text = re.sub(r'(<img class=\\"c-flex-image\\" )src=\\"/assets/images/crystal-clean-home\.png\\"(?: style=\\"[^\\]*\\")?',
                  r'\1src=\\"/assets/images/crystal-clean-home.png\\" style=\\"width:160px;height:82px;object-fit:contain;object-position:left center\\"', text)
    text = text.replace("/assets/images/footer/footer-tel-sp.gif", "/assets/images/footer/footer-phone-demo-sp.svg")
    text = text.replace("/assets/images/footer/footer-tel-pc.gif", "/assets/images/footer/footer-phone-demo-pc.svg")
    text = text.replace("0120-24-1000", "00-0000-0000").replace("0120241000", "00-0000-0000")
    text = text.replace("03-6630-6104", "00-0000-0000").replace("0366306104", "00-0000-0000")
    text = text.replace('placeholder="XXXXX@sample.com"', 'placeholder=""')
    text = text.replace('&copy; HITOWA Co., Ltd.', BRAND).replace('© HITOWA Co., Ltd.', BRAND)
    text = text.replace('&copy; HITOWA Life Partner Co., Ltd.', BRAND)
    text = text.replace('HITOWAの強み', 'サービスの強み')
    text = text.replace('www.osoujihompo.com', 'yasojima.github.io')
    text = text.replace('/assets/images/campaign/m10/logo.png', '/assets/images/crystal-clean-home.png')
    text = text.replace('/assets/images/campaign/ots/sec7_logo.png', '/assets/images/crystal-clean-home.png')
    text = re.sub(r'<picture\b[^>]*>(?:(?!</picture>).)*?about-link_pc\.webp(?:(?!</picture>).)*?</picture>',
                  BRAND_BANNER.format(kind='about', eyebrow='初めての方はこちら',
                                      label='お掃除サービスのご案内'), text, flags=re.S)
    text = re.sub(r'<picture\b[^>]*>(?:(?!</picture>).)*?prevention-link_pc\.webp(?:(?!</picture>).)*?</picture>',
                  BRAND_BANNER.format(kind='prevention', eyebrow='',
                                      label='感染予防への取り組み'), text, flags=re.S)
    text = re.sub(r'<picture\b[^>]*>(?:(?!</picture>).)*?campaign_banner_02v2_pc\.webp(?:(?!</picture>).)*?</picture>',
                  BRAND_BANNER.format(kind='coating', eyebrow='水まわりを清潔に',
                                      label='お手入れ簡単コーティング'), text, flags=re.S)
    text = re.sub(r'<a\b[^>]*class="mv__slide swiper-slide"[^>]*>\s*<picture\b[^>]*>'
                  r'(?:(?!</picture>).)*?hctop_banner_lineyoyaku_PC\.webp(?:(?!</picture>).)*?'
                  r'</picture>\s*</a>\s*', '', text, flags=re.S)
    text = re.sub(r'<a\b[^>]*class="pickup-card swiper-slide"[^>]*>\s*'
                  r'<img\b[^>]*img-app750\.webp[^>]*>.*?</a>\s*', '', text, flags=re.S)
    text = re.sub(r'<a\b[^>]*>\s*<img\b[^>]*'
                  r'/assets/images/campaign/(?:aircon-all-year|aircon-multiple-units)/line_bnr\.webp'
                  r'[^>]*>\s*</a>\s*', '', text, flags=re.S)
    text = re.sub(r'<a\b[^>]*class="c-line-inquiry"[^>]*>.*?</a>\s*', '', text, flags=re.S)
    text = re.sub(r'(<span class="c-brand-banner[^\r\n]*</span>)[ \t]+(?=\r?\n)',
                  r'\1', text)
    if is_html and '<h2 class="c-heading-level-2 contact__heading">株式会社HITOWA' in text:
        text = re.sub(r'<section\b[^>]*>(?:(?!</section>).)*株式会社HITOWA(?:(?!</section>).)*</section>\s*',
                      '', text, flags=re.S)
    text = OLD_SOCIAL_ITEM.sub("", text)
    sns_indexes = iter(range(1, 20))
    text = re.sub(r'<ul class="c-footer-sns">.*?</ul>',
                  lambda _: footer_sns(next(sns_indexes)), text, flags=re.S)
    text = re.sub(r'<li class="c-footer-bottom-links__item"><a class="c-footer-bottom-links__link" '
                  r'href="/sitemap/">サイトマップ</a></li>\s*', '', text)
    text = re.sub(r'<li><a href="/sitemap/">サイトマップ</a></li>\s*', '', text)
    pending_note = '<span class="c-pending-link__note">※ページ作成後、リンク設定の予定</span>'
    text = text.replace(
        '<div class="c-footer-item-heading"><a class="link" aria-disabled="true">ハウスクリーニング</a></div>',
        '<div class="c-footer-item-heading"><a class="link" aria-disabled="true">ハウスクリーニング</a>'
        + pending_note + '</div>')
    text = re.sub(
        r'(<span class="c-footer-item-heading__text"><a aria-disabled="true">ハウスクリーニング</a></span>)'
        r'(?!<span class="c-pending-link__note">)',
        lambda match: match.group(1) + pending_note, text)
    text = re.sub(r'<p class="footer-tel-img">.*?</p>',
                  '<p class="footer-tel-img">' + FOOTER_PHONE_MARKUP.format(size='sp') + '</p>',
                  text, flags=re.S)
    text = re.sub(r'<p class="footer-tel-pc">.*?</p>',
                  '<p class="footer-tel-pc">' + FOOTER_PHONE_MARKUP.format(size='pc') + '</p>',
                  text, flags=re.S)
    text = text.replace('<p class="footer-tel-btn"><a href="#" data-demo-dialog="">今すぐ電話する</a></p>',
                        '<p class="footer-tel-btn"><a href="#" data-demo-dialog="">電話窓口について</a></p>')
    text = LINK.sub(replace_link, text)
    text = re.sub(r'href=\\"https?://(?:twitter\.com/osoujihonpo|x\.com/osoujihonpo|'
                  r'(?:www\.)?facebook\.com/osoujihonpo|(?:www\.)?instagram\.com/osoujihonpo|'
                  r'(?:www\.)?youtube\.com/@osoujihonpo)[^\\]*\\"',
                  r'href=\\"#\\"', text, flags=re.I)
    text = text.replace("https://www.osoujihonpo.com", PUBLIC)
    text = text.replace("http://www.osoujihonpo.com", PUBLIC)
    text = text.replace(f'{PUBLIC}/assets/images/ogp.jpg',
                        f'{PUBLIC}/assets/images/crystal-clean-home.png')
    text = re.sub(r'https?://cdn\.osoujihonpo\.com/(?:campaign/images/(?:[^"\s]*/)?logo\.(?:gif|png|webp)|images/front/common/ogp_logo\.jpg)',
                  '/assets/images/crystal-clean-home.png', text, flags=re.I)
    text = re.sub(r'(<meta\b[^>]*property="og:image"[^>]*content=")/assets/images/crystal-clean-home\.png',
                  rf'\g<1>{PUBLIC}/assets/images/crystal-clean-home.png', text, flags=re.I)
    text = re.sub(r'\s*"sameAs"\s*:\s*\[[^\]]*\],', '', text, flags=re.S)
    # The site's old social identities must not be advertised in page metadata.
    text = re.sub(r'^\s*<meta\b[^>]*name="twitter:site"[^>]*>\s*\r?\n', '', text, flags=re.I | re.M)
    if not is_html:
        return text
    # Imported pages must not send demo visits to the former operator's
    # review or analytics accounts.
    text = re.sub(r'<script\b[^>]*>(?:(?!</script>).)*?api\.u-komi\.com(?:(?!</script>).)*?</script>\s*',
                  '', text, flags=re.I | re.S)
    text = re.sub(r'<!-- Google Tag Manager(?: \(noscript\))? -->.*?'
                  r'<!-- End Google Tag Manager(?: \(noscript\))? -->\s*',
                  '', text, flags=re.I | re.S)
    text = re.sub(r'<script\b[^>]*src="/assets/ganalytics\.php[^"]*"[^>]*></script>',
                  '', text, flags=re.I)
    text = re.sub(r'<script\b[^>]*src="(?:https?:)?//(?:statics\.a8\.net|'
                  r'110006162\.collect\.igodigital\.com|b92\.yahoo\.co\.jp|'
                  r's\.yimg\.jp/images/listing/tool/cv|www\.googleadservices\.com|'
                  r'www\.googletagmanager\.com/gtag|osoujihonpo\.com/lab/)[^"]*"[^>]*>'
                  r'\s*</script>\s*', '', text, flags=re.I | re.S)
    text = re.sub(r'<script\b[^>]*>(?:(?!</script>).)*?'
                  r'(?:UA-2197051-1|GTM-KKMLGNX|google_conversion|yahoo_conversion|a8sales)'
                  r'(?:(?!</script>).)*?</script>\s*', '', text, flags=re.I | re.S)
    text = re.sub(r'<noscript\b[^>]*>(?:(?!</noscript>).)*?'
                  r'(?:googleads\.g\.doubleclick\.net|googletagmanager\.com)'
                  r'(?:(?!</noscript>).)*?</noscript>\s*', '', text, flags=re.I | re.S)
    text = ICON_LINKS.sub(lambda m: m.group() if ICON in m.group() else "", text)
    text = MANIFEST_LINK.sub("", text)
    if '<title>' in text:
        text = re.sub(r'(<title>)(.*?)(</title>)',
                      lambda m: m.group(1) + tab_title(m.group(2)) + m.group(3),
                      text, count=1, flags=re.I | re.S)
    else:
        raise ValueError("HTML page has no title")
    if ICON not in text:
        text = re.sub(r'</head\s*>', ICON + "\n</head>", text, count=1, flags=re.I)
    if DEMO_SCRIPT not in text:
        text = re.sub(r'</head\s*>', DEMO_SCRIPT + "\n</head>", text, count=1, flags=re.I)
    if TRANSLATION_SCRIPT not in text:
        text = re.sub(r'</head\s*>', TRANSLATION_SCRIPT + "\n</head>", text,
                      count=1, flags=re.I)
    return add_typography_links(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed: dict[str, bytes] = {}
    pages = sorted(SITE.rglob("*.html"))
    manifest_paths = {record["path"] for record in manifest["files"].values()}
    unregistered_pages = [p.relative_to(SITE).as_posix() for p in pages
                          if p.relative_to(SITE).as_posix() not in manifest_paths]
    legal_pages = {"policy/index.html": "プライバシーポリシー",
                   "sitepolicy/index.html": "サイトのご利用にあたって",
                   "policy-1/index.html": "外部送信ポリシー",
                   "policy-2/index.html": "個人関連情報の取扱い",
                   "campaign/policy-1/index.html": "外部送信ポリシー",
                   "campaign/policy-2/index.html": "個人関連情報の取扱い"}
    for path in pages + list(SITE.rglob("*.js")) + [SITE / "sitemap.xml"]:
        if not path.is_file():
            continue
        old = path.read_bytes()
        if path.suffix == ".js" and not any(marker in old for marker in
                                           (b"logo.webp", b"0120241000", b"osoujihonpo",
                                            b"img-app750.webp", b"line_bnr.webp",
                                            *(name.encode() for name in OLD_NAMES))):
            continue
        rel = path.relative_to(SITE).as_posix()
        new_text = transform(old.decode("utf-8"), path.suffix == ".html")
        if rel in legal_pages:
            title = legal_pages[rel]
            notice = (f'<main><section class="l-section l-section--limited u-pt-0 u-pb-96_80">'
                      f'<div class="l-section-inner"><h1 class="c-page-heading">{title}</h1>'
                      '<p class="c-text">現在はデモ画面です。正式な規約・ポリシーは掲載しておりません。</p>'
                      '</div></section></main>')
            new_text = re.sub(r'<main\b[^>]*>.*?</main>', notice, new_text,
                              count=1, flags=re.I | re.S)
        if rel in ("campaign/180223-01/index.html", "campaign/osoujihonpo-app/index.html"):
            is_app = rel == "campaign/osoujihonpo-app/index.html"
            new_text = re.sub(r'<main\b[^>]*>.*?</main>',
                              '<main><section class="l-section l-section--limited u-pt-0 u-pb-96_80">'
                              '<div class="l-section-inner"><h1 class="c-page-heading">'
                              + ("アプリについて" if is_app else "ご予約について") + '</h1>'
                              '<p class="c-text">この画面はデモです。'
                              + ("アプリとの連携" if is_app else "予約先") + 'は設定されておりません。</p>'
                              '</div></section></main>', new_text, count=1, flags=re.I | re.S)
            new_text = re.sub(r'<title>.*?</title>', f'<title>{TAB_BRAND}</title>',
                              new_text, count=1, flags=re.I | re.S)
        if rel in ("campaign/outerwall_complete/index.html", "error/403/index.html",
                   "house-cleaning/room/mattress/index.html"):
            new_text = re.sub(r'[ \t]+(?=\r?\n)', '', new_text)
        new = new_text.encode("utf-8")
        if new != old:
            changed[rel] = new
    for path in SITE.rglob("*.css"):
        old = path.read_bytes()
        if not any(name.encode() in old for name in OLD_NAMES):
            continue
        new = transform(old.decode("utf-8"), False).encode("utf-8")
        if new != old:
            changed[path.relative_to(SITE).as_posix()] = new
    old_logo_css = "\n@media screen and (max-width: 767.98px) {\n  .c-header__logo { width: 175px; height: 70px; }\n}\n"
    logo_css = "\n.c-header__logo { width: 175px; height: 82px; }\n"
    for rel in ("assets/css/common.css", "assets/css/campaign/legacy-common.css",
                "assets/css/campaign/ac456_monthcp/common.css"):
        path = SITE / rel
        if not path.is_file():
            continue
        data = changed[rel].decode("utf-8") if rel in changed else path.read_text(encoding="utf-8")
        data = data.replace(old_logo_css, "")
        if logo_css not in data:
            data += logo_css
        if data.encode("utf-8") != path.read_bytes():
            changed[rel] = data.encode("utf-8")
    banner_css = """
.c-brand-banner{box-sizing:border-box;position:relative;display:flex;align-items:center;gap:14px;min-height:96px;width:100%;padding:8px 22px;background:#fff;color:#005bac;font-weight:700;text-align:left}
.c-brand-banner--prevention{background:#d1e7f7}
.c-brand-banner__logo{display:block;flex:0 0 145px;width:145px;height:80px;object-fit:contain}
.c-brand-banner__copy{display:flex;flex-direction:column;gap:2px;min-width:0}
.c-brand-banner__eyebrow{font-size:14px;color:#7d858c}
.c-brand-banner__eyebrow:empty{display:none}
.c-brand-banner__label{font-size:26px;line-height:1.35}
.c-brand-banner__arrow{margin-left:auto;font-size:36px;line-height:1}
@media screen and (max-width:767.98px){.c-brand-banner{min-height:174px;flex-direction:column;justify-content:center;gap:0;padding:9px 35px;text-align:center}.c-brand-banner__logo{flex:none;width:190px;height:102px}.c-brand-banner__copy{gap:0}.c-brand-banner__eyebrow{font-size:13px}.c-brand-banner__label{font-size:22px}.c-brand-banner__arrow{position:absolute;right:10px;top:calc(50% - 18px)}}
"""
    rel = "assets/css/common.css"
    data = changed.get(rel, (SITE / rel).read_bytes()).decode("utf-8")
    if banner_css not in data:
        changed[rel] = (data + banner_css).encode("utf-8")
    # Only SVG text metadata is changed; vector paths remain untouched.
    path = SITE / "assets/images/house-cleaning/aircon/wall/mv-txt.svg"
    if path.is_file():
        old = path.read_bytes()
        new = transform(old.decode("utf-8"), False).encode("utf-8")
        if new != old:
            changed[path.relative_to(SITE).as_posix()] = new
    app_manifest = SITE / "favicon/manifest.json"
    app_data = {"name": TAB_BRAND, "short_name": TAB_BRAND,
                "icons": [{"src": "/favicon/crystal-clean-home.svg", "sizes": "any", "type": "image/svg+xml"}]}
    new_manifest = (json.dumps(app_data, ensure_ascii=False, indent=2) + "\n").encode()
    if app_manifest.read_bytes() != new_manifest:
        changed["favicon/manifest.json"] = new_manifest
    assets = {
        "assets/images/crystal-clean-home.png": ROOT / "assets/images/brand/crystal-clean-home.png",
        "favicon/crystal-clean-home.svg": ROOT / "assets/images/docs/brand/favicon.svg",
        **{f"assets/images/common-parts/sns-icon/icon-{name}.png":
           ROOT / f"assets/images/brand/shared-ui/social/{name}.png"
           for name in ("x", "instagram", "tiktok", "youtube")},
        "assets/images/common-parts/sns-icon/icon-translate.png":
            ROOT / "assets/images/brand/header/translate-material-white-96.png",
    }
    missing_assets = [key for key, src in assets.items()
                      if not (SITE / key).exists() or (SITE / key).read_bytes() != src.read_bytes()]
    obsolete = ["assets/images/logo.webp", "assets/images/footer/footer-tel-sp.gif",
                "assets/images/footer/footer-tel-pc.gif", "favicon.ico",
                "assets/images/campaign/m10/logo.png", "assets/images/campaign/ots/sec7_logo.png",
                "assets/images/top/about-link_pc.webp", "assets/images/top/about-link_sp.webp",
                "assets/images/top/prevention-link_pc.webp", "assets/images/top/prevention-link_sp.webp",
                "assets/images/house-cleaning/top/about-link_pc.webp",
                "assets/images/house-cleaning/top/about-link_sp.webp"]
    obsolete += ["assets/images/top/banner/campaign_banner_02v2_pc.webp",
                 "assets/images/top/banner/campaign_banner_02v2_sp.webp",
                 "assets/images/house-cleaning/kv/hctop_banner_lineyoyaku_PC.webp",
                 "assets/images/top/pickup/img-app750.webp",
                 "assets/images/campaign/aircon-all-year/line_bnr.webp",
                 "assets/images/campaign/aircon-multiple-units/line_bnr.webp"]
    obsolete += [p.relative_to(SITE).as_posix() for p in (SITE / "favicon").glob("*.png")]
    if args.check:
        if changed or missing_assets or unregistered_pages or any((SITE / p).exists() for p in obsolete):
            raise SystemExit(f"Identity sync required: {len(changed)} files, {len(missing_assets)} assets, {len(unregistered_pages)} new pages")
        print(json.dumps({"pages_checked": len(pages), "identity_current": True}, ensure_ascii=False))
        return
    for rel, data in changed.items():
        (SITE / rel).write_bytes(data)
    for rel, src in assets.items():
        dest = SITE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if rel in missing_assets:
            shutil.copyfile(src, dest)
    for rel in obsolete:
        (SITE / rel).unlink(missing_ok=True)
    for url, record in list(manifest["files"].items()):
        rel = record["path"]
        if rel in obsolete:
            del manifest["files"][url]
        elif rel in changed:
            record.setdefault("source_sha256", record["sha256"])
            record["bytes"] = len(changed[rel])
            record["sha256"] = hashlib.sha256(changed[rel]).hexdigest()
    for rel in unregistered_pages:
        data = (SITE / rel).read_bytes()
        url = manifest["origin"].rstrip("/") + "/" + rel
        manifest["files"][url] = {"path": rel, "effective_url": url, "status": 200,
                                  "content_type": "text/html", "bytes": len(data),
                                  "sha256": hashlib.sha256(data).hexdigest(),
                                  "origin_type": "local-site-page"}
    for rel in [*assets, "assets/images/footer/footer-phone-demo-sp.svg",
                "assets/images/footer/footer-phone-demo-pc.svg", "assets/js/demo-contact.js",
                "assets/js/shared-translation-control.js", "assets/js/shared-translation.js",
                "assets/js/shared-translation-layout.js", "assets/css/translation-layout.css"]:
        data = (SITE / rel).read_bytes()
        url = manifest["origin"].rstrip("/") + "/" + rel
        manifest["files"][url] = {"path": rel, "effective_url": url, "status": 200,
                                  "content_type": "image/svg+xml" if rel.endswith(".svg") else
                                                  "image/png" if rel.endswith(".png") else
                                                  "text/css" if rel.endswith(".css") else "text/javascript",
                                  "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                                  "origin_type": "local-site-identity"}
    unique = {record["path"]: record for record in manifest["files"].values()}
    manifest["counts"].update(urls=len(manifest["files"]), unique_paths=len(unique),
                              bytes=sum(record["bytes"] for record in unique.values()))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pages": len(pages), "updated_files": len(changed),
                      "new_assets": len(missing_assets), "removed_assets": len(obsolete)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
