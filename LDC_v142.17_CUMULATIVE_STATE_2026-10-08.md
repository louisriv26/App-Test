# LDC — Cumulative governing state, v142.17 (2026-10-08)

## 0. Authority and non-negotiable controls (APP-GOV-1.0)
Public identity **142.17** (format N or N.M); technical build identity `v2.19.142.17-R1B-READER-TRANSACTION-REPAIR`. No public Rxx version. Corpus and protected surfaces cannot be altered without explicit new mutation authority. Historical PASS labels are not current evidence. Source mutation, App-Test deployment and production deployment are **three distinct authorities**. The owner authorized the narrowly scoped v142.17 source correction, **not** App-Test or production deployment.

- GitHub repository: `louisriv26/App-Test`.
- Successor branch: `ldc-v142.17-reader-transaction-repair-candidate`.
- Frozen reference from v142.16: runtime commit `15fb524cc8929c04d2e92f560374cdbe5404148c`; evidence-complete branch head `d1970a527bf94325c78c2c396adf4987d9001a3e`.
- **Current v142.17 exact runtime candidate commit:** `87000d27a1ebeef3b18e185d21462088dd32e8c1`. Evidence/docs/manifest updates after this commit must not change its four runtime blobs. Treat this as the runtime freeze for source/hosted qualification; a later material runtime-byte mutation requires a new governed candidate.
- Current state: **SOURCE REGRESSION TESTS PASS; MANIFEST/ZIP/HOSTED/PHYSICAL GATES SEPARATE**. No approval to deploy to App-Test. No production authorization.

## 1. Verified exact runtime identities (SHA-256 over UTF-8 bytes)
| File | Bytes | SHA-256 |
|:--|--:|:--|
| `index.html` | 935145 | `9613ec288a6eb35b8f976bd55053bad8fce3c7c018106354cf415f70301ca7ce` |
| `sw.js` | 32270 | `b9cfd936d7ecaa5276052766bbb229de68974d3bbe5f96d4f2427f7e786cd252` |
| `version.json` | 257768 | `39bdba39c21cb93e890fdd01cd33bc792449991cd8cd52bb8358557b81ad9be2` |
| `offline_manifest.json` | 59964 | `dcf1c0e1c04a3b2a06de5ca85ccc6bd5525a2b62b6c0e7398051b0fb37a5a18f` |

All four are on the candidate branch at the runtime-freeze commit. The existing generic package manifest remains an **old v142.16 manifest** until regenerated as the final step. A manifest SHA-256 is **not** a ZIP SHA-256, and no v142.17 deploy ZIP has yet been adjudicated.

## 2. Historical exact lineage and status
### v142.10 — production reference recorded previously
Public `142.10`, Git commit `a914ba9267ba18717101f5d9e783fe164073f8a6`, package hash `c5ef73e6738ef8e2b586dfeb5ff44d4569860d023706e704e940fd365692a460`, Pages deployment run `37501594691`. These are *inherited records* and are not a new live-production verification in this cycle. The Par le sens Dense96/72+BM25 96/72 RRF60 runtime belongs to this protected lineage.
### v142.14 — earlier inherited QA baseline
Its build, runtime, evidence reconciliation and staleness reports are historical evidence, not transferable current PASS labels.
### v142.15 — rejected physical predecessor
Exact Git commit `572d9df7927765b575a76eaee98fd3cc9d455e74`; old package SHA-256 `cca03c4a6e07cd7f25b4a6a8cc6caadaf912ede76354a0b71236c93d2dd728bc`; manifest SHA-256 `4b01800e94b2c1809a75c2b9cfae920867344ac74d61cf17b9d85af558eac956`. Claude Code established a prior 309/309 App-Test hosted binding and supplementary Chrome offline/update/resume/highlight/documentary tests. Real iPhone user then found two Reader regressions, so physical adjudication was **REJECTED**: opening Mon Espace highlight could shift the entire document (huge gap), and portrait→landscape could compress the Reader text pane almost to zero. Device/VoiceOver gates in the Claude Code report were NOT FULLY TESTABLE; desktop Chrome cannot close them.
### v142.16 — frozen first repair, superseded as target
Exact frozen runtime commit `15fb524cc8929c04d2e92f560374cdbe5404148c`, evidence head `d1970a527bf94325c78c2c396adf4987d9001a3e`, final v142.16 manifest SHA-256 `85e86a22f4d464fc318985634e4ce917e64527e9d620fb55b68d4b8239378d82` (312 entries excluding manifest). Files/hashes: index `c1b6af56b25d5d7ee419d765f76c2c73d374730578915cd0f4e209a1b0b531c3`; sw `1c0b9168c72bfbd514838041963101a59f0487335fa79269a4713ceb65a6309d`; version `4cbccfcad4b3306b4a3ad700d9f92c108071a11da1adf3a5212bcf4e214a42c4`; offline manifest `35721f05cc13d6b85abca309206e50d85d480cc10d0b2fdec0690130043f51a6`. Added internal #reader-scroll paragraph targeting, measurement-driven low-height mode, debounced rotation semantic restoration. Initial 28/28 machine and 19/19 challenge claims were subsequently **qualified by new reproducible race findings**.
### v142.17 — current bounded successor
Source changes: four runtime files `index.html`, `sw.js`, `version.json`, `offline_manifest.json`; other prior baseline package files Git blob-identical. Fixes shared global scroll boolean race and stale callbacks after leaving Reader via epoch ownership, reader session / entry / supplement / source identity, explicit invalidation on Reader exit or committed next-entry, descendant-only scroller targeting. Initial v142.17 worker/manifest mismatch was corrected on this branch, not on main.

