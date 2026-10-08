# HOME ピックアップ・お知らせのワイヤーフレーム

現行HOMEから生成するローカルの複製です。上部の「エアコン２台、まとめてお得に。」を残し、後半のお悩みと末尾８項目の間に３つの漫画LP用のピックアップ枠を置きます。既存の２枚バナーと全セクションを保持します。

- [上部のエアコン２台バナー](http://127.0.0.1:8773/home-wireframe/#home-pickup-banner)
- [後半のピックアップ３枠](http://127.0.0.1:8773/home-wireframe/#home-pickup)
- [お知らせＡ](http://127.0.0.1:8773/home-wireframe/?news=A#wf-news)／[Ｂ](http://127.0.0.1:8773/home-wireframe/?news=B#wf-news)／[Ｃ](http://127.0.0.1:8773/home-wireframe/?news=C#wf-news)

後半の題材は「ハウスクリーニングが人気な理由」「エアコンクリーニングが人気な理由」「水まわりが人気な理由」の３つ。今回はNO IMAGEの骨格だけです。お客様がGPTと台本・シーンを作成し、Codexがその台本をもとに、既存beginnerのようなアニメ調・４コマ漫画のLPとバナーを制作します。完成後に新規LPのリンクを接続します。未制作の枠に仮のクリック先は付けません。

上部のリンク先は既存 `/house-cleaning/aircon/`。割引額は既存カタログの１台価格と２台以上価格の差額から表示し、機種・数量・税込の条件を併記します。

お知らせの３つの形は保持します。仮原稿の３件を一覧・注目１件＋２件・３カードで比較し、本文・一覧をダイアログで確認できます。比較表示と固定見積もりの表示切替も保持します。

上部バナーと後半３枠の正本は `tools/home_pickups.py`。公開HOMEへ組み込み、`build.py` は本番ソースから複製する。`index.html` は生成成果物。NO IMAGEはHOME冒頭のプレースホルダーCSSを再利用します。既存マークアップの保持をビルド時に検査し、素材を複製しません。公開HOMEへの反映はCHG-2026-10-07-015で確定しました。お知らせの３案は比較画面だけに保持します。

```powershell
python prototypes/home-wireframe/build.py
python prototypes/home-wireframe/serve.py --port 8773
```

決定事項はプロジェクト最上層のGoogle Docs議事録の「7. HOMEのピックアップと漫画LPの制作方針」にも記録しています。

## 2026-10-07 採用エアコンバナーの追従

CHG-2026-10-07-020で黄色×青のA案を本編へ採用しました。このHOME比較は本編から生成し、同じ１素材を参照します。画像全体はリンクにせず、料金・サービスを見るCTAだけを操作できるようにしています。

今回のaircon-banner３案比較と旧検証画像・生成時の複製は、デスクトップの削除用フォルダーへ退避済みです。本編素材と生成情報の所有元はsource/site/assets/images/home/aircon-bundle-banner.png、source/home-pickup-banner、tools/home_pickups.pyです。統合後の確認記録はevidence/2026-10-07/aircon-banner-integration。このHOME比較と未採用のお知らせ３案は維持します。

## 法人ページの本編統合

CHG-2026-10-08-017で法人の採用構成を本編へ移しました。[本編の法人ページ](http://127.0.0.1:8773/business/cleaning/)を使用します。法人のbusiness・business-copy比較フォルダーは既存の削除用へ移動済みです。生成正本はtools/build_office_cleaning.py、原稿と構造はsource/office-cleaning、表示はsource/site/assets/css/office-cleaning.cssです。このHOME比較とお知らせの3案は保持します。

法人本文の現在の構成はCHG-2026-10-08-022です。参考部分の導入・左右交互4説明・12写真一覧・締めの文章を本編に適用し、法人の比較複製は作成しません。


法人の冒頭はCHG-2026-10-09-002により、サービス8分類と同じsource/shared-ui/service-banner.html、tools/service_banner.py、aircon-hero.css、service-first-view.jsで管理します。法人用の帯を別所有しません。本文はCHG-022を維持します。


[変更 2026-10-09 / CHG-2026-10-09-003] 本編のサービス8分類の帯へPC用横長広告とスマホ用画像を適用。画像割り当てはcopy.json.banners、構造・高さ・Check!の配置は共通正本で管理します。帯高は維持し、共通カードと見積もり導線・商品・価格・カートは変更しません。現行表示と制作情報は仕様書CHG-003、source/service-pages/banner-assets.jsonを参照します。
