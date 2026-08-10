# Luisa — 24 Heures de la Passion

Version: `v101.62`

Stage-G programme baseline: **v101.60 / 24H-F**, explicitly approved by the product owner as the immutable input to 24H-G.

Corrective repair input: the exact audited **v101.61 / 24H-G** candidate. v101.62 changes only reader-history continuity and progress-strip restoration after leaving the reader; corpus, storage schemas, Repères, contextual actions, deep-link contracts, navigation decisions and platform highlighting semantics remain unchanged.


## 24H-G corrective repair (v101.62) — Mon Espace → Retour reader continuity

- Fixes the owner-reproduced v101.61 defect where leaving an Hour for **Mon Espace** and pressing **Retour** reopened only the Hour start instead of the exact reading position.
- Reader history now carries the Hour, active reader tab and a stable visible paragraph/visual offset snapshot.
- Returning to the reader restores that exact context and immediately re-enables/recalculates the top reading-progress strip.
- Legacy numeric reader-history entries remain accepted for compatibility.
- This repair does not change corpus declarations, note/highlight schemas, Repères, search/deep links, navigation structure, Apple exact-range highlighting or Samsung paragraph policy.

## 24H-G candidate (v101.61) — accessibility / PWA hardening

Stage G keeps the approved 24H-F navigation and hardens cross-cutting release behavior: frequent interactive hit areas target 44×44 CSS px, reduced-motion behavior is reinforced, an unsaved Note draft blocks Actualiser, and the dynamic update banner is exposed as a polite status region. The service-worker strategy itself is preserved and re-certified rather than redesigned.

Physical iPhone/iPad/Samsung, installed-PWA and live GitHub Pages checks remain release-critical and must not be inferred from local browser/static evidence.

## Historical input baseline — 24H-F candidate (v101.60) — navigation prototype

- Primary bottom navigation is now **Accueil · Heures · Recherche · Mon Espace**.
- The existing top-header Search shortcut is deliberately preserved during the transition.
- **Approfondir is not deleted**: it remains prominent on Accueil, gains a direct entry on Heures, remains available within each Hour through linked texts/end actions, and stays in Réglages/sidebar.
- Search now owns the bottom-nav active state; Back from a result must restore query/filter/scroll context.
- `Espace` is renamed to the exact ecosystem label **Mon Espace**.
- This is a staging/user-acceptance prototype. Production certification requires owner/user acceptance and staging usability review; inherited Stage-E live-route and Stage-C device gates remain open.

Input baseline: **v101.58 / 24H-D**, explicitly authorised by the product owner as the input to 24H-E. Stage E changes only search normalisation, stable routing/linking, and privacy-safe support hooks. Protected corpus, personal-data schema, Repères and Stage-C selection/highlighting policies remain unchanged.

## 24H-E candidate (v101.59) — search, deep links and support

- Preserves the six search filters and 140 ms debounce, while formalising a versioned **French search normalizer (`fr-v1`)** with fixtures for accents, `œ/oe`, `æ/ae`, apostrophes, NBSP/narrow spaces and case.
- Adds validated startup routes for `?open=hour&hour=<n>&pid=<stable-id>`, `?open=prayer&id=<stable-id>`, `?open=text&id=<stable-id>` and `?open=search&q=<query>`, with recoverable fallbacks for invalid targets.
- Adds **Lien** to the shared contextual action bar. It copies only a stable route; it never embeds selected text, notes or highlight content.
- Search-result opening continues to push the full Search state (query/filter/speaker/scroll/focus) so Back restores context.
- Adds **Signaler un problème de texte** and **Copier les diagnostics** in Aide/À propos. Both payloads are deliberately privacy-safe and exclude notes/highlight contents.
- No corpus declarations, stable IDs, speech offsets, personal-data schema, Apple exact-range policy, Samsung whole-paragraph policy, PWA `id/scope/start_url`, or navigation structure are changed.
- Local served-origin route/runtime tests and immutable-package audits are required. The roadmap also requires a live/staging-origin route test for production release; that remains pending unless separately executed.

Input baseline: **v101.57 / 24H-C repaired candidate**, explicitly authorised by the product owner as the input to 24H-D. Stage D changes only Mon Espace/personal-data UX. The inherited Stage-C physical-device gaps remain open and are not represented as passed.

