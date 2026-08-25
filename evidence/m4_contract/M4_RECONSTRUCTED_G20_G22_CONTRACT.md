# RA19E.2 M4 reconstructed atomic contract — final immutable package lock

**Contract provenance: RECONSTRUCTED_2026-08-25_NOT_HISTORICALLY_RECOVERED**

The approved macro workflow defines M4 as `FINAL_IMMUTABLE_PACKAGE_LOCK = G20–G22`, but the exact historical G20–G22 names and prose were not recovered from the supplied continuation material, File Library, or historical RA19E.2 evidence. The following contract is therefore explicitly reconstructed from the project's governing final-package reopen, report-integrity, stale-reference and decision-lock rules. It must not be represented as recovered historical wording.

## G20 — FINAL_PACKAGE_BUILD_AND_INTERNAL_CONSISTENCY
PASS only if:
- the final package is built twice independently from the same frozen M3 candidate and both written ZIPs are byte-identical;
- the HTML replicas remain exactly the M3-tested bytes;
- APP_VERSION, `manifest.json`, `version.json`, service-worker cache generation, README and release metadata are consistent with v101.111;
- JavaScript and service-worker syntax checks pass;
- package/hash manifests match the final pre-ZIP tree;
- root `index.html` and `luisa_24_heures.html` are byte-identical;
- the root GitHub Pages artifact is explicitly documented as the deploy artifact; separate deploy directory is N/A;
- no nested ZIP exists unless explicitly declared and audited;
- recursive stale-reference scan across runtime, reports, scripts, metadata and evidence has zero unjustified stale references;
- active report claims are supported by direct evidence.

## G21 — FINAL_ZIP_REOPEN_AND_INDEPENDENT_REOPEN_AUDIT
PASS only if:
- the exact final ZIP written to disk is freshly extracted into a new audit directory;
- CRC, safe paths and duplicate-path checks pass;
- all G20 package consistency and manifests are rerun against reopened bytes;
- M2 semantic/presentation invariants are rerun against reopened HTML;
- M3 runtime presentation matrix is rerun against reopened HTML in Chromium, with environmental limitations explicitly retained;
- a separately implemented independent auditor performs a second fresh extraction and independently verifies package identity, manifests, runtime invariants and report integrity;
- both reopened audits produce PASS for the scoped static/runtime package.

## G22 — FINAL_DECISION_LOCK_AND_REPORT_INTEGRITY
PASS only if:
- the external final decision lock is written only after G21 passes;
- it binds the exact final ZIP name, size and SHA-256;
- it cannot contradict the final reopened-ZIP result;
- no report treats URL navigation, real service-worker registration, offline lifecycle, installed PWA, live GitHub Pages, screen-reader or physical-device testing as passed when those were not executed;
- the scoped RA19E.2 evidence status and broader release-readiness status are distinguished.

## Final status semantics
- M4 macro gate may PASS when G20–G22 all pass for the scoped speaker/presentation package.
- Overall public/device release status remains `LIMITED_PASS_STATIC` while physical devices, live origin/service-worker/offline and representative screen-reader tests remain unexecuted.
