# 現在地と正本一覧

更新：2026-09-26 / CCH-WEB-20260921 / PRIMARY_ROUTE_ID：WEB。

ホームの骨格・デザインは一旦区切り、サービス内容は後から確定する。共通UIは441ページへ生成する。ホームだけにヘッダーを表示し、下層ページは右上MENUを常設する。追従バーとフッターは共通。PC/SPのCSS・画像選択・UI寸法設定はsource/deviceの端末別正本で管理する。

商品8カテゴリは元HTMLの複製を構造の入力として `product_wireframe.py` で組み立て、`integrated_product_pages.py` を通じて本編 `docs/house-cleaning/` に生成する。口コミ48件は見出しと元の話題を保って加筆した掲載用サンプルであり、実際の顧客の声ではない。洗濯機の種類別3ページは既存の本編ページを維持する。共通の構造・文言は `product_wireframe.py` と `source/product-wireframe/*-copy.json`、PC/SPの見た目は `source/device/{desktop,mobile}/css/product-wireframe/` が正本。8カテゴリのオプションは個別詳細を外して説明3行以内とし、親商品の「詳しく見る」はデモ注記をポップアップ表示する。現行カテゴリー画像は `brand/category-illustrations-v2/`。不要になった旧画像等はデスクトップの `削除用/Crystal-Clean-Home_20260924` で最終削除待ち。8商品ページの公開反映はGitHub Pagesで確認済みで、実機検収は別に確認する。

2026-09-26時点の本編出力：洗濯機・コーティング・「その他」の事例は独自生成の比較画像各2組を使用。洗濯機の商品一覧は3種類を個別見出しで区切り、水まわりから複製した商品カード・オプション欄に種類別3ページのID・価格・素材を入れ、カートへ直接追加できる。3カテゴリのおすすめ各2件も既存のプランカード型と商品IDへ接続。「その他」の外壁手洗い洗浄は元の基本料金44,000円と追加1㎡990円を本編カートへ接続。ホーム上下のカテゴリーカード16件は各本編ページへ接続。実予約送信・実機検収は未実施。

法人向けページ `/service/corporation/` は、商品ページと共通の紺色・游明朝の全幅見出し帯、独自の本文7箇所、対象を保ちつつ元画像と構図・視点を変えた人物なしのリアルなアニメ調画像18点を使用する。見出し左の装飾マークを除き、後付けした淡い水色の背景帯は元に戻す。正本は `corporation.py`、`brand/corporation/images/`、`source/device/{desktop,mobile}/css/corporation.css`。旧ラフ出力 `docs/_product-wireframe/` は現行ビルドで生成しない。

お問い合わせ `/contact/` は最上部の「お問い合わせ窓口」だけを法人向けと同じ全幅の紺帯にする。画像は追加せず、フォーム内見出しと項目を維持する。正本は `shared_ui.py` と端末別の `css/brand/shared-ui/style.css`。

カートは取得済みの参考HTML/CSSとSwiperを使用し、自社のローカル計算・保存へ接続する。空状態も参考元の見出し・セクション構造に合わせる。追従バー左はカートアイコン、右はお問い合わせ。両ラベルは同じ書体・太さ。実予約送信・全クーポン判定は未接続。

「初めての方へ」 `/first/` に、初めての方へ・清掃への取り組み・感染予防への取り組みの順で既存内容を仮統合した。本文と画像は変更せず、LP制作前の素材集約とする。独立 `/reason/` の生成入力と公開HTMLを削除し、技術研修 `/reason/training/` は維持する。感染予防は元から `/first/` 内にあり独立ページはない。グローバルナビはHOME・サービスと料金・初めての方へ・訪問地域の4項目、PC幅840px。

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

## Route確認・引継ぎ完了
ROUTE_LOCK_REFRESH（2026-09-23、新担当取込）：WEB / 1.0-rc46 / EXECUTION_READY。PACKAGE_MANIFEST SHA256=C8B737D4244B962D9D1EBC3570EAD4D5EFA22BBB51FB7C718E0B2C2C774B1B0E、PACKAGE_START SHA256=991ECC24C98BDD1AF10FF67A0F4A7B3C081097EEFC51B8251972FBBC7BC33F81を現物確認。許可する実行参照は02_WEB_Web制作のみ、他Route参照0。source rootと本タスクcwdは上記作業正本で一致。外部AI・PDCAはPROJECT_EXCEPTIONSと人間指示により除外。VS Codeゲートの新規検証は未実施でPASS扱いにせず、既存案件を本Codexタスクで継続する明示指示に従う。

引継ぎ閉鎖：元task 01a0bfe6-f9a1-7253-81ba-2d4fba702ad4 → 本task 01a0ce6d-933e-7ce1-a618-a3ac155e38d5。同一保存済みProject 76b77638-9f25-49f5-809a-9e3ca8c373a2。元担当のHANDOFF_COMPLETE受領記録（2026-09-23T13:22:01.329Z）を確認。未完了3点は80532f37で実装し、Pages 35868425891成功・公開29リンク遷移確認まで完了。確定内容を仕様書とSITE_VERIFICATIONへ移したため、一時引継ぎ書・受領JSONを閉鎖整理。