## 24H-D candidate (v101.58) — Mon Espace completeness and backup UX

- Separates **Passages à vérifier**, healthy **Surlignages**, **Notes**, and **Progression** rather than mixing stale records into the highlight preview.
- Every stale/recovery record, highlight group and note is reachable: each section has an explicit count and an expandable preview; there is no hard personal-data ceiling.
- Adds a local **Dernier export de sauvegarde** timestamp plus a gentle reminder only when meaningful personal data exists and no recent export is recorded.
- Keeps the machine-readable JSON export/import contract and adds a separate human-readable **Markdown journal export**, which is never accepted as a restore format.
- Does not change the canonical personal snapshot schema, corpus, stable IDs, speech offsets, highlighting schema, Repères, Apple exact-range policy or Samsung whole-paragraph policy.
- Stage-D package/browser gates must prove all records reachable and JSON round-trip preservation. Production certification remains limited by inherited Stage-C device evidence.

## 24H-C iPhone picker repair (v101.57)

- Replaces the historical hard-coded `220 × 110 px` existing-highlight picker assumption with measurement of the actual rendered picker.
- Clamps the picker to the current `visualViewport`/viewport bounds with an 8 px margin and chooses an above/below position that fits.
- Adds a CSS `max-width`/`box-sizing` safety bound.
- Does **not** change highlight offsets, colours, persistence, note schema, contextual-action semantics, Apple exact-range policy or Samsung whole-paragraph policy.
- Product-owner evidence from v101.56: iPhone exact selection/highlighting works; Samsung/Android was not available for testing.
- v101.57 requires targeted real-iPhone confirmation of the repaired existing-highlight picker. Samsung/Android Stage-C remains `NOT_TESTED`.

Input baseline: **v101.55 / 24H-B**, explicitly authorised as the input to 24H-C. **v101.56 / 24H-C is the shared contextual-actions candidate; 24H-D has not started.**

## 24H-C candidate (v101.56) — one contextual action component

- Range selections and paragraph targets now feed one internal target contract and one rendered contextual-action component: **Surligner · Copier · Note · Fermer**.
- The historical `#mobileActionBar` and `#selectionActionBar` business-logic paths are retired; compatibility wrapper function names feed `#contextActionBar`.
- iPhone/iPad/desktop exact selected-text offsets are preserved. Multi-paragraph range selections retain their per-paragraph canonical offsets.
- Samsung/Android explicit **Paragraphe** mode still avoids native word selection; tapping a paragraph now opens the same contextual component, and choosing Surligner then highlights the whole paragraph.
- Highlight range normalization and overlap detection have pure helpers with mutation/adversarial tests. Existing text hashes, paragraph fingerprints, grouped-highlight behavior and conservative stale-recovery logic remain unchanged.
- Notes remain paragraph-anchored and retain the existing transactional save/rollback schema; no note schema migration is introduced.
- The six protected corpus declarations remain byte-identical to v101.55.
- Physical-device validation of iPhone/iPad exact range and Samsung paragraph mode is release-critical for Stage C; static/browser PASS alone cannot certify production.

Input baseline: **v101.54 / 24H-A**, owner-confirmed as working before explicit authorisation to begin 24H-B. **v101.55 / 24H-B is the audited Repères baseline carried into 24H-C.**

## 24H-B candidate (v101.55) — calm reader + optional Repères

- The former user-facing binary mode is retired. The neutral **Repères** control now governs only technical/source markers.
- Repères OFF hides paragraph numbers, source/page cues and speaker-attribution badges; direct-speech colours remain visible.
- **Note · Surligner · Copier remain available with Repères OFF or ON**, including desktop paragraph actions and existing mobile selection/long-press routes.
- Toggling Repères changes CSS classes only; it does not rebuild the reader. A semantic visible-anchor offset is restored after the layout change, while the DOM selection is preserved where the browser permits.
- Persisted `studyMode` / `lp24_mode` storage remains unchanged for this compatibility release. New exports include both `showReperes` and `studyMode`; old exports containing only `studyMode` restore the equivalent Repères preference.
- The six protected corpus declarations remain byte-identical to v101.54.
- Stage-B static/runtime acceptance passed before packaging. This payload is designated the audited-candidate target; immutable reopened-package and independent audit results remain the final authority and no production deployment is claimed.

## Carried forward from 24H-A (v101.54) — display settings contract

