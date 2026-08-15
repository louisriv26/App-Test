# Luisa — 24 Heures de la Passion

Version: `v101.82`

## v101.82 — Minute-detail corrective (15 August 2026)

- Corrects the reference-action defect found during the prior four-pass recheck: **Partager** / **Copier le lien** now resolve strictly from the passage actually visible in the reader, never from stale contextual-selection state.
- Corrects reader text-size continuity: changing among **Petit 16 / Normal 19 / Grand 22 / Très grand 26 px** captures the active selected passage when present, otherwise the visible passage nearest the reading position, and restores its visual offset with the same reader-offset restoration mechanism used by Repères.
- Replaces a stale migration-failure message that incorrectly referred only to a text-size preference with a generic, truthful personal-data migration message.
- Replaces internal development wording in the Samsung/Android settings with user-facing explanation of the existing **Paragraphe** workflow.
- Corrects focus restoration when **Note** or the colour picker is opened from the temporary contextual toolbar: if that trigger disappears, focus returns to the stable main reading region instead of falling to the document body.
- No corpus text, speech data, stable IDs, storage schema, snapshot version, notes, coloured highlight model, search, navigation, Repères semantics, theme semantics or PWA identity changed.
- Exact v101.82 physical iPhone/iPad/Samsung, installed-PWA, offline, assistive-technology and live-origin certification remain external gates.

## Historical release lineage — v101.80 and earlier (superseded by v101.82)

The entries below are retained as historical provenance only. They do not describe the current v101.82 interaction contract.

## v101.80 — Ecosystem interaction closure (15 August 2026)

- Contextual passage actions are now **Surligner · Note · Copier · Fermer**.
- Stable reference actions moved to reader Réglages as **Partager** and **Copier le lien**.
- `Partager` uses native Web Share where available; user cancellation is silent; genuine failure falls back to copying the stable link with truthful feedback.
- The obsolete desktop `◈` paragraph-mark rail and its separate `state.highlights` persistence/export/Mon Espace path are retired. Existing legacy marks are intentionally discarded on migration.
- Samsung/Android **Paragraphe** remains supported as an ordinary coloured whole-paragraph `textHighlights` workflow. iPhone/iPad/desktop exact-selection highlighting remains unchanged.
- Storage schema advances **6 → 7** and personal snapshot **3 → 4** solely to remove the retired paragraph-mark state safely. Protected corpus declarations are unchanged.
- Exact v101.80 physical iPhone/iPad/Samsung, installed-PWA, offline and live-origin certification remain external gates.

Stage-G programme baseline: **v101.60 / 24H-F**, explicitly approved by the product owner as the immutable input to 24H-G.

Historical four-pass corrective input: the exact audited **v101.62 / 24H-G reader-return repair**. v101.63 preserves that return-context fix and closes additional Stage-G touch-target/report-integrity gaps found only when on-demand surfaces were exercised. No corpus, personal-data schema, route contract, Repères behavior, navigation decision or platform highlighting policy is changed.


Historical persistence corrective input: the exact audited **v101.63 / 24H-G four-pass corrective hardening**. v101.64 fixes a downgrade-safety defect found only by the subsequent historical-profile replay: a canonical snapshot created by a newer app version could be detected as future-version and then silently overwritten by current-schema legacy fallback data. v101.64 preserves that future canonical snapshot byte-for-byte, uses only compatible fields in memory for the session, blocks all current-version durable writes while the future snapshot owns the canonical key, skips destructive R41/stale-highlight migration writes, and gives honest not-saved feedback. No corpus declaration, stable ID, user-data schema, route contract, navigation, Repères or highlighting policy changes.


Historical persistence corrective input: the exact audited **v101.64 / 24H-G future-snapshot preservation repair**. The subsequent minute-detail replay found a second downgrade edge case: `snapshot_version` could be current while `schema_version` was newer, allowing an older preference/action write to down-convert the canonical record. v101.65 guards both version axes. It also refuses to label a compatible-subset export as a complete machine backup while a newer canonical generation is present, and corrects persistence-failure messages that could otherwise misdescribe the newer-version guard as storage exhaustion. No corpus declaration, stable ID, user-data schema, route contract, navigation, Repères or highlighting policy changes.


Historical corrective input: the exact **v101.65 / 24H-G persistence-safety completion** bytes. A subsequent minute-detail H4 audit found three inherited **storage-level** count ceilings that were not UI previews: notes per paragraph and text highlights per paragraph were silently truncated at 200 during sanitisation, and legacy highlight IDs were truncated at 5,000. A normal later save could then persist the truncated state. v101.66 removes those three count ceilings while preserving all validation, the 5 MB import-size guard, note text limits, highlight validation, future-version preservation, and all prior Stage-G behavior.


