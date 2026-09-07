# Report claims vs evidence audit — v101.123

**PASS_PREFREEZE — direct evidence bindings**

- v101.122 deep re-audit findings: `evidence/v101123/V101122_DEEP_FOUR_PASS_FINDINGS.json`.
- Full-package build contract/reproduction: `scripts/build_v101123_full_package_reconciliation.py` plus `metadata/full_build_overlay_manifest.json` and current manifests.
- Functional HTML parity: `evidence/v101123/FUNCTIONAL_HTML_PARITY.json`.
- Protected declarations: `evidence/v101123/PROTECTED_DECLARATION_PARITY.json`.
- Help parity: `evidence/v101123/HELP_PARITY.json`.
- JavaScript syntax: `evidence/v101123/JAVASCRIPT_SYNTAX_CHECK.json`.
- Service-worker syntax: `evidence/v101123/SERVICE_WORKER_SYNTAX_CHECK.json`.
- Hour-24 state transitions: 16/16 — `evidence/v101123/HOUR24_STATE_TRANSITION_MATRIX.json`.
- Five-profile Hour-24 UX: 70/70 — `evidence/v101123/HOUR24_FIVE_PROFILE_UX_MATRIX.json`.
- Help browser: 70/70 — `evidence/v101123/HELP_BROWSER_MATRIX.json`.
- Broad Chromium: 52/52 — `evidence/v101123/BROAD_CHROMIUM_RUNTIME_MATRIX.json`.
- Quoted-span fixed point: A=0 / B=0 / 398 relevant spans — `evidence/v101123/fixed/M1_FIXED_POINT_SUMMARY.json`.
- Exhaustive presentation: 1,990/1,990 — `evidence/v101123/EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX.json`.
- Service-worker logic: 15/15 — `evidence/v101123/SERVICE_WORKER_LOGIC_MATRIX.json`.
- Mutation detection: 12/12 — `evidence/v101123/MUTATION_TEST_MATRIX.json`.
- Independent Hour-24: 55/55 — `evidence/v101123/INDEPENDENT_HOUR24_PROBE.json`.
- Independent runtime: 50/50 — `evidence/v101123/INDEPENDENT_RUNTIME_SMOKE.json`.
- Independent presentation: 1,990/1,990; 257 cross-record spans — `evidence/v101123/INDEPENDENT_PRESENTATION_MATRIX.json`.
- Physical iPhone/iPad/Samsung, installed PWA, true-offline reopen, live-origin exact-byte binding and VoiceOver/TalkBack remain NOT_TESTED.
