# Les 24 Heures de la Passion — v101.105 Native-24H Paragraph + LDC Semantic Hybrid Presentation Repair
## Integrated hard-gated no-regression execution specification

**Date:** 23 August 2026  
**Target version:** `v101.105`  
**Target stage:** `NATIVE_24H_PARAGRAPH_LDC_SEMANTIC_HYBRID_PRESENTATION_R1`  
**Execution mode:** strict, evidence-gated, minimal-diff, stop-on-failure  
**Release ceiling before physical-device validation:** `LIMITED_PASS_STATIC`

---

# 0. Governing decision — freeze this before execution

The target architecture is now fixed as:

> **Native 24H visual paragraph presentation + LDC semantic quotation/speaker intelligence + one shared renderer/Samsung visible-paragraph topology.**

This supersedes the v101.102/v101.103 policy that mechanically created a new presentation paragraph at each validated divine-speech start.

The repair is **not** a return to old speech heuristics. It must retain the semantic improvements introduced by the LDC projection work while restoring the visual paragraph rhythm of the validated 24H presentation.

The final model must obey all three principles simultaneously:

1. **Visual paragraph authority:** use the v101.101/native-24H visual topology as the paragraph witness.
2. **Speaker/quotation authority:** use the validated v101.103 LDC-derived semantic presentation model for speaker styling and quote-role decisions.
3. **Interaction authority:** rendering, Samsung `Paragraphe`, highlighting persistence and Mon Espace must resolve the **same final visible-paragraph topology**.

No implementation shortcut may sacrifice one principle to satisfy another.

---

# 1. Exact authority hierarchy and input freeze

## 1.1 Sole executable editing baseline

Use only:

```text
L24H_v101103_GITHUB_DEPLOY_DIVINE_QUOTE_PRESENTATION_REGRESSION_REPAIR_R1_LOCKED.zip
SHA-256 = d08fa70a4931f8c2e997bc8bae46a8292ed9b14725346727852361a84cfdb664
```

Required external state/evidence:

```text
CURRENT_STATE_AND_HANDOVER_v101103_UPDATED_2026-08-22.md
v101103_EXTERNAL_RELEASE_EVIDENCE.zip
```

Before any edit, independently verify that the external evidence records:

```text
FINAL_PACKAGE_REOPEN_GATE = PASS
INDEPENDENT_REOPENED_ZIP_AUDIT_GATE = PASS
APPWIDE_TERMINAL_REGRESSION_GATE = PASS
final_status = LIMITED_PASS_STATIC
```

If any of these facts cannot be proved against the exact v101.103 SHA above: **STOP — FAIL_BASELINE_AUTHORITY**.

## 1.2 Native 24H visual-topology reference — read-only witness

Use the exact validated v101.101 package only to reconstruct the visual paragraph topology that existed before the v101.102 blanket divine-speech-start projection:

```text
L24H_v101101_GITHUB_DEPLOY_RA19B_DIRECT_SPEECH_DISPLAY_BOUNDARY_REPAIR_R1_LOCKED.zip
SHA-256 = 77f7577b20dc4bb06ba403bc97074e0f9326f7c37d6ed68a0b756018b2da476e
```

Its role is strictly:

- paragraph/topology witness;
- speech-end presentation-boundary witness;
- prior native 24H rendering witness.

Do **not** copy its old quote-suppression heuristics or revert v101.103 semantic speaker/quotation logic.

Expected v101.101 speech-end presentation evidence, to be re-derived and verified rather than merely assumed:

```text
same-target divine-speech → narration continuations = 139
cross-record display-only speech-end breaks = 1
```

If the freshly derived witness does not reconcile with the validated v101.101 evidence: **STOP — FAIL_NATIVE_TOPOLOGY_WITNESS**.

## 1.3 LDC semantic/flow authorities — read-only

Latest implementation authority:

```text
LDC Version 31 / v2.19.31-R1B / RA19D
SHA-256 = b91aabf84803685cb5a86379c2a76c6239c2882bc1fa8b4277479f978c025441
```

Protected corpus/flow authority:

```text
LDC Version 29 / v2.19.29-R1B / RA19B
SHA-256 = eb2fa6abce1525399547f469ad1c2d64e818ff8685fe11cc20a57571c59f92fc
```

RA19B source-backed flow decisions remain authoritative. This stage must not rewrite them.

## 1.4 v101.104 — forensic evidence only, never an editing baseline

The unvalidated v101.104 candidate is:

```text
L24H_v101104_GITHUB_DEPLOY_CROSS_RECORD_QUOTE_EDGE_PRESENTATION_REPAIR_R1_LOCKED.zip
SHA-256 = c56edea1751f6a64fb954f5448ada849a8c5bbf5b17b6144bd14757e275220e5
```

It may be inspected only to understand the failed direction and its discovered edge-case inventory.

Do **not**:

- use v101.104 as the source tree;
- copy its generic `MOVE_VISUAL_BOUNDARY_BEFORE_OPENING_GUILLEMET` policy;
- treat its quote-edge boundary relocations as authoritative;
- inherit its package/evidence status.

All final decisions must be re-derived from v101.103 + v101.101 + the governing semantic/flow authorities.

## 1.5 User visual evidence — regression authority

Treat the following physical-iPad screenshots as mandatory regression evidence, not as styling suggestions:

