# Independent four-pass prepackage audit — v101.105

Overall status: **PASS**

This auditor is separately implemented from the build script and recomputes critical runtime and package-tree facts directly.

## Pass 1

- **PASS** — `baseline_exact_sha` — `"d08fa70a4931f8c2e997bc8bae46a8292ed9b14725346727852361a84cfdb664"`
- **PASS** — `root_runtime_parity` — `{"index":"62e232cfbc6b154305d0cb2987daf6f4d71aea05b5eb40af3d273a7c7ab31f9f","app":"62e232cfbc6b154305d0cb2987daf6f4d71aea05b5eb40af3d273a7c7ab31f9f"}`
- **PASS** — `required_prepackage_artifacts_present` — `[]`
- **PASS** — `protected_declarations_exact_semantic_parity` — `{"CORPUS":true,"TEXT_LIBRARY":true,"HOUR_LINKED_TEXTS":true,"SPEECH_DATA":true,"INTERNAL_SUBHEADINGS":true,"DISPLAY_SEGMENTS":true,"CONTINUITY_GROUPS":true,"LDC_LIBRARY_FLOW_LAYOUT":true}`
- **PASS** — `final_local_break_map_equals_v101101_native_speech_end_map` — `{"final_targets":125,"native_targets":125,"final_count":139,"native_count":139}`
- **PASS** — `final_cross_breaks_equal_v101101` — `[["PASSION24.TEXT.PROMISES_BENEFITS.BODY.P103","PASSION24.TEXT.PROMISES_BENEFITS.BODY.P104"]]`
- **PASS** — `quote_edge_join_population` — `[["PASSION24.TEXT.PART_III_DIVINE_PASSION.BODY.P159","PASSION24.TEXT.PART_III_DIVINE_PASSION.BODY.P160"],["PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P011","PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P012"],["PASSION24.TEXT.RELATED_HOUR_03.BODY.P018","PASSION24.TEXT.RELATED_HOUR_03.BODY.P019"],["PASSION24.TEXT.RELATED_HOUR_06.BODY.P053","PASSION24.TEXT.RELATED_HOUR_06.BODY.P054"],["PASSION24.TEXT.RELATED_HOUR_06.BODY.P068","PASSION24.TEXT.RELATED_HOUR_06.BODY.P069"],["PASSION24.TEXT.RELATED_HOUR_07.BODY.P036","PASSION24.TEXT.RELATED_HOUR_07.BODY.P037"],["PASSION24.TEXT.RELATED_HOUR_11.BODY.P058","PASSION24.TEXT.RELATED_HOUR_11.BODY.P059"],["PASSION24.TEXT.RELATED_HOUR_13.BODY.P039","PASSION24.TEXT.RELATED_HOUR_13.BODY.P040"],["PASSION24.TEXT.RELATED_HOUR_13.BODY.P047","PASSION24.TEXT.RELATED_HOUR_13.BODY.P048"],["PASSION24.TEXT.RELATED_HOUR_15.BODY.P174","PASSION24.TEXT.RELATED_HOUR_15.BODY.P175"],["PASSION24.TEXT.RELATED_HOUR_16.BODY.P009","PASSION24.TEXT.RELATED_HOUR_16.BODY.P010"],["PASSION24.TEXT.RELATED_HOUR_16.BODY.P076","PASSION24.TEXT.RELATED_HOUR_16.BODY.P077"],["PASSION24.TEXT.RELATED_HOUR_17.BODY.P010","PASSION24.TEXT.RELATED_HOUR_17.BODY.P011"],["PASSION24.TEXT.RELATED_HOUR_17.BODY.P053","PASSION24.TEXT.RELATED_HOUR_17.BODY.P054"],["PASSION24.TEXT.RELATED_HOUR_20.BODY.P015","PASSION24.TEXT.RELATED_HOUR_20.BODY.P016"],["PASSION24.TEXT.RELATED_HOUR_20.BODY.P029","PASSION24.TEXT.RELATED_HOUR_20.BODY.P030"],["PASSION24.TEXT.RELATED_HOUR_21.BODY.P064","PASSION24.TEXT.RELATED_HOUR_21.BODY.P065"],["PASSION24.TEXT.RELATED_HOUR_21.BODY.P067","PASSION24.TEXT.RELATED_HOUR_21.BODY.P068"],["PASSION24.TEXT.RELATED_HOUR_21.BODY.P080","PASSION24.TEXT.RELATED_HOUR_21.BODY.P081"],["PASSION24.TEXT.RELATED_HOUR_21.BODY.P091","PASSION24.TEXT.RELATED_HOUR_21.BODY.P092"],["PASSION24`

## Pass 2

