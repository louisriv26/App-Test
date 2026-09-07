# Build script vs files — v101.125

- Status: **PASS** only if `evidence/v101125/FULL_PACKAGE_BUILD_REPRODUCTION.json` is current and PASS.
- Baseline: immutable v101.124 ZIP SHA-256 `15b9fdb66fb07617ac8078fddb3e4076347390252a510c6eeb4b613f4a06d3ac`.
- Builder: `scripts/build_v101125_full_package_reconciliation.py`.
- Contract: baseline extraction + exact `metadata/full_build_overlay_manifest.json` must reproduce the complete current package-source tree and reconcile the current hash manifest.
- Deterministic ZIP freeze is permitted only after current reports, tooling, evidence and manifests are final.
Evidence: `evidence/v101125/FULL_PACKAGE_BUILD_REPRODUCTION.json`, `metadata/release_evidence_lifecycle.json`.
