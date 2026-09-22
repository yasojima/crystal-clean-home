# 編集・生成ガイド

更新：2026-09-23。作業ディレクトリはPROJECT_MANIFEST.md参照。docsだけを編集しない。

## 編集元

| 対象 | 正本 / 生成 |
| --- | --- |
| 店舗情報・ロゴ | brand/site.json、brand/crystal-clean-home.png / build.py |
| 旧基盤本文 | source/（osouji以外）、copy/ja.json / build.py、copywriting.py |
| 共通ヘッダー | brand/header/ / header.py |
| ヒーロー | brand/hero/ / hero.py |
| ホーム追加部品 | brand/estimate-cta、service-cards、reasons、prevention、service-directory / home_sections.py |
| 商品移植 | source/osouji/pages、assets、brand/reference/ / reference.py |
| カート・フォーム | brand/shop/ / shop.py → reference.py |
| 旧基盤の色・端末分離 | brand/theme.json、theme.py、source/layout/ / device_styles.py |

## 生成順

全体：`python build.py`。コピー変換→ヘッダー→デモ→HUD→ヒーロー→ホーム部品→shop→referenceの順。referenceが最後に商品ページと結合カタログを出力する。

対象別：
- ヒーロー：`python build.py --hero-only`
- ホーム部品：`python home_sections.py` の後 `python shop.py`（カテゴリー導線とカートを再接続）
- カート・商品：`python shop.py`。CLI内でreference.pyも呼ぶ。
- 移植のみ：`python reference.py`（既存のdocs/cart・estimate等を前提とする）
- header-only、layout-only、tabs-only、demo-only、hud-only等は旧基盤の処理。新ページも対象になる場合があるため、生成前後の差分を確認し、商品側は最後にreference.pyで整える。

全体ビルドは大量の差分が出る場合がある。限定修正は対応publisherを使い、無関係な生成差分を混ぜない。共通CSSだけなら正本変更後、同じ内容を対応するdocs公開パスへコピー可能（publisherでも同じファイルをコピーする）。

## 依存と確認

Python：requirements.txtのrequests、beautifulsoup4、lxmlに加え、reference.pyはtinycss2が必要（現状requirements.txtへの追記は未実施）。既存環境では動作確認済み。新環境ではtinycss2もインストールする。
Node：`node test-shop.cjs`、`node test-reference.cjs`。比較UI等の動作変更は非表示IABで実操作も確認。
プレビュー：`python preview.py` → http://127.0.0.1:8766/crystal-clean-home/ 。既存サーバーが起動中なら重複起動しない。

変更を対象別にgit addしてコミット・push。未管理ファイルを一括追加しない。GitHub Pagesの対象SHA成功と公開レスポンスを照合する。実装変更なしの文書整理ではサイトの再ビルドは不要。

## 取得ソースとレポート

旧基盤取得はcapture.json、商品取得はsource/osouji/capture.json。取得ソースは再生成に必要なので旧式という理由で削除しない。再取得は参考元の料金等も変わるため、単なる再ビルドと混同しない。
reference-report.json、copy-change-log.json等は生成・照合データで、現在の承認事項の正本ではない。過去の公開状態を固定文でMDへ上書きする旧補助スクリプトは撤去済み。
