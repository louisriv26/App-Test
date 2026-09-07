#!/usr/bin/env python3
from pathlib import Path
import json,csv,hashlib,zipfile,sys,re
CAND=Path(sys.argv[1]); BASE_ZIP=Path(sys.argv[2]); OUT=Path(sys.argv[3]); OUT.mkdir(parents=True,exist_ok=True)
VERSION='v101.131'; STAGE='GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR_R1'
BASE_SHA='53d542f3514b5b2b233fe513219886020a6d178e89f8d79d254bd6979c784327'; BASE_MEMBERS=613; BASE_HTML_SHA='6400a743255ef56b5ad556d5a23e6dc26749adf8abbeea24334ead40c9ce7f07'
LEDGER_SHA='d40aea7f9fbf7f237802efbf2d7cf0219ec0dd7c3fb1d6397fb3dbf3b214bca8'
RAW_PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY']
MUTABLE=['SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_END_VISUAL_BREAKS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY']

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha(p): return sha_bytes(Path(p).read_bytes())
def ex_raw(txt,name):
 marker=f'const {name} = ';i=txt.index(marker)+len(marker)
 try:o,e=json.JSONDecoder().raw_decode(txt[i:]);return o,txt[i:i+e]
 except json.JSONDecodeError:e=txt.index(';',i);return None,txt[i:e]
