# M1.1 independent correction audit

**Status: PASS**

Checks: 25/25

| Check | Status | Evidence |
|---|---|---|
| H21_T35_UNIQUE_BODY_HEADING | PASS | [124] |
| H21_T35_SOURCE_MAP_COUNT | PASS | {"label": "Tome 35 — 22 mars 1938", "volume": 35, "date_iso": "1938-03-22", "status": "SYNCED_CURRENT_LDC_RA19B", "matched_entry_id": "LDC.T35.E0040", "matched_date_iso": "1938-03-22", "matched_title": "Dès que la créature se décide à vivre dans notre Vouloir, tout change pour elle, parce qu’elle est mise dans les mêmes conditions que la Divinité. Ce à quoi serviront les enfants du divin Fiat qui auront en eux la Vie de leur Père céleste. L’ultime regard d’Amour au moment de la mort.", "confiden |
| H21_T35_RUNTIME_RANGE | PASS | 125-179 |
| SOURCE_P023_MAPS_P147 | PASS | 147 |
| P146_IS_NOT_TARGET | PASS | 'Les enfants de notre Fiat nous permettront d’accomplir en eux notre Volonté. Ils seront par conséquent notre gloire, notre triomphe et notre victoire. Ils seront nos enfants véritables qui non seulement porteront notre image, mais la vie du Père céleste lui-même qui demeurera en eux comme leur propre Vie.' |
| P147_CONTAINS_TARGET | PASS | 'Ces enfants seront notre vie, nos cieux et nos soleils. Oh ! comme nous prendrons plaisir à créer en eux des vents qui soufflent l’amour et des mers qui murmurent : « Je vous aime, je vous aime. »' |
| P147_EXACT_167_194 | PASS | 167-194 |
| A16_INTERSECTION_SINGLETON | PASS | 1 |
| A16_SOURCE_ROW | PASS | {'segment_id': 'LDC.T35.E0040.P023.R3A31.0165.0192.GENERIC_SOUL.02', 'volume': '35', 'entry_id': 'LDC.T35.E0040', 'paragraph_id': 'LDC.T35.E0040.P023', 'current_speaker': 'GENERIC_SOUL', 'new_speaker': 'PERSONIFIED_VOICE', 'start_char': '167', 'end_char': '194', 'quotation_depth': '1', 'text': 'Je vous aime, je vous aime.', 'source': 'A14_HIGH_PRECISION_SHADOW_FULL_CONTEXT', 'reason': 'The quotation is explicitly murmured by created winds and seas formed in the children; created natural elements |
| A16_OFFSETS_MATCH_RUNTIME | PASS | 167-194 Je vous aime, je vous aime. |
| ACTION_COUNT_10 | PASS | 10 |
| ACTION_IDS_UNIQUE | PASS | ['M1-SA-001', 'M1-SA-002', 'M1-SA-003', 'M1-SA-004', 'M1-SA-005', 'M1-SA-006', 'M1-SA-007', 'M1-SA-008', 'M1-SA-009', 'M1-SA-010'] |
| SA010_TARGET_P147 | PASS | PASSION24.TEXT.RELATED_HOUR_21.BODY.P147 |
| SA010_NOT_P146 | PASS | {"action_id": "M1-SA-010", "target_id": "PASSION24.TEXT.RELATED_HOUR_21.BODY.P147", "class": "SEMANTIC_NESTED_PERSONIFIED_VOICE_MIRROR_DRIFT", "baseline_observation": "Runtime P147 contains the nested quoted words « Je vous aime, je vous aime. » at offsets 167–194 inside a JESUS outer presentation run 0–196; A16 identifies the inner words as PERSONIFIED_VOICE. P146 is a different paragraph and was the superseded off-by-one target in M1.", "source_backed_shadow_action": "Preserve JESUS visible pr |
| G3_40_ROWS | PASS | 40 |
| G3_80_BINDINGS | PASS | 80 |
| G4_PRIMARY_48 | PASS | 48 |
| G4_INDEPENDENT_48 | PASS | 48 |
| G4_PRIMARY_INDEPENDENT_AGREEMENT | PASS | mismatches=0 independent_nonpass_match=0 |
| GATE_MATRIX_10 | PASS | 10 |
| G1_G10_ALL_PASS | PASS | [] |
| DECISION_LOCK_PASS | PASS | PASS_EVIDENCE_FIXED_POINT |
| DECISION_LOCK_TARGET_P147 | PASS | target present |
| BASELINE_HASH_IMMUTABLE | PASS | 4e204832023ff8d6d71319caf854a94bda53f148258df700b8792789597294a8 |
| NO_V101111_CREATED | PASS | no v101111 artifact found |
