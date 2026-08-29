# Livre du Ciel — v2.19.60-R1B / Public 60 — M13 supplement provenance validator repair

**Current candidate:** v2.19.60-R1B · Public version 60 · build date 2026-08-29.

**Baseline:** exact locked v59 deploy SHA-256 `703cb893a5fb3a558569bdd5cbb53c678a5b0d5767d17e66cd36b9a6103c5c9e`.

**Current corpus architecture:** ALIGNÉ `G036-AFLP-R3-UWR2` = 2,312 entries / 74,348 paragraphs; COMPLÉMENT = 74 items / 176 paragraphs / 142 speaker segments; ENRICHI `G036-AFLP-R3-SUP-T4` = 2,325 entries / 74,524 paragraphs.

**M13 runtime repair:** the live v59 diagnostic proved that CORPUS_INIT rejected the sole SUP-T3 item because the loader incorrectly required `decision_id` and `source_evidence_ids` on every supplement. Those fields belong to the SUP-T1/SUP-T2/SUP-T4 provenance model and were never part of the M6 SUP-T3 record. v60 validates SUP-T3 against its genuine M6 evidence (`M2-0270`/`M2-0282`, IT-PM primary source/span hashes, reciprocal IT-DV placement hashes, translation hash/confidence and provenance contract) while retaining the existing common contract for the other 73 items. No corpus wording or supplement record is changed.

**Protected:** all corpus text, paragraph IDs/order, supplement payloads, search/speaker/display/flow data, user-data schema v4, `ldc-reading-position-v3`, protected Ma lecture suivie state machine, and the M12 atomic bootstrap/service-worker architecture.

**External status:** live v59 CORPUS_INIT failed; v60 requires a fresh live deployment/retest. Wide/public release is not authorized.

> Everything below this line is the byte-preserved v59 README and inherited historical documentation. Older “current”/PASS/count/version wording below is historical only.

---

# Livre du Ciel — v2.19.59-R1B / Public 59 — M12 atomic bootstrap successor

**Current candidate:** v2.19.59-R1B · Public version 59 · build date 2026-08-28.

**Baseline:** exact locked v55 deploy SHA-256 `a7ac741f28b243c86c7c58d21ea5ae24120cd45a287ae8384fddc2df0bd76dc4`.

**M9 authorised scope:** exactly 6 R3 fidelity cases / 10 existing paragraphs plus 15 SUP-T4 cases / 22 internal complement fragments, as locked by M8. No other corpus mutation is authorised.

**Current corpus architecture:** ALIGNÉ `G036-AFLP-R3-UWR2` = 2,312 entries / 74,348 paragraphs; COMPLÉMENT = 74 items / 176 paragraphs / 142 speaker segments; ENRICHI `G036-AFLP-R3-SUP-T4` = 2,325 entries / 74,524 paragraphs.

**Protected:** existing paragraph IDs/order, user-data schema v4, `ldc-reading-position-v3`, Ma lecture suivie SEQUENTIAL/CONSULTATION model, Lu independence, inherited SUP-T1/SUP-T2/SUP-T3 payloads/placements, and excluded/held M8 cases.

**External status:** real browser/physical/PWA/accessibility validation remains successor-specific and is not inherited from v54/v55.

> Everything below this line is the byte-preserved v55 README and inherited historical release documentation. Older “current”/PASS/count/version wording below is historical only.

---

# Livre du Ciel — v2.19.55-R1B / Public 55 — M6 bounded corpus-metadata successor

**Current candidate:** v2.19.55-R1B · Public version 55 · build date 2026-08-28.

**Baseline:** exact locked v54 deploy SHA-256 `c860ee3c1f722135a84abdd66d5f0b9bea2ca611fd6b3a1cb7121cc83f66e0fc`.

**M6 authorised scope:** exactly the six M5/G17 bounded candidates: three AFLP display-date restorations; one COMPLÉMENT-only SUP-T3 recovery of the historically bound T15/T16 “three columns” discourse at 2 December 1922; M2-0105 identifier/provenance reconciliation with legacy alias; M2-0113 post-R2 anchor-authority reconciliation.

**Current corpus architecture:** ALIGNÉ `G036-AFLP-R2-UWR2` = 2,312 entries / 74,348 paragraphs; COMPLÉMENT = 59 items / 154 paragraphs / 120 speaker segments; ENRICHI `G036-AFLP-R2-SUP-T3` = 2,325 entries / 74,502 paragraphs.

**Protected:** ALIGNÉ paragraph wording/IDs/order, R2 speaker layer, display/flow topology, all inherited SUP-T1/SUP-T2 textual payloads/placements, user-data schema v4, `ldc-reading-position-v3`, protected Ma lecture suivie state machine, notes/highlights/favourites/Lu and Collection Luisa contracts.

**Physical/browser authority:** not promoted by this package. Real browser IndexedDB and physical Samsung/iPhone/iPad/PWA/offline/accessibility tests remain external gates.

> Everything below this line is the byte-preserved v54 README and its inherited historical release documentation. Any older “current”, PASS, release, count, generation, or next-stage wording below is historical only and is not current v55 authority.

---

# Livre du Ciel — v2.19.54-R1B / Public 54 — Protected Ma lecture suivie successor

**Current candidate:** v2.19.54-R1B · Public version 54 · build date 2026-08-27.

**Baseline:** immutable locked v2.19.53-R1B ZIP SHA-256 `8eb546ceb9c8bc9d778c2c4d3912be1736d523dd94d427ade713a20f2cdb28d7`.

**v54 functional scope:** protected `Ma lecture suivie` state machine only: explicit SEQUENTIAL/CONSULTATION reader intent, session-scoped immutable position snapshots, ordered/atomic persistence, stale-callback rejection, navigation flush/invalidation, immediate sequential persistence, lifecycle safety flushes, journey source-mode binding, v2→v3 reading-position migration/confirmation, explicit confirmed/undoable relocation, minimal journey/consultation UX, and backup/import compatibility.

**Protected content:** canonical corpus/search/speaker/display/flow/SUP-T1/SUP-T2 content, paragraph IDs/order, notes semantics, highlight anchoring semantics, favourites semantics, Lu semantics, and Collection Luisa architecture are not intentionally changed.

**Release status inside package:** candidate bytes only; no final PASS claim. Final authority requires deterministic Build A/B, primary and independent reopened-ZIP audits, executable state-machine evidence, report/stale-reference reconciliation, reopened evidence ZIP, and final decision lock written last. Physical Samsung/iPhone/iPad/PWA/offline/VoiceOver/TalkBack gates remain external.

> Everything below this line is historical predecessor documentation. Any older wording such as “current”, “governing”, “PASS”, “next stage” or release instruction applies only to its historical version and is superseded by the current v54 authority section above.

---

# Historical predecessor — Livre du Ciel v2.19.53-R1B / Public 53 — package-binding & current-metadata reconciliation successor

**Historical v53 status:** locked `LIMITED_PASS`; package/binding consistency repaired. Superseded as the functional baseline by v54.

# Livre du Ciel — v2.19.53-R1B / Public 53 — package-binding & current-metadata reconciliation successor

**Current candidate:** v2.19.53-R1B · Public version 53 · build date 2026-08-27.

**Baseline:** immutable failed-evidence v2.19.52-R1B ZIP SHA-256 `c49da37d61e83164071fad4f8596233aac479dfe74ea07b05b687beb56d27025`.

**v53 repair scope:** release/package metadata and binding consistency only. No intentional change to corpus wording, paragraph IDs/order, search text/IDs, speaker data/offsets, display/flow/SUP payloads, user-data restore logic, reading-position runtime logic, highlights, notes, favourites, Lu semantics, or Collection Luisa architecture.

**Release status inside package:** candidate bytes only; no final PASS claim. Final authority requires deterministic Build A/B, reopened-ZIP audit, separately implemented independent reopen, report/evidence reconciliation, reopened evidence ZIP, and decision lock written last. Physical Samsung/iPhone/iPad/PWA/offline/VoiceOver/TalkBack gates remain external.

> Everything below this line is historical predecessor documentation. Any older wording such as “current”, “governing”, “PASS”, “next stage” or release instruction applies only to its historical version and is superseded by the current v53 authority section above.

---

# Historical immediate predecessor — Livre du Ciel v2.19.52-R1B / Public 52 — user-data restore compatibility + active binding repair successor

**Historical status:** frozen failed evidence. Deep reconciliation found active `version.json` binding contradictions; v52 must not be deployed.

**Historical v52 scope:** backward-compatible restore of older valid user-data backups, safe multi-paragraph highlight re-anchoring, fail-closed preservation of unresolved anchors, restore rollback protection, and attempted current binding reconciliation. Canonical corpus/search/speaker/display/flow/SUP payloads were preserved.

---

# Historical predecessor — Livre du Ciel v2.19.51-R1B / Public 51 — final four-pass metadata-binding reconciliation successor

**Current candidate:** v2.19.51-R1B · Public version 51 · build date 2026-08-26.

**Current corpus architecture**

- ALIGNÉ: `G036-AFLP-R2-UWR2` — 2,312 entries / 74,348 paragraphs.
- COMPLÉMENT: 58 active supplement items — 14 historical SUP-T1 + 44 M3-authorised SUP-T2; 149 paragraphs total.
- ENRICHI: `G036-AFLP-R2-SUP-T2` — 2,324 entries / 74,497 paragraphs.
- Active supplement speakers: 117 segments; total backbone + supplement speaker segments: 65,129.
- User-data schema: v4. Eight corrected ALIGNÉ paragraphs retain stable IDs; exact selections migrate only by exact/context/unique-normalized evidence, otherwise remain preserved as stale/unresolved.
- Within-paragraph complements use display slicing while preserving the unsplit canonical ALIGNÉ paragraph identity and offsets.
- Historical `G036-AFLP-R1B-UWR2` and the original 14-item SUP-T1 layer remain immutable evidence snapshots.

**v51 metadata-binding repair:** canonical corpus wording, paragraph IDs, search, speaker, display, flow, SUP-T1/SUP-T2 content and user-state migration data are unchanged from locked v50. This successor corrects the final stale active binding found by Pass 4 (`corpus/manifest.json → reader_architecture.version`) and rebinds version/cache/offline metadata.