Historical corrective input: the exact **v101.66 / 24H-G personal-data completeness repair** bytes. The subsequent full personal-state inventory found a separate active compatibility store, `state.highlights`, used by the whole-paragraph `◈` marking action. Those marks were persisted and exported but were not represented anywhere in Mon Espace; a mark whose paragraph no longer existed was therefore also impossible to remove from the personal workspace. v101.67 surfaces resolved whole-paragraph marks in **Surlignages**, missing-target marks in **Passages à vérifier**, and provides transactional removal without converting or deleting any record automatically.


Historical corrective input: the exact **v101.67 / 24H-G legacy-mark reachability repair** bytes. The subsequent personal-data surface audit found two remaining completeness omissions for the same active `state.highlights` whole-paragraph marks: the backup-reminder counter ignored them, and the human-readable Markdown journal could state `Aucun surlignage` even when such marks existed. v101.68 brings those two derived surfaces into parity with Mon Espace and the machine backup.


Historical corrective input: the exact **v101.68 / 24H-G legacy-mark personal-data completion** bytes. A final derived-surface inventory found that the wide/tablet right-side Mon Espace preview still built its `Surlignages` mini-list from exact-text highlights only. With only whole-paragraph marks present it incorrectly displayed `Aucun surlignage`; stale/missing exact-text annotations were similarly omitted from the preview. v101.69 makes this preview truthful without turning it into the full workspace: resolved text/paragraph marks can appear in the three-item preview and any stale/missing records are disclosed as `passage(s) à vérifier dans Mon Espace`.


Historical ultra-deep audit input: the exact **v101.69 / 24H-G annotation-preview truth repair** bytes (HTML SHA-256 `c7161e360b1b2e861ad911d494c5785a92671f3929fce1141a0ab43426838cb3`). The minute-detail recheck rejected v101.63 through v101.68 as deploy candidates while successively exposing and repairing: future canonical downgrade, future schema downgrade, hidden 200/200/5,000 personal-data caps, unreachable whole-paragraph marks, missing backup/journal coverage for those marks, and a wide-panel false `Aucun surlignage`. v101.69 passed those runtime corrections. v101.70 is the report/identity finalization of that exact functional state; no corpus declaration or user-data schema is changed.


Historical extreme-deep audit input: the exact **v101.70 / 24H-G ultra-deep recheck** bytes (HTML SHA-256 `7b95564c0e15fe49d22d1f6befde25a3df2cf2b1c14e30480c44b83c778ec9a2`). A still-deeper adversarial pass rejected v101.70 as deployable after finding three cross-stage defects that ordinary UI regression did not expose: (1) a legitimate pretty-printed machine backup could exceed the inherited 5 MiB import guard and be rejected by the app that created it; (2) the external prayer route treated inherited JavaScript object keys such as `__proto__` as if they were real prayer IDs and could throw during startup; (3) an inactive legacy integrity helper still carried the stale text `revue éditoriale en cours` even though the speech-attribution review had already been closed and frozen before the A–G programme. v101.71 corrects only those three concerns plus release identity; protected corpus declarations and the user-data schema stay unchanged.


Historical extreme-deep accessibility input: the exact **v101.71 / 24H-G backup/deep-link repair** bytes (HTML SHA-256 `054934c97c32942cf45d639448b5a7302fae87ce58d005722805e66165512081`). A full-surface runtime measurement found one additional Stage-G accessibility edge case: the colour picker declared 44px swatches, but its parent entrance animation scaled the complete picker from 90% to 100%, so the actual clickable swatches temporarily measured **39.6px at animation start**, **42.86px around 80ms**, and only reached 44px when the 150ms animation settled. v101.72 removes scaling from that entrance animation while retaining its opacity/vertical motion, so the controls remain full-sized for the entire interactive lifetime. No corpus, storage schema or user-data semantics change.


Historical extreme-deep persistence input: the exact **v101.72 / 24H-G picker hit-area repair** bytes (HTML SHA-256 `4bda4da366876a4396bdaedbf585eb67cbe81c4f0eaa25f837c013bc452c044a`). A post-write failure probe found that the canonical writer could successfully change `lp24_snapshot_v2`, then fail its verification read, return failure and roll back only the in-memory UI while leaving the new canonical bytes durable. v101.73 captures the previous canonical bytes before writing and restores them if verification fails or mismatches. If the previous canonical value cannot be read, the write is refused before mutation. No corpus or user-data schema change.


Historical extreme-deep restore-safety input: the exact **v101.73 / 24H-G canonical atomicity repair** bytes (HTML SHA-256 `48c1d7041a0668c3dcfed4729b45dbba661f9b2ef3d639de7aba01d3c8688e46`). An adversarial wrong-file restore test found that arbitrary/foreign JSON carrying only a supported `schema_version` could pass validation, be confirmed as an import, and replace genuine 24H notes/progression with empty defaults while reporting success. v101.74 adds an explicit machine-backup identity and a backward-compatible historical 24H signature gate before any replace-import. No corpus or canonical storage-schema change.


