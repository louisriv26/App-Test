# Les 24 Heures de la Passion — v101.133
## Visual-Boundary Leading-Whitespace Alignment Repair
### Master Execution Script — R1 — 3 September 2026

---

# 0. Mission

Create a **strictly bounded presentation-renderer successor** of immutable v101.132 that eliminates the one-space horizontal misalignment appearing at renderer-generated visual paragraph starts, while preserving all canonical text, source offsets, semantic speaker authorities, presentation topology, stable IDs, storage schemas, highlighting/notes semantics, and all previously closed functionality.

The successor shall be numbered:

**v101.133**

The repair target is not “paragraph indentation” generally. The proven defect class is:

> a renderer-generated **intra-record block-level visual boundary** is inserted immediately before a valid source separator character `U+0020`; because the reading surface uses `white-space: pre-wrap`, that source separator consumes visible horizontal width at the new visual line start.

The correct architectural repair is:

> retain the `U+0020` in the DOM/source-offset/text-selection stream, but give that separator **zero visual advance only at the synthetic block boundary**.

This execution must operate autonomously through all internal/static gates. Stop only at an explicit hard-stop condition below.

---

# 1. Governing authority and immutable baseline

## 1.1 Authority order

Read and bind authorities in this order:

1. `FINAL_V101132_DECISION_LOCK.json`
2. exact immutable v101.132 deploy ZIP
3. current v101.132 state document
4. final v101.132 post-freeze report and meta-audit
5. v101.132 deep four-pass audit / final evidence bundle
6. any supplied alignment-boundary universe or prototype evidence
7. this script

If two authorities contradict each other, **do not silently reconcile them**. Freeze the contradiction and stop before mutation.

## 1.2 Exact immutable baseline

Required baseline package:

`L24H_v101132_GITHUB_DEPLOY_DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION_R1_LOCKED.zip`

Required ZIP SHA-256:

`5a529f8bfee3022fe03da02f42f843d40482a287fbfd61bcb3e0a1bcb8e5bf75`

Required member count:

`701`

Required root `index.html` SHA-256:

`256862863e66d5274ce0835fa725bf853dfda08f03206e210cb266543f32232e`

Current v101.132 decision:

`PASS_STATIC_INTERNAL_FIXED_POINT__EXTERNAL_VALIDATION_OPEN`

v101.132 is immutable. **Never patch it in place.**

## 1.3 Mutation authority

At script start:

`MUTATION AUTHORITY = NONE`

Mutation may begin only after M1 reproduces the defect fixed point and the user has explicitly authorised the bounded v101.133 renderer-only repair.

If explicit user authorisation is already supplied together with this script, record it verbatim in the execution evidence and proceed. Otherwise stop after M1 and request approval.

---

# 2. Expected pre-edit fixed point to reproduce, not assume

The following values are **reproduction targets**, not facts to force onto the evidence.

## 2.1 Raw-text universe

Expected:

- `4,613` text-bearing records
- `0` records whose stored text begins with accidental leading whitespace
- canonical source text itself is not the cause of the observed indentation

If the reconstructed raw universe differs, stop and investigate before mutation.

## 2.2 Runtime synthetic-boundary universe

Expected runtime-visible synthetic-boundary universe:

- `1,748` actual rendered synthetic boundaries
- `82` runtime-visible one-space alignment failures
- `76` unique exact text+offset loci after collapsing exact duplicate renderings

Expected defect-mechanism split:

- `78` `speech-presentation-visual-break` failures
- `4` block-level `ldc-visual-paragraph-break` failures

Expected content-surface distribution of rendered failures:

| Surface | Expected failures |
|---|---:|
| Main Hour meditation text | 42 |
| Réflexions et pratiques | 1 |
| Promesses et bienfaits — main section | 5 |
| Promesses et bienfaits — Library mirror | 5 |
| Linked Livre du Ciel — Hours 1–24 | 28 |
| Part III Livre du Ciel | 1 |
| Prayers | 0 |
| Other Library material | 0 |
| **Total** | **82** |

Expected notable controls:

- Hour 8 contains 5 visible failures.
- `RELATED_HOUR_21.P073` includes the M1C003 Father→narration boundary and must remain semantically/topologically correct; only the visual separator advance is defective.
- `PART_III_MARY_SORROWS.BODY.P212` is the Part III LDC case and must be covered by the LDC visual-flow renderer path.

