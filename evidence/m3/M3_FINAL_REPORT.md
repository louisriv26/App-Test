# RA19E.2 M3 — runtime presentation matrix

**Final status: PASS_RUNTIME_PRESENTATION_MATRIX**

## Contract provenance
The historical wording of G17–G19 was not recovered. The M3 atomic contract is explicitly reconstructed from the approved four-macro-gate workflow and the documented runtime/presentation invariants; it is not represented as historical text.

## Primary runtime matrix
- Browser: system Chromium through Playwright content injection.
- Viewports: phone 390×844, tablet 820×1180, desktop 1200×900.
- G17: PASS
- G18: PASS
- G19: PASS
- Checks: 90/90 PASS.

## Independent runtime recheck
- Separate implementation using direct `renderParaText()`/`getFullParaText()` temporary-DOM probes.
- Does not reuse the primary `openLibraryText`/`openSection` navigation method.
- G17: PASS
- G18: PASS
- G19: PASS
- Checks: 102/102 PASS.

## Scope limitation
Normal URL/file navigation is blocked by the managed browser environment. These M3 checks therefore do **not** claim real service-worker registration, offline lifecycle, installed-PWA behaviour or physical iPhone/iPad/Samsung validation.

## Decision
M3 closes for the scoped RA19E.2 runtime-presentation reconciliation. M4 final immutable package lock is authorised.