Historical build input: the exact **v101.74 / 24H-G restore identity repair** bytes (HTML SHA-256 `ff47a2e0db334c9c4d166f4da0ba0ad1fb91f18f5d78a7c14a6f3c06f4a2c140`). A still-deeper persistence probe found that a post-write verification failure followed by a rollback-write failure could leave new canonical bytes durable while the UI rolled back and said the change was not saved. A separate malformed-backup probe found that one invalid text-highlight sibling could make the validator silently discard the entire paragraph's otherwise valid highlight array and still report import success. v101.75 classifies rollback-failure durability instead of making a false claim and rejects malformed personal-record structures before any replace-import. No corpus or canonical storage-schema change.


Historical build input: the exact **v101.75 / 24H-G storage/import integrity repair** bytes (HTML SHA-256 `8aa71a3a6859a09d2d4e3fc2781830766d30637c4aead5706de09f1ac6aa0d61`). An auxiliary-storage honesty probe found two smaller session-state contradictions: a failed `lp24_recent_texts` write claimed the recent text remained visible for the session even though it disappeared immediately, and a failed `lp24_onboarded` write claimed the dismissal remained valid for the session even though the welcome card reappeared on the next Home render. v101.76 adds real in-memory session fallbacks and dedicated warning state. No corpus or canonical personal-data schema change.


Historical build input: the exact **v101.76 / 24H-G auxiliary-storage honesty repair** bytes (HTML SHA-256 `b1be16d1242c9770f17673049a81534c448a1925ded26cac8a0c324e452b1a2a`). Owner review found the Aide function materially incomplete: the contextual bar named Surligner · Copier · Lien · Note · Fermer without explaining each action where users encounter it, and several current features (note lifecycle, paragraph marks versus coloured highlights, backup/journal distinction, display controls, update draft protection) were either scattered, duplicated or insufficiently explained. v101.77 is a help/documentation-only correction: no runtime behavior, corpus, stable ID, persistence schema or annotation data is changed.

Historical build input: the exact **v101.77 / 24H-G help completeness repair** bytes (HTML SHA-256 `8e4b534c399c4bd35e0d516cfda77b31a0838cc5fbcf9612d7dee7a16c81857e`). The final claim-by-claim Help review found one stale inherited status in two Help locations: the direct-speech attribution layer was described as still subject to editorial validation even though the project state records that the speech-attribution review was already fully closed before the A–G programme. v101.78 preserves the entire v101.77 Help rewrite and corrects only that status wording plus release identity. No runtime behavior, corpus, SPEECH_DATA, stable ID or persistence schema is changed.

Historical build input: the exact **v101.78 / 24H-G help completeness finalization** bytes (HTML SHA-256 `60e67f3b4b298e5a15c12be8f76203254099a37cb8267b3bb77ce3d1a040408f`). Physical iPad screenshots exposed the legacy desktop paragraph-action rail (◈ Marquer le paragraphe / ⎘ Copier la citation; meditation also has ✎ Note) half-clipped at the right edge of the reader. The rail is positioned outside the text column and is intended for fine-pointer desktop hover, not for iPad or Samsung. v101.79 suppresses that rail on iOS/touch/coarse-pointer and Android runtime classes while preserving the intended iPad exact-selection contextual bar, Samsung whole-paragraph mode and desktop hover actions. No corpus, SPEECH_DATA, stable ID or persistence schema changes.

## 24H-G iPad paragraph-side action repair (v101.79)

- Hides the legacy `.para-actions` / `.ref-actions` side rail on iOS and touch/coarse-pointer runtimes.
- Explicitly hides the same legacy rail on the Android/Samsung runtime class; Android continues to use the dedicated **Paragraphe** workflow.
- Leaves the rail available on non-iOS fine-pointer desktop, where its outboard hover placement is intentional.
- Does not change the shared contextual action bar **Surligner · Copier · Lien · Note · Fermer** used by exact selection / explicit paragraph targeting.
- Protected corpus declarations, reader-return repair, Help v101.78, persistence and PWA behavior remain unchanged.

## 24H-G help completeness finalization (v101.78)

- Preserves the complete v101.77 Aide rewrite and all action-by-action guidance.
- Replaces the stale `reste soumise à validation éditoriale` wording with current-status wording: the search filter uses the corpus's current attribution layer, and the Help states that its editorial review is already closed.
- Does not modify `SPEECH_DATA`; this is documentation/status alignment only.
- Protected corpus declarations and all runtime/persistence behavior remain unchanged.