## 2.3 Clean negative-control universes

Expected:

- `124` declared `DISPLAY_SEGMENTS` boundaries
- `122` actual block-level display-segment starts in the current renderer
- `0` display-segment alignment failures
- `1,467` rendered LDC cross-record boundaries, all aligned
- `1` speech cross-record boundary, aligned
- `1,468/1,468` cross-record controls aligned
- prayers: `0` affected
- native canonical paragraph starts: `0` accidental leading-space defect

These are required negative controls. The repair must not disturb them.

## 2.4 Known static-only false positives

Do not classify a boundary as defective merely because metadata shows `break → U+0020`.

At least these cases are expected to be runtime-clean because a later display-segment boundary resets the visual start:

- H05 P028
- H07 P117
- H08 P015
- H13 P005
- H22 REF P001

The governing universe is therefore **runtime-rendered geometry**, not static metadata adjacency alone.

If runtime reconstruction does not resolve these as clean, stop and investigate.

---

# 3. Non-negotiable protected authorities

The following must remain semantically and, where representable as isolated declarations, byte-identical to v101.132:

- `CORPUS`
- `TEXT_LIBRARY`
- `HOUR_LINKED_TEXTS`
- `INTERNAL_SUBHEADINGS`
- `DISPLAY_SEGMENTS`
- `CONTINUITY_GROUPS`
- `LDC_LIBRARY_FLOW_LAYOUT`
- `SPEECH_END_VISUAL_BREAKS`
- `SPEECH_CROSS_RECORD_VISUAL_BREAKS`
- `SPEECH_DATA`
- `VISIBLE_PARAGRAPH_TOPOLOGY`
- `SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS`
- `SPEECH_PRESENTATION_PROJECTION`
- `SPEECH_PRESENTATION_ADJUDICATIONS`
- all M1C001–M1C004 adjudications
- the 34-operation v101.126 textual fixed point
- the v101.127 strict glyph-flow five-pair authority
- the v101.128 Méditée single-state model
- the v101.129 eight approved host-sentence/topology repairs
- storage schema version
- personal snapshot schema version
- stable paragraph IDs/order
- note/highlight anchors and source-offset semantics

The repair must not alter:

- canonical/devotional text
- speaker identity
- quote identity
- presentation-span offsets
- local-break offsets
- continuity-pair membership
- paragraph topology
- search/source offsets
- user-state schema
- highlighting model
- navigation or product behaviour

Any need to alter one of these authorities is a **HARD STOP / SCOPE EXPANSION**.

---

# 4. Permitted v101.133 functional change

Only the following functional mutation is authorised after M1/user approval:

## 4.1 Boundary-space rule

At a renderer-generated **block-level intra-record visual paragraph boundary**:

1. inspect the first source character immediately after the governed boundary;
2. if and only if that character is exactly ordinary ASCII space `U+0020`;
3. retain that character in the rendered DOM/source text;
4. retain it in source-offset accounting;
5. retain it in `textContent`;
6. retain it in selection/copy text;
7. give that one separator character **zero visual horizontal advance** at the synthetic visual paragraph start.

Do not suppress:

- NBSP `U+00A0`
- narrow NBSP `U+202F`
- tabs
- newlines
- multiple characters
- any non-space character

Do not use generic trimming.

## 4.2 Renderer pathways that must be covered

The rule must be implemented in both actual v101.132 rendering pathways responsible for the defect class:

1. speech/presentation local visual breaks;
2. block-level LDC intra-record visual-flow breaks.

Confirm the exact source functions/classes in v101.132 before editing. The conceptual labels above are not permission to guess source identifiers.

## 4.3 Preferred implementation architecture

Use a dedicated boundary-separator wrapper/class, conceptually:

`visual-boundary-separator-space`

Preferred behavior:

- wrapper contains the original `U+0020` text node;
- visually zero-width;
- overflow clipped if required;
- does not change line height;
- does not alter baseline;
- does not become `display:none`;
- does not remove the source character;
- does not use `aria-hidden="true"`;
- does not use a generic `trimStart()`;
- does not rewrite the canonical string;
- does not move the governed boundary offset.

A typical safe CSS direction is an inline zero-width box around the original space, e.g. an implementation equivalent to:

```css
.visual-boundary-separator-space {
  display: inline-block;
  width: 0;
  overflow: hidden;
  white-space: pre;
  vertical-align: baseline;
}
```

