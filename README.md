# Luisa — 24 Heures de la Passion

Version: `v101.32` — **staging / test build. NOT authorised for production.**

App SHA-256: `76f6cba7649167715374132e90fac0420d769b4cf50629b6fa49e69d9aeb08b6` (1,733,939 bytes). `index.html` and `luisa_24_heures.html` are byte-identical replicas.

## What's in this build

Three changes stacked on production v101.25.

**(1) The accepted v101.26 corpus.** 48 R3A text operations across 44 paragraphs — reverence capitalisation per the documented referent policy, grammar/agreement/punctuation fixes, and 9 substantive editorial items individually approved by Louis on 2026-07-27.

**(2) The v101.32 persistence correction.** v101.26 introduced `lp24_snapshot_v2` as the canonical personal-data snapshot but left three mutation paths writing only the old legacy keys, so the canonical snapshot went stale and won on the next load. Fixed by adding `state.lastHour` as the single live source for the resume Hour, making `applyPersonalSnapshot()` a pure in-memory apply (it previously wrote legacy storage, which is what overwrote newer values with older ones), and committing `openHour`, study mode and cycle reset through the canonical snapshot. `lp24_lastHour` and `lp24_mode` are now migration/mirror-only — live call sites dropped from 12 to 3. Production v101.25 never had these defects: it has no canonical snapshot layer, so no divergence was possible.

**(3) A speech-punctuation fix (P2-COLON).** v101.26 also deleted the introducing colon and its adjacent spaces from the *rendered* text of 99 paragraphs across 22 Hours plus the Approfondir section — "après le péché : « Viens dans mes Bras" displayed as "après le péchéViens dans mes Bras", and "qui Lui dit : « Fils, bénis-moi aussi ! » Ô Jésus" displayed as "qui Lui ditFils, bénis-moi aussi !Ô Jésus". Reported by Louis from screenshots of Hours 20 and 21. Cause: v101.26 moved 189 paragraphs' speech boundaries to exclude the guillemets, which made a quote-hiding regex fire that also swallowed the colon. Renderer-only fix — `CORPUS` and `SPEECH_DATA` are untouched. 98 of the 99 paragraphs now render byte-identically to production v101.25; the remaining one is an improvement (production left a narrow no-break space where a normal space belongs).

**(4) Meditated-hour boxes are easier to see.** The completed-Hour border goes from 1px to 2px in both light and dark, so border thickness now consistently means “meditated”. Until now only completed Holy Hours (5–7) got a 2px border — a side effect of the v101.20 fix — so the other 21 read as a faint edge. Border colour is unchanged in both themes. The completion tick also goes from 0.58rem to 0.66rem and from --accent-light to --accent, lifting it from 2.0:1 to 5.5:1 contrast in light mode. CSS only — no corpus, speech or behaviour change.

**(5) The Heures list view now matches the home grid,** with the same 2px meditated border and darker tick. While doing that I found and fixed a pre-existing dark-mode contrast failure: the « · Heure Sainte » label was hardcoded dark purple with no dark override, giving 2.18:1 against the dark card (WCAG AA needs 4.5:1). It now uses the lightened purple the home grid already used, measured at 6.32:1. Light mode was already 6.88:1 and is unchanged.

**(6) Theme option renamed.** The Automatique/Clair/Sombre (previously « Système ») theme-preference option now reads « Automatique » throughout - button label, settings-sheet description, quick-toggle tooltip, and the confirmation toast. Copy only; the stored preference value is still 'system', so no migration and no behaviour change.

**(7) A misplaced blurb was removed from a Complément.** « Les trois Heures de Gethsémani » (linked from Hours 5/6/7 and in Compléments) had two sentences that did not belong there - « Approfondir la Passion » and its description - left over from import. Removed; the item now shows only its genuine « Règle spéciale » sentence. This is a TEXT_LIBRARY content change, not CORPUS/SPEECH_DATA - no Hour text or speech attribution is affected. Verified live via the actual Hour 5 -> Approfondir path.

Carries all prior v101.x fixes (v101.2 through v101.26). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure, protected declaration hashes) pass; the persistence correction is proven by executable browser tests using genuine reload cycles; the punctuation fix is proven by simulating the renderer over the whole corpus. Real-device validation is `NOT_TESTED` — that is what this staging build is for. The Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) remains under investigation.

## What to test on device — priority order

Items 1–3 are the persistence fix. Each needs a **full app close and reopen** (not just backgrounding) between the action and the check.

1. **Resume Hour is remembered.** Open an Hour, read a little, close the app completely, reopen. The home screen must offer "Reprendre la lecture" pointing at that same Hour.
2. **Study mode sticks.** Toggle the `#` study-marks button on, close the app completely, reopen. Study marks must still be on.
3. **Reset stays reset.** With some progress recorded, use "Recommencer les 24 Heures" / "Réinitialiser ma progression" and confirm. Close the app completely, reopen. There must be **no** "Reprendre la lecture" card — the home screen should offer "Prier la 1re Heure". *This was the worst defect: the old resume Hour came back after a reset.*
4. **Speech punctuation reads correctly.** Spot-check the Seven Words headings in Hours 20–22 and any "Il te dit : …" lead-in. Expected: `La première Parole : Père, pardonne-leur car ils ne savent pas ce qu'ils font !` — colon present, a space either side of the speech, and **no** guillemets. Hours 8, 17, 19, 21 and 22 have the most instances; the Approfondir section has 20.

Then, in rough order of risk:

5. **Upgrade with existing data.** On a device that already has the production build installed with real notes, highlights and progress, upgrade to this build and confirm nothing is lost. This is the highest-risk untested path — every existing user will take it.
6. Notes, highlights and progress still save and survive a reopen.
7. Export / import round-trip.
8. Offline launch after first load; the "Actualiser" update flow.
9. General reading, search (including the Réflexions filter), Hour 24 burial + Désolation structure.

## Known limits — not defects

- **Deliberately not fixed in v101.32**, deferred to a later candidate: behaviour when device storage is full or unavailable, malformed/future snapshot recovery, atomic R41 highlight-anchor reset, and honest "not saved" messaging across all mutation paths. If a save fails because storage is full, the app may still report success. Known and out of scope.
- **R3B reflection completeness is not certified** — the supplied Italian edition does not contain the complete *Riflessioni e Pratiche*.

## Desktop verification already completed

```text
Semantic preservation         PASS   CORPUS/SPEECH_DATA/INTERNAL_SUBHEADINGS byte-identical to accepted v101.26
Speech-quote suppression      PASS   378 paragraphs, 270 ranges; hides only guillemets and whitespace
                                     (same guard FAILS with 67 findings on v101.26)
Persistence tests             6/6 PASS post-fix; 3/6 pre-fix (suite proven to detect the defects)
Static resilience guards      16/16
Corpus integrity              44/44
Mutation teeth                11/11 caught
Storage-contract audit        20/20 keys, 0 unclassified
Predeploy check               all passed, 0 warnings
```
