# Real-device and live-origin QA checklist — v101.118

Status before physical/live execution: **NOT_TESTED**.

Candidate under test:

- App version: `v101.118`
- Build stage: `FOUR_PASS_GENERIC_EXECUTION_SPEC_INTEGRITY_REPAIR_R1`
- Final ZIP SHA-256: **fill from the external final decision lock after immutable ZIP freeze**

Use the exact frozen v101.118 ZIP. Record device model, OS/browser version, served/live origin where applicable, exact ZIP SHA-256, result and notes for every scenario.

## Samsung / Samsung Internet

1. Hour 3 duplicate regression: Judas/Jean sentences appear exactly once.
2. Hour 22 structure: each `« Jésus et Marie, je Vous recommande mon âme ! ».` is followed by `Jésus, je donne…` in a separate visible paragraph.
3. Paragraphe mode selects exactly one visible paragraph and does not cross the new Hour-22 boundary.
4. Highlight persists, recolours and deletes from Mon Espace.
5. No Google/Translate/Search overlay hijacks the Paragraphe workflow.
6. Long scroll and portrait/landscape continuity.

## iPhone / Safari

7. Hour 3 duplicate regression and Hour 22 paragraph/punctuation presentation.
8. Exact selected-text highlighting, persistence and Mon Espace reopen.
9. Nested quotation / divine-wrapper presentation regression fixtures.
10. Long-scroll/navigation/progress continuity.

## iPad / Safari — portrait and landscape

11. Hour 3 duplicate regression.
12. All ten Hour-22 punctuation cases and nine same-record visible splits.
13. Exact selected-text highlighting and orientation continuity.
14. No clipped reader/navigation controls.

## Installed PWA / live origin

15. Bind served `index.html`, `luisa_24_heures.html`, `version.json`, `sw.js`, `manifest.json` and icons to the intended v101.118 package.
16. Older installed version → v101.118 update; cache generation becomes `luisa-24h-v101-118`; personal data survives.
17. Close/reopen installed PWA and confirm version continuity.
18. True offline warm reopen after cache installation.
19. True offline cold reopen after full browser/app close and network disablement.

## Accessibility

20. Representative VoiceOver navigation/reader/actions.
21. Representative TalkBack navigation/reader/actions, including Samsung Paragraphe discoverability.

No physical/live/PWA/accessibility scenario may be marked PASS without direct execution evidence.