This is **illustrative**, not blindly prescriptive. Prove the final implementation against all gates below.

Reject any implementation that achieves visual alignment by deleting or changing source text.

---

# 5. Execution architecture

Use four macro-gates.

```text
M1  PRE_EDIT_ALIGNMENT_EVIDENCE_FIXED_POINT
M2  AUTHORISED_RENDERER_MUTATION_INTEGRITY
M3  RUNTIME_PRESENTATION_AND_USER_STATE_MATRIX
M4  FINAL_FOUR_PASS_IMMUTABLE_PACKAGE_LOCK
```

Do not stop between atomic sub-gates unless a hard-stop condition is triggered.

---

# M1 — PRE_EDIT_ALIGNMENT_EVIDENCE_FIXED_POINT

## M1.1 Verify immutable baseline

From the uploaded/source ZIP itself:

- compute ZIP SHA-256;
- count members;
- extract root `index.html`;
- compute HTML SHA-256;
- verify package/root layout;
- verify no working copy has been substituted for the immutable baseline.

Required exact match: Section 1.2.

Write:

- `M1_01_BASELINE_IDENTITY.json`

## M1.2 Reconstruct the complete raw text universe

Reconstruct text-bearing records from current runtime authorities, not from an old CSV alone.

Produce a canonical ledger with at least:

- stable ID
- surface/family
- source text
- source length
- raw text SHA-256
- source container
- renderer path(s)

Verify the expected `4,613` universe.

Explicitly scan for source records that begin with:

- U+0020
- tabs
- CR/LF
- U+00A0
- U+202F

Expected accidental leading-whitespace count: `0`.

Write:

- `M1_02_RAW_TEXT_UNIVERSE.csv`
- `M1_03_RAW_LEADING_WHITESPACE_AUDIT.json`

## M1.3 Reconstruct every synthetic visual boundary

Do not rely on one metadata table.

Enumerate actual runtime boundaries produced by:

- speech/presentation local-break renderer;
- LDC intra-record visual-flow renderer;
- display-segment renderer;
- LDC cross-record flow;
- speech cross-record flow;
- any other renderer-generated block subdivision found in v101.132.

For each rendered boundary record:

- stable record ID
- surface
- renderer family
- governed source offset
- character at offset
- next 8 Unicode code points
- whether boundary is block-level at runtime
- whether another renderer boundary supersedes/resets it
- DOM marker/class
- first visible text node/offset
- measured leading-whitespace visual advance
- measured paragraph/content left edge
- PASS/FAIL
- classification rationale

Write:

- `M1_04_RUNTIME_BOUNDARY_UNIVERSE.csv`

Expected runtime boundary count: `1,748`.

If count differs, stop and reconcile.

## M1.4 Measure the defect directly

Primary geometry invariant:

For each synthetic block start, measure the visual advance contributed by characters before the first non-whitespace visible glyph.

Define:

`leadingWhitespaceAdvancePx`

A boundary is defective when:

- it is intended to begin as a normal unindented visual paragraph; and
- one or more source whitespace characters consume visible horizontal width before the first content glyph.

For the current defect class, expected:

- exactly one source character;
- exactly `U+0020`;
- positive advance materially above 1 px.

Use `<= 1 px` as the alignment tolerance.

Do not infer alignment from DOM structure alone.

Do not use vertical displacement as a proxy for horizontal alignment.

## M1.5 Reproduce the 82-case positive universe

Expected:

- `82` runtime-visible failures
- all `82/82` have exactly one immediate `U+0020`
- defect split `78 + 4`
- surface split exactly as Section 2.2
- `76` unique exact text+offset loci after exact deduplication

Write:

- `M1_05_ALIGNMENT_POSITIVE_82_LEDGER.csv`
- `M1_06_ALIGNMENT_UNIQUE_76_LEDGER.csv`

The 82-case runtime ledger, not the 76-case deduplicated ledger, is the governing user-visible regression universe.

## M1.6 Reproduce negative controls

Verify at minimum:

- display-segment block starts: `0` failures;
- all `1,468` cross-record controls aligned;
- prayers: `0` failures;
- ordinary native paragraph starts: `0` failures;
- known static-only false positives are runtime clean.

Write:

- `M1_07_ALIGNMENT_NEGATIVE_CONTROLS.csv`

## M1.7 Baseline failure proof

Run the new alignment gate against immutable v101.132.

