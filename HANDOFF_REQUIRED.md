# Crystal Clean Home 引き継ぎ（受領確認済み・閉鎖）

2026-10-07、新担当チャット `01a1145d-d0bc-7f91-a817-14226b818bb3` が正本を確認して受領した。受領記録は `evidence/2026-10-07/handoff/intake.json`。恒久仕様は各正本を参照し、本書から追加作業を開始しない。

ユーザーが現担当から新しい担当への引き継ぎを明示的に要求した。新担当は下記の現行正本を読み、受領を記録したうえで次のユーザー指示を待つ。この文書は一件だけの引き継ぎ入口であり、恒久仕様は各正本に記録済み。

## 完了地点

- 公開先は https://yasojima.github.io/ 。Pages `de800205dd9f0d45e068119167f961849b551e57`、Actions37565446402成功。84変更ファイルのHTTP取得・SHA-256一致を確認済み。
- 共通のカテゴリアイコン・白い枠・青い枠・見出しを参考HTML/CSSの寸法で統一。全61ページは共通正本を参照する。HOMEお悩みのタブ幅は比較部品と同じ最大750px。
- 商品８カテゴリの冒頭をヘッダーの実高と画面高から自動計算。カードが多い場合は完全な行を表示し、一覧内で残りをスクロールできる。末尾フッターの計算と独立しており、セクション増減の検査を通過。
- `/beginner/` の通常PCとスマホは縮小前へ復旧。追加の縮小・余白・文字・CTA・列数調整は幅768px以上かつ高さ720px以下だけ。1439×799を含む通常PCを再縮小しない。既存iOS背面フィルター修正を保持。
- HOME本編へ上部エアコン２台バナーと後半３テーマのNO IMAGE枠を実装・公開。上部リンクは既存エアコンページ。割引は既存価格正本から生成。
- HOME既存法人バナーのリンク先 `/business/cleaning/` を新設。参考の紹介２段落・４説明・12写真一覧・締めを元に独自原稿で構成し、冒頭写真バナーだけ除外。人物なし・別場面の実写調13素材を新規制作、７本文段落の文字数・改行を照合。共通メニュー／フッターも同ページへ接続。相談CTAは既存のデモ案内で、本番送信なし。
- 全61ページと逆順を含む1,071条件、共通冒頭158条件・末尾33条件・法人34条件をローカル確認。冒頭158・末尾33・法人34・LP復旧９条件を公開先でも確認。PC／スマホ保存画面も目視確認済み。

## 次に読む正本

1. 親ディレクトリのAGENTS.mdとSOURCE_AND_HISTORY_POLICY.md
2. Crystal-Clean-Home_要件定義書.md、Crystal-Clean-Home_仕様書.mdのCHG-2026-10-07-014〜017と最新公開記録
3. Crystal-Clean-Home_タスク確認表.md、変更履歴.md、Crystal-Clean-Home_見積もり導線仕様.md
4. prototypes/home-wireframe/README.md
5. evidence/2026-10-07/first-view-fit/verification-summary.json、final-publication.json

## 実装の所有元

- 共通header／footerはsource/shared-ui、生成はtools/build_shared_ui.py。生成HTMLをページ別に分岐させない。
- 共通カテゴリはcommon.css／aircon-layout.css、冒頭はaircon-hero.css／service-first-view.js、末尾はsite-footer.css／aircon-header.js。
- LPはbeginner-lp.css。通常PC・スマホへ短いPCの調整を広げない。
- HOME追加２領域はtools/home_pickups.py／home-pickups.css。比較画面は本編を入力として生成する。
- 法人原稿はsource/office-cleaning/content.json、画像プロンプトは同フォルダーのimage-prompts.json（built-in image_gen）。生成はtools/build_office_cleaning.py、画像はsource/site/assets/images/office-cleaningの13PNG。

## 維持・後続事項

- ユーザーは速やかな公開と確実な表示確認を要求している。確認なしの完了・完全一致を報告しない。既存の採用済み構図と指定外の画面条件を変更しない。
- 後半３テーマの漫画LPはユーザーがGPTで台本・場面を制作して渡す予定。今回は骨格のみで完了。台本を推測して制作しない。
- 「最新のお知らせ」３案はローカル比較画面だけ。未採用。却下された重複メニュー・簡易見積もり・追加フローを復活させない。
- 実機iPhoneの受入、３LPの台本、本番受付API・メール接続は後続。Windows検証を実機受入とは扱わない。
- 既存カート395商品／460選択肢、既存バナー・動画・漫画・iOS修正、末尾のヘッダー表示とCTA退避を守る。
- 非表示で作業する。検証ブラウザは同時に１件、終了後に閉じる。ユーザーのプレビュー8773は残す。Git履歴の再取得や大量の複製・不要な画像生成を行わない。
- 古い未追跡のevidenceは今回の変更と無関係。無差別に登録・削除しない。ソースGitとPages Gitは別で、Pages checkoutは `C:\Users\yasoj\AppData\Local\Temp\cch-pages-deploy-20261003`。

## 受領操作

新担当は正本を読み、Gitの現在HEAD・公開記録・未完了事項を確認して、`evidence/2026-10-07/handoff/intake.json` に担当チャットID・読んだファイル・理解した制約・待機状態を記録する。実装や公開を追加せず「引き継ぎ受領、次の指示待ち」と返答する。受領後は本書を閉鎖扱いとし、確定事項の変更時は恒久正本を更新する。
