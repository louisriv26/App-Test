# Les 24 Heures de la Passion — LDC Presentation-Projection Parity Repair
## Integrated evidence-gated no-regression execution script

**Target stage:** `24H-LDC-PRESENTATION-PROJECTION-PARITY-REPAIR`  
**Expected successor:** `v101.102` if unused; otherwise allocate the next unused version **before any edit**.  
**Date:** 2026-08-22

---

# 0. Governing objective

Repair the two post-audit defects in v101.101 by replacing the ad-hoc 24H direct-speech display logic with the **same architecture, distinctions and validation methodology used by the Livre du Ciel app**:

1. **semantic speaker information and visible presentation are separate layers**;
2. visible styling follows the **active outer speaking turn / presentation projection**, not raw nested semantic speaker labels alone;
3. redundant **outer** guillemets around validated continuous divine speech are hidden only in the display layer;
4. **meaningful nested, inline, reported and non-divine quotations remain visible**;
5. each validated visible divine direct-speech run starts as a new visible block/paragraph when preceded by narration or another turn;
6. narration or another turn following divine direct speech starts as a new visible block/paragraph;
7. turn continuity and quotation semantics are resolved **across canonical paragraph/record boundaries**, not by paragraph-local adjacency heuristics;
8. the renderer and Samsung/Android `Paragraphe` interaction model consume **one shared visible-paragraph topology**;
9. canonical devotional text, punctuation and stable offsets are preserved unless a separately evidenced speaker/presentation-data correction is explicitly authorised by this script;
10. no runtime heuristic may perform scholarly speaker adjudication in normal use: the scholarly/presentation decisions must be frozen into deterministic derived metadata during the build.

This is a **presentation/speaker-topology repair**, not a new corpus-editing stage.

---

# 1. Immediate baseline and status

Use **only** the exact immutable v101.101 package as the mechanical patch baseline:

```text
BASELINE ZIP
  L24H_v101101_GITHUB_DEPLOY_RA19B_DIRECT_SPEECH_DISPLAY_BOUNDARY_REPAIR_R1_LOCKED.zip

BASELINE SHA-256
  77f7577b20dc4bb06ba403bc97074e0f9326f7c37d6ed68a0b756018b2da476e

BASELINE APP
  v101.101

BASELINE STATUS FOR THIS STAGE
  FAIL_POST_AUDIT
```

The v101.101 ZIP is the newest mechanical baseline because it contains the v101.100 text-reconciliation corrections and v101.101 presentation work, but its prior `LIMITED_PASS_STATIC` conclusion is superseded for continued work by the minute-detail findings:

```text
POST_AUDIT_NESTED_QUOTATION_SEMANTICS = FAIL
POST_AUDIT_SAMSUNG_VISIBLE_PARAGRAPH_TOPOLOGY = FAIL
```

Do **not** patch v101.100, v101.99, a live deployment, a loose HTML copy, or an earlier local tree.

Before any edit:

1. recompute baseline ZIP SHA-256;
2. inventory all members, sizes and hashes;
3. extract into a new clean working directory;
4. prove `index.html` and `luisa_24_heures.html` are byte-identical;
5. parse current version/cache/storage/snapshot identities;
6. parse all protected data declarations and record their exact hashes and counts;
7. record the current v101.101 direct-speech metadata objects and runtime functions as **historical implementation evidence only**, not as semantic authority.

If the SHA, package identity or required baseline files do not match, **STOP — FAIL_BASELINE_AUTHORITY**.

---

# 2. Livre du Ciel methodology authority — mandatory

The repair must reproduce the **LDC presentation model**, not merely imitate its colours or remove guillemets.

## 2.1 Governing LDC methodological contracts

Use these LDC rules as the design authority:

```text
CANONICAL TEXT
  remains unchanged by presentation work.

SEMANTIC SPEAKER
  remains distinct from visible presentation speaker.

NESTED QUOTATION PRESENTATION
  visible font/colour follows the active outer speaking turn where the LDC
  presentation projection requires continuity.

OUTER GUILLEMETS
  redundant outer delimiters of validated continuous styled divine speech
  are hidden only in the normal reader/display layer.

MEANINGFUL QUOTATIONS
  nested/reported/inline quotations, quoted formulas/titles and non-divine
  direct speech remain visibly delimited.

DIRECT-SPEECH BLOCK START
  each validated visible divine direct-speech run starts as a new visual block.

POST-SPEECH NARRATION
  narration/another turn following that run starts as a new visual block.

CROSS-RECORD CONTINUITY
  outer-turn state and nested quotation semantics may depend on preceding
  records; paragraph-local logic is insufficient.
```

The LDC app has already demonstrated that raw semantic speaker comparison alone can produce false presentation conclusions, and that nested quotations must be projected through the active outer speaking turn.

## 2.2 Exact current LDC authority for 24H-derived material

For the **115 mapped LDC source blocks** inside 24H, bind to the exact governing LDC authority already recorded for this project:

