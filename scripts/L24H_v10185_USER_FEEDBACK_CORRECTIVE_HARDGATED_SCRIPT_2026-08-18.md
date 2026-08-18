# L24H v101.85 — User-feedback corrective hard-gated execution script

Date: 2026-08-18  
Governing baseline: `L24H_v10184_GITHUB_DEPLOY_PREPUBLIC_RELEASE_CORRECTED_LOCKED_HARDENED_R2.zip`  
Required baseline SHA-256: `92fdaf4ff2c1b20096d21b57cc3ad51794bf88094e9d3e5d68483a1e2d65a1f4`

## 0. Non-negotiable decision rules

1. Stop before modifying runtime files if the baseline hash, package inventory, governing state, or requested scope conflicts.
2. Stop before modifying runtime files if a requested devotional-text change lacks governing source/editorial evidence.
3. Do not make product/editorial choices beyond the approved user-feedback intent recorded in the governing state.
4. Execute one item at a time. Each item must pass its own evidence gate before the next item starts.
5. For every item: `PLAN → IMPLEMENT → DIFF → LINE-BY-LINE REVIEW → BUILD/STRUCTURE CHECK → TARGETED TEST → MINI-REGRESSION → INDEPENDENT RECHECK → PASS OR REDO/REVERT`.
6. No Word review packs.
7. Final ZIP is the source of truth. Reopen it in a fresh folder and audit it independently.
8. Never declare overall `PASS` while external physical/PWA/AT/live/rollback release gates remain open. If all package/static gates pass but those gates remain untested, final status is `LIMITED_PASS`.
9. If final reopened-ZIP or independent reopened-ZIP audit fails, final status is `FAIL` (or the exact stronger failure code such as `FAIL_REPORT_INTEGRITY` / `FAIL_EVIDENCE_MISSING`).
10. Final response must exactly match `metadata/final_decision_lock.json`.

## 1. Baseline freeze and evidence inputs

Required inputs:

- exact baseline ZIP with SHA-256 above;
- governing state `luisa-24h-state_v101.84_2026-08-18_HARDENED_R2_UPDATED_USER_FEEDBACK.md`;
- user-feedback instruction embedded in the supplied markdown/history.

Record before modification:

- ZIP SHA-256, bytes, member count;
- SHA-256 for `index.html`, `luisa_24_heures.html`, `sw.js`, `manifest.json`, `version.json`;
- `APP_VERSION`, `STORAGE_SCHEMA_VERSION`, `PERSONAL_SNAPSHOT_VERSION`, `BUILD_DATE`;
- counts for Hours, library items, paragraph IDs, speech targets/segments, existing personal-data fields;
- hash of protected corpus structures.

### Pre-modification authority gate

The 15th-Hour correction is permitted only because the governing state records Louis's explicit approved correction:

`... humilié par ton silence, il proclame devant tous que Tu es un fou.`

This explicit editorial approval is the governing evidence for UF-15-01. Do not infer any additional wording change.

## 2. Exact scope

### UF-17-01 — 17e Heure visible split in `et`

Reported display:

`... contiennent, e` + line/break + `t constitue-Moi ...`

Protected devotional corpus contains contiguous `et` and must not be rewritten merely to mask a renderer defect.

Required investigation before any fix:

1. locate `PASSION24.HOUR.17.P027` text;
2. map `SPEECH_DATA`, `SPEECH_END_VISUAL_BREAKS`, display segmentation and quote-suppression positions against the exact character indices;
3. scan **all** `SPEECH_END_VISUAL_BREAKS` for positions that fall inside an alphabetic token;
4. if and only if a deterministic runtime/render cause is proven, fix the smallest metadata/render cause;
5. preserve paragraph ID, paragraph wording, speech offsets and highlight offsets;
6. after fix, prove there are zero mid-word visual-break positions package-wide.

If the exact R2 runtime cannot reproduce or prove a deterministic cause, classify this item `NOT_REPRODUCED_STATIC / PHYSICAL_DEVICE_REQUIRED`, make no corpus edit, and continue only if this is an adjudicated NOT_TESTED condition rather than a failed implementation gate.

### UF-15-01 — 15e Heure punctuation/continuation

Current:

- `PASSION24.HOUR.15.P014` ends `... ton silence.`
- `PASSION24.HOUR.15.P015` starts `Il proclame ...`

Approved result:

- P014 ends `... ton silence,`
- P015 starts `il proclame ...`

Hard constraints:

- do not delete/renumber P014 or P015;
- do not merge IDs;
- do not change any other wording;
- preserve paragraph order;
- verify search, anchors, notes/highlights, history/deep links and speech targets remain valid;
- prove normalized word sequence is unchanged except the approved punctuation and capitalization transition.

### UF-APPROF-01 — separately mark/highlight an `Approfondir` reading title

Approved product intent is already fixed by the governing state:

- title/whole-reading marker is independent of body text highlights;
- persistence key is the stable `TEXT_LIBRARY` item ID;
- user chooses one of the existing five highlight colours;
- title visibly carries the chosen colour;
- body highlights remain unchanged and independent;
- marked reading appears clearly in `Mon Espace`;
- opening it from `Mon Espace` opens the complete reading at the beginning;
- unmark/remove has Undo protection;
- machine backup export/import preserves it;
- no collision with paragraph-highlight IDs or offset model;
- keyboard/screen-reader semantics are explicit.

Implementation model (locked to avoid product ambiguity):

- add a separate `libraryMarks` personal-data store keyed by stable library item ID;
- do **not** encode title marks as text-offset highlights;
- add a dedicated title-marker colour picker rather than overloading native selection or Samsung paragraph mode;
- increment personal-data schema/snapshot versions because a persistent field is added;
- old backups without `libraryMarks` migrate safely to `{}`;
- new backups validate `libraryMarks` strictly.