## 3. Known defects, root causes, closures and non-closures
**A. v142.15 Mon Espace → Surlignage root scroll:** root cause generic `pendingParaId` path used `scrollIntoView()` which can move root ancestors. v142.16 switched to internal-reader-only placement. Device proof: **OPEN**.

**B. v142.15 short Safari landscape blank Reader:** fixed chrome plus bottom navigation consumed vertical height; flex Reader scroll pane shrank. v142.16 introduced measurement-driven compact Reader, hides global tabs only when height deficient, preserves Reader Back/previous/read/next and safe area, applies hysteresis, restores semantic position after layout. iPhone Safari physical proof: **OPEN**.

**C. v142.16 stale scroll-suppression race (P1):** transaction A stale RAF could set global `semanticRestoreInProgress=false` while B active, making B correction appear as user scrolling. v142.17 introduced single-owner epoch and owner-qualified completion across target, entry-start lock and semantic restoration. Source-extracted deterministic regression: **PASS**; live app: OPEN.

**D. v142.16 stale callback on exit (P1):** identity snapshot only bound volume/entry, so callback could root-reset after screen exit or reader session replacement. v142.17 now binds visible screen, active session, source mode, supplement and entry; invalidates pending transactions on screen exit and committed entry. Source-extracted regression: **PASS**; browser/integration/device: OPEN.

**Remaining risks:** Safari low viewport with `Très grand` text and status bar; fixed selection tools/toast/colour picker/update banner overlap; VoiceOver focus when global nav hides/returns; PWA safe-area behavior; long-entry Resume/entry-start locks; cross-navigation and rapid user scrolling. Do not report these as passed.

## 4. Protected source, corpus, search, provenance and user data
Git compare v142.16→v142.17 shows *only* four runtime files changed, plus evidence/doc files. In the predecessor's 312-file package ledger, **308** have the identical Git blob ID, all baseline paths remain, and the only four changed entries are the approved runtime file universe. Corpus JSON, search payload/index/ranking (Par les mots and Par le sens), provenance payload/documentary wording, IndexedDB user-data schema, backups and offline asset bytes are protected. Offline content binding remains `1fb8d6d8a532806ad6a25b32250091deed174ddb54130f1b05d3da2233a05384`; offline manifest retains 204 assets.

## 5. Current reproducible QA and evidence limits
- v142.17 actual index inline JavaScript: **syntax PASS**.
- v142.17 actual service worker JavaScript: **syntax PASS**.
- Four-way v142.17 identity and worker offline-manifest compatibility: **PASS**.
- v142.17 extracted-function controlled event-loop regressions: **14/14 PASS** plus **6/6 supplementary PASS**; these are machine simulations of exact current source, not Safari integration.
- Protection delta and baseline byte identity: **PASS for Git blob invariance**.
- Initial static false positive for word `orientation` occurred in a comment, not executable code; adjudicated.
- Full hosted browser execution, App-Test exact byte binding, offline PWA upgrade, iPhone/iPad, VoiceOver and user acceptance: **OPEN**.
- No new deployment ZIP/package digest yet; do not infer one from a source commit or manifest.

## 6. Evidence hierarchy, promotion and authority
1. Exact current source blobs, SHA-256, Git commit and current package manifest once created.
2. Fresh v142.17 machine/source regression evidence and adversarial source challenge.
3. Fresh browser run on exact hosted v142.17 package and byte binding.
4. Fresh device evidence on actual iPhone/iPad and installed PWA/VoiceOver.
5. Earlier v142.16/v142.15 reports as historical claims only.

**Runtime mutation authority:** NONE after declared v142.17 freeze at `87000d27...`. Reopen only on demonstrated defect with new successor candidate/version. **App-Test deployment authority:** NONE. **Production deployment authority:** NONE. Deployment must never silently update `main` or any protected surface. Exact live-tested bytes must be promoted without rebuilding. A source-only PASS is not a release PASS.

## 7. Remaining mandatory gates / next authorized decision
Finish the last v142.17 evidence/manifest ledger; verify its exact entries and hashes. A ZIP if independently assembled must receive its own SHA-256. For App-Test, obtain explicit owner authorization and bind every served runtime asset to the candidate. Then browser smoke and the focused physical protocol `LDC_v142.17_PHYSICAL_RETEST_PROTOCOL_2026-10-08.md`: iPhone Mon Espace paragraph target, iPhone portrait→landscape×5 with browser chrome, iPad, installed PWA, VoiceOver, Resume and Search. Any FAIL blocks promotion and requires governed successor bytes.

**Current decision: source correction promising; NO App-Test or production authority; no physical claim.**