```text
LDC PUBLIC VERSION
  Version 29

LDC TECHNICAL VERSION
  v2.19.29-R1B

LDC STAGE
  RA19B-MULTI-SOURCE-FLOW-ADJUDICATED

LDC FINAL DEPLOY ZIP
  LDC_v2.19.29-R1B_GITHUB_DEPLOY_RA19B_MULTI_SOURCE_FLOW_ADJUDICATED_LOCKED.zip

LDC ZIP SHA-256
  eb2fa6abce1525399547f469ad1c2d64e818ff8685fe11cc20a57571c59f92fc
```

Retrieve the exact LDC ZIP/state and its actual reader presentation implementation (`speech_model.js` / equivalent active runtime projection) before adjudicating LDC-derived speech presentation.

For LDC-derived passages, compare against the **actual LDC presentation projection**, not against raw semantic speaker rows and not against v101.101 suppression arrays.

If the exact LDC authority package or its active presentation implementation cannot be obtained or verified, **STOP BEFORE MODIFYING THE 24H APP — FAIL_SOURCE_EVIDENCE_MISSING**.

---

# 3. Exact authorised scope

This stage may change only what is necessary to make 24H use the LDC speech-presentation methodology correctly.

## 3.1 Authorised changes

1. Replace v101.101's adjacency-based guillemet suppression with a deterministic **presentation-projection-derived quote-display map**.
2. Replace fragmented speech-start/speech-end display rules with one deterministic **presentation turn/block map**.
3. Reconcile 24H visible divine-speech styling against the LDC presentation projection for every mapped LDC block.
4. Correct 24H divine styling-span metadata only where the authoritative projection proves the current presentation span is wrong.
5. Preserve or explicitly model non-divine direct speech such as Luisa's replies so it is not absorbed into divine styling.
6. Preserve meaningful nested/reported quotations inside a divine outer turn while retaining the outer divine presentation style where the LDC model requires it.
7. Make every validated visible `JESUS`, `MARY` and `FATHER` outer speech run start on its own visible paragraph/block when preceded by narration/another turn.
8. Make narration/Luisa/another turn following such a divine speech run start on its own visible paragraph/block.
9. Handle the above across canonical target boundaries and across RA19B flow JOINs.
10. Make Samsung/Android `Paragraphe` consume the **same visible-paragraph boundary model used by rendering**.
11. Generalise visible-paragraph targeting beyond LDC-only flow surfaces where a speech presentation boundary splits one legacy 24H paragraph.
12. Preserve Apple/iPad/iPhone exact-selection highlighting.
13. Rebuild only directly derived presentation/speaker-coordinate metadata that the proven repair requires.
14. Update app/cache/version identity, reports, manifests and state only after all relevant gates pass.

## 3.2 Explicitly out of scope

Do not alter:

- devotional wording merely for style;
- v101.100 approved text corrections;
- raw/canonical guillemet characters merely because they are hidden in the reader;
- paragraph IDs, Hour IDs, prayer IDs, stable refs or ordering;
- RA19B source-flow decisions (`paragraph_break`, `preserve_break`) except coordinate reprojection if a separately authorised metadata change mathematically requires it;
- internal subheadings;
- search wording/index semantics except mechanical rebuild required by an authorised text/offset change;
- update/PWA lifecycle logic except version/cache identity;
- navigation, reader layout, font controls, theme, favourites, notes, sharing or help unless exact wording must change to describe the repaired behaviour;
- storage schema unless absolutely required by the visible-paragraph interaction repair;
- user highlight ranges or notes through destructive migration;
- unrelated capitalization or editorial policy.

If any required repair would exceed this scope, **STOP — FAIL_SCOPE_EXPANSION**.

---

# 4. Protected baseline objects

Before editing, hash and parse at minimum:

```text
CORPUS
TEXT_LIBRARY
HOUR_LINKED_TEXTS
SPEECH_DATA
INTERNAL_SUBHEADINGS
SPEECH_END_VISUAL_BREAKS
LDC_LIBRARY_FLOW_LAYOUT
SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS
SPEECH_CROSS_RECORD_VISUAL_BREAKS
storage/snapshot constants
search/index target sets
```

Also preserve:

```text
paragraph IDs and order
24 Hour IDs
5 prayer identities
4 section identities
40 TEXT_LIBRARY identities
source maps
RA19B flow action types
highlight anchoring semantics
Apple exact-selection behaviour
Samsung stored-highlight persistence
Mon Espace records
user backup/export/import compatibility
```

Any protected-data drift must be either:

```text
A. explicitly authorised by this script,
B. proven necessary by the LDC presentation projection or deterministic coordinate reprojection,
C. fully ledgered before/after,
D. independently revalidated.
```

Otherwise: **FAIL_PROTECTED_DATA_DRIFT**.

---

# 5. Pre-edit hard gate — reconstruct the presentation truth first

