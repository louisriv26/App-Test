# Real-device QA checklist — v101.137 R2

Use only the exact **v101.137 R2** controlled device-test candidate whose SHA-256 is supplied in the external final-validation receipt.

Package identity to verify before testing:
- `app_version = v101.137`
- `build_revision = R2`
- `cache_name = luisa-24h-v101-137-r2`
- `APP_EVIDENCE_STAGE = TEXTUAL_PROVENANCE_ABOUT_RECONCILIATION_R2`
- Aide / À propos displays **v101.137 R2**
- corpus fingerprint begins `87733d22b5e899e2` and remains identical to R1

The immutable installed update predecessor for this test is **v101.136 R5**. R1 is the immutable content predecessor for R2 but is not the required installed-PWA update starting point.

## A. Live-origin binding immediately after test deployment
- Confirm the deployed ZIP SHA-256 matches the external **v101.137 R2** final-validation receipt.
- Open Aide / À propos and confirm **v101.137 R2**.
- Confirm `Édition française de base : GE / Lumen Luminis / septembre 2021`.
- Confirm the Validation textuelle paragraph states that all 24 meditations and 24 Réflexions et pratiques, including H24 Desolation, underwent source-critical validation and were compared Hour by Hour with AFLP 27th edition.
- Confirm the scope note says the associated Livre du Ciel texts in Approfondir are a distinct validation programme.
- Confirm `version.json` reports `app_version = v101.137`, `build_revision = R2`, `cache_name = luisa-24h-v101-137-r2`.
- Use `Signaler un problème de texte` and `Copier les diagnostics`; both copied payloads must contain `Version : v101.137 R2`.
- Hard refresh once and confirm the same identity; no blank/stuck/bootstrap screen.

## B. Existing-PWA update — mandatory
Test an installation currently running **v101.136 R5**; do not uninstall first.
- Before update record: at least one Heure méditée, one note, one highlight, one favourite/library mark if used, last reading position, theme and font size.
- Open installed v101.136 R5 online and trigger/allow the normal update.
- Confirm it becomes **v101.137 R2**.
- Close completely and reopen **three times**.
- Confirm no fallback to v101.136 R5 or an older cache, blank screen, or repair loop.
- Confirm all pre-existing user data and last-place state remain coherent.

## C. Core functional smoke on each physical device
Run on iPhone, iPad portrait, iPad landscape, and Samsung/Android. On each:
- home renders/scrolls; all 24 Heures open; search works; Mon Espace opens; Aide opens;
- light/dark theme and normal/large font work;
- Méditée top/bottom controls remain synchronized;
- notes/highlights can be created and persist after close/reopen;
- no horizontal clipping/overflow; back navigation and last-place restore work.

## D. R2 provenance-only invariants
- Corpus fingerprint displayed in Aide matches R1 (`87733d22b5e899e2…`).
- No meditation/reflection wording differs from the certified R1 corpus.
- No linked Livre du Ciel text differs from R1.
- The 24 preserve-move records remain absent from the current UI.

## E. Representative inherited R1 corpus controls
- H1: `Afflictions, tes Affections et tes Réparations`; standalone final `Gloire au Père,…` record absent.
- H15: authorized angel-defense wording visible; moved devotional expansion absent.
- H18 reflection: corrected veil/sweat sentence renders normally.
- H19 reflection: documentary letters absent from reflection.
- H20 meditation: Psalm 116 / Gloria insertion absent from canonical prose.
- H23: `Défends-Moi, fais-Moi réparation, conduis-les tous dans mon Cœur`; no A/B synthesis.
- H24: burial/deposition remains in H24; Desolation present; leading duplicate and final Latin paratext absent.

## F. Inherited v101.136 R5 regression controls
- H19 P118 intact; H22 punctuation loci correct; `RELATED_HOUR_06.P013` flow preserved; `RELATED_HOUR_16.P038` does not split `en`; `RELATED_HOUR_04.P127` break natural; H24 cycle controls correct; Tome 20 — 25 décembre 1926 displays `à la porte de leur cœur`.

## G. Offline gate
After a complete online load of v101.137 R2: close PWA, enable airplane mode, cold-open; open two Heures, one linked text, Mon Espace and Aide; close/reopen once more offline; restore network and confirm no downgrade or repair loop.

## H. Accessibility gate
Representative VoiceOver/TalkBack on main navigation, Aide, Méditée, search/back controls; actionable controls named; focus restoration sensible.

## Release rule
Any failure involving version/update identity, provenance misstatement, user-data loss, blank/stuck startup, true-offline cold reopen, text corruption, H23 recension contamination, H24 scope/placement, or persistent navigation/rendering regression is a **release blocker**. Final public release remains unauthorized until mandatory physical/live gates are closed.
