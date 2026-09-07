# v101.133 Boundary-Universe Evidence Reconciliation — v101.134 corrective authority

## Finding

The immutable v101.133 application repair remains functionally supported, but its package-local release-engineering evidence was incomplete:

1. `M1_09_PRE_EDIT_FIXED_POINT_MANIFEST.json` names `M1_04_RUNTIME_BOUNDARY_UNIVERSE.csv`, but that artifact was absent from the locked v101.133 package.
2. `scripts/reconstruct_runtime_boundary_universe.py` was added by the v101.133 overlay but omitted from `metadata/current_tooling_inventory.json`.
3. That packaged helper classified raw DOM markers incorrectly and failed to reproduce the stated 1,748 effective runtime-boundary universe.
4. Several named M3 deliverables required by the master script were not embedded as separately named package-local artifacts even though the underlying passing evidence existed.

This is a **release-engineering/evidence reproducibility defect**, not a new renderer defect. Immutable v101.133 is not modified.

## Corrected runtime-boundary definition

Direct browser reconstruction from the immutable v101.132 baseline and the functionally equivalent v101.133 renderer yields:

- raw synthetic DOM markers: **1,858**
- non-block markers excluded: **105**
- local wrapper-only markers with no visible semantic content after the boundary: **5**
- effective user-visible synthetic boundaries: **1,748**

Effective family decomposition:

- LDC cross-record: **1,467**
- display-segment: **122**
- LDC intra-record block boundary: **78**
- local speech/presentation block boundary: **80**
- speech cross-record: **1**

Total: **1,748**.

The five wrapper-only exclusions are not user-visible paragraph starts. The 82 positive alignment loci remain completely contained in the corrected 1,748-row universe; their composition remains **78 speech/presentation + 4 LDC intra-record**.

## Historical-manifest restraint

The v101.133 M1 manifest recorded a historical `M1_04_RUNTIME_BOUNDARY_UNIVERSE.csv` identity that is not present in the locked package. v101.134 does **not** fabricate that missing historical byte-stream or rewrite the historical manifest. Instead, it embeds a newly generated, directly reproducible R2 boundary-universe artifact plus raw-marker and exclusion ledgers, clearly labelled as a later reconciliation.

## Corrective scope

v101.134 is release-engineering-only:

- canonical text changes: **0**
- renderer behavior changes relative to v101.133: **0**
- speaker adjudication changes: **0**
- topology/offset changes: **0**
- storage/schema changes: **0**

The successor corrects current package identity, tooling inventory, gate mapping, package-local evidence completeness and reproducibility reporting, then reruns the complete v101.133 functional suite and the strengthened four-pass audit.
