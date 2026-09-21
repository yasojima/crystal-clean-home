"""Publish contact controls as a disconnected, local-only demo."""
from pathlib import Path
from urllib.parse import urlsplit
from lxml import html, etree
import re

BASE = '/crystal-clean-home/'
NOTICE = 'デモサイトのため、実際のお問い合わせ・お見積もりの送信は行われません。入力内容が店舗へ届くことはありません。'

def prepare_demo(markup, path):
    if path.startswith('vendor/'):
        return markup
    doc = html.document_fromstring(markup)
    head = doc.find('head')
    for n in doc.xpath('//script[contains(@src,"contact-guard.js") or contains(@src,"ajaxzip3")]'):
        n.drop_tree()
    for n in doc.xpath('//script[not(@src)]'):
        if 'AjaxZip3.zip2addr' in (n.text or ''):
            n.drop_tree()
        elif n.text:
            n.text = re.sub(r'"youtubeUrl"\s*:\s*"[^"]*"', '"youtubeUrl":""', n.text)
    for a in doc.xpath('//a[@href] | //area[@href]'):
        href = a.get('href', '').strip()
        url = urlsplit(href)
        if url.scheme or href.startswith('//'):
            kind = 'phone' if url.scheme in ('tel', 'sms', 'fax') else 'email' if url.scheme == 'mailto' else 'line' if 'lin.ee' in href or 'line.me' in href else 'external'
            for attr in ['href', 'target', 'ping', 'download', 'onclick']:
                a.attrib.pop(attr, None)
            a.set('data-demo-action', kind)
            a.set('role', 'button')
            a.set('tabindex', '0')
            a.set('aria-haspopup', 'dialog')
    for n in doc.xpath('//*[@onclick]'):
        if re.search(r'gtag|window\.open|https?://|mailto:|tel:', n.get('onclick', '')):
            n.attrib.pop('onclick', None)
    for form in doc.xpath('//form'):
        form.set('action', '#')
        form.set('method', 'dialog')
        form.set('data-demo-form', 'true')
        for attr in ['data-original-action', 'data-contact-unconfigured', 'target']:
            form.attrib.pop(attr, None)
        for n in form.xpath('.//*[@formaction or @formmethod]'):
            n.attrib.pop('formaction', None)
            n.attrib.pop('formmethod', None)
        for n in form.xpath('.//input[@name="mw_wp_form_token" or @name="mw-wp-form-form-id"]'):
            n.drop_tree()
        if form.get('id') != 'mitsumoriForm' and not form.xpath('.//*[@data-demo-notice]'):
            note = etree.Element('p', {'data-demo-notice': 'true', 'class': 'demo-form-notice'})
            note.text = NOTICE + ' 動作確認には架空の情報をご利用ください。'
            form.insert(0, note)
    for n in doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," zip-button ")]'):
        n.set('data-demo-action', 'address')
    for n in doc.xpath('//iframe[@src or @data-src]'):
        src = n.get('src') or n.get('data-src', '')
        if src and (urlsplit(src).scheme or '/vendor/' in src):
            n.attrib.pop('src', None)
            n.attrib.pop('data-src', None)
            n.set('srcdoc', '<p style="font:16px sans-serif;color:#17354b;padding:24px">デモ表示：外部コンテンツへの接続は設定されていません。</p>')
    for img in doc.xpath('//img'):
        for attr in ['src', 'data-src']:
            if 'M_gainfriends_qr' in img.get(attr, ''):
                img.set(attr, BASE + 'brand/demo-qr.svg')
                img.set('alt', 'デモ表示：LINEのQRコードは未設定です')
    for n in doc.xpath('//a[@data-demo-action="email"]'):
        n.text = 'メール送信先は未設定です（デモ）'
    if path.startswith(('contact/', 'simulation-contact/')) and ('/thanks/' in path or '/confirm/' in path):
        replacements = {
            '送信完了': 'デモの操作完了',
            '送信内容の確認': '送信内容の確認（デモ）',
            'お問い合わせいただき、誠にありがとうございます。': 'デモをご確認いただき、ありがとうございます。',
            '内容を確認のうえ、担当よりご連絡をさせていただきます。今しばらくお待ちくださいますようお願い申し上げます。': NOTICE,
            '1～2日経っても連絡がない場合は、弊社にお問い合わせ内容が届いていない可能性がございます。': 'この画面はサンプルです。お問い合わせの受付や予約は成立しておらず、店舗からの返信もありません。',
            'その際はお手数ですがお電話（': '表示されている電話番号（',
            '）までご連絡ください。': '）もサンプルのため、発信できません。',
            'このページには直接アクセスできません。': 'デモ画面です。実際の送信は行われていません。',
            '各項目をご確認の上「送信する」ボタンをクリックしてください。': '送信前の確認画面のサンプルです。実際の送信先は設定されていません。',
            '入力いただいた情報を安全に送受信するためにSSL（暗号化送信）を使用しております。': '入力した内容を店舗へ送信する機能はありません。',
        }
        for n in doc.iter():
            if n.tag in ('script', 'style') or not isinstance(n.tag, str):
                continue
            for attr in ['text', 'tail']:
                value = getattr(n, attr)
                if value and value.strip() in replacements:
                    setattr(n, attr, value.replace(value.strip(), replacements[value.strip()]))
    if head is not None:
        for n in head.xpath('./meta[@http-equiv="Content-Security-Policy"] | ./script[@data-demo-guard] | ./link[@data-demo-style]'):
            head.remove(n)
        # The browser itself blocks form submissions, even if scripts fail or are disabled.
        csp = etree.Element('meta', {'http-equiv':'Content-Security-Policy', 'content':"form-action 'none'; connect-src 'self'; frame-src 'self'"})
        head.insert(1, csp)
        script = etree.Element('script', {'src': BASE+'brand/demo.js?v=1', 'data-demo-guard':'true'})
        head.insert(2, script)
        head.append(etree.Element('link', {'rel':'stylesheet','href':BASE+'brand/demo.css?v=1','data-demo-style':'true'}))
    return '<!DOCTYPE html>\n' + html.tostring(doc, encoding='unicode', method='html')

def publish_demo(root):
    import json
    manifest = json.loads((root/'capture.json').read_text(encoding='utf-8'))
    paths = sorted({f['path'] for f in manifest['files'] if f.get('html') and not f['path'].startswith('vendor/')})
    for path in paths:
        dest = root/'docs'/path
        dest.write_text(prepare_demo(dest.read_text(encoding='utf-8'), path), encoding='utf-8')
    return len(paths)

if __name__ == '__main__':
    print(publish_demo(Path(__file__).resolve().parent))
