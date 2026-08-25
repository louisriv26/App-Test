# Current metadata semantic consistency — v101.118

Status: `PASS_PREPACKAGE`.

- `version.json.release_scope`, `metadata/scope_escalation_authority.md` and the active no-regression ledger identify the current v101.118 evidence-only scope.
- Generic `scripts/EXECUTION_SPEC.md` identifies `v101.118` / `FOUR_PASS_GENERIC_EXECUTION_SPEC_INTEGRITY_REPAIR_R1`.
- The previous v101.111 execution specification is preserved under the explicit historical path `scripts/historical/EXECUTION_SPEC_v101111.md`.
- `scripts/run_independent_prefreeze_audit.py` remains version-parameterized; it does not hard-code a current evidence version folder.
- Governed runtime declarations remain exact v101.117 parity.
