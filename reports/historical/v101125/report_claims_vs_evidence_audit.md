# Report claims vs evidence — v101.125

- Status: **PASS** only when both exact line coverage and claim-specific assertion checks pass.
- Current source-report universe is declared in `metadata/active_report_inventory.json`.
- Historical reports under `reports/historical/` are excluded from current claims.
- `reports/active_report_line_audit.csv` is self-excluded from its own source universe.
- Every nonblank source-report line is represented exactly once.
- Every claim line has a claim-specific evidence path and assertion ID; unrelated/generic evidence pointers are prohibited.
- Structural headings/schema rows are explicitly classified as structure rather than falsely treated as execution claims.
Evidence: `evidence/v101125/ACTIVE_REPORT_LINE_AUDIT_SUMMARY.json`, `evidence/v101125/REPORT_CLAIM_ASSERTIONS.json`.
