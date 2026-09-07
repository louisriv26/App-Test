# Evidence-schema and direct-report-binding reconciliation — v101.125

- v101.124 application/runtime evidence reruns remain PASS, but its report/evidence layer is superseded for current continuation.
- Reproduced v101.124 defect A: some active report lines were bound to evidence that did not directly prove that specific claim.
- Reproduced v101.124 defect B: current generated evidence contained older schema identifiers (`V101123` / `V101121`) while current v101.124 tools had already moved some schemas forward.
- Reproduced v101.124 defect C: the v101.124 stale scanner did not include the current `evidence/v101124` tree, so its zero-stale-reference claim did not cover current evidence artifacts.
- v101.125 corrects only release identity, current evidence schemas, stale-scan scope and claim-specific report bindings.
- Functional application behaviour is unchanged after normalising release identity.
Evidence: `evidence/v101125/V101124_DEEP_FOUR_PASS_FINDINGS.json`, `evidence/v101125/FUNCTIONAL_HTML_PARITY.json`, `evidence/v101125/CURRENT_EVIDENCE_SCHEMA_AUDIT.json`.