```text
1.PNG       SHA-256 b12ad05cc13b7516ab22819a9b207089563b855e59dd057ac63914cc5ab610db
2.PNG       SHA-256 e3c79710ecd3a312d9c4c62202f55287e5a6962f3a6027080386fbb7183ff0b2
IMG_4531.PNG SHA-256 c95b5b41e073920658922200aea37f115c8cef974a73a92f027bf482d38f695f
IMG_4532.PNG SHA-256 ec127ecfb7068073945f175ffad3f200273756d4a1c6da20273067d369682966
IMG_4533.PNG SHA-256 1dc7120b4281c8e286e3fc1505d3a5a45cef11420163d38cdb909663b67c564c
IMG_4534.PNG SHA-256 24256dcf6013decd40db1496be825b9417c47aacf41b82c3dfe08b5fe0c36c72
```

The user decision of 23 August 2026 is locked:

> **Retain native 24H paragraph presentation; retain LDC semantic quotation/speaker intelligence; retain shared Samsung/render topology.**

Do not reopen that product decision during execution unless a source conflict makes it impossible to implement safely; if so, stop for explicit user adjudication.

---

# 2. Non-negotiable presentation contract

The build script must encode these rules explicitly and generate a machine-readable decision ledger proving how each rule was applied.

## 2.1 Canonical text is immutable

Presentation logic may style, suppress visually redundant wrapper delimiters, join governed fragments, or insert approved visual boundaries, but it must not alter canonical devotional text.

The exact text reconstructed from the rendered target must equal the canonical target after presentation-only nodes are normalized away.

No source character may be silently deleted, added, reordered or editorially rewritten.

## 2.2 Source/native paragraph rhythm is primary

A speaker change is **not by itself** a paragraph boundary.

A new visible paragraph may exist only because it is supported by one of these authorities:

1. the v101.101/native 24H visual topology;
2. an RA19B `paragraph_break` / governed source-backed visual boundary;
3. a validated internal subheading/source structural boundary already present in the protected app;
4. an already validated v101.101 divine-speech-end → resumed-narration display boundary.

One narrow corrective overlay is also authorized: if the native/storage topology places a structural boundary **between a visible opening guillemet and the first lexical content of that same quotation**, or **between the final lexical content and its visible closing guillemet**, remove that internal quote-edge boundary so the punctuation and quotation remain one visual unit. Record every such removal as `QUOTE_EDGE_INTEGRITY_JOIN`. Do not move the boundary elsewhere merely to preserve the same paragraph count.

A storage record boundary, JSON fragment boundary, speech offset, quote edge, or LDC source-PID boundary is **not** independently sufficient to create a visual paragraph.

## 2.3 Divine speech start — restored native 24H rule

For Jesus, Mary or the Father:

```text
narration/attribution + divine direct speech
```

must remain in the same visual paragraph **unless the native/source topology already contains a genuine paragraph boundary there**.

Therefore this is valid and normally preferred:

```text
... Jésus me dit : [JESUS STYLE] Ma fille, ...
```

and this must no longer be generated mechanically:

```text
... Jésus me dit :

[JESUS STYLE] Ma fille, ...
```

No `presentation_break` may be created solely because a `JESUS`, `MARY` or `FATHER` run begins.

## 2.4 Redundant outer divine guillemets remain hidden

Retain v101.103 semantic quote-role adjudication.

Hide only guillemets proven to be redundant outer wrappers around validated divine direct speech.

Canonical characters remain present for offset fidelity and must continue to be representable/reconstructable.

Do not restore the v101.101 adjacency heuristic.

## 2.5 Divine speech end → narration

Preserve the validated v101.101/native-24H rule:

When a divine speaking turn ends and Luisa/narration/another non-divine continuation resumes, the validated speech-end presentation boundary remains a new visible paragraph where v101.101 established it.

This includes the validated cross-record display-only speech-end boundary that overrides an RA19B JOIN visually without altering the RA19B decision.

Do not extend this rule to every speaker transition generically.

## 2.6 Luisa and other uncoloured visible quotations

Luisa/OTHER/CONFESSOR/ANGEL visible quotations remain normal prose unless another established presentation style explicitly applies.

The presence of a visible opening guillemet does not create a paragraph.

Attribution + opening guillemet + quoted words remain in the same native visual paragraph when that was the v101.101 topology.

For the IMG_4532 regression class, the attribution, visible opening guillemet and first quoted words must form one visual paragraph unit:

```text
... je me disais : « Mon Jésus, je veux recevoir l'absolution dans Ta Volonté.» ...
```

If v101.101/storage structure places a boundary after that opening `«`, remove that internal quote-edge boundary as `QUOTE_EDGE_INTEGRITY_JOIN`; **do not relocate it before the guillemet**. The later Jesus speech must follow whatever paragraph boundary the native/source witness independently supports; no boundary may be created solely because Jesus begins.

Do not implement the v101.104 generic policy of moving a visual boundary before visible opening guillemets.

## 2.7 Meaningful/nested quotations stay visible

Retain v101.103 exact semantic quote roles.

Meaningful visible quotations include, at minimum:

```text
«Voici l'homme» / «Voici l'Homme !»
«Crucifie-Le...»
« J’ai soif » when quoted/referred to
«le Tout»
Seven Words headings
scriptural nested quotations
reported human quotations
hypothetical quotations
Luisa's own direct quotation
personified/formula quotations where already adjudicated KEEP
```

A meaningful quote may never be hidden merely because it overlaps or touches `SPEECH_DATA`.

## 2.8 Nested quotation presentation speaker

Retain the LDC-derived distinction:

```text
semantic speaker != presentation speaker
```

A nested human quotation inside Jesus' active discourse may remain Jesus-styled.

A quote of Jesus inside Luisa's active discourse must not mechanically switch the surrounding discourse to Jesus styling unless the governing presentation projection explicitly identifies a true outer Jesus turn.

