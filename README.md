# Luisa — 24 Heures de la Passion

Version: `v101.46` — **STAGE 2 UPDATE-FLOW TEST BUILD. NOT authorised for production.**

App SHA-256: `213b5d6290a4e9c57c3ee02d2619c2a2fdc8274ba9aeac92e6153bf7fd68a45d` (1,745,711 bytes). `index.html` and `luisa_24_heures.html` are byte-identical replicas. Service-worker cache: `luisa-24h-v101-46`.

Production remains at **v101.25**. This build is 21 versions ahead of it.

> ## What v101.46 is, and why it exists
>
> **v101.46 differs from v101.45 by exactly one line** — the `APP_VERSION` string — confirmed by a
> line-by-line diff (9,156 lines each, 1 differing). Identity strings in `sw.js` `CACHE_NAME`,
> `manifest.json` and `version.json` follow it. **No logic, corpus, CSS or behaviour change.**
>
> Its only purpose is to give the device test something to update *to*, so the FINDING-01
> service-worker fix can actually be validated. Because nothing else differs, a successful
> single-press update to v101.46 cannot be explained by anything other than the update path
> working correctly. That makes it a clean control.
>
> **Press Actualiser once. It should land on v101.46 immediately.**
>
> The corpus, the persistence work and every other fix below are carried through from v101.45
> byte-identical. v101.46 is not a content release.

## Corpus status — frozen and complete

The corpus is frozen at the **v101.44** content and carried into v101.45 **byte-identical**: all six protected declarations (`CORPUS`, `TEXT_LIBRARY`, `HOUR_LINKED_TEXTS`, `SPEECH_DATA`, `INTERNAL_SUBHEADINGS`, `SPEECH_END_VISUAL_BREAKS`) verified against the v101.44 hash contract, twice — once in the work tree and again from the reopened package.

It contains the full accumulated editorial line:

- **R3A** — 48 text operations across 44 paragraphs (reverence capitalisation per the documented referent policy, grammar/agreement/punctuation fixes, and 9 substantive editorial items individually approved by Louis).
- **R3B — complete, all 24 Hours.** 24 operations across 23 records; 13 Hours corrected, 11 with no substantive change; every Hour `SOURCE_CONTENT_RECONCILED`, none pending. Reconciled against **both** complete Italian witnesses (`IT_COMPLETE_364` and `IT_REFLECTIONS_174`) plus the English witness.
- **v101.40–v101.42** — full-text convergence across every `TEXT_LIBRARY.body` record and all active textual layers; 94/94 Book-of-Heaven extracts reconciled.
- **v101.43–v101.44** — two independent blind adversarial revalidation passes.

Independently reproduced at takeover: 24 Hours, 5 prayers, 4 sections, 40 library objects, 2,735 body records, 381 speech segments, 30 internal subheadings, 94 extracts, 4,501 runtime-addressable DOM targets, 0 duplicate paragraph IDs.

> **Correction to earlier versions of this file.** Every README up to v101.32 carried the line *"R3B reflection completeness is not certified — the supplied Italian edition does not contain the complete Riflessioni e Pratiche."* **That statement is obsolete and was wrong to carry forward.** It described the *initial* Stage S0 attempt, which halted before any modification because the complete Italian binaries were not then available. Once they were supplied, Stage S0 was rerun and R3B was completed at v101.37. The witness in question — `IT_Luisa_Piccarreta_Le_24_Ore_complete_con_Riflessioni_e_Pratiche.pdf`, SHA-256 `7af33d29854078366a4cb0fabafb8b547370faef20997178c91e2bbe84f3d671` — was bound and used in that process. The stale line caused a closed question to be reopened in error during the v101.45 takeover; supersession markers have now been added to the two v101.26-era decision documents that carried it.

## What's new in v101.45 — one fix

**Service-worker update flow (FINDING-01).** Pressing "Actualiser" could complete and leave the client still running the **old** version — permanently, not just for one reload. Reproduced end-to-end, then fixed.

`sw.js`'s install handler precached with `cache.addAll(ASSETS)`, whose fetches consult the browser's HTTP cache. A newly installing worker could therefore pull the *previous* version's files out of the HTTP cache and store them into its *own new* cache. The cache name flipped to the new version while its contents were still the old build; because the fetch handler is cache-first with `{ignoreSearch: true}`, the `?lp_force_reload=` parameter could not escape it. Fixed with:

```js
await cache.addAll(ASSETS.map(u => new Request(u, { cache: 'reload' })));
```

This is the defect behind the reported iOS symptom ("it actualises but stays on the old version", surviving a hard close on iPhone and iPad) and why deleting the home-screen icon and re-adding from Safari was the only reliable remedy — that clears both the service-worker registration and the origin's HTTP cache.

Trade-off accepted: `addAll` is all-or-nothing, so an update now needs real network at install time. If it fails, the old worker keeps serving and the app stays usable — the update simply waits.

## Everything carried forward from v101.26–v101.44