**Evidence status:** all package/report evidence must be regenerated from v51 bytes. No public release PASS is claimed until the frozen v51 ZIP is reopened from disk and independently audited. Physical iPhone/iPad/Samsung/PWA/accessibility tests remain external unless explicitly recorded in the final decision.

## Historical release lineage below — non-governing

The following inherited sections document superseded versions and historical audit stages. Version/count/PASS statements below are historical unless explicitly marked current.

# Livre du Ciel — Version 47 / report-integrity & release-metadata reconciliation

- Public version: **47**. Technical identifier: **v2.19.47-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-V47-REPORT-INTEGRITY-METADATA-RECONCILIATION**. Build date: **2026-08-25**.
- Immutable immediate baseline: Version 46 SHA-256 `0e7a9c1eed2d104d7c6d9ce316126dccf68cea4adf4936e0325d3c8e1e627831`.
- Trigger: the post-freeze deep four-pass re-audit found two evidence/release-metadata integrity defects in frozen Version 46: `version.json.package_state_at_freeze` still described V45 as the current freeze candidate, and `V46_FOUR_PASS_REAUDIT.json` encoded `failures=true` / `blocking_current_contradictions=true` while its Markdown and decision lock claimed zero failures/contradictions.
- Version 46 is therefore **FAIL_REPORT_INTEGRITY / SUPERSEDED** as a release authority. Its Help/onboarding content remains valid and is inherited byte-for-byte in Version 47.
- V47 substantive change: current release metadata/report-integrity reconciliation only. Canonical text, Help/onboarding wording, paragraph/search/speaker/flow/display/supplement payloads, `speech_model.js`, search logic, user-state schemas, highlighting/storage/navigation logic and service-worker algorithm are unchanged.
- Corpus manifest SHA-256: `1d61468afb5fc5e0a52d71113b8d9bdb1b3e9468e09caf11f9a998c901edb43c`; cache epoch: `cm-1d61468afb5fc5e0`; offline binding: `e617677684cbb8316a860e1f49500c788db99d1242f37ca590895ba6419f6541`.
- **Package state at freeze:** candidate bytes only. Post-freeze audits and decision lock are external evidence.
- Version 47 external validation has not started. Version 45 E1/E2 evidence does **not** transfer to V47. Begin with V47 E1, then E2, then E3–E11.
- Wide public release is not authorized.

> Everything below this line is historical predecessor documentation. Any older wording such as “current”, “governing”, “PASS”, “next stage” or release instruction applies only to its historical version and is superseded by the current v51 authority section at the top of this README.

---

# Livre du Ciel — Version 46 / Help & onboarding trust/comprehension successor

- Public version: **46**. Technical identifier: **v2.19.46-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-V46-HELP-ONBOARDING-TRUST-COMPREHENSION**. Build date: **2026-08-25**.
- Immutable immediate baseline: Version 45 SHA-256 `65220058924d3fe1823e3d7fe5f1dcee2010fa5a4270a725b0de8ea2c679b4bc`.
- Substantive scope: Help information architecture, semantic Help headings, plain-language explanations, trust boundaries, copy/share/support clarification, local-data no-sync explanation, update-banner guidance, and narrower onboarding wording.
- Protected and byte-unchanged from Version 45: canonical paragraph/search/speaker/flow/display/supplement payloads, `speech_model.js`, user-data schemas, highlighting/storage logic, navigation logic and service-worker runtime algorithm.
- Corpus manifest SHA-256: `f649b3ebd0c231ddce02202f84d40a4ecafc7dde4bab9d59ad2ea05a9f574e66`; cache epoch: `cm-f649b3ebd0c231dd`; offline binding: `f8ff9ac1bbcf5f0abe7e30b5dfe6c06b44989339b3a6ca8f10d0d5e39bff81de`.
- **Package state at freeze:** candidate bytes only. Reopened-ZIP audits and decision lock are external evidence written after freeze.
- Version 45 E1/E2 evidence is historical for Version 45 bytes and does **not** transfer to Version 46. Version 46 external validation must restart at E1 controlled origin, then E2 exact served-byte binding, before E3–E11.
- Wide public release is not authorized by this package.

> Version 45 below remains the immutable mixed-entry runtime-hardening and external E1/E2 historical authority.

---

# Livre du Ciel — Version 45 / mixed-entry explicit-parent runtime hardening

- Public version: **45**. Technical identifier: **v2.19.45-R1B**.
- Immutable immediate baseline: Version 44 SHA-256 `8e1e58899750a42a0d32caa7570f631e36ab70996b148b4d4df289677c3e84ae`.
- Substantive change: `speech_model.js` now computes legacy context once, then overlays every valid explicit `presentation_parent` per segment. Parentless supplement segments alone depend on fallback.
- The 52 supplement speaker records remain parentless by design; no `presentation_parent` is invented for them.
- The locked V44 B-v7.11 speaker data, presentation counts, canonical text, search, flow, display and paragraph geometry are byte-identical.
- Mixed-entry fallback usage is exposed through resolver counts/ledger.
- Corpus manifest SHA-256: `b66766990e5c5ab3877eb34f960769c4f9b58a12ea716d6e2fb3dfb4b64995b9`; cache epoch: `cm-b66766990e5c5ab3`; offline binding: `0fc9ce5a20c142566661c2cb6764710a46c592ce3c9f5360d93589f65eabe71e`.
- **Package state at freeze:** candidate bytes only. No post-freeze PASS is claimed inside this deploy package.
- External physical-device/PWA validation remains not authorized at this stage.

> Version 44 below remains the immutable B-v7.11 data authority.

---

# Livre du Ciel — Version 44 / B-v7.11 Luisa-reset presentation-parent reconciliation

- Public version: **44**. Technical identifier: **v2.19.44-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-V44-BV7_11-LUISA-RESET-PRESENTATION-PARENT-RECONCILIATION**. Build date: **2026-08-25**.
- Immutable immediate baseline: Version 43 SHA-256 `8c416449a5754fa683029f1015a845bb9e12f91316809ba4df91de726ca438dc`.
- Evidence authority: exact 17-row `LUISA / depth-0 / JESUS-parent` challenge closed at **8 KEEP / 9 RESET / 0 REVIEW_BLOCKING**.
- Data mutation only: exactly nine `presentation_parent` values change from `JESUS` to `LUISA`, with provenance `RA19E1_BV7_11_LUISA_RESET_EVIDENCE_FIXED_POINT`. Semantic speaker, offsets/geometry, canonical text, paragraph IDs/order, RA19B flow, search, display, supplements and user-state schemas are unchanged.
- Presentation counts: **JESUS 59,972 / LUISA 4,831 / MARY 209 = 65,012**.
- Final governing seed fixture: **39/39** controls, using the explicitly corrected Seed #22 expectation (`Comme Je suis fatigué.` → JESUS).
- Corpus manifest SHA-256: `3ee2dc93278c195e4a6d15449c6474682c6bbf3bd36d09733cd59ce327551794`; cache epoch: `cm-3ee2dc93278c195e`. Offline binding: `01dc1fbbaaa9273f8bc63558f7cc1572cdc68c283876f362b881cb7a65ed72ae`.
- **Package state at freeze:** candidate bytes only. Primary reopened-ZIP, separately implemented independent reopened-ZIP, adversary/runtime checks, stale/report-integrity audit and final decision lock are external authorities written after freeze. No post-freeze PASS is claimed inside this deploy package.
- External physical-device/PWA validation remains **not authorized** at this stage.

> Version 43 below remains the immutable V42-A scroll-containment baseline and historical evidence.

---

# Livre du Ciel — Version 43 / Stage C.1A scroll containing-block closure

- Public version: **43**. Technical identifier: **v2.19.43-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-V43-STAGE-C1A-DESKTOP-SCROLL-CONTAINING-BLOCK-CLOSURE**. Build date: **2026-08-25**.
- Immutable immediate baseline: Version 42 SHA-256 `c1cc7996119d1d76bb744c21c270104b1bd19cbedf018e488db07849c97a3d55`.
- Trigger: the independent V42 re-audit measured residual document-level scrolling on Aide. The cause was the visually hidden, absolutely positioned `#offline-at-status` whose containing block could escape the intended clipped flex shell.
- Substantive fix only: add `position:relative` to the existing `#main-content` containment rule. Existing flex sizing, screen-level `.scroll` rules, AT live-region semantics, speaker attribution, highlight anchoring, search logic, F1/F3 runtime-cache logic and F8 Android targeting are not changed.
- Protected: canonical corpus, paragraph IDs/order, A17 semantic speakers, B-v7.10 presentation parents, RA19B flow, all search/speaker/display/flow payloads, user-state schemas and all runtime algorithms outside mechanically required release/cache bindings.
- Corpus manifest SHA-256: `c88095cef0e8d3dce43d9c0103c69ae889003edd2193dc3f241cb6465f4b3420`; corpus cache epoch: `cm-c88095cef0e8d3dc`.
- Offline content binding SHA-256: `ae67d24d63fe4a002a7563e2ef5cd527c8cb33ab8ef8aedb979b417183521635`; assets: **224**; bytes: **191941037**.
- **Package state at freeze:** candidate bytes only. Primary reopened-ZIP, separately implemented independent reopened-ZIP, runtime browser evidence, stale/report-integrity audit and final decision lock are external authorities written after freeze. No post-freeze PASS is claimed inside this deploy package.
- External physical-device/PWA validation remains **not authorized** at this stage.

> Version 42 below remains the immutable Stage C.1 baseline and historical evidence.

---

# Livre du Ciel — Version 42 / Stage C.1 desktop scroll containment

