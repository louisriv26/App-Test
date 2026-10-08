# LDC v142.18 — R8 adversarial packaging-order clarification (8 October 2026)

**Scope: independent audit/documentation, no app change, no deployment. This revision explicitly supersedes the first R8 draft's unsupported manifest-last ZIP-order FAIL.**

## Precise independently reverified bytes

- Application ZIP: `LDC_v142.18_INTEGRATED_WIP_APP_DO_NOT_DEPLOY.zip`
- Exact SHA-256: `954085cc54cbc401d49512811276b5c633c72b9f48e8963881792f176b20d7eb`, size **125,604,084 bytes**.
- 273 application resources plus `PACKAGE_MANIFEST_SHA256.json`. All 273 application files match the embedded manifest's SHA-256 and exact byte lengths; ZIP CRC PASS.
- All 204 offline-corpus assets and 20 semantic-qualified pack assets match their expected exact digests; canonical corpus binding recomputed.
- GitHub Actions downloaded outer artifact includes precisely the same frozen inner app ZIP.
- Full R7 documentary handover is separately complete and has its own `99_HANDOVER_MEMBER_SHA256.json` as last entry with verified member digests.

## ZIP member-order observation: not a proven defect

The application ZIP does have `PACKAGE_MANIFEST_SHA256.json` as its **first** entry (index 0/274). But the pinned authoritative builder at source commit `7c292d6221bb350fac3aeaa83750b8784706d45c` works in this sequence:

1. Copy **all application resources to staging**, capture each file's SHA-256 and length;
2. **Generate and write the package manifest after those application-file hashes are known**;
3. Write the archive members in a deterministic sorted order. This lexicographically puts the uppercase `PACKAGE_` file ahead of lowercase app paths;
4. Reopen the archive, validate members, extract all bytes and independently rehash every declared resource.

Thus the prior description **“manifest generated last” is correct regarding manifest generation order**. No available governing requirement has been established demanding that the manifest be the final **ZIP member**. The initial R8 tool mistakenly conflated these two meanings and created a non-authoritative `manifest_last_REQUIRED_REPRODUCIBILITY` assertion.

**Correct adjudication:** 27/27 applicable independent archive/content/handover checks PASS; ZIP member order is an informational observation, **not an extra release failure**. The initial R8 27/28 FAIL report is retained as a methodology correction, **not a current release result**. No successor repackaging is needed merely to reorder entries; altering the frozen ZIP without authority would be counterproductive.

## Still-open actual release blockers

- E16/E19: same-origin hosted App-Test vs production and root/sibling Service Worker isolation remain **OPEN**; two localhost-port origins test architecture, not hosted closure.
- Real physical iPhone and iPad Safari, installed PWA, update/offline, VoiceOver, highlights/orientation, older-device peak memory remain **OPEN**. Linux WebKit and Chromium viewports are not physical devices.
- Semantic model inference offline is **not qualified**, while narrower offline 204 text/lexical search and truthful unavailable-semantic UX did pass local R7D2 tests.
- Various source-text/documentary validation gates must not be silently deemed complete solely from byte fidelity.
- App-Test deployment and production deployment authority remain **NONE**. Frozen v142.18 mutation authority remains **NONE**.

**Final decision: complete applicable archive-byte integrity audit PASS, local browser evidence scoped PASS, release/deployment NO-GO solely because existing hosted/physical/authority gates remain open—not because of archive ordering.**