No raw semantic-speaker recolouring is permitted.

## 2.9 Visible quote edge integrity

For every visible quotation:

- no presentation break may occur **after the opening guillemet and before its first quoted lexical content**;
- no presentation break may occur **before the closing guillemet and after its final quoted lexical content**;
- no opening or closing guillemet may become an orphan visual paragraph;
- normal browser wrapping must not strand an opening guillemet by itself.

Do **not** solve ordinary line wrapping by changing canonical text.

If native Unicode spacing is insufficient at a cross-fragment edge, first prefer an inline presentation wrapper (`white-space: nowrap` or equivalent) that contains the existing opening guillemet + existing spacing + first lexical token without changing `textContent` or offsets. Any such runtime change requires the expanded renderer/selection regression gate in §8.7 and must be separately justified.

## 2.10 Internal subheaders and lists

Preserve the already validated internal-subheading model and all restored source-backed headings.

Do not merge headings back into body prose, re-number them as ordinary paragraphs, or alter the Seven Words heading quotation semantics.

Preserve genuine source/list rhythm; do not globally reinterpret dashes or line starts.

## 2.11 One topology for display and Samsung

The final visible paragraph graph must be shared by:

- reader rendering;
- Samsung/Android `Paragraphe` selection;
- whole-visible-paragraph highlight grouping;
- recolour/delete;
- Mon Espace paragraph labelling.

No secondary Samsung-only paragraph inference is allowed.

## 2.12 Apple selection remains exact-range

Do not alter iPhone/iPad/desktop exact-text selection semantics.

Presentation nodes must not shift canonical selection offsets, corrupt stored highlights, or convert exact selections into whole-paragraph selections.

---

# 3. Protected declarations and behaviour

Before modification, parse and hash the exact v101.103 declarations/functions. Preserve them byte/source-identically unless explicitly named as an allowed derived change.

## 3.1 Protected data declarations

```text
CORPUS
TEXT_LIBRARY
HOUR_LINKED_TEXTS
SPEECH_DATA
INTERNAL_SUBHEADINGS
DISPLAY_SEGMENTS
CONTINUITY_GROUPS
LDC_LIBRARY_FLOW_LAYOUT
```

Also protect:

```text
paragraph IDs and order
Hour/prayer/library IDs
approved v101.100 text corrections
RA19B flow actions and coordinates
H19/H21 explicit French speaker adjudications
storage schema
personal snapshot schema
existing saved-highlight bytes/data model
favourites/notes state model
PWA identity: manifest id/scope/start_url
```

## 3.2 Protected runtime behaviour

Unless a separately justified quote-edge inline wrapper is unavoidable, runtime JS/CSS functions should remain identical to v101.103 after normalizing generated constants and version/cache identity.

Protect at minimum:

```text
Apple selection/highlighting code
Samsung paragraph-mode interaction code
highlight add/recolour/delete persistence
Mon Espace reconstruction
search
navigation/back stack
font controls
theme/dark mode
help/modal behaviour
export/import
update/Actualiser logic
service-worker strategy
scroll/orientation logic
internal subheader renderer
```

## 3.3 Allowed derived changes

The first implementation attempt must be **data/projection-only**.

Allowed:

```text
SPEECH_PRESENTATION_PROJECTION.breaks
VISIBLE_PARAGRAPH_TOPOLOGY.local_breaks
VISIBLE_PARAGRAPH_TOPOLOGY.cross_record_breaks
other purely derived topology metadata required to reproduce the v101.101 visual witness
version/cache/stage identity
reports, ledgers, metadata and manifests for v101.105
```

Keep v101.103 `runs`, `hidden`, quote roles and explicit `presentation_speaker` adjudications unchanged unless the pre-edit semantic audit proves a contradiction.

If the target cannot be achieved without changing renderer JS/CSS, **STOP before doing so** and issue `FAIL_SCOPE_ESCALATION_REQUIRED` with exact proof. Do not silently broaden scope.

---

# 4. Hard-stop conditions before any edit

Stop immediately if any condition below is true:

1. v101.103 ZIP hash mismatch.
2. v101.101 witness ZIP hash mismatch.
3. required LDC authority hashes mismatch or are unavailable.
4. root `index.html` and `luisa_24_heures.html` differ within either baseline.
5. external v101.103 reopen evidence cannot be tied to exact SHA `d08fa70...db664`.
6. protected declaration hashes differ unexpectedly between the extracted baseline and recorded v101.103 state.
7. v101.101 and v101.103 canonical render targets cannot be mapped 1:1 by stable ID and exact text.
8. any canonical text difference exists between v101.101 and v101.103 that prevents a direct topology witness comparison and cannot be explained by already-approved lineage.
9. H19/H21 user-adjudicated speaker overrides are missing or changed.
10. the semantic quote-role ledger contains unresolved roles.
11. native topology reconstruction is ambiguous for any affected target.
12. implementing the hybrid requires a new editorial/source decision.
13. a required test cannot be implemented without materially changing production code.
14. any per-item gate fails and cannot be corrected or reverted cleanly.

No app modification is permitted past a failed pre-edit gate.

---

# 5. Phase A — baseline freeze and evidence reconstruction

## A1. Fresh extraction

Extract v101.103, v101.101 and both LDC authorities into separate new folders.

Do not reuse prior extracted folders.

Record:

```text
file path
size
SHA-256
ZIP member count
root HTML SHA-256
service-worker SHA-256
manifest/version hashes
```

## A2. Parse actual runtime declarations

Do not trust report counts alone.