**Do not modify the app until this entire section passes.**

Build a complete presentation ledger for every active renderable speech-bearing target across:

```text
24 Hours
reflections/subsections
5 prayers
4 sections
all active TEXT_LIBRARY items
all HOUR_LINKED_TEXTS routes
both Promesses et bienfaits surfaces
all 115 mapped LDC source blocks
```

## 5.1 Build one canonical target map

Reconstruct the actual runtime target universe exactly as the reader resolves it.

For every target record capture:

```text
target_id
surface/item/hour/section/library origin
canonical text
source/flow membership
active render route(s)
current speech spans
current RA19B boundary actions
current presentation-only boundaries
current highlight/selectable surface identity
```

Gate:

```text
all current SPEECH_DATA targets resolve
all offsets are valid
no overlaps unless schema explicitly permits them
all duplicate mirror surfaces are identified
```

## 5.2 Reconstruct semantic/presentation turns using the LDC method

For LDC-derived material, run the actual LDC presentation projection and align it word-for-word to 24H.

For all other 24H material, reconstruct speaking-turn state using the same conceptual model:

```text
semantic speaker / narrative role
outer active speaking turn
nested quotation depth/role
presentation speaker
quotation delimiter role
turn start
turn end
cross-record continuation
```

Use punctuation as evidence, **not sole authority**. Use explicit attribution/context such as:

```text
Il me dit / Jésus me dit / le Père dit / Marie dit
Je dis / je repris / je répondis
Il reprit / elle répondit
quoted formulas/titles
reported speech
nested speech
```

Where an LDC-derived passage exists, the exact LDC source/presentation model governs over a local heuristic.

If any material speaker/quotation boundary remains ambiguous or requires editorial judgement, **STOP BEFORE EDIT — FAIL_AMBIGUOUS_SPEAKER_OR_QUOTATION**.

## 5.3 Explicit regression fixture — Luisa must not be absorbed into Jesus

The ledger must explicitly resolve the class represented by:

```text
À l'instant, Il me dit : «Aurais-Tu ... ?» Je repris : «Non ! Et que cela ne soit jamais !»
```

Required semantic/presentation outcome:

```text
Jesus turn
  styled as Jesus
  outer wrapper eligible for display suppression

Je repris
  narration / turn transition

Luisa quotation
  NOT styled as Jesus merely because it follows a Jesus segment
  guillemets remain visible
```

Do not hard-code this one sentence; use it as a regression fixture for the general turn-state algorithm.

## 5.4 Exhaustive quotation-role classification

Every guillemet adjacent to or inside a speech-bearing target must receive one explicit classification:

```text
OUTER_DIVINE_OPEN_WRAPPER_HIDE
OUTER_DIVINE_CLOSE_WRAPPER_HIDE
MEANINGFUL_NESTED_QUOTE_KEEP
REPORTED_QUOTE_KEEP
NON_DIVINE_DIRECT_QUOTE_KEEP
QUOTED_FORMULA_OR_TITLE_KEEP
NARRATIVE_QUOTE_KEEP
UNRESOLVED
```

`UNRESOLVED > 0` is blocking.

Never infer `HIDE` from adjacency to a divine span alone.

## 5.5 Full presentation-run inventory

Build the cross-target visible run model first, then derive counts. Do not hard-code v101.101's `116`, `139`, `1`, `1,584` or the minute-audit `19/60/140` values as target outcomes.

For each run record:

```text
run_id
semantic source span(s)
presentation speaker
outer turn id
start target + offset
end target + offset
starts_after narration/other/divine continuation
ends_before narration/other/divine continuation
opening wrapper action
closing wrapper action
visible block start required
visible block end required
source evidence / LDC projection evidence
```

All runs must be accounted for before edits.

---

# 6. Target architecture — one LDC-style presentation projection

The repair must remove dual/triple sources of truth.

## 6.1 One governing derived presentation model

Create or generate one authoritative derived presentation map, conceptually equivalent to the LDC presentation projection.

It must be sufficient to derive:

```text
visible presentation speaker
outer-turn continuity
outer-guilllemets to hide
meaningful guillemets to keep
speech block starts
post-speech narrative block starts
cross-record turn continuity
visible paragraph boundaries
```

The exact object name may differ, but there must be **one governing derived model**.

Existing objects such as:

```text
SPEECH_END_VISUAL_BREAKS
SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS
SPEECH_CROSS_RECORD_VISUAL_BREAKS
```

may remain only if they are **deterministically generated outputs** of that one model. They must not remain separately hand-maintained authorities.

## 6.2 No normal-runtime scholarly heuristics

Do not make `getSpeechQuoteSuppressionRanges()` or any normal render path infer speaker scholarship from local punctuation at runtime.

The build must freeze the decisions into derived metadata.

Runtime may only:

```text
read validated derived metadata
clip it to the current rendered fragment
apply presentation styles
hide approved outer wrappers
insert approved visible block boundaries
```

