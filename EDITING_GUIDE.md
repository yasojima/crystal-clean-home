# Crystal Clean Home 編集ガイド

正本：C:/Users/yasoj/codex Projects/Crystal Clean Home

## 編集先

- 店名・電話・営業時間：brand/site.json
- 採用済みロゴ：brand/crystal-clean-home.png
- 各ページの文章・構成：source/内の該当index.html
- 画像・CSS・JavaScript：source/wp/wp-content/以下
- 全ページへの共通変換：build.py

python build.pyでdocs/を再生成する。docs/だけを手編集しない。python preview.pyでhttp://127.0.0.1:8766/crystal-clean-home/を確認できる。

依存Pythonライブラリー：requests、beautifulsoup4、lxml。生成後にmainへコミット・pushするとGitHub Pagesへ公開される。公開先はhttps://yasojima.github.io/crystal-clean-home/。

capture.jsonには取得URLと保存先、取得失敗の対応表がある。取得元のフォーム送信処理は含まれないため、受信先を決めて接続するまで送信を保留する。

## 全ページのタブ表示

タブ名はbrand/site.jsonのname、タブのアイコンは採用PNGのC部分を拡大したbrand/favicon.svgをbuild.pyで生成し、一括管理する。python build.pyで全生成、python build.py --tabs-onlyで既存の公開HTMLのタブ情報だけを一括更新できる。

## 書体とヘッダー比率

書体の確定仕様は要件定義書v1.2「ブランド・表現方針」を参照する。theme.pyが用途別の游明朝・游ゴシックを指定し、brand/theme.jsonが全ページの共通配色を管理する。logo.svgの表示枠は48 72 1578 731。元PNGの縦横比を保持し、PCは180×約83px、スマホは高さ38px。電話画像は元SVGの表示領域を維持する。python build.py --assets-onlyで共通SVGとスタイルを再生成できる。

## デザイン変更時の参照

2026-09-22更新。配色・コンセプト・動画・アニメーションは要件定義書v1.2を正本とする。書体と配色を共通スタイル・電話SVGへ実装済み。レイアウト・サイズ・動きは変えない。再生成はpython build.py --assets-only。指定フォントがない端末は定義済みの日本語代替書体を使用する。

作業データの保存先は本ローカルプロジェクトのみ。Driveは中央マニュアルの確認専用。作業中のDriveへの新規作成・更新・同期は禁止し、最終集約は人間の明示指示時のみ。詳細はAGENTS.md「Driveとローカルの役割」を参照。

[更新 2026-09-22] 文章置換はcopy/ja.jsonとcopywriting.pyで共通管理し、変更前後は文章変更一覧.mdを参照する。デモ案内は通常本文には出さず操作時のポップアップに限定する。接続解除と案内の仕様はDEMO_MODE.mdを参照。

Viewport HUD：brand/viewport-hud.jsで表示・閾値を共通管理。hud.pyで全ページへ組み込む。HUDのみの反映はpython build.py --hud-only。MOBILE 640px以下／TABLET 641～992px／DESKTOP 993px以上。


共通ヘッダーはbrand/header/を一括編集し、python build.py --header-onlyで全ページへ反映。ページ固有の追加はpages.json。詳細はHEADER_UI.md。



## CHG-2026-09-22-DEVICE-LAYOUT

[変更 2026-09-22] PC・スマホのレイアウト編集を分離する。サイト本体と見積はsource/layout/desktop・mobile、共通ヘッダーはbrand/header/desktop.css・mobile.cssで管理する。文章・画像素材・メニュー内容・事業情報は共通管理し、文章変更は双方へ反映する。見た目の再設計は行わない。編集場所・生成・確認方法はDEVICE_LAYOUT.mdを参照。Driveは変更しない。


## CHG-2026-09-22-HERO

トップの旧バナーを竹下設計の大画面フレームとスクロール演出に差し替える。PC・スマホ別にbrand/hero/で管理し、右側のお問い合わせ・LINE、ヘッダー、本文は維持する。高さ変更は承認済み。既存写真を仮置きし、清掃前後の新規画像はユーザーの動作確認後に制作する。詳細はHERO_UI.md。