def add(rows,case,ok,detail=''): rows.append({'case':case,'status':'PASS' if ok else 'FAIL','detail':str(detail)})
def summ(rows): return {'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'total':len(rows)}
def write_json(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Exact baseline material from immutable zip in-memory.
assert sha(BASE_ZIP)==BASE_SHA
with zipfile.ZipFile(BASE_ZIP) as z:
 assert len(z.infolist())==BASE_MEMBERS and z.testzip() is None
 B=z.read('index.html').decode('utf-8')
assert sha_bytes(B.encode())==BASE_HTML_SHA
H=(CAND/'index.html').read_text(encoding='utf-8'); HM=(CAND/'luisa_24_heures.html').read_text(encoding='utf-8')
v=json.loads((CAND/'version.json').read_text(encoding='utf-8'));man=json.loads((CAND/'manifest.json').read_text(encoding='utf-8'));sw=(CAND/'sw.js').read_text(encoding='utf-8')
ev=CAND/'evidence/v101131';pref=ev/'prefreeze'
# PASS 1 — files vs build / authority
p1=[]
add(p1,'baseline_zip_sha_exact',sha(BASE_ZIP)==BASE_SHA,sha(BASE_ZIP))
with zipfile.ZipFile(BASE_ZIP) as z:add(p1,'baseline_members_exact',len(z.infolist())==BASE_MEMBERS,len(z.infolist()))
add(p1,'baseline_html_sha_exact',sha_bytes(B.encode())==BASE_HTML_SHA,sha_bytes(B.encode()))
add(p1,'mirrored_html_byte_identical',H==HM,sha(CAND/'index.html'))
add(p1,'version_stage_index_exact',"const APP_VERSION = 'v101.131';" in H and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in H)
add(p1,'version_json_stable_static_status',v.get('app_version')==VERSION and v.get('overall_release_status')=='LIMITED_PASS_STATIC__EXTERNAL_VALIDATION_OPEN',v.get('overall_release_status'))
add(p1,'manifest_version_exact',man.get('version')==VERSION,man.get('version'))
add(p1,'service_worker_version_cache_exact',sw.startswith('/* v101.131 */') and "const CACHE_NAME = 'luisa-24h-v101-131';" in sw)
ledger=ev/'V101131_APPROVED_MUTATION_LEDGER.csv';add(p1,'approved_ledger_sha_exact',sha(ledger)==LEDGER_SHA,sha(ledger))
rows=list(csv.DictReader(ledger.open(encoding='utf-8-sig')));add(p1,'approved_ledger_exact_four', [r['operation_id'] for r in rows]==['M1C001','M1C002','M1C003','M1C004'] and all(r['status']=='FROZEN_AUTHORISED_USER_VALIDATED' for r in rows),len(rows))
auth=json.loads((ev/'V101131_APPROVED_MUTATION_AUTHORITY.json').read_text(encoding='utf-8'));add(p1,'explicit_user_authority_bound',auth.get('approved_ledger',{}).get('operations')==4 and auth.get('canonical_text_mutation_authority')=='NONE' and 'autorise la préparation du successeur v101.131' in auth.get('user_approval',''),auth.get('user_approval',''))
add(p1,'prevalidation_word_embedded',(ev/'23_PREVALIDATION_BEFORE_AFTER.docx').is_file(),sha(ev/'23_PREVALIDATION_BEFORE_AFTER.docx') if (ev/'23_PREVALIDATION_BEFORE_AFTER.docx').exists() else '')
for n in RAW_PROTECTED:
 add(p1,'raw_protected_'+n,ex_raw(B,n)[1]==ex_raw(H,n)[1],sha_bytes(ex_raw(H,n)[1].encode()))
for n in MUTABLE:
 add(p1,'approved_authority_changed_'+n,ex_raw(B,n)[1]!=ex_raw(H,n)[1])
# Full expected mutation integrity evidence is mandatory.
integ=json.loads((pref/'01_MUTATION_INTEGRITY.json').read_text());add(p1,'independent_mutation_integrity_17_17',integ['summary']['pass']==17 and integ['summary']['fail']==0,integ['summary'])
# Package manifests self consistency.
hm=json.loads((CAND/'metadata/hash_manifest.json').read_text());pm=json.loads((CAND/'metadata/package_manifest.json').read_text());exc=set(hm.get('self_exclusion',[]))
actual={p.relative_to(CAND).as_posix():p for p in CAND.rglob('*') if p.is_file() and p.relative_to(CAND).as_posix() not in exc}; listed={x['path']:x for x in hm['files']};mismatch=[]
for rel,p in actual.items():
 x=listed.get(rel)
 if not x or x.get('size')!=p.stat().st_size or x.get('sha256')!=sha(p):mismatch.append(rel)
add(p1,'hash_manifest_path_universe_exact',set(listed)==set(actual),f'listed={len(listed)} actual={len(actual)}')
add(p1,'hash_manifest_bytes_exact',not mismatch,','.join(mismatch[:10]))
add(p1,'package_manifest_count_exact',pm.get('file_count')==len(actual),f"{pm.get('file_count')} vs {len(actual)}")
inv=json.loads((CAND/'metadata/current_tooling_inventory.json').read_text());missing=[x for x in inv.get('current_tools',[]) if not (CAND/x).is_file()]
add(p1,'current_tools_all_resolve',len(inv.get('current_tools',[]))>=9 and not missing,f"count={len(inv.get('current_tools',[]))} missing={missing}")
ari=json.loads((CAND/'metadata/active_report_inventory.json').read_text());add(p1,'single_current_report_exact',ari.get('source_reports')==['reports/GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR.md'] and (CAND/'reports/GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR.md').is_file())
add(p1,'v101130_report_archived',(CAND/'reports/historical/v101130/FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md').is_file() and not (CAND/'reports/FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md').exists())
# PASS 2 — runtime/package behaviour: current gates only, all green.
p2=[]
gate_names=['01_MUTATION_INTEGRITY.json','02_GLOBAL_RAW_TEXT_COMPLETENESS_GATE.json','03_APPROVED_CASES_RUNTIME_PRESENTATION.json','04_MUTATION_TEST_MATRIX.json','05_STRICT_CROSS_RECORD_GLYPH_FLOW_MATRIX.json','06_LEGACY_CONTINUITY_MATRIX.json','07_MEDITEE_REGRESSION_MATRIX.json','08_MEDITEE_RESPONSIVE_REGRESSION_MATRIX.json','09_HOUR24_REGRESSION_MATRIX.json','10_HELP_REGRESSION_MATRIX.json','11_PRESENTATION_SUCCESSOR_MATRIX.json','12_INDEPENDENT_PRESENTATION_SUCCESSOR_MATRIX.json','13_BROAD_RUNTIME_MATRIX.json','14_SERVICE_WORKER_MATRIX.json']
aggregate=0
for fn in gate_names:
 p=pref/fn
 if not p.exists(): add(p2,fn,False,'missing');continue
 d=json.loads(p.read_text(encoding='utf-8'));s=d.get('summary',{}) if isinstance(d.get('summary'),dict) else {}
 pa=s.get('pass',d.get('pass',d.get('passed')));fa=s.get('fail',d.get('fail',d.get('failed')));tot=s.get('total',d.get('total'))
 if tot is None and isinstance(pa,int) and isinstance(fa,int):tot=pa+fa
 aggregate += tot or 0
 add(p2,fn,fa==0 and pa is not None and (tot is None or pa==tot),f'pass={pa} fail={fa} total={tot}')
summary=json.loads((pref/'PREFREEZE_GATE_SUMMARY.json').read_text());add(p2,'prefreeze_summary_14_families_5033_zero_fail',summary.get('all_current_gates_pass') is True and len(summary.get('gate_files',[]))==14 and summary.get('aggregate_assertions')==5033 and summary.get('aggregate_failures')==0,summary.get('aggregate_assertions'))
pr=list(csv.DictReader((pref/'V101131_PRESENTATION_LEDGER.csv').open(encoding='utf-8-sig')));add(p2,'successor_presentation_ledger_400',len(pr)==400,len(pr))
recon=json.loads((pref/'V101131_PRESENTATION_LEDGER_RECONCILIATION.json').read_text());add(p2,'presentation_ledger_reconciliation_evidence_only',recon.get('functional_app_mutation') is False and recon.get('source_rows')==398 and recon.get('successor_rows')==400)
add(p2,'invalid_responsive_harness_excluded',summary.get('invalid_harness_event',{}).get('classification')=='INVALID_HARNESS_IDENTITY_MISMATCH' and summary.get('invalid_harness_event',{}).get('excluded_from_release_gates') is True)
# PASS 3 — active report line-by-line.
report=CAND/'reports/GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR.md'; rec=[]
for i,line in enumerate(report.read_text(encoding='utf-8').splitlines(),1):
 if not line.strip():continue
 ok=False;evidence=''
 if line.startswith('# v101.131'):
  ok=VERSION in line;evidence='index/version bindings'
 elif line.startswith('- Immutable predecessor:'):
  ok=('v101.130' in line and BASE_SHA in line and '613 members' in line);evidence='baseline exact ZIP'
 elif line.startswith('- Approved mutation ledger SHA-256:'):
  ok=LEDGER_SHA in line and sha(ledger)==LEDGER_SHA;evidence='approved frozen ledger'
 elif line.startswith('- User-approved operations:'):
  ok='**4**' in line and 'M1C001' in line and 'M1C004' in line and len(rows)==4;evidence='ledger + user authority'
 elif line.startswith('- Canonical text mutations:'):
  ok='**0**' in line and all(ex_raw(B,n)[1]==ex_raw(H,n)[1] for n in RAW_PROTECTED);evidence='raw protected declarations'
 elif line.startswith('- Implicated mutable authorities only:'):
  ok=all(n in line for n in MUTABLE) and all(ex_raw(B,n)[1]!=ex_raw(H,n)[1] for n in MUTABLE);evidence='five approved mutable authorities'
 elif line.startswith('- Raw corpus/library text'):
  ok=integ['summary']['fail']==0 and json.loads((pref/'02_GLOBAL_RAW_TEXT_COMPLETENESS_GATE.json').read_text())['summary']['fail']==0;evidence='integrity + raw completeness'
 elif line.startswith('- Permanent v101.131 raw-text'):
  ok=(CAND/'scripts/run_v101131_global_raw_quote_gate.py').exists() and (CAND/'scripts/run_v101131_mutation_tests.py').exists();evidence='current tooling inventory'
 elif line.startswith('- Current prefreeze evidence closes'):
  ok='14 gate families' in line and '5,033 assertions' in line and '0 FAIL' in line and summary['aggregate_assertions']==5033 and summary['aggregate_failures']==0 and len(pr)==400;evidence='PREFREEZE_GATE_SUMMARY + successor ledger'
 elif line.startswith('- Physical-device/PWA/offline/screen-reader/live-origin'):
  ok='remains external' in line and bool(v.get('external_open_gates')) and 'NOT_TESTED' in v.get('real_device_status','');evidence='version external gates'
 rec.append({'line':i,'claim':line,'evidence':evidence,'status':'PASS' if ok else 'FAIL'})
with (OUT/'03_ACTIVE_REPORT_LINE_RECONCILIATION.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=['line','claim','evidence','status']);w.writeheader();w.writerows(rec)
p3=[{'case':f"report_line_{x['line']}",'status':x['status'],'detail':x['claim']} for x in rec]
# PASS 4 — contradictions/stale/current authority.
p4=[]
add(p4,'no_unapproved_fifth_operation',set(r['operation_id'] for r in rows)=={'M1C001','M1C002','M1C003','M1C004'} and len(rows)==4)
scope=(CAND/'metadata/scope_escalation_authority.md').read_text(encoding='utf-8');add(p4,'scope_authority_no_fifth_mutation','No fifth functional/display mutation is permitted' in scope and 'Canonical text mutation authority is **NONE**' in scope)
add(p4,'stable_package_local_status_not_pending_reopen',v.get('overall_release_status')=='LIMITED_PASS_STATIC__EXTERNAL_VALIDATION_OPEN' and 'PENDING_FINAL_REOPEN' not in v.get('overall_release_status',''))
add(p4,'external_gates_still_open',len(v.get('external_open_gates',[]))==5 and 'NOT_TESTED' in v.get('real_device_status',''))
add(p4,'no_stale_v101130_current_index_binding',"const APP_VERSION = 'v101.130';" not in H and "const APP_EVIDENCE_STAGE = 'FOUR_PASS_FINAL_PACKAGE_METADATA_EVIDENCE_RECONCILIATION_R1';" not in H)
add(p4,'no_stale_v101130_sw_cache',"luisa-24h-v101-130" not in sw)
rawgate=json.loads((pref/'02_GLOBAL_RAW_TEXT_COMPLETENESS_GATE.json').read_text()); rg={x.get('check'):x.get('detail') for x in rawgate.get('rows',[])}; add(p4,'raw_universe_gate_exact_4613_807',rg.get('all_text_record_count_4613')==4613 and rg.get('quote_bearing_record_count_807')==807,{'all_text_records':rg.get('all_text_record_count_4613'),'quote_bearing_records':rg.get('quote_bearing_record_count_807')})
ids={r['span_id'] for r in pr};add(p4,'obsolete_linear_pair_ids_retired',not {'A-Q00264','A-Q00265','A-Q00268','A-Q00269'} & ids)
add(p4,'m1_adjudicated_pair_ids_present',{'V131-Q00264-OUTER','V131-Q00265-INNER-M1C001','V131-Q00268-OUTER','V131-Q00269-INNER-M1C002','V131-M1C003-FATHER-OUTER','V131-M1C004-JESUS-NESTED'} <= ids)
add(p4,'blind_classifier_limitation_preserved',(ev/'m1/M1_BLIND_SEMANTIC_LAYER_QUALIFICATION.md').is_file())
add(p4,'v101129_controls_integrity_green',integ['summary']['fail']==0 and any((x.get('check') or x.get('case'))=='v101129_closed_break_controls_preserved' and x.get('status')=='PASS' for x in integ.get('checks',integ.get('rows',[]))), 'integrity evidence')
# Current root reports must equal active report universe.
root_reports=sorted(p.relative_to(CAND).as_posix() for p in (CAND/'reports').glob('*.md'));add(p4,'no_stale_current_root_reports',root_reports==['reports/GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR.md'],root_reports)
# write structured outputs
write_json('01_PASS1_FILES_VS_BUILD.json',{'schema':'L24H_V101131_PASS1_V1','version':VERSION,'summary':summ(p1),'checks':p1})
write_json('02_PASS2_RUNTIME_PACKAGE.json',{'schema':'L24H_V101131_PASS2_V1','version':VERSION,'summary':summ(p2),'checks':p2})
write_json('03_PASS3_ACTIVE_REPORT.json',{'schema':'L24H_V101131_PASS3_V1','version':VERSION,'summary':summ(p3),'checks':p3})
write_json('04_PASS4_STALE_CONTRADICTION.json',{'schema':'L24H_V101131_PASS4_V1','version':VERSION,'summary':summ(p4),'checks':p4,'historical_reference_policy':'Explicit v101.130 and earlier references in historical/predecessor lineage are valid and not stale current claims.'})
passes=[('Pass 1 — files vs build/authority',p1),('Pass 2 — runtime/package behaviour',p2),('Pass 3 — active report line-by-line',p3),('Pass 4 — contradictions/stale/obsolete evidence',p4)];overall=all(summ(r)['fail']==0 for _,r in passes)
md=['# v101.131 — Four-pass prefreeze audit','',f'Candidate: `{CAND}`','',f'Immutable predecessor: `v101.130` / `{BASE_SHA}` / 613 members.','']
for title,rr in passes:
 s=summ(rr);md += [f'## {title}','',f"**Result: {'PASS' if s['fail']==0 else 'FAIL'} — {s['pass']}/{s['total']} checks**",'']
 for x in rr: md.append(f"- `{x['status']}` — {x['case']}"+(f" — {x['detail']}" if x.get('detail') else ''))
 md.append('')
md += ['## Decision','',f"**PREFREEZE FOUR-PASS: {'PASS' if overall else 'FAIL'}**",'',f'Current gate family assertions: **{summary["aggregate_assertions"]} / {summary["aggregate_assertions"]} PASS**.','', 'This is static/prefreeze evidence only. Deterministic Build A/B identity, exact frozen-ZIP reopen, independent reopen/meta audit and external physical-device/PWA/offline/screen-reader/live-origin gates remain downstream.']
(OUT/'05_FOUR_PASS_PREFREEZE.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({'pass1':summ(p1),'pass2':summ(p2),'pass3':summ(p3),'pass4':summ(p4),'overall':'PASS' if overall else 'FAIL'},ensure_ascii=False,indent=2))
if not overall:raise SystemExit(2)
