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
| カート・フォーム | source/osouji/checkout、brand/reference/checkout.js/css、brand/shop/cart-core.js / reference.py → checkout.py |
| 旧基盤の色・端末分離 | brand/theme.json、theme.py、source/layout/ / device_styles.py |

## 生成順

全体：`python build.py`。コピー変換→ヘッダー→デモ→HUD→ヒーロー→ホーム部品→shop→referenceの順。referenceが最後に商品ページ・結合カタログとcheckout.pyのカート/フォームを出力する。

対象別：
- ヒーロー：`python build.py --hero-only`
- ホーム部品：`python home_sections.py` の後 `python shop.py`（カテゴリー導線とカートを再接続）
- カート・商品：`python shop.py`。CLI内でreference.pyも呼ぶ。
- 移植のみ：`python reference.py`（商品・カート・フォームを再生成）
- header-only、layout-only、tabs-only、demo-only、hud-only等は旧基盤の処理。新ページも対象になる場合があるため、生成前後の差分を確認し、商品側は最後にreference.pyで整える。

全体ビルドは大量の差分が出る場合がある。限定修正は対応publisherを使い、無関係な生成差分を混ぜない。共通CSSだけなら正本変更後、同じ内容を対応するdocs公開パスへコピー可能（publisherでも同じファイルをコピーする）。

## 依存と確認

Python：requirements.txtのrequests、beautifulsoup4、lxml、tinycss2。
Node：`node test-shop.cjs`、`node test-reference.cjs`、`node test-checkout.cjs`。比較UI等の動作変更は非表示IABで実操作も確認。
プレビュー：`python preview.py` → http://127.0.0.1:8766/crystal-clean-home/ 。既存サーバーが起動中なら重複起動しない。

変更を対象別にgit addしてコミット・push。未管理ファイルを一括追加しない。GitHub Pagesの対象SHA成功と公開レスポンスを照合する。実装変更なしの文書整理ではサイトの再ビルドは不要。

## 取得ソースとレポート

旧基盤取得はcapture.json、商品取得はsource/osouji/capture.json。取得ソースは再生成に必要なので旧式という理由で削除しない。再取得は参考元の料金等も変わるため、単なる再ビルドと混同しない。
reference-report.json、copy-change-log.json等は生成・照合データで、現在の承認事項の正本ではない。過去の公開状態を固定文でMDへ上書きする旧補助スクリプトは撤去済み。

カートの取得ソース：capture_checkout.py（カート・入力・確認。実予約送信は行わない）、capture_cart_samples.py（16セットの公開カート応答・推薦カード）。通常生成時に再取得しない。source/osouji/checkout/set-samples.jsonを価格根拠として保持。旧brand/shopの独自shell/script/CSSは撤去済み。住所補完データはbrand/reference/postal-data.js（日本郵便2026-08-31版、120717郵便番号）。

## 共通UIとカード文言

- 全ページの実テキスト書体とセクション三角形：brand/header/typography.css、section-triangles.svg。header/style.cssから参照し、header.pyで配布する。
- カード文言の正本：brand/reference/card-copy.json（確認済みの原文と置換文221組）。card_copy.pyが原文に完全一致するテキストノードだけを置換する。未知の文章への一般的な単語置換は行わない。
- 適用：home_sections.py、reference.py、checkout.py。要素・属性・リンク・注意書きを保持する。商品名、料金、作業範囲の列挙、お客様の声は編集対象から除外。
- 検証：python test_card_copy.py（元HTMLの構造/属性/数値/お客様の声/再適用時の不変性）、python audit_shared_ui.py（共有CSS・接続・カード文言の棚卸し）。生成レポートはcard-copy-review.jsonとcard-copy-inventory.json。

- 共通カテゴリーカード形状・帯・ラベル・hover：brand/header/category-cards.css。参考元デザインへ復元済み。比較用nth-child例外は再追加しない。
