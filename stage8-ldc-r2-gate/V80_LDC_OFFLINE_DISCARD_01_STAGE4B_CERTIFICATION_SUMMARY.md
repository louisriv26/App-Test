# LDC v2.19.80-R1B — Stage 4B Prepared-Offline Retention Certification Summary

**Date:** 2026-09-10  
**Direct predecessor:** v2.19.79-R1B / `88f7e06831bc9cae4f69155abe8dabfe1f12a9b6b348e41648fe2b5fe4aa9930`  
**Owner authorization proposal:** `c2c20cb7051692ab0801171407448416052089573ee95b832483b805568b9c5b`  
**Protected Stage 4A authorization:** `ae14ae9bce3b5c1ab9075e0a3879c963ec16126fcde551333de70ad8943bbb3f`  
**Protected renderer:** `speech_model.js` `3bd067956a5275e0be7231add3b425c124fb17f3d0be548080eee10c649134f6`  
**Public deployment:** NOT AUTHORIZED BY THIS PACKAGE

## Bounded repair

Stage 4B decouples prepared offline corpus persistence from the shell app version. Shell and runtime caches remain versioned. Prepared corpus storage uses `ldc-offline-storage-v3` and a deterministic fingerprint of `self.registration.scope`; current content identity uses `ldc-offline-content-binding-v2` and excludes app version and physical cache name.

Legacy `ldc-le-livre-du-ciel-offline-v*` caches are preserved during activation. An existing response may be reused only for the current service-worker scope when its `x-ldc-verified-sha256` and `x-ldc-verified-bytes` markers exactly match the current manifest asset. The predecessor global binding remains provenance only and cannot reject an otherwise exact asset. Missing, changed or invalid current assets are downloaded into the stable scope-specific cache. No full-cache copy migration is required.

Offline reads search the stable cache first and eligible legacy versioned caches second, so exact unchanged assets remain usable immediately after an update even before manual Reprendre. Clear removes the current scope's persistent entries without deleting another scope's entries from shared legacy caches. The IndexedDB `offline_completion` setting records storage/content identity rather than an app-version cache name.

## Protected domains

The v79 Stage 4A transactional/concurrency functions are byte-preserved. No canonical/devotional text, paragraph IDs/order, renderer, speaker/display/flow authority, SEARCH-V2 payload/ranking semantics, supplement content, IndexedDB schema, historical migration algorithm, backup architecture, diagnostics/privacy, accessibility, CSP, typography or reading-UX change is authorized or introduced.

## External boundary

Machine/static/state-machine tests do not substitute for live installed-PWA upgrade, true offline cold reopen, physical iPhone/iPad/Samsung or accessibility gates. Those remain explicitly open.

## Engineering QA fixed points

- exact service-worker offline-retention suite: **17/17 PASS**;
- exact index offline-completion-state suite: **3/3 PASS**;
- scope/protected-domain verifier: **27/27 PASS**;
- independent second-path challenge: **42/42 PASS**;
- inherited Stage 4A transaction/staleness suites: **17/17 + 6/6 PASS**;
- deliberate Stage 4B bypass mutants: **4/4 caught**;
- inherited FAST fixed point: **2,996 affected records + 288/288 flow joins, zero errors**;
- managed Chromium localhost navigation: **ENVIRONMENT_BLOCKED (`ERR_BLOCKED_BY_ADMINISTRATOR`)**, neither app PASS nor FAIL.

## Residual risks carried forward

The four inherited regular-space-before-comma corpus artifacts remain unchanged and outside this authorization: `LDC.T28.E0023.P070`, `LDC.T34.E0040.P016`, `LDC.T36.E0036.P021`, `LDC.T36.E0046.P016`. Ten inherited v74 checkpoint source archives are not carried in this lineage. `CONC-LDC-MIGRATION-BYPASS-01` remains a separate skipped-version/migration concurrency promotion gate. None is claimed fixed by Stage 4B.
