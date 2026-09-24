# 編集・生成ガイド

更新：2026-09-23。作業正本：C:/Users/yasoj/codex Projects/Crystal Clean Home。

## 編集先
|対象|正本|
|---|---|
|PCの配置・色・幅・背景・アニメーションCSS|source/device/desktop/css/|
|スマホの配置・色・幅・背景・アニメーションCSS|source/device/mobile/css/|
|端末別の採用画像|各端末のimages.json|
|端末別のUI寸法・復帰待ち|各端末のui.json|
|店舗情報・ロゴ|brand/site.json、brand/crystal-clean-home.png|
|ホーム・共通メニューの8カテゴリ画像|brand/category-illustrations-v2/、source/device/{desktop,mobile}/css/brand/header/category-cards.css|
|ホーム部品の文章・構造|brand各部品のtemplate.html|
|共通ヘッダー内容|brand/header/template.html|
|共通フッター内容|brand/shared-ui/footer.html|
|MENU・追従バー・カート概要の共通動作|brand/header/floating.js|
|カートの計算・保存|brand/shop/cart-core.js|
|カートのDOM・操作|brand/reference/checkout.js、checkout.py|
|商品データ・移植入力|source/osouji、brand/reference/card-copy.json|
|旧基盤本文|source、copy/ja.json|

brandのCSSおよびdocsの元CSSパスは振り分け用。見た目はsource/deviceを編集する。文章とカート計算は共有し、見た目を片方だけ変更するときは他方の正本を変更しない。HTML内styleブロックもcss/inlineへ端末別に分離している。

## 生成と公開
- 見た目だけ：python device_ui.py。
- 共通UI：python shared_ui.py（末尾でdevice_uiを実行）。
- 商品・カート：python reference.py（最後に共通UI・端末分離も生成）。
- 全体：python build.py。取得ソースを再取得する必要はない。
- ホーム部品・動画など単独publisherを実行した後は、最後にpython shared_ui.py。
- CSS/JS変更時は公開キャッシュも確認する。docsだけで修正を完結させない。

検証：python test_device_ui.py、node test-checkout.cjs、node test-reference.cjs、node test-shop.cjs。UI変更は非表示IABで実操作も確認する。実予約送信はしない。

Gitはmain、Pagesはdocs。変更ファイルを明示してcommit/pushし、該当SHAのPages成功と公開ページを確認する。無関係な作業中ファイルを一括登録しない。旧版はGitで保持する。