It must fail on the complete reproduced defect universe and pass the clean controls.

Target outcome:

```text
v101.132
  affected alignment loci     82 FAIL
  clean negative controls      0 unexpected FAIL
```

Do not continue if the gate is incapable of detecting the user-reported H08 examples.

Write:

- `M1_08_V101132_NEGATIVE_CONTROL_RESULT.json`

## M1.8 Freeze M1

Freeze:

- all ledgers;
- all scripts;
- all source/package identities;
- hash manifest;
- aggregate M1 manifest hash.

Write:

- `M1_09_PRE_EDIT_FIXED_POINT_MANIFEST.json`
- `M1_10_PRE_EDIT_FIXED_POINT_REPORT.md`

### M1 hard-stop conditions

STOP before mutation if any of the following occurs:

- baseline SHA/member count mismatch;
- raw universe is not reproducible;
- runtime-boundary universe materially differs and cannot be reconciled;
- defect count is not 82;
- any affected case uses a character other than single U+0020;
- any case appears to require canonical-text editing;
- any M1C001–M1C004 semantic/topology decision appears wrong;
- additional defect families are discovered;
- any clean negative-control family is already failing for another reason.

If the fixed point is reproduced and mutation is not yet explicitly authorised, stop and request user approval.

---

# M2 — AUTHORISED_RENDERER_MUTATION_INTEGRITY

Proceed only with explicit renderer-only authority.

## M2.1 Build from a fresh extraction

Create a fresh candidate tree directly from the verified immutable v101.132 ZIP.

Do not reuse a previously edited working directory.

Record baseline-to-working-tree provenance.

## M2.2 Implement only the two renderer-path changes

Implement the dedicated zero-visual-advance handling for immediate U+0020 after:

1. speech/presentation block-level local visual break;
2. LDC block-level intra-record visual-flow break.

No per-record patch list may be used in application logic.

The repair must be rule-based and general across the complete defect class.

## M2.3 Preserve source text and offsets

For every affected record, require:

```text
candidate DOM textContent == v101.132 source text
candidate source length    == v101.132 source length
candidate source SHA       == v101.132 source SHA
all governed offsets       unchanged
```

Also verify entire `CORPUS` and `TEXT_LIBRARY` byte identity.

## M2.4 Protected declaration integrity

Extract and compare all protected declarations listed in Section 3.

Require exact byte identity wherever declarations can be isolated.

Where mechanical release identity prevents whole-file byte comparison, use:

- declaration-level exact comparison;
- function-level/AST comparison;
- explicit diff allowlist.

Any unexplained functional diff is blocking.

## M2.5 Release identity

Update only the necessary successor release bindings:

- app version → `v101.133`
- public version if applicable
- build date
- stage
- cache/service-worker version identifiers
- package metadata
- manifests
- current reports
- current tooling/gate inventory
- QA checklist

Recommended stage:

`VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_R1`

Do not leave stale v101.132/v101.131/v101.122 current-version wording in active operational documents.

Historical references are permitted only when explicitly marked historical/baseline/negative-control.

## M2.6 Self-contained evidence dependency rule

Every script advertised as a current package-local gate must have all required immutable inputs inside the package or a clearly bound package-local evidence bundle.

At minimum embed/freeze:

- M1 runtime boundary universe;
- 82-case positive ledger;
- clean negative-control ledger;
- baseline v101.132 negative-control result;
- current gate map;
- current tooling inventory.

No hidden dependency on `/mnt/data`, an earlier chat, or an unbundled temporary CSV is permitted.

## M2.7 Mutation-integrity gate

Create a dedicated v101.133 scope gate proving:

- exactly the allowed renderer/CSS logic changed functionally;
- release identity changed mechanically;
- protected declarations unchanged;
- canonical text unchanged;
- local-break offsets unchanged;
- storage/personal schemas unchanged;
- no third renderer family altered.

Write:

- `M2_01_V101133_MUTATION_INTEGRITY.json`

---

# M3 — RUNTIME_PRESENTATION_AND_USER_STATE_MATRIX

All tests in M3 must execute against the actual v101.133 candidate, not a prototype.

## M3.1 New exhaustive alignment gate

Run the complete reconstructed synthetic-boundary universe.

For every intended unindented synthetic block start:

- compute `leadingWhitespaceAdvancePx`;
- require `<= 1 px`;
- confirm first visible content begins at the normal content edge;
- record device/profile/font-size state.