If runtime still decides `hide/keep` using only regex adjacency to `SPEECH_DATA`, **FAIL_ARCHITECTURE_PARITY**.

## 6.3 Preserve canonical punctuation

Canonical text must continue to contain all original/approved guillemets.

Display hiding must be reversible and non-destructive.

For hidden outer wrappers:

- canonical offsets remain unchanged;
- text fingerprints remain tied to canonical text;
- highlight offsets remain valid;
- search authority remains canonical;
- copy/link/selection behaviour must be explicitly tested;
- screen-reader exposure must match the intended normal-reader presentation.

## 6.4 Presentation-speaker rule

For nested/reported quotations inside a continuous divine outer turn:

```text
semantic quoted speaker
  may differ

presentation speaker
  follows the active outer turn where the LDC model requires continuity

quotation punctuation
  remains visible because it is meaningful
```

Do not rewrite semantic speaker identity merely to obtain the desired colour.

For a real turn transition such as `Je repris`, terminate the divine outer turn before the Luisa turn.

## 6.5 Father parity

Apply the same architecture to `FATHER` as to Jesus/Mary in 24H:

- presentation styling based on validated outer Father turn;
- only redundant outer Father wrappers hidden;
- meaningful quotations inside the Father's speech remain visible;
- narration/Jesus-addressing text after the Father turn begins a new visible block.

The screenshot case ending at `créatures ensemble !` and continuing with `Mais Toi, ô mon Jésus...` is a mandatory regression fixture, not a one-off patch.

---

# 7. Shared visible-paragraph topology — renderer and Samsung must agree

The current defect exists because rendering gained speech-end boundaries that Samsung grouping does not consume.

Replace that split-brain model.

## 7.1 One visible-boundary union

Define the visible paragraph topology from the union of:

```text
A. source/RA19B ordinary paragraph boundaries
   action = paragraph_break

B. presentation block boundaries
   validated divine-speech start after narration/another turn
   validated narration/another turn start after divine speech
   equivalent cross-record presentation boundaries

C. structural reader boundaries already authoritative
   internal subheading/subsection boundaries where applicable
```

Explicitly **exclude** from paragraph splitting:

```text
RA19B preserve_break
zero-margin internal source breaks
pure technical storage-fragment boundaries
hidden guillemet positions
highlight mark boundaries
```

## 7.2 One topology resolver

Refactor so the renderer and Android/Samsung interaction logic use the same boundary source.

Do not leave:

```text
renderer = RA19B + speech boundaries
Samsung = RA19B paragraph_break only
```

A recommended shape is one shared resolver such as:

```text
getVisibleParagraphPieces(...)
getVisibleParagraphGroups(...)
```

or equivalent, consumed by both:

```text
rendering/rerender validation
Samsung tap-to-Paragraphe target construction
Mon Espace visual-paragraph grouping
copy/note/highlight target summaries
```

Do not create a second independent reimplementation of the same topology in Android code.

## 7.3 Non-LDC surfaces

Speech presentation boundaries can split a legacy paragraph outside `.ldc-flow-surface`.

Samsung/Android `Paragraphe` must therefore target the **actual visible paragraph** on those surfaces as well.

Do not fall back to “entire legacy paragraph” when the renderer visibly presents two paragraphs.

## 7.4 Existing user highlights

Do not destructively rewrite existing stored highlight ranges.

For existing `visual_paragraph` highlights created under older topology:

1. preserve the stored range bytes;
2. render them at the same canonical text ranges;
3. recompute only their presentation/group label where safe;
4. if an old group now spans multiple current visible paragraphs, do not silently truncate it;
5. treat it as an existing multi-paragraph range or mark it for non-destructive re-anchoring according to existing user-data policy;
6. no user data may disappear because topology changed.

If compatibility cannot be preserved without a storage migration/product decision, **STOP — FAIL_USER_DATA_MIGRATION_DECISION_REQUIRED**.

---

# 8. Implementation order — hard-gated, one item at a time

Do not implement several fixes and audit afterwards.

For every item use:

```text
PLAN
→ IMPLEMENT
→ EXACT DIFF
→ LINE-BY-LINE REVIEW
→ PROTECTED-DATA CHECK
→ BUILD-SCRIPT COMPLIANCE CHECK
→ TARGETED TEST
→ MINI-REGRESSION
→ INDEPENDENT RECHECK
→ PASS OR REVERT/REDO
```

Do not proceed to the next item until the current item passes.

## Item 1 — presentation authority extractor/auditor

Create the deterministic build-time evaluator that reconstructs the LDC-style presentation truth and emits the complete ledgers.

Gate:

```text
all speech-bearing targets covered
all LDC-derived mapped blocks bound to LDC projection
all quotation roles classified
all outer turns classified
0 unresolved cases
```

No app mutation before PASS.

## Item 2 — corrected visible divine presentation spans

