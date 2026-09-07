# Cross-record continuity product contract — v101.124

- Scope: presentation continuity only; canonical text and stable paragraph IDs remain unchanged.
- Approved continuity universe: exactly five leader→follower pairs recorded in `CONTINUITY_GROUPS`.
- Visual contract: each approved pair renders as one inline grammatical flow with exactly one ordinary space between record texts.
- Stable-ID contract: leader and follower remain separately addressable `.para-block` fragments with their original `id` and `data-para-id`.
- Annotation contract: notes/highlights/deep links retain record-level identity.
- Repères contract: one paragraph-number/speaker header is shown for the visual continuity unit; no mid-sentence follower paragraph number is inserted.
- Fail-closed contract: grouping occurs only when the approved follower is immediately adjacent in the rendered paragraph sequence.
- No automatic broad punctuation heuristic is used at runtime.
Evidence: `evidence/v101124/CONTINUITY_RUNTIME_MATRIX.json`, `evidence/v101124/CONTINUITY_MUTATION_TESTS.json`.