- **PASS** — `runtime_identity` — `{"v":"v101.105","stage":"NATIVE_24H_PARAGRAPH_LDC_SEMANTIC_HYBRID_PRESENTATION_R1","joins":24}`
- **PASS** — `G_PRES_001_native_inline_Jesus` — `{"breaks":[],"hidden":2,"jesus":["Viens dans mes Bras que Je te pardonne. Le sceau de mon Pardon est mon Sang."],"domBreaks":0,"text":"Ce n’est pas seulement ta Voix, mais aussi ton Sang et tes Plaies qui crient à chaque cœur après le péché : « Viens dans mes Bras que Je te pardonne. Le sceau de mon Pardon est mon Sang. »","canonical":"Ce n’est pas seulement ta Voix, mais aussi ton Sang et tes Plaies qui crient à chaque cœur après le péché : « Viens dans mes Bras que Je te pardonne. Le sceau de mon Pardon est mon Sang. »"}`
- **PASS** — `all_24_quote_edges_group_and_no_orphan_geometry` — `{"tested":72,"bad":[]}`
- **PASS** — `IMG4532_and_shared_Samsung_topology` — `{"group":[{"id":"PASSION24.TEXT.RELATED_HOUR_20.BODY.P015","start":105,"end":177,"text":" Plus tard, en recevant l'absolution de mon confesseur, je me disais : «"},{"id":"PASSION24.TEXT.RELATED_HOUR_20.BODY.P016","start":0,"end":120,"text":"Mon Jésus, je veux recevoir l'absolution dans Ta Volonté.» Avant que j'aie pu dire un seul mot de plus, Jésus me dit : «"}],"ranges":[{"paraId":"PASSION24.TEXT.RELATED_HOUR_20.BODY.P015","start":106,"end":177,"text":"Plus tard, en recevant l'absolution de mon confesseur, je me disais : «"},{"paraId":"PASSION24.TEXT.RELATED_HOUR_20.BODY.P016","start":0,"end":120,"text":"Mon Jésus, je veux recevoir l'absolution dans Ta Volonté.» Avant que j'aie pu dire un seul mot de plus, Jésus me dit : «"}],"count":1}`
- **PASS** — `all_projection_DOM_reconstructs_canonical` — `{"n":2197,"bad":[]}`
- **PASS** — `speech_offsets_independent` — `{"targets":2197,"segments":3293,"bad":[]}`
- **PASS** — `H19_H21_locked` — `{"h19":[],"h21":[{"start":26,"end":93,"speaker":"JESUS"}]}`
- **PASS** — `runtime_no_console_errors` — `[]`

## Pass 3

- **PASS** — `full_regression_matrix_no_fail` — `{"rows":44,"failures":0}`
- **PASS** — `fix_ledger_no_fail` — `{"rows":4,"failures":0}`
- **PASS** — `protected_report_matches_recomputed` — `{"report_rows":8,"recomputed":{"CORPUS":true,"TEXT_LIBRARY":true,"HOUR_LINKED_TEXTS":true,"SPEECH_DATA":true,"INTERNAL_SUBHEADINGS":true,"DISPLAY_SEGMENTS":true,"CONTINUITY_GROUPS":true,"LDC_LIBRARY_FLOW_LAYOUT":true}}`
- **PASS** — `appwide_summary_matches_matrix` — `{"status":"PASS","static_runtime_prepackage_gate":"PASS","scenario_count":44,"pass_count":44,"failure_count":0,"not_tested":["physical Samsung","physical iPhone","physical iPad","installed PWA update","live GitHub Pages exact-byte binding","true airplane-mode/cold offline reopen","VoiceOver/TalkBack"],"release_ceiling_if_postpackage_audits_pass":"LIMITED_PASS_STATIC"}`

## Pass 4

- **PASS** — `quote_ledger_no_unresolved_or_catchall` — `{"events":1026,"bad":[]}`
- **PASS** — `no_speech_start_only_or_other_extra_break` — `{"extra":[],"final_breaks":139}`
- **PASS** — `no_v101104_generic_relocation_in_production` — `[]`
- **PASS** — `meaningful_fixture_quotes_remain_visible` — `[{"pid":"PASSION24.TEXT.RELATED_HOUR_17.BODY.P067","needle":"Voici l'homme","visible":true},{"pid":"PASSION24.TEXT.RELATED_HOUR_17.BODY.P067","needle":"Crucifie-Le","visible":true},{"pid":"PASSION24.TEXT.RELATED_HOUR_22.BODY.P063","needle":"J’ai soif","visible":true},{"pid":"PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P069","needle":"le Tout","visible":true}]`
- **PASS** — `embedded_stale_scan_zero_active` — `["v101.105 prepackage stale-reference scan (before final manifests)","files_scanned=69","patterns=9","hits=346","active_stale_failures=0","HISTORICAL_PROVENANCE_ALLOWED | README.md:5 | v101.103","HISTORICAL_PROVENANCE_ALLOWED | audit/independent_four_pass_audit.json:394 | v101.103","HISTORICAL_PROVENANCE_ALLOWED | audit/independent_four_pass_audit.json:395 | v101.103"]`
- **PASS** — `no_embedded_postpackage_final_evidence` — `[]`

## Not tested externally

- physical Samsung
- physical iPhone
- physical iPad
- installed-PWA update
- live GitHub Pages exact-byte binding
- true airplane-mode/cold offline reopen
- VoiceOver/TalkBack