## 3. Protected areas

Unless explicitly named above, preserve:

- devotional wording and all corpus paragraphs;
- all paragraph IDs and order;
- `TEXT_LIBRARY` body content and item IDs;
- `HOUR_LINKED_TEXTS`;
- `SPEECH_DATA` offsets and targets;
- existing text-highlight offset model;
- notes;
- read/progress state;
- navigation/history behavior;
- Samsung whole-paragraph highlighting mode;
- iPhone/iPad exact-selection highlighting;
- fixed bottom navigation;
- update/service-worker logic except required version/cache metadata;
- icons and manifest display identity.

## 4. Item execution gates

### Gate A — UF-17-01

Evidence required:

- exact paragraph text and length;
- exact suspect break position and adjacent characters;
- exact renderer code proving how the break is inserted;
- package-wide mid-word break scan before and after;
- diff limited to the proven visual-break metadata/render fix;
- speech target/offset parity unchanged.

PASS only if deterministic root cause is proven and corrected, or if the item is explicitly adjudicated NOT_TESTED without an unsafe edit. A reproduced-but-unfixed defect is FAIL.

### Gate B — UF-15-01

Evidence required:

- exact before/after strings for P014/P015;
- IDs and paragraph counts unchanged;
- only approved punctuation/case transition changed;
- no speech segment targets P014/P015 are invalidated;
- search target resolution still finds both IDs;
- existing highlight/note ID validation continues to accept both IDs.

### Gate C — UF-APPROF-01

Evidence required:

- `libraryMarks` sanitizer, snapshot persistence, legacy migration, export/import validation;
- title-mark UI uses stable library ID and existing 5 colours;
- title markup exposes button semantics and `aria-pressed`/dialog labels;
- Mon Espace lists marked readings separately;
- card opens full reading at top;
- unmark + Undo restores exact previous mark after durable commit;
- body `textHighlights` structure/hashes/logic not repurposed;
- Android/Samsung highlight state and iOS selection state remain isolated.

## 5. Versioning and migration

Successor runtime version: `v101.85`.

Because `libraryMarks` is a new persisted field:

- `STORAGE_SCHEMA_VERSION`: 7 → 8;
- `PERSONAL_SNAPSHOT_VERSION`: 4 → 5;
- migration from schema 7/snapshot 4 must preserve all prior fields and initialize `libraryMarks` to `{}`;
- historical backups accepted by current validation remain accepted, with `libraryMarks` defaulting to `{}`;
- v101.85 backups must carry `libraryMarks` and schema 8.

External migration/offline proof remains a physical/PWA release gate and cannot be declared complete from static execution.

## 6. Full post-item regression

At minimum rerun from final runtime:

- JavaScript syntax extraction/check;
- JSON parsing for embedded corpus/library/speech structures;
- 24 Hours and paragraph-ID uniqueness/count parity;
- all speech targets resolve to actual runtime render targets;
- every speech offset is valid;
- all visual-break positions valid and none split an alphabetic token;
- title-marker sanitizer rejects invalid IDs/colours/prototype pollution;
- legacy backup with no `libraryMarks` migrates to empty store;
- current backup round-trip preserves a title mark;
- all existing highlight/note sanitizer checks remain unchanged/passing;
- `index.html` and `luisa_24_heures.html` are byte-identical;
- SW/cache/version references match v101.85;
- no stale deploy-facing v101.84/package-name/PASS claims survive.

## 7. Clean evidence rebuild

Do not carry old final-PASS reports forward as current evidence.

Build a clean current evidence universe containing at least:

- `reports/no_regression_fix_ledger.csv`
- `reports/full_regression_matrix.csv`
- `reports/stale_reference_scan.txt`
- `reports/root_deploy_consistency_report.md`
- `reports/nested_zip_consistency_report.md`
- `reports/report_claims_vs_evidence_audit.md`
- `audit/independent_four_pass_audit.md`
- `metadata/hash_manifest.json`
- `metadata/package_manifest.json`
- `metadata/final_decision_lock.json`
- `metadata/build_provenance.json`
- `metadata/user_feedback_authority.md`
- executed build and independent-audit scripts.

Historical baseline identity may be referenced only as explicitly labelled baseline/historical evidence.

## 8. Final ZIP reopen gate

After writing the final ZIP:

1. compute ZIP hash/bytes/member count;
2. reopen from disk into a fresh folder;
3. recompute every file hash;
4. validate package and hash manifests against actual reopened bytes;
5. compare twin runtime HTML files byte-for-byte;
6. parse versions/schema/snapshot/build date;
7. rebuild runtime target map and revalidate all speech targets/offsets;
8. rerun UF-17, UF-15 and title-marker gates from reopened files only;
9. rerun stale-reference scan across all files, reports, metadata and scripts;
10. audit every report claim against current evidence;
11. verify all mandatory evidence artifacts exist;
12. issue `FINAL_PACKAGE_REOPEN_GATE`.

## 9. Independent reopened-ZIP audit

Use a separately implemented auditor, not the assembly/build checker. It must independently reopen the final ZIP, parse and hash files, verify the three corrective items, verify manifests/reports, and issue `INDEPENDENT_REOPEN_GATE`.

## 10. Final decision lock

Decision algorithm:

- if final reopen != PASS → exact failure status;
- else if independent reopen != PASS → exact failure status;
- else if any implemented corrective item fails → FAIL;
- else if any report claim lacks evidence → FAIL_REPORT_INTEGRITY / FAIL_EVIDENCE_MISSING;
- else because external real-device/PWA/AT/live/rollback gates remain open → `LIMITED_PASS`;
- `public_release_ready = false` until those external gates pass on the exact v101.85 package.

The final response must not contradict this lock.
