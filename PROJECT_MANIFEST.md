# Crystal Clean Home PROJECT_MANIFEST

更新日：2026-09-22 / PRIMARY_ROUTE_ID：WEB / PROFILE：GENERAL_SITE

- 正本：C:/Users/yasoj/codex Projects/Crystal Clean Home
- 要件：Crystal-Clean-Home_要件定義書.md v1.2
- 制作準備：Crystal-Clean-Home_制作準備書.md v1.1
- 参照：https://iekire.com/
- ソース：source/、brand/、build.py
- 取得記録：capture.json
- 公開出力：docs/
- GitHub：https://github.com/yasojima/crystal-clean-home
- 公開URL：https://yasojima.github.io/crystal-clean-home/
- 検証結果：SITE_VERIFICATION.md
- 採用書体見本：design/mincho-gothic-sample.png


事業情報と実受付先は未定。外部AI監査・PDCAはPROJECT_EXCEPTIONS.mdの適用除外。

デザイン方針の正本：要件定義書v1.2「ブランド・表現方針」。CHG-2026-09-22-BRANDの書体・配色は実装済み。動き・動画の追加なし。共通配色はbrand/theme.json、用途別書体はtheme.py。

作業データの保存先は本ローカルプロジェクトのみ。Driveは中央マニュアルの確認専用。作業中のDriveへの新規作成・更新・同期は禁止し、最終集約は人間の明示指示時のみ。詳細はAGENTS.md「Driveとローカルの役割」を参照。

[更新 2026-09-22] 文章置換はcopy/ja.jsonとcopywriting.pyで共通管理し、変更前後は文章変更一覧.mdを参照する。デモ案内は通常本文には出さず操作時のポップアップに限定する。接続解除と案内の仕様はDEMO_MODE.mdを参照。

共通ヘッダー正本：brand/header/、組込みheader.py、仕様HEADER_UI.md。CHG-2026-09-22-SHARED-HEADERで開閉動作を更新。



## CHG-2026-09-22-DEVICE-LAYOUT

[変更 2026-09-22] PC・スマホのレイアウト編集を分離する。サイト本体と見積はsource/layout/desktop・mobile、共通ヘッダーはbrand/header/desktop.css・mobile.cssで管理する。文章・画像素材・メニュー内容・事業情報は共通管理し、文章変更は双方へ反映する。見た目の再設計は行わない。編集場所・生成・確認方法はDEVICE_LAYOUT.mdを参照。Driveは変更しない。