Parse from HTML using a parser capable of handling the exact JavaScript literal syntax:

```text
CORPUS
TEXT_LIBRARY
HOUR_LINKED_TEXTS
SPEECH_DATA
INTERNAL_SUBHEADINGS
DISPLAY_SEGMENTS
CONTINUITY_GROUPS
LDC_LIBRARY_FLOW_LAYOUT
SPEECH_PRESENTATION_PROJECTION
VISIBLE_PARAGRAPH_TOPOLOGY
explicit speaker-presentation adjudication map
```

Validate all declared targets and offsets against the actual canonical render-target map.

## A3. Build v101.101 native visual-topology witness from runtime behaviour

Do **not** infer the native topology by subtracting v101.102/v101.103 breaks heuristically.

Define a **visual paragraph** structurally from the reader DOM/topology, not from ordinary browser soft line wrapping. Viewport-dependent line wrapping must never be mistaken for paragraph topology.

Run the actual v101.101 renderer in Chromium and extract the full visible-paragraph graph for:

```text
all 24 Hours
all visible/non-group TEXT_LIBRARY items
all Promesses/Benefits surfaces
all linked LDC flow surfaces
all internal-subheading surfaces
```

For each visible paragraph write:

```text
surface_id
ordered_visual_paragraph_index
source target IDs contributing to it
canonical start/end offsets per target
inter-record joins
boundary before/after
boundary origin if determinable
visible normalized text
canonical reconstructed text hash
```

Output:

```text
reports/v101101_native_visual_topology_witness.json
reports/v101101_native_visual_topology_witness.csv
```

Reconcile the witness with v101.101 validated counts, including the 139 same-target divine-speech-end boundaries and 1 cross-record display-only speech-end boundary.

If runtime witness and recorded v101.101 evidence disagree: stop.

## A4. Build v101.103 semantic presentation witness

Extract, without changing:

```text
all presentation runs
all hidden quote-wrapper ranges
all quote roles
all explicit presentation-speaker overrides
all 2,197 SPEECH_DATA target mappings / 3,293 segments
```

Output:

```text
reports/v101103_semantic_presentation_witness.json
reports/v101103_quote_role_witness.csv
```

Require:

```text
unresolved quote roles = 0
H19 explicit Luisa override present
H21 Jesus + Luisa split override present
```

## A5. Build a complete hybrid decision ledger before editing

For every v101.103 presentation target, enumerate each current v101.103 presentation break and every relevant v101.101 native/storage boundary and classify it as:

```text
NATIVE_SOURCE_BOUNDARY_KEEP
V101101_SPEECH_END_BOUNDARY_KEEP
QUOTE_EDGE_INTEGRITY_JOIN
V101102_PLUS_DIVINE_START_BOUNDARY_REMOVE
OTHER_EXISTING_BOUNDARY_REQUIRES_PROOF
```

For cross-record presentation breaks, use the same classification.

Each ledger row must contain:

```text
target / prev_id / next_id
offset if local
v101.101 visual-topology evidence
v101.103 break evidence
RA19B flow action if applicable
speaker before / speaker after
quote role around boundary
final action KEEP/REMOVE
reason
evidence path
```

Output:

```text
reports/hybrid_boundary_decision_ledger.csv
```

**Hard gate:** every v101.103 presentation break must have exactly one final decision supported by witness evidence. No catch-all/default decisions.

---

# 6. Phase B — construct the hybrid topology without broad runtime rewrite

## B1. Hybrid projection rule

Construct successor `SPEECH_PRESENTATION_PROJECTION` as:

```text
runs   = v101.103 semantic presentation runs, unchanged
hidden = v101.103 semantically adjudicated hidden wrapper ranges, unchanged
breaks = only boundaries supported by the v101.101 native visual-topology witness
```

No break may survive merely because a divine run begins.

## B2. Shared final topology

Regenerate `VISIBLE_PARAGRAPH_TOPOLOGY` from the same approved hybrid boundary ledger.

There must be no separate renderer topology and Samsung topology.

Expected presentation-specific result should reconcile to the v101.101 witness; do not hardcode counts without independently proving them.

If the reconstructed witness confirms the previously validated numbers, expected presentation-only speech-end topology is:

```text
same-target speech-end offsets = 139
cross-record speech-end pairs = 1
```

Any difference requires an explicit ledger explanation and hard-stop for review before packaging.

## B3. Explicitly delete the v101.102 blanket divine-start rule

Search production code/build scripts/reports for logic equivalent to:

```text
if divine speech begins -> insert presentation break
```

The final build must prove there is no active rule that creates a paragraph **solely** from speech-start status.

A source/native boundary may still coincide with a divine speech start; such a boundary must be attributed to the source/native topology, not to the speaker transition.

## B4. Do not inherit v101.104 quote-edge relocation

The build must not create generic boundaries before visible opening guillemets.

For the 138 v101.104 forensic trailing-opening cases, rebuild their final display from native v101.101 topology + v101.103 semantic quote roles.

Produce:

```text
reports/quote_edge_hybrid_reconciliation.csv
```

Each row must state whether the final quote edge is:

```text
INLINE_NATIVE
SOURCE_BOUNDARY_BEFORE_QUOTE
HIDDEN_DIVINE_WRAPPER
OTHER — explicit proof required
```

No `MOVE_VISUAL_BOUNDARY_BEFORE_OPENING_GUILLEMET` generic action may remain.

## B5. Minimal-diff code gate

After regenerating constants and version identity, normalize these allowed differences and compare the entire runtime HTML against v101.103.

Expected:

