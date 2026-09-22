# Reference import

2026-09-23: user explicitly requested public Osoujihonpo source composition, images, product cards, copy and links, with only store name, fonts and palette adapted. No service pruning in this pass.

- Original public responses: `source/osouji`, captured by `capture_reference.py` (52 cleaning pages, 1036 assets).
- Publisher: `reference.py`, invoked after `shop.py` and by `build.py`.
- Main markup and source CSS dimensions/breakpoints retained. CSS scoped to avoid the existing header's styles. Yu Mincho headings; Yu Gothic body/buttons; existing blue palette.
- Native common.js supplies tabs, comparison images, accordions, dialogs and sliders. Its remote header/cart initialization is disabled; original unmodified bundle is archived.
- `bridge.js` connects source product controls to the local estimate cart. Public numeric prices, room variants and visible quantity tiers are extracted. Options require their parent service.
- Private reference APIs, booking submission and all backend promotion rules cannot be transplanted from public HTML. Final booking remains the existing demo (no transmission). Prices/campaign copy are reference snapshots pending the user's later selection and pricing decisions.
- Uncaptured campaign/information links remain external. Large reference footer is outside the previously agreed import boundary.
- Source server returned 404 for `assets/css/house-cleaning/others.css`, `assets/css/images/shop/top/prefecture-bg.webp`, and `assets/images/common-parts/illust/office-uv-flooring.svg`. See capture.json. These are source gaps, not successful downloads.
- Verification: test-shop.cjs, test-reference.cjs; browser set quantity 2 = 68,200; room 104 = 35,200; AC 2 = 22,000; combined = 125,400; native FAQ and comparison tabs.
