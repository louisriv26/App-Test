# LDC 142.18 — R8 independent archive-order adjudication (2026-10-08)

**Scope:** Audit-only evidence. No application source mutation and no deployment authority.

## Directly reverified frozen package
- Archive: `LDC_v142.18_INTEGRATED_WIP_APP_DO_NOT_DEPLOY.zip`
- SHA-256: `954085cc54cbc401d49512811276b5c633c72b9f48e8963881792f176b20d7eb`
- Size: 125604084 bytes
- Manifest-declared application files: **273**, all 273 independently hashed and size-checked against actual ZIP bytes; CRC PASS.
- 204 corpus assets individually verified; offline corpus binding and all 20 qualified semantic asset digests verified.
- GitHub Actions outer downloadable ZIP contains byte-identical inner frozen application ZIP.
- R7 full documentary handover contains hash-indexed members with correct sizes/checksums; its `99_HANDOVER_MEMBER_SHA256.json` **is** the final member.

## Confirmed newly found packaging-process breach
- **FAIL: application ZIP's `PACKAGE_MANIFEST_SHA256.json` is the FIRST member (index 0), not the LAST (index 273).**
- The WIP builder `.github/ldc-v14218-curated-wip-package.py` has `for p in sorted(runtime|{"PACKAGE_MANIFEST_SHA256.json"}):` at approximately line 115. Sorting all paths lexicographically necessarily places uppercase `PACKAGE_` ahead of lowercase `assets/`, `corpus/`, etc.
- Existing `zip_members_exact` compares sets, not required order. Thus its historical **564/564 PASS** does not cover the manifest-last claim. The source/docs asserting the package was manifest-last are inaccurate.
- This is a **release-procedure/evidence defect**, not a demonstrated change in any extracted application file or observed browser malfunction.
- Independent current audit: **27/28 checks PASS; 1 procedural check FAIL**.
- Do **NOT** silently rewrite or replace the immutable 142.18 archive. A manifest-last corrected ZIP has different SHA-256 and is a new engineering package candidate under APP-GOV; requires distinct identity and separate mutation/release/deployment authorizations.
- Treat complete packaging-procedure closure as **OPEN/FAIL** until independently rebuilt, rehashed, verified for order, and requalified under appropriate authority.

## Remaining open gates
- Hosted distinct-origin App-Test E16/E19: OPEN.
- Real iPhone/iPad Safari/installed PWA, rotation, highlights, VoiceOver, updates, peak memory: OPEN.
- Semantic inference offline: not qualified; current offline text + explicit Par les mots / unavailable Par le sens user-facing test passed its narrower scope.
- Full public version promotion, App-Test deployment and production deployment: **NONE AUTHORIZED**.
- Local independent Chromium re-execution inside the ChatGPT container could not begin because navigation to localhost was blocked by the container administrator. Earlier real Chromium evidence was produced by GitHub Actions and is separately available; do not conflate them.

**R8 conclusion: NO-GO for package release/deployment. Audit documentation correction only; source app remains frozen.**
