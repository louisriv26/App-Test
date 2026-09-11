#!/usr/bin/env python3
from pathlib import Path
import csv,json,re,sys,hashlib
ROOT=Path(sys.argv[1]); CSVOUT=Path(sys.argv[2]); ASSERTOUT=Path(sys.argv[3]); SUMMARYOUT=Path(sys.argv[4])
VER='v101.125'; STAGE='FOUR_PASS_EVIDENCE_SCHEMA_AND_DIRECT_REPORT_BINDING_RECONCILIATION_R1'
def J(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def exists(rel): return (ROOT/rel).exists()
def all_rows(d,check,count=None):
 rows=d.get('rows') or d.get('results') or []
 rr=[r for r in rows if r.get('check')==check]
 return (count is None or len(rr)==count) and rr and all(r.get('status')=='PASS' for r in rr)
def summary(rel): return J(rel).get('summary',{})
# Load core evidence.
par=J('evidence/v101125/PROTECTED_DECLARATION_PARITY.json'); fp=J('evidence/v101125/FUNCTIONAL_HTML_PARITY.json'); findings=J('evidence/v101125/V101124_DEEP_FOUR_PASS_FINDINGS.json')
cont=J('evidence/v101125/CONTINUITY_RUNTIME_MATRIX.json'); icont=J('evidence/v101125/INDEPENDENT_CONTINUITY_PROBE.json'); cand=J('evidence/v101125/CONTINUITY_CANDIDATE_AUDIT.json'); cmut=J('evidence/v101125/CONTINUITY_MUTATION_TESTS.json'); speak=J('evidence/v101125/CONTINUITY_SPEAKER_HEADER_AUDIT.json')
version=J('version.json'); schema=J('evidence/v101125/CURRENT_EVIDENCE_SCHEMA_AUDIT.json') if exists('evidence/v101125/CURRENT_EVIDENCE_SCHEMA_AUDIT.json') else {'status':'MISSING'}
vs=J('evidence/v101125/VERSION_STALE_SCAN.json') if exists('evidence/v101125/VERSION_STALE_SCAN.json') else {'status':'MISSING'}; ss=J('evidence/v101125/SEMANTIC_STALE_SCAN.json') if exists('evidence/v101125/SEMANTIC_STALE_SCAN.json') else {'status':'MISSING'}
build=J('evidence/v101125/FULL_PACKAGE_BUILD_REPRODUCTION.json') if exists('evidence/v101125/FULL_PACKAGE_BUILD_REPRODUCTION.json') else {'status':'MISSING'}
html=(ROOT/'index.html').read_text(encoding='utf-8'); sw=(ROOT/'sw.js').read_text(encoding='utf-8'); lifecycle=J('metadata/release_evidence_lifecycle.json')
# Gate expectations for full regression rows.
gates={
 'continuity_runtime': lambda: cont.get('pass')==215 and cont.get('fail')==0,
 'continuity_candidate_universe': lambda: cand.get('status')=='PASS' and len(cand.get('approved_universe',[]))==5 and len(cand.get('strong_candidate_pairs',[]))==3,
 'continuity_speaker_header': lambda: speak.get('summary')=={'pass':5,'fail':0,'total':5},
 'continuity_mutation_detection': lambda: cmut.get('summary')=={'pass':9,'fail':0,'total':9},
 'hour24_state': lambda: summary('evidence/v101125/HOUR24_STATE_TRANSITION_MATRIX.json')=={'pass':16,'fail':0,'total':16},
 'hour24_five_profile_ux': lambda: summary('evidence/v101125/HOUR24_FIVE_PROFILE_UX_MATRIX.json').get('pass')==70 and summary('evidence/v101125/HOUR24_FIVE_PROFILE_UX_MATRIX.json').get('fail')==0,
 'help': lambda: summary('evidence/v101125/HELP_BROWSER_MATRIX.json').get('pass')==70 and summary('evidence/v101125/HELP_BROWSER_MATRIX.json').get('fail')==0,
 'broad_runtime': lambda: summary('evidence/v101125/BROAD_CHROMIUM_RUNTIME_MATRIX.json')=={'pass':52,'fail':0,'total':52},
 'quoted_span_fixed_point': lambda: (lambda d:d.get('scanner_a_valid_defects')==0 and d.get('scanner_b_valid_defects')==0 and d.get('presentation_relevant_spans')==398)(J('evidence/v101125/fixed/M1_FIXED_POINT_SUMMARY.json')),
 'presentation': lambda: summary('evidence/v101125/EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX.json').get('pass')==1990 and summary('evidence/v101125/EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX.json').get('fail')==0,
 'service_worker': lambda: summary('evidence/v101125/SERVICE_WORKER_LOGIC_MATRIX.json')=={'pass':15,'fail':0,'total':15},
 'independent_hour24': lambda: summary('evidence/v101125/INDEPENDENT_HOUR24_PROBE.json').get('pass')==55 and summary('evidence/v101125/INDEPENDENT_HOUR24_PROBE.json').get('fail')==0,
 'independent_runtime': lambda: summary('evidence/v101125/INDEPENDENT_RUNTIME_SMOKE.json')=={'pass':50,'fail':0,'total':50},
 'independent_presentation': lambda: summary('evidence/v101125/INDEPENDENT_PRESENTATION_MATRIX.json').get('pass')==1990 and summary('evidence/v101125/INDEPENDENT_PRESENTATION_MATRIX.json').get('fail')==0,
 'independent_continuity': lambda: summary('evidence/v101125/INDEPENDENT_CONTINUITY_PROBE.json')=={'pass':205,'fail':0,'total':205},
 'hour24_mutation_detection': lambda: summary('evidence/v101125/HOUR24_MUTATION_TEST_MATRIX.json')=={'pass':12,'fail':0,'total':12},
 'protected_declarations': lambda: par.get('unchanged')==14 and par.get('changed')==0,
 'functional_html_parity': lambda: fp.get('normalized_equals_baseline') is True and fp.get('showHelp_byte_identical') is True,
 'current_evidence_schema': lambda: schema.get('status')=='PASS',
}
assertions=[]; rows=[]; deferred=[]
def add(rel,ln,text,typ,ok,evidence,detail,aid=None):
 aid=aid or f'A{len(assertions)+1:04d}'; assertions.append({'assertion_id':aid,'path':rel,'line':ln,'line_text':text,'type':typ,'status':'PASS' if ok else 'FAIL','evidence_path':evidence,'evidence_detail':detail}); rows.append({'path':rel,'line':str(ln),'line_text':text,'line_type':typ,'status':'PASS' if ok else 'FAIL','assertion_id':aid,'evidence_type':typ,'evidence_path':evidence,'evidence_detail':detail})
def pointer_paths(text): return re.findall(r'`([^`]+(?:\.json|\.csv|\.md|\.txt|\.html|\.js))`',text)
inv=J('metadata/active_report_inventory.json'); source=inv['source_reports']
# Independent actual root report universe.
actual=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'reports').iterdir() if p.is_file() and p.name!='active_report_line_audit.csv')
universe_ok=set(source)==set(actual)
for rel in source:
 lines=(ROOT/rel).read_text(encoding='utf-8-sig').splitlines()
 for ln,text in enumerate(lines,1):
  if not text.strip(): continue
  # Structural headings.
  if text.startswith('#'):
   add(rel,ln,text,'STRUCTURE',True,rel,'heading/structure only'); continue
  # Evidence pointer lines: all referenced paths must exist.
  if text.startswith('Evidence:'):
   pp=pointer_paths(text); ok=bool(pp) and all(exists(x) for x in pp); add(rel,ln,text,'EVIDENCE_POINTERS',ok,';'.join(pp),'all declared evidence paths exist' if ok else f'missing={[x for x in pp if not exists(x)]}'); continue
  # CSV report schemas and rows.
  if rel=='reports/full_regression_matrix.csv':
   if ln==1: add(rel,ln,text,'STRUCTURE',text=='gate,result,status,evidence',rel,'exact CSV schema'); continue
   fields=next(csv.reader([text])); gate=fields[0]; ev=fields[3]; ok=gate in gates and exists(ev) and gates[gate](); add(rel,ln,text,'EXECUTED_GATE',ok,ev,f'claim-specific gate assertion {gate}'); continue
  if rel=='reports/protected_declaration_parity.csv':
   if ln==1: add(rel,ln,text,'STRUCTURE',text=='declaration,baseline_sha256,current_sha256,status,detail',rel,'exact CSV schema'); continue
   f=next(csv.reader([text])); name=f[0]; match=next((r for r in par['rows'] if r['declaration']==name),None); ok=bool(match) and [match['declaration'],match['baseline_sha256'],match['current_sha256'],match['status'],match['detail']]==f; add(rel,ln,text,'DECLARATION_PARITY',ok,'evidence/v101125/PROTECTED_DECLARATION_PARITY.json',f'exact row match for {name}'); continue
  # Stale scan text reports.
  if rel=='reports/stale_reference_scan.txt':
   ok=vs.get('status')=='PASS' and not vs.get('unexplained_hits') and not vs.get('schema_hits'); add(rel,ln,text,'VERSION_STALE_SCAN',ok,'evidence/v101125/VERSION_STALE_SCAN.json','current version/evidence stale scan PASS with zero unexplained/schema hits'); continue
  if rel=='reports/semantic_stale_scan.txt':
   ok=ss.get('status')=='PASS' and not ss.get('transient_hits') and not ss.get('schema_hits'); add(rel,ln,text,'SEMANTIC_STALE_SCAN',ok,'evidence/v101125/SEMANTIC_STALE_SCAN.json','semantic/transient/schema scan PASS'); continue
  # Continuity contract explicit claims.
  if rel=='reports/CONTINUITY_PRODUCT_CONTRACT.md':
   checks={3:(fp.get('normalized_equals_baseline') and par.get('unchanged')==14,'evidence/v101125/FUNCTIONAL_HTML_PARITY.json','functional/canonical/stable identity inherited'),4:(cand.get('status')=='PASS' and len(cand.get('approved_universe',[]))==5,'evidence/v101125/CONTINUITY_CANDIDATE_AUDIT.json','exact five approved pairs'),5:(all_rows(cont,'true_inline_fragments',25) and all_rows(cont,'exact_single_space_joiner',25),'evidence/v101125/CONTINUITY_RUNTIME_MATRIX.json','25/25 inline + single-space across five profiles'),6:(all_rows(cont,'stable_ids_and_single_surface',25) and all_rows(icont,'data_ids',25),'evidence/v101125/CONTINUITY_RUNTIME_MATRIX.json','stable id/data-id checks across all pairs/profiles'),7:(all_rows(cont,'annotation_identity_preserved',25) and all_rows(cont,'notes_do_not_restore_paragraph_gap',5) and par.get('unchanged')==14,'evidence/v101125/CONTINUITY_RUNTIME_MATRIX.json','record-level ids/notes plus unchanged anchor/storage authorities'),8:(all_rows(cont,'one_reperes_number_surface',25) and all_rows(cont,'reperes_keeps_one_visible_number',25) and speak.get('summary')=={'pass':5,'fail':0,'total':5},'evidence/v101125/CONTINUITY_SPEAKER_HEADER_AUDIT.json','one repères surface and no distinct follower divine speaker suppressed'),9:('if (next && next.id===followerId)' in html and any(r.get('mutation')=='remove_adjacency_guard' and r.get('status')=='PASS' for r in cmut.get('rows',[])),'evidence/v101125/CONTINUITY_MUTATION_TESTS.json','adjacency guard exists and its removal is detected'),10:('getContinuationFollower(p.id)' in html[html.index('function buildMeditationParagraphHtml'):html.index('function buildParaBlock')],'index.html','runtime grouping is fixed-group lookup; no punctuation heuristic in renderer')}
   ok,ev,det=checks.get(ln,(False,rel,'unmapped continuity claim'));add(rel,ln,text,'CONTINUITY_CONTRACT',bool(ok),ev,det);continue
  # Reconciliation report claims.
  if rel=='reports/EVIDENCE_SCHEMA_AND_BINDING_RECONCILIATION.md':
   fmap={3:(findings['pass2_runtime_package']=='PASS' and findings['pass3_report_integrity'].startswith('FAIL'),'evidence/v101125/V101124_DEEP_FOUR_PASS_FINDINGS.json','runtime PASS; report layer superseded'),4:(any(x['id']=='R125-01' for x in findings['findings']),'evidence/v101125/V101124_DEEP_FOUR_PASS_FINDINGS.json','reproduced direct-binding defect'),5:(any(x['id']=='R125-02' for x in findings['findings']),'evidence/v101125/V101124_DEEP_FOUR_PASS_FINDINGS.json','reproduced stale generated schema defect'),6:(any(x['id']=='R125-03' for x in findings['findings']),'evidence/v101125/V101124_DEEP_FOUR_PASS_FINDINGS.json','reproduced stale-scan scope defect'),7:(schema.get('status')=='PASS' and vs.get('status')=='PASS','evidence/v101125/CURRENT_EVIDENCE_SCHEMA_AUDIT.json','current evidence schemas/stale scope corrected'),8:(fp.get('normalized_equals_baseline') is True,'evidence/v101125/FUNCTIONAL_HTML_PARITY.json','identity-normalized byte parity')}
   ok,ev,det=fmap.get(ln,(False,rel,'unmapped reconciliation claim'));add(rel,ln,text,'RECONCILIATION',bool(ok),ev,det);continue
  # Build report claims.
  if rel=='reports/build_script_vs_files_audit.md':
   fmap={3:(build.get('status')=='PASS_FULL_PACKAGE_REPRODUCTION','evidence/v101125/FULL_PACKAGE_BUILD_REPRODUCTION.json','current full build reproduction PASS'),4:(build.get('baseline_zip_sha256')=='15b9fdb66fb07617ac8078fddb3e4076347390252a510c6eeb4b613f4a06d3ac','evidence/v101125/FULL_PACKAGE_BUILD_REPRODUCTION.json','exact immutable baseline hash'),5:(build.get('builder')=='scripts/build_v101125_full_package_reconciliation.py','evidence/v101125/FULL_PACKAGE_BUILD_REPRODUCTION.json','exact builder recorded'),6:(build.get('exact_source_tree_reproduction')=='PASS' and build.get('hash_manifest_reconciliation')=='PASS','evidence/v101125/FULL_PACKAGE_BUILD_REPRODUCTION.json','full tree + hash manifest reconciliation'),7:(lifecycle.get('immutable_package_rule')=='do not insert postfreeze PASS reports into frozen ZIP','metadata/release_evidence_lifecycle.json','freeze lifecycle contract')}
   ok,ev,det=fmap.get(ln,(False,rel,'unmapped build claim'));add(rel,ln,text,'BUILD_REPRODUCTION',bool(ok),ev,det);continue
  # Current metadata claims.
  if rel=='reports/current_metadata_semantic_consistency.md':
   fmap={3:(version.get('app_version')==VER and "const APP_VERSION = 'v101.125';" in html,'version.json','version.json + HTML current identity'),4:("const APP_EVIDENCE_STAGE = 'FOUR_PASS_EVIDENCE_SCHEMA_AND_DIRECT_REPORT_BINDING_RECONCILIATION_R1';" in html,'index.html','exact current stage constant'),5:(version.get('cache_name')=='luisa-24h-v101-125' and 'luisa-24h-v101-125' in sw,'sw.js','version metadata and SW cache identity agree'),6:(version.get('storage_schema')==8 and version.get('personal_snapshot')==5,'version.json','exact storage/personal snapshot versions'),7:(par.get('unchanged')==14 and fp.get('normalized_equals_baseline'),'evidence/v101125/PROTECTED_DECLARATION_PARITY.json','canonical/protected declarations unchanged'),8:(par.get('unchanged')==14 and par.get('changed')==0,'evidence/v101125/PROTECTED_DECLARATION_PARITY.json','14/14 exact declaration parity'),9:(fp.get('normalized_equals_baseline') is True,'evidence/v101125/FUNCTIONAL_HTML_PARITY.json','complete functional HTML parity after release identity normalization'),10:(lifecycle.get('postfreeze_final_reopen_reports')=='external only' and 'IF_FINAL_REOPEN_AUDITS_PASS' in version.get('overall_release_status',''),'metadata/release_evidence_lifecycle.json','package remains prefreeze/conditional; postfreeze decision external')}
   ok,ev,det=fmap.get(ln,(False,rel,'unmapped metadata claim'));add(rel,ln,text,'CURRENT_METADATA',bool(ok),ev,det);continue
  # Four-pass prefreeze claims; pass3 is deferred until all report claims evaluated.
  if rel=='reports/four_pass_deep_audit.md':
   if ln==5: deferred.append((rel,ln,text,'PASS3')); continue
   fmap={3:(build.get('status')=='PASS_FULL_PACKAGE_REPRODUCTION','evidence/v101125/FULL_PACKAGE_BUILD_REPRODUCTION.json','fresh full build evidence'),4:(all(fn() for fn in gates.values() if fn is not gates['current_evidence_schema']),'reports/full_regression_matrix.csv','all current runtime/package regression rows pass'),6:(vs.get('status')=='PASS' and ss.get('status')=='PASS' and schema.get('status')=='PASS','evidence/v101125/CURRENT_EVIDENCE_SCHEMA_AUDIT.json','version/semantic/schema stale gates all pass'),7:(findings.get('pass3_report_integrity','').startswith('FAIL') and findings.get('application_runtime_defect_found') is False,'evidence/v101125/V101124_DEEP_FOUR_PASS_FINDINGS.json','predecessor report defect superseded; runtime retained'),8:('NOT_TESTED' in version.get('real_device_status',''),'version.json','external device/live gates explicitly not tested'),9:(lifecycle.get('postfreeze_final_reopen_reports')=='external only','metadata/release_evidence_lifecycle.json','reopen decisions external/postfreeze')}
   ok,ev,det=fmap.get(ln,(False,rel,'unmapped four-pass claim'));add(rel,ln,text,'FOUR_PASS',bool(ok),ev,det);continue
  # Report-claims audit report; status/coverage lines deferred to self-result.
  if rel=='reports/report_claims_vs_evidence_audit.md':
   if ln in (3,7,8,9): deferred.append((rel,ln,text,'SELF')); continue
   fmap={4:(universe_ok,'metadata/active_report_inventory.json','declared source-report universe equals actual current root report universe'),5:(exists('reports/historical/v101124'),'reports/historical/v101124','historical predecessor reports segregated'),6:(inv.get('self_excluded_output')=='reports/active_report_line_audit.csv','metadata/active_report_inventory.json','self-excluded derived line-audit output declared')}
   ok,ev,det=fmap.get(ln,(False,rel,'unmapped report-audit claim'));add(rel,ln,text,'REPORT_AUDIT',bool(ok),ev,det);continue
  # Unknown nonblank current report line is a hard failure.
  add(rel,ln,text,'UNMAPPED',False,rel,'no claim-specific assertion mapping')
