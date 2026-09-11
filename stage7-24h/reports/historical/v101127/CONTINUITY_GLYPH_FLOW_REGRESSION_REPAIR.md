# v101.127 Cross-Record Continuity Glyph-Flow Regression Repair

- Predecessor: `v101.126` / `87d812e39b14148a640dfc8095a8d07b25ce37e056e815d66c286c94638a0d85` / 434 members.
- User-reported regression: Hour 3 visually broke after `peines,` before `afin que…`.
- Root cause: `continuity-flow-fragment` and `.para-text` were inline, but the leader's final `.para-seg` from `DISPLAY_SEGMENTS` remained `display:block`, forcing a new line.
- Same mechanism also affected the Hour 13 continuity pair. The Hour 15 and two Hour 19 pairs were not affected because their boundary records have no `DISPLAY_SEGMENTS`.
- Repair is presentation-only: the final display segment of a continuity leader participates in the shared inline flow; the earlier internal segment rhythm is preserved by shifting the existing 0.9em break spacing to the preceding block segment.
- Canonical/devotional text changes in v101.127: **0**.
- The inherited governed textual universe remains **34 = 15 LDC-governed synchronizations + 19 native 24H/prayer repairs**.
- `CORPUS`, `TEXT_LIBRARY`, `SPEECH_DATA`, presentation projection/adjudications, visible topology, `DISPLAY_SEGMENTS`, `CONTINUITY_GROUPS`, LDC flow and LDC sync authority are byte-identical declarations to v101.126.
- Storage schema remains 8 and personal snapshot schema remains 5.
- Package-local status remains pre-final-reopen; post-freeze reopen/device evidence is external by design.