## 24H-G help completeness repair (v101.77)

- Rewrote the complete Aide modal against the exact active runtime rather than appending isolated lines.
- Added a dedicated action-by-action explanation of **Surligner · Copier · Lien · Note · Fermer**.
- Clarified that **Lien** copies a privacy-safe stable route; for selected text in an Hour it targets the containing paragraph and does not transmit the selected words, notes or highlight contents.
- Added a full note workflow: open, write, 2,000-character limit, Enregistrer, multiple notes per paragraph, delete, Mon Espace retrieval, and the unsaved-draft update guard.
- Distinguished coloured text **surlignage** from the separate whole-paragraph **◈ marquage** action.
- Documented edit/delete of existing highlights, Passages à vérifier, Samsung/Android paragraph mode, Repères, four semantic text-size levels, theme preferences, Search, Mon Espace JSON backup/import versus readable Markdown journal, update behavior, support diagnostics and privacy boundaries.
- Removed stale/ambiguous help wording such as paragraph actions being described as Surligner when the persistent paragraph action is actually ◈ Marquer.
- Protected corpus declarations and all runtime/persistence behavior are unchanged.

## 24H-G auxiliary-storage honesty repair (v101.76)

- Recent linked-text history now has an in-memory session cache. If the `lp24_recent_texts` compatibility write fails, the text really remains in the recent list for the current app session, matching the warning shown to the user.
- Onboarding dismissal now has an in-memory session flag. If `lp24_onboarded` cannot be written, the welcome card remains dismissed across subsequent Home renders in the same app session, matching the warning shown to the user.
- These auxiliary warnings use dedicated flags and no longer compete with the passive reader-position warning flag.
- v101.75 canonical snapshot atomicity/import validation, v101.74 backup identity, v101.62 reader-return repair and all prior A-G protections remain preserved.
- Physical-device, installed-PWA and live-origin evidence remains pending and is never inferred from local browser/machine tests.

## 24H-G storage/import integrity repair (v101.75)

- If canonical verification fails and rollback itself fails, the writer performs a final canonical read. A confirmed new payload is treated as durable success; a confirmed old payload is treated as rollback; otherwise the result is explicitly `durabilityUncertain` rather than falsely `not saved`.
- Durable actions, notes, passive state and Restore keep the current session aligned with an uncertain durable outcome and tell the user that persistence could not be verified; they do not silently roll the UI back to a state that may disagree with disk.
- Restore now strictly validates personal-record structures before replacement. A malformed highlight/note/progression/position payload is rejected instead of being accepted with silently dropped valid siblings.
- Current v101.74 backup identity markers and genuine v101.53 unmarked backup compatibility remain preserved.
- Physical-device, installed-PWA and live-origin evidence remains pending and is never inferred from local browser/machine tests.

## 24H-G restore identity / wrong-file protection (v101.74)

- New machine exports identify `format: luisa-24h-user-data` and `app_id: passion24`.
- Restore rejects an explicit foreign `app_id` or foreign backup `format` before confirmation/persistence.
- Restore also rejects arbitrary JSON that lacks the core historical 24H export shape.
- Genuine older 24H backups without the new markers remain accepted when their historical v101/prototype app identity or the bound 24H corpus identity is present; the v101.53 production-export fixture is a mandatory regression.
- v101.73 canonical rollback-on-verification-failure, v101.72 picker hit-area repair and all earlier A-G behavior remain unchanged.
- Physical-device, installed-PWA and live-origin evidence remains pending and is never inferred from local browser/machine tests.

## 24H-G canonical save atomicity repair (v101.73)

- Before a canonical snapshot write, the exact previous canonical bytes are read and retained as a rollback image.
- If the pre-write read itself fails, no canonical write is attempted.
- If the write succeeds but post-write verification fails or mismatches, the exact previous canonical bytes are restored (or the new key is removed when none existed).
- The existing UI rollback/"not saved" semantics therefore agree with the durable canonical state in the tested partial-storage failure paths.
- v101.72 picker hit areas, v101.71 self-backup/deep-link safeguards, future-version preservation and all earlier A-G behavior remain unchanged.
- Physical-device, installed-PWA and live-origin evidence remains pending and is never inferred from local browser/machine tests.

## 24H-G colour-picker transient hit-area repair (v101.72)

- Five colour swatches and the remove-highlight action retain their full >=44px hit area from the first rendered animation frame; no parent `scale()` can temporarily shrink them below the H7 target.
- The picker keeps the same position, colours, viewport clamping, focus behavior and 150ms opacity/vertical entrance motion.
- v101.71's >5 MiB self-export/restore symmetry and prototype-safe prayer deep-link routing remain unchanged.
- All earlier A-G behavior, v101.62 reader return/progress repair, future-snapshot guards and complete personal-data reachability remain preserved.
- Physical-device, installed-PWA and live-origin evidence remains pending and is never inferred from local browser/machine tests.

