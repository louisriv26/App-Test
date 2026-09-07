# v101.119 M2 — authorised mutation integrity

- Fixed-point mutation targets: **45**.
- Projection targets changed: **45** exactly.
- Adjudication targets changed: **2** exactly: Hour-24 Désolation P033 and Related Hour-22 P090.
- Raw `SPEECH_DATA`: unchanged exactly.
- `CORPUS`, `TEXT_LIBRARY`, `HOUR_LINKED_TEXTS`: unchanged exactly.
- `VISIBLE_PARAGRAPH_TOPOLOGY`: unchanged exactly.
- P090 local projection break 215 removed inside `SPEECH_PRESENTATION_PROJECTION`; canonical text unchanged.
- P053/P068 projections remain byte/JSON-identical to the immutable v101.118 baseline.

Status: `PASS_MUTATION_SCOPE` pending post-mutation fixed-point/runtime checks.
