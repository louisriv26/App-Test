# L24H v101.90 — Internal Extract Heading Annotation — Hard-Gated Execution Script

## Baseline
- Source of truth: `L24H_v10189_GITHUB_DEPLOY_WEBKIT_TITLE_BOUNDARY_R2_AUDIT_RECONCILED.zip`
- Required SHA-256: `d6ba4b975d16a8601b91ce0a1e52128bb4aab8e018ffb52530c284c23941a35f`
- Baseline runtime: v101.89 / cache `luisa-24h-v101-89` / schema 8 / snapshot 5.

## User-evidence authority
Physical iPhone/iPad screenshots dated 2026-08-20 prove that selecting words inside internal Approfondir extract headings such as:
- `PASSION24.TEXT.RELATED_HOUR_18.BODY.P050` — Tome 10 — 12 novembre 1910 …
- `PASSION24.TEXT.PART_III_DIVINE_PASSION.BODY.P064` — Tome 12 — 20 mars 1919 …
shows Apple's native selection menu but not the app actions `Surligner / Note / Copier / Fermer`.

This physical evidence overrides prior automated PASS claims for the reported surface.

## Gate 0 — Stop-before-modification preflight
STOP before any app modification if any condition fails:
1. baseline ZIP hash is not exact;
2. runtime twins are not byte-identical;
3. active version/cache/schema/snapshot are not v101.89 / v101-89 / 8 / 5;
4. the two screenshot headings cannot be found with the exact stable IDs above;
5. the full indexed corpus does not contain exactly 94 `Tome … — …` internal extract headings across 27 indexed visible readings;
6. any heading lacks a unique `PASSION24.TEXT.*.BODY.Pnnn` target resolvable by `getTargetInfo()`;
7. any protected devotional structure differs between runtime twins;
8. implementation would require wording/source/editorial judgement.

## Protected structures — immutable
The following embedded structures must remain byte/hash identical to baseline:
- `CORPUS`
- `TEXT_LIBRARY`
- `HOUR_LINKED_TEXTS`
- `SPEECH_DATA`
- `INTERNAL_SUBHEADINGS`
- `SPEECH_END_VISUAL_BREAKS`

Also immutable unless a hard gate proves otherwise:
- all paragraph/body stable IDs and ordering;
- storage schema 8;
- personal snapshot 5;
- existing user highlight/note/libraryMark stores;
- H15/H17 corrections;
- search corpus and speech offsets.

## Exact implementation scope
### A. Render internal extract headings as annotation surfaces
Keep the existing styled/anchored `<h3 class="library-extract-heading" id="PID">`, but render its text through a dedicated child:

```html
<h3 class="library-extract-heading library-extract-heading-target" id="PID" data-target-type="library_text">
  <span class="library-extract-heading-selectable" data-para-id="PID">renderParaText(text, PID)</span>
</h3>
```

Requirements:
- visible text must remain character-for-character identical when no annotation exists;
- `<h3>` ID must remain exact so all live-index anchors remain valid;
- no generic body typography class may be added to the `<h3>` itself.

### B. Selection registry
Add `.library-extract-heading-selectable` to the canonical selectable-surface selector used by iOS/body annotation code.

### C. iOS/WebKit boundary normalisation
Generalise the existing v101.89 owned-surface boundary resolver so it supports both:
- top-level `.library-title-target` → `.library-title-selectable`;
- internal `.library-extract-heading-target` → `.library-extract-heading-selectable`.

It must accept text-node, child-span, and WebKit-style parent `<h3>` boundaries only when the Range boundary actually points to the owned surface. It must not map arbitrary ancestors.

### D. Highlight rendering/rerender
Internal headings must use the existing `renderParaText()` / `renderStructuredParaText()` path so partial highlights, recolouring, removal and Undo render immediately and after reload.

### E. Platform behaviour
- iPhone/iPad: exact selected words in internal extract headings use normal `Surligner / Note / Copier / Fermer` actions.
- Samsung/Android explicit Paragraphe mode may treat the whole internal extract heading as one existing `library_text` target; do not enable native Android word selection.

### F. Help terminology
Help must explicitly include internal extract headings, e.g. `Tome … — date — …`, not merely the top-level Approfondir reader title.

### G. Version/package
- app version: v101.90
- service-worker cache: `luisa-24h-v101-90`
- schema 8 / snapshot 5 unchanged.
- active QA must include exact screenshot-target scenarios.

## Mandatory per-fix lifecycle
For each modified area:
IMPLEMENT → DIFF REVIEW → LINE-BY-LINE CHECK → BUILD-SCRIPT COMPLIANCE → TARGETED TEST → MINI-REGRESSION → INDEPENDENT RECHECK → PASS/REDO.

Do not proceed past any failed gate.

## Targeted automated acceptance
On the immutable candidate, test all 94 headings and require:
1. exact stable `<h3>` ID;
2. `.library-extract-heading-selectable[data-para-id=ID]` exists;
3. heading `textContent === getTargetInfo(ID).text`;
4. text→text Range opens normal app actions;
5. `<h3>`→text Range opens normal app actions;
6. text→`<h3>` Range opens normal app actions;
7. `<h3>`→`<h3>` full-heading Range opens normal app actions;
8. partial highlight creates ordinary `textHighlights[ID]` record;
9. immediate `<mark class="hl ...">` render;
10. recolour/remove/Undo;
11. note path and copy target resolve;
12. `rerenderPara(ID)` retains `<h3>` container/ID;
13. live-index buttons still reference extant heading IDs.

Exact screenshot-target automated cases are mandatory for:
- `PASSION24.TEXT.RELATED_HOUR_18.BODY.P050`
- `PASSION24.TEXT.PART_III_DIVINE_PASSION.BODY.P064`.

## Mini-regression
Must prove no regression to:
- top-level Approfondir title exact selection;
- ordinary Approfondir body selection;
- Hour body highlighting;
- libraryMarks / `Marquer cette lecture` independence;
- Samsung paragraph mode routing;
- Mon Espace target reopening;
- JSON backup/import target validation;
- light/dark and font-size rendering;
- live extract index anchors.

## Four passes
1. Files vs governing/build script and immutable/protected hashes.
2. Runtime/package behaviour, including all 94 headings and screenshot targets.
3. Parse every active report/QA claim line-by-line against current evidence.
4. Search contradictions, stale PASS/FAIL, stale versions/cache names/numbers and obsolete evidence.

Any failed pass must stop packaging until corrected and all four passes rerun from baseline.

## Deterministic packaging gate
Build twice from the frozen baseline. ZIP A and ZIP B must be byte-for-byte identical before either may become canonical.

## Immutable reopened-ZIP gates
After canonical ZIP is frozen:
1. reopen in a fresh directory and recompute archive/member/manifests/protected hashes;
2. rerun targeted runtime tests from extracted final bytes;
3. rerun active-report/stale-reference checks;
4. run a separately implemented independent reopened-ZIP auditor, including the two screenshot heading IDs.

No PASS may be reported unless both reopened gates PASS.

## Physical-device decision rule
Automated tests cannot close the physical iPhone/iPad gate. The final package must remain `LIMITED_PASS` until the exact v101.90 package is tested on physical iPhone/iPad and the app action bar appears when selecting part of one of the internal `Tome …` headings.

## Final decision lock
Final response must exactly match the final immutable decision lock. Do not regenerate Word review packs.
