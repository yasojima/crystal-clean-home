from pathlib import Path
from urllib.request import urlopen, Request
from concurrent.futures import ThreadPoolExecutor
import json, subprocess

root = Path(__file__).resolve().parent
commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=root, text=True).strip()
paths = ['index.html','contact/index.html','line/index.html','service/house/air-conditioner/index.html','brand/demo.js','brand/demo.css']
def check(path):
    url = 'https://yasojima.github.io/crystal-clean-home/' + path.removesuffix('index.html') + '?release=' + commit[:7]
    with urlopen(Request(url, headers={'Cache-Control':'no-cache'}), timeout=30) as response:
        body = response.read().decode('utf-8').replace('\r\n','\n')
        expected = (root/'docs'/path).read_text(encoding='utf-8').replace('\r\n','\n')
        return {'path':path,'url':url,'status':response.status,'matchesLocal':body==expected}
with ThreadPoolExecutor(max_workers=6) as pool:
    results = list(pool.map(check, paths))
report = {'commit':commit,'workflow':'https://github.com/yasojima/crystal-clean-home/actions/runs/35664113073','results':results}
(root/'publication.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
assert all(r['status']==200 and r['matchesLocal'] for r in results)

change = '''
## CHG-2026-09-22-COPY-DEMO 文章と接続先

- サイト本体387ページへ文章置換を適用。延べ37,604箇所、変更前後1,835組を文章変更一覧.mdに記録。料金・事実・引用・画像文字等の維持範囲も同書に記載。
- 通常の案内文へデモ注意書きを混ぜた実装を修正。電話・LINE・外部接続・最終送信の操作時のみ中央ポップアップで説明する。
- 全387ページの外部リンク、8フォームの送信先を解除。入力確認とブラウザ内の見積計算を維持。
- 公開コミット：5e28374182f03bab776bd4a9c15956817d1d7308。Pages実行35664113073成功。公開4ページと共通JS/CSSのHTTP 200・ローカル一致を確認（改行正規化）。
- 非表示IABで電話・LINE・入力確認から最終送信・Esc・390px幅の表示を確認。全ページの目視検証ではない。
- 要件定義書v1.2と関連MDを指定のローカル内で更新。Driveの作成・編集・同期は実施していない。
'''
for name in ['CHANGELOG.md','SITE_VERIFICATION.md']:
    path=root/name
    path.write_text(path.read_text(encoding='utf-8')+change,encoding='utf-8')