- Public version: **42**. Technical identifier: **v2.19.42-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-V42-STAGE-C1-DESKTOP-SCROLL-FLEX-CONTAINMENT**. Build date: **2026-08-25**.
- Immutable immediate baseline: Version 41 SHA-256 `aa3f5d3bb848847ba1b2d01f77ed2d1bf84c9e56fca3dd739cc1608ef7b12929`.
- Trigger: external desktop feedback reported that the reader and Bibliothèque/Tome list could no longer scroll, while iPhone/iPad scrolling remained functional.
- Root cause: the Stage A semantic `<main id="main-content">` wrapper inserted an extra element between the flex-column body and `.screen`, but the wrapper itself had no flex/`min-height:0` containment. Desktop `.scroll` children therefore lost a bounded viewport while `body` remained `overflow:hidden`.
- Fix: restore the missing shell contract on `#main-content` only: `display:flex; flex:1 1 auto; min-height:0; min-width:0; flex-direction:column; overflow:hidden; width:100%`. Existing `.screen` and `.scroll` rules are unchanged.
- Protected: canonical corpus, paragraph IDs/order, A17/B-v7.10, RA19B flow, all search/speaker/display/flow payloads, Stage B search logic, Stage C F1/F3 runtime-cache algorithm, F8 Android handler and user-data schema.
- Corpus manifest SHA-256: `45b5a86eabacc4a5e2b8a6ad49f032a7d859b344a61030d7445b3629a6c3d55e`; corpus cache epoch: `cm-45b5a86eabacc4a5`.
- Offline content binding SHA-256: `5118ef47b7fb43a3b2323cd890ac7311976cc7fe62b12d9536a80fe0fc511885`; assets: **224**; bytes: **191940115**.
- **Package state at freeze:** candidate bytes only. Desktop browser validation, iPhone/iPad regression confirmation, reopened-ZIP audits and final decision lock are external authorities written after freeze. No post-freeze PASS is claimed inside this deploy package.

> Version 41 below remains the immutable Stage C runtime-storage/PWA baseline and historical evidence.

---

# Livre du Ciel — Version 41 / Stage C runtime storage + PWA

- Public version: **41**. Technical identifier: **v2.19.41-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-V41-STAGE-C-RUNTIME-STORAGE-PWA**. Build date: **2026-08-25**.
- Immutable immediate baseline: Version 40 SHA-256 `15d9b2bc926583a2e68fa67eb505966a47aaf8f74fe459ff2830d2bd5fa345c9`.
- Stage C scope only: F3 bounds the integrity-verified temporary runtime corpus cache to **48 entries / 50331648 bytes (~48 MiB)**; completed full offline preparation clears the now-redundant runtime cache; **Effacer les caches** deletes both the full offline preparation cache and the temporary reading/search runtime cache while leaving Mon Espace/user data untouched; runtime-cache usage is reported separately in the offline UI.
- F1 integrity rule remains mandatory: no network corpus response is adopted until byte length + SHA-256 verification succeeds; cached corpus hits still require the verified SHA/byte/content-binding headers. A fresh poison-cache adversary is required for this successor because service-worker cache-management code changed.
- Corpus/search protection: all 36 search shards, semantic/search metadata indexes, canonical paragraph shards, all 36 speaker shards, A17/B-v7.10, RA19B flow data and Stage B search-trust logic are byte-unchanged from Version 40.
- Corpus manifest SHA-256: `6a4c9dd408469ae6e7e1f42433a6c4fe9ee741ebc563389a6107dd63e679a6a9`; corpus cache epoch: `cm-6a4c9dd408469ae6`.
- Offline content binding SHA-256: `c9a745098723f4f2b21c26600e04eefd2b59acae35a74157a0bbfef4c9c0fcc4`; assets: **224**; bytes: **191939638**.
- **Package state at freeze:** candidate bytes only. Primary reopened-ZIP, independent reopened-ZIP, F1 adversary, installed-PWA/update/offline tests and final decision lock are external authorities written after package freeze. This deploy ZIP contains no post-freeze PASS claim.
- Native HTTP/PWA navigation is known to be blocked by administrator policy in the current execution environment unless later evidence proves otherwise; such gates must be `NOT_TESTED_ENVIRONMENT`, not package FAIL or PASS.

> Version 40 below remains the immutable Stage B search-trust baseline.

---

# Livre du Ciel — Version 40 / Stage B search trust

- Public version: **40**. Technical identifier: **v2.19.40-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-V40-STAGE-B-SEARCH-TRUST**. Build date: **2026-08-25**.
- Immutable immediate baseline: Version 39 SHA-256 `a2daae6334a63352983d0680748be16fcf9dc399a5a7b687657f652ee77c7e79`.
- Stage B scope only: F5 replaces raw substring admission with exact normalised token/phrase boundaries in both thematic-family matching and the core phrase/word lexical checks; F4 makes displayed counts/categories describe the same accepted result population; F12 highlights raw text before HTML escaping so entity names cannot be corrupted; the Jesus search filter is truthfully labelled **Passages contenant des paroles de Jésus**; F6 receives a fresh host-side full-corpus algorithmic benchmark.
- Search corpus/index protection: all 36 search shards, `semantic_index.json`, `search_metadata_index.json`, all canonical paragraph shards, all 36 speaker shards and A17/B-v7.10 authorities are byte-unchanged from Version 39. No BM25/IDF/index rebuild is performed.
- Corpus manifest SHA-256: `03c28d07abdf93ea436ee6b3c3ccbb5f53856fe4ed6dd5cd3040e7d0ac84947f`; corpus cache epoch: `cm-03c28d07abdf93ea`.
- Offline content binding SHA-256: `02986a86f7838b0d8cb5dbaf74ea95abb71363faa1c5e849d70422c5831c1e6a`; assets: **224**; bytes: **191939192**.
- **Package state at freeze:** candidate bytes only. Primary reopened-ZIP, independent reopened-ZIP and final decision lock are external authorities written after package freeze. This deploy ZIP contains no post-freeze PASS claim.
- Physical-device browser/PWA/offline/accessibility behaviour and live-origin binding are not claimed by package metadata.

> Version 39 below remains the cache-epoch-corrected immutable baseline. Version 38 remains historical but its Stage A release-integrity PASS was superseded after the cache-epoch contradiction was discovered.

---

# Livre du Ciel — Version 39 / Stage A.1 cache-epoch reconciliation

- Public version: **39**. Technical identifier: **v2.19.39-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-V39-STAGE-A1-CACHE-EPOCH-RECONCILIATION**. Build date: **2026-08-25**.
- Immutable immediate baseline: Version 38 SHA-256 `6d9c5d37aa7e885a923e27eb0c1d8fbaffeb69543948329513d677fc6be5ded3`.
- Trigger: pre-Stage-B evidence recheck found a genuine Version 38 release-binding contradiction. Its current `corpus/manifest.json` digest was `c9c296…` while runtime `CORPUS_CV` still used the older Version 36 epoch `cm-2fb4a1…`, and the active `version.json` `corpus_cache_epoch` still carried the Version 33 epoch. This means the Version 38 Stage A PASS decision is superseded for release authority by this correction.
- Stage A.1 scope only: restore the F1 contract that the runtime corpus cache epoch is mechanically derived from the current frozen corpus-manifest digest. No search logic, canonical text, paragraph IDs, semantic/BM25 index, search shards, speakers, presentation parents, flow/display data or user-state schema are changed.
- Corpus manifest SHA-256: `ba92e2a4c3f581a6a3e5218804dea3e6883b568339eaa9cb455fad95dcb7e56d`; corpus cache epoch: `cm-ba92e2a4c3f581a6`.
- Offline content binding SHA-256: `6ce3b4ec874c473ac941d31049fbb32779fd32368043fd70ff8ae2b77e8441fd`; assets: **224**; bytes: **191938725**.
- **Package state at freeze:** candidate bytes only. Primary reopened-ZIP, independent reopened-ZIP and final decision lock are external authorities written after package freeze. This deploy ZIP contains no post-freeze PASS claim.
- Physical Samsung/iPhone/iPad, installed-PWA, true-offline, live-origin and VoiceOver/TalkBack results are not claimed by package metadata.

> Version 38 below is retained as immutable historical evidence but is **not deployment-authoritative** because the newly discovered cache-epoch binding contradiction invalidated its release-integrity PASS claim.

---

# Livre du Ciel — Version 38 / Stage A accessibility + date + featured-quote correctness

- Public version: **38**. Technical identifier: **v2.19.38-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-V38-STAGE-A-ACCESSIBILITY-DATE-QUOTE-FREEZE-METADATA-ANCHOR-HARDENED**. Build date: **2026-08-25**.
- Immutable immediate baseline: Version 36 SHA-256 `c6eda0803fafe6fc005ced2fe673b4aa2004cbeffe0b342d82e291453c30a4ef`.
- Stage A scope only: F15 accessible Jesus/Mary speaker equivalent independent of colour/Repères; F16 semantic screen headings + one main landmark; F17 one shared visual/AT attribution model; F18 throttled offline live announcements + non-live selection action panel; F22 all 137 formerly omitted visible entries routed to `Sans date`; F11 all 14 featured quotes bound to frozen exact paragraph targets; package freeze-state metadata contract.
- Protected bytes: all 36 speaker shards, canonical paragraph/search/display/flow/supplement payloads and user-state schema are unchanged except `corpus/manifest.json` release metadata. Semantic speaker and `presentation_parent` values are unchanged. `interaction_anchor.js` changes only its injected-metadata exclusion list so accessibility/Repères labels cannot enter canonical selection offsets.
- F1 cache-integrity algorithm and F8 Android non-fragment targeting handler are preserved; release/cache identifiers are mechanically rebound to Version 38.
- Corpus manifest SHA-256: `c9c296300508048e1b2a52a2c751faf3b187db4ee27ad14ddf2f8899102b98eb`; corpus cache epoch: `cm-c9c296300508048e`.
- Offline content binding SHA-256: `dc1954bec2302d788a8dba05df9f17fa7769c45419a8f07d41f6fef3d68580c4`; assets: **224**; bytes: **191938140**.
- **Package state at freeze:** candidate bytes only. Primary reopened-ZIP, independently implemented reopened-ZIP and final decision lock are external authorities written after package freeze. This deploy ZIP contains no post-freeze PASS claim.
- Physical Samsung/iPhone/iPad, installed-PWA, true-offline, live-origin and VoiceOver/TalkBack results are not claimed by package metadata.