# First-pass results excluding deferred self assertions.
pre_ok=universe_ok and all(r['status']=='PASS' for r in rows)
# Add deferred lines with exact self semantics.
for rel,ln,text,kind in deferred:
 if kind=='PASS3': add(rel,ln,text,'FOUR_PASS_REPORT_INTEGRITY',pre_ok,'evidence/v101125/REPORT_CLAIM_ASSERTIONS.json','all non-self active report claims have claim-specific PASS assertions')
 else:
  if ln==3: ok=pre_ok;detail='overall report-line audit PASS iff exact coverage and claim assertions pass'
  elif ln==7: ok=True;detail='exact coverage reconstructed below from source universe'
  elif ln==8: ok=pre_ok;detail='all non-self claim rows have claim-specific evidence and assertion id'
  elif ln==9: ok=all(r['line_type']=='STRUCTURE' for r in rows if r['line_text'].startswith('#')) and all(r['line_type']=='STRUCTURE' for r in rows if r['path'].endswith('.csv') and r['line']=='1');detail='headings/CSV schemas explicitly classified STRUCTURE'
  add(rel,ln,text,'REPORT_AUDIT_SELF',ok,'evidence/v101125/REPORT_CLAIM_ASSERTIONS.json',detail)
# Exact coverage after deferred insertion.
expected=[]
for rel in source:
 for i,line in enumerate((ROOT/rel).read_text(encoding='utf-8-sig').splitlines(),1):
  if line.strip():expected.append((rel,str(i),line))