Required result:

```text
82 prior failures        82/82 repaired
all clean controls       remain clean
unexpected new failures  0
```

## M3.2 Geometry matrix

Run at least these browser profiles:

- desktop Chromium
- iPad portrait-sized profile
- iPad landscape-sized profile
- iPhone-sized profile
- Samsung/Android-sized profile

For the 82 positive controls, run at minimum font sizes:

- 16 px
- 19 px
- 22 px
- 26 px
- 30 px

For the complete 1,748-boundary universe, run at least:

- minimum supported reading size
- default reading size
- maximum supported reading size

Run both Repères states where Repères can alter the relevant DOM flow.

Run light and dark modes on a representative full-surface subset and at least one case from each affected renderer family.

Browser emulation is supporting evidence only; it does not close physical-device gates.

## M3.3 Renderer-path sensitivity tests

Create test-only mutants; never package them.

Required mutants:

### Mutant A — disable the speech boundary-space repair

Expected:

- approximately the reproduced speech-family failures return;
- target: `78` failures;
- LDC-only 4 remain repaired.

### Mutant B — disable the LDC boundary-space repair

Expected:

- exactly the reproduced LDC-family failures return;
- target: `4` failures;
- speech-family 78 remain repaired.

### Mutant C — disable the zero-width CSS behavior globally

Expected:

- full 82-case defect class returns.

### Mutant D — delete the source space instead of zeroing visual advance

Expected:

- source/textContent preservation gate fails.

### Mutant E — apply `aria-hidden` to the separator wrapper

Expected:

- accessibility-structure gate fails.

These mutants prove that the permanent gates are sensitive to both the user-visible defect and forbidden shortcuts.

## M3.4 Text conservation and copy/selection

For all 82 rendered occurrences and all 76 unique exact source loci:

Verify:

- DOM `textContent` exactly equals source text;
- the U+0020 remains present;
- source string length unchanged;
- selecting across the boundary returns the original text including the separator;
- selection offsets before/after the boundary map to the same source indices as v101.132.

Where browser clipboard automation is reliable, also verify copied text; otherwise bind `Selection.toString()` plus source-offset recovery as the minimum automated proof.

## M3.5 Highlighting and notes regression

At representative boundaries from:

- main Hour text
- reflection
- Promesses
- linked LDC
- Part III LDC

test:

### Apple-style exact selection

- select text beginning before and ending after the synthetic boundary;
- apply highlight;
- reload;
- verify exact range/text restored;
- remove highlight;
- verify no orphan spans.

### Samsung/Android whole-paragraph mode

- apply whole-paragraph highlight to a visual paragraph beginning at a repaired boundary;
- verify correct paragraph identity;
- reload;
- verify persistence;
- remove cleanly.

### Notes

- create note anchored before boundary;
- create note anchored after boundary;
- create note/range spanning boundary where supported;
- reload and verify anchor stability.

No storage migration is permitted.

## M3.6 Accessibility-structure check

Automated static/browser check:

- separator wrapper is not `aria-hidden`;
- no new interactive node is introduced;
- no role changes the reading order;
- accessibility text around the boundary remains semantically equivalent to v101.132;
- no duplicate spoken token is introduced in the browser accessibility tree where inspectable.

Physical VoiceOver/TalkBack remains open.

## M3.7 Preserve all inherited application gates

Rerun the complete v101.132 functional/runtime suite, parameterized for v101.133 release identity.

At minimum include the gate families previously closed in v101.132:

- release/mutation integrity
- raw-text completeness
- M1 approved-case rendering
- mutation detection
- strict glyph flow
- legacy continuity
- Méditée core
- responsive
- Hour 24
- Help
- broad runtime
- service worker
- exhaustive presentation
- independent exhaustive presentation

The inherited 5,037 assertions must remain functionally PASS, except where a version-identity assertion is mechanically updated to v101.133.

Do not accept a lower count without explaining the exact harness change.

## M3.8 Presentation matrices

The existing 400-span governed presentation universe remains protected.

Require:

- primary presentation matrix: all PASS across its governed profiles;
- independently implemented presentation matrix: all PASS;
- no speaker-color/italic/wrapper regression at any of the 82 repaired starts.

## M3.9 Continuity gates

Rerun:

- strict five-pair glyph-flow geometry gate;
- legacy continuity matrix;
- cross-record boundary controls.