> Version 36 below is retained as immutable historical provenance and is superseded only for Stage A validation by this Version 38 candidate.
> The frozen Version 37 candidate (`0e26740387911fe15a9a275c3ff04d08ba9cbb28f46c2ec74670eb795fbe22d6`) remains rejected historical evidence: deep regression found that legacy canonical-text/fallback highlight paths still counted injected Repères/accessibility metadata.

---

# Livre du Ciel — Version 36 / Repères dual attribution

- Public version: **36**. Technical identifier: **v2.19.36-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-V36-REPERES-DUAL-ATTRIBUTION**. Build date: **2026-08-25**.
- Immutable immediate baseline: Version 35 SHA-256 `87e138759eb8a4402785ebce8dd63ca246c813f36691bd389d5263185339070c`.
- Owner-approved product rule: Repères keeps the outer presentation label `JÉSUS`/`MARIE`; when nested quoted words have a different semantic speaker, a second non-canonical line identifies that quoted voice in natural French. Multiple differing voices are listed uniquely in occurrence order.
- Examples: `JÉSUS` alone for ordinary direct Jesus; `JÉSUS / voix citée : créatures`; `JÉSUS / voix citée : Luisa`; `MARIE / voix citée : Entité Suprême`.
- Repères OFF normal reader is unchanged. Canonical devotional text, paragraph IDs/order, all 36 speaker shards, semantic speakers, presentation parents, offsets, guillemets, search, display/flow shards, F8 Android targeting and iPhone/iPad exact-selection behavior are unchanged from Version 35.
- Corpus manifest SHA-256: `2fb4a1c5cb4c7e9407e0cc14880dbf6ebe456d13caa18b70dc8c1c5b64de57a0`; corpus cache epoch: `cm-2fb4a1c5cb4c7e94`.
- Offline content binding SHA-256: `5323695121d727d0a3de0d7a6d521fedd9c57bdef659bfb4d6ff761d3e651a02`; assets: **224**; bytes: **191936747**.
- Final reopened-ZIP, independent reopened-ZIP, Repères browser matrix, inherited F8 browser regression and F1 cache-integrity regression remain external authorities. Physical Samsung/iPhone/iPad and live-origin/PWA/offline/AT gates are not claimed by this package.

> Version 35 below is retained as historical provenance and is superseded by this Version 36 authority block.

---

# Livre du Ciel — Version 35 / F8 Android non-fragment highlight targeting (clean rebuild)

- Public version: **35**. Technical identifier: **v2.19.35-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-V35-F8-ANDROID-NONFRAGMENT-HIGHLIGHT-REBUILD**. Build date: **2026-08-25**.
- Immutable immediate baseline: Version 33 SHA-256 `97d117fc6ebf0cd8dc03f2962f43f702fe1134db1dafffe5459faea9362ed0bd`.
- Rejected intermediate candidate: Version 34 SHA-256 `a2d973d8951e5241eb5849624f6e31aa2b8cb28f740b16edce8df12b46dfc902` — **FAIL_PACKAGE_CONSISTENCY**, never deploy; its index offline constants were not fully rebound from Version 33.
- F8 repair: in Android/Samsung whole-paragraph mode, only a direct `.para-fragment` tap can start highlighting; taps on `.flow-joiner`, `.reperes-flow-meta`, or other flow-level surfaces are ignored rather than mapped to the first paragraph.
- iPhone/iPad exact selected-text highlighting is unchanged. Canonical devotional text, paragraph IDs/order, search, all 36 speaker shards, display and flow shards are unchanged from Version 33.
- Corpus manifest SHA-256: `ca5494ccd20f7baca50d105cb2f87ee17487488e5dc3b3dbb9bff7c7c47c8f09`; corpus cache epoch: `cm-ca5494ccd20f7bac`.
- Offline content binding SHA-256: `0baff4d489d07ce85c91b418ee2b04bf8d7e8abd786b40fe763aabe67e4a8b58`; assets: **224**; bytes: **191935811**.
- Final reopened-ZIP, independent reopened-ZIP, F8 browser regression and F1 cache-integrity regression remain external authorities. Physical Samsung/iPhone/iPad and live-origin/PWA/offline/AT gates are not claimed by this package.

> Version 33 below is retained as historical provenance and is superseded by this Version 35 authority block.

---

# Livre du Ciel — Version 33 / RA19E.1 semantic + presentation-parent fixed point

- Public version shown to users: **Version 33**.
- Technical app/update identifier: **v2.19.33-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E1-A17-BV7_10-SPEAKER-PARENT-F1-F7**.
- Build date: **2026-08-24**.
- Immutable immediate baseline: **Version 32 / v2.19.32-R1B**, SHA-256 `a5e6a0d76e4e7e7e93eff5583c304d5be9c64fc6370449a2f0634cb067a6aa78`.
- Semantic authority: **A17 PASS_EVIDENCE_FIXED_POINT**, 65,012 main-corpus speaker segments.
- Presentation-parent authority: **B-v7.10/A17 PASS_EVIDENCE_FIXED_POINT**, 65,012 explicit build-generated parent projections; `REVIEW_BLOCKING = 0`.
- Seed controls: **39/39 PASS** after one explicitly re-adjudicated stale control fixture from exact Version 32 context.
- F1: corpus cache epoch is mechanically derived from the frozen corpus-manifest digest; runtime corpus misses use `cache: reload` and size/SHA-256 verification before runtime-cache adoption.
- F7: current release counts and offline bindings are generated after corpus payload freeze; superseded Version 32 values are retained only as historical provenance.
- Canonical devotional paragraphs, paragraph IDs/order/stable refs, search, display, flow, volume and supplement layers remain byte-identical to Version 32.
- Final package/reopen and independent reopen audits remain external release authority; physical Samsung/iPhone/iPad, installed-PWA, live-origin and true-offline tests are not claimed by this static build.

## Current generated bindings

- Corpus manifest SHA-256: `ae456d2c95939ba0a187de281917d006eac7a031d31164bea27fce2c4f4c06f4`.
- Corpus cache epoch: `cm-ae456d2c95939ba0`.
- Offline content binding SHA-256: `1821ea56f67a802c629c53f7c152695d6537662cd2ea3b9ba7828c42b7b22afd`.
- Offline asset count: **224**; total bytes: **191935128**.

> The Version 32 / RA19E block below is retained as historical provenance only and is superseded by this Version 33 authority block.

---

# Historical provenance — Version 32 / RA19E exhaustive speaker-integrity reconciliation

- Public version shown to users: **Version 32**.
- Technical app/update identifier: **v2.19.32-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19E-SPEAKER-INTEGRITY-RECONCILIATION**.
- Build date: **2026-08-23**.
- Exact immediate baseline: **Version 31 / v2.19.31-R1B / RA19D**, SHA-256 `b91aabf84803685cb5a86379c2a76c6239c2882bc1fa8b4277479f978c025441`.
- RA19E scope: exhaustive speaker-integrity reconciliation of the frozen 2,611-candidate universe; **483 correction rows** applied to **20 speaker shards** after `REVIEW_BLOCKING=0`.
- Final speaker inventory: **65,004 segments**; canonical devotional paragraph text, paragraph IDs/order/stable refs, search, display, flow and supplement shards are unchanged.
- Nested semantic voices remain distinct from presentation: RA19E explicitly reconciles quotation depth where required so approved outer-speaker styling remains intact.
- RA19B remains the unchanged source-backed flow authority; flow shards are byte-identical and runtime semantic links are recomputed from corrected speaker data.
- Candidate status: **STATIC PACKAGE CANDIDATE — FINAL REOPEN AUDITS EXTERNAL — PHYSICAL DEVICE RETEST REQUIRED**.
- Physical Samsung/iPhone/iPad, live GitHub Pages, installed-PWA and true-offline release gates are not claimed by this static/package build.
- Wide public release remains subject to the external final decision lock.

## RA19E evidence binding

- Adjudication ledger SHA-256: `6b40bddc43b562537ec8d7102c31535375443e8740a10a59458cb186900b0c21`.
- Frozen correction ledger SHA-256: `b3f809d3d08c4623c23c7a49e57ce180ca3ab2d89eaf6cbab71925eb6c437878`.
- Final deploy ZIP intentionally contains no audit reports; reopened-ZIP and independent audit evidence is maintained externally.

> Version 30 / RA19C below is retained as historical provenance only. It was audited but never deployed.

---

# Historical provenance — Livre du Ciel — RA19C app sharing on RA19B corpus authority

- Public version shown to users: **Version 30**.
- Technical app/update identifier: **v2.19.30-R1B**.
- Stage: **LDC-AFLP-SUP-T1-RA19C-APP-SHARING**.
- Build date: **2026-08-22**.
- Immediate RA19C app baseline: **Version 29 / v2.19.29-R1B / RA19B**, deploy ZIP SHA-256 `eb2fa6abce1525399547f469ad1c2d64e818ff8685fe11cc20a57571c59f92fc`.
- RA19B corpus-flow editing baseline: **Version 28 / v2.19.28-R1B / RA18**, deploy ZIP SHA-256 `cbe48143dd41661a3bbe1da6cf8f1213c705ff9d15527848969587723affe3cc`.
- Frozen source-backed decision ledger: **20,811/20,811** linked boundaries; **20,062 JOIN_CERTAIN**, **749 KEEP_BREAK_CERTAIN**, **0 KEEP_LIST_CERTAIN**, **0 REVIEW**; ledger SHA-256 `d3acc508e1264811916b3c456952a53ebc5b95ccd80d09316bea619769175484`.
- RA19C changes only the app shell: **Aide → À propos → Partager l’application** now uses the device native share sheet with a clean app-home URL and a copy-link fallback.
- RA19B remains the unchanged corpus/display-flow authority: it stores the final source-backed visual policy/action and evidence hash on every active linked `boundary_after`; the RA18 heuristic remains only as a legacy compatibility fallback and is not used by any active linked boundary.
- Canonical devotional text, paragraph IDs/order/stable refs, search shards, speaker identities/offsets, display transforms, supplement data and user anchor semantics are protected and unchanged.
- Physical iPhone/iPad/Samsung, assistive-technology, live GitHub Pages, installed-PWA update and true-offline reopening gates remain external and must not be inferred from static/package checks.

> Corpus provenance: Version 29 / RA19B remains the governing source-backed boundary authority. Version 30 / RA19C changes the app-sharing shell only; it does not reopen the 20,811 RA19B boundary decisions.

