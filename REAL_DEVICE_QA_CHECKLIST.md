# Real-device QA checklist — v101.137 R1

Use only the exact **v101.137 R1** controlled device-test candidate whose SHA-256 is supplied in the external final-validation receipt.

Package identity to verify before testing:
- `app_version = v101.137`
- `build_revision = R1`
- `cache_name = luisa-24h-v101-137-r1`
- `APP_EVIDENCE_STAGE = AUTHORIZED_79_MEDITATION_REFLECTION_SUCCESSOR_R1`

The immutable update predecessor for this test is **v101.136 R5**. Do not substitute v101.135 or an earlier v101.136 revision when testing the in-place update path.

## A. Live-origin binding immediately after test deployment
- Confirm the deployed ZIP SHA-256 matches the external **v101.137 R1** final-validation receipt.
- Open the site normally and confirm **v101.137** in Aide / À propos.
- Confirm `version.json` reports `app_version = v101.137`, `build_revision = R1`, and `cache_name = luisa-24h-v101-137-r1`.
- Hard refresh once and confirm the same identity.
- Confirm no blank/stuck/bootstrap screen.

## B. Existing-PWA update — mandatory
Test an installation currently running **v101.136 R5**; do not uninstall first.
- Before update record: at least one Heure méditée, one note, one highlight, one favourite/library mark if used, last reading position, theme and font size.
- Open installed v101.136 R5 online and trigger/allow the normal update.
- Confirm it becomes **v101.137 / R1**.
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

## D. Targeted v101.137 R1 corpus controls
These are representative physical-device checks of the newly authorized 79-row universe; the package validator separately checks all 79 rows exactly.
- H1: the first meditation includes `Afflictions, tes Affections et tes Réparations`; the standalone final `Gloire au Père,…` record is absent.
- H7 reflection: `Terminer par la prière de remerciement de l’Heure Sainte.` is not displayed as reflection prose in this version.
- H15: the authorized angel-defense wording is visible; the moved body-part devotional expansion is not displayed.
- H16: the moved body-part flagellation-prayer block is not displayed.
- H18 reflection: the corrected sentence ends `afin qu’elles soient comme un voile qui essuie ses Sueurs et Le réconforte` without malformed syntax.
- H19 reflection: it ends before the documentary letters; the ten moved documentary records are not displayed in the reflection.
- H20 meditation: the Psalm 116 / `Gloire au Père` insertion is absent from canonical meditation prose.
- H23: representative corrected wording includes `Défends-Moi, fais-Moi réparation, conduis-les tous dans mon Cœur`; no Form-A/Form-B synthesis is visible.
- H24: the burial/deposition block is still located in H24; the authorized burial wording corrections render normally; Desolation remains present; the leading duplicate Desolation sentence and final Latin Marian paratext are not displayed.

## E. Inherited regression controls from v101.136 R5
- H19 P118 repaired French sentence: no truncation/garbling.
- H22 authorized quote/punctuation loci: no stale period after the closing guillemet where v101.136 removed it.
- `RELATED_HOUR_06.P013`: paragraph flow normal; historical breaks preserved.
- `RELATED_HOUR_16.P038`: no break splitting the word `en`.
- `RELATED_HOUR_04.P127`: remapped break visually natural.
- H24 end-of-cycle panel, Méditée toggle and restart behaviour correct.
- Tome 20 — 25 décembre 1926 linked text: verify `à la porte de leur cœur` (with `de`).

## F. Offline gate
After a complete online load of v101.137 R1:
- close the PWA, disconnect network/enable airplane mode, cold-open it;
- confirm **v101.137 R1** opens normally; open two Heures, one linked text, Mon Espace and Aide;
- close/reopen once more offline; restore network and confirm no downgrade or repair loop.

## G. Accessibility gate
- iPhone/iPad: representative VoiceOver navigation of main nav, Aide, Méditée, search and back controls.
- Samsung: corresponding TalkBack checks.
- No visible actionable button unnamed; focus restoration after modal/Aide closure sensible.

## Release rule
Any failure involving version/update identity, user-data loss, blank/stuck startup, true-offline cold reopen, text corruption, H23 recension contamination, H24 scope/placement, or persistent navigation/rendering regression is a **release blocker**. Final public release remains unauthorized until all mandatory physical/live gates are closed.
