"""Write the local, reviewable editorial change record."""
from pathlib import Path
from collections import OrderedDict
import json

root = Path(__file__).resolve().parent
pages = json.loads((root/'copy-change-log.json').read_text(encoding='utf-8'))
unique = OrderedDict()
for page in pages:
    for change in page['changes']:
        pair = (change['before'], change['after'])
        if pair not in unique:
            unique[pair] = {'id': len(unique)+1, 'pages': []}
        if page['path'] not in unique[pair]['pages']:
            unique[pair]['pages'].append(page['path'])
def cell(text):
    return text.replace('|', '\\|').replace('\n', '<br>')
lines = ['# サイト文章の変更一覧', '', '更新日：2026-09-22', '',
    '清掃サービスとしての丁寧で落ち着いた語調を維持し、サービス説明、利用案内、見出し、FAQ、コラム、地域ページの共通説明などを言い換えました。ページ構成・セクション順序・共通配色・書体は維持しています。', '',
    f'変更を適用したHTMLは{len(pages)}ページです（取得一覧の388件のうち1件は同じファイルへの別表記）。変更履歴は延べ{sum(len(p["changes"]) for p in pages):,}箇所、変更前後の組み合わせは{len(unique):,}種類です。共通文章は下表にまとめ、ページ別の参照番号を後半に記載しました。', '',
    '## 表示と操作の方針', '',
    'ページ本文には「ご予約」「担当者から返信します」等の通常の案内を掲載します。デモである旨は本文に追加せず、電話・LINE・メール・外部リンクを押した時、またはフォームの最終送信時の中央ポップアップに限って表示します。入力確認画面から「送信する」を押すと案内が表示され、入力情報は送信・保存されません。', '',
    '## 今回の変更に含めない内容', '',
    '料金・数量・対応地域・固有名詞・所在地・沿革等の事実情報、引用・お客様の声、地域固有の説明の一部は維持しています。これらを自社の実績として確認したものではありません。画像内の焼き込み文字、構造化データ、メタ説明文もこの文章置換の対象外です。全ページに変更を適用しましたが、掲載されている全ての文字列を書き換えたという意味ではありません。', '',
    '清掃方法の記事は、読み替えによって危険な手順を強めないよう、製品表示と取扱説明書を優先する表現に調整しています。確認資料：[花王・塩素系製品](https://www.kao.com/jp/qa/detail/16568/)、[花王・業務用製品の使用方法](https://pro.kao.com/jp/products/kps08/4901301506177/)、[FUJIOH・お手入れFAQ](https://www.fujioh.com/support/faq/faq-fujioh)。', '',
    '## 変更前と変更後', '', '| 番号 | 変更前 | 変更後 | 適用ページ数 |', '| --- | --- | --- | --- |']
for (before, after), item in unique.items():
    lines.append(f'| {item["id"]} | {cell(before)} | {cell(after)} | {len(item["pages"])} |')
lines += ['', '## ページ別の変更番号', '', '| ページ | 上表の変更番号 |', '| --- | --- |']
for page in pages:
    ids = sorted({unique[(c['before'], c['after'])]['id'] for c in page['changes']})
    lines.append(f'| /{page["path"].removesuffix("index.html")} | '+', '.join(map(str, ids))+' |')
lines += ['', '## 再生成と保存先', '', '文章の編集正本はcopy/ja.json、適用処理はcopywriting.pyです。build.pyで取得ソースへ文章置換を適用し、続いてdemo.pyで外部接続を解除します。変更履歴はcopy-change-log.json、本書および関連MDはこのローカルプロジェクト内に保存します。Driveへの書き込みは行いません。', '']
(root/'文章変更一覧.md').write_text('\n'.join(lines), encoding='utf-8')