Generate the 24H visible divine styling spans from the validated presentation projection.

For all mapped LDC blocks require **word-level parity with the actual LDC presentation speaker projection**.

If current `SPEECH_DATA` is used as the presentation-styling layer, update only proven mismatches and ledger every changed target/offset/speaker.

Gate:

```text
missing targets = 0
invalid offsets = 0
overlaps = 0
LDC word-level presentation mismatches = 0
false divine styling of Luisa/other turns = 0
```

## Item 3 — quote-display projection

Replace regex/adjacency authority with the validated quotation-role map.

Required results:

```text
outer divine wrappers hidden = all and only validated outer wrappers
meaningful nested/reported quotes visible = 100%
Luisa/other direct quote guillemets visible = 100%
quoted formulas/titles visible = 100%
canonical guillemet bytes changed = 0
```

Mandatory fixtures include, at minimum:

```text
Je repris : «Non ! ...»
Ponce Pilate dit : «Voici l'homme»
Ils crièrent : «Crucifie-Le... »
« J'ai soif » as a quoted formula/reference
«Sitio !» references
«Heureuse faute !»
quoted Divine-Will formulas/titles
cross-record opening wrappers
Father screenshot case
```

## Item 4 — speech block-start / post-speech block-end projection

Apply the LDC RA4C-style global rule:

```text
every validated visible JESUS/MARY/FATHER outer run starts as a new visible block
when preceded by narration/another turn;

narration/another turn following that run starts as a new visible block.
```

Resolve this across records and RA19B JOINs.

Do not use current v101.101 manual boundary lists as proof; regenerate from the projection.

Gate:

```text
styled divine runs still incorrectly inline = 0
required post-speech separations missing = 0
spurious separations inside continuous same turn = 0
canonical reconstruction mismatch = 0
```

## Item 5 — unified visible-paragraph resolver

Make the rendering topology and Samsung interaction topology consume the same validated boundary map.

Gate every visible group exhaustively, not by sampling.

For every group verify:

```text
correct canonical ranges
no omitted text
no duplicated text
no preserve_break split
all presentation block boundaries split
cross-record groups correct
```

## Item 6 — highlighting/rerender integration

Exercise add/recolour/remove over all relevant presentation classes.

Required invariants after each rerender:

```text
same visible paragraph topology
same RA19B action types
same divine presentation runs
same quote visibility classifications
same direct-speech block boundaries
same canonical text
```

## Item 7 — Mon Espace / journal / existing-highlight compatibility

Verify:

```text
new single visible-paragraph Samsung highlight
  → Paragraphe surligné

new highlight spanning >1 visible paragraph
  → Surlignage multi-paragraphes — N passages

existing pre-repair stored ranges
  → preserved, not silently truncated/deleted

contiguous technical fragments of one visible paragraph
  → no fake ellipsis

genuinely separate visible paragraphs
  → remain semantically separate
```

## Item 8 — version/evidence/package update

Only after Items 1–7 pass:

- set successor app version;
- set successor cache identity;
- update `version.json`, SW/runtime version references and README;
- regenerate reports/metadata from final candidate bytes;
- do not carry stale v101.101 PASS claims as current evidence.

---

# 9. Required exhaustive tests

## 9.1 Presentation projection tests

Across the complete active runtime target map:

```text
all presentation turns reconstructed
all LDC mapped blocks aligned to actual LDC projection
all styled divine runs accounted for
all turn starts/ends valid
all nested quotation roles resolved
all cross-record continuity resolved
```

Report exact counts from the final model.

## 9.2 Quotation semantics tests

Prove separately:

```text
outer wrappers hidden
meaningful nested guillemets retained
reported speech guillemets retained
Luisa direct-speech guillemets retained
quoted formulas/titles retained
no global «/» deletion
canonical guillemet count/hash unchanged unless an explicitly authorised corpus correction exists
```

Include a machine-readable ledger for every hidden guillemet range with its semantic reason.

## 9.3 Speech/narration boundary tests

For every visible divine run:

```text
preceded by narration/other turn
  → new visible block before run

followed by narration/other turn
  → new visible block after run

continuous same outer turn
  → no false break
```

Run across same-target, cross-target and RA19B JOIN boundaries.

## 9.4 Samsung/Android topology tests

Build the expected visible paragraph groups independently from the frozen presentation/boundary metadata, then compare against the actual interaction resolver.

For **every** visible group:

```text
first character tap
middle character tap
last character tap
```

must resolve to exactly that group.

Also test:

```text
whole-paragraph highlight creation
colour choice
persistence after reload
recolour
delete
Mon Espace reopening
copy/note target if supported
no Google Translate/Search native-selection overlay in Paragraphe mode
```

Static/headless checks may validate algorithms; physical Samsung remains separately `NOT_TESTED` until actually run.

## 9.5 Apple/iPad/iPhone regression

Verify statically/runtime-harness where possible:

