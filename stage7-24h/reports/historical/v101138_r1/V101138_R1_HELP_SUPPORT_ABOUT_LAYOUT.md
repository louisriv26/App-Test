# v101.138 R1 — Help support / À propos layout successor

## Scope
v101.138 R1 is a UI/help-only successor of exact R2 SHA-256 `0ae4e7da4ec034952e0e596bb2c5ded947f7c7fade21c8974783de7308b0dbc5`. It introduces no canonical, linked-text, stable-ID, storage, annotation, preservation or source-critical mutation.

## User-facing changes
- The former cramped native support-button line is removed.
- A dedicated **Assistance** area presents two styled, accessible controls: **Signaler un problème de texte** and **Copier les diagnostics**, each with a short explanation.
- **Vie privée** is a separate section rather than being mixed into the support controls.
- **À propos des textes** is a dedicated provenance card showing version/revision, corpus fingerprint, French base edition, textual validation, reference principle and validation scope.
- On large screens the support actions use two columns; on mobile they stack vertically.
- The Help modal may expand to 900px on large screens while remaining responsive on mobile.

## Protected invariants
- CORPUS and TEXT_LIBRARY byte-identical to R2/R1.
- all 14 protected presentation/topology declarations byte-identical.
- corpus fingerprint unchanged `87733d22b5e899e23da263c37a2c2b30d85585b7a40f3dbf5b9ab4c05ae496d7`.
- evidence/v101137_r1 and evidence/v101137_r2 byte-identical.
- exact 79-row content authority unchanged.
- PRESERVE_MOVE remains evidence-only/not UI.
- support payload semantics unchanged; only their visual controls are reorganized.