demo = '''# デモ時の操作仕様

更新日：2026-09-22

通常のページには、予約・相談・返信など通常のサービス案内を掲載する。本文へデモの注意書きや受付不可の案内を追加しない。

| 操作 | 表示・動作 |
| --- | --- |
| 電話番号 | 中央のポップアップで、デモサイトで実際の発信は行われない旨を表示 |
| LINEの予約・友だち追加、案内画像 | ポップアップを表示。LINEアカウントへ接続しない |
| メール・外部リンク | ポップアップを表示。メールアプリや外部サイトを開かない |
| 問い合わせフォーム | 入力内容の確認後、「送信する」でデモ案内を表示。送信しない |
| 見積もりの最終送信 | デモ案内を表示。送信しない。金額計算はブラウザ内で維持 |
| サービス案内・入力フォームへの内部リンク | 通常どおりページを移動 |
| 住所検索 | 案内を表示し、外部の検索先へ接続しない |

ユーザー提供の見本に合わせて背景を暗くし、中央の白いパネルに見出し・説明・「閉じる」を配置する。サイト共通の青系配色を使用する。電話等の案内に送信ボタンを出さない。Esc・背景クリックでも閉じ、操作元へフォーカスを戻す。

編集正本：demo.py、brand/demo.js、brand/demo.css、brand/demo-qr.svg。通常のpython build.pyにも適用する。操作機能のみ再生成する場合はpython build.py --demo-only。

静的HTMLの送信先・外部href・旧フォームトークンを除去する。CSPでもform-actionとconnect-srcを禁止し、スクリプトが動かない場合も送信しない。入力内容を外部送信・永続保存しない。

検証：387ページ、外部への有効なリンク0件、8フォームの送信先解除、通常本文のデモ注意書き0件。電話2,935、LINE171、メール2、その他外部85、住所検索2箇所。verify_demo.pyで確認。非表示IABで電話案内、入力確認、最終送信、390px幅の表示を確認した。ユーザーのChrome・右側プレビューは操作していない。
'''
(root/'DEMO_MODE.md').write_text(demo, encoding='utf-8')
req = root/'Crystal-Clean-Home_要件定義書.md'
text = req.read_text(encoding='utf-8').replace('版：1.1', '版：1.2')
text = text.replace('参照元の文章・写真・料金表等は型を保存するために残すもので、', '参照元の写真・料金表・未確定の事実情報は型を保存するために残すもので、')
text += '\n## サイト全体の文章と外部接続\n\n[変更 2026-09-22 / CHG-2026-09-22-COPY-DEMO]\n清掃業者としての落ち着いた丁寧語を保ち、全ページの見出し・説明・利用案内を独自の言い回しへ変更する。料金等の事実や引用を創作しない。構成を変更しない。変更前後は文章変更一覧.mdに保存する。ページ上は通常の予約・返信の案内を掲載し、デモの注意書きを常設しない。電話・予約・外部接続・最終送信の操作時のみ、中央ポップアップで実際の発信・接続・送信を行わないことを案内する。内部ページ移動と見積計算は維持する。詳細はDEMO_MODE.md。\n'
req.write_text(text, encoding='utf-8')
for name in ['AGENTS.md', 'PROJECT_MANIFEST.md', 'EDITING_GUIDE.md', 'Crystal-Clean-Home_制作準備書.md']:
    path = root/name
    text = path.read_text(encoding='utf-8').replace('要件定義書v1.1', '要件定義書v1.2').replace('要件定義書.md v1.1', '要件定義書.md v1.2')
    text += '\n[更新 2026-09-22] 文章置換はcopy/ja.jsonとcopywriting.pyで共通管理し、変更前後は文章変更一覧.mdを参照する。デモ案内は通常本文には出さず操作時のポップアップに限定する。接続解除と案内の仕様はDEMO_MODE.mdを参照。\n'
    path.write_text(text, encoding='utf-8')
print(json.dumps({'pages':len(pages),'uniqueChanges':len(unique),'report':'文章変更一覧.md'}, ensure_ascii=False))