- **Canonical personal-state persistence.** `state.lastHour` is the single live source for the resume Hour; `applyPersonalSnapshot()` is a pure in-memory apply; `openHour`, study mode and cycle reset commit through the canonical snapshot. Fixes the last-opened Hour being forgotten, study mode reverting, and a completed reset resurrecting the old resume Hour.
- **Speech punctuation (P2-COLON).** The introducing colon and its adjacent spaces are no longer deleted from rendered text; 99 paragraphs across 22 Hours plus the Approfondir section restored.
- **Meditated-hour boxes.** 2px border in both themes on the home grid *and* the Heures list, so thickness consistently means "meditated"; completion tick darkened and enlarged.
- **Dark-mode accessibility.** The "· Heure Sainte" label was 2.18:1 against the dark card (WCAG AA needs 4.5:1); now 6.32:1.
- **Theme option** reads "Automatique" rather than "Système".
- **Compléments cleanup.** "Les trois Heures de Gethsémani" shows only its genuine "Règle spéciale" sentence.

## What to test on device

**Read this first — a single-stage test will not test the update fix.**

Because a client already pinned by the old bug can be served the *old* `sw.js` from its HTTP cache, installing this build on a device that already has an older one requires deleting the icon and re-adding from Safari — and **that step bypasses the update path entirely**. So:

- **Stage 1 — install. DONE** on iPhone and iPad (2026-07-31). Icon deleted, v101.45 confirmed in Safari, re-added to Home Screen. The app then offered Actualiser and the update succeeded — an encouraging real-device signal, because the *incoming* worker’s install code is what runs, and v101.45 carries the fix.
- **Stage 2 — the actual update test. THIS BUILD.** From v101.45, press **Actualiser** once. It must land on **v101.46** immediately. *This is the test that matters*, because the starting state is known and the only difference is identity. Do it on both iPhone and iPad — each home-screen icon has its own storage partition, so one does not validate the other.

Then, in order of risk:

1. **Resume Hour is remembered.** Open an Hour, read a little, close the app completely, reopen. Home should offer "Reprendre la lecture" pointing at that Hour.
2. **Study mode sticks.** Toggle the `#` button on, close completely, reopen — still on.
3. **Reset stays reset.** With progress recorded, use "Réinitialiser ma progression" and confirm. Close completely, reopen. There must be **no** "Reprendre la lecture" card.
4. **Speech punctuation.** Hour 20 should read `La première Parole : Père, pardonne-leur car ils ne savent pas ce qu'ils font !` — colon present, spaces either side, no guillemets. Hours 8, 17, 19, 21, 22 have the most instances.
5. **Upgrade with real data.** On a device holding real notes, highlights and progress, confirm nothing is lost. Highest-risk untested path.
6. **Dark mode.** "· Heure Sainte" on Hours 5–7 in the Heures list must be readable.
7. Notes/highlights/progress survive a reopen; export–import round-trip; offline launch after first load.
8. General reading, search including the Réflexions filter, Hour 24 burial + Désolation structure.

## Known limits — not defects

- **Real-device QA is `NOT_TESTED`.** That is the remaining release blocker and the purpose of this build.
- **The update fix is verified on desktop Chrome only**, on a real HTTP origin with a genuine before/after reproduction. It is *not* yet verified on an installed iOS PWA, where storage partitioning differs. Stage 2 above is what closes that gap.
- **Deliberately deferred:** storage-full / storage-unavailable recovery, malformed or future-snapshot recovery, atomic R41 highlight-anchor reset, and honest "not saved" messaging across all mutation paths. If a save fails because storage is full, the app may still report success.
- **`stored_text_units = 4577`** is a hardcoded literal in the v101.44 build script and does not reconcile with an independent recount (4,574 / 4,579). Corpus integrity is unaffected — the declarations hash-match — but that figure is unverified.
- **One stray bare LF** at offset 959303 is pre-existing in the v101.44 baseline and carried forward unchanged. Outside all protected declarations.
- **Android Play Protect** "compatibility too low" on a browser-minted WebAPK: one unreproduced report, deprioritised.

## Verification completed

```text
Input binding (FP2 baseline)   PASS   both ZIPs exact on bytes + members + SHA-256
Package integrity              PASS   760/760 manifest records, 0 missing, 0 mismatch, 0 unaccounted
Protected declarations         PASS   6/6 byte-identical to the v101.44 contract (verified twice)
Replica parity                 PASS   app == deploy/luisa == deploy/index
Packaged suites                6/6    11/11, 6/6, 7/7, 29/29, 14/14, 4501-target map
Reopened-ZIP gate              PASS   CRC, no duplicates, no unsafe paths, 73/73 records
Live HTTP load                 PASS   0 console errors on a served origin
SW registration + activation   PASS   cache luisa-24h-v101-45
DOM target sweep               PASS   4501/4501, 0 missing, 0 page errors
Offline cold start             PASS   booted and rendered with the HTTP server stopped
Update flow (before)           FAIL   reproduced on v101.44 — pinned to old version
Update flow (after)            PASS   single Actualiser press landed on the successor
Real-device QA                 NOT_TESTED
```
