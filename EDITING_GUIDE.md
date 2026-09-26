# 編集・生成ガイド

更新：2026-09-26。作業正本：C:/Users/yasoj/codex Projects/Crystal Clean Home。

## 編集先
|対象|正本|
|---|---|
|PCの配置・色・幅・背景・アニメーションCSS|source/device/desktop/css/|
|スマホの配置・色・幅・背景・アニメーションCSS|source/device/mobile/css/|
|端末別の採用画像|各端末のimages.json|
|端末別のUI寸法・復帰待ち|各端末のui.json|
|店舗情報・ロゴ|brand/site.json、brand/crystal-clean-home.png|
|ホーム部品の文章・構造|brand各部品のtemplate.html|
|ホーム上部・下部の8カテゴリーリンク|brand/service-cards/template.html、brand/service-directory/template.html（home_sections.pyでdocs/index.htmlへ反映）|
|共通ヘッダー内容|brand/header/template.html|
|共通フッター内容|brand/shared-ui/footer.html|
|MENU・追従バー・カート概要の共通動作|brand/header/floating.js|
|カートの計算・保存|brand/shop/cart-core.js|
|カートのDOM・操作|brand/reference/checkout.js、checkout.py|
|商品データ・移植入力|source/osouji、brand/reference/card-copy.json|
|初めての方へのLP統合原稿|source/first/lp-copy.md|
|初めての方への漫画LPの構成・本文・画像|brand/first-lp/template.html・images/（first_lp.py → shared_ui.py、FIRST_LP.md参照）|
|旧基盤本文|source、copy/ja.json|
|8カテゴリ本編の共通構造・文章|product_wireframe.py、source/product-wireframe/{review,faq,flow,service,option-brief}-copy.json|
|8カテゴリ本編のPCの見た目|source/device/desktop/css/product-wireframe/wireframe.css|
|8カテゴリ本編のスマホ・タブレットの見た目|source/device/mobile/css/product-wireframe/wireframe.css|
|カテゴリー画像の現行版|brand/category-illustrations-v2/|
|法人向けページの本文・画像参照・見出し帯|corporation.py、brand/corporation/images/|
|法人向けページのPC/SPの見た目|source/device/{desktop,mobile}/css/corporation.css|

brandのCSSおよびdocsの元CSSパスは振り分け用。見た目はsource/deviceを編集する。文章とカート計算は共有し、見た目を片方だけ変更するときは他方の正本を変更しない。HTML内styleブロックもcss/inlineへ端末別に分離している。

## 生成と公開
- 見た目だけ：python device_ui.py。
- 漫画LP：`python -B first_lp.py`。構成・本文はbrand/first-lp、配置は端末別first-lp.css、CTAは既存の共有正本から生成する。3アンカーは維持する。旧reasonの再生成はしない。検証はtest_first_lp.pyと非表示IAB。
- 共通UI：python shared_ui.py（末尾でdevice_uiを実行）。
- お問い合わせの最上部見出し帯：`shared_ui.py` で `/contact/` の上部H1を指定し、PC/SPの色・書体・高さは `source/device/{desktop,mobile}/css/brand/shared-ui/style.css` で管理する。フォーム内H2と入力欄は変更しない。
- 商品・カート：python reference.py（最後に共通UI・端末分離も生成）。
- 全体：python build.py。取得ソースを再取得する必要はない。
- 法人向けページ：python corporation.py。本文と画像参照を生成し、最後に共通UIを反映する。全体生成でもbuild.pyの末尾から実行される。
- 8カテゴリの本編商品ページ：python reference.py が `integrated_product_pages.py` を呼び、`docs/house-cleaning/{8カテゴリ}/` と `docs/reference/product-pages/` のCSS・画像を生成する。旧 `docs/_product-wireframe/` の独立ラフ生成は終了した。
- 本編のオプションカードに個別の「詳しく見る」と専用ダイアログは置かない。説明本文は source/product-wireframe/option-brief-copy.json で管理し、PC・スマホの狭い幅を含めて表示3行以内に収める。条件・注意事項は落とさず、3行を超えそうなときは本文を確定する前に人間へ確認する。カード内の本文枠は3行分を確保し、同じ段の下端を揃える。
- 親商品の「詳しく見る」は現在のデモでは押すとポップアップが開き、「※デモンストレーションのサンプル表示のため、「詳しく見る」のパッケージはありません。」を表示する。商品カードの写真下には常時表示しない。実案件のパッケージを作る際は、確認できた独自技術・権利・追加条件など、説明で差別化できる内容がある場合だけ詳細画面を用意する。特別な内容がなければ親商品の「詳しく見る」も削除し、数量選択と「カートに追加」の操作だけを残す。商品ID・価格・カート連携は維持する。
- 洗濯機・コーティング・「その他」の追加比較画像は `source/product-wireframe/assets/{washer,coating,others}/case-*-{before,after}.png` が正本。比較タブ・おすすめ欄・洗濯機の商品概要と個別見出しは `product_wireframe.py` で生成する。洗濯機の商品名・料金・サービス時間・オプション名と価格は `source/product-wireframe/pages/house-cleaning/washer/{top,front,side}/index.html` から抽出し、本編の商品・オプション欄には水まわりの既存カードHTMLを複製して入れる。おすすめも既存のプランカードHTMLを使い、元の商品IDに連携する。「その他」の外壁洗浄は元の44,000円／40㎡以下と超過1㎡990円を連携。商品IDと価格は本編共通カート・見積画面で扱う。最初の洗濯機選択カードは本編内の3見出しへ接続する。
- ホーム部品・動画など単独publisherを実行した後は、最後にpython shared_ui.py。
- CSS/JS変更時は公開キャッシュも確認する。docsだけで修正を完結させない。

検証：python test_device_ui.py、node test-checkout.cjs、node test-reference.cjs、node test-shop.cjs。UI変更は非表示IABで実操作も確認する。実予約送信はしない。
商品ページ変更はpython -B test_integrated_product_pages.pyも実施し、PC/SPの境界992px/993pxと狭い幅を確認する。画像の古い版は現行参照を調べてからデスクトップの「削除用」へ移し、復旧はGitで行う。

公開元はmainのdocs。商品8カテゴリは本編出力に統合済み。公開する変更では対象ファイルを明示してcommit/pushし、該当SHAのPages成功と公開ページを確認する。無関係な作業中ファイルを一括登録しない。旧版はGitで保持する。
