# R238 Independent Audit — v142.38 (16 October 2026)

## Decision
**HOLD; not deployable.** A seven-paragraph Tome-34 presentation pilot exists in a separate dev branch, but the full R237 28/21 structural repair is **absent**. All user-data/Reader/iOS/offline end-to-end gates remain open.

## Current Git evidence
- App Test main @ `8c036b4736d3ebde5bc816e772c29f05da54126d` (v142.37); no merge or deploy from branch.
- MAIN production @ `6f66f8c25f4bade8a59bbf03125bc8420878d7bb` (v142.34); no changes.
- Development branch current verified HEAD @ `7d100a1b44649c37bf53f95a1acdef81b5ca2e2a` with prior initial pilot commit `5555cd06c3689e0482df2ee23e39f8bdbd57fddb`.
- Baseline->dev Git diff has **zero corpus/ file changes**. Offline persistent content binding `38833ef76d248a6b55c1a09d460939781c30e081a2d7bbd27ed47aa7d9ed12ee` preserved.
- App/SW/offline app version synchronized as v2.19.142.38-R1B-UNIFIED; SHELL asset count increased from 39 to 40 (new JS); offline corpus manifest 205 assets and 119,244,276 bytes. Storage schema remains user-data v4 / IndexedDB internal v5.

## Behavioral controls completed, without overclaiming
- Actual `speech_model.js`, `ldc_r237_t34_visual_pilot.js` and real Tome 34 data: 97/97 module-level assertions including 7 guarded presentation cases and multiple corrupted-text/offset/segment controls. Real standalone Mary speaker interventions stay untouched.
- The model-level run-merging displayed a confirmed **hidden French closing guillemet** in 5/7 pilots. Current HEAD adds `restoreNestedClosingQuote()` invoked in real `openEntryCore()` **before** `LDCAnchor.indexFragment()`. Replayed 5/5 recovered cases (E0016.P009, E0018.P019, E0019.P010/P012/P018), 2/2 unaffected (E0019.P011/P014). Canonical paragraphs remain unchanged in the module tests.
- **Not proven:** DOM geometry, native Safari selection semantics, indexing after mark wrapping, actual HTML accessibility reader behavior, multi-fragment highlights, IndexedDB migration, offline upgrade, backup restore and physical devices. Synthetic PASS does not upgrade these gates.

## Release/integrity issues
1. **P0:** The original R237 structural adapter 28 paragraphs/21 boundaries is absent from current 142.38 dev source.
2. **P0:** Do not publish the repository GitHub archive as a deploy ZIP. The dev repository tree had 6,346 blobs vs 277 application files in `PACKAGE_MANIFEST_SHA256.json` (package + manifest -> 278 files). Build a separate exact application ZIP; the included safe builder is read-only against the source repository.
3. **P1 resolved in dev source:** initial 142.38 manifest used `localeCompare`, disrupting inherited code-point lexical order (262 differing positions). HEAD `7d100a1b44649c37bf53f95a1acdef81b5ca2e2a` has restored 277 entries in strict lexical order. Re-run independent SHA checks before final candidate.
4. **P1 editorial review only:** T34 E0019.P018 is semantically tagged MARY even though Jesus addresses Luisa and invites her to voice a love expression; screen-reader attribution can still announce Mary. No silent semantic mutation.
5. **P0:** Historical user state / offline / deployment QA not run. No App Test/MAIN authorization.
6. **P1 documentation:** An earlier summary misstated the SW shell change as 38->40; verified baseline 39 -> current 40.
7. **P1 master source integrity:** this reconstructed cumulative master comes from 32 parsed text windows of 31,654 original R237 lines; raw-byte equivalence with original R237 file has not been cryptographically established.

## Next action
Reunify original R237 exact code with T34 pilot in an isolated candidate, inspect real Reader coupling and native selections, rebuild deterministic package, execute independent and physical tests, then obtain explicit App Test GO and later separate MAIN GO.
