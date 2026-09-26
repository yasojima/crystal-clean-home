# 初めての方へ LP仕様

更新：2026-09-26。対象：`/first/`。初めての方へ・清掃への取り組み・感染予防への取り組みを一つのLPとして整理する。

## 構成と原稿

冒頭の訴求と見積CTA → 悩みの提示 → 吹き出し付き4コマ → 見積CTA → 清掃への取り組み6項目 → 感染予防3項目 → 匿名5社との比較サンプルとCTA → お約束 → ご利用の流れ5段階 → FAQ5項目 → 最終CTA・お問い合わせ。

`source/first/lp-copy.md` の承認済み原稿を要約・整理する。丁寧で落ち着いた清掃業者らしいビジネス文体を維持し、判断・説明・養生・衛生管理・仕上がり確認という具体的な行動で専門性と責任感を伝える。実証していない実績・満足度・効果・競合優位の断定は追加しない。

## 漫画と端末別表示

- 人間の修正指示により、従来のリアルなアニメ調ではなく、参考イラストに近い太い輪郭線・簡潔な塗り・親しみやすい顔立ちの説明漫画調を使用する。
- 冒頭画像の女性と男性スタッフをキャラクターの基準とする。4コマでも髪型・顔立ち・服装を揃え、男性に眼鏡を付けない。表情・姿勢だけを場面に合わせる。今後も新しいコマには冒頭画像を人物の参照として渡す。
- 漫画は相談→事前説明→清掃→仕上がり確認。吹き出しと説明は画像へ焼き込まず、表示されるHTMLの文章とする。実際のお客様の体験談ではない旨を明記する。
- PCは4コマを左から右へ並べ、601〜992pxは2列、600px以下は1列で上から順に読む。比較表だけ内部を横スクロールし、狭い画面ではメニュー列を固定する。
- 基調色は紺 `#06408c`、水色 `#e3f1fc`、白。CTAは既存の赤/白反転・電卓アイコン・右下角丸の部品と端末別CSSを生成時に再利用する。未設定の電話番号は置かない。リンク先は既存の見積メニューとお問い合わせ。

## 比較表

人間の承認に従いA社〜E社を架空の比較対象とする。自社を含む税込価格は仮設定であることを表の直前に常時明示し、実在企業の料金・評価として扱わない。実案件で使う場合は、同条件で確認した資料と承認済み料金へ置き換える。比較用の価格は商品カタログ・カートに追加しない。

## SEOとアクセシビリティ

Google Search CentralのSEOスターターガイドを確認。主要本文・吹き出し・比較表は静的HTMLで表示し、検索向けの隠し文章は置かない。H1は1つ、H2/H3で構造化し、画像には説明的なaltと実寸のwidth/heightを付ける。下部画像は遅延読み込み、冒頭画像は優先読み込み。独自title・description・canonical・OG情報を生成する。FAQはキーボードでも開閉できる標準details/summary、比較表はcaption・見出しセルとフォーカス可能なスクロール領域を使う。架空の口コミや実績の構造化データは追加しない。検索順位やインデックス登録の保証はしない。

参考：[Google SEOスターターガイド](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)、[LP構成の解説](https://losta.co.jp/labo/landing-page-guide/)。

## 正本と生成

| 対象 | 正本 |
| --- | --- |
| 統合原稿 | source/first/lp-copy.md |
| 公開する構成・本文・吹き出し | brand/first-lp/template.html |
| 画像・生成指示の記録 | brand/first-lp/images/、image-prompts.json |
| PC/SPの配置 | source/device/{desktop,mobile}/css/first-lp.css |
| CTAの共有元 | brand/estimate-cta/template.html、端末別css/brand/estimate-cta/style.css |
| 生成 | first_lp.py → shared_ui.py |

`python -B first_lp.py` または `python -B shared_ui.py` で生成する。全体buildでもshared_uiから実行する。生成結果はsource/first/index.htmlのmain、docs/first/index.htmlとdocs/brand/first-lp。docsだけを直接編集しない。CSS内容のハッシュでキャッシュを更新する。既存の3アンカー `first-introduction`・`cleaning-approach`・`infection-prevention` を維持する。

検証：`python -B test_first_lp.py`（再生成の安定性・アンカー・表示HTML・比較サンプル・画像参照・SEO）、`python -B test_device_ui.py`。非表示IABでPC/SPの描画・吹き出し・FAQ・横スクロール・CTA遷移を確認する。実機検収と事業者情報・サービス方針・価格の最終承認は別とする。
