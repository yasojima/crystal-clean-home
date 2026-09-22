# 商品移植・共通UI

更新：2026-09-23。

source/osoujiは取得時の公開レスポンス（52ページ、1036アセット）。capture_reference.pyは再取得用であり、通常の再生成では実行しない。
reference.pyが元main構成と画像・価格・説明を保持し、店舗名/書体/色を適合。/house-cleaning/と/services/へ出力。CSSは.cch-referenceへスコープ化。固定ヘッダーは.cch-hostと共有brand/headerを使用。

shop.pyの後に実行し、旧データと移植292グループ/316バリアントを結合（合計311/356）。bridge.jsが元商品の数量・間取り・オプションをローカルカートへ接続する。
元common.jsのタブ・FAQ・比較画像等は保持。リモートヘッダー/カート初期化は停止。比較画像のbodyロックもpublisherで除去し、ハンドルのtouch-actionで操作制御する。42出力ページが同じJSを使用。
カート追加の赤はbrand.cssで共通指定。公開出力のbundleだけを手修正しない。

非公開API、予約送信、全バックエンド割引規則は未移植。最終操作はデモ。未取得キャンペーン等への情報リンクは外部参照元へ残る。価格/本文/写真/実績は事業情報として未承認。不要項目を独自削除しない。
取得元404：assets/css/house-cleaning/others.css、assets/css/images/shop/top/prefecture-bg.webp、assets/images/common-parts/illust/office-uv-flooring.svg。capture.jsonに記録。

node test-reference.cjsで代表計算と参照を確認。現在の検証範囲・残件はルートSITE_VERIFICATION.md、生成順はEDITING_GUIDE.md。
