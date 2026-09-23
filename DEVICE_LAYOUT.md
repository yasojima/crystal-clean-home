# PC・スマホの編集境界

更新：2026-09-23。

| 対象 | 共通 / PC / スマホ |
| --- | --- |
| 旧基盤 | source/layout/manifest.json、desktop/site.css、mobile/site.css |
| 旧見積 | source/layout/desktop/estimate.css、mobile/estimate.css |
| 共通ヘッダー | brand/header/style.css、desktop.css、mobile.css |
| ヒーロー | brand/hero/desktop.css、mobile.css、script.js |
| 新カート | brand/shop/style.css、desktop.css、mobile.css |
| 移植ページ | source/osouji/assets/cssの元メディアクエリ＋brand/reference/brand.css、desktop.css、mobile.css |

ヘッダー・旧基盤・ヒーローのPC境界は993px、スマホ/タブレットは992px以下。移植本文には元サイト独自のブレークポイントがあり、一律993pxではない。
文章・画像・商品データは端末別に複製しない。移植CSSは.cch-reference、ホストCSSは.cch-hostにスコープ化する。生成・公開はEDITING_GUIDE.md参照。
過去のPC/390pxブラウザー確認は実機検収ではない。現在の全ページ・全幅で目視合格したとは扱わない。

## 2026-09-23 動画ワイヤーフレームと右側ナビ

ホームは全幅のグレー動画仮枠へ変更。ヘッダーは固定せずスクロールで上へ抜ける。PCはヘッダー通過後に右側MENUを表示、スマートフォンは常時表示。右から開くメニューは既存6項目とサービス詳細を共有する。お見積りアイコンは右側に追従し、既存カートの件数・合計と連動する。実動画は後日video.jsonで設定。
