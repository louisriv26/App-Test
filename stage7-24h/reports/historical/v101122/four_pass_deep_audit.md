# v101.122 four-pass deep audit

**PASS_PREFREEZE**

## Pass 1 — files vs build script
- Immutable v101.121 baseline hash: PASS.
- Current v101.122 builder reproduces the six governed runtime/release files byte-for-byte: PASS.
- Protected declarations: 14/14 byte-identical.
- `showHelp()` block: byte-identical to v101.121.
- Current prefreeze tooling is packaged and executed; post-freeze reopen tooling is packaged for execution only after immutable ZIP freeze.

## Pass 2 — runtime/package behaviour
- Hour-24 state matrix: 16/16 PASS.
- Five-profile Hour-24 UX matrix: 70/70 PASS.
- Help browser: 70/70 PASS.
- Broad Chromium: 52/52 PASS.
- Quoted-span fixed point: Scanner A 0 / Scanner B 0 across 398 relevant spans.
- Exhaustive presentation: 1,990/1,990 PASS.
- Service-worker logic: 15/15 PASS.
- Mutation tests: 12/12 synthetic defects detected.
- Independent Hour-24 probe: 55/55 PASS.
- Independent runtime smoke: 50/50 PASS.
- Independent presentation: 1,990/1,990 PASS; 257 cross-record spans.

## Pass 3 — active reports vs direct evidence
- Every nonblank active-report line is bound to direct evidence in `reports/active_report_line_audit.csv`; generic presence-only evidence is prohibited.

## Pass 4 — stale/contradiction/obsolete evidence
- Unexplained current-facing stale version/reference claims: 0.
- Obsolete current-tool semantic assumptions: 0.
- Current completion authority remains canonical `getProgressSnapshot().complete` (24/24 explicit Méditée states).

Final immutable ZIP reopen audits are external and are not claimed inside this package. Physical-device/live-origin gates remain NOT_TESTED.