```text
all unrelated HTML/CSS/JS bytes = identical
```

A topology-only `QUOTE_EDGE_INTEGRITY_JOIN` is still a derived-data change and does not authorize a broad renderer rewrite.

If any unrelated function/style block changes, stop and inspect line-by-line.

---

# 7. Mandatory per-change cycle

For each implementation item B1–B5:

```text
PLAN
→ IMPLEMENT ONE ITEM ONLY
→ EXACT DIFF
→ LINE-BY-LINE REVIEW
→ BUILD-SCRIPT COMPLIANCE CHECK
→ TARGETED TEST
→ MINI-REGRESSION
→ INDEPENDENT RECHECK
→ PASS OR REDO/REVERT
```

Do not begin the next item while the current item is not evidence-PASS.

For each item record:

```text
item_id
files changed
exact lines/blocks changed
before/after hashes
reason
protected areas checked
targeted test result
mini-regression result
independent result
redo_count
final item status
```

Output:

```text
reports/no_regression_fix_ledger.csv
```

---

# 8. Phase C — mandatory presentation regression matrix

The following gates are blocking.

## 8.1 User screenshot fixtures — exact required outcomes

### G-PRES-001 — original H20 direct Jesus words (`PASSION24.HOUR.20.P016`)

Required:

- canonical `« ... »` remain in source/offset model;
- redundant outer divine wrappers are visually hidden;
- Jesus styling begins exactly at the first spoken character;
- **no new visual paragraph at Jesus-speech start unless the v101.101 witness already has one**;
- visual result follows the native-24H form:

```text
... après le péché : Viens dans mes Bras que Je te pardonne. Le sceau de mon Pardon est mon Sang.
```

with only the direct words styled as Jesus.

### G-PRES-002 — IMG_4532 Luisa quotation (`RELATED_HOUR_20` P015→P016)

Required:

- the visible sequence `je me disais : « Mon Jésus...` is one visual paragraph unit;
- `«` remains visible;
- no paragraph break exists after `«` before `Mon Jésus`;
- if such a native/storage boundary exists, remove it as `QUOTE_EDGE_INTEGRITY_JOIN` rather than moving it before `«`;
- Luisa quotation stays normal prose;
- the following Jesus speech receives Jesus styling but does **not** create a new paragraph solely because Jesus begins; its paragraph position must follow independent native/source topology evidence;
- any later validated divine-speech-end → narration boundary follows the v101.101 witness.

### G-PRES-003 — `Ce matin ... Jésus m'a dit : « / Ma fille, Je t'apporte...` (`RELATED_HOUR_20` P020→P021)

Required:

- opening wrapper hidden;
- `Ma fille...` Jesus-styled;
- attribution and Jesus words follow native 24H paragraph topology — no mechanical divine-start block.

### G-PRES-004 — `Il m'embrassa et Il poursuivit : « / Étant dans Ma Volonté...` (`RELATED_HOUR_20` P022→P023)

Same rule as G-PRES-003.

### G-PRES-005 — `mon Jésus me dit : « / Ma fille, J'ai éprouvé...` (`RELATED_HOUR_20` P030→P031)

Same rule as G-PRES-003, while preserving genuine nested `«peine, pardon»` visibly inside Jesus styling.

## 8.2 Exhaustive divine-start regression

For every Jesus/Mary/Father presentation run in all 2,197 targets:

- determine whether a v101.101/native visual boundary exists immediately before its start;
- if not, final DOM must not contain a presentation-only block boundary there;
- if yes, final DOM may contain the boundary but its evidence origin must be source/native, not speech-start inference.

Output all exceptions. Expected unexplained exceptions: **0**.

## 8.3 Exhaustive visible-quote regression

For every one of the 1,026 v101.103 quotation events:

Verify:

```text
role unchanged from approved v101.103 semantics
hidden iff role is an adjudicated outer divine wrapper
visible KEEP quote remains visible
no break after opening guillemet before quoted content
no break before closing guillemet after quoted content
no orphan guillemet DOM block
```

At minimum explicitly retain fixtures:

```text
«Voici l'homme» / «Voici l'Homme !»
«Crucifie-Le...»
« J’ai soif »
«le Tout»
Seven Words headings
```

## 8.4 Cross-record quote-edge audit

Re-run the app-wide stored-record edge scan, including every record ending with an opening guillemet or beginning/ending inside a visible quotation.

Do not use storage-record boundaries as paragraph authority.

For each edge verify the final visual result against v101.101 topology.

Expected IMG_4532-class failures: **0**.

## 8.5 Speaker-style continuity and leakage

For every presentation run:

- exact speaker class matches v101.103 semantic presentation witness;
- narrator attribution remains outside styled speech where appropriate;
- nested quote does not incorrectly change presentation speaker;
- no styled speech leaks into resumed narration;
- no unstyled hole appears inside one continuous active presentation turn unless source/native paragraph structure legitimately separates blocks.

H19/H21 explicit overrides must be tested individually.

## 8.6 Full canonical-text reconstruction

For all 2,197 presentation targets:

- reconstruct canonical text from final rendered DOM, including hidden presentation-only characters;
- require exact equality with v101.103 canonical target text;
- validate all 3,293 `SPEECH_DATA` segments against actual target text;
- require no invalid offsets/overlaps introduced by this stage.

## 8.7 Geometry / line-wrap tests

Run Chromium geometry tests at minimum:

```text
390×844   phone portrait
430×932   large phone portrait
820×1180  iPad portrait class
1024×1366 iPad portrait class
1366×1024 iPad landscape class
1480×1000 user-screenshot class
```