## 24H-G extreme-deep backup/deep-link/evidence repair (v101.71)

- Machine restore retains a finite **32 MiB** parser/file guard but no longer rejects a realistic valid self-export merely because pretty-printing pushed it above the historical 5 MiB ceiling.
- Regression fixture: 2,550 valid maximum-length notes produce a >5 MiB app-generated JSON backup; the exact exported File must be accepted by `handleImportFile()` and all 2,550 notes must survive the replace-import.
- The prayer registry is prototype-free and the startup prayer router validates an owned stable `PASSION24.*` ID before lookup. `__proto__`, `constructor`, `toString`, malformed and overlong IDs recover to Home with the normal invalid-prayer message; none can throw or execute markup/script.
- The inactive legacy integrity helper's stale `revue éditoriale en cours` string is corrected for evidence hygiene. No new integrity-check UI is introduced; the helper remains inactive/deferred architecture debt.
- v101.70 persistence downgrade guards, unlimited valid annotation preservation, whole-paragraph reachability/backup/journal/wide-preview truth, v101.62 reader-return repair, and every earlier A–G behavior remain preserved.
- Physical-device, installed-PWA and live-origin evidence remains pending and is never inferred from local browser/machine tests.

## 24H-G ultra-deep recheck finalization (v101.70)

- Preserves the exact v101.69 functional behavior; only release identity/current-facing evidence wording is advanced.
- Current-facing README claims now distinguish current evidence from historical corrective inputs; no older precursor is labelled as the current input.
- Future `snapshot_version` **and** future `schema_version` canonical records remain byte-preserved and block older durable writes/false complete machine backup.
- Valid notes, exact-text highlights and legacy whole-paragraph marks are not silently truncated by record-count sanitisation caps.
- Whole-paragraph marks are reachable/removable in Mon Espace, included in backup-reminder counts and the readable journal, and represented truthfully in the wide/tablet preview.
- Physical-device, installed-PWA and live-origin evidence remains pending and is never inferred from local browser/machine tests.

## 24H-G annotation-preview truth repair (v101.69)

- Wide/tablet Mon Espace preview includes resolved whole-paragraph marks as `Marquage de paragraphe`.
- Stale/missing text highlights and missing legacy marks are not silently ignored; the preview reports how many passages require review in full Mon Espace.
- `Aucun surlignage` is shown only when there are genuinely no text-highlight or whole-paragraph-mark records.
- The panel remains a three-item preview and links to full Mon Espace; no unbounded rendering is introduced.
- All v101.68/v101.67/v101.66/v101.65 and earlier A–G protections remain unchanged.

## 24H-G legacy-mark personal-data completion (v101.68)

- `personalDataRecordCount()` includes active whole-paragraph marks, so backup reminders are based on all annotation records rather than only exact-text highlights/notes.
- The human-readable journal includes every whole-paragraph mark, with a resolved passage excerpt or an explicit missing-target warning.
- Machine JSON export was already complete and remains unchanged.
- Mon Espace reachability/removal from v101.67 is preserved.
- High-count record preservation, future snapshot/schema protection, reader-return restoration, accessibility and all earlier A–G behavior remain unchanged.
- No protected corpus declaration or user-data schema version changes.

## 24H-G legacy paragraph-mark reachability repair (v101.67)

- Keeps the active whole-paragraph `◈` marking compatibility path and its stored IDs unchanged.
- Resolved paragraph marks now appear in Mon Espace alongside text highlights, explicitly labelled `Marquage de paragraphe`.
- Marks whose target paragraph no longer resolves now appear under `Passages à vérifier` instead of remaining hidden indefinitely.
- Every legacy mark shown in Mon Espace has an explicit transactional `Retirer le marquage` action; storage failure rolls the removal back.
- Preview limits remain UI previews only: combined totals are disclosed and `Voir tout` expands the complete list.
- Preserves v101.66 high-count personal-data completeness, v101.65 future-version protection and every earlier A–G correction.
- No protected corpus declaration or user-data schema version changes.

## 24H-G personal-data completeness repair (v101.66)

- Removes the hidden 200-record sanitisation cap on valid notes attached to one paragraph.
- Removes the hidden 200-record sanitisation cap on valid text-highlight records attached to one paragraph.
- Removes the hidden 5,000-ID sanitisation cap on the legacy paragraph-highlight list.
- These are **storage/data corrections**, not an instruction to render thousands of cards at once. Mon Espace may still use an explicit preview only when it states the total and provides `Voir tout`.
- Keeps per-record validation, note text maximum 2,000 characters, highlight field/range validation and the 5 MB machine-import size guard.
- Does not change the canonical snapshot/schema version; old records remain compatible.
- Preserves v101.65 future snapshot/schema protection, v101.63 touch-target correction, v101.62 reader-return/progress repair, and all earlier A–G behavior.
- Physical-device, installed-PWA and live-origin evidence remains pending and is never inferred from local tests.

