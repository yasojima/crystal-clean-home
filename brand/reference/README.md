# 商品移植・共通UI

更新：2026-09-26。

source/osoujiは取得時の公開レスポンス（52ページ、1036アセット）。capture_reference.pyは再取得用であり、通常の再生成では実行しない。
reference.pyが元main構成と画像・価格・説明を保持し、店舗名/書体/色を適合。8カテゴリの本編はproduct_wireframe.pyとintegrated_product_pages.pyで承認済みの構造へ組み立ててから/house-cleaning/と/services/へ出力する。画像・端末別CSSは/docs/reference/product-pages/へ生成する。CSSは.cch-referenceへスコープ化。固定ヘッダーは.cch-hostと共有brand/headerを使用。

shop.pyの後に実行し、旧データと移植292グループ/316バリアントに外壁手洗い洗浄の基本商品・追加1㎡を加える（合計313グループ/358バリアント）。bridge.jsが元商品の数量・間取り・オプションをローカルカートへ接続する。
元common.jsのタブ・FAQ・比較画像等は保持。リモートヘッダー/カート初期化は停止。比較画像のbodyロックもpublisherで除去し、ハンドルのtouch-actionで操作制御する。52出力ページが同じJSを使用。
商品側のカート追加・右下カート・見積CTAは元の赤を保持。公開出力のbundleだけを手修正しない。

非公開API、予約送信、全バックエンド割引規則は未移植。最終操作はデモ。参照元フォーム・旧店舗へのリンクは出力時に除去または自サイト内へ変更し、商品に関係するメーカー・動画の情報リンクだけを残す。価格/本文/写真/実績は事業情報として未承認。取得元の複製は保持する。
`card-copy.json` は生成用の対応辞書であり、公開出力へ複製しない。旧会社概要・プライバシーポリシーは `shared_ui.py` で確定待ちの案内に置換する。
取得元404：assets/css/house-cleaning/others.css、assets/css/images/shop/top/prefecture-bg.webp、assets/images/common-parts/illust/office-uv-flooring.svg。capture.jsonに記録。

node test-reference.cjsで代表計算と参照を確認。現在の検証範囲・残件はルートSITE_VERIFICATION.md、生成順はEDITING_GUIDE.md。

## カートと入力確認

checkout.pyはsource/osouji/checkoutのcart/estimate/confirm.htmlを使用。checkout.js/cssが数量変更、親子明細、追加オプション、割引内訳、入力・確認・戻る・デモ確定を接続する。set-samples.jsonは16セットの公開カート応答（トークンやセッションIDを保存しない）、recommend-cards.jsonは元の推薦カード。個人情報は画面メモリだけ。postal-data.jsは日本郵便の公開データを同梱した住所補完用。取得元：https://www.post.japanpost.jp/service/search/zipcode/download/utf-zip.html （2026-08-31版）。

node test-checkout.cjsで16セットの構成と金額、税額、親子削除、保存復元、ローカルフォームの送信禁止を検証。全クーポン・店舗別価格・実予約送信・予約完了後の参照元画面は未検証/未接続。

カードの説明・訴求見出しはcard-copy.jsonとcard_copy.pyで編集。承認済み原文との完全一致に限定し、構造・属性・料金条件・商品名・引用を保持。実テキストの共通書体と3段三角形はsource/device/{desktop,mobile}/css/brand/header/typography.cssを参照する。

カート本文の書体はcart-exact.cssで参考元へ統一し、共通サイト書体の上書きから分離する。checkout.pyがcartページだけに読み込む。

## 2026-09-23 カート移植の追加照合

カート本文へ参考元の未改色CSSをスコープ付きで適用。おすすめ欄も参考元top.js内のSwiperと初期化設定（20px間隔、PC3.5枚・768px以上2.5枚）を移植。私有APIと送信処理は切り離す。追従バーのカート文字はHTML化し、お問い合わせと同じCardo/Noto Serif JP・600へ統一。

現行CSSの編集元はsource/device/{desktop,mobile}/css/reference/。brand配下のCSSは振分け入口。空カートは参考元のc-page-headingとl-section構造を使用する。