```text
exact text selection still uses canonical offsets
selection may cross styled spans without offset drift
highlight survives reload
recolour/delete works
hidden outer wrappers do not corrupt range mapping
meaningful nested guillemets remain selectable/copyable as intended
```

Physical Safari remains `NOT_TESTED` unless actually run.

## 9.6 RA19B flow regression

Revalidate all active mapped LDC flow actions:

```text
paragraph_break count/action parity
preserve_break count/action parity
no preserve_break promoted to paragraph boundary
no source-flow action rewritten merely for presentation
presentation boundaries remain a separate derived layer
```

## 9.7 Duplicate/mirrored surface consistency

At minimum verify:

```text
Promesses et bienfaits section vs library mirror
linked LDC texts vs their canonical library source
all duplicate routes to the same text
```

For each mirror require equivalent:

```text
canonical text
presentation speaker projection
quote visibility
visible paragraph topology
search/anchor target validity
```

---

# 10. Full regression matrix

After all fixes pass individually, rerun a full package regression including at minimum:

```text
JavaScript syntax
service-worker syntax
24/24 Hours render
5/5 prayers render
4/4 sections render
40 TEXT_LIBRARY identities
HOUR_LINKED_TEXTS resolution
search target resolution
internal subheadings
speaker targets/offsets/overlaps
LDC presentation-speaker parity
RA19B flow fidelity
quote-display semantics
speech-start boundaries
post-speech boundaries
Samsung visible-paragraph grouping
Apple exact-selection path
highlight add/recolour/remove
Mon Espace
favourites
notes
read state
backup/export/import schema acceptance
navigation/back behaviour
version/update identity
manifest/PWA identity
static offline package references
no duplicate runtime DOM IDs in exhaustive renders
```

No regression may be inferred from unchanged code alone; execute the applicable test or record `NOT_TESTED`.

---

# 11. Independent four-pass audit

Use an auditor that did **not** implement the repair.

## Pass 1 — files vs build script

Verify:

- exact baseline hash;
- exact changed-file set;
- protected-file/hash parity;
- generated metadata provenance;
- no unapproved text/ID/order changes;
- version/cache/package identities.

## Pass 2 — runtime/package behaviour

Independently reconstruct:

- actual render target map;
- actual presentation turns;
- actual quote visibility;
- actual visible paragraph groups;
- actual Samsung target ranges;
- actual Apple range-offset invariants;
- RA19B flow actions;
- speech offsets and overlaps.

Do not rely on the build script's own summary files.

## Pass 3 — report claims vs evidence

Parse every active report line-by-line and compare each PASS/count/hash/current-authority statement to final package evidence.

Any unsupported PASS claim is:

```text
FAIL_REPORT_INTEGRITY
```

## Pass 4 — contradiction/stale scan

Search recursively across root, deploy, nested ZIPs, reports, scripts, metadata, README, HTML, SW, version files and manifests for:

```text
v101.101 as current authority
old successor attempt versions
old cache names
old package filenames
obsolete 116/139/manual-suppression claims presented as current authority
obsolete 1,584 current-topology claim if the final topology differs
RA18 current-authority claims
stale PASS / LIMITED_PASS claims
FAIL_POST_AUDIT contradictions
```

Historical/baseline references are allowed only when explicitly labelled historical/baseline.

---

# 12. Required evidence artifacts

The final candidate must contain or be accompanied by at least:

```text
reports/no_regression_fix_ledger.csv
reports/full_regression_matrix.csv
reports/presentation_turn_ledger.csv
reports/quotation_role_ledger.csv
reports/quote_suppression_ledger.csv
reports/speech_block_boundary_ledger.csv
reports/ldc_presentation_parity_report.md
reports/visible_paragraph_topology_report.md
reports/android_visible_paragraph_groups.csv
reports/protected_data_diff_report.md
reports/stale_reference_scan.txt
reports/root_deploy_consistency_report.md
reports/nested_zip_consistency_report.md
reports/report_claims_vs_evidence_audit.md
reports/real_device_status.md
metadata/hash_manifest.json
metadata/package_manifest.json
audit/independent_four_pass_audit.md
audit/final_reopened_zip_audit.md
audit/independent_reopened_zip_audit.md
FINAL_DECISION_LOCK.json
```

If an exact filename must differ because of established package conventions, record the mapping in the package manifest. Do not omit the evidence class.

---

# 13. Mandatory package-wide stale-reference scan

Scan recursively through:

```text
root files
deploy folder
nested ZIP contents
README files
version files
manifest files
reports
scripts
metadata
app HTML
deploy HTML
service worker
QA templates
```

Classify each hit as:

```text
CURRENT
HISTORICAL_ALLOWED
BASELINE_PROVENANCE
FAIL_STALE_ACTIVE
```

Any unexplained stale current-authority/version/report claim is blocking.

---

# 14. Root/deploy/nested consistency gate

Before writing the final ZIP and again after reopening it, verify:

