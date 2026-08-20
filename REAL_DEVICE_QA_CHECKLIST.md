# REAL DEVICE QA — v101.90

All scenarios are **NOT_TESTED** until executed on the stated real device/build.

- G-01 — iPad screenshot target: open `PASSION24.TEXT.RELATED_HOUR_18`, select `ÊTRE, À L’INTÉRIEUR` inside `TOME 10 — 12 NOVEMBRE 1910 — …`; app bar `Surligner / Note / Copier / Fermer` must appear.
- G-02 — iPhone screenshot target: open `PASSION24.TEXT.PART_III_DIVINE_PASSION`, select words around `JÉSUS PAR LA DIVINITÉ N’ÉTAIENT` inside `TOME 12 — 20 MARS 1919 — …`; app bar must appear.
- G-03 — iPhone: apply yellow partial extract-heading highlight, reload, verify persistence.
- G-04 — iPhone: recolour the heading highlight blue, remove, then Annuler; exact range/colour must restore.
- G-05 — iPhone: add a Note and use Copier on selected extract-heading words.
- G-06 — iPad: select text spanning a wrapped line within a long extract heading; exact selected words only are highlighted.
- G-07 — iPhone/iPad: live `Index des extraits` buttons still scroll to the same 94 heading anchors.
- G-08 — iPhone: top-level Approfondir reader-title highlighting still works.
- G-09 — iPhone: ordinary Approfondir body highlighting still works.
- G-10 — Samsung/Android: explicit Paragraphe mode can treat an internal extract heading as one whole `library_text` target; native word selection remains disabled.
- G-11 — `Marquer cette lecture` remains independent of extract-heading text highlights.
- G-12 — Mon Espace opens an extract-heading highlight back to the same reading/anchor.
- G-13 — JSON export/import preserves extract-heading highlight/note records.
- G-14 — installed PWA: confirm app displays v101.90 and cache generation is `luisa-24h-v101-90`.
