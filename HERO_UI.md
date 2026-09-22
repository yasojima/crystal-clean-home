# ホームのヒーロー仕様

更新：2026-09-23。参考は竹下設計の大画面フレーム。現在の画像はソファ→エアコンフィルター→コンロの生成ビフォーアフター3枚。

- 画像とalt：brand/hero/slides.json、images/。
- PC：desktop.css。ヘッダー実測高をsticky停止位置とし、フレーム高は100dvh−ヘッダー高。後続20vh間隔。最後の画像到達後は全体が上へ抜ける。
- スマホ：mobile.css。相対配置の縦並び。PCと別編集。
- 両方ともobject-fit:cover。左右の白余白なしを優先し、比率差は中央トリミングする。
- script.js：ResizeObserverでヘッダー高を同期。Lenis duration:2、autoRaf:trueをページ全体で継続。ヘッダー・dialog・simulation等の通常入力へ渡すときはresetで慣性を止める。
- GSAP/ScrollTriggerは元のyPercent:0→0処理。独自ズームなし。PCのwill-changeとcontain:paintを維持。
- hero.pyとbuild.py --hero-onlyで生成。vendorのライセンス表記を維持。

右側問い合わせ・LINEを維持。ホームの簡単見積りパネルは別処理shop.pyでカート導線へ変更済み。
過去のcontain表示、ヒーロー境界で通常スクロールに切り替える方式、仮写真待ちの記述は現行ではない。経緯はGit履歴。
商品ページの左右比較バーはbrand/reference側の別UIで、このLenisを使用しない。
