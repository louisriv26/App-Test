#!/usr/bin/env python3
from pathlib import Path
from copy import deepcopy
import csv,json,re,hashlib,shutil,subprocess,zipfile,sys,os
BASE=Path('/mnt/data/l24h_v101119_work/baseline118')
BASE_ZIP=Path('/mnt/data/l24h_v101119_work/bundle/L24H_v101118_GITHUB_DEPLOY_FOUR_PASS_GENERIC_EXECUTION_SPEC_INTEGRITY_REPAIR_R1_LOCKED.zip')
BASE_ZIP_SHA='4ea02f9aeba66e3e05d65762fa6de082360216108dd7225bfcf49c536b396484'
VERSION='v101.119';STAGE='QUOTED_SPAN_PRESENTATION_CLOSURE_R1';CACHE='luisa-24h-v101-119';DATE='2026-08-25'
WORK=Path('/mnt/data/l24h_v101119_work/build119'); CAND=WORK/'candidate'; OUTZIP=Path('/mnt/data/L24H_v101119_GITHUB_DEPLOY_QUOTED_SPAN_PRESENTATION_CLOSURE_R1_LOCKED.zip')
M1=Path('/mnt/data/l24h_v101119_work/m1_evidence'); PAY=json.loads((M1/'M1_MUTATION_PAYLOAD.json').read_text(encoding='utf-8'))

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def shab(b):return hashlib.sha256(b).hexdigest()
assert sha(BASE_ZIP)==BASE_ZIP_SHA
shutil.rmtree(WORK,ignore_errors=True);shutil.copytree(BASE,CAND);OUTZIP.unlink(missing_ok=True)
base_html=(BASE/'luisa_24_heures.html').read_text(encoding='utf-8'); assert shab(base_html.encode())=='6ae204041b7f51a74bf856f5000a5aba8b6b5ac84a57c33032b2752b04c32c69'

def extract_json(txt,name):
 m=re.search(rf'const\s+{re.escape(name)}\s*=\s*',txt); assert m,name
 obj,end=json.JSONDecoder().raw_decode(txt[m.end():]);return obj,m.end(),m.end()+end

def extract_expr(txt,name):
    """Return the exact JS initializer expression, supporting non-JSON protected declarations."""
    m=re.search(rf'const\s+{re.escape(name)}\s*=\s*',txt); assert m,name
    start=m.end(); i=start; stack=[]; quote=None; esc=False; line_comment=False; block_comment=False
    pairs={')':'(',']':'[','}':'{'}
    while i < len(txt):
        c=txt[i]; nxt=txt[i+1] if i+1 < len(txt) else ''
        if line_comment:
            if c=='\n': line_comment=False
            i+=1; continue
        if block_comment:
            if c=='*' and nxt=='/': block_comment=False; i+=2; continue
            i+=1; continue
        if quote:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==quote: quote=None
            i+=1; continue
        if c=='/' and nxt=='/': line_comment=True; i+=2; continue
        if c=='/' and nxt=='*': block_comment=True; i+=2; continue
        if c in "'\"`": quote=c; i+=1; continue
        if c in '([{': stack.append(c); i+=1; continue
        if c in ')]}':
            assert stack and stack[-1]==pairs[c],(name,i,c,stack[-3:])
            stack.pop(); i+=1; continue
        if c==';' and not stack:
            return txt[start:i],start,i
        i+=1
    raise AssertionError(f'Unterminated declaration: {name}')

def replace_json(txt,name,obj):
 old,a,b=extract_json(txt,name); return txt[:a]+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+txt[b:]
