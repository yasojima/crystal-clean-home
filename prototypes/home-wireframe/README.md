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
