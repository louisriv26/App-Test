#!/usr/bin/env python3
from pathlib import Path
import zipfile,hashlib,json,shutil,sys
VERSION='v101.135';STAGE='MASTER_SCRIPT_VALIDATION_COMPLETION_R1';DATE='2026-09-04';CACHE='luisa-24h-v101-135'
BASE_SHA='241ef8b3953e840cc321d07fe3186e41cd4a772e449268381416575a5f60471a';BASE_MEMBERS=809;BASE_HTML_SHA='e0e954e6ec526c8b4dea6b52ff4a47cc71937df95978dd69c05c74116d8416e5'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def writej(p,o):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def allfiles(r):return {p.relative_to(r).as_posix():p for p in Path(r).rglob('*') if p.is_file()}
def verify_inputs(base_zip,source_dir,manifest):
 m=json.loads(Path(manifest).read_text());errs=[]
 if sha(base_zip)!=m['baseline_zip']['sha256']:errs.append('baseline_zip_sha')
 for x in m['source_files']:
  p=Path(source_dir)/x['path']
  if not p.is_file() or sha(p)!=x['sha256']:errs.append(x['path'])
 if errs:raise RuntimeError('input manifest mismatch: '+','.join(errs))
def build(base_zip,out,source_dir,input_manifest,prefreeze=None):
 base_zip=Path(base_zip);out=Path(out);source_dir=Path(source_dir);input_manifest=Path(input_manifest);verify_inputs(base_zip,source_dir,input_manifest)
 assert sha(base_zip)==BASE_SHA
 with zipfile.ZipFile(base_zip) as z:
  assert len(z.infolist())==BASE_MEMBERS and z.testzip() is None
  shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True);z.extractall(out)
 assert sha(out/'index.html')==BASE_HTML_SHA
 # app release identity only
 for name in ['index.html','luisa_24_heures.html']:
  p=out/name;s=p.read_text(encoding='utf-8')
  s=s.replace("const APP_VERSION = 'v101.134';","const APP_VERSION = 'v101.135';",1)
  s=s.replace("const APP_EVIDENCE_STAGE = 'BOUNDARY_UNIVERSE_EVIDENCE_REPRODUCIBILITY_RECONCILIATION_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
  s=s.replace("const BUILD_DATE = '2026-09-04'; // v101.134 / release-engineering evidence-reproducibility reconciliation; v101.133 renderer behavior unchanged","const BUILD_DATE = '2026-09-04'; // v101.135 / master-script validation completion; v101.134 functional renderer behavior unchanged",1)
  p.write_text(s,encoding='utf-8')
 v=json.loads((out/'version.json').read_text());v.update({'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,'release_scope':'Validation/release-engineering-only successor of immutable v101.134. Closes strict master-script validation coverage gaps; no renderer, canonical text, speaker, topology, offset, schema or user-state behavior change.','real_device_status':'Physical Samsung/iPhone/iPad, mandatory installed-PWA update from v101.132, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.135.','overall_release_status':'LIMITED_PASS_STATIC__EXTERNAL_VALIDATION_OPEN','known_blockers':[],'external_open_gates':['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update from v101.132','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'],'postfreeze_reopen_evidence':'External SHA-bound decision/evidence; not embedded after immutable freeze.'});writej(out/'version.json',v)
 m=json.loads((out/'manifest.json').read_text());m['version']=VERSION;writej(out/'manifest.json',m)
 sw=(out/'sw.js').read_text();sw=sw.replace("const CACHE_NAME = 'luisa-24h-v101-134';",f"const CACHE_NAME = '{CACHE}';",1).replace('/* v101.134 */','/* v101.135 */',1);(out/'sw.js').write_text(sw)
 # predecessor reports become historical
 for a,b in [('reports/DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION.md','reports/historical/v101132/DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION.md'),('reports/V101133_VISUAL_BOUNDARY_ALIGNMENT_REPAIR.md','reports/historical/v101133/V101133_VISUAL_BOUNDARY_ALIGNMENT_REPAIR.md'),('reports/V101134_BOUNDARY_UNIVERSE_EVIDENCE_REPRODUCIBILITY_RECONCILIATION.md','reports/historical/v101134/V101134_BOUNDARY_UNIVERSE_EVIDENCE_REPRODUCIBILITY_RECONCILIATION.md')]:
  a=out/a;b=out/b;b.parent.mkdir(parents=True,exist_ok=True)
  if a.exists():shutil.move(a,b)
 # current scripts from frozen source directory
 for p in (source_dir/'scripts').glob('*'):
  if p.is_file():shutil.copy2(p,out/'scripts'/p.name)
 # docs
 (out/'README.md').write_text('# Les 24 Heures de la Passion — v101.135\n\nValidation/release-engineering-only successor of immutable v101.134. Functional renderer behavior, canonical text, speaker/topology/offset authorities, storage schemas and user-state behavior are unchanged. v101.135 closes strict master-script validation coverage gaps. External physical-device/PWA/offline/screen-reader/live-origin validation remains open.\n',encoding='utf-8')
 (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text('# Real-device QA checklist — v101.135\n\nUse only the exact SHA-bound locked v101.135 package and confirm `v101.135` in Aide.\n\n## Mandatory installed-PWA migration\n- **Mandatory:** update an installed PWA directly from immutable v101.132 to v101.135; verify update, close/reopen persistence and user data.\n- Optional technical-lineage control: v101.134 → v101.135.\n\n## Alignment controls\nVerify native left-edge alignment at Hour 8 P007/P008/P009; Hour 5 reflection P005; one Promesses main case and its Library mirror; one linked-LDC case; `RELATED_HOUR_21.P073`; and `PART_III_MARY_SORROWS.BODY.P212`.\n\n## External gates\n- iPhone; iPad portrait; iPad landscape; Samsung/Android.\n- Installed-PWA update from v101.132 and close/reopen persistence.\n- True offline cold reopen.\n- Representative VoiceOver/TalkBack.\n- Live GitHub Pages exact-byte binding.\n\nBrowser emulation is supporting evidence only.\n',encoding='utf-8')
 (out/'scripts/EXECUTION_SPEC.md').write_text('# Les 24 Heures de la Passion — v101.135\n## Master-Script Validation Completion\n\nAuthority: immutable v101.134. Scope: validation/release-engineering only. Required closure: complete 1,748-boundary geometry; Repères/theme; exhaustive selection; annotation lifecycle; accessibility-tree; complete-tree stale/dependency classification; mandatory PWA upgrade from v101.132; SHA-bound build inputs; inherited suite; four-pass; deterministic freeze/reopen; independent audit; meta-audit; decision lock last. External gates remain open until directly tested.\n',encoding='utf-8')
 # prefreeze evidence package-local
 if prefreeze:
  shutil.rmtree(out/'evidence/v101135',ignore_errors=True);shutil.copytree(Path(prefreeze),out/'evidence/v101135/prefreeze')
 # current metadata
 cur=[p.relative_to(out).as_posix() for p in sorted((out/'scripts').glob('run_v101135_*.py'))]
 for x in ['scripts/build_v101135_validation_completion.py','scripts/freeze_v101135_deterministic.py']:
  if x not in cur:cur.append(x)
 reuse=['scripts/run_v101127_strict_continuity_glyph_flow_matrix.py','scripts/run_v101128_legacy_continuity_matrix.py','scripts/run_v101119_exhaustive_presentation_matrix.py','scripts/run_v101121_independent_presentation_matrix.py','scripts/run_broad_runtime_matrix.py','scripts/run_sw_logic_matrix.js','scripts/reconstruct_runtime_boundary_universe.py']
 writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'stage':STAGE,'current_tools':sorted(cur),'reused_validated_runtime_lineage':reuse,'rule':'Every current v101.135 validation/build/freeze harness is listed.'})
 led='evidence/v101133/m1/M1_05_ALIGNMENT_POSITIVE_82_LEDGER.csv'
 gates=[('R-1','scripts/run_v101135_release_integrity.py',['predecessor v101.134 index.html','index.html']),('V-1','scripts/run_v101135_full_boundary_geometry.py',['index.html']),('V-2','scripts/run_v101135_reperes_theme_geometry.py',['index.html',led]),('V-3','scripts/run_v101135_exhaustive_selection_offsets.py',['index.html','predecessor v101.132 index.html',led]),('V-4','scripts/run_v101135_annotation_lifecycle.py',['index.html',led]),('V-5','scripts/run_v101135_accessibility_tree.py',['index.html',led]),('A-1','scripts/run_v101135_alignment_geometry.py',['index.html',led]),('A-2','scripts/run_v101135_static_controls.py',['index.html']),('A-3','scripts/run_v101135_mutant_sensitivity.py',['index.html',led]),('A-4','scripts/run_v101135_accessibility_structure.py',['index.html',led]),('I-1','scripts/run_v101135_global_raw_quote_gate.py',['index.html','evidence/v101132/authority/02_ALL_TEXT_RECORD_UNIVERSE.csv']),('I-2','scripts/run_v101135_runtime_presentation.py',['index.html']),('I-3','scripts/run_v101135_mutation_tests.py',['index.html','evidence/v101132/authority/02_ALL_TEXT_RECORD_UNIVERSE.csv']),('I-4','scripts/run_v101127_strict_continuity_glyph_flow_matrix.py',['index.html']),('I-5','scripts/run_v101128_legacy_continuity_matrix.py',['index.html']),('I-6','scripts/run_v101135_meditee_regression.py',['index.html']),('I-7','scripts/run_v101135_meditee_responsive_regression.py',['index.html']),('I-8','scripts/run_v101135_hour24_regression.py',['index.html']),('I-9','scripts/run_v101135_help_browser_matrix.py',['index.html']),('I-10','scripts/run_v101119_exhaustive_presentation_matrix.py',['index.html','evidence/v101131/prefreeze/V101131_PRESENTATION_LEDGER.csv']),('I-11','scripts/run_v101121_independent_presentation_matrix.py',['index.html','evidence/v101131/prefreeze/V101131_PRESENTATION_LEDGER.csv']),('I-12','scripts/run_broad_runtime_matrix.py',['index.html']),('I-13','scripts/run_sw_logic_matrix.js',['sw.js']),('B-1','scripts/run_v101135_builder_input_manifest.py',['metadata/builder_input_manifest.json','predecessor v101.134 ZIP']),('T-1','scripts/run_v101135_complete_tree_scan.py',['metadata/active_report_inventory.json','metadata/current_tooling_inventory.json','metadata/current_gate_map.json'])]
 writej(out/'metadata/current_gate_map.json',{'version':VERSION,'stage':STAGE,'gate_families':[{'gate':g,'script':s,'inputs':i} for g,s,i in gates],'package_local_dependency_rule':'Every non-predecessor input resolves inside the package; predecessor inputs are immutable SHA-bound authorities.'})
 active=['README.md','REAL_DEVICE_QA_CHECKLIST.md','scripts/EXECUTION_SPEC.md','reports/V101135_MASTER_SCRIPT_VALIDATION_COMPLETION.md','version.json','metadata/current_tooling_inventory.json','metadata/current_gate_map.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/builder_input_manifest.json']
 writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'stage':STAGE,'active_documents':active,'historical_reports_root':'reports/historical/','rule':'Only listed documents are current v101.135 operational/claim surfaces; predecessor reports are under reports/historical.'})
 writej(out/'metadata/build_provenance.json',{'version':VERSION,'stage':STAGE,'build_date':DATE,'baseline_version':'v101.134','baseline_zip_sha256':BASE_SHA,'baseline_members':BASE_MEMBERS,'mutation_scope':'validation/release-engineering-only master-script validation completion','functional_renderer_changed':False,'canonical_text_changed':False,'speaker_adjudication_changed':False,'topology_offsets_changed':False,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True})
 writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'stage':STAGE,'functional_authority':'v101.134 inherits v101.133 renderer alignment repair','validation_completion':'v101.135 adds no functional change; closes master-script validation coverage gaps','external_validation':'OPEN'})
 shutil.copy2(input_manifest,out/'metadata/builder_input_manifest.json')
 agg=fail=0
 if prefreeze and (Path(prefreeze)/'GATE_SUMMARY.json').is_file():
  gs=json.loads((Path(prefreeze)/'GATE_SUMMARY.json').read_text());agg=gs.get('aggregate_assertions',0);fail=gs.get('aggregate_failures',0)
 (out/'reports/V101135_MASTER_SCRIPT_VALIDATION_COMPLETION.md').write_text(f'# v101.135 Master-Script Validation Completion\n\n- Immutable functional predecessor: `v101.134` / `{BASE_SHA}` / {BASE_MEMBERS} members.\n- Functional renderer change relative to v101.134: **0**.\n- Canonical text / speaker / topology-offset / schema changes: **0**.\n- Complete 1,748-boundary geometry, Repères/theme geometry, exhaustive 82/76 selection preservation, annotation lifecycle, accessibility-tree comparison, complete-tree scan and SHA-bound builder-input validation are current authorities.\n- Current prefreeze evidence: **{agg} assertions / {fail} FAIL**.\n- Mandatory external installed-PWA migration starts from **v101.132**.\n- Physical-device/PWA/true-offline/screen-reader/live-origin validation remains external and open.\n',encoding='utf-8')
 # manifests relative to baseline
 with zipfile.ZipFile(base_zip) as z:
  import tempfile
  td=out.parent/'__basecheck135';shutil.rmtree(td,ignore_errors=True);td.mkdir(parents=True);z.extractall(td)
 a=allfiles(td);b=allfiles(out);changed=sorted(k for k,p in b.items() if k not in a or sha(p)!=sha(a[k]));removed=sorted(set(a)-set(b));shutil.rmtree(td)
 for rel in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
  if rel not in changed:changed.append(rel)
 changed.sort();writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101135_FULL_BUILD_OVERLAY_V1','version':VERSION,'stage':STAGE,'baseline_version':'v101.134','baseline_zip_sha256':BASE_SHA,'changed_or_added':changed,'removed':removed})
 ex={'metadata/hash_manifest.json','metadata/package_manifest.json'};rows=[]
 for p in sorted(x for x in out.rglob('*') if x.is_file()):
  rel=p.relative_to(out).as_posix()
  if rel in ex:continue
  rows.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p)})
 writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(ex),'file_count':len(rows),'files':[{'path':r['path'],'size':r['size']} for r in rows]})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(ex),'file_count':len(rows),'files':rows})
 return {'version':VERSION,'stage':STAGE,'files_total':len(allfiles(out)),'html_sha256':sha(out/'index.html')}
if __name__=='__main__':
 if len(sys.argv)<5:raise SystemExit('usage: build BASE_ZIP OUT SOURCE_DIR INPUT_MANIFEST [PREFREEZE]')
 print(json.dumps(build(*sys.argv[1:]),indent=2))
