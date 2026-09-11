# Build script vs files — v101.124

- Status: **PASS**.
- Baseline: immutable v101.123 ZIP SHA-256 `2959dfb832521af6f810d5f6b30ee187448aa799900993fd54ceae2b7c252b0d`.
- Builder: `scripts/build_v101124_full_package_reconciliation.py`.
- Contract: baseline extraction + exact `metadata/full_build_overlay_manifest.json` reproduces the complete current package-source tree; hash manifest reconciliation is mandatory.
- Deterministic ZIP freeze occurs only after all current reports/tooling/manifests are final.
Evidence: `evidence/v101124/FULL_PACKAGE_BUILD_REPRODUCTION.json`.
