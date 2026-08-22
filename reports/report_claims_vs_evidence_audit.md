# Report claims vs evidence audit — pre-package

Active report files scanned: **29**.
PASS-like evidence tokens found: **79**.
Premature final-reopen PASS claims in active reports: **0**.
Prohibited embedded final PASS claims outside specification scripts: **0**.
PENDING tokens in active reports: **0**.

Evidence basis:

- syntax claims → `reports/prepackage_release_engineering_checks.json`;
- Chromium/runtime/topology/highlight claims → `reports/chromium_interaction_topology_results.json`;
- protected-data claims → `reports/protected_data_diff_report.csv` and release-scope parity checks;
- quotation claims → `reports/quotation_role_ledger.csv` + `reports/presentation_projection_summary.json`;
- root HTML identity → `reports/root_deploy_consistency_report.md`;
- stale references → `reports/stale_reference_scan.csv` / `.txt`;
- post-package deterministic/reopen/independent outcomes → deliberately `POST_PACKAGE_EXTERNAL`, never PASS inside this ZIP.

`PREPACKAGE_REPORT_INTEGRITY_GATE = PASS`

This is not the final release decision. The final decision lock is written externally only after both immutable-ZIP audits.