- Four semantic reading levels: **Petit 16 px · Normal 19 px · Grand 22 px · Très grand 26 px**.
- Fresh/untouched profiles default to **Normal 19 px**; old numeric `fontSize` values migrate once to semantic `fontLevel` while the numeric legacy mirror remains compatible.
- The size panel has a live preview; reader body/title/reading metadata scale, while navigation and UI chrome stay at their normal size.
- 22/26 px levels receive more line-height and paragraph spacing.
- Theme contract remains **Automatique · Clair · Sombre**; Automatique alone follows OS changes.
- Direct-speech spans now expose non-colour speaker semantics to assistive technology; dark Father colour is adjusted to pass the tested speaker/highlight contrast matrix.
- `CORPUS`, `TEXT_LIBRARY`, `HOUR_LINKED_TEXTS`, `SPEECH_DATA`, `INTERNAL_SUBHEADINGS` and `SPEECH_END_VISUAL_BREAKS` are unchanged.
- 24H-A static/runtime/package qualification was documented in its evidence bundle; the product owner subsequently confirmed that the candidate works and explicitly authorised 24H-B. Device details were not supplied in that confirmation.

### Historical production note

v101.53 promoted v101.52 and v101.53 in one step.

## Corpus — the approved targeted change set (v101.52)

The first release since v101.44 in which the corpus itself changes, under an explicit approved
change-set instruction.

- **21 mandatory wording corrections.** All 21 targets required correcting (`CHANGED = 21,
  ALREADY_PRESENT = 0, UNMAPPED = 0`), applied as minimal clause-level edits rather than
  whole-paragraph rewrites. Measured against the untouched v101.51 corpus: exactly 21 of 1,839
  records changed, 0 unrelated, record-ID set identical.
- **65 non-destructive display segmentations, 180 display units.** Canonical ids, order and text
  are unchanged; every record's segment slices concatenate back to its canonical text exactly.
  Segments render through the app's existing canonical-coordinate renderer, so notes, highlights,
  favourites and saved positions keep resolving through the canonical parent id — no migration.
- **4 cross-record continuity operations**, both stable ids preserved in every group; copying
  either member of a group copies the whole grammatical unit.
- **The 3 expressly excluded stylistic constructions are untouched.**
- **Speech offsets recalculated by exact delta** for the 7 affected records; any boundary that
  would have fallen inside a replaced span was refused rather than approximated — none did.
- **Protected-declaration contract re-baselined**, not dropped: `CORPUS` and `SPEECH_DATA` moved by
  design; `TEXT_LIBRARY`, `HOUR_LINKED_TEXTS`, `INTERNAL_SUBHEADINGS` and `SPEECH_END_VISUAL_BREAKS`
  verified unchanged.

## App fix (v101.53) — iPad bottom bar no longer covers the end of a view

Reported on the Approfondir screen: the bottom navigation partly hid the last card and it could not
be scrolled any further. Cause: `html.ios-device .content` is a flex column with `overflow-y: auto`,
and iOS Safari excludes such a container's `padding-bottom` from its scrollable overflow — the space
reserved for the bar evaporated on device even though the app reserves it correctly (Chrome honours
it, which is why this only showed on iPad). Fixed by reserving that space with a flex-item spacer
instead of padding, which cannot be dropped by that Safari behaviour.

## Carried forward from v101.26–v101.51

Notes reachable from both mobile action bars; recovery for highlights broken by editorial
corrections, with a working **✕ Retirer** in Mon Espace; Mon Espace ordered newest-first with a
"Voir tout" expander so nothing is silently hidden; the note-panel iOS zoom/pan fix; the
service-worker update fix; speech punctuation restored across 99 paragraphs; progress/study-mode/
reset persistence fixes; meditated-hour border weight; dark-mode contrast fix; "Automatique" in
place of "Système"; Gethsémani Compléments cleanup.

## Real-device status

**Confirmed by Louis** before this promotion: reviewed the corpus text corrections, and confirmed
the iPad bottom-bar/scroll fix.

Internal history, the full version-by-version record, the corpus decision record (including the
v101.52 protected-declaration contract) and open items still tracked (a hardcoded corpus unit count
pending an independent recount; one unreproduced Android WebAPK install report) are in
`luisa-24h-state_1.md` in the project working directory.
