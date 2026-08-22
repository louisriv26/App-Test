# Visible paragraph topology — v101.102

One frozen `VISIBLE_PARAGRAPH_TOPOLOGY` supplies presentation boundaries to rendering and Samsung/Android targeting.

- Local presentation boundaries: **243**.
- Cross-record presentation boundaries inside RA19B flow joins/preserves: **4**.
- RA19B `paragraph_break` remains a visible paragraph boundary.
- RA19B `preserve_break` remains non-splitting unless an independent presentation turn boundary occurs.
- Existing stored highlight bytes are not migrated or rewritten; Mon Espace labels are recomputed against current topology.
