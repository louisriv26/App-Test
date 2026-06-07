# Real-device QA intake guide

Use this package to collect real-device evidence after deploying the nested GitHub Pages ZIP.

1. Deploy the contents of deploy/luisa_24h_github_deploy.zip.
2. Open the live URL on the required devices.
3. Execute REAL_DEVICE_QA_MATRIX.md.
4. Record results in REAL_DEVICE_QA_RESULTS_TEMPLATE.csv.
5. For every FAIL or LIMITED_PASS, complete BUG_REPORT_TEMPLATE.md and attach screenshots/videos.
6. Return the CSV and evidence files for Stage 5C-R1 triage.

Do not edit app code while testing. If the service worker appears stale, reload twice or clear site data and record exactly what happened.
