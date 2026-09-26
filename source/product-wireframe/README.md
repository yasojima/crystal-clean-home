# 商品カテゴリ8ページの生成元

更新：2026-09-26。本編に統合済みの8カテゴリを生成するための正本です。`pages/house-cleaning/` の8カテゴリと洗濯機の種類別3ページは取得元HTMLの保管入力で、`baseline.json` に複製直後のSHA-256を記録しています。入力HTMLを直接編集せず、公開ページは `reference.py` → `integrated_product_pages.py` → `product_wireframe.py` の生成処理で更新します。

公開先は `docs/house-cleaning/{カテゴリ}/`、共通のCSS・画像は `docs/reference/product-pages/` です。生成処理に残る `_product-wireframe` という文字列は内部の組立用URLであり、公開用の独立ラフページではありません。商品ID・価格・オプション・カートの連携は元の種類別ページと共通カタログに従います。

説明文は `service-copy.json`、オプションの短文は `option-brief-copy.json`、口コミの掲載用サンプル文は `review-copy.json`、FAQは `faq-copy.json`、利用と支払いの流れは `flow-copy.json` を編集します。口コミと施工前後の画像は構成確認用の創作例であり、実績として表示しません。オプション本文は表示3行以内を原則とし、条件や注意事項を残したまま収まらない場合は人間に確認します。親商品の「詳しく見る」はデモの説明ダイアログを示すもので、実際の商品詳細ページはありません。

画像の対応は [PHOTO_ASSETS.md](PHOTO_ASSETS.md) を参照します。生成画像は `assets/`、共通カテゴリ画像は `brand/category-illustrations-v2/` に保存します。PC/SPの見た目はそれぞれ `source/device/desktop/css/product-wireframe/wireframe.css`、`source/device/mobile/css/product-wireframe/wireframe.css` が正本です。単独publisherを実行した後は `shared_ui.py` も実行します。