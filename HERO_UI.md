# ホームのヒーロー仕様

更新：2026-09-23。

ホームだけに全幅の動画フレームを表示。PCはheight:min(100svh,80vw)、最低330px。992px以下は比率5:4、最低330px。動画はcover。ロゴ・ナビを上に重ね、スクロールで通常どおり上へ抜ける。
現在は木漏れ日の室内sunlit-room.webpと「イメージ動画」を仮表示。brand/hero/video.jsonのsrcが未設定で、実動画は後日差し替える。SCROLL DOWN表示は撤去。旧ソファ等の縦積み比較画像は使用しない。
動画はミュート・ループ、停止ボタンと動きを減らす設定に対応。本文の比較UIは維持する。
見た目はsource/device/{desktop,mobile}/css/brand/hero/video.css、端末別画像設定は同階層images.json。文章と動画設定は共有。hero.pyの更新後にはpython shared_ui.pyで共通UI・端末別表示を再生成する。