## 24H-G persistence-safety completion (v101.65)

- A canonical record is future-owned when **either** `snapshot_version > 3` **or** `schema_version > 6`.
- Snapshot/schema versions must be positive integers; malformed version metadata is treated as malformed rather than silently trusted.
- Older supported schema generations are migrated to current v3/schema6 idempotently.
- While a future canonical generation is present, all current-version durable writes remain blocked and the raw canonical bytes stay untouched.
- Machine JSON export is blocked rather than falsely claiming a complete backup from only the future fields this older runtime understands.
- Note deletion, stale-highlight removal, preference and import failures report the actual preservation condition instead of a false storage-full diagnosis.
- Preserves all v101.64/v101.63/v101.62 Stage-G corrections.
- Physical-device, installed-PWA and live-origin evidence remains pending and is never inferred from local tests.

## 24H-G persistence-safety repair (v101.64)

- Future canonical snapshot versions are **never down-converted or overwritten** by this older runtime.
- Compatible future fields may be read into memory for the current session; the original raw canonical JSON remains untouched.
- R41 anchor-reset and stale-highlight persistence are bypassed while a future canonical snapshot is bound.
- Note/durable actions roll back with explicit future-version preservation wording; preference changes can remain session-only with honest unsaved feedback.
- Adds executable future-snapshot fixtures covering boot, missing migration marker, legacy mirrors, attempted Note write and attempted preference write.
- Preserves all v101.63 touch-target corrections and the v101.62 exact reader-return/progress repair.
- Physical-device, installed-PWA and live-origin evidence remains pending and is never inferred from local tests.

## 24H-G four-pass corrective hardening (v101.63)

- Preserves the v101.62 Hour → Mon Espace → Retour exact paragraph/tab/progress-strip repair.
- Completes the 44×44 CSS-px target on on-demand controls missed by the earlier primary-view scan: note indicator, Plan, theme choices, prayer/Plan close controls, Approfondir back/breadcrumb/index controls, cycle restart and side-panel close.
- The note indicator keeps its small visual dot; only its interactive hit area becomes 44×44.
- Refreshes current-facing report/QA identity and explicitly classifies v101.61/v101.62 raw audit files as inherited historical evidence rather than current execution claims.
- Physical-device, installed-PWA and live-origin evidence remains pending and is never inferred from local Chromium/static tests.


Historical corrective-repair input: the exact audited **v101.61 / 24H-G** candidate. v101.62 changes only reader-history continuity and progress-strip restoration after leaving the reader; corpus, storage schemas, Repères, contextual actions, deep-link contracts, navigation decisions and platform highlighting semantics remain unchanged.


## Historical 24H-G corrective repair (v101.62) — Mon Espace → Retour reader continuity

- Fixes the owner-reproduced v101.61 defect where leaving an Hour for **Mon Espace** and pressing **Retour** reopened only the Hour start instead of the exact reading position.
- Reader history now carries the Hour, active reader tab and a stable visible paragraph/visual offset snapshot.
- Returning to the reader restores that exact context and immediately re-enables/recalculates the top reading-progress strip.
- Legacy numeric reader-history entries remain accepted for compatibility.
- This repair does not change corpus declarations, note/highlight schemas, Repères, search/deep links, navigation structure, Apple exact-range highlighting or Samsung paragraph policy.

## Historical 24H-G candidate (v101.61) — accessibility / PWA hardening

Stage G keeps the approved 24H-F navigation and hardens cross-cutting release behavior: frequent interactive hit areas target 44×44 CSS px, reduced-motion behavior is reinforced, an unsaved Note draft blocks Actualiser, and the dynamic update banner is exposed as a polite status region. The service-worker strategy itself is preserved and re-certified rather than redesigned.

Physical iPhone/iPad/Samsung, installed-PWA and live GitHub Pages checks remain release-critical and must not be inferred from local browser/static evidence.

## Historical input baseline — 24H-F candidate (v101.60) — navigation prototype

- Primary bottom navigation is now **Accueil · Heures · Recherche · Mon Espace**.
- The existing top-header Search shortcut is deliberately preserved during the transition.
- **Approfondir is not deleted**: it remains prominent on Accueil, gains a direct entry on Heures, remains available within each Hour through linked texts/end actions, and stays in Réglages/sidebar.
- Search now owns the bottom-nav active state; Back from a result must restore query/filter/scroll context.
- `Espace` is renamed to the exact ecosystem label **Mon Espace**.
- This is a staging/user-acceptance prototype. Production certification requires owner/user acceptance and staging usability review; inherited Stage-E live-route and Stage-C device gates remain open.