got={(r['path'],r['line'],r['line_text']) for r in rows}; exact=(set(expected)==got and len(expected)==len(rows))
# If exact coverage fails, self claims must fail.
if not exact:
 for r in rows:
  if r['line_type']=='REPORT_AUDIT_SELF':r['status']='FAIL'
 for a in assertions:
  if a['type']=='REPORT_AUDIT_SELF':a['status']='FAIL'
final_ok=exact and universe_ok and all(r['status']=='PASS' for r in rows)
# Current report-line summary and outputs.
ASSERTOUT.parent.mkdir(parents=True,exist_ok=True);ASSERTOUT.write_text(json.dumps({'schema':'L24H_V101125_REPORT_CLAIM_ASSERTIONS_V1','version':VER,'status':'PASS' if final_ok else 'FAIL','assertions_total':len(assertions),'assertions_pass':sum(a['status']=='PASS' for a in assertions),'assertions_fail':sum(a['status']=='FAIL' for a in assertions),'assertions':assertions},ensure_ascii=False,indent=2)+'\n')
CSVOUT.parent.mkdir(parents=True,exist_ok=True)
with CSVOUT.open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['path','line','line_text','line_type','status','assertion_id','evidence_type','evidence_path','evidence_detail']);w.writeheader();w.writerows(sorted(rows,key=lambda r:(r['path'],int(r['line']))))
summary_obj={'schema':'L24H_V101125_ACTIVE_REPORT_LINE_AUDIT_SUMMARY_V1','version':VER,'status':'PASS' if final_ok else 'FAIL','source_report_count':len(source),'nonblank_lines':len(expected),'pass_lines':sum(r['status']=='PASS' for r in rows),'fail_lines':sum(r['status']=='FAIL' for r in rows),'exact_coverage':exact,'claim_specific_assertions':True,'source_reports':source}
SUMMARYOUT.write_text(json.dumps(summary_obj,indent=2)+'\n')
print(json.dumps(summary_obj));raise SystemExit(0 if final_ok else 2)