The new zero-width separator rule must never be applied to a cross-record boundary merely because adjacent source strings happen to contain whitespace.

## M3.10 Service worker / offline package logic

Verify:

- cache version updated;
- all required runtime assets included;
- no stale v101.132 cache binding;
- service worker install/activate logic passes;
- no current file missing from package manifest.

True installed-PWA upgrade and cold-offline physical validation remain open until executed externally.

## M3.11 M3 result

Write:

- `M3_01_ALIGNMENT_GEOMETRY_FULL.json`
- `M3_02_ALIGNMENT_POSITIVE_82_RESULTS.csv`
- `M3_03_ALIGNMENT_NEGATIVE_CONTROL_RESULTS.csv`
- `M3_04_MUTANT_SENSITIVITY.json`
- `M3_05_TEXT_SELECTION_OFFSET_PRESERVATION.json`
- `M3_06_HIGHLIGHT_NOTE_REGRESSION.json`
- `M3_07_ACCESSIBILITY_STRUCTURE.json`
- `M3_08_INHERITED_GATE_SUMMARY.json`
- `M3_09_RUNTIME_FIXED_POINT_REPORT.md`

M3 is PASS only if:

- prior 82 defects → 0;
- unexpected alignment failures → 0;
- protected clean controls remain clean;
- inherited functional gates → all PASS;
- no source/offset/state regression.

---

# M4 — FINAL_FOUR_PASS_IMMUTABLE_PACKAGE_LOCK

## M4.1 Deep Pass 1 — files vs build script

Verify:

- clean immutable v101.132 baseline;
- complete v101.133 overlay/change allowlist;
- every changed file explained;
- every generated file reproducible;
- package manifest accounts for every member;
- hash manifest accounts for every governed file;
- no untracked working artifact;
- no temporary paths;
- no hidden external input dependency.

Full-tree accounting is required. Do not repeat the v101.131 failure where active package changes were omitted from the overlay/accounting model.

## M4.2 Deep Pass 2 — runtime/package behaviour

Rerun on the fully assembled candidate:

- all M3 gates;
- alignment geometry;
- source preservation;
- user-state regression;
- presentation;
- continuity;
- Méditée;
- Hour 24;
- Help;
- broad runtime;
- service worker;
- mutation sensitivity.

All must PASS.

## M4.3 Deep Pass 3 — active reports line by line

Define the active report/document universe explicitly.

At minimum audit:

- `README.md`
- `scripts/EXECUTION_SPEC.md`
- `REAL_DEVICE_QA_CHECKLIST.md`
- current package/version metadata
- current gate map
- current tooling inventory
- current final/prefreeze reports
- any `CURRENT_*` authority document
- current evidence summary

For every nonblank active claim line:

- bind to direct current evidence;
- verify version;
- verify count;
- verify SHA if stated;
- verify status;
- verify that cited gate/tool actually exists and is package-local;
- verify that its required input exists.

No generic “line present” proof is sufficient for factual claims.

## M4.4 Deep Pass 4 — contradiction/staleness/obsolete evidence scan

Search the complete current package/evidence tree for:

- stale `v101.132`, `v101.131`, `v101.130`, `v101.129`, `v101.128`, `v101.127`, `v101.122` references presented as current;
- stale stage names;
- stale member counts;
- stale ZIP/HTML hashes;
- stale gate counts;
- stale FAIL/PASS statements;
- references to missing tools;
- tools omitted from current tooling inventory;
- report gates not mapped in current gate map;
- unbundled input paths;
- `/mnt/data` dependencies;
- obsolete evidence asserted as current;
- “all fixed” wording that would imply external gates are closed.

Historical references are permitted only when context makes their historical/baseline/negative-control role explicit.

## M4.5 Prefreeze four-pass fixed point

All four passes must be PASS.

If any pass fails:

1. classify defect;
2. determine whether repair remains within release-engineering scope;
3. if yes, correct and restart M4.1;
4. if repair requires functional scope beyond the authorised renderer mutation, stop for user approval.

## M4.6 Deterministic Build A/B

From the same verified baseline and frozen v101.133 overlay:

- create Build A;
- create Build B independently;
- compare member paths;
- compare every member byte;
- compare ZIP bytes.

Require byte-identical A/B.

Record:

- member count
- ZIP SHA-256
- root HTML SHA-256
- member-hash manifest

## M4.7 Freeze exact candidate

After deterministic equivalence:

