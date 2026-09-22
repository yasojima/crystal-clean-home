# カート・見積フォーム

更新：2026-09-23。現在の公開商品一覧はreference.pyによる移植ページ。shop.pyの独自一覧を最終成果として公開しない。

- brand/shop/catalog.json：旧19グループ/40バリアント。旧保存カート互換用として維持。
- cart-core.js：ID・数量の検証と合計、複数台単価。
- script.js：カート編集・削除・フォーム確認・デモ終了。個人情報の送信/永続保存なし。
- style.css、desktop.css、mobile.css：新カート/フォームの表示。
- shop.py実行後にreference.pyが移植商品を結合し、/cart/・/estimate/へ注入。CLI python shop.pyはこの順で実行する。
- 保存キーcch-estimate-cart-v1。保存内容は商品IDと整数数量のみ。

検証：node test-shop.cjs、node test-reference.cjs。料金は事業者未承認。正式な価格・全割引条件・実受付接続は未完了。共通現行仕様はルートの要件定義書、未対応はSITE_VERIFICATION.md。
