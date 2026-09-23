# カテゴリー用立体イラスト v1

2026-09-23。承認済みエアコンのリアル寄り立体表現を基準に7点を新規生成。参考元の線画アイコンをトレースせず、視点・設備・構成を描き分けた。白基調、自然な陰影、青/紺の差し色。

- aircon.webp：承認済みエアコン
- pack.webp：マンション住戸全体
- water.webp：浴室・水まわり
- washing.webp：洗濯機
- kitchen.webp：キッチン
- room.webp：窓・壁・床
- coating.webp：床コーティング
- other.webp：外壁洗浄

生成方法：組み込みimage_gen。最終プロンプトはprompts.json。7点とも1536×1024の生成画像。サイトの共通カテゴリーカードへ適用済み。採用WebPを保持し、未参照の生成PNGはGit履歴へ整理。CSSでcontain表示し、元の青帯・ラベル・hoverは維持。header.pyがWebPを公開先へ配布する。
