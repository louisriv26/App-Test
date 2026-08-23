# REAL DEVICE QA — v101.105

Build: `v101.105`  
Cache: `luisa-24h-v101-103`

All scenarios are NOT_TESTED until executed on the exact final bytes.

- G-00A iPad/iPhone H20.P016: outer guillemets are not visible; no stranded opening guillemet; Jesus text begins cleanly after the intended paragraph boundary.
- G-00B iPad/iPhone kept-quotation regression: `«Voici l'homme»`, `«Crucifie-Le...»`, `« J’ai soif »` and `«le Tout»` remain visible and are not split after the opening guillemet.

- G-01 iPhone exact-text highlight.
- G-02 iPad exact-text highlight.
- G-03 Samsung whole-visible-paragraph highlight.
- G-04 RA19B continuous-prose representative case.
- G-05 RA19B source-backed preserved-break representative case.
- G-06 Highlight add/recolour/remove preserves RA19B boundary action.
- G-07 Promesses et bienfaits Jesus differentiation.
- G-08 Mon Espace visual-paragraph representation.
- G-09 Search/deep link stable anchor.
- G-10 Notes/favourites persistence.
- G-11 Portrait/landscape scroll.
- G-12 Installed PWA update to v101.105.
- G-13 Live GitHub Pages byte binding.
- G-14 True offline/airplane reopen.
- G-15 VoiceOver/TalkBack representative navigation.

## v101.105 mandatory presentation fixtures
- iPad/iPhone H20.P016: direct Jesus words inline with native paragraph rhythm; redundant outer guillemets invisible.
- iPad/iPhone IMG_4532 class: `je me disais : « Mon Jésus...` stays one visual paragraph; no orphan opening guillemet.
- Verify all visible quotation openings never strand `«` from the first lexical word.
- Samsung: whole-paragraph target matches the same visible joined paragraph as the reader.
