#!/usr/bin/env python3
from pathlib import Path
import zipfile,hashlib,json,sys,shutil,re,csv
VERSION='v101.134'
STAGE='BOUNDARY_UNIVERSE_EVIDENCE_REPRODUCIBILITY_RECONCILIATION_R1'
DATE='2026-09-04'
CACHE='luisa-24h-v101-134'
BASE_VERSION='v101.133'
BASE_SHA='1479ac5f1de0a425f3c7f2e5cd9ce7340ba1465dccac817cd27cb93f49f09b9a'
BASE_MEMBERS=751
BASE_HTML_SHA='a49a130440791771aa75721d31fb8aeacbb0dc908893ac5cda4ea7cc794f742e'

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def writej(p,o):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def allfiles(root):return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}

def patch_html(s):
 assert "const APP_VERSION = 'v101.133';" in s
 assert "const APP_EVIDENCE_STAGE = 'VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_R1';" in s
 assert "const BUILD_DATE = '2026-09-04'; // v101.133 / visual-boundary leading-whitespace alignment repair; no canonical text mutation" in s
 s=s.replace("const APP_VERSION = 'v101.133';",f"const APP_VERSION = '{VERSION}';",1)
 s=s.replace("const APP_EVIDENCE_STAGE = 'VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
 s=s.replace("const BUILD_DATE = '2026-09-04'; // v101.133 / visual-boundary leading-whitespace alignment repair; no canonical text mutation",f"const BUILD_DATE = '{DATE}'; // {VERSION} / release-engineering evidence-reproducibility reconciliation; v101.133 renderer behavior unchanged",1)
 return s

def execution_spec():
 return f'''# Les 24 Heures de la Passion — {VERSION}\n## Boundary-Universe Evidence Reproducibility Reconciliation\n### Corrective M4 execution specification\n\n## Authority\n\n- Immutable functional predecessor: `v101.133`.\n- Predecessor ZIP SHA-256: `{BASE_SHA}`.\n- Governing user authority: the approved v101.133 master script authorised M2–M4 and requires release-engineering defects found during M4 to be corrected and M4 restarted without broadening functional scope.\n- v101.133 remains immutable.\n\n## Why {VERSION} exists\n\nThe v101.133 functional alignment repair passed its runtime gates, but final deliverable reconciliation found package-local evidence/tooling defects: the required M1 boundary-universe artifact was missing; the added reconstruction helper was omitted from current tooling inventory and did not reproduce 1,748; and several required named M3 deliverables were not separately embedded.\n\n## Permitted scope\n\nRelease-engineering only. Preserve v101.133 renderer behavior exactly after normalising release identity. Canonical text, speaker adjudications, topology/offsets, continuity authority, storage schema and user-state semantics must not change.\n\n## Required reconciliation\n\n1. Embed the corrected runtime-boundary reconstruction tool.\n2. Reproduce `1,858 raw markers -> 1,748 effective boundaries` using explicit exclusions: 105 non-block markers and 5 wrapper-only local speech markers without visible semantic content after the boundary.\n3. Preserve the 82-case repair universe: 78 speech/presentation + 4 LDC intra-record.\n4. Embed the missing M1/M3 named reconciliation artifacts without pretending they are byte-identical historical artifacts.\n5. List every current/added validation tool in current tooling inventory and map every current gate dependency.\n6. Rerun the complete v101.133 functional suite on {VERSION}.\n7. Run strengthened four-pass, deterministic Build A/B, exact reopen, independent audit and meta-audit.\n8. Write the final decision lock last.\n\n## Hard stop\n\nStop for user approval if any correction requires a functional renderer change, canonical text change, speaker/topology/offset change, schema change or content-specific exception.\n\n## External boundary\n\nPhysical iPhone/iPad/Samsung, installed-PWA upgrade, true cold-offline, live-origin binding and representative VoiceOver/TalkBack remain OPEN unless directly tested.\n'''

def build(base_zip,out,recon_dir,tools_dir,prefreeze=None,prefreeze_fourpass=None):
 base_zip=Path(base_zip);out=Path(out);recon_dir=Path(recon_dir);tools_dir=Path(tools_dir)
 assert sha(base_zip)==BASE_SHA,(sha(base_zip),BASE_SHA)
 with zipfile.ZipFile(base_zip) as z:
  assert len(z.infolist())==BASE_MEMBERS and z.testzip() is None
  shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True);z.extractall(out)
 assert sha(out/'index.html')==BASE_HTML_SHA
 base_html=(out/'index.html').read_text(encoding='utf-8');assert base_html==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 new=patch_html(base_html);(out/'index.html').write_text(new,encoding='utf-8');(out/'luisa_24_heures.html').write_text(new,encoding='utf-8')
 # Release identity / cache only. Renderer implementation remains v101.133.
 v=json.loads((out/'version.json').read_text());v.update({
  'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,
  'release_scope':'Release-engineering-only successor of immutable v101.133. Reconciles boundary-universe evidence reproducibility, missing named M1/M3 deliverables, current tooling inventory and current gate mapping. v101.133 renderer behavior and all protected content/presentation authorities are unchanged.',
  'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update from v101.133, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.134.',
  'overall_release_status':'LIMITED_PASS_STATIC__EXTERNAL_VALIDATION_OPEN','known_blockers':[],
  'external_open_gates':['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update from v101.133','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'],
  'postfreeze_reopen_evidence':'External SHA-bound decision/evidence; not embedded after immutable freeze.'})
 writej(out/'version.json',v)
 m=json.loads((out/'manifest.json').read_text());m['version']=VERSION;writej(out/'manifest.json',m)
 sw=(out/'sw.js').read_text(encoding='utf-8');sw=sw.replace('/* v101.133 */','/* v101.134 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-133';",f"const CACHE_NAME = '{CACHE}';",1);(out/'sw.js').write_text(sw,encoding='utf-8')
 # Current operational files.
 (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION}\n\nRelease-engineering-only successor of immutable v101.133.\n\n- Functional renderer behavior is unchanged from v101.133.\n- The v101.133 repair remains 82/82 aligned with canonical text/source offsets preserved.\n- {VERSION} repairs package-local evidence reproducibility: corrected 1,748-boundary reconstruction, missing named M1/M3 reconciliation artifacts, tooling inventory and gate mapping.\n- Canonical text operations: 0. Speaker/topology/offset/schema changes: 0.\n- Physical-device/PWA/offline/screen-reader/live-origin validation remains external and open.\n''',encoding='utf-8')
 (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(f'''# Real-device QA checklist — {VERSION}\n\nUse only the exact SHA-bound locked {VERSION} package and confirm `{VERSION}` in Aide.\n\n## Alignment controls\nVerify native left-edge alignment at Hour 8 P007/P008/P009; Hour 5 reflection P005; one Promesses main case and its Library mirror; one linked-LDC case; `RELATED_HOUR_21.P073`; and `PART_III_MARY_SORROWS.BODY.P212`.\n\n## External gates\n- iPhone; iPad portrait; iPad landscape; Samsung/Android.\n- Installed-PWA update from v101.133 and close/reopen persistence.\n- True offline cold reopen.\n- Representative VoiceOver/TalkBack.\n- Live GitHub Pages exact-byte binding.\n\nBrowser emulation is supporting evidence only. Natural wrapping is valid; a synthetic one-space left indent is not.\n''',encoding='utf-8')
 (out/'scripts/EXECUTION_SPEC.md').write_text(execution_spec(),encoding='utf-8')
 # Current v101.134 reconciliation evidence.
 ev=out/'evidence/v101134/reconciliation';shutil.rmtree(out/'evidence/v101134',ignore_errors=True);ev.mkdir(parents=True)
 for p in recon_dir.iterdir():
  if p.is_file():shutil.copy2(p,ev/p.name)
 auth=out/'evidence/v101134/authority';auth.mkdir(parents=True)
 src_master=recon_dir/'L24H_V101133_VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_MASTER_EXECUTION_SCRIPT_R1_2026-09-03.md'
 if src_master.exists():shutil.copy2(src_master,auth/src_master.name)
 (auth/'USER_AUTHORITY.md').write_text('User explicitly authorised the bounded v101.133 renderer-only repair and execution of M2–M4 with no expansion beyond scope. The governing script requires release-engineering defects discovered within M4 to be corrected and M4 restarted; v101.134 performs only that release-engineering correction.\n',encoding='utf-8')
 if prefreeze:shutil.copytree(Path(prefreeze),out/'evidence/v101134/prefreeze',dirs_exist_ok=True)
 if prefreeze_fourpass:shutil.copytree(Path(prefreeze_fourpass),out/'evidence/v101134/prefreeze_four_pass',dirs_exist_ok=True)
 # Current tools. Remove obsolete broken v101.133 reconstruction helper from current path by replacing same path with corrected R2.
 for p in tools_dir.iterdir():
  if p.is_file() and p.suffix in ('.py','.js'):shutil.copy2(p,out/'scripts'/p.name)
 shutil.copy2(Path(__file__),out/'scripts/build_v101134_release_engineering_reconciliation.py')
 # Current tool/gate authorities.
 current=[
  'scripts/build_v101134_release_engineering_reconciliation.py','scripts/freeze_v101134_deterministic.py','scripts/reconstruct_runtime_boundary_universe.py',
  'scripts/run_v101134_release_integrity.py','scripts/run_v101134_boundary_reproducibility.py','scripts/run_v101134_accessibility_structure.py',
  'scripts/run_v101134_alignment_geometry.py','scripts/run_v101134_static_controls.py','scripts/run_v101134_mutant_sensitivity.py','scripts/run_v101134_source_selection_state.py',
  'scripts/run_v101134_four_pass.py','scripts/run_v101134_global_raw_quote_gate.py','scripts/run_v101134_runtime_presentation.py','scripts/run_v101134_mutation_tests.py',
  'scripts/run_v101134_meditee_regression.py','scripts/run_v101134_meditee_responsive_regression.py','scripts/run_v101134_hour24_regression.py','scripts/run_v101134_help_browser_matrix.py']
 reused=['scripts/run_v101127_strict_continuity_glyph_flow_matrix.py','scripts/run_v101128_legacy_continuity_matrix.py','scripts/run_v101119_exhaustive_presentation_matrix.py','scripts/run_v101121_independent_presentation_matrix.py','scripts/run_broad_runtime_matrix.py','scripts/run_sw_logic_matrix.js']
 writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'stage':STAGE,'current_tools':current,'reused_validated_runtime_lineage':reused,'rule':'Every tool used by current v101.134 validation is listed. The corrected boundary reconstruction helper is current and explicitly inventoried; predecessor/historical tools are not represented as current.'})
 gm=[
  {'gate':'R-1','script':'scripts/run_v101134_release_integrity.py','inputs':['predecessor v101.133 index.html','index.html']},
  {'gate':'R-2','script':'scripts/run_v101134_boundary_reproducibility.py','inputs':['index.html','scripts/reconstruct_runtime_boundary_universe.py','evidence/v101134/reconciliation/M1_04_RUNTIME_BOUNDARY_UNIVERSE.csv','evidence/v101133/m1/M1_05_ALIGNMENT_POSITIVE_82_LEDGER.csv']},
  {'gate':'R-3','script':'scripts/run_v101134_accessibility_structure.py','inputs':['index.html','evidence/v101133/m1/M1_05_ALIGNMENT_POSITIVE_82_LEDGER.csv']},
  {'gate':'A-1','script':'scripts/run_v101134_alignment_geometry.py','inputs':['index.html','evidence/v101133/m1/M1_05_ALIGNMENT_POSITIVE_82_LEDGER.csv']},
  {'gate':'A-2','script':'scripts/run_v101134_static_controls.py','inputs':['index.html']},
  {'gate':'A-3','script':'scripts/run_v101134_mutant_sensitivity.py','inputs':['index.html','evidence/v101133/m1/M1_05_ALIGNMENT_POSITIVE_82_LEDGER.csv']},
  {'gate':'A-4','script':'scripts/run_v101134_source_selection_state.py','inputs':['index.html','evidence/v101133/m1/M1_05_ALIGNMENT_POSITIVE_82_LEDGER.csv','predecessor v101.132 index.html']},
  {'gate':'I-1','script':'scripts/run_v101134_global_raw_quote_gate.py','inputs':['index.html','evidence/v101132/authority/02_ALL_TEXT_RECORD_UNIVERSE.csv']},
  {'gate':'I-2','script':'scripts/run_v101134_runtime_presentation.py','inputs':['index.html']},
  {'gate':'I-3','script':'scripts/run_v101134_mutation_tests.py','inputs':['index.html','evidence/v101132/authority/02_ALL_TEXT_RECORD_UNIVERSE.csv']},
  {'gate':'I-4','script':'scripts/run_v101127_strict_continuity_glyph_flow_matrix.py','inputs':['index.html']},
  {'gate':'I-5','script':'scripts/run_v101128_legacy_continuity_matrix.py','inputs':['index.html']},
  {'gate':'I-6','script':'scripts/run_v101134_meditee_regression.py','inputs':['index.html']},
  {'gate':'I-7','script':'scripts/run_v101134_meditee_responsive_regression.py','inputs':['index.html']},
  {'gate':'I-8','script':'scripts/run_v101134_hour24_regression.py','inputs':['index.html']},
  {'gate':'I-9','script':'scripts/run_v101134_help_browser_matrix.py','inputs':['index.html']},
  {'gate':'I-10','script':'scripts/run_v101119_exhaustive_presentation_matrix.py','inputs':['index.html','evidence/v101131/prefreeze/V101131_PRESENTATION_LEDGER.csv']},
  {'gate':'I-11','script':'scripts/run_v101121_independent_presentation_matrix.py','inputs':['index.html','evidence/v101131/prefreeze/V101131_PRESENTATION_LEDGER.csv']},
  {'gate':'I-12','script':'scripts/run_broad_runtime_matrix.py','inputs':['index.html']},
  {'gate':'I-13','script':'scripts/run_sw_logic_matrix.js','inputs':['sw.js']}]
 writej(out/'metadata/current_gate_map.json',{'version':VERSION,'stage':STAGE,'gate_families':gm,'package_local_dependency_rule':'Every non-predecessor input resolves inside the package. Predecessor inputs are explicit immutable SHA-bound authorities.'})
 writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'stage':STAGE,'active_documents':['README.md','REAL_DEVICE_QA_CHECKLIST.md','scripts/EXECUTION_SPEC.md','reports/V101134_BOUNDARY_UNIVERSE_EVIDENCE_REPRODUCIBILITY_RECONCILIATION.md','version.json','metadata/current_tooling_inventory.json','metadata/current_gate_map.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json'],'historical_reports_root':'reports/historical/','rule':'Only listed documents are current v101.134 operational/claim surfaces. v101.133 and earlier materials are predecessor/historical evidence.'})
 writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'stage':STAGE,'current_evidence_root':'evidence/v101134','functional_predecessor':{'version':'v101.133','sha256':BASE_SHA},'reconciliation_root':'evidence/v101134/reconciliation','historical_v101133_evidence':'evidence/v101133','rule':'v101.134 does not rewrite v101.133 historical manifests; later reconstructed artifacts are explicitly labelled reconciliation evidence.'})
 writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'stage':STAGE,'package_local_evidence':'reconciliation authority plus prefreeze gate/four-pass evidence may be embedded before deterministic freeze','postfreeze_reopen_and_decision':'external exact-ZIP-SHA-bound evidence written after immutable freeze','physical_device_claims':'NOT_TESTED until direct evidence','immutable_package_rule':'no postfreeze file is inserted into the frozen ZIP; any byte change requires a successor'})
 (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} Scope / Mutation Authority\n\nAuthority is limited to release-engineering evidence/tooling reproducibility reconciliation under the already authorised M4 failure-handling rule. Functional v101.133 renderer behavior is protected.\n\nNo canonical text, speaker adjudication, presentation/topology offset, continuity, schema or content-specific exception is authorised.\n\nAfter immutable freeze, mutation authority for the exact package is **NONE**.\n''',encoding='utf-8')
 # Current report, populated with known prefreeze aggregate if supplied.
 agg='PENDING';fails='PENDING'
 if prefreeze:
  q=Path(prefreeze)/'GATE_SUMMARY.json'
  if q.exists():
   x=json.loads(q.read_text());agg=x.get('aggregate_assertions','PENDING');fails=x.get('aggregate_failures','PENDING')
 (out/'reports/V101134_BOUNDARY_UNIVERSE_EVIDENCE_REPRODUCIBILITY_RECONCILIATION.md').write_text(f'''# v101.134 Boundary-Universe Evidence Reproducibility Reconciliation\n\n- Immutable functional predecessor: `v101.133` / `{BASE_SHA}` / 751 members.\n- Functional renderer change relative to v101.133: **0**.\n- Canonical text / speaker / topology-offset / schema changes: **0**.\n- Corrected package-local reconstruction: **1,858 raw markers -> 1,748 effective runtime boundaries**.\n- Explicit exclusions: **105 non-block markers + 5 wrapper-only local markers without visible semantic content**.\n- v101.133 alignment repair remains **82/82 repaired**: 78 speech/presentation + 4 LDC intra-record loci.\n- Missing named M1/M3 artifacts are embedded as **later reconciliation evidence**, not fabricated historical byte-streams.\n- Corrected reconstruction helper is current, package-local and explicitly listed in tooling/gate authorities.\n- Current prefreeze evidence: **{agg} assertions / {fails} FAIL**.\n- Physical-device/PWA/true-offline/screen-reader/live-origin validation remains external and open.\n''',encoding='utf-8')
 writej(out/'metadata/build_provenance.json',{'version':VERSION,'stage':STAGE,'build_date':DATE,'baseline_version':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,'baseline_members':BASE_MEMBERS,'mutation_scope':'release-engineering-only boundary-universe evidence/tooling reproducibility reconciliation','functional_renderer_changed':False,'canonical_text_changed':False,'speaker_adjudication_changed':False,'topology_offsets_changed':False,'continuity_changed':False,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'candidate_html_sha256':sha(out/'index.html')})
 # Full overlay and manifests relative to immutable v101.133.
 tmp=out.parent/'__basecheck';shutil.rmtree(tmp,ignore_errors=True);tmp.mkdir(parents=True)
 with zipfile.ZipFile(base_zip) as z:z.extractall(tmp)
 a=allfiles(tmp);b=allfiles(out);changed=sorted(k for k,p in b.items() if k not in a or sha(p)!=sha(a[k]));removed=sorted(set(a)-set(b));shutil.rmtree(tmp)
 for rel in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
  if rel not in changed:changed.append(rel)
 changed.sort();writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101134_FULL_BUILD_OVERLAY_V1','version':VERSION,'stage':STAGE,'baseline_version':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,'changed_or_added':changed,'removed':removed})
 exclude={'metadata/hash_manifest.json','metadata/package_manifest.json'};rows=[]
 for p in sorted(x for x in out.rglob('*') if x.is_file()):
  rel=p.relative_to(out).as_posix()
  if rel in exclude:continue
  rows.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p)})
 writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(rows),'files':[{'path':r['path'],'size':r['size']} for r in rows]})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(rows),'files':rows})
 return {'version':VERSION,'stage':STAGE,'files_total':len(allfiles(out)),'html_sha256':sha(out/'index.html')}

if __name__=='__main__':
 if len(sys.argv)<5:raise SystemExit('usage: build BASE_ZIP OUT RECON_DIR TOOLS_DIR [PREFREEZE] [PREFREEZE_FOURPASS]')
 print(json.dumps(build(*sys.argv[1:]),indent=2))