Historical input baseline: **v101.58 / 24H-D**, explicitly authorised by the product owner as the input to 24H-E. Stage E changes only search normalisation, stable routing/linking, and privacy-safe support hooks. Protected corpus, personal-data schema, Repères and Stage-C selection/highlighting policies remain unchanged.

## Historical 24H-E candidate (v101.59) — search, deep links and support

- Preserves the six search filters and 140 ms debounce, while formalising a versioned **French search normalizer (`fr-v1`)** with fixtures for accents, `œ/oe`, `æ/ae`, apostrophes, NBSP/narrow spaces and case.
- Adds validated startup routes for `?open=hour&hour=<n>&pid=<stable-id>`, `?open=prayer&id=<stable-id>`, `?open=text&id=<stable-id>` and `?open=search&q=<query>`, with recoverable fallbacks for invalid targets.
- Adds **Lien** to the shared contextual action bar. It copies only a stable route; it never embeds selected text, notes or highlight content.
- Search-result opening continues to push the full Search state (query/filter/speaker/scroll/focus) so Back restores context.
- Adds **Signaler un problème de texte** and **Copier les diagnostics** in Aide/À propos. Both payloads are deliberately privacy-safe and exclude notes/highlight contents.
- No corpus declarations, stable IDs, speech offsets, personal-data schema, Apple exact-range policy, Samsung whole-paragraph policy, PWA `id/scope/start_url`, or navigation structure are changed.
- Local served-origin route/runtime tests and immutable-package audits are required. The roadmap also requires a live/staging-origin route test for production release; that remains pending unless separately executed.

Historical input baseline: **v101.57 / 24H-C repaired candidate**, explicitly authorised by the product owner as the input to 24H-D. Stage D changes only Mon Espace/personal-data UX. The inherited Stage-C physical-device gaps remain open and are not represented as passed.

## Historical 24H-D candidate (v101.58) — Mon Espace completeness and backup UX

- Separates **Passages à vérifier**, healthy **Surlignages**, **Notes**, and **Progression** rather than mixing stale records into the highlight preview.
- Every stale/recovery record, highlight group and note is reachable: each section has an explicit count and an expandable preview; there is no hard personal-data ceiling.
- Adds a local **Dernier export de sauvegarde** timestamp plus a gentle reminder only when meaningful personal data exists and no recent export is recorded.
- Keeps the machine-readable JSON export/import contract and adds a separate human-readable **Markdown journal export**, which is never accepted as a restore format.
- Does not change the canonical personal snapshot schema, corpus, stable IDs, speech offsets, highlighting schema, Repères, Apple exact-range policy or Samsung whole-paragraph policy.
- Stage-D package/browser gates must prove all records reachable and JSON round-trip preservation. Production certification remains limited by inherited Stage-C device evidence.

## Historical 24H-C iPhone picker repair (v101.57)

- Replaces the historical hard-coded `220 × 110 px` existing-highlight picker assumption with measurement of the actual rendered picker.
- Clamps the picker to the current `visualViewport`/viewport bounds with an 8 px margin and chooses an above/below position that fits.
- Adds a CSS `max-width`/`box-sizing` safety bound.
- Does **not** change highlight offsets, colours, persistence, note schema, contextual-action semantics, Apple exact-range policy or Samsung whole-paragraph policy.
- Product-owner evidence from v101.56: iPhone exact selection/highlighting works; Samsung/Android was not available for testing.
- v101.57 requires targeted real-iPhone confirmation of the repaired existing-highlight picker. Samsung/Android Stage-C remains `NOT_TESTED`.

Historical v101.56 checkpoint: **v101.55 / 24H-B** was the authorised input to 24H-C; at that checkpoint 24H-D had not yet started. 24H-D through 24H-G were subsequently authorised and executed.

## Historical 24H-C candidate (v101.56) — one contextual action component

- Range selections and paragraph targets now feed one internal target contract and one rendered contextual-action component: **Surligner · Copier · Note · Fermer**.
- The historical `#mobileActionBar` and `#selectionActionBar` business-logic paths are retired; compatibility wrapper function names feed `#contextActionBar`.
- iPhone/iPad/desktop exact selected-text offsets are preserved. Multi-paragraph range selections retain their per-paragraph canonical offsets.
- Samsung/Android explicit **Paragraphe** mode still avoids native word selection; tapping a paragraph now opens the same contextual component, and choosing Surligner then highlights the whole paragraph.
- Highlight range normalization and overlap detection have pure helpers with mutation/adversarial tests. Existing text hashes, paragraph fingerprints, grouped-highlight behavior and conservative stale-recovery logic remain unchanged.
- Notes remain paragraph-anchored and retain the existing transactional save/rollback schema; no note schema migration is introduced.
- The six protected corpus declarations remain byte-identical to v101.55.
- Physical-device validation of iPhone/iPad exact range and Samsung paragraph mode is release-critical for Stage C; static/browser PASS alone cannot certify production.

