# ローカル試作用・生成写真の対応表

更新：2026-09-26。生成方法は標準の画像生成ツール。すべて構成確認用の独自生成イメージであり、実際の施工写真・実商品の撮影ではない。元の参考写真は生成入力に使わず、作業対象と実写調の方向のみ指定した。人物、店名、ロゴ、文字を避け、被写体を主役にして正面寄りの自然光で描写した。

## ビフォーアフター

元の比較欄がある5カテゴリは、既存のタブ・比較スライダー・750×433の画像枠を保ち、`assets/<カテゴリ>/case-<番号>-before.webp` と `case-<番号>-after.webp` を差し込む。生成時の2列×3段のシートは表示に使わず、未使用素材としてデスクトップの「削除用」へ移した。次の表は作成時に検討した被写体であり、表示対象は「採用組数」の範囲のみ。

| カテゴリ | 1組目 | 2組目 | 3組目 | 採用組数 |
| --- | --- | --- | --- | ---: |
| aircon | アルミフィン | 送風ファン | フィルター | 3 |
| pack | キッチン | 窓・サッシ | — | 2 |
| water | 浴槽・壁面 | トイレ | 洗面台 | 3 |
| washer | 縦型の洗濯槽まわり | ドラム式のドアパッキン | — | 2（今回追加） |
| kitchen | レンジフード | コンロ | 冷蔵庫 | 3 |
| room | フローリング | カーペット | 壁紙 | 3 |
| coating | 浴槽の表面 | フローリング | — | 2（今回追加） |
| others | 外壁 | ベランダ | — | 2（今回追加） |

洗濯機・コーティング・その他の追加分は `case-1-before.png` / `case-1-after.png`、`case-2-before.png` / `case-2-after.png` をそれぞれのカテゴリに置く。元の比較タブ・スライダーと750×433の表示枠を使い、画像そのものは独自生成のPNG。施工前後は同じ被写体を指定して生成した構成確認用のイメージで、実際の施工写真ではない旨を比較欄に明記する。

生成指示の共通部分：`photorealistic-natural; Japanese home-cleaning subjects; exactly 2 columns × 3 rows; each row depicts the same object before and after cleaning from a comparable frontal camera position; natural light, familiar textures; no people, logos, text, montage effects or illustrations.` 各行の被写体は表の通り。特定の施工効果を保証する表示ではない。

## 商品一覧の写真付き親カード

各セルは既存の商品カード順に対応する。`product-sheet*.png` をそのまま正本にし、CSSでセルを表示する。選択カードやオプションの画像は対象外。

| カテゴリ | シート構成とセル順（左→右、上→下） |
| --- | --- |
| aircon | 2×2：壁掛け通常、壁掛けお掃除機能付き、天井埋込。4セル目は未使用。 |
| pack | 1×2：空室の引越し前後、在宅中の家。 |
| water | 2×3：浴室、追い焚き配管、ウルトラファインバブル取付部、浴室乾燥機、トイレ、洗面台。 |
| kitchen | 2×2：レンジフード、キッチン、冷蔵庫、食洗機。 |
| room | 3×2の3枚：床洗浄ワックス、床剥離ワックス、マットレス2種、ソファ、カーペット／壁紙染色、壁紙清掃、窓・サッシ、白木、畳、玄関床／換気ダクト4種、空気清浄機。最後の1セルは未使用。 |
| coating | 2×2の2枚：浴室、キッチン、トイレ、洗面台／床、UV床、床補修。最後の1セルは未使用。 |
| others | 2×2：外壁洗浄、光触媒の対象壁、ベランダ、お墓。 |
| washer | カテゴリ本編に3種類の商品概要カードを追加。縦型・ドラム式の既存の正面画像を使い、種類別ページにある商品名・価格・時間・オプションを表示する。カート操作と詳細条件は元の種類別ページに残す。 |

生成指示の共通部分：`product-mockup; original photorealistic contact sheet with the specified fixed grid and cell order; Japanese residential setting, natural light, frontal or near-frontal object-only views; no people, company branding, lettering, logos or illustration style.` 各シートの被写体と順序は表の通り。