Run in both light and dark themes for representative fixtures.

For every visible opening guillemet fixture, assert that ordinary line wrapping never leaves `«` alone on a rendered line while its first lexical token begins the next line.

For every closing guillemet fixture, assert equivalent non-orphan behaviour.

If an inline keep-together wrapper is required, re-run all selection/highlight offset tests because this changes DOM structure.

## 8.8 Visible topology reconciliation gate

Build the successor full visible-paragraph graph and compare it against the v101.101 native topology witness by stable surface/target/offset coordinates.

Allowed differences are limited to:

```text
REMOVE v101.102+ divine-speech-start-only presentation boundaries
REMOVE native/storage boundaries classified and proved as QUOTE_EDGE_INTEGRITY_JOIN
```

Required:

```text
unexplained added visual boundaries = 0
unexplained removed visual boundaries = 0
all explained differences present in hybrid_boundary_decision_ledger.csv
```

No quote-edge repair may be implemented by moving a boundary before the opening guillemet merely to preserve paragraph count.

This is the principal gate proving that the hybrid restores native 24H paragraph presentation while correcting only the user-confirmed orphan-quote edge defect class.

---

# 9. Phase D — highlighting and interaction regression

## 9.1 Samsung/Android shared topology

Using the final hybrid topology:

- `Paragraphe` resolves exactly one current visible paragraph;
- source fragments joined into one visual paragraph remain one Samsung target;
- v101.101 speech-end boundaries split Samsung targets exactly where they split the reader;
- no divine-start-only split exists;
- no quote-edge-only split exists.

## 9.2 Samsung highlight lifecycle

Automate where possible:

```text
enter Paragraphe mode
select paragraph
choose colour
rerender
recolour
delete
reload
Mon Espace reopen
```

Verify grouping and labels remain correct.

Physical Samsung remains `NOT_TESTED` until actually tested on device.

## 9.3 Apple/desktop exact-selection lifecycle

Automate selection ranges spanning representative:

- narration → inline Jesus style boundary;
- visible Luisa guillemet;
- hidden divine wrapper location;
- nested visible quotation;
- RA19B joined fragments.

Verify:

```text
exact selected text preserved
stored offsets preserved
rerender preserves highlight
recolour/delete works
Mon Espace reopening targets correct text
```

Physical iPhone/iPad selection remains `NOT_TESTED` until tested on device.

## 9.4 Historical highlight invariant

Do not rewrite existing saved highlight bytes.

If a historical visual-paragraph highlight maps differently under the final topology, classification must be derived honestly from the current topology; do not silently mutate stored data to make the label fit.

---

# 10. Phase E — app-wide no-regression matrix

Run the existing regression harness plus new hybrid tests against the actual successor runtime.

At minimum:

## Corpus/data

```text
24 Hours
5 prayers
4 sections
40 TEXT_LIBRARY items
24 linked-text mappings
30 internal subheadings
2,197 SPEECH_DATA targets
3,293 SPEECH_DATA segments
all stable IDs unique
all links resolve
all protected declaration hashes unchanged
```

Use freshly parsed counts from the final candidate; do not merely copy expected numbers into the report.

## Rendering

Render:

```text
all 24 Hours
all visible/non-group library texts
Promesses et bienfaits
all linked LDC texts
all internal subheadings
light mode
dark mode
Prier/Étudier states where applicable
```

Check zero console errors.

## Search

Test:

```text
accent-insensitive normalization
ordinary Hour result
linked LDC result
quoted phrase result
internal subheading result
anchor/jump target
```

## Navigation

Test:

```text
Accueil
Heures
Recherche
Mon Espace
Hour → Mon Espace → Retour
linked text → Retour
help/modal open/close
back-stack state
progress indicator restoration
```

## User state

Test:

```text
favourite add/remove
highlight add/recolour/delete
notes if present
read/unread if present
font size
theme
export/import
reload persistence
```

## Update/PWA static/runtime

Verify:

```text
APP_VERSION = v101.105
version.json
service-worker cache identity
manifest identity unchanged except permitted version metadata
root/deploy HTML parity
update/Actualiser wiring still present
```

Do not claim live update or true offline PASS without real deployment/device evidence.

## Accessibility static checks

Verify no regression in:

```text
aria labels
focusable navigation controls
modal roles
screen-reader-hidden presentation nodes
suppressed guillemets not announced twice
visible guillemets remain accessible as source text
```

Real VoiceOver/TalkBack remains external.

---

# 11. Build-script compliance, evidence-universe cleanup and stale-reference gates

After every fix and again before packaging:

## 11.0 Rebuild the active evidence universe cleanly

Do not carry forward v101.103 reports as if they were current v101.105 evidence. Before final prepackage report generation:

1. remove/supersede generated active reports, manifests and metadata inherited from the baseline that describe v101.103 as current;
2. either regenerate them for v101.105 or move clearly historical material under an explicitly historical/provenance path;
3. regenerate reports only from the final frozen prepackage source tree;
4. generate manifests only after the prepackage file tree is final;
5. avoid self-referential hash dependencies — a hash manifest must not require its own final hash to validate itself unless the format explicitly defines a non-circular canonicalization rule;
6. no prepackage report may claim that the future immutable ZIP has passed a reopen audit.

Any mixed current/historical evidence without explicit classification is blocking.

## 11.1 Full recursive stale-reference scan

Scan:

```text
root files
deploy files
scripts
reports
metadata
README
version files
app HTML
service worker
nested ZIPs if any
```

Search at minimum for:

