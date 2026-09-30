# Crystal Clean Home — 現行状態の引継ぎ

更新：2026-10-01。ユーザーが「HUDが終わったら、重たいので新しいエージェントへ引継ぎ」と明示依頼したため作成。

## 最初に行うこと

このファイル、要件定義書、変更履歴、Git状態、最新の検証JSONを読み、受領と現在地だけを短く報告する。HUD作業は完了済み。新しいユーザー指示が来るまで追加改修しない。ユーザーに過去の経緯を説明し直してもらわない。

## 正本と最優先の経緯

- 保存プロジェクト：Crystal Clean Home。projectId：76b77638-9f25-49f5-809a-9e3ca8c373a2。
- 作業正本：C:/Users/yasoj/codex Projects/Crystal Clean Home。
- 親のAGENTS.mdとSOURCE_AND_HISTORY_POLICY.mdを適用する。
- ユーザーは旧サイト基盤・旧仕様・旧要件などのリセットを明示指示済み。旧AGENTSで説明されていたsource/device、brand、publisher、shop.py、reference.py等は現在の構成ではない。復活させない。
- 現行PROJECT_MANIFEST.mdは存在しない。Route/PASS/EXECUTION_READYを推測で新設しない。handoff-codex-taskスキルのRoute別前提はリセット後に成立しないため、同一保存プロジェクトへの標準タスク作成、自動プロンプト送付、受領確認を行う。
- 現在のサイト正本はsource/site/。現行仕様はCrystal-Clean-Home_要件定義書.md。ソース取得・加工後のファイル情報はsource/manifest.json。
- 要望のないデザイン・内容・機能の作り替えはしない。丁寧な日本語で、実施と検証の範囲を正確に伝える。
- サブエージェントを使わない。ブラウザー検証は非表示IABのみ。ユーザーのChrome・右側プレビューを操作しない。外部AI監査・PDCAは明示指示がない限り適用しない。Driveへ書き込まない。

## 現在のサイト

- ユーザーはおそうじ本舗サイト一式の利用許可を得ていると明示回答し、公開画面側の複製とGitHub公開を依頼した。カート・予約・問い合わせのサーバー接続は後から行うことも明示承認済み。
- その後、FCパートナー募集・店舗求人・関連サービス・お役立ち情報・店舗一覧と配下の地域/店舗ページを不要と指定。source/scope.jsonに対象を定義し、ページ・案内リンク・専用素材を除外済み。
- 当初約3.46GBだった公開データは現在約179MB。全413 HTML、サイトファイル2,202件（HUDを含む）。本文や共用CSS/JS/画像は指定部分以外を維持。
- 旧LP・画像素材はプロジェクトのassets/に保管。公開対象には含めていない。assets/には画像1,681件とLP_materials.zipがある。勝手に削除・改変しない。
- 除外ファイル12,811件はC:/Users/yasoj/OneDrive/デスクトップ/削除用/Crystal Clean Home_除外ページ_2026-10-01に退避。永久削除はユーザーが行う。
- 旧構成退避先：C:/Users/yasoj/OneDrive/デスクトップ/削除用/Crystal Clean Home_旧構成_2026-10-01。現在の土台として参照・復元しない。

## 最新の完了作業：Viewport HUD

- 全HTMLのheadに/assets/js/viewport-hud.jsをdeferで読み込む1タグだけを追加。HTMLの既存部分は変更していないことを全413ページで確認済み。
- 共通実装：source/site/assets/js/viewport-hud.js。
- 右端・下端から各1px、黒背景、白い10px等幅文字、高さ18px、固定表示、z-index 2147483647。pointer-events:noneで下の操作を妨げない。
- 表示：window.innerWidth × window.innerHeight px | 区分名。
- HUD表示区分：MOBILE <768px、TABLET 768〜1023px、DESKTOP >=1024px。サイト本体の既存レスポンシブ指定は変えていない。
- resize時にrequestAnimationFrameでリアルタイム更新。二重生成防止、aria-hiddenあり。
- tools/apply_viewport_hud.pyは全HTMLへの共通タグ追加と、HTML/HUDのmanifestハッシュ更新を行う。再実行してもタグは重複しない。
- ローカル390/767/768/1023/1024/1440pxで表示・境界・右下1px・18px高・操作透過を確認。商品詳細でスクロール時の固定も確認。
- 公開先でも390×844 MOBILE、800×700 TABLET、1280×800 DESKTOPへ同じページのリサイズで更新することを確認済み。
- source/viewport-hud-verification.json、source/verification.json、source/deployment-verification.json、source/browser-verification.jsonに検証範囲を記録。
- 全ページ目視・実機・受付処理は未検収。既存の元サイト依存/取得できなかった外部素材を完全解消したとは主張しない。

## Gitと公開

- ソースGitHub：https://github.com/yasojima/crystal-clean-home 。ブランチmain。
- HUDの公開検証までのソースコミット：d5c507a0574e4774bb0b8a58280cf92a641428f7。その後の引継ぎコミットはGitで確認。
- 公開サイト：https://yasojima.github.io/ 。ルート相対URLを維持するためユーザーサイトのルートで公開。
- 配信用GitHub：https://github.com/yasojima/yasojima.github.io 。main、Pagesはbranch source /、.nojekyll使用。
- 現在の公開コミット：a7e737edb5e593dc2727352c2b5219a46bf4cff7。Pages run 36762530754成功。
- 配信用ローカルcheckout：C:/Users/yasoj/AppData/Local/Temp/cch-pages-host。ローカルブランチcodex/static-publishからorigin HEAD:mainへpush。
- 公開するのはsource/site/の内容だけ。プロジェクト直下assets、資料、manifest等を混ぜない。
- 同checkoutの旧ローカルmainや無視対象.github/workflowsは使わない。OAuthにworkflow権限がないため、workflowの新規pushは拒否される。現在は標準Pages公開で正常稼働しており権限拡張は不要。
- 公開変更は通常のcommit/push。履歴のforce push/resetはしない。
- Python整合確認：python -X utf8 tools/verify_public_site.py --git（Gitコミット後）。公開HTTP確認：python -X utf8 tools/verify_deployed_site.py。
- ローカル表示：python -X utf8 -u tools/serve_public_site.py（127.0.0.1:8769）。確認後は停止する。

## 残作業と引継ぎ受領

- HUDの実装・公開・検証に残作業なし。次はユーザーの新しい指示を待つ。
- 元タスク側で確認用ブラウザーのviewportを解除し、確認タブを閉じ、プレビューサーバーを停止する。
- 新規タスクへの自動送付・読み取り開始の受領は、元タスク側がこの欄に追記する。受け側はこのファイルを変更せず、読み取りと受領報告だけを行う。

### 自動引継ぎ受領記録

- 宛先threadId：01a0f3b4-8faf-7aa2-8b67-f312ac4d617c（local、同一保存プロジェクト）。
- 新規タスク作成と初回引継ぎプロンプトの自動送付：成功。
- 宛先の応答：「引継ぎ内容の読み取りを開始します。HANDOFF.mdを起点に、現行の要件・変更履歴・検証記録・Git状態を確認します。ファイルの編集や追加改修は行いません。」
- 宛先で実際の読み取りコマンド完了も確認。受領開始を確認済み。
- 元タスクの確認タブは閉じ、viewport設定を解除、ローカルプレビューは停止済み。
