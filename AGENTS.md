# Crystal Clean Home

作業正本：C:/Users/yasoj/codex Projects/Crystal Clean Home

PROJECT_EXCEPTIONS.md、PROJECT_MANIFEST.md、要件定義書を読むこと。親フォルダーのAGENTS.mdとSOURCE_AND_HISTORY_POLICY.mdを適用する。

現在の参照はhttps://iekire.com/。公開ソース全体をコピーし、構成や内容を独自判断で省略・再設計しない。確定した店名・ロゴ・電話番号・営業時間はbrand/から適用する。配色・書体・コンセプト・動きは要件定義書v1.2「ブランド・表現方針」を正本とする。参照元の配色・書体を維持する旧方針より、2026-09-22の確定方針を優先する。資料上の決定と公開実装の完了を区別する。

source/は編集用、docs/はbuild.pyで生成する公開用。共通設定はbrand/site.json。手作業でdocs/だけを修正しない。公開はcrystal-clean-homeリポジトリmainの/docsを使用する。

ユーザーのローカルブラウザーを操作しない。右側プレビューを開かない。非表示IABで検証する。外部AI監査・PDCAはオーナーの明示指示がある場合のみ。サブエージェントを使用しない。

## Driveとローカルの役割

[変更 2026-09-22 / CHG-2026-09-22-LOCAL]
Driveは会社の中央原本・マニュアルの確認専用とする。原本を編集しない。確認後に必要な案件MD・作業データはすべて指定のローカルプロジェクト内で作成・更新する。作業中にDriveへ新規作成・アップロード・同期しない。Driveへの集約は制作の最後に、人間の明示指示と中央マニュアルの手順に従って行う。

[更新 2026-09-22] 文章置換はcopy/ja.jsonとcopywriting.pyで共通管理し、変更前後は文章変更一覧.mdを参照する。デモ案内は通常本文には出さず操作時のポップアップに限定する。接続解除と案内の仕様はDEMO_MODE.mdを参照。

ヘッダーはbrand/header/の共通部品を正本とする。個別ページに複製・直接修正しない。例外はpages.jsonで追加する。HEADER_UI.mdを参照。