```text
v101.102
v101.103
v101.104
old stage names
old package filenames
old current-authority claims
premature FINAL_PACKAGE_REOPEN_GATE = PASS
premature INDEPENDENT... = PASS
obsolete blanket divine-start rule claims
MOVE_VISUAL_BOUNDARY_BEFORE_OPENING_GUILLEMET
```

Historical references are allowed only when explicitly labelled historical/provenance and classified in the stale-reference ledger.

Any unexplained active stale reference = `FAIL`.

## 11.2 Report-integrity gate

Parse every active report line-by-line and compare each claim to current evidence.

A report must not claim:

```text
checked
verified
PASS
unchanged
no regression
```

without direct evidence in the current run.

Any contradiction = `FAIL_REPORT_INTEGRITY`.

---

# 12. Independent four-pass prepackage audit

Implement independently from the main build logic.

## Pass 1 — files vs execution specification

Verify:

- correct baseline/hash;
- protected data;
- exact allowed diff scope;
- build script output;
- version/cache identity;
- all required ledgers/reports.

## Pass 2 — runtime/package behaviour

Re-run presentation, topology, quote, speaker, highlight, search/navigation and syntax checks without trusting build-script summaries.

## Pass 3 — report claims vs evidence

Parse every active report and verify every numeric/status claim against fresh evidence.

## Pass 4 — contradiction/staleness/adversarial search

Search for:

- hidden meaningful quotations;
- visible redundant divine wrappers;
- divine-start-only paragraph breaks;
- quote-edge-only paragraph breaks;
- orphan guillemets;
- speaker style leakage;
- topology divergence between renderer/Samsung;
- stale PASS/FAIL statements;
- stale counts;
- obsolete v101.104 boundary logic;
- evidence circularity.

Any failed pass blocks packaging.

---

# 13. Required prepackage proof artifacts

The successor package must contain evidence available **before** immutable packaging only.

At minimum:

```text
reports/no_regression_fix_ledger.csv
reports/full_regression_matrix.csv
reports/v101101_native_visual_topology_witness.csv
reports/v101101_native_visual_topology_witness.json
reports/v101103_semantic_presentation_witness.json
reports/v101103_quote_role_witness.csv
reports/hybrid_boundary_decision_ledger.csv
reports/quote_edge_hybrid_reconciliation.csv
reports/presentation_projection_summary.json
reports/visible_paragraph_topology_report.md
reports/android_visible_paragraph_groups.csv
reports/chromium_interaction_topology_results.json
reports/appwide_prepackage_regression.json
reports/protected_data_diff_report.csv
reports/stale_reference_scan.txt
reports/stale_reference_scan.csv
reports/root_deploy_consistency_report.md
reports/nested_zip_consistency_report.md
reports/report_claims_vs_evidence_audit.md
audit/independent_four_pass_audit.md
metadata/hash_manifest.json
metadata/package_manifest.json
metadata/build_provenance.json
metadata/release_evidence_lifecycle.json
```

Also include the executed build and test scripts.

Do not include a post-package final PASS report inside the ZIP.

---

# 14. Deterministic freeze and non-circular release lifecycle

The v101.102 RE1 evidence model remains mandatory.

## 14.1 Deterministic Build A/B

From two fresh copies of the exact frozen prepackage source tree:

1. run Build A;
2. run Build B independently;
3. normalize only intentionally deterministic timestamps/ZIP metadata as specified by the build system;
4. require byte-identical ZIP output.

If hashes differ: `FAIL_DETERMINISTIC_BUILD`.

Target final filename:

```text
L24H_v101105_GITHUB_DEPLOY_NATIVE_24H_LDC_SEMANTIC_HYBRID_PRESENTATION_R1_LOCKED.zip
```

## 14.2 Freeze immutable ZIP

Once A/B are identical:

- copy one byte-identical artifact to the final locked filename;
- compute SHA-256;
- never rewrite that ZIP afterward.

## 14.3 Primary final-package reopen audit

In a fresh audit directory:

1. reopen exact immutable ZIP from disk;
2. recompute package hash;
3. extract all files;
4. unpack every nested ZIP if present;
5. recompute all file hashes;
6. validate manifests;
7. compare root/deploy/nested runtime files;
8. parse actual runtime target map;
9. rerun protected-data checks;
10. rerun hybrid presentation/topology invariants;
11. rerun quote/speaker regressions;
12. rerun `SPEECH_DATA` target/offset validation;
13. rerun stale-reference scan;
14. compare all embedded report claims to evidence;
15. verify no embedded post-package PASS claims.

## 14.4 Separately implemented independent reopened-ZIP audit

Use independently written audit code — not the primary audit functions imported under another name.

The independent auditor must recompute critical facts from the immutable ZIP/runtime itself. It may compare its results to the ledgers, but must not treat build ledgers or primary-audit summaries as proof of the facts they claim.

Reopen the same immutable SHA in another fresh directory and independently verify the same critical invariants, including actual DOM/runtime rendering for the core presentation fixtures.

## 14.5 External evidence only after both audits

Only after the immutable ZIP exists and both reopened audits finish, write externally:

```text
FINAL_REOPEN_AUDIT.md
INDEPENDENT_REOPEN_AUDIT.md
FINAL_DECISION_LOCK.json
EXECUTION_SUMMARY.md
CURRENT_STATE_AND_HANDOVER_v101105_UPDATED_2026-08-23.md
```

Then run an external-evidence integrity audit tying every report to the exact immutable ZIP SHA.

Never insert these post-package files back into the audited ZIP.

---

# 15. Final decision lock

Use exactly these rules.

## FAIL

Final status = `FAIL` if any of the following occurs:

