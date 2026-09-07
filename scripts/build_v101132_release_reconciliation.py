#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,zipfile,shutil,sys
PRE_SHA='2932131da56ed1c02efb1507b5529f4cbb51bfa370691944cf0bd6c34fb01fa2'
PRE_MEMBERS=659
VERSION='v101.132'; STAGE='DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION_R1'; DATE='2026-09-03'; CACHE='luisa-24h-v101-132'
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''): h.update(c)
 return h.hexdigest()
def writej(p,o): p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def files(root): return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}
def build(pre_zip,out,tools,source_audit,frozen_csv,prefreeze=None,fourpass=None):
 pre_zip=Path(pre_zip);out=Path(out);tools=Path(tools);source_audit=Path(source_audit);frozen_csv=Path(frozen_csv)
 assert sha(pre_zip)==PRE_SHA
 with zipfile.ZipFile(pre_zip) as z:
  assert len(z.infolist())==PRE_MEMBERS and z.testzip() is None
  shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True);z.extractall(out)
 base_html=(out/'index.html').read_text(encoding='utf-8');assert base_html==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 assert "const APP_VERSION = 'v101.131';" in base_html and "const APP_EVIDENCE_STAGE = 'GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR_R1';" in base_html
 new=base_html.replace("const APP_VERSION = 'v101.131';",f"const APP_VERSION = '{VERSION}';",1).replace("const APP_EVIDENCE_STAGE = 'GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",1).replace("const BUILD_DATE = '2026-09-03'; // v101.131 / global raw-quote host-sentence successor; no canonical text mutation",f"const BUILD_DATE = '{DATE}'; // {VERSION} / deep four-pass release-engineering reconciliation; no functional or canonical text mutation",1)
 (out/'index.html').write_text(new,encoding='utf-8');(out/'luisa_24_heures.html').write_text(new,encoding='utf-8')
 # archive current predecessor report
 rp=out/'reports/GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR.md'; dest=out/'reports/historical/v101131/GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR.md';dest.parent.mkdir(parents=True,exist_ok=True);shutil.move(rp,dest)
 # identity files
 v=json.loads((out/'version.json').read_text());v.update({'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,'release_scope':'Release-engineering-only successor of immutable v101.131 after an independent deep four-pass audit. No corpus, speech, presentation, topology, continuity, storage-schema or user-state functional changes. Corrects stale operational QA/specification files, embeds the frozen raw-text gate authority, reconciles tooling inventory to the actual gate harnesses, and repairs full-overlay accounting.','overall_release_status':'LIMITED_PASS_STATIC__EXTERNAL_VALIDATION_OPEN','real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.132.','known_blockers':[],'external_open_gates':['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update from v101.131','true offline cold reopen','VoiceOver/TalkBack representative testing'],'postfreeze_reopen_evidence':'External SHA-bound decision/evidence; not embedded after immutable freeze.'});writej(out/'version.json',v)
 m=json.loads((out/'manifest.json').read_text());m['version']=VERSION;writej(out/'manifest.json',m)
 sw=(out/'sw.js').read_text(); assert sw.startswith('/* v101.131 */') and "luisa-24h-v101-131" in sw; sw=sw.replace('/* v101.131 */','/* v101.132 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-131';",f"const CACHE_NAME = '{CACHE}';",1);(out/'sw.js').write_text(sw)
 # operational docs corrected
 (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION}\n\nRelease-engineering-only successor of immutable v101.131.\n\n## Deep four-pass reconciliation\n\n- Functional/canonical application state is unchanged from v101.131.\n- Corrects the stale v101.122 `scripts/EXECUTION_SPEC.md` and `REAL_DEVICE_QA_CHECKLIST.md`.\n- Embeds the frozen `02_ALL_TEXT_RECORD_UNIVERSE.csv` required to rerun the permanent raw-text and mutation-detection gates.\n- Reconciles `current_tooling_inventory.json` to the actual 14 gate harnesses, including the 52-check broad runtime and primary 2,000-check presentation matrices.\n- Repairs `full_build_overlay_manifest.json` so package/hash manifests are included in the full changed-file universe.\n- Physical-device/PWA/offline/screen-reader/live-origin validation remains external.\n''',encoding='utf-8')
 (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(f'''# Real-device QA checklist — {VERSION}\n\nPackage under test must match the final locked v101.132 ZIP SHA-256 published in the external decision lock and report `{VERSION}` in Aide.\n\n## Required external gates\n- iPhone: core navigation, exact-selection highlighting, Hour-24 terminal layout, bottom navigation, updated M1C001–M1C004 presentation.\n- iPad portrait/landscape: same plus orientation and scroll containment.\n- Samsung/Android: whole-paragraph highlighting, Hour-24 terminal layout, bottom navigation, updated M1C001–M1C004 presentation.\n- Installed PWA update from v101.131, close/reopen, and true offline cold reopen.\n- VoiceOver/TalkBack representative navigation and speech-label checks.\n- Live origin must be byte-bound to the final locked ZIP before any deployment claim.\n\nRecord results in `REAL_DEVICE_QA_RESULTS_TEMPLATE.csv`. Browser emulation is not physical-device evidence.\n''',encoding='utf-8')
 (out/'scripts/EXECUTION_SPEC.md').write_text(f'''# Execution specification — {VERSION}\n\nStage: `{STAGE}`\n\nPurpose: release-engineering-only reconciliation of immutable v101.131 after a deeper four-pass audit. No functional/display/canonical text mutation is authorised.\n\nPass 1: reproduce predecessor/build lineage; verify manifests and full overlay; verify every active operational document; verify all gate scripts and required evidence inputs resolve from the package.\n\nPass 2: rerun the 14 runtime/package gate families on the candidate, including raw-text completeness, mutation detection, continuity, Méditée, Hour 24, Help, two independent presentation matrices, broad runtime and service-worker logic.\n\nPass 3: parse every line of the sole active report and bind each claim to current package/evidence.\n\nPass 4: search active surfaces for stale versions/stages, stale FAIL/PASS claims, stale counts, obsolete harness references, missing dependencies and contradictions with the external-open-gate boundary.\n\nAfter correction: repeat all four passes, freeze deterministic Build A/B, reopen the exact ZIP, rerun all gates and the four passes on that exact extraction, perform an independent meta-audit, and write the SHA-bound external decision lock last.\n\nProtected byte-for-byte from v101.131 except release identity: CORPUS, TEXT_LIBRARY/HOUR_LINKED_TEXTS, speaker/presentation authorities, DISPLAY_SEGMENTS, VISIBLE_PARAGRAPH_TOPOLOGY, continuity groups, notes/highlights behavior, storage schema and personal snapshot schema.\n\nPhysical-device, installed-PWA, true-offline, VoiceOver/TalkBack and live-origin evidence remain external.\n''',encoding='utf-8')
 # current evidence root
 ev=out/'evidence/v101132';shutil.rmtree(ev,ignore_errors=True);(ev/'authority').mkdir(parents=True);(ev/'source_audit_v101131').mkdir(parents=True)
 shutil.copy2(frozen_csv,ev/'authority/02_ALL_TEXT_RECORD_UNIVERSE.csv')
 shutil.copy2(out/'evidence/v101131/m1/BLIND_FREEZE_MANIFEST.json',ev/'authority/BLIND_FREEZE_MANIFEST.json')
 shutil.copy2(out/'evidence/v101131/V101131_APPROVED_MUTATION_LEDGER.csv',ev/'authority/V101131_APPROVED_MUTATION_LEDGER.csv')
 for p in source_audit.iterdir():
  if p.is_file(): shutil.copy2(p,ev/'source_audit_v101131'/p.name)
 if prefreeze: shutil.copytree(Path(prefreeze),ev/'prefreeze',dirs_exist_ok=True)
 if fourpass: shutil.copytree(Path(fourpass),ev/'prefreeze_four_pass',dirs_exist_ok=True)
 # current tools overlay
 for p in tools.iterdir():
  if p.is_file(): shutil.copy2(p,out/'scripts'/p.name)
 current=['scripts/build_v101132_release_reconciliation.py','scripts/freeze_v101132_deterministic.py','scripts/run_v101132_four_pass.py','scripts/run_v101132_release_integrity.py','scripts/run_v101132_global_raw_quote_gate.py','scripts/run_v101132_runtime_presentation.py','scripts/run_v101132_mutation_tests.py','scripts/run_v101132_meditee_regression.py','scripts/run_v101132_meditee_responsive_regression.py','scripts/run_v101132_hour24_regression.py','scripts/run_v101132_help_browser_matrix.py']
 reused=['scripts/run_v101127_strict_continuity_glyph_flow_matrix.py','scripts/run_v101128_legacy_continuity_matrix.py','scripts/run_v101119_exhaustive_presentation_matrix.py','scripts/run_v101121_independent_presentation_matrix.py','scripts/run_broad_runtime_matrix.py','scripts/run_sw_logic_matrix.js']
 writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'stage':STAGE,'current_tools':current,'reused_validated_runtime_lineage':reused,'rule':'Every harness used by the current 14-family release gate suite is listed here; package-local gate inputs are mapped by current_gate_map.json.'})
 gate_map=[
 {'gate':1,'script':'scripts/run_v101132_release_integrity.py','inputs':['predecessor v101.131 index.html','index.html']},
 {'gate':2,'script':'scripts/run_v101132_global_raw_quote_gate.py','inputs':['index.html','evidence/v101132/authority/02_ALL_TEXT_RECORD_UNIVERSE.csv']},
 {'gate':3,'script':'scripts/run_v101132_runtime_presentation.py','inputs':['index.html']},
 {'gate':4,'script':'scripts/run_v101132_mutation_tests.py','inputs':['index.html','evidence/v101132/authority/02_ALL_TEXT_RECORD_UNIVERSE.csv']},
 {'gate':5,'script':'scripts/run_v101127_strict_continuity_glyph_flow_matrix.py','inputs':['index.html']},
 {'gate':6,'script':'scripts/run_v101128_legacy_continuity_matrix.py','inputs':['index.html']},
 {'gate':7,'script':'scripts/run_v101132_meditee_regression.py','inputs':['index.html']},
 {'gate':8,'script':'scripts/run_v101132_meditee_responsive_regression.py','inputs':['index.html']},
 {'gate':9,'script':'scripts/run_v101132_hour24_regression.py','inputs':['index.html']},
 {'gate':10,'script':'scripts/run_v101132_help_browser_matrix.py','inputs':['index.html']},
 {'gate':11,'script':'scripts/run_v101119_exhaustive_presentation_matrix.py','inputs':['index.html','evidence/v101131/prefreeze/V101131_PRESENTATION_LEDGER.csv']},
 {'gate':12,'script':'scripts/run_v101121_independent_presentation_matrix.py','inputs':['index.html','evidence/v101131/prefreeze/V101131_PRESENTATION_LEDGER.csv']},
 {'gate':13,'script':'scripts/run_broad_runtime_matrix.py','inputs':['index.html']},
 {'gate':14,'script':'scripts/run_sw_logic_matrix.js','inputs':['sw.js']},]
 writej(out/'metadata/current_gate_map.json',{'version':VERSION,'stage':STAGE,'gate_families':gate_map,'package_local_dependency_rule':'All non-predecessor gate inputs resolve inside this package.'})
 writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'stage':STAGE,'source_reports':['reports/DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION.md'],'historical_reports_root':'reports/historical/','rule':'Only the listed report is current for v101.132; v101.131 and earlier reports/evidence are predecessor/historical lineage.'})
 writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'stage':STAGE,'current_evidence_root':'evidence/v101132','predecessor_24h':{'version':'v101.131','sha256':PRE_SHA},'source_audit':'evidence/v101132/source_audit_v101131','frozen_raw_authority':'evidence/v101132/authority/02_ALL_TEXT_RECORD_UNIVERSE.csv','rule':'v101.131 and earlier evidence is predecessor/historical lineage; v101.132 current evidence closes only release-engineering reconciliation and revalidation.'})
 writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'stage':STAGE,'package_local_evidence':'source deep-audit findings plus candidate prefreeze gate/four-pass evidence may be embedded before deterministic freeze','postfreeze_reopen_and_decision':'external exact-ZIP-SHA-bound evidence written after immutable freeze','physical_device_claims':'NOT_TESTED until direct evidence','immutable_package_rule':'no postfreeze file is inserted into the frozen ZIP; any byte change requires a successor','active_report_rule':'only metadata/active_report_inventory.json source_reports are current claims'})
 (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} Scope / Mutation Authority\n\nUser instruction authorises correction of failures found by the deep four-pass audit. This successor is constrained to release-engineering reconciliation only. Functional/display/canonical text mutation authority is **NONE**.\n\nAll v101.131 corpus, speech, presentation, topology, continuity, storage and user-state functional authorities are protected byte-for-byte.\n\nAfter immutable freeze, mutation authority for this exact package is **NONE**.\n''',encoding='utf-8')
 # report populated from available prefreeze summary
 agg=None
 if prefreeze:
  sp=Path(prefreeze)/'GATE_SUMMARY.json'
  if sp.exists(): agg=json.loads(sp.read_text())
 assertions=agg.get('aggregate_assertions') if agg else 'PENDING'; fails=agg.get('aggregate_failures') if agg else 'PENDING'
 report=out/'reports/DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION.md'; report.write_text(f'''# {VERSION} Deep Four-Pass Release-Engineering Reconciliation\n\n- Immutable predecessor: `v101.131` / `{PRE_SHA}` / 659 members.\n- Functional/display/canonical mutations relative to v101.131: **0**.\n- Deep source audit found five release-engineering defects in v101.131: incomplete full-overlay accounting; stale v101.122 execution specification; stale v101.122 real-device QA checklist; missing frozen raw-text gate input; incomplete current tooling inventory.\n- All five defects are corrected in v101.132 without changing CORPUS, TEXT_LIBRARY/HOUR_LINKED_TEXTS, speech/presentation authorities, DISPLAY_SEGMENTS, VISIBLE_PARAGRAPH_TOPOLOGY, continuity groups, storage schema or personal snapshot schema.\n- The frozen raw-text authority `02_ALL_TEXT_RECORD_UNIVERSE.csv` is package-local and SHA-256 bound by the M1 blind-freeze manifest.\n- `current_gate_map.json` maps all 14 current gate families to their actual harnesses and required package-local inputs; the 52-check broad runtime and primary 2,000-check presentation harnesses are explicitly inventoried.\n- Current prefreeze gate evidence: **{assertions} assertions / {fails} FAIL** across 14 families.\n- Physical-device/PWA/true-offline/screen-reader/live-origin validation remains external and open.\n''',encoding='utf-8')
 # build provenance
 writej(out/'metadata/build_provenance.json',{'version':VERSION,'stage':STAGE,'build_date':DATE,'baseline_version':'v101.131','baseline_zip_sha256':PRE_SHA,'mutation_scope':'release-engineering reconciliation only','canonical_text_changed':False,'speech_presentation_topology_changed':False,'continuity_changed':False,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'candidate_html_sha256':sha(out/'index.html')})
 # copy this build script itself into package
 shutil.copy2(Path(__file__),out/'scripts/build_v101132_release_reconciliation.py')
 # Full overlay: include self + both manifests explicitly because they are changed in final package.
 tmp=out.parent/'__pre131';shutil.rmtree(tmp,ignore_errors=True);tmp.mkdir(parents=True)
 with zipfile.ZipFile(pre_zip) as z:z.extractall(tmp)
 a=files(tmp);b=files(out);changed=sorted(k for k,p in b.items() if k not in a or sha(p)!=sha(a[k]));removed=sorted(set(a)-set(b))
 for rel in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
  if rel not in changed: changed.append(rel)
 changed.sort(); writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101132_FULL_BUILD_OVERLAY_V1','version':VERSION,'stage':STAGE,'baseline_version':'v101.131','baseline_zip_sha256':PRE_SHA,'changed_or_added':changed,'removed':removed})
 shutil.rmtree(tmp)
 exclude={'metadata/hash_manifest.json','metadata/package_manifest.json'};rows=[]
 for p in sorted(x for x in out.rglob('*') if x.is_file()):
  rel=p.relative_to(out).as_posix()
  if rel in exclude:continue
  rows.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p)})
 writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(rows),'files':[{'path':r['path'],'size':r['size']} for r in rows]})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(rows),'files':rows})
 return {'version':VERSION,'stage':STAGE,'files_total':len(files(out)),'html_sha256':sha(out/'index.html'),'manifest_files':len(rows)}
if __name__=='__main__':
 if len(sys.argv)<6: raise SystemExit('usage: build PRE_ZIP OUT TOOLS SOURCE_AUDIT FROZEN [PREFREEZE] [FOURPASS]')
 print(json.dumps(build(*sys.argv[1:]),indent=2))
