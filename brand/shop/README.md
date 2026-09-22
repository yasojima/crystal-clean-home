# 共通カート計算・旧データ互換

更新：2026-09-23。

- catalog.json：旧19グループ/40種類の保存カート互換データ。
- cart-core.js：ID・数量検証、セット分解、合計、複数台価格、割引・税額、本体削除時のオプション削除。
- 保存キーcch-estimate-cart-v1。保存対象は商品IDと整数数量だけ。
- 画面はsource/osouji/checkoutの参考元HTML/CSSをcheckout.pyで生成。brand/reference/checkout.jsがローカル操作を担当する。
- 旧独自shell/script/CSSは撤去。shop.pyは共有アセットとホームの入口を管理し、CLIではreference.pyを続けて実行する。

検証：node test-shop.cjs、node test-reference.cjs、node test-checkout.cjs。実予約・クーポン判定は未接続。現行仕様と残件はルートの要件定義書とSITE_VERIFICATION.md。
