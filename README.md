# Luisa — 24 Heures de la Passion

Version: `v101.56`

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