# Livre du Ciel — RA16 search-date affordance + simplified public version

- Public version shown to users: **Version 26**.
- Technical app/update identifier: **v2.19.26-R1B** (kept for update integrity, diagnostics and audit only).
- Stage: **LDC-AFLP-SUP-T1-RA16-SEARCH-DATE-AFFORDANCE-VERSION-SIMPLIFICATION**.
- Baseline: **v2.19.25-R1B / RA15** — SHA-256 `c63a29387df707a13bd35753d0314eb623032df38a99e3b6f2816956a85b6d73`.
- Search UI: **Parcourir par date** is now an outlined rounded secondary-action card with visible calendar icon, chevron, hover/active/focus feedback and a 44px+ touch target.
- Version UX: normal users now see one sequential release number only. The former separate application/corpus/backbone technical identifiers are no longer displayed together in Help; they remain available in diagnostic/metadata evidence.
- Search/date algorithms: unchanged.
- Canonical devotional text, paragraph IDs, speaker/search/display/flow shards: unchanged.
- Package role: controlled-test/static candidate. Wide public release remains **NOT AUTHORIZED** while external device/PWA/AT/textual-fidelity/rights/deployment-binding gates remain open.

> The RA15 README content below is retained as historical provenance and is superseded by this RA16 authority block.

---

# Livre du Ciel — RA15 four-pass corrective recheck candidate

- Version: **v2.19.25-R1B**
- Stage: **LDC-AFLP-SUP-T1-RA15-FOUR-PASS-CORRECTIVE-RECHECK**
- Baseline: **v2.19.24-R1B / RA14** — SHA-256 `8fb501d4a841dfcfe5f62da684419e1c2794fc6e04903c113b025bfb491dc228`
- Help/UI corrections: `Thème approché` now describes the actual weaker lexical-match path; `Autour → Thème proche` now truthfully permits same-Tome or other-Tome results; current metadata/context result badges are documented. Search/Autour algorithms are unchanged.
- Report-integrity correction: RA14's active Pass-1 report said “three” harness corrections while the locked redo ledger contained seven. RA14 Pass-3/Pass-4/report-integrity claims are therefore historical/superseded; RA15 uses an evidence-aware claim audit.
- Protected: RA14's Tome-3 `OTHER→JESUS` semantic correction and every supplement/canonical/search/speaker/display/flow shard remain unchanged.
- Package role: controlled-test/static candidate. Wide public release remains **NOT AUTHORIZED** while external device/PWA/AT/textual-fidelity/rights/deployment-binding gates remain open.

> The RA14 README content below is historical provenance and is superseded by this RA15 authority block.

---

# Livre du Ciel — RA14 speaker/help correspondence candidate

- Version: **v2.19.24-R1B**
- Stage: **LDC-AFLP-SUP-T1-RA14-SPEAKER-HELP-CORRESPONDENCE**
- Baseline: **v2.19.23-R1B / RA13** — SHA-256 `1944a3e92b1703badf6a22fbdc8127b037b152df3f8e3f022c43cba9af37f8d8`
- Semantic correction: `LDCSUP.T03.1900-02-12.E001.P003.S01` corrected from OTHER to JESUS on the owner-confirmed direct-Jesus attribution. Translation/devotional text and offsets are unchanged.
- User-facing reconciliation: Help consolidated into 8 task-oriented sections; onboarding/home copy now accurately describes the existing Jesus shortcut and current controls. No new Jesus-only reader was introduced.
- Package role: controlled-test/static candidate. Wide public release remains **NOT AUTHORIZED** while external device/PWA/AT/textual-fidelity/rights/deployment-binding gates remain open.

> The RA13 README content below is historical provenance and is superseded by this RA14 authority block.

---

# Livre du Ciel — RA13 four-pass corrective candidate

- Version: **v2.19.23-R1B**
- Stage: **LDC-AFLP-SUP-T1-RA13-FOUR-PASS-CORRECTIVE-RECHECK**
- Baseline: **v2.19.22-R1B / RA12** — SHA-256 `658758dd09ace331b488f6150e2f295121b80fbf97ed779f709769379e7676b2`
- Package role: **controlled-test/static candidate**. Wide public release remains **NOT AUTHORIZED** until the external device/PWA/AT/textual-fidelity/rights/deployment-binding gates pass.
- Final package authority: the separate RA13 immutable reopened-ZIP audit, independent audit, four-pass audit and final decision lock.
- RA13 corrections: service-worker/current offline-binding trust repair; deterministic ZIP builder made executable/reproducible; F8 report count reconciliation; exact F12 export-byte metadata; current vector-retirement manifest cleanup; last-live hash-field semantics; expanded stale/contradiction scans.
- Protected: canonical corpus text/IDs, all paragraph/search/speaker/display/flow/volume shards, supplements and lexical/BM25 semantic index.

> The RA12 README content below is retained as historical provenance and is superseded by this RA13 authority block.

---

# Livre du Ciel — RA12 static remediation candidate

- Version: **v2.19.22-R1B**
- Stage: **LDC-AFLP-SUP-T1-RA12-PUBLIC-RELEASE-REMEDIATION-CERTIFICATION**
- Baseline: **v2.19.21-R1B / RA11** — SHA-256 `e3fb1de9d4b75f1e8f0e9133ab0ec4da9172c0102a58a561af3fa187f418ff84`
- Static package status target: **LIMITED_PASS_STATIC** until immutable reopened-ZIP audits complete.
- Wide public release: **NOT AUTHORIZED** until physical iPhone/iPad/Samsung, installed-PWA update, true offline, assistive-technology, textual-fidelity/provenance, rights and served-byte binding gates pass.
- RA12 scope: public-release safety/accessibility, Undo, iOS input sizing, focus visibility, modal focus, reduced motion, microtype/touch target fixes, local diagnostics, backup-limit honesty, metadata consistency and release evidence.
- Protected: canonical corpus text/IDs, 36 paragraph/search/speaker/display/flow/volume shards, supplement content, semantic index and RA9–RA11 flow/speech decisions.
- F11 manifest identity: deliberately deferred because the current production path is stable; no `id`/`scope` migration is introduced in this static remediation candidate.
- F12: current 10 MiB single-file import ceiling retained pending required physical-device stress testing; row cap is now named and exports disclose/warn about restorability limits.

> The RA11 README content below is retained as historical provenance and is superseded by this RA12 authority block.

---

# Livre du Ciel — RA11 current deploy authority

- Version: **v2.19.21-R1B**
- Stage: **LDC-AFLP-SUP-T1-RA11-BROADER-BOUNDARY-ADJUDICATION**
- Baseline: RA10 v2.19.20-R1B, SHA-256 `af33a3fd14be8ffe17f3e52ffd26921928c4dac3554707fc038ed4b8d2c015ac`
- Broader boundary inventory adjudicated: **226/226**
- Display joins added: **210 boundaries** in **204 flow groups**
- Intentional-structure boundaries retained: **14**
- Tome-10 source-proven boundaries retained: **2**
- Remaining unclassified cases from the RA10 226-case inventory: **0**
- Canonical devotional paragraph text/IDs/search/speaker/display shards: protected unchanged
- Corpus manifest SHA-256: `ef4adece54ee4ed52ed6c1fe2c075ab0519868a69c74b7a4e5b719788d3c4af9`
- Offline assets: **224**, **168207301 bytes**
- Offline content binding: `a9572242ee9e991872021224c8adb84b542ad789d0f50cc54ff628fbebe52555`
- Static/package status: **LIMITED_PASS_STATIC** pending physical-device/live-origin validation.

> The RA10 README content below is retained as historical provenance and is superseded by this RA11 authority block.

---

# Le Livre du Ciel — v2.19.20-R1B

## RA10 — audit 36 tomes des fausses coupures de paragraphe (2026-08-17)

RA10 part exactement du paquet RA9 v2.19.19-R1B (`39eaab8a9aa81f922cc4bcf42b6a512cfb777a42d17d232de9914526ae05947f`). Il achève la classe de coupures visuelles de mise en page qui avait historiquement été repérée mais laissée non fusionnée pour préserver les identifiants. La couche `flow_NN.json` permet maintenant de corriger l'affichage sans réécrire le texte canonique.