Historical input baseline: **v101.54 / 24H-A**, owner-confirmed as working before explicit authorisation to begin 24H-B. **v101.55 / 24H-B is the audited Repères baseline carried into 24H-C.**

## Historical 24H-B candidate (v101.55) — calm reader + optional Repères

- The former user-facing binary mode is retired. The neutral **Repères** control now governs only technical/source markers.
- Repères OFF hides paragraph numbers, source/page cues and speaker-attribution badges; direct-speech colours remain visible.
- **Note · Surligner · Copier remain available with Repères OFF or ON**, including desktop paragraph actions and existing mobile selection/long-press routes.
- Toggling Repères changes CSS classes only; it does not rebuild the reader. A semantic visible-anchor offset is restored after the layout change, while the DOM selection is preserved where the browser permits.
- Persisted `studyMode` / `lp24_mode` storage remains unchanged for this compatibility release. New exports include both `showReperes` and `studyMode`; old exports containing only `studyMode` restore the equivalent Repères preference.
- The six protected corpus declarations remain byte-identical to v101.54.
- Stage-B static/runtime acceptance passed before packaging. This payload is designated the audited-candidate target; immutable reopened-package and independent audit results remain the final authority and no production deployment is claimed.

## Historical — carried forward from 24H-A (v101.54) — display settings contract

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

## Historical corpus — the approved targeted change set (v101.52)

The first release since v101.44 in which the corpus itself changes, under an explicit approved
change-set instruction.

- **21 mandatory wording corrections.** All 21 targets required correcting (`CHANGED = 21,
  ALREADY_PRESENT = 0, UNMAPPED = 0`), applied as minimal clause-level edits rather than
  whole-paragraph rewrites. Measured against the untouched v101.51 corpus: exactly 21 of 1,839
  records changed, 0 unrelated, record-ID set identical.
- **65 non-destructive display segmentations, 180 display units.** Canonical ids, order and text
  are unchanged; every record's segment slices concatenate back to its canonical text exactly.
  Segments render through the app's existing canonical-coordinate renderer, so notes, highlights,
  saved positions keep resolving through the canonical parent id — no migration.
- **4 cross-record continuity operations**, both stable ids preserved in every group; copying
  either member of a group copies the whole grammatical unit.
- **The 3 expressly excluded stylistic constructions are untouched.**
- **Speech offsets recalculated by exact delta** for the 7 affected records; any boundary that
  would have fallen inside a replaced span was refused rather than approximated — none did.
- **Protected-declaration contract re-baselined**, not dropped: `CORPUS` and `SPEECH_DATA` moved by
  design; `TEXT_LIBRARY`, `HOUR_LINKED_TEXTS`, `INTERNAL_SUBHEADINGS` and `SPEECH_END_VISUAL_BREAKS`
  verified unchanged.

## Historical app fix (v101.53) — iPad bottom bar no longer covers the end of a view

Reported on the Approfondir screen: the bottom navigation partly hid the last card and it could not
be scrolled any further. Cause: `html.ios-device .content` is a flex column with `overflow-y: auto`,
and iOS Safari excludes such a container's `padding-bottom` from its scrollable overflow — the space
reserved for the bar evaporated on device even though the app reserves it correctly (Chrome honours
it, which is why this only showed on iPad). Fixed by reserving that space with a flex-item spacer
instead of padding, which cannot be dropped by that Safari behaviour.

## Historical — carried forward from v101.26–v101.51

Notes reachable from both mobile action bars; recovery for highlights broken by editorial
corrections, with a working **✕ Retirer** in Mon Espace; Mon Espace ordered newest-first with a
"Voir tout" expander so nothing is silently hidden; the note-panel iOS zoom/pan fix; the
service-worker update fix; speech punctuation restored across 99 paragraphs; progress/study-mode/
reset persistence fixes; meditated-hour border weight; dark-mode contrast fix; "Automatique" in
place of "Système"; Gethsémani Compléments cleanup.

## Historical real-device status — v101.53

**Confirmed by Louis** before the v101.53 promotion: reviewed the corpus text corrections, and confirmed
the iPad bottom-bar/scroll fix.

Internal history, the full version-by-version record, the corpus decision record (including the
v101.52 protected-declaration contract) and open items still tracked (a hardcoded corpus unit count
pending an independent recount; one unreproduced Android WebAPK install report) are in
`luisa-24h-state_1.md` in the project working directory.