1. root `index.html` and `luisa_24_heures.html` match their intended package contract;
2. deploy equivalents match;
3. nested ZIP equivalents match;
4. `APP_VERSION`, cache version, `version.json`, README and SW identities agree;
5. package manifest equals actual inventory;
6. hash manifest equals recomputed hashes;
7. reports describe the exact final package, not a pre-final candidate;
8. presentation metadata hashes/counts in reports match the final HTML;
9. the final state document does not retain the superseded v101.101 `LIMITED_PASS_STATIC` conclusion as current.

Any unexplained inconsistency = **FAIL**.

---

# 15. Deterministic build gate

Build the final successor twice independently from the same frozen inputs and script.

Require:

```text
ZIP A SHA-256 == ZIP B SHA-256
member inventory identical
member bytes identical
```

If deterministic reproduction fails, diagnose before final packaging. Do not claim release integrity from a non-reproducible build unless the exact nondeterministic fields are both necessary and explicitly excluded from deterministic scope with evidence.

---

# 16. Final immutable ZIP reopen gate

After the candidate ZIP is completely written and closed:

1. compute final ZIP SHA-256;
2. open it from disk into a brand-new audit directory;
3. extract every member;
4. extract every nested ZIP/package;
5. recompute all file hashes;
6. rerun manifests;
7. rerun syntax checks;
8. reconstruct the actual runtime target map;
9. independently reconstruct the presentation turn model;
10. independently classify visible/hidden quotation delimiters;
11. revalidate every visible divine speech run;
12. revalidate every speech-start/post-speech visual boundary;
13. independently reconstruct visible paragraph topology;
14. compare Android target resolver against every expected visible group;
15. revalidate all `SPEECH_DATA` targets/offsets/overlaps;
16. revalidate all RA19B flow actions;
17. rerun duplicate/mirror consistency;
18. rerun stale-reference scan;
19. rerun report-claims-vs-evidence audit;
20. verify required evidence files exist;
21. verify no report says PASS without direct proof.

Required result:

```text
FINAL_PACKAGE_REOPEN_GATE = PASS
```

Anything else makes the stage FAIL.

---

# 17. Separately implemented independent reopened-ZIP audit

A second auditor must be implemented separately and must **not** call the primary reopen-audit routine.

It must independently:

- extract the exact final ZIP again into another fresh folder;
- recompute package/hash manifests;
- parse canonical text and speaker/presentation metadata independently;
- reconstruct cross-record outer speaking turns independently;
- reconstruct nested quote semantics independently;
- verify that only outer wrappers are hidden;
- verify meaningful nested/reported/Luisa quotes remain visible;
- reconstruct all visible paragraph boundaries independently;
- verify Android groups against those boundaries;
- verify the Father screenshot class and `Je repris` class specifically;
- verify LDC 115-block presentation parity against the LDC authority;
- verify no protected text/ID/order drift;
- verify report integrity and stale references.

Required result:

```text
INDEPENDENT_REOPENED_ZIP_AUDIT_GATE = PASS
```

A second extraction using the same audit function is **not** independent enough.

---

# 18. Hard stop conditions

Stop immediately and do not proceed to the next item if any of the following occurs:

```text
baseline hash mismatch
missing LDC authority evidence
LDC source/presentation conflict that cannot be resolved
ambiguous speaker turn
ambiguous nested quotation role
editorial judgement required
unapproved canonical wording change
paragraph/stable-ID drift
unexplained speech offset change
word-level LDC presentation mismatch
meaningful quotation suppressed
outer wrapper left visible where projection says hide
spurious paragraph break inside a continuous outer turn
missing paragraph break at a real turn transition
RA19B preserve_break retyped
renderer/Android topology disagreement
existing user highlight loss/truncation
Apple exact-selection regression
search/anchor regression
report claim unsupported
stale active authority reference
manifest/hash mismatch
final reopen failure
independent reopen failure
```

On failure:

```text
STOP
→ diagnose exact cause
→ revert or correct the current item only
→ rerun that item's gates from scratch
→ repeat until PASS or safe revert
```

Record `redo_count` per fix.

---

# 19. Final decision lock

Write `FINAL_DECISION_LOCK.json` **last**, after both reopened-ZIP audits.

Decision logic:

```text
if FINAL_PACKAGE_REOPEN_GATE != PASS
  final_status = FAIL

else if INDEPENDENT_REOPENED_ZIP_AUDIT_GATE != PASS
  final_status = FAIL

else if PRESENTATION_PROJECTION_GATE != PASS
  final_status = FAIL

else if QUOTATION_SEMANTICS_GATE != PASS
  final_status = FAIL

else if VISIBLE_PARAGRAPH_TOPOLOGY_GATE != PASS
  final_status = FAIL

else if REPORT_INTEGRITY_GATE != PASS
  final_status = FAIL

else if physical iPhone/iPad/Samsung or live/offline/accessibility gates remain untested
  final_status = LIMITED_PASS_STATIC

else
  final_status = PASS
```

