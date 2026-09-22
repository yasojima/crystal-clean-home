# Shopping prototype — 2026-09-23

Canonical data: `brand/shop/catalog.json`. Shared renderer: `shop.py`; full build invokes it after homepage sections. Targeted rebuild: `python home_sections.py` then `python shop.py`. PC and mobile overrides are separate.

Routes: `/services/`, `/cart/`, `/estimate/`. Category links on homepage and lower directory lead to filtered catalog. Old homepage floating calculator replaced by cart link. Existing detail pages are retained.

19 cards / 40 variants, including 3 set combinations and 2 individual-estimate consultation items. Prices copied from existing simulation `formConfig` as draft data, not newly approved commercial rates. Existing water-set pricing is used for the three combinations; I-shaped kitchen, standard bathroom and hood are the scope. Do not present this as a complete import of every reference-site service or optional treatment. Existing source price anomalies (standard wax 1,430 vs high-grade 1,100 per square metre) require business review before production. No automatic discounts or source-company campaign offers are implemented.

Cart stores only variant IDs and integer quantities in localStorage; computes current prices from catalog, rejects unknown/invalid records and caps quantities. Contact data lives only in the form DOM. CSP forbids network connections and form submission. Final reservation button opens the demo notice, never submits. Actual booking integration and validated commercial catalog are a later step.

Checks: `node test-shop.cjs` covers duplicates, invalid storage, quantity bounds, variant/area/set totals and all image files. Browser checks cover variant selection, add multiple items, cart persistence, quantity editing, deletion, confirmation and demo completion; responsive checks at 390px and desktop.
