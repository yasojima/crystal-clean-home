# 現在地と正本一覧

更新：2026-09-23 / CCH-WEB-20260921 / PRIMARY_ROUTE_ID：WEB。

ホームの骨格・デザインは一旦区切り、サービス内容は後から確定する。共通UIは443ページへ生成する。ホームだけにヘッダーを表示し、下層ページは右上MENUを常設する。追従バーとフッターは共通。PC/SPのCSS・画像選択・UI寸法設定はsource/deviceの端末別正本で管理する。

カートは取得済みの参考HTML/CSSとSwiperを使用し、自社のローカル計算・保存へ接続する。空状態も参考元の見出し・セクション構造に合わせる。追従バー左はカートアイコン、右はお問い合わせ。両ラベルは同じ書体・太さ。実予約送信・全クーポン判定は未接続。

## 正本

| 資料 | 内容 |
| --- | --- |
| Crystal-Clean-Home_要件定義書.md | 現行要求と未確定事項 |
| EDITING_GUIDE.md | 編集元、生成順、検証 |
| HEADER_UI.md / HERO_UI.md | 共通UIとホームのフレーム |
| DEVICE_LAYOUT.md | PC/SPの所有境界 |
| DEMO_MODE.md | 実送信と情報リンクの区別 |
| SITE_VERIFICATION.md | 実施済み確認、未確認、制約 |
| CHANGELOG.md | 現行方針への変更決定 |
| PROJECT_EXCEPTIONS.md | 外部監査等の適用除外 |
| brand/reference/README.md | 商品・カートの生成 |

作業：C:/Users/yasoj/codex Projects/Crystal Clean Home。
Git：https://github.com/yasojima/crystal-clean-home （main）。公開：https://yasojima.github.io/crystal-clean-home/ （docs）。
source/は取込データと端末別正本、brand/は共有構造とロジック、docs/は生成結果。Driveは参照専用。取得元の来歴はcaptureデータに保持し、ホーム実行HTMLから不要な他社名・旧メタ情報を除去する。来歴の保持と自社サービスの承認は別である。
