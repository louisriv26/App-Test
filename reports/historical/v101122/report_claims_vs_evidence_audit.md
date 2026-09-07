# Report claims vs evidence audit — v101.122

**PASS_PREFREEZE — direct evidence bindings**

- Baseline identity/finality: PASS — external prerequisite `v101122_run/gate0/V101121_FINAL_DECISION_LOCK_EXTERNAL.json`; baseline ZIP SHA-256 `e22782a8dd73fb54287cd13d61b3ff217c4d24f33702bd1397dc1b4df5c34d3a`.
- Runtime build reproduction: PASS — `evidence/v101122/BUILD_RUNTIME_PARITY.json`.
- Protected declarations: PASS 14/14 — `evidence/v101122/PROTECTED_DECLARATION_PARITY.json`.
- Help parity: PASS — `evidence/v101122/HELP_PARITY.json`.
- JavaScript syntax: PASS — `evidence/v101122/JAVASCRIPT_SYNTAX_CHECK.json`.
- Service-worker syntax: PASS — `evidence/v101122/SERVICE_WORKER_SYNTAX_CHECK.json`.
- Hour-24 state transitions: PASS 16/16 — `evidence/v101122/HOUR24_STATE_TRANSITION_MATRIX.json`.
- Five-profile Hour-24 UX: PASS 70/70 — `evidence/v101122/HOUR24_FIVE_PROFILE_UX_MATRIX.json`.
- Help browser regression: PASS 70/70 — `evidence/v101122/HELP_BROWSER_MATRIX.json`.
- Broad Chromium regression: PASS 52/52 — `evidence/v101122/BROAD_CHROMIUM_RUNTIME_MATRIX.json`.
- Quoted-span fixed point: PASS A=0 / B=0 over 398 presentation-relevant spans — `evidence/v101122/post_hour24_fixed_point/M1_FIXED_POINT_SUMMARY.json`.
- Exhaustive presentation: PASS 1,990/1,990 — `evidence/v101122/EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX.json`.
- Service-worker logic: PASS 15/15 — `evidence/v101122/SERVICE_WORKER_LOGIC_MATRIX.json`.
- Mutation challenge: PASS 12/12 synthetic defects detected — `evidence/v101122/MUTATION_TEST_MATRIX.json`.
- Independent Hour-24 browser probe: PASS 55/55 — `evidence/v101122/INDEPENDENT_HOUR24_PROBE.json`.
- Independent runtime smoke: PASS 50/50 — `evidence/v101122/INDEPENDENT_RUNTIME_SMOKE.json`.
- Independent presentation: PASS 1,990/1,990 with 257 cross-record spans — `evidence/v101122/INDEPENDENT_PRESENTATION_MATRIX.json`.
- Physical iPhone/iPad/Samsung, installed-PWA, true-offline cold reopen and VoiceOver/TalkBack: NOT_TESTED; no PASS is inferred from browser emulation.
