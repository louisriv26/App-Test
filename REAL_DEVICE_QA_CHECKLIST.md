# Real-device QA checklist — v101.136 R5

Use only the exact **v101.136 R5** GitHub/device-test candidate whose SHA-256 is supplied in the external release receipt.

Package identity to verify before testing:
- `app_version = v101.136`
- `build_revision = R5`
- `cache_name = luisa-24h-v101-136-r5`
- `APP_EVIDENCE_STAGE = INTERIM_CLOSED_97_SUCCESSOR_R5_FOUR_PASS_RELEASE_RECONCILED`

Do not use v101.136 R1, R2, R3 or R4 for deployment; R5 supersedes them for device testing. R5 changes release engineering/documentation only; the 97-record canonical corpus is identical to R4.

## A. Live-origin binding immediately after test deployment
- Confirm the deployed ZIP SHA-256 matches the external R5 release receipt.
- Open the site normally and confirm **v101.136** in Aide / À propos.
- Confirm `version.json` reports `app_version = v101.136`, `build_revision = R5`, and `cache_name = luisa-24h-v101-136-r5`.
- Hard refresh once and confirm the same identity.
- Confirm no blank/stuck/bootstrap screen.

## B. Existing-PWA update — mandatory
Test an installation currently running **v101.135**; do not uninstall first.
- Before update record: at least one Heure méditée, one note, one highlight, one favourite/library mark if used, last reading position, theme and font size.
- Open installed v101.135 online and trigger/allow the normal update.
- Confirm it becomes **v101.136 / R5**.
- Close completely and reopen **three times**.
- Confirm no fallback to v101.135, R1/R2/R3/R4 cache, blank screen, or repair loop.
- Confirm all pre-existing user data and last-place state remain coherent.

## C. Core functional smoke on each physical device
Run on iPhone, iPad portrait, iPad landscape, and Samsung/Android. On each:
- home renders/scrolls; all 24 Heures open; search works; Mon Espace opens; Aide opens;
- light/dark theme and normal/large font work;
- Méditée top/bottom controls remain synchronized;
- notes/highlights can be created and persist after close/reopen;
- no horizontal clipping/overflow; back navigation and last-place restore work.

## D. Targeted v136 controls
- H19 P118 repaired French sentence: no truncation/garbling.
- H22 authorized quote/punctuation loci: no stale period after the closing guillemet where v136 removed it.
- `RELATED_HOUR_06.P013`: paragraph flow normal; historical breaks preserved.
- `RELATED_HOUR_16.P038`: no break splitting the word `en`.
- `RELATED_HOUR_04.P127`: remapped break visually natural.
- H23: unchanged from v101.135; no new AFLP/source-critical material inserted.
- H24: end-of-cycle panel, Méditée toggle and restart behaviour correct.
- Tome 20 — 25 décembre 1926 linked text: verify `à la porte de leur cœur` (with `de`).

## E. Offline gate
After a complete online load of v101.136 R5:
- close the PWA, disconnect network/enable airplane mode, cold-open it;
- confirm v101.136 opens normally; open two Heures, one linked text, Mon Espace and Aide;
- close/reopen once more offline; restore network and confirm no downgrade or repair loop.

## F. Accessibility gate
- iPhone/iPad: representative VoiceOver navigation of main nav, Aide, Méditée, search and back controls.
- Samsung: corresponding TalkBack checks.
- No visible actionable button unnamed; focus restoration after modal/Aide closure sensible.

## Release rule
Any failure involving version/update identity, user-data loss, blank/stuck startup, true-offline cold reopen, text corruption, wrong H23 content, or persistent navigation/rendering regression is a **release blocker**. Final public release remains unauthorized until all mandatory physical/live gates are closed.
