# LDC 142.17 — Adversarial source review (2026-10-08)

**Target:** branch `ldc-v142.17-reader-transaction-repair-candidate`, successor to evidence-complete v142.16 `d1970a527bf94325c78c2c396adf4987d9001a3e`.

## Adversarial challenge of the actual implementation

1. **A/B target race:** Queue target A and B before A's first animation frame. The obsolete A callback must not release B's programmatic scroll suppression. **PASS, source-extracted deterministic test.**
2. **Second frame race:** Start B after A enters its first animation frame. A's stale second callback must not release B's ownership. **PASS.**
3. **Exit/same-entry session:** Leave Reader or replace session without changing entry identity while RAFs are outstanding. No stale root reset or positioning. **PASS.**
4. **Source/volume/supplement:** Change active source, entry or supplement before RAF. Stale operations rejected. **PASS** for simulated identity transitions.
5. **Outside-scroller target:** Non-descendant target rejected without changing scroll. **PASS.**
6. **Shared epoch:** Explicit semantic restoration and entry-start enforcement now participate in the same single-owner protocol. Simulated interference between semantic restore and target placement: **PASS.**
7. **Compact mode:** Height threshold and hysteresis are measurement-based; no forced landscape or iPhone identifier. Deterministic boundary tests: **PASS**. Real geometry **OPEN**.
8. **Protection boundaries:** Git compare shows only four intended runtime files changed. Inherited protected assets remain Git blob-identical. **PASS within examined baseline; inherited SHA ledger is historical for untouched binary assets.**
9. **Release binding:** HTML, service worker, offline manifest and version metadata now agree on v142.17. **PASS at source level.**

## Remaining risks — not closed by these checks

- Safari viewport, short landscape, large text, documentary-status bar, toast, colour picker, selection panels and safe areas have NOT been demonstrated on actual rendered v142.17.
- An existing Reader callback outside the new ownership helpers may still affect edge cases; full integration is necessary.
- Focus/VoiceOver changes require device testing.
- Offline install/update behavior after worker version transition requires an installed PWA.
- No v142.17 hosted App-Test files have been served and compared to the source candidate.
- No production approval; no App-Test deployment approval.

**Verdict:** narrow Reader transaction corrections survive the executed source-extracted challenges; package and real-browser/physical gates remain separate. Do not label these results as a release PASS.