- designate one exact ZIP byte-stream as frozen candidate;
- never modify it again;
- extract that exact ZIP to a fresh directory.

## M4.8 Exact-reopen rerun

On the exact reopened ZIP:

- verify every member against Build A;
- rerun complete M3 suite;
- rerun all four deep passes;
- rerun the new alignment gate;
- rerun mutant sensitivity against test copies;
- rerun independent presentation;
- rerun independent structural/release audit.

The exact frozen ZIP, not the prefreeze working directory, must be the object that passes final validation.

## M4.9 Separately implemented independent audit

Use an implementation that does not merely call or parse the primary gate outputs.

Independently verify at minimum:

- exact ZIP identity;
- raw text unchanged;
- protected declarations unchanged;
- 82 baseline loci now aligned;
- both renderer paths covered;
- clean boundary families unchanged;
- no topology offset mutation;
- source text/selection preserved;
- package self-contained;
- tooling inventory complete;
- gate map complete;
- active documents current;
- all external gates still correctly OPEN.

## M4.10 Final meta-audit

Cross-check all final evidence for:

- contradictory counts;
- mismatched hashes;
- stale version labels;
- stale PASS/FAIL;
- missing files;
- unbound claims;
- different defect counts between reports;
- unacknowledged harness changes;
- overclaim of physical/accessibility/PWA/live-origin evidence.

Meta-audit must PASS before the decision lock is written.

## M4.11 Decision lock must be written last

Only after all prior steps pass, write:

`FINAL_V101133_DECISION_LOCK.json`

Recommended internal/static verdict if all gates pass:

`PASS_STATIC_INTERNAL_FIXED_POINT__EXTERNAL_VALIDATION_OPEN`

Do **not** use `FULL_PASS` while external validation remains open.

Record at minimum:

- exact ZIP filename
- ZIP SHA-256
- member count
- root HTML SHA-256
- baseline SHA-256
- mutation scope
- prior defect count = 82
- post-repair defect count = 0
- protected-authority integrity result
- complete gate summary
- independent audit result
- meta-audit result
- external gates still open
- mutation authority reset to NONE

---

# 6. Mandatory external-validation boundary

No static/headless/browser-emulation result may close:

- physical iPhone
- physical iPad portrait
- physical iPad landscape
- physical Samsung/Android
- installed-PWA update from v101.132
- installed-PWA close/reopen persistence
- true offline cold reopen
- exact live GitHub Pages byte binding
- representative VoiceOver
- representative TalkBack
- wide/public release decision

Update `REAL_DEVICE_QA_CHECKLIST.md` to v101.133 and include specific visual checks at representative repaired loci:

- Hour 8 P007
- Hour 8 P008
- Hour 8 P009
- the one Réflexions case
- at least one Promesses main case
- the corresponding Promesses Library mirror
- one linked LDC case
- `RELATED_HOUR_21.P073`
- `PART_III_MARY_SORROWS.BODY.P212`

At ordinary reading sizes, verify that repaired visual starts align with native paragraphs and that no natural wrapping/spacing regression is introduced.

---

# 7. Required package-local artifacts

The final v101.133 package/evidence must include or directly bind:

## Core package

- deployable application files
- current `version.json`
- current service worker/cache bindings
- package manifest
- hash manifest

## Authority/evidence

- M1 baseline identity
- raw text universe
- runtime boundary universe
- 82-case positive ledger
- 76-case unique ledger
- negative-control ledger
- baseline v101.132 negative-control result
- mutation-integrity result
- full alignment geometry result
- mutant sensitivity result
- source/selection preservation result
- highlight/note regression result
- accessibility-structure result
- inherited gate summary
- four-pass results
- deterministic Build A/B proof
- exact-reopen identity proof
- independent audit
- final meta-audit
- final post-freeze report
- final decision lock

## Current operational files

- `README.md`
- `scripts/EXECUTION_SPEC.md`
- `REAL_DEVICE_QA_CHECKLIST.md`
- `REAL_DEVICE_QA_RESULTS_TEMPLATE.csv`
- `metadata/current_tooling_inventory.json`
- `metadata/current_gate_map.json`

Every current operational file must identify v101.133, not an obsolete release.

---

# 8. Failure-handling rules

## 8.1 Do not silently broaden scope

If a defect requires:

- text correction;
- speaker re-adjudication;
- topology change;
- offset change;
- schema change;
- new continuity group;
- change to M1C001–M1C004;
- new content-specific exception;

