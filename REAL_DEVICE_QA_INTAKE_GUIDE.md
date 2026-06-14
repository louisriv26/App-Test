> HISTORICAL_CARRIED_FORWARD_RECORD_NOT_CURRENT_GATE: This file is retained for provenance only. It is not a current Stage 6O.1 package gate result. Old package names, old PASS/FAIL rows, and old error counts inside this file are superseded by metadata/final_decision_lock.json, audit/final_reopen_audit.md, and audit/independent_four_pass_audit.md for the current package.

# Stage 6L-B QA intake guide — prototype-97

## Required submission per tester
1. Device model.
2. OS version.
3. Browser/app mode.
4. URL or install source used.
5. App version visible in the app.
6. Completed CSV rows from `REAL_DEVICE_QA_RESULTS_TEMPLATE.csv`.
7. Screenshots or short screen recording for each PASS/FAIL area.
8. Exact reproduction steps for each FAIL.

## Result vocabulary
- PASS: physically tested on the stated device and passed.
- FAIL: physically tested and failed; attach proof.
- BLOCKED: tester could not complete because of environment or access issue.
- NOT_TESTED: no real-device evidence.

Do not promote the package above LIMITED_PASS_STATIC until required real-device rows are PASS or explicitly accepted as risk.