The assistant's final response must match the lock exactly.

Do not use `PASS_WITH_WARNINGS` to override any failed gate.

---

# 20. State-document update rule

Only after the final decision lock is written:

## If the successor passes static/reopen gates

Update the state document so the successor becomes the sole current editing baseline and record:

- exact ZIP/hash/version/cache;
- exact presentation-run counts;
- exact outer-wrapper hide counts;
- exact meaningful quotation retention counts;
- exact speech-start and post-speech boundary counts;
- exact current visible-paragraph topology count;
- exact Android topology parity result;
- exact LDC 115-block presentation parity result;
- protected data hashes;
- final reopen and independent reopen results;
- physical/live/offline gates as tested or `NOT_TESTED`.

The state must explicitly supersede v101.101's ad-hoc adjacency-based methodology.

## If the successor fails

Do not promote it.

Update the state/current handover to retain:

```text
v101.101 mechanical baseline
current status = FAIL_POST_AUDIT
blocking defects = nested-quotation semantics + visible-paragraph topology
successor attempt = FAILED / historical only
```

Do not leave `LIMITED_PASS_STATIC` as the current v101.101 conclusion after the new post-audit evidence.

---

# 21. Minimum mandatory regression fixtures

The final suite must include explicit fixtures for all of the following classes:

```text
A. Father speech → narration/Jesus-address continuation
   ending: "créatures ensemble !"
   continuation: "Mais Toi, ô mon Jésus..."
   expected: new visible paragraph after Father turn.

B. Jesus speech → "Je repris" → Luisa direct reply
   expected: Jesus turn ends; Luisa quote retains guillemets and is not Jesus-styled.

C. Jesus outer turn quoting Pilate/crowd
   expected: outer Jesus presentation continuity where LDC projection requires it;
   inner quotation guillemets remain visible.

D. Quoted formula/title inside divine speech
   examples: "J'ai soif", "Sitio !", "Heureuse faute !", Divine-Will formulas.
   expected: meaningful guillemets remain visible.

E. Cross-record opening wrapper
   narration/attribution ends in one target, divine speech starts in next.
   expected: only redundant outer wrapper hidden.

F. Cross-record post-speech narration under RA19B JOIN
   expected: presentation boundary overrides visual JOIN without rewriting RA19B flow authority.

G. Continuous same divine outer turn spanning canonical records
   expected: no spurious new paragraph merely because storage target changes.

H. Nested semantic speaker differs from outer presentation speaker
   expected: semantic identity preserved; outer presentation continuity follows LDC projection;
   nested guillemets visible.

I. Samsung tap inside both sides of every speech-derived visible split
   expected: each side resolves to its own actual visible paragraph.

J. Apple exact selection across/near hidden outer wrapper
   expected: canonical offsets/highlights remain stable.
```

These fixtures are minimums; they do not replace exhaustive scans.

---

# 22. Success criteria

The stage is technically successful only if the exact final reopened package proves all of the following:

```text
1. 24H uses an LDC-style presentation projection, not local quote adjacency heuristics.
2. Every mapped LDC block has zero word-level presentation-speaker mismatch vs current LDC authority.
3. All validated divine outer wrappers are hidden in normal reader presentation.
4. No meaningful nested/reported/Luisa/quoted-formula guillemet is incorrectly hidden.
5. Every validated visible JESUS/MARY/FATHER run begins at the correct visible block boundary.
6. Every narration/other turn following divine speech begins at the correct visible block boundary.
7. Continuous same outer turns are not spuriously split.
8. Canonical text and punctuation remain intact except separately proven/authorised metadata corrections.
9. Renderer and Samsung/Android share one visible-paragraph topology.
10. Every Samsung visible group resolves exactly to its rendered paragraph.
11. Apple exact-selection behaviour remains intact in executed checks.
12. RA19B paragraph_break/preserve_break authority remains intact.
13. Existing user data is not lost or silently truncated.
14. Primary reopened-ZIP audit passes.
15. Separately implemented independent reopened-ZIP audit passes.
16. Report-integrity and stale-reference gates pass.
17. Final response matches the final decision lock.
```

If static/package gates pass but exact physical iPhone/iPad/Samsung, installed-PWA, live-origin, true-offline and accessibility validation remain open, the highest permitted final status is:

```text
LIMITED_PASS_STATIC
```

---

# 23. Governing principle

```text
Do not fix guillemets as punctuation.
Fix the speaking-turn model.

Do not fix paragraph breaks as CSS.
Fix the presentation topology.

Do not give Samsung a second interpretation of the page.
Make interaction consume the same visible structure the reader renders.

Canonical text is the source layer.
Semantic speaker data is the meaning layer.
Presentation projection is the reader layer.
User interaction anchors to the reader's actual visible topology.

A fix is not done unless the exact final ZIP proves all four layers remain coherent.
```