- baseline/authority hash mismatch;
- protected data changed unexpectedly;
- any canonical text difference;
- any unresolved quote role;
- any unexplained visual-topology difference vs v101.101 witness plus the narrowly authorized `QUOTE_EDGE_INTEGRITY_JOIN` overlay;
- any mechanical divine-start-only paragraph break remains;
- any v101.104 generic quote-edge relocation remains active;
- any visible quote is split after its opening guillemet;
- any meaningful quotation is hidden;
- any redundant divine outer wrapper is visibly restored;
- speaker styling/presentation override regression;
- Samsung/render topology disagreement;
- highlight persistence/recolour/delete regression;
- JS/service-worker syntax failure;
- app-wide runtime regression;
- stale active reference;
- manifest/package inconsistency;
- unsupported report claim;
- deterministic Build A/B mismatch;
- primary reopen failure;
- independent reopen failure.

Use the more specific failure label where applicable:

```text
FAIL_BASELINE_AUTHORITY
FAIL_NATIVE_TOPOLOGY_WITNESS
FAIL_SCOPE_ESCALATION_REQUIRED
FAIL_EVIDENCE_MISSING
FAIL_REPORT_INTEGRITY
FAIL_DETERMINISTIC_BUILD
```

## LIMITED_PASS_STATIC

Use only if:

- every executable static/code/runtime/Chromium/prepackage gate passes;
- deterministic Build A/B passes;
- exact immutable ZIP primary reopen passes;
- separately implemented independent reopen passes;
- external evidence integrity passes;
- but exact v101.105 has not yet passed all required physical-device/live/offline gates.

## PASS

Full `PASS` is forbidden unless exact v101.105 is additionally validated on the required external surfaces, including at minimum:

```text
physical iPad — presentation fixtures + selection
physical iPhone — exact text selection/highlighting
physical Samsung — whole-visible-paragraph highlighting
installed PWA update
live GitHub Pages exact-byte binding
true offline cold reopen / airplane mode
```

If these remain untested, the highest permitted status is `LIMITED_PASS_STATIC`.

The assistant's final response must exactly match `FINAL_DECISION_LOCK.json`.

**Do not regenerate Word review packs.** This stage is presentation/release engineering only; Word review packs require a separate explicit user request.

---

# 16. Mandatory physical-device checklist for the exact successor

Prepare, but do not mark PASS before user/device evidence exists.

## iPad — first priority

Test exact user regression examples:

1. H20 `... après le péché :` → Jesus words are inline under native topology, outer divine guillemets hidden.
2. IMG_4532 Luisa quote → `je me disais : « Mon Jésus...` stays together; no break after or generically before `«`.
3. `Ce matin ... Jésus m'a dit : Ma fille...` → no mechanical divine-start paragraph.
4. `Il m'embrassa et Il poursuivit : Étant...` → no mechanical divine-start paragraph.
5. `mon Jésus me dit : Ma fille, J'ai éprouvé...` → no mechanical divine-start paragraph; nested `«peine, pardon»` remains visible.
6. dark/light mode.
7. portrait/landscape.
8. exact selection/highlight/recolour/delete/Mon Espace.

## iPhone

Repeat presentation fixtures at narrow width plus exact selected-text highlighting.

## Samsung

Repeat presentation fixtures and verify `Paragraphe` selects exactly the same visible paragraph the reader shows.

---

# 17. Final handover requirements

If the stage reaches `LIMITED_PASS_STATIC` or `PASS`, the state document must record:

```text
exact v101.105 ZIP filename/hash
exact runtime HTML hash
baseline v101.103 hash
v101.101 topology-witness hash
authority hierarchy
the hybrid presentation contract
explicit statement that v101.104 is forensic-only/superseded
protected declaration hashes
final topology counts and witness parity
quote-role counts
H19/H21 adjudications
all executed test counts
all NOT_TESTED external gates
release-evidence lifecycle
mandatory first action for next conversation
```

The handover must state clearly:

> **Do not reintroduce the blanket divine-speech-start paragraph rule. Do not reintroduce generic quote-edge boundary relocation. Paragraph topology comes from the validated native 24H witness; speaker/quotation semantics come from the LDC-derived v101.103 projection.**

---

# 18. Execution summary — one-line governing algorithm

```text
FREEZE v101.103
→ RECONSTRUCT v101.101 NATIVE VISUAL TOPOLOGY FROM ACTUAL RUNTIME
→ FREEZE v101.103 LDC-DERIVED SPEAKER/QUOTE SEMANTICS
→ BUILD COMPLETE BREAK DECISION LEDGER
→ REMOVE ONLY v101.102+ SPEECH-START-ONLY BREAKS
→ PRESERVE v101.101 SOURCE/SPEECH-END TOPOLOGY
→ KEEP v101.103 RUNS/HIDDEN/QUOTE ROLES
→ REGENERATE ONE SHARED RENDERER/SAMSUNG TOPOLOGY
→ EXHAUSTIVE QUOTE/SPEAKER/TEXT/HIGHLIGHT REGRESSION
→ FOUR-PASS INDEPENDENT PREPACKAGE AUDIT
→ DETERMINISTIC A/B
→ FREEZE IMMUTABLE ZIP
→ PRIMARY REOPEN
→ SEPARATE INDEPENDENT REOPEN
→ WRITE FINAL EVIDENCE EXTERNALLY
→ DECISION LOCK
```

A fix is not complete because it looks correct in one screenshot.  
The stage is complete only when the entire corpus obeys the frozen hybrid presentation contract and the exact immutable successor proves no regression in the executed gates.