- **131 frontières** ajoutées dans **127 groupes** de flux, sur **26 tomes**.
- **126 frontières** appartiennent à la classe stricte réauditée (fragment sans ponctuation terminale ou court fragment finissant par une virgule, suivi d'une continuation en minuscule).
- **5 frontières supplémentaires** sont individuellement appuyées par source/ledger approuvé (T6, T14, T25 ×2, T36).
- Les 79 paragraphes de compléments ont été scannés : **0** candidat de cette classe.
- Aucun texte canonique, ID, shard de recherche, shard de locuteur sémantique ni transform d'affichage n'est modifié.
- La valeur obsolète `version.json.offline_total_bytes` héritée de RA8 a été corrigée pour correspondre exactement au manifeste hors ligne recomputé.
- Les cas plus larges `virgule + majuscule`, `point-virgule + majuscule`, `deux-points + minuscule` et frontières rhétoriques/listes restent inventoriés séparément lorsqu'ils ne disposent pas d'une preuve équivalente ; RA10 ne les convertit pas automatiquement en prose.

Agrégat de flux après RA10 : **11,628 groupes · 35,349 membres · 23,721 frontières · 187 groupes non-tiret**.

Le statut reste **LIMITED_PASS_STATIC** tant que l'origine GitHub Pages et les appareils physiques ne sont pas validés sur ces octets exacts.


## RA9 — paragraphing des paroles non colorées + flux source Tome 4 (2026-08-17)

RA9 part exactement du paquet RA8 v2.19.18-R1B (`0d4230982b8bde9f5b30cbf0c37bd019446ad1eddd3a37893f8cea39fca62cc1`). Il corrige des coupures visuelles observées sur iPad sans réécrire le texte canonique.

- Les paroles directes non colorées (Luisa, anges et autres locuteurs validés) restent en prose normale, mais ne sont plus séparées visuellement de leur attribution et du guillemet ouvrant par une frontière interne du modèle de locuteur.
- Après le guillemet fermant d’une telle parole directe, la narration qui reprend commence dans un nouveau paragraphe visuel; le guillemet fermant reste attaché à la parole.
- Trois coupures Tome 4, prouvées comme artefacts de mise en page/source, sont jointes dans la couche `flow_04.json` uniquement : 10 septembre 1900 P002→P003, 18 septembre 1900 P008→P009 et 19 septembre 1900 P006→P007.
- Aucun texte de `paragraphs_*.json`, aucun ID stable, aucun offset de locuteur, aucune recherche et aucune donnée utilisateur ne change. Le style Jésus/Marie reste inchangé.


## RA8 — fiabilité des mises à jour PWA (2026-08-17)

RA8 part exactement du paquet RA7C v2.19.17-R1B (`2d9808ad065365e206935d504e6a791e91b716367189c207b7d194abc5bcaac9`) et corrige uniquement le chemin de mise à jour. Le corpus, les icônes, la navigation, les interactions de lecture et les données personnelles ne sont pas modifiés.

- La vérification manuelle lit maintenant `version.json` par une requête réseau sans cache et ne peut plus conclure « dernière version » simplement parce qu'aucun worker `waiting` n'est visible après un délai fixe.
- Les états `installing` / `waiting` / `statechange` sont suivis avec une borne de temps ; si la version publiée diffère encore de la page courante, l'interface indique explicitement que l'installation n'est pas terminée.
- L'installation du Service Worker remplit le nouveau shell avec des requêtes `cache: reload`, afin qu'un nouveau cache ne puisse pas être construit à partir d'un ancien `index.html` du cache HTTP.
- Les navigations en ligne utilisent également une requête fraîche avant d'actualiser le repli du shell. `version.json` est servi réseau-sans-cache par le Service Worker.
- `controllerchange` reste l'autorité de rechargement après activation ; aucune réussite n'est annoncée avant convergence entre la version publiée et la version réellement exécutée.
- Les 224 actifs de préparation hors ligne restent byte-identical ; seuls l'identité/version du cache et le content binding sont rebondés à v2.19.18-R1B.


## RA7 — identité finale Collection Luisa / icône Livre du Ciel (2026-08-17)

RA7 part exactement des octets v2.19.16-R1B (`a4b0754f700ed6bdeca62822df9d31dbcff77a9814475896f521c893fa0a8c1c`) et ne modifie aucune donnée de corpus ni logique de lecture. Il remplace l’ancienne identité d’icône par la famille **Collection Luisa v1.0 FINAL_LOCKED** du 15 août 2026, variante `ldc` / `Le Livre du Ciel`.

- Les neuf actifs runtime sont ceux du lock : favicon 16/32/ICO, Apple touch 60/120/180, PWA 192/512 et maskable 512.
- Les trois anciens `icon-source-*.svg`, non référencés, sont supprimés afin qu’aucune ancienne identité graphique ne subsiste dans le paquet de déploiement.
- `index.html`, `manifest.json` et le shell du service worker référencent uniquement les actifs finaux.
- Tous les fichiers `corpus/**` restent byte-identical à v2.19.16. RA6 (Explications Tome 1 + navigation basse véritablement fixe) est préservé.
- L’identité cache/offline est rebondée à v2.19.17-R1B; la liste des 224 actifs du corpus hors ligne reste inchangée.


## RA6 — Explications éditoriales du Tome 1 + vraie navigation basse fixe (2026-08-16)

RA6 part exactement des octets v2.19.15-R1B (`e0fe99803194f4030ae66c240783f7e48374620e2d3e2bab75793242ea7f4231`) et corrige deux défauts de présentation sans modifier le corpus canonique.

- Les 16 enregistrements `LDC.T01.EDITORIAL.EXPLICATIONS.NOTE001..NOTE016` restent conservés byte-for-byte dans le corpus comme matériel éditorial de l’appendice 2021, mais ne sont plus présentés ni comptés comme les 16 premières entrées du Tome 1. La liste commence désormais par `Luisa commence à écrire`.
- Un seul appendice non compté, `Explications éditoriales`, reprend les 16 notes dans leur ordre source. Le scan exact du corps du Tome 1 ne trouve que trois repères numérotés : `(3)` à `LDC.T01.SEC081.P005`, `(4)` à `LDC.T01.SEC082.P001` et `(5)` à `LDC.T01.SEC082.P009`. Des liens sont ajoutés uniquement à ces trois passages. Aucun rattachement contextuel n’est inféré pour les notes 1, 2 et 6–16.
- Les résultats de recherche et anciens liens ciblant une pseudo-entrée éditoriale ouvrent l’appendice correspondant au lieu d’un lecteur normal.
- La barre `Accueil · Tomes · Recherche · Mon Espace` est maintenant réellement fixée au viewport (`position: fixed; left:0; right:0; bottom:0`) avec réserve de hauteur et safe area. Toast, bannière de mise à jour, panneau contextuel et sélecteur de couleur se placent au-dessus.
- Les 224 fichiers `corpus/**`, tous les paragraphes, recherches, locuteurs, display/flow, suppléments, IDs et offsets restent byte-identical à v2.19.15. Le total technique du backbone reste 2 312 records d’entrée, dont 16 records éditoriaux non comptés comme entrées de lecture ; le dénominateur utilisateur ALIGNÉ devient 2 296 entrées de lecture.


## RA5C — réconciliation ciblée des locuteurs (2026-08-16)

RA5C part exactement du ZIP v2.19.14-R1B bloqué (`16b9d2377a0d29db7e81d6b1cff546cd9f14ccee3a47973d0a4a825c25639ee1`). Il ne rouvre pas l’adjudication générale du corpus. Les décisions antérieures fondées sur le français, Queen et Hugh Owen restent l’autorité; RA5C réconcilie uniquement sept paragraphes où les offsets/structures de citation n’étaient plus synchronisés avec le texte canonique final ou avec la projection locuteur extérieur/intérieur.

- Tome 11: trois dérives d’offset après réparations typographiques/de guillemets sont resynchronisées, sans changement d’identité du locuteur.
- Tome 23 E0040 P117-P118: le tour extérieur continu de Jésus est restauré; les citations illustratives internes restent visibles et sont structurellement imbriquées.
- Tome 25 E0035 P040: le mot `seule` est réintégré dans `«Une seule»`; la citation interne reste visible.
- Tome 20 E0012 P073: Jésus reste le locuteur extérieur; la prière complète déjà identifiée par les preuves antérieures comme parole du Fiat personnifié est `PERSONIFIED_VOICE` en profondeur 2 et hérite visuellement de la typographie de Jésus.

Le texte dévotionnel canonique, les IDs, l’ordre, la recherche, les suppléments, les cartes display/flow, `speech_model.js` et les schémas de données utilisateur ne sont pas modifiés. Les seuls fichiers `corpus/**` modifiés par RA5C sont `corpus/manifest.json` et les quatre shards de locuteurs `speakers_11.json`, `speakers_20.json`, `speakers_23.json`, `speakers_25.json`. Le total de segments backbone devient 65 110, dont 59 009 JESUS et 468 PERSONIFIED_VOICE.


## RA5B — recheck profond performance + intégrité des preuves (2026-08-16)

RA5B repart des octets v2.19.13-R1B (`65ade47bf7baa385bf4b5951d91e11780c41a58e341d16253131c084bed15044`). Le recheck a confirmé les trois objectifs RA5 mais a trouvé un défaut de profondeur dans le chargement : les chemins légers (`boot`, Tomes, index de Tome, statistiques/dates) appelaient encore le chargeur de suppléments monolithique et téléchargeaient aussi `supplement_search.json` et `supplement_speakers.json` avant que Recherche ou le lecteur n'en aient besoin. Les chargeurs sont maintenant séparés : registre+manifeste pour la navigation/index, locuteurs uniquement pour le lecteur/filtre locuteur, recherche uniquement pour les recherches textuelles. La sémantique du corpus et des compléments ne change pas.

Le recheck a aussi invalidé l'ancien paquet de preuves RA5 comme preuve autonome : plusieurs scripts dépendaient de chemins absolus `/mnt/data/ra5_exec` et le rebuild déterministe exigeait un ZIP baseline absent du paquet de preuves. Le nouveau paquet de preuves RA5B inclut donc la baseline v2.19.13 et des outils relatifs/portables.

À l’étape historique RA5B, les **224 fichiers `corpus/**`, `speech_model.js`, les IDs, offsets de locuteur, la recherche, les schémas utilisateurs et la palette active Jaune · Bleu · Vert · Violet · Rose restaient inchangés**. La navigation basse persistante et le chargement Tier-1/Tier-2 RA5 sont conservés.

**Blocage découvert par le recheck global des paroles directes.** Le test RA4C/RA5 prouvait que chaque *segment déjà validé comme Jésus/Marie* commençait en bloc, mais il ne prouvait pas que la géométrie de tous les segments couvrait l'intégralité de chaque parole directe. Le recheck a trouvé plusieurs sous-couvertures certaines (notamment T11 24-02-1912 P009, T11 14-10-1914 P004, T11 14-12-1916 P007, T23 E0040 P117-P118 et T25 E0035 P040) ainsi qu'un cas imbriqué T20 E0012 P073 où le discours extérieur de Jésus contient une citation personnifiée du Fiat. Ce dernier cas interdit une expansion automatique sans adjudication source/locuteur. **Historique RA5B : v2.19.14 était donc un candidat correctif de travail, non autorisé au déploiement.** Ce blocage est précisément celui traité par RA5C; les validations physiques/PWA restent séparées et externes.


## RA5 — navigation persistante, ouverture rapide des Tomes et palette unique (2026-08-16)

RA5 part des octets v2.19.12-R1B (`cc1522e9c5480eef558ac1090467a54778bea874937894df26837314bb0108d4`). RA5 avait traité le bandeau principal `Accueil · Tomes · Recherche · Mon Espace` comme structurellement persistant parce qu'il était un sibling flex hors des écrans. RA6 a ensuite démontré que cette preuve était insuffisante : le bandeau n'était pas réellement fixé au viewport et pouvait être déplacé/poussé par la géométrie du shell. La vraie fixation viewport est donc une correction RA6.

L'ouverture d'un Tome utilise maintenant deux niveaux : le fichier léger `volume_NN.json` suffit pour afficher la liste des entrées, tandis que `paragraphs_NN.json`, `speakers_NN.json`, `display_NN.json` et `flow_NN.json` sont chargés séparément lorsque le lecteur en a besoin ou en préchargement non bloquant après l'affichage de la liste. Les index légers peuvent rester en mémoire pour la session ; le LRU de 4 volumes ne concerne que les données lourdes du lecteur. Les métadonnées `volume_NN.json` sont servies cache-first par le service worker versionné, avec repli réseau.

La création et la modification d'un surlignage utilisent désormais une seule palette et le même sélecteur : **Jaune · Bleu · Vert · Violet · Rose** (`yellow · blue · green · purple · pink`). La valeur historique `gold` reste lisible/importable pour compatibilité mais n'est jamais proposée comme sixième choix actif ni écrite par une nouvelle création/recoloration.

À l’étape historique RA5, les **224 fichiers `corpus/**` étaient protégés et inchangés**. RA5 ne modifiait ni le texte, ni les IDs, ni les offsets de locuteur, ni la recherche, ni les schémas de données personnelles, ni le contrat RA4C des paroles directes. Une validation physique des octets v2.19.13 exacts restait requise.


## LDC-AFLP-SUP-T1-RA4C-DIRECT-SPEECH-BLOCK-START-GLOBAL-HARDENING — séparation globale des paroles directes

**Statut embarqué :** candidat non déployé ; la décision finale de release est portée par les audits externes du ZIP immuable et leur decision lock.  
**Lignée source originale :** v2.18.9-R1B / GR9, SHA-256 `cc0759f1c635b0b2be8d58bd2c97305b11168e5b3ab90d194f757340f14c5f90`  
**Baseline immédiate de RA4C :** v2.19.11-R1B, SHA-256 `949ec1e4b5af6f486c096e49fa071868749662d2e6809cd134d932b005a3a992`  
**Backbone AFLP immuable :** `G036-AFLP-R1B-UWR2`  
**Vue composite :** `G036-AFLP-R1B-SUP-T1`

### Portée éditoriale

Translation Set 1 ajoute, dans une couche `LDCSUP` séparée du backbone AFLP :

- **2 compléments internes** : Tome 4 — 30 janvier 1901 ; Tome 5 — 29 octobre 1903 ;
- **12 entrées datées complètes** absentes de l'édition AFLP ;
- **79 paragraphes français** ;
- **79 enregistrements de recherche** ;
- **52 segments de locuteur**.

Les traductions françaises ont été établies directement à partir d'**IT-PM**. Queen et Hugh Owen sont utilisés uniquement comme traductions comparatives. Chaque complément porte une provenance structurée et un badge visible **`COMPLÉMENT · IT-PM`**.

### Contrat de lecture

- **ENRICHI** est la vue par défaut : corpus ALIGNÉ + compléments approuvés.
- **ALIGNÉ** affiche les 2 312 entrées du corpus français aligné sur le périmètre de l’édition AFLP de référence. Le terme « aligné » décrit le périmètre éditorial des textes/dates ; il ne signifie pas que chaque formulation française reproduit nécessairement mot pour mot la traduction imprimée AFLP.
- **COMPLÉMENT** isole les 14 compléments approuvés : 12 entrées complètes + 2 compléments internes, traduits directement depuis IT-PM, avec ancrage explicite et action « Voir dans le contexte ».
- Le sélecteur **ALIGNÉ · COMPLÉMENT · ENRICHI** est visible dans Bibliothèque, dans chaque Tome et dans le lecteur ; le choix est mémorisé.
- Le style du locuteur reste indépendant de la provenance : Jésus garde le style Jésus, Luisa le style Luisa, etc.
- La provenance est indiquée au niveau du conteneur/badge afin de ne pas entrer en conflit avec les surlignages personnels.
- Les favoris, notes, surlignages et états de lecture existants restent attachés à leurs identifiants stables ; les compléments ont leur propre identité `LDCSUP` et leur propre version de traduction.

### Protection du backbone

À l’étape historique RA4C, les **224 fichiers `corpus/**` du paquet de cette étape restaient byte-identical par rapport à v2.19.11**. Les 220 actifs hérités de GR9 constituaient le noyau historique ; les 4 fichiers de supplément ajoutés ensuite restaient eux aussi inchangés. Aucun texte, ID, ordre, offset de locuteur, recherche ou métadonnée canonique R1B n’était réécrit par ce recheck.

À l’étape historique RA4C, backbone : **2 312 entrées · 74 348 paragraphes · 74 348 recherches · 65 107 segments sémantiques**.  
Vue enrichie : **2 324 entrées visibles · 74 427 paragraphes visibles**, dont 79 paragraphes `LDCSUP`.

### Recherche

La recherche **métadonnées + lexicale/BM25** couvre le backbone et les compléments. Le sous-système vectoriel/embeddings dormant a été **retiré du paquet RA3**, y compris les trois artefacts R1B et le chargeur Xenova. `corpus/semantic_index.json` est conservé : il sert au classement lexical/BM25 et thématique, pas aux embeddings. Toute future recherche vectorielle nécessitera une reconstruction complète contre le corpus composite exact ainsi qu’un runtime bundlé ou auto-hébergé, dans une tranche séparément autorisée.

### Hors ligne / PWA

La préparation hors ligne inclut **224 actifs vérifiés** : les 220 actifs hérités et les 4 fichiers du supplément. L'identité de cache, le manifeste hors ligne et son content binding sont versionnés pour v2.19.16-R1B.

### Limites de décision

Translation Set 1 améliore la complétude par rapport à AFLP, mais **ne certifie pas la complétude absolue des 36 tomes**. Les autres différences propositionnelles ou généalogiques restent hors de cette tranche.

Les validations physiques restent distinctes : iPhone/iPad/Samsung, PWA installée, mode avion, cycle de mise à jour, lecteur d'écran et origine GitHub Pages exacte ne peuvent être déclarés PASS sans tests réels sur ce paquet exact.

### Baseline UX préservée

La ligne GR9 reste la base fonctionnelle : surlignage aligné avec 24 Heures, continuité visuelle du locuteur extérieur, favoris avec cœur dans le répertoire de Tome, statut explicite `Lu`, navigation contextuelle, mode clair/sombre, mise à jour PWA et intégrité offline. Le détail historique demeure dans `ldc-state.md`; il n'est pas dupliqué dans ce README de déploiement.


## RA1 deep re-audit repair (2026-08-14)

A four-pass audit of the written v2.19.0 ZIP found and corrected three runtime/data issues that the earlier static suite had missed: (1) six inherited lexical/BM25 helper functions were accidentally deleted by the v2.19.0 vector-disable patch, which could make body search fail at runtime; (2) enriched `searchMetadataIndex` retained the backbone paragraph count and changed `volume_counts` object values into numbers; and (3) public diagnostics referenced the undefined `metadataSearchIndex` variable. The re-audit also replaces the prior key-claim-only report check with exhaustive active-report line/row reconciliation and exact shipped-function extraction tests. At the RA1 stage, the R1B backbone and all 14 Translation Set 1 texts remained unchanged. The RA2 section below supersedes that translation-freeze statement for exactly two source-controlled amendments; the R1B backbone remains unchanged.


## RA2 deep recheck corrections (2026-08-14)

A fresh audit of the written RA1 ZIP found three classes not covered by the prior suite: (1) shared/deep links and Mon Espace targets pointing to an inline `LDCSUP` paragraph could fail when the saved reading mode was `AFLP uniquement`; complete-supplement deep links could also fail before `openEntry()` had a chance to enable enriched mode; (2) two Translation Set 1 items required source-controlled amendment — Tome 6, 5 May 1905 heading restored to the masculine `figlio` wording of IT-PM, and Tome 14, 9 September 1922 restored the human will as grammatical agent in the sentence corroborated by both Queen and Hugh Owen; (3) the four core supplement bootstrap JSON files are now in the service-worker shell as well as the verified full-offline manifest, so the enriched app can bootstrap offline without depending on an opportunistic runtime-cache fill. Original R1B files remain untouched.



## RA2 strict three-source execution

Le correctif RA2A historique a été reconstruit déterministiquement depuis le ZIP exact v2.19.4-R1B (SHA-256 `02f546409fa2f46c340db8b4d393c5ab4028f81d1e3effdf894f2f34895c6f86`). La lignée éditoriale de Translation Set 1 remonte à RA1/v2.19.1 et à GR9, mais ces versions ne sont pas l'entrée directe du build RA2A. Les valeurs internes du mode de source sont `aflp`, `additions` et `enriched`. À l’étape RA2, les anciens libellés utilisateur étaient AFLP, AJOUTS et ENRICHI ; ils sont historiques et sont remplacés dans RA2B par ALIGNÉ, COMPLÉMENT et ENRICHI. Deux amendements de fidélité de Translation Set 1 avaient été revalidés avant l'intégration RA2.


## RA2A deep four-pass repair (2026-08-14)

A new independent audit of the written v2.19.4 package found release-evidence and runtime edge-case defects not covered by the previous exact-function suite. RA2A corrects source-selector accessibility, gives inline supplements their own favourite/read/reading-position identity instead of mutating the AFLP host entry, exposes correct IT-PM provenance in Infos et source and support reports, visibly labels supplement-owned Mon Espace records, keeps Accueil/Parcours actions safe in the internal `additions` mode, and makes date navigation include both inline supplements in that mode. The former AJOUTS user label is historical and superseded by COMPLÉMENT in RA2B. The 14 supplement texts and all inherited R1B corpus files are unchanged.


## RA2B terminology / About update (2026-08-14)

Le correctif RA2B part du ZIP exact v2.19.5-R1B. Il ne modifie aucun fichier `corpus/`, aucune traduction Translation Set 1, aucun ID et aucun schéma de données utilisateur. Il remplace uniquement la terminologie visible des trois vues par **ALIGNÉ · COMPLÉMENT · ENRICHI**, remplace le badge utilisateur `AJOUT · IT-PM` par **`COMPLÉMENT · IT-PM`**, met à jour l'Aide et ajoute un véritable écran **À propos** expliquant la portée de l'alignement AFLP, la provenance IT-PM des 14 compléments, le rôle comparatif de Queen/Hugh Owen, l'absence de revendication de complétude absolue et la conservation locale des données Mon Espace. Les valeurs techniques internes `aflp`, `additions` et `enriched`, ainsi que les noms de fichiers/IDs `LDCSUP`, restent inchangés pour éviter tout risque de migration inutile.


## RA4C direct-speech block-start global hardening (2026-08-16)

RA4C repart des octets immuables v2.19.11-R1B (SHA-256 `949ec1e4b5af6f486c096e49fa071868749662d2e6809cd134d932b005a3a992`). Le recheck global a trouvé une classe résiduelle importante : **287 tours de parole validés et visibles de Jésus/Marie restaient `inline`** sous l'heuristique RA4B (**281 Jésus, 6 Marie**). Cela signifiait que certaines paroles directes pouvaient encore commencer sur la même ligne que la narration précédente, même si les reprises de narration après la parole avaient déjà été largement corrigées.

Le contrat lecteur est maintenant explicite et global : **toute parole directe validée et visible de Jésus ou de Marie commence dans un nouveau paragraphe visuel** ; lorsqu'une narration de Luisa reprend après cette parole, elle commence également dans un nouveau paragraphe visuel. Les guillemets extérieurs redondants continuent d'être masqués uniquement dans la présentation ; le texte canonique, les offsets et les IDs restent inchangés. Les citations imbriquées/reportées que la projection attribue à Luisa restent du texte narratif et ne sont pas artificiellement transformées en parole directe.

À l’étape historique RA4C, les **224 fichiers `corpus/**` restaient byte-identical** à v2.19.11. Aucun texte dévotionnel, ID de paragraphe, offset de locuteur, index de recherche, complément, schéma utilisateur ou donnée personnelle n’était modifié. Une validation physique des octets exacts de cette étape restait requise sur iPhone/iPad/Samsung et pour le cycle PWA/live-origin.

## RA4B four-pass corrective recheck — superseded by RA4C (2026-08-16)

RA4B repart des octets immuables v2.19.10-R1B (SHA-256 `6eb568094178a3c745873792a97ddbf61fe296ef4e26a72fa5d33d16c0617367`). L'audit indépendant a reproduit le build mais a refusé la conclusion globale RA4 sur les frontières de parole. La correction reste strictement dans la couche de présentation : cinq fins de parole directe de Jésus précédemment `inline` créent désormais un nouveau paragraphe visuel pour la narration qui suit ; deux guillemets ouvrants non adjacents sont masqués uniquement lorsque le contexte contient une attribution explicite à Jésus/Marie et aucun guillemet imbriqué ; les deux cas du tome 4 ont conduit à un scan global qui a identifié et corrigé six guillemets fermants séparés de l'offset par de la ponctuation, sans masquer cette ponctuation. Les citations intégrées telles que « Je vous épouserai dans la foi » restent inline et les citations imbriquées/reportées restent visibles.

Le contraste du toast sombre validé en RA4 est conservé (12,17:1 en mode sombre ; 13,21:1 en mode clair). Aucun fichier `corpus/**`, aucun ID, aucun offset de locuteur, aucune donnée de recherche, aucun schéma utilisateur et aucune donnée personnelle ne change. À l’étape historique RA4B, une validation physique des octets v2.19.11 était encore requise sur iPhone/iPad/Samsung et pour le cycle PWA/live-origin.

## RA4 initial speech-boundary / dark-toast hardening — superseded by RA4B recheck (2026-08-15)

RA4 a corrigé le contraste des messages temporaires et une grande partie des guillemets/retours de narration sans modifier le corpus. Le recheck RA4B du 16 août a toutefois démontré que la couverture globale RA4 était incomplète : cinq fins de tours de parole directs encore classées `inline` laissaient la narration suivante sur la même ligne, deux guillemets ouvrants restaient visibles lorsque l'offset validé commençait après un court préfixe lexical explicitement attribué à Jésus, et deux cas du tome 4 ont révélé une classe de guillemets fermants restant visibles lorsque l'offset s'arrêtait avant la ponctuation terminale ; le scan global RA4B en a ensuite identifié six relevant de la même correction de présentation. Les preuves RA4 de type « 829/829 » ne couvraient que les cas déjà classés en bloc et ne constituaient donc pas une preuve exhaustive du défaut signalé. RA4B supersède cette conclusion.

Le correctif de contraste RA4 est conservé. À l’étape historique RA4, les 224 fichiers `corpus/**`, les IDs et les offsets de locuteur restaient inchangés.

## RA3 four-pass corrective recheck (2026-08-15)

Ce successeur part du ZIP immuable v2.19.8-R1B (SHA-256 `9ede0aa80a46b76d3201d25d708ab669899cf2e7a5933ddb356874b00e079589`). Le runtime fonctionnel de RA3 est conservé : aucun texte `corpus/**`, aucun index de recherche, aucun complément, aucun schéma de données utilisateur et aucune interaction de lecture n'est modifié.

Le recheck corrige deux défauts de métadonnées embarquées et deux défauts de méthodologie d'audit : (1) `version.json` utilisait le nom `ra3_repairs` pour une ancienne tranche de modes de source, en conflit avec l'actuelle RA3 de retrait vectoriel ; cette provenance est maintenant explicitement historique ; (2) les champs génériques `baseline_candidate_*` pointaient encore vers v2.19.1 et sont rebondés sur la baseline immédiate v2.19.8 ; l'ancien champ générique `baseline_deploy_sha256`, qui contenait en réalité le hash historique GR9, est renommé explicitement ; (3) l'ancien audit « ligne par ligne » propageait simplement le statut du fichier à toutes ses lignes ; (4) l'ancien scanner de contradictions autorisait globalement tout `version.json`. Les audits du présent paquet doivent donc vérifier les claims réellement ligne par ligne et ne plus utiliser ces raccourcis.

Les validations physiques iPhone/iPad/Samsung, PWA installée/mode avion/origine live et VoiceOver/TalkBack/NVDA restent externes et ne sont pas promues par ce recheck machine.

## RA3 vector/embedding retirement (2026-08-15)

RA3 part du ZIP exact v2.19.7-R1B deep-recheck (SHA-256 `e34785817e0e02ec7ad47ea16f6f1c9454cef6d1ea01bfab3685905fcf1aad67`). Cette tranche retire uniquement le chemin de recherche vectorielle dormant : `embeddings_ldc.bin`, `embeddings_ldc_ids.json`, `embeddings_manifest.json`, le chargeur `@xenova/transformers`, les contrôles/états vectoriels et la branche de résultats « Par le sens ». Elle **ne modifie aucun fichier `corpus/`**, aucun texte AFLP/Translation Set 1, aucun ID, aucun segment de locuteur, aucun schéma de données utilisateur et aucune politique de sélection.

La recherche active reste : **métadonnées → lexical/BM25 → résultats**, avec le normaliseur français, les filtres de tomes/locuteur, les compléments et les liens profonds. `corpus/semantic_index.json` reste gouverné et inchangé parce qu’il fournit les IDF/repères thématiques utilisés par BM25 ; son nom ne signifie pas qu’il s’agit d’un embedding. Les anciennes préférences `vector_search_enabled` éventuellement présentes dans IndexedDB sont simplement ignorées ; aucun bump de schéma n’est requis.

Les validations physiques iPhone/iPad/Samsung, PWA installée/mode avion, origine live et VoiceOver/TalkBack/NVDA restent externes et ne sont pas promues par cette tranche machine.

## RA2C interaction harmonisation (2026-08-15)

RA2C part du ZIP exact v2.19.6-R1B (SHA-256 `64872f494449c2be5e54da67e0b14acb8825fe0a5b6cafb7fd78d86348f92638`). Cette tranche est limitée à l'interface : elle fusionne **À propos** dans la fin de **Aide** sous **À propos et sources**, sans réécrire la provenance éditoriale, et réduit la barre contextuelle primaire à **Surligner · Note · Copier · Fermer**. **Partager la référence** et **Copier le lien** restent dans les outils du lecteur ; **Ajouter à une collection** reste une action secondaire propre au Livre du Ciel.

Aucun fichier `corpus/`, aucune traduction Translation Set 1, aucun ID, aucun segment de locuteur, aucun index de recherche, aucun schéma de données utilisateur et aucun comportement de sélection Android/iPhone/iPad n'est modifié par RA2C. La palette reste **Jaune · Bleu · Vert · Violet · Rose**. Les validations physiques iPhone/iPad/Samsung, PWA installée, mode avion, origine GitHub Pages exacte et lecteurs d'écran restent externes à cette tranche.


## M10 v57 runtime hotfix

Version 57 preserves the exact R3/SUP-T4 corpus content from the corrected v56 baseline. It moves service-worker synchronisation ahead of the first corpus request so an older installed worker cannot mix predecessor corpus files with a newer index. If boot still cannot synchronise, the loading screen becomes a visible repair action that clears app caches/service-worker state only; IndexedDB user data is preserved.


## M11 v58 bootstrap hardening

v58 supersedes v57 after deep re-audit. It preserves the exact R3/SUP-T4 corpus payload, extends service-worker install tolerance for the ~7.5 MB/35-asset atomic shell, prevents destructive repair while offline, distinguishes service-worker/corpus failures from IndexedDB/other boot failures, and corrects active current-state metadata that still referred to v56.


## M12 v59 atomic bootstrap hardening

v59 supersedes v58 after an additional adversarial service-worker review. The installed shell cache is now immutable for its release; network navigation no longer overwrites an older shell with a newer HTML document. Corpus files that the fetch handler never reads from SHELL_CACHE were removed from the install shell. Instead, the two boot-critical registry files (`corpus/supplements.json` and `corpus/supplement_manifest.json`) are fetched by the installing worker, SHA/size/content-binding verified against the new offline manifest, and staged in the new versioned runtime cache before activation. Thus a successful worker installation carries the exact registry needed for the next boot. Generic corpus timeouts now default to retry rather than cache deletion; repair remains available only for an identified version/integrity conflict.
