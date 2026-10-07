# エアコン２台バナー・３案比較

2026-10-07のユーザー依頼によるローカル提案です。再提案の指示に基づき、画像より主訴求と数字を強くし、左に訴求・価格・CTA・条件、右に２台のエアコンを置く３案へ更新しました。公開案の採用は未決定です。

- [３案を並べて見る](http://127.0.0.1:8773/home-wireframe/aircon-banner/)
- [AをHOME内で見る](http://127.0.0.1:8773/home-wireframe/aircon-banner/context.html?banner=A#home-pickup-banner)
- [BをHOME内で見る](http://127.0.0.1:8773/home-wireframe/aircon-banner/context.html?banner=B#home-pickup-banner)
- [CをHOME内で見る](http://127.0.0.1:8773/home-wireframe/aircon-banner/context.html?banner=C#home-pickup-banner)

| 案 | 見せ方 | 主な訴求 |
| --- | --- | --- |
| A | 黄色×青・薄いドットと放射・オレンジCTA | 4,400円お得を最大158pxで主役にした販促型 |
| B | 白×水色×青・オレンジラベル・黄色帯 | １台あたり11,000円を最大138pxで主役にした料金理解型 |
| C | クリーム×青・オレンジ・黄色下線 | ２台の文字を最大114px、まとめてお得にキレイを大きく見せる親しみ型 |

金額は `source/service-pages/catalogue.json` の `products.1` を、既存の `tools/build_cart_catalogue.py: prices` で読み出します。１台13,200円、２台以上は１台11,000円、１台あたり2,200円・２台合計4,400円のお得額、２台合計22,000円をビルド時に計算します。料金を独立した正本として手入力しません。３案共通の条件は「壁掛けタイプ（お掃除機能なし）／同時に２台以上のご注文時／税込」です。参考画像の他社名、電話番号、期間、プレゼント、女性スタッフ対応などは採用していません。

## 所有元と実装

- `build.py`: 既存価格正本から共通料金を取り出し、３バナーの静的HTML、比較画面、HOME内比較画面を生成。
- `banner.css`: この提案に限定した配色、放射形、背景、見出し、料金、条件、レスポンシブ表示。共通CSSは編集しない。
- `context.js`: HOME内比較画面のA/B/C切替とURLパラメータ。バナー本文はJavaScriptなしでもHTMLに存在する。
- `assets/aircon-pair.png`: 人物・文字・価格・ロゴを含まない２台のエアコンの透過素材。1536×1024。３案で同じ１素材を参照する。
- `index.html`、`context.html`、`build-info.json`: ビルド成果物。採用・公開は未実施。

HOME内比較は現行 `source/site/index.html` を入力とし、上部の `home-pickup-banner` だけを置き換えて生成します。共通ヘッダー・フッター・動画・既存２枚バナー・後半３枠は保持検査を行います。本番HOME、既存HOME比較画面、既存の共通正本は変更していません。比較画面はnoindexです。採用時は既存の `tools/home_pickups.py` を表示の唯一の正本として更新する範囲を別途確定します。

## SEOについて確認した公式資料

ユーザーの希望どおり、エアコンクリーニングの見出し、金額、条件、行き先を静的HTMLへ置き、CSSと文字なしの画像を重ねて一つのバナーとして見せます。見た目用のスクリーンショットを掲載用画像として使う構成ではありません。

- [Google公式・開発者向けガイド](https://developers.google.com/search/docs/fundamentals/get-started-developers): 重要情報をDOM内の可視テキストで表現し、意味のあるHTMLを用いる。重要文言をCSSのcontentへ置かない。
- [Google公式・画像のベストプラクティス](https://developers.google.com/search/docs/appearance/google-images): 主な画像はimgのsrcで提供する。CSS背景画像はGoogle画像検索のインデックス対象にならないため、装飾背景はCSS、エアコン素材はimgを使用。本文と内容が重複する装飾素材はaltを空にする。
- [Google公式・リンクのベストプラクティス](https://developers.google.com/search/docs/crawling-indexing/links-crawlable): href付きのaと内容を説明するリンク文言を使用。３案とも既存の `/house-cleaning/aircon/` へつながる。
- [Google公式・2026年3月のGooglebot記事](https://developers.google.com/search/blog/2026/03/crawler-blog-post): 最新年の公式記事も確認し、主要内容を取得可能なHTMLへ置く方針を確認した。

これらは検索エンジンに内容を伝えやすくする実装です。検索順位向上やインデックス登録の実測を意味しません。

## 素材生成

画像生成スキルのbuilt-in image_genを使用。新規素材は１点で、３案の違いはHTML/CSSの色、構図、文字と料金の優先順位で作りました。以下が使用したプロンプトです。

```text
Use case: ads-marketing. Asset type: reusable transparent foreground artwork for three HTML/CSS promotional banners for a Japanese home cleaning service. Create exactly TWO unbranded white wall-mounted room air conditioners as a compact diagonal pair, one a little behind and above the other, both completely visible. They look freshly cleaned, polished, friendly and realistic with a playful premium 3D advertising illustration finish. Front three-quarter view, recognizable horizontal white shells, open louver vents and subtle cool blue airflow ribbons underneath. Around them add only a few small blue water droplets and four-point yellow/white sparkle accents. Crisp smooth shading, clean white surfaces, cyan accents, cheerful pop advertising mood inspired by colorful Japanese air-conditioner cleaning promotions. Artwork should fill most of a landscape canvas with modest transparent margin and no large empty white padding. Both units must be legible when reduced for mobile. No people, hands, faces, mascots, room, walls, scenery, cleaning tools, logos, branding, lettering, numbers, labels, price tags, badges, border or watermark. Background must be truly transparent; preserve all outer edges and airflow ribbons. The campaign words and all pricing will be real HTML, so do not draw ANY text. Save a finished high-quality raster cutout.
```

## 確認記録

再提案の検証は `evidence/2026-10-07/aircon-banner-proposals/verification-revised.json`、保存画面は `A/B/C-revised-1439.png` と `A/B/C-revised-414.png` を参照してください。初回提案の検証と画面は同フォルダーの旧記録として保持します。検証は非表示Chrome１ブラウザーで逐次実行し、終了時に閉じます。ブラウザー幅の確認と実機受入、ローカル提案と公開採用を区別します。

指定された公開エアコンページをHTTP取得し、ローカル正本とSHA-256が一致することを確認しました。ローカルの既存プレビューが応答しなかったため、既存のserve.pyを8773で起動しました。このユーザー用プレビューは維持します。

```powershell
python prototypes/home-wireframe/aircon-banner/build.py
```

<!-- proposal-notes:start -->
## 再提案３案の設計説明

３案とも左に訴求・価格・CTA・条件、右に２台の画像を置きます。販促ラベルは「まとめてお得」「２台以上」を使用します。

### A案：4,400円お得！が主役

- **狙い**：お得額が見た瞬間に分かる、最も販促感の強い案。画像より大きい数字と、黄色・青の強い対比で目を引きます。
- **レイアウト**：左に「２台まとめて」→最大サイズの4,400→円お得！→CTA→条件。右のエアコン２台は小さめにまとめ、青い斜めパネルで分離します。
- **配色**：黄色#ffdf32×濃い青#06439d。お得ラベルとCTAはオレンジ、数字は白い縁取り。ドット・放射は薄く、文字の背面を優先。
- **メインコピー**：２台まとめて 4,400円お得！
- **価格の見せ方**：4,400をPC最大158pxで主役に。１台あたり2,200円お得は小さく補足。
- **CTA**：エアコンクリーニングの料金を見る
- **HTML/CSS構造**：a要素全体をリンクにし、CSS Gridで左64％／右36％。左はラベル→h3→価格補足→CTA→条件、右は文字なしのimgとCSS装飾。すべての文字は静的HTML。

### B案：11,000円を一番に

- **狙い**：いくらで頼めるかを最短で伝える案。１台あたりの11,000円を最も大きくし、２台合計は補助情報に留めます。
- **レイアウト**：左に「２台以上なら」→１台あたり→大きな11,000円（税込）→小さな２台合計→CTA→条件。右は２台の画像と青い丸背景。
- **配色**：白・水色#eaf7ff×濃い青#06439d。料金の円と販促ラベルにオレンジ、帯に黄色。数値部分は無地で読みやすく。
- **メインコピー**：２台以上なら、１台あたり11,000円（税込）
- **価格の見せ方**：11,000をPC最大138px。２台合計22,000円（税込）は下に小さく表示し、情報の強弱を明確に。
- **CTA**：エアコンクリーニングの料金を見る
- **HTML/CSS構造**：a要素全体をリンクにし、CSS Gridで左64％／右36％。左はラベル→h3→価格補足→CTA→条件、右は文字なしのimgとCSS装飾。すべての文字は静的HTML。

### C案：２台まとめて、お得にキレイ！

- **狙い**：まとめて注文するメリットに暮らしの親しみを添える案。２台の文字を大きくし、リビング・寝室は補助情報として扱います。
- **レイアウト**：左に大きな「２台」→「まとめて、お得にキレイ！」→生活場面→２台合計料金→CTA→条件。右は２台の画像と部屋名ラベル。
- **配色**：クリーム#fff0d4×サイトの濃い青。オレンジの帯と黄色の下線で販促感を加え、温かさと視認性を両立。
- **メインコピー**：２台まとめて、お得にキレイ！
- **価格の見せ方**：２台の文字はPC最大114px。２台合計22,000円（税込）は最大42pxで、メインコピーの次に見せます。
- **CTA**：エアコンクリーニングの料金を見る
- **HTML/CSS構造**：a要素全体をリンクにし、CSS Gridで左64％／右36％。左はラベル→h3→価格補足→CTA→条件、右は文字なしのimgとCSS装飾。すべての文字は静的HTML。
<!-- proposal-notes:end -->
