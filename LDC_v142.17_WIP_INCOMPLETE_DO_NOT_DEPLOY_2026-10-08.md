# LDC 142.17 — WIP. DO NOT DEPLOY.

Date: 2026-10-08. APP-GOV-1.0.

The owner authorized a **bounded v142.17 successor implementation** after independent verification of two v142.16 asynchronous Reader defects. This branch is **not frozen, not a deployable package, and not App-Test/production authorized**.

- v142.16 exact runtime baseline: `15fb524cc8929c04d2e92f560374cdbe5404148c`
- v142.16 evidence-complete branch head: `d1970a527bf94325c78c2c396adf4987d9001a3e`
- v142.17 source/metadata changes committed: `index.html`, `version.json`, `offline_manifest.json`.
- **Hard blocker:** `sw.js` still declares v142.16 release identity. An authorized full-file write was blocked by tool safety checks; the worker was not updated.
- **Hard blocker:** `PACKAGE_MANIFEST_SHA256.json` is still the old v142.16 manifest, so the v142.17 WIP branch cannot pass package integrity.
- **Human/browser gates:** none closed. Deterministic function-level checks passed on extracted code; this is not an iOS Safari certification.
- **Protected:** corpus, Par les mots, Par le sens, provenance, offline assets/content binding and user-data schema unchanged.

Next: finish coherent service worker identity via approved local editing, run full machine/browser QA, independent challenge, hash all actual files, regenerate the manifest LAST, update the actual cumulative state, and seek distinct owner authorization before any App-Test deployment. Production remains blocked.

The existing v142.16 QA reports are historical evidence and must not be relabelled as v142.17 PASS.
