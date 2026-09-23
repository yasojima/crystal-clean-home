# Crystal Clean Home — エージェント入口

更新：2026-09-23。作業正本：C:/Users/yasoj/codex Projects/Crystal Clean Home。
親のAGENTS.mdとSOURCE_AND_HISTORY_POLICY.mdを適用する。

1. PROJECT_MANIFEST.md → 要件定義書 → EDITING_GUIDE.md → SITE_VERIFICATION.mdの順で現在地を確認する。
2. 旧サイト基盤はiekire、現行の商品一覧・詳細はおそうじ本舗の公開ソース。参照元はページ群別に判断する。
3. 現在は骨格を作る段階。移植商品の画像・構成を独自に再設計・削除しない。カードの説明・訴求見出しは最新の承認に基づきcard-copy.jsonで原意を保って編集する。不要項目の選別は人間が後で行う。
4. 商品側の追加・右下カート・見積CTAは赤。カート画面も参考HTML/CSSを保持。ホーム見積CTAは赤/白の反転。書体・見た目はsource/deviceのPC/SP正本で管理し、店舗名・青系の基本配色とヘッダーも共通管理。同じUIの修正は共通処理に適用する。
5. docsだけを直接編集しない。source/、brand/、publisherが正本。商品ページはshop.pyの後にreference.pyが生成する。
6. ソースと公開状態を確認し、完了・完全一致を証拠なしに報告しない。全ページ目視・実機・実予約は未検収。
7. 非表示IABのみ。ユーザーのChrome・右側プレビューを操作しない。サブエージェントを使わない。外部AI監査・PDCAは明示指示がない限り適用除外。
8. Driveは中央原本の参照専用。本案件資料はローカルで管理し、明示指示なしにDriveへ書き込まない。
9. 変更時は要件・関連仕様・変更履歴を同期。過去状態はGitで保存し、旧版コピーや一時引継ぎを増やさない。
10. 事業情報・実受付先は未確定。移植ページの外部情報リンクと、禁止している予約送信を区別する（DEMO_MODE.md）。

11. 現行の見た目はsource/device/{desktop,mobile}を編集する。brandのCSSは生成用入口。単独publisher実行後はshared_ui.pyを実行する。
