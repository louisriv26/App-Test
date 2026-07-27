# Luisa — 24 Heures de la Passion

Version: `v101.27` — **staging / test build. NOT authorised for production.**

App SHA-256: `6fd1f2c6fe918d041718c1f47fb745d8314483eac106e3315404d68bd47bcd2c` (1,730,985 bytes). `index.html` and `luisa_24_heures.html` are byte-identical replicas.

Notes: Two changes stacked on production v101.25. **(1) The accepted v101.26 corpus** — 48 R3A text operations across 44 paragraphs (reverence capitalisation per the documented referent policy, grammar/agreement/punctuation fixes, and 9 substantive editorial items individually approved by Louis on 2026-07-27). **(2) The v101.27 persistence correction** — v101.26 introduced `lp24_snapshot_v2` as the canonical personal-data snapshot but left three mutation paths writing only the old legacy keys, so the canonical snapshot went stale and won on the next load. Fixed by adding `state.lastHour` as the single live source for the resume Hour, making `applyPersonalSnapshot()` a pure in-memory apply (it previously wrote legacy storage, which is what overwrote newer values with older ones), and committing `openHour`, study mode and cycle reset through the canonical snapshot. `lp24_lastHour` and `lp24_mode` are now migration/mirror-only — live call sites dropped from 12 to 3. Production v101.25 never had these defects: it has no canonical snapshot layer, so no divergence was possible. Carries all prior v101.x fixes (v101.2 through v101.26). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure, protected declaration hashes) pass, and the persistence correction is proven by executable browser tests using genuine reload cycles. Real-device validation is `NOT_TESTED` — that is what this staging build is for. The Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) remains under investigation.

## What to test on device — priority order

These three are the actual fix. Each needs a **full app close and reopen** (not just backgrounding) between the action and the check.

1. **Resume Hour is remembered.** Open an Hour, read a little, close the app completely, reopen. The home screen must offer "Reprendre la lecture" pointing at that same Hour.
2. **Study mode sticks.** Toggle the `#` study-marks button on, close the app completely, reopen. Study marks must still be on.
3. **Reset stays reset.** With some progress recorded, use "Recommencer les 24 Heures" / "Réinitialiser ma progression" and confirm. Close the app completely, reopen. There must be **no** "Reprendre la lecture" card — the home screen should offer "Prier la 1re Heure". *This was the worst defect: the old resume Hour came back after a reset.*

Then, in rough order of risk:

4. **Upgrade with existing data.** On a device that already has the production build installed with real notes, highlights and progress, upgrade to this build and confirm nothing is lost. This is the highest-risk untested path — every existing user will take it.
5. Notes, highlights and progress still save and survive a reopen.
6. Export / import round-trip.
7. Offline launch after first load; the "Actualiser" update flow.
8. General reading, search (including the Réflexions filter), Hour 24 burial + Désolation structure.

## Known limits — not defects

- **Deliberately not fixed in v101.27**, deferred to a later candidate: behaviour when device storage is full or unavailable, malformed/future snapshot recovery, atomic R41 highlight-anchor reset, and honest "not saved" messaging across all mutation paths. If a save fails because storage is full, the app may still report success. Known and out of scope.
- **R3B reflection completeness is not certified** — the supplied Italian edition does not contain the complete *Riflessioni e Pratiche*.

## Desktop verification already completed

```text
Semantic preservation      PASS   CORPUS/SPEECH_DATA/INTERNAL_SUBHEADINGS byte-identical to accepted v101.26
Persistence tests          6/6 PASS post-fix; 3/6 pre-fix (suite proven to detect the defects)
Static resilience guards   16/16
Corpus integrity           44/44
Mutation teeth             11/11 caught
Storage-contract audit     20/20 keys, 0 unclassified
Predeploy check            all passed, 0 warnings
```
