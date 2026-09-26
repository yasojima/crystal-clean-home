# 初めての方へ LP仕様

更新：2026-09-26。対象：`/first/`。初めての方へ・清掃への取り組み・感染予防を一つのLPに統合する。

## 画像を主役にする制作方式

人間の修正指示により、説明カードやCSSの吹き出しを中心にする方式を終了する。見出し・人物・背景・吹き出し・コマ枠を一体で仕上げた画像を先に制作し、基調色 `#e3f1fc` の上に縦に並べる。画像間には短い説明とCTAを配置する。HTML/CSSは配置・端末切替・リンク・開閉・読み上げに用いる。

中央のLPは最大1040px。紺 `#06408c`、青 `#096ba1`、水色 `#e3f1fc`、白を使う。室内の自然光、木や石の素材感、青い曲線を背景画に含め、場面と訴求に強弱を付ける。元の参考サイトの黄色・緑の配色や人物、数値、認定、電話番号を転載しない。

## 読む順番

完成画像のファーストビュー → 画像CTA → 相談前の4コマ → 清掃の6つの姿勢 → CTA → 作業中の4コマ → 衛生管理 → 既存の比較イメージ2組 → 作業後の4コマ → CTA → 掲載用サンプルの声3件 → 匿名比較の画像 → CTA → 既存8カテゴリ → 5段階の流れ → FAQ5件 → 最終CTA・問い合わせ。

漫画は3章・計12コマの連続シーンとする。相談前の不安、説明への納得、専門的な判断と養生、仕上がりと日頃のお手入れへと展開する。同じ女性客と男性スタッフを使い、髪型・顔立ち・服装を統一する。参考イラストに近い輪郭線と塗りの漫画調を使用し、リアルなアニメ調の人物には戻さない。吹き出しの尾は発言した人物を指す。

丁寧で落ち着いた清掃業者らしい文体を維持し、`source/first/lp-copy.md` の承認済み原稿を要約する。実証していない実績、満足度、効果、競合優位は追加しない。漫画はサービス説明用のイメージで、実際のお客様の体験談ではない旨を表示する。

参考の情報設計：[LP構成ガイド](https://losta.co.jp/labo/landing-page-guide/)、[公式の清掃方針](https://www.osoujihonpo.com/about/)、人間が提示したPC/SPの長尺LP・漫画LP。悩み、解決の過程、専門性、判断材料、FAQ、行動の順序を取り入れる。

## 画像と端末別表示

- 完成WebPは14点。基本8点（表紙、漫画3章、6つの姿勢、衛生管理、比較表、CTA）とスマホ用6点（表紙、漫画3章、衛生管理、CTA）。
- 600px以下ではpicture/sourceでスマホ画像に切り替える。漫画はPCの2×2から、スマホの上から読む縦4コマへ描き直す。単純縮小や部分切り抜きで代用しない。
- 画像内の文字を見切れさせない。完成画像は全体をwidth:100%、height:autoで表示し、object-fit:coverを使わない。スマホの会話は縦の余裕を確保して読みやすくする。
- 比較画像のみ最小幅900pxで内部横スクロールする。ページ全体を横にはみ出させない。テキスト版の表にも独立した横スクロールを用意する。
- 商品選択はPC4列・SP2列、声はPC3列・SP1列。清掃前後の画像には常にラベルを表示する。
- 作成には内蔵image_genを使用。生成指示と採用元は`brand/first-lp/art-assets.json`。変換時は原寸を保ち、WebP quality 94とする。原生成PNGはツールの保存先に保持する。
- 旧画像のうち文字のないhero.webpは人物の初期基準・OG用として保持する。旧4コマ等を表示用に重複公開しない。

## CTAと比較表

CTAは背景・人物・見出し・電卓アイコン・赤いボタン・右下角丸・右矢印まで完成画像に含める。PC/SPそれぞれの画像を5箇所で再利用する。画像全体を意味のあるa要素で囲み、行き先は既存共有正本`brand/estimate-cta/template.html`から取得する。現行は`/services/`。他のページのCTAは変更しない。未設定の電話番号や新しい受付フォームは追加しない。

比較対象は人間の承認に従い架空のA社〜E社。自社を含む全価格が税込・仮設定であることを画像内と隣接HTMLに表示する。実案件では同じ条件の確認済み資料に置き換える。価格は`art-content.json`のcomparisonに記録し、画像内の24価格とテキスト表の一致を確認する。商品カタログ・カートの価格には流用しない。

## 既存素材と本文

`materials.json`で商品側の比較画像2組と口コミ3件の選択を管理する。画像は原本と同一、口コミの見出し・本文も正本から再利用する。生成イメージで実際の施工写真ではない旨と、掲載用サンプルで実際の口コミではない旨を表示する。

8カテゴリの名称・URLは`brand/service-cards/template.html`、画像は端末別カテゴリCSSと`brand/category-illustrations-v2/`を再利用する。商品・数量・オプション・カートの既存導線へ接続する。LP内で料金計算を作らない。

## SEOとアクセシビリティ

Google Search Centralの[画像SEO](https://developers.google.com/search/docs/appearance/google-images)と[非表示テキストの扱い](https://developers.google.com/search/docs/essentials/spam-policies#hidden-text-and-link-abuse)を再確認。画像はCSS背景ではなくimg/pictureで置き、意味のあるalt、実寸width/height、見出しと関連する短い説明を付ける。冒頭は優先読み込み、下部は遅延読み込みとし、スマホにPC/SP両画像を同時表示しない。

画像内の会話・清掃方針は、誰でも開いて読める「画像の内容を文章で読む」に静的HTMLで掲載する。比較表にも同じ数値のHTML表を用意する。これらは読みやすさ・読み上げ・テキスト確認のためのdetails/summaryであり、検索エンジンだけに文章を見せる手法は使わない。H1は1つ、本文はH2/H3で整理。独自title・description・canonical・OGを保持し、架空の口コミ・評価の構造化データは追加しない。

## 正本と生成

| 対象 | 正本 |
| --- | --- |
| 統合原稿 | source/first/lp-copy.md |
| 構成と短い補足文章 | brand/first-lp/template.html |
| 完成画像 | brand/first-lp/art/ |
| 画像生成指示・採用元 | brand/first-lp/art-assets.json |
| alt・テキスト版・比較数値 | brand/first-lp/art-content.json |
| 既存素材の選択 | brand/first-lp/materials.json |
| PC/SPの配置 | source/device/{desktop,mobile}/css/first-lp.css |
| CTAの遷移先 | brand/estimate-cta/template.html |
| 生成 | first_lp.py → shared_ui.py |

`python -B first_lp.py` または`python -B shared_ui.py`で生成する。出力はsource/first/index.htmlのmain、docs/first/index.htmlとdocs/brand/first-lp。docsのみの直接編集は禁止。CSSハッシュを更新し、3アンカー first-introduction・cleaning-approach・infection-preventionを保持する。全体ナビは4項目、旧reasonは再生成しない。

検証は`test_first_lp.py`（再生成、本文一致、画像寸法・レスポンシブ画像、会話テキスト、比較データ、CTA、既存素材）と`test_device_ui.py`。非表示IABでPC/SPの画像、文字、開閉、横スクロールとリンクを確認する。人間・実機の最終検収は別とする。
