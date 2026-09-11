# v101.138 R2 — release/accessibility cleanup

## Scope
This build is a narrowly bounded successor of exact v101.138 R1 SHA-256 `a1b996c766e5b912f0eceb88ff9b4a1c38c3f7c2bf296f2c7d4f7c3f666d373a`. No corpus/source-critical mutation is authorized or introduced.

## Implemented repairs
1. `helpJumpTo()` now resolves either `.help-section-hd` or `.help-feature-title`, so activating **Signaler un problème** scrolls to Assistance and transfers keyboard/screen-reader focus to `#help-support-title`. Existing Help sections continue to use `.help-section-hd`.
2. Six stale `_r2_to_r3` keys in `metadata/build_provenance.json` are replaced with final v101.137 R2 → v101.138 R2 lineage names; all six values remain zero.
3. Active provenance wording distinguishes the **observed live predecessor** from the **exact SHA-bound immutable builder input**. Live-origin exact-byte binding remains an external gate.
4. Version/build/cache/release evidence is refreshed to v101.138 R2.

## Protected invariants
- CORPUS and TEXT_LIBRARY are byte-identical to v101.138 R1.
- all 14 protected declarations are byte-identical.
- corpus fingerprint remains `87733d22b5e899e23da263c37a2c2b30d85585b7a40f3dbf5b9ab4c05ae496d7`.
- stable IDs and record order are unchanged.
- `evidence/v101137_r1`, `evidence/v101137_r2`, and predecessor `evidence/v101138_r1` remain byte-identical.
- storage schema 8 and personal snapshot schema 5 are unchanged.
- exact 79-row source-critical authority and PRESERVE_MOVE evidence-only visibility remain unchanged.
- approved `Validation textuelle`, `Principe de référence`, and `Portée de cette validation` wording is unchanged.

Final public deployment remains unauthorized pending the external live/device/PWA/offline/accessibility gates.