STOP and obtain explicit approval.

## 8.2 Do not force expected counts

The expected 82/78/4/1,748 counts are reproduction targets.

If independent evidence contradicts them:

- preserve the discrepancy;
- identify its cause;
- update the fixed point only with direct evidence;
- do not manipulate the scanner to recover expected values.

## 8.3 No local ID patching

Do not hard-code the 82 IDs into production rendering logic.

The 82 ledger is a regression-control universe, not the implementation mechanism.

## 8.4 No source trimming

Forbidden:

- `.trimStart()`
- deleting leading U+0020 from source strings
- offset-shifting boundaries to jump over the space
- replacing ordinary spaces with zero-width Unicode characters in source text
- global change from `white-space: pre-wrap` to `white-space: normal`

## 8.5 No audit overclaim

A headless PASS proves only the tested invariant.

Do not infer:

- physical-device PASS;
- screen-reader PASS;
- installed-PWA upgrade PASS;
- true-offline PASS;
- live-origin binding PASS.

---

# 9. Success criteria

v101.133 may be internally locked only when all are true:

```text
immutable v101.132 identity                        VERIFIED

M1 raw-text universe                              REPRODUCED
M1 runtime synthetic-boundary universe            REPRODUCED
v101.132 negative control                         82 alignment FAIL
v101.132 clean controls                           0 unexpected FAIL

v101.133 canonical text changes                   0
v101.133 speaker adjudication changes             0
v101.133 topology/offset changes                  0
v101.133 schema changes                           0

speech-path prior failures                        0 remaining
LDC-path prior failures                           0 remaining
all 82 rendered prior failures                    82/82 repaired
unexpected new alignment failures                 0

source textContent preservation                   PASS
selection/source-offset preservation              PASS
highlights/notes regression                       PASS
accessibility-structure regression                PASS

display-segment clean controls                    PASS
cross-record clean controls                       PASS
strict glyph continuity                           PASS
all inherited v101.132 functional gates           PASS
primary presentation matrix                       PASS
independent presentation matrix                   PASS
service-worker/package logic                      PASS

mutant sensitivity                                PASS
four-pass prefreeze                               PASS
Build A == Build B                                BYTE-IDENTICAL
exact reopen member identity                      PASS
exact-reopen full gate rerun                      PASS
exact-reopen four-pass                            PASS
independent audit                                 PASS
final meta-audit                                  PASS

external physical/PWA/offline/accessibility gates OPEN
mutation authority after freeze                   NONE
```

---

# 10. Final deliverables

After successful lock, produce:

1. `L24H_v101133_GITHUB_DEPLOY_VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_R1_LOCKED.zip`
2. `FINAL_V101133_DECISION_LOCK.json`
3. `FINAL_POSTFREEZE_REPORT_V101133.md`
4. `FINAL_META_AUDIT_V101133.json`
5. independent exact-reopen audit
6. complete v101.133 evidence bundle
7. SHA-256 checksum file for the app ZIP and evidence bundle
8. updated full `state.md` making v101.133 the current internal/static authority
9. continuation package for a new conversation
10. exact GitHub deploy ZIP, unchanged from the locked byte-stream

Do not update the state document to call v101.133 current until the exact frozen ZIP has completed the final reopen, independent audit, meta-audit, and decision lock.

---

# 11. Exact continuation rule

After a successful v101.133 lock:

```text
CURRENT 24H INTERNAL/STATIC PACKAGE
  v101.133

TEXTUAL AUTHORITY
  unchanged from inherited v101.132/v101.126 fixed point

NEW TEXT OPERATIONS
  0

NEW SPEAKER ADJUDICATIONS
  0

NEW TOPOLOGY/OFFSET OPERATIONS
  0

FUNCTIONAL CHANGE
  renderer-only suppression of visual advance for one immediate U+0020
  at governed intra-record synthetic block boundaries

PRIOR V101.132 ALIGNMENT DEFECTS
  82 rendered occurrences

V101.133 EXPECTED REMAINING DEFECTS
  0

MUTATION AUTHORITY
  NONE

EXTERNAL VALIDATION
  OPEN

WIDE/PUBLIC RELEASE
  NOT AUTHORISED until the governing external release gates are explicitly closed
```

Any subsequent byte change requires a separately numbered successor. Never patch the locked v101.133 ZIP in place.