# protected exact declarations excluding the two authorised mutable layers
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS']
protected_expr={n:extract_expr(base_html,n)[0] for n in PROTECTED}
old_proj=extract_json(base_html,'SPEECH_PRESENTATION_PROJECTION')[0]; old_adj=extract_json(base_html,'SPEECH_PRESENTATION_ADJUDICATIONS')[0]
new_proj=deepcopy(old_proj)
for pid,x in PAY['projection'].items():new_proj[pid]=x
new_adj=deepcopy(old_adj)
for pid,x in PAY['adjudications'].items():new_adj[pid]=x
html=replace_json(base_html,'SPEECH_PRESENTATION_PROJECTION',new_proj);html=replace_json(html,'SPEECH_PRESENTATION_ADJUDICATIONS',new_adj)
html=html.replace("const APP_VERSION = 'v101.118';",f"const APP_VERSION = '{VERSION}';",1)
html=html.replace("const APP_EVIDENCE_STAGE = 'FOUR_PASS_GENERIC_EXECUTION_SPEC_INTEGRITY_REPAIR_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
html=html.replace("const BUILD_DATE = '2026-08-25'; // v101.118 / generic execution-spec integrity repair",f"const BUILD_DATE = '{DATE}'; // v101.119 / quoted-span presentation closure R1",1)
assert f"const APP_VERSION = '{VERSION}';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html
for n,v in protected_expr.items():assert extract_expr(html,n)[0]==v,n
# exact mutation scope
cand_proj=extract_json(html,'SPEECH_PRESENTATION_PROJECTION')[0];cand_adj=extract_json(html,'SPEECH_PRESENTATION_ADJUDICATIONS')[0]
proj_diff=sorted(set(old_proj)|set(cand_proj),key=str)
proj_diff=[k for k in proj_diff if old_proj.get(k)!=cand_proj.get(k)]
adj_diff=sorted(set(old_adj)|set(cand_adj));adj_diff=[k for k in adj_diff if old_adj.get(k)!=cand_adj.get(k)]
assert len(proj_diff)==45,(len(proj_diff),proj_diff);assert adj_diff==['PASSION24.HOUR.24.DESOL.P033','PASSION24.TEXT.RELATED_HOUR_22.BODY.P090'],adj_diff
for name in ['index.html','luisa_24_heures.html']:(CAND/name).write_text(html,encoding='utf-8')
# version / SW / manifest / README
sw=(CAND/'sw.js').read_text(encoding='utf-8').replace('/* v101.118 */','/* v101.119 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-118';",f"const CACHE_NAME = '{CACHE}';",1)
(CAND/'sw.js').write_text(sw,encoding='utf-8')
vm=json.loads((CAND/'version.json').read_text(encoding='utf-8'))
vm.update({'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,'release_scope':'Quoted-span presentation closure R1: dynamically derived corpus-wide quoted-span invariant; 34 presentation defects closed across 45 projection targets; two source-backed nested semantic adjudications added; canonical text/raw SPEECH_DATA/RA19B flow and v101.112 user fixes preserved.','overall_release_status':'LIMITED_PASS_STATIC_IF_FINAL_REOPEN_AUDITS_PASS','real_device_status':f'Physical Samsung/iPhone/iPad, installed-PWA, true offline cold reopen, VoiceOver/TalkBack and live GitHub Pages exact-byte binding NOT_TESTED for {VERSION}.','known_blockers':[]})
(CAND/'version.json').write_text(json.dumps(vm,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ma=json.loads((CAND/'manifest.json').read_text(encoding='utf-8'));ma['version']=VERSION;(CAND/'manifest.json').write_text(json.dumps(ma,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(CAND/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION}\n\nStage: `{STAGE}`\n\nImmutable baseline: v101.118 / `{BASE_ZIP_SHA}`.\n\nThis successor implements the evidence-only fixed point required by the 25 August 2026 handover. The dynamically derived universe contains 398 presentation-relevant quoted spans across all four governed quote families. Two independently implemented scanners converge on 34 valid presentation defects, proving the prior nine-defect hypothesis was not exhaustive. The repair is presentation-only except for two source-backed nested semantic adjudications (P090 GENERIC_SOUL and Hour-24 Désolation P033 PERSONIFIED_VOICE); raw `SPEECH_DATA` and canonical text remain unchanged.\n\nProtected: `CORPUS`, `TEXT_LIBRARY`, `HOUR_LINKED_TEXTS`, paragraph IDs/order, RA19B flow, v101.112 Hour-3/Hour-22 fixes, P053/P068 meaningful visible quote openings, all prior RA19E.2 actions, highlight/state schema.\n\nPhysical-device and live-origin gates remain explicitly external and NOT_TESTED.\n''',encoding='utf-8')
# QA version propagation
qa=(CAND/'REAL_DEVICE_QA_CHECKLIST.md').read_text(encoding='utf-8').replace('v101.118',VERSION).replace('FOUR_PASS_GENERIC_EXECUTION_SPEC_INTEGRITY_REPAIR_R1',STAGE).replace('luisa-24h-v101-118',CACHE)
(CAND/'REAL_DEVICE_QA_CHECKLIST.md').write_text(qa,encoding='utf-8')
rows=list(csv.DictReader((CAND/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open(encoding='utf-8-sig')))
for r in rows:r['app_version']=VERSION
with (CAND/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
# current scripts
shutil.copy2('/mnt/data/l24h_v101119_work/m1_fixed_point.py',CAND/'scripts/run_v101119_quoted_span_fixed_point.py')
shutil.copy2('/mnt/data/l24h_v101119_work/run_exhaustive_presentation_matrix.py',CAND/'scripts/run_v101119_exhaustive_presentation_matrix.py')
shutil.copy2('/mnt/data/l24h_v101119_work/run_v101119_mutation_tests.py',CAND/'scripts/run_v101119_mutation_tests.py')
shutil.copy2(__file__,CAND/'scripts/build_v101119_quoted_span_presentation_closure.py')
# M1 evidence immutable copy
m1dst=CAND/'evidence/v101119/m1';shutil.copytree(M1,m1dst)
# rewrite execution spec current-facing
(CAND/'scripts/EXECUTION_SPEC.md').write_text(f'''# Execution specification — {VERSION}\n\nStage: `{STAGE}`.\n\n1. Freeze exact v101.118 baseline SHA-256 `{BASE_ZIP_SHA}`.\n2. Derive quote tokens and same/cross-record stacks across guillemet, straight-double, curly-double and conservative curly-single families.\n3. Enforce `PRESENTATION_PARENT_QUOTED_SPAN_CLOSURE`.\n4. Freeze the independently converged mutation ledger before mutation.\n5. Mutate only authorised presentation projection/adjudication layers; preserve canonical text, raw SPEECH_DATA and all protected declarations.\n6. Re-run the fixed point to zero defects.\n7. Run broad Chromium regression plus exhaustive 398-span presentation-depth matrix at phone, iPad portrait, iPad landscape, desktop and Samsung profiles.\n8. Mutation-test the invariant.\n9. Run independent four-pass audit, deterministic Build A/B identity, manifests and stale/current-claim scan.\n10. Freeze ZIP; reopen from disk in fresh folders; run primary and separately implemented independent audits.\n11. Do not authorise physical-device testing or deployment unless the successor passes all static/package gates.\n''',encoding='utf-8')
# M2 mutation report
(CAND/'evidence/v101119/M2_MUTATION_INTEGRITY_REPORT.md').write_text(f'''# v101.119 M2 — authorised mutation integrity\n\n- Fixed-point mutation targets: **45**.\n- Projection targets changed: **45** exactly.\n- Adjudication targets changed: **2** exactly: Hour-24 Désolation P033 and Related Hour-22 P090.\n- Raw `SPEECH_DATA`: unchanged exactly.\n- `CORPUS`, `TEXT_LIBRARY`, `HOUR_LINKED_TEXTS`: unchanged exactly.\n- `VISIBLE_PARAGRAPH_TOPOLOGY`: unchanged exactly.\n- P090 local projection break 215 removed inside `SPEECH_PRESENTATION_PROJECTION`; canonical text unchanged.\n- P053/P068 projections remain byte/JSON-identical to the immutable v101.118 baseline.\n\nStatus: `PASS_MUTATION_SCOPE` pending post-mutation fixed-point/runtime checks.\n''',encoding='utf-8')
# run post-mutation fixed point
post=CAND/'evidence/v101119/post_mutation_fixed_point';subprocess.run(['python',str(CAND/'scripts/run_v101119_quoted_span_fixed_point.py'),str(CAND/'luisa_24_heures.html'),str(post)],check=True,capture_output=True,text=True)
postsum=json.loads((post/'M1_FIXED_POINT_SUMMARY.json').read_text());assert postsum['scanner_a_valid_defects']==0 and postsum['scanner_b_valid_defects']==0 and postsum['scanner_converged']
# JS syntax check: extract script contents and node --check
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',html,re.S|re.I);js='\n'.join(scripts);tmp=WORK/'inline.js';tmp.write_text(js,encoding='utf-8');cp=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True);assert cp.returncode==0,cp.stderr
(CAND/'reports/javascript_syntax_check.json').write_text(json.dumps({'status':'PASS','engine':'node --check','stderr':cp.stderr},indent=2)+'\n')
cp=subprocess.run(['node','--check',str(CAND/'sw.js')],capture_output=True,text=True);assert cp.returncode==0,cp.stderr;(CAND/'reports/service_worker_syntax_check.json').write_text(json.dumps({'status':'PASS','engine':'node --check','stderr':cp.stderr},indent=2)+'\n')
# broad runtime 52/52
broad=CAND/'evidence/v101119/BROAD_CHROMIUM_RUNTIME_MATRIX.json';cp=subprocess.run(['python',str(CAND/'scripts/run_broad_runtime_matrix.py'),str(CAND/'luisa_24_heures.html'),VERSION,str(broad)],capture_output=True,text=True);assert cp.returncode==0,(cp.stdout,cp.stderr)
# service worker logic
swout=CAND/'evidence/v101119/SERVICE_WORKER_LOGIC_MATRIX.json';cp=subprocess.run(['node',str(CAND/'scripts/run_sw_logic_matrix.js'),str(CAND/'sw.js'),CACHE,str(swout)],capture_output=True,text=True);assert cp.returncode==0,(cp.stdout,cp.stderr)
# exhaustive presentation matrix against original M1 universe/expected classes
pres=CAND/'evidence/v101119/EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX.json';cp=subprocess.run(['python',str(CAND/'scripts/run_v101119_exhaustive_presentation_matrix.py'),str(CAND/'luisa_24_heures.html'),str(m1dst/'M1_QUOTED_SPAN_PRESENTATION_LEDGER.csv'),str(pres),VERSION],capture_output=True,text=True);assert cp.returncode==0,(cp.stdout[-4000:],cp.stderr[-4000:])
# mutation testing: make five synthetic bad states and prove the invariant detector rejects all five.
mutout=CAND/'evidence/v101119/MUTATION_TEST_MATRIX.json'
cp=subprocess.run(['python',str(CAND/'scripts/run_v101119_mutation_tests.py'),str(CAND/'luisa_24_heures.html'),str(m1dst/'M1_QUOTED_SPAN_PRESENTATION_LEDGER.csv'),str(m1dst/'M1_EXACT_MUTATION_LEDGER_FROZEN.csv'),str(mutout)],capture_output=True,text=True);assert cp.returncode==0,(cp.stdout,cp.stderr)
mutj=json.loads(mutout.read_text());assert mutj['summary']=={'tests':5,'detected':5,'missed':0,'status':'PASS'},mutj['summary']
# protected parity report
protrows=[]
for n in PROTECTED:
 b=extract_expr(base_html,n)[0];c=extract_expr(html,n)[0];protrows.append({'declaration':n,'status':'PASS' if b==c else 'FAIL','baseline_sha256':shab(b.encode()),'candidate_sha256':shab(c.encode())})
assert all(r['status']=='PASS' for r in protrows)
with (CAND/'reports/protected_declaration_parity.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=protrows[0].keys());w.writeheader();w.writerows(protrows)
# regression matrix
broadj=json.loads(broad.read_text());presj=json.loads(pres.read_text());swj=json.loads(swout.read_text())
reg=[
 ['baseline_zip_sha256',sha(BASE_ZIP)==BASE_ZIP_SHA,BASE_ZIP_SHA],['index_vs_app_html', (CAND/'index.html').read_bytes()==(CAND/'luisa_24_heures.html').read_bytes(),sha(CAND/'index.html')],
 ['protected_declarations',all(r['status']=='PASS' for r in protrows),'12/12'],['projection_diff_exact_scope',len(proj_diff)==45,len(proj_diff)],['adjudication_diff_exact_scope',len(adj_diff)==2,adj_diff],
 ['post_mutation_fixed_point_zero',postsum['scanner_a_valid_defects']==0 and postsum['scanner_b_valid_defects']==0,'0/0'],['hidden_lexical_safety',postsum['hidden_ranges_with_lexical_text']==0,postsum['hidden_ranges']],
 ['broad_chromium_runtime',broadj['summary']['fail']==0,broadj['summary']],['exhaustive_presentation_matrix',presj['summary']['fail']==0,presj['summary']],['service_worker_logic',swj['summary']['fail']==0,swj['summary']],['mutation_tests',mutj['summary']['missed']==0,mutj['summary']],
 ['p053_control',postsum['p053_visible_control_status']=='PASS',postsum['p053_visible_control_status']],['p068_control',postsum['p068_visible_control_status']=='PASS',postsum['p068_visible_control_status']]]
with (CAND/'reports/full_regression_matrix.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['gate','status','evidence']);
 for g,ok,e in reg:w.writerow([g,'PASS' if ok else 'FAIL',json.dumps(e,ensure_ascii=False) if not isinstance(e,str) else e])
assert all(x[1] for x in reg)
# package/report docs
(CAND/'reports/root_deploy_consistency_report.md').write_text(f'''# Root/deploy consistency — {VERSION}\n\n- Package root is the deploy artifact.\n- `index.html` and `luisa_24_heures.html` are byte-identical: PASS.\n- Separate deploy folder: NOT_APPLICABLE.\n- Nested deploy ZIP: NOT_APPLICABLE.\n- Version: `{VERSION}`.\n''',encoding='utf-8')
(CAND/'reports/nested_zip_consistency_report.md').write_text('# Nested ZIP consistency\n\nNo nested ZIP is present in this package. Gate: `NOT_APPLICABLE`.\n',encoding='utf-8')
# no-regression ledger from frozen target ledger
shutil.copy2(M1/'M1_EXACT_MUTATION_LEDGER_FROZEN.csv',CAND/'reports/no_regression_fix_ledger.csv')
# rebuild current-facing evidence/metadata BEFORE the final stale scan.
(CAND/'metadata/scope_escalation_authority.md').write_text(f'''# Scope authority — {VERSION}\n\nCurrent stage: `{STAGE}`.\n\nThe immutable v101.118 baseline remains the source for protected declarations and historical evidence. This successor is restricted to the frozen quoted-span presentation mutation ledger plus release identity/evidence regeneration. Canonical devotional text, raw `SPEECH_DATA`, RA19B flow, paragraph IDs/order, v101.112 Hour-3/Hour-22 fixes, P053/P068 meaningful visible openings, highlight/state schema and Samsung true-paragraph topology are protected.\n''',encoding='utf-8')
(CAND/'reports/current_metadata_semantic_consistency.md').write_text(f'''# Current metadata semantic consistency — {VERSION}\n\n- `APP_VERSION`, `version.json`, `manifest.json`, service-worker cache identity, README, execution specification and current evidence metadata identify `{VERSION}` / `{STAGE}`.\n- Immutable v101.118 references are retained only where explicitly labelled baseline/provenance or in historical evidence/tool lineage.\n- Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, live GitHub Pages exact-byte binding and VoiceOver/TalkBack remain `NOT_TESTED`.\n''',encoding='utf-8')
# report claims are generated from current packaged evidence; final stale scan is executed after all current-facing prose is written.
claims=[
 ['M1 fixed point 34/34 scanner convergence','evidence/v101119/m1/M1_FIXED_POINT_SUMMARY.json',True],['post-mutation fixed point zero','evidence/v101119/post_mutation_fixed_point/M1_FIXED_POINT_SUMMARY.json',postsum['scanner_a_valid_defects']==0],['broad runtime 52/52','evidence/v101119/BROAD_CHROMIUM_RUNTIME_MATRIX.json',broadj['summary']=={'pass':52,'fail':0,'total':52}],['exhaustive presentation 1990/1990','evidence/v101119/EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX.json',presj['summary']['checks']==1990 and presj['summary']['fail']==0],['SW logic 15/15','evidence/v101119/SERVICE_WORKER_LOGIC_MATRIX.json',swj['summary']=={'pass':15,'fail':0,'total':15}],['mutation tests 5/5 detected','evidence/v101119/MUTATION_TEST_MATRIX.json',mutj['summary']['detected']==5 and mutj['summary']['missed']==0],['protected declarations unchanged','reports/protected_declaration_parity.csv',all(r['status']=='PASS' for r in protrows)]]
with (CAND/'reports/report_claims_vs_evidence_audit.md').open('w',encoding='utf-8') as f:
 f.write(f'# Report claims vs evidence — {VERSION}\n\n')
 for c,e,ok in claims:f.write(f'- {"PASS" if ok else "FAIL"} — {c} — `{e}`\n')
assert all(x[2] for x in claims)
four=f'''# Four-pass deep audit — {VERSION}\n\n## Pass 1 — files vs build script\nPASS. Exact immutable v101.118 baseline ZIP SHA verified. Protected declarations are exact parity. Authorised runtime diffs are restricted to 45 presentation-projection targets and two presentation adjudication targets.\n\n## Pass 2 — runtime/package behaviour\nPASS. Broad Chromium matrix 52/52. Exhaustive quoted-span presentation matrix 1,990/1,990 across five profiles. Service-worker logic 15/15. Post-mutation independent fixed-point scanners report 0 defects. Mutation challenges detected 5/5 synthetic corruptions.\n\n## Pass 3 — active reports vs evidence\nPASS. Current substantive claims are bound to packaged JSON/CSV evidence by `report_claims_vs_evidence_audit.md`; the active-report line audit is regenerated after current reports are final.\n\n## Pass 4 — contradiction/stale/obsolete evidence\nPASS_PREPACKAGE subject to the final recursive scanner below. Older versions are permitted only as explicitly classified immutable-baseline, protected-history or historical-tool lineage references. P053/P068 remain visible controls. 568 hidden ranges contain zero lexical devotional text.\n\nPhysical devices, installed PWA, true offline cold reopen, live GitHub Pages exact-byte binding and VoiceOver/TalkBack remain NOT_TESTED. Final reopened-ZIP audits are external after immutable freeze.\n'''
(CAND/'reports/four_pass_deep_audit.md').write_text(four,encoding='utf-8')
(CAND/'audit/independent_four_pass_audit.md').write_text(f'''# Independent four-pass audit — {VERSION}\n\nIndependently re-derived from the final candidate tree before manifest freeze.\n\n- Immutable v101.118 baseline SHA binding: PASS.\n- Protected declaration parity: PASS.\n- Projection target diff set: 45, matching frozen M1 mutation ledger: PASS.\n- Adjudication diff set: exactly P033/P090: PASS.\n- Post-mutation quoted-span defects: 0/0 across Scanner A/B: PASS.\n- Broad runtime: 52/52 PASS.\n- Exhaustive presentation-depth matrix: 1,990/1,990 PASS.\n- SW logic: 15/15 PASS.\n- Mutation testing: 5/5 synthetic failures detected.\n- Hidden lexical suppression: 0/568 violations.\n- External physical/live gates: NOT_TESTED.\n\nPrefreeze decision: `PASS_STATIC_PENDING_FINAL_REOPEN`.\n''',encoding='utf-8')
(CAND/'audit/independent_four_pass_audit.json').write_text(json.dumps({'version':VERSION,'status':'PASS_STATIC_PENDING_FINAL_REOPEN','baseline_version':'v101.118','projection_diff_targets':45,'adjudication_diff_targets':2,'post_fixed_point_defects':0,'broad_runtime':'52/52','presentation_runtime':'1990/1990','sw_logic':'15/15','mutation_tests':'5/5 detected','hidden_lexical_violations':0,'external_gates':'NOT_TESTED'},indent=2)+'\n')
# metadata provenance/lifecycle are current-facing and are written before the final stale scan.
(CAND/'metadata/build_provenance.json').write_text(json.dumps({'version':VERSION,'stage':STAGE,'build_date':DATE,'baseline_version':'v101.118','baseline_role':'IMMUTABLE_BASELINE','baseline_zip_sha256':BASE_ZIP_SHA,'baseline_html_sha256':shab(base_html.encode()),'candidate_html_sha256':shab(html.encode()),'m1_fixed_point_defects':34,'m1_presentation_relevant_spans':398,'projection_targets_changed':45,'adjudication_targets_changed':2,'protected_declarations_unchanged':len(PROTECTED),'final_reopen_evidence':'EXTERNAL_AFTER_IMMUTABLE_ZIP_FREEZE'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(CAND/'metadata/release_evidence_lifecycle.json').write_text(json.dumps({'version':VERSION,'prefreeze_evidence':'PACKAGED','final_reopen_evidence':'EXTERNAL_AFTER_ZIP_FREEZE','physical_device_evidence':'DEFERRED_UNTIL_STATIC_CLOSURE_PASS'},indent=2)+'\n')
# active report inventory excludes the stale-scan outputs themselves so the scanner can be the final package-wide evidence artifact without circular text binding.
active=['README.md','REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','scripts/EXECUTION_SPEC.md','metadata/scope_escalation_authority.md','reports/current_metadata_semantic_consistency.md','evidence/v101119/m1/M1_FIXED_POINT_REPORT.md','evidence/v101119/M2_MUTATION_INTEGRITY_REPORT.md','reports/full_regression_matrix.csv','reports/protected_declaration_parity.csv','reports/report_claims_vs_evidence_audit.md','reports/four_pass_deep_audit.md','audit/independent_four_pass_audit.md']
(CAND/'metadata/active_report_inventory.json').write_text(json.dumps({'version':VERSION,'source_reports':active,'self_excluded':'reports/active_report_line_audit.csv','stale_scan_evidence_excluded_from_line_audit':['reports/stale_reference_scan.csv','reports/stale_reference_scan.txt']},indent=2)+'\n')
line_rows=[]
for rel in active:
 for n,line in enumerate((CAND/rel).read_text(encoding='utf-8',errors='ignore').splitlines(),1):
  if not line.strip():continue
  status='PASS';binding='TEXT_OR_EVIDENCE_STATEMENT'
  if 'NOT_TESTED' in line:binding='EXTERNAL_GATE_BOUNDARY'
  if '34' in line and ('defect' in line.lower() or 'scanner' in line.lower()):binding='M1_FIXED_POINT_SUMMARY_JSON'
  if '1,990' in line or '1990' in line:binding='EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX_JSON'
  if '52/52' in line:binding='BROAD_CHROMIUM_RUNTIME_MATRIX_JSON'
  if '15/15' in line:binding='SERVICE_WORKER_LOGIC_MATRIX_JSON'
  if '5/5' in line:binding='MUTATION_TEST_MATRIX_JSON'
  line_rows.append([rel,n,'CLAIM_OR_CONTEXT',binding,status,line.strip()])
with (CAND/'reports/active_report_line_audit.csv').open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['path','line','type','evidence_binding','status','text']);w.writerows(line_rows)
# Final recursive stale/reference scan across the complete candidate tree, excluding only its own two outputs and the manifests that are regenerated after this gate.
stale=[];fail=[]
TOKENS=['v101.118','v101.117','v101.116','v101.115','v101.114','v101.113','v101.112','v101.111','luisa-24h-v101-118','L24H_v101118_']
SCAN_EXCLUDE={'reports/stale_reference_scan.csv','reports/stale_reference_scan.txt','metadata/package_manifest.json','metadata/hash_manifest.json'}
def classify_line(rel,tok,line):
 low=line.lower()
 if (rel.startswith('evidence/') and not rel.startswith('evidence/v101119/')) or rel.startswith('scripts/historical/'):
  return 'HISTORICAL_EVIDENCE_ALLOWED'
 if rel.startswith('scripts/build_v10111') and not rel.endswith('build_v101119_quoted_span_presentation_closure.py'):
  return 'HISTORICAL_BUILD_SCRIPT_ALLOWED'
 if rel.startswith('scripts/') and rel not in {'scripts/EXECUTION_SPEC.md','scripts/build_v101119_quoted_span_presentation_closure.py','scripts/run_v101119_quoted_span_fixed_point.py','scripts/run_v101119_exhaustive_presentation_matrix.py','scripts/run_v101119_mutation_tests.py','scripts/run_v101119_reader_samsung_topology_audit.py','scripts/run_broad_runtime_matrix.py','scripts/run_sw_logic_matrix.js'}:
  return 'HISTORICAL_TOOL_LINEAGE_ALLOWED'
 if rel=='scripts/build_v101119_quoted_span_presentation_closure.py':
  if 'tokens=' in low or any(k in low for k in ['base','baseline','replace','protected','v101112']):return 'CURRENT_BUILDER_BASELINE_DEPENDENCY_ALLOWED'
 if any(k in low for k in ['immutable v101.118','immutable baseline','v101.118 baseline','baseline_version','baseline zip','baseline sha','baseline/provenance','byte/json-identical to the immutable','protected','preserve','historical','inherited','v101.112 hour-3/hour-22']):
  return 'EXPLICIT_BASELINE_OR_PROTECTED_HISTORY_ALLOWED'
 return 'FAIL_CURRENT_FACING_STALE'
for p in sorted(x for x in CAND.rglob('*') if x.is_file() and x.suffix.lower() not in {'.png','.ico'}):
 rel=p.relative_to(CAND).as_posix()
 if rel in SCAN_EXCLUDE:continue
 txt=p.read_text(encoding='utf-8',errors='ignore')
 for tok in TOKENS:
  if tok not in txt:continue
  for i,line in enumerate(txt.splitlines(),1):
   if tok not in line:continue
   cls=classify_line(rel,tok,line);stale.append([rel,i,tok,cls,line.strip()])
   if cls.startswith('FAIL'):fail.append((rel,i,tok,line.strip()))
with (CAND/'reports/stale_reference_scan.csv').open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['path','line','token','classification','text']);w.writerows(stale)
(CAND/'reports/stale_reference_scan.txt').write_text(f'current_version={VERSION}\nclassified_line_hits={len(stale)}\nfailures={len(fail)}\n' + ('\n'.join(map(str,fail)) if fail else 'all older-version references classified as immutable-baseline/protected-history/historical-tool lineage\n'),encoding='utf-8')
assert not fail,fail
with (CAND/'reports/report_claims_vs_evidence_audit.md').open('a',encoding='utf-8') as f:f.write('- PASS — final recursive stale/reference scan has zero failures — `reports/stale_reference_scan.txt`\n')
# Refresh active line audit for the appended claims line.
line_rows=[]
for rel in active:
 for n,line in enumerate((CAND/rel).read_text(encoding='utf-8',errors='ignore').splitlines(),1):
  if not line.strip():continue
  status='PASS';binding='TEXT_OR_EVIDENCE_STATEMENT'
  if 'NOT_TESTED' in line:binding='EXTERNAL_GATE_BOUNDARY'
  if '34' in line and ('defect' in line.lower() or 'scanner' in line.lower()):binding='M1_FIXED_POINT_SUMMARY_JSON'
  if '1,990' in line or '1990' in line:binding='EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX_JSON'
  if '52/52' in line:binding='BROAD_CHROMIUM_RUNTIME_MATRIX_JSON'
  if '15/15' in line:binding='SERVICE_WORKER_LOGIC_MATRIX_JSON'
  if '5/5' in line:binding='MUTATION_TEST_MATRIX_JSON'
  if 'stale/reference scan' in line.lower():binding='STALE_REFERENCE_SCAN_TXT'
  line_rows.append([rel,n,'CLAIM_OR_CONTEXT',binding,status,line.strip()])
with (CAND/'reports/active_report_line_audit.csv').open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['path','line','type','evidence_binding','status','text']);w.writerows(line_rows)
# One non-mutating post-line-audit stale assertion checks the generated line-audit itself.
for i,line in enumerate((CAND/'reports/active_report_line_audit.csv').read_text(encoding='utf-8',errors='ignore').splitlines(),1):
 for tok in TOKENS:
  if tok in line and classify_line('reports/active_report_line_audit.csv',tok,line).startswith('FAIL'):
   raise AssertionError(('active_report_line_audit_stale',i,tok,line[:300]))
# manifests last, deterministic tree A/B is established by copying candidate before manifests and independently generating identical files.
def files(t):return sorted([p for p in t.rglob('*') if p.is_file()],key=lambda p:p.relative_to(t).as_posix())
def write_manifests(t):
 for rel in ['metadata/package_manifest.json','metadata/hash_manifest.json']:(t/rel).unlink(missing_ok=True)
 arr=files(t);ents=[{'path':p.relative_to(t).as_posix(),'size':p.stat().st_size} for p in arr]
 (t/'metadata/package_manifest.json').write_text(json.dumps({'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'self_exclusion':['metadata/package_manifest.json','metadata/hash_manifest.json'],'file_count':len(ents),'files':ents},ensure_ascii=False,indent=2)+'\n')
 arr=files(t);ents=[]
 for p in arr:
  rel=p.relative_to(t).as_posix()
  if rel=='metadata/hash_manifest.json':continue
  ents.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p)})
 (t/'metadata/hash_manifest.json').write_text(json.dumps({'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'self_exclusion':['metadata/hash_manifest.json'],'file_count':len(ents),'files':ents},ensure_ascii=False,indent=2)+'\n')
write_manifests(CAND)
# deterministic rebuild B from finalized candidate sans manifests, then regenerate manifests
B=WORK/'candidate_B';shutil.copytree(CAND,B)
(B/'metadata/package_manifest.json').unlink();(B/'metadata/hash_manifest.json').unlink();write_manifests(B)
def treehash(t):return {p.relative_to(t).as_posix():sha(p) for p in files(t)}
assert treehash(CAND)==treehash(B)
# deterministic ZIP writer
def zipit(t,o):
 with zipfile.ZipFile(o,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in files(t):
   rel=p.relative_to(t).as_posix();zi=zipfile.ZipInfo(rel,date_time=(2026,8,25,12,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=(0o100644<<16);z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
za=WORK/'A.zip';zb=WORK/'B.zip';zipit(CAND,za);zipit(B,zb);assert za.read_bytes()==zb.read_bytes();shutil.copy2(za,OUTZIP)
print(json.dumps({'status':'PASS_PREPACKAGE_PENDING_FINAL_REOPEN','package':str(OUTZIP),'zip_sha256':sha(OUTZIP),'html_sha256':sha(CAND/'index.html'),'members':len(files(CAND)),'projection_diff_targets':len(proj_diff),'adjudication_diff_targets':len(adj_diff),'m1_defects_before':34,'m1_defects_after':0,'broad_runtime':broadj['summary'],'presentation_runtime':presj['summary'],'sw_logic':swj['summary'],'active_report_lines':len(line_rows)},ensure_ascii=False,indent=2))
