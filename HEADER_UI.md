# 共通ヘッダー仕様

更新：2026-09-23。

正本はbrand/header/。template.htmlがロゴ・連絡先・7メニュー・詳細21リンクを所有し、style.css、desktop.css、mobile.css、script.jsが表示と開閉を制御する。事業情報はbrand/site.json。pages.jsonはページ別拡張用で、現在空。

HOME、サービスと料金、清掃への取り組み、初めての方へ、ご利用前のご質問、対応地域、会社概要。サービスのみメガメニューあり。既存詳細リンクは旧/service/へ残るものがある。
PCは固定ヘッダー・半透明背景とぼかし、ホバーで白いメガメニューを開閉。992px以下はタップ式。Esc・キーボード操作と動きを減らす設定を扱う。旧スクロール時の上段隠しは使わない。

旧基盤はheader.py、新カートはshop.py、移植ページはreference.pyが同じtemplateを組み込む。移植用host.cssは元テーマCSSを.cch-hostへスコープ化する。
テンプレート変更後は生成経路を横断して確認する。旧header-onlyだけの検証で全ページ反映完了としない。reference.pyは現在pages.json拡張を読まず、将来その機能を使う場合は対応が必要。

パンくず文字撤去・HUD・統一タブ名は旧基盤に適用済み。新移植ページは元パンくずとページ別タイトルを出力し、HUDを含まない。この差分はSITE_VERIFICATION.mdで残件管理する。
参考：idhome.co.jpのすりガラス・メガメニュー。取得比較資料design/reference-header/は実行ソースではない。
