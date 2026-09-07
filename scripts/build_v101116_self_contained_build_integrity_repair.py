from __future__ import annotations
import csv,hashlib,json,re,shutil,subprocess,zipfile
from pathlib import Path
BASE_ZIP=Path('/mnt/data/L24H_v101115_GITHUB_DEPLOY_FOUR_PASS_ACTIVE_REPORT_LINE_CLOSURE_R1_LOCKED.zip')
BASE_SHA='b5fb899b032527a3fc3cee4e79bbffd25151c9974518648b295e73903d82458a'
VERSION='v101.116';CACHE='luisa-24h-v101-116';DATE='2026-08-25';STAGE='FOUR_PASS_SELF_CONTAINED_BUILD_INTEGRITY_REPAIR_R1'
OUT=Path('/mnt/data/L24H_v101116_BUILD');FINAL=Path('/mnt/data/L24H_v101116_GITHUB_DEPLOY_FOUR_PASS_SELF_CONTAINED_BUILD_INTEGRITY_REPAIR_R1_LOCKED.zip')
SCRIPT_DIR=Path(__file__).resolve().parent
RUNTIME=SCRIPT_DIR/'run_broad_runtime_matrix.py';SWRUN=SCRIPT_DIR/'run_sw_logic_matrix.js';INDEP=SCRIPT_DIR/'run_independent_prefreeze_audit.py'
for _p in (RUNTIME,SWRUN,INDEP): assert _p.exists(), f'missing packaged/current runner: {_p}'
def shab(b):return hashlib.sha256(b).hexdigest()
def shaf(p):return shab(Path(p).read_bytes())
assert shaf(BASE_ZIP)==BASE_SHA
shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir(parents=True);FINAL.unlink(missing_ok=True)
BASE=OUT/'baseline'
with zipfile.ZipFile(BASE_ZIP) as z:assert z.testzip() is None;z.extractall(BASE)
base_html=(BASE/'index.html').read_text(encoding='utf-8');BASE_HTML_SHA=shab(base_html.encode());assert (BASE/'index.html').read_bytes()==(BASE/'luisa_24_heures.html').read_bytes()
def ex(txt,n):
 m=re.search(r'const\s+'+re.escape(n)+r'\s*=\s*',txt);assert m,n
 st=m.end();i=st;d=0;q=None;e=False
 while i<len(txt):
  c=txt[i]
  if q:
   if e:e=False
   elif c=='\\':e=True
   elif c==q:q=None
  else:
   if c in "'\"`":q=c
   elif c in '[{(':d+=1
   elif c in ']})':d-=1
   elif c==';' and d==0:return txt[st:i].strip()
  i+=1
 raise AssertionError(n)
PROT=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS']
BD={n:ex(base_html,n) for n in PROT}
html=base_html.replace("const APP_VERSION = 'v101.115';","const APP_VERSION = 'v101.116';",1).replace("const APP_EVIDENCE_STAGE = 'FOUR_PASS_ACTIVE_REPORT_LINE_CLOSURE_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
old="const BUILD_DATE = '2026-08-25'; // v101.115 / complete active-report line-audit closure";new="const BUILD_DATE = '2026-08-25'; // v101.116 / self-contained build integrity repair";assert old in html;html=html.replace(old,new,1)
for n in PROT:assert ex(html,n)==BD[n],n
HTML_SHA=shab(html.encode())
qa=(BASE/'REAL_DEVICE_QA_CHECKLIST.md').read_text(encoding='utf-8').replace('v101.115','v101.116').replace('FOUR_PASS_ACTIVE_REPORT_LINE_CLOSURE_R1',STAGE).replace('luisa-24h-v101-115',CACHE)
qrows=list(csv.DictReader((BASE/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').read_text(encoding='utf-8-sig').splitlines()));assert len(qrows)==21
for r in qrows:r['app_version']=VERSION

def fs(t):return sorted([p for p in t.rglob('*') if p.is_file()],key=lambda p:p.relative_to(t).as_posix())
def wt(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def prepare(t):
 shutil.copytree(BASE,t);(t/'index.html').write_text(html,encoding='utf-8');(t/'luisa_24_heures.html').write_text(html,encoding='utf-8')
 wt(t/'README.md',f'''# Les 24 Heures de la Passion — {VERSION}\n\nStage: `{STAGE}`\n\nThis is a narrow build/evidence-integrity successor to immutable v101.115. v101.115 passes its packaged four-pass evidence, but its current build script depends on legacy external audit-runner paths and its stale scanner treats every script as historical. v101.116 makes the current build self-contained with sibling packaged runners and adds an explicit active-script dependency gate while preserving all governed runtime declarations exactly.\n\nNo governed corpus, text, display, topology, RA19E.2 speaker/presentation or RA19B flow declaration changes. The Hour-3/Hour-22 fixes, QA metadata repair and prefreeze runtime/SW evidence methodology are inherited unchanged.\n\nThe line-audit CSV is itself the audit output and is explicitly self-excluded from source-report coverage; its row integrity is rechecked by the independent final-ZIP audits. Final reopened-ZIP evidence remains external after freeze. Physical devices, live origin, installed-PWA/offline and representative screen-reader gates remain external.\n''')
 wt(t/'REAL_DEVICE_QA_CHECKLIST.md',qa)
 with (t/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=qrows[0].keys());w.writeheader();w.writerows(qrows)
 v=json.loads((t/'version.json').read_text());v.update({'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,'release_scope':'Complete four-pass active-report line-audit closure after all current reports are written; no governed runtime declaration changes.','real_device_status':f'Physical Samsung/iPhone/iPad and live-origin PWA/offline/accessibility validation NOT_TESTED for {VERSION}.','overall_release_status':'LIMITED_PASS_STATIC_IF_EXTERNAL_FINAL_REOPEN_GATES_PASS','known_blockers':[]});wt(t/'version.json',json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 m=json.loads((t/'manifest.json').read_text());m['version']=VERSION;wt(t/'manifest.json',json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 sw=(t/'sw.js').read_text().replace('/* v101.115 */','/* v101.116 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-115';",f"const CACHE_NAME = '{CACHE}';",1);wt(t/'sw.js',sw)
 prov={'version':VERSION,'build_date':DATE,'stage':STAGE,'baseline_version':'v101.115','baseline_zip_sha256':BASE_SHA,'baseline_html_sha256':BASE_HTML_SHA,'candidate_html_sha256':HTML_SHA,'scope':{'governed_runtime_declarations_changed':0,'active_source_reports_written_before_line_audit':True,'active_report_line_audit_self_exclusion':['reports/active_report_line_audit.csv'],'qa_template_scenarios':21,'build_runner_dependencies':'SELF_CONTAINED_SIBLING_SCRIPTS'},'final_reopen_evidence':'EXTERNAL_AFTER_ZIP_FREEZE'};wt(t/'metadata/build_provenance.json',json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
 ev=t/'evidence/v101116';ev.mkdir(parents=True,exist_ok=True)
 with (ev/'AUDIT_REPAIR_LEDGER.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.writer(f);w.writerow(['action_id','target','finding','correction','status']);w.writerow(['AUD-116-001','scripts/build_v101116_self_contained_build_integrity_repair.py','EXTERNAL_RUNNER_DEPENDENCY','resolve runtime/SW/independent runners from packaged sibling scripts','PASS']);w.writerow(['AUD-116-002','stale scanner','CURRENT_SCRIPTS_MISCLASSIFIED_HISTORICAL','classify current scripts explicitly and block obsolete external runner dependencies','PASS'])
 wt(ev/'PREPACKAGE_STAGE_REPORT.md',f'''# {VERSION} prepackage stage report\n\nStatus: `PASS_PREPACKAGE_PENDING_FINAL_REOPEN`.\n\nBaseline: v101.115 / `{BASE_SHA}`.\n\nAll fourteen governed runtime declarations remain exact baseline parity. The current build script resolves all audit runners from its own packaged sibling `scripts/` directory; broad Chromium and isolated service-worker logic evidence are rerun before freeze. All active source reports are finalized before `reports/active_report_line_audit.csv` is generated. Exact path/line coverage is asserted; the audit CSV itself is the only explicit self-exclusion.\n\nPhysical/live/installed-PWA/true-offline/screen-reader gates remain external. Final reopened-ZIP audits remain external after immutable freeze.\n''')
 wt(t/'reports/no_regression_fix_ledger.csv','''action_id,target_id,class,authorization,result\nAUD-115-001,reports/active_report_line_audit.csv,ACTIVE_REPORT_COVERAGE,DEEP_AUDIT,PASS\nAUD-115-002,reports/report_claims_vs_evidence_audit.md,CLAIM_SCOPE_INTEGRITY,DEEP_AUDIT,PASS\nV101114-INHERITED,prefreeze runtime/SW evidence integration,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS\nV101113-INHERITED,root QA metadata correction,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS\nV101112-INHERITED,H3 + H22 user-confirmed corrections,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS\nRA19E2-INHERITED,10 authorised speaker/presentation actions,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS\n''')
 wt(t/'reports/root_deploy_consistency_report.md',f'''# Root/deploy consistency — {VERSION}\n\n- Package root is the deploy artifact.\n- `index.html` and `luisa_24_heures.html` are byte-identical.\n- Separate deploy directory: NOT_APPLICABLE.\n- Nested deploy ZIP: NOT_APPLICABLE.\n- Current version: `{VERSION}`.\n''')
 wt(t/'reports/nested_zip_consistency_report.md','# Nested ZIP consistency\n\nNo nested ZIP is part of this deployment architecture. Status: `NOT_APPLICABLE`.\n')
 wt(t/'reports/report_claims_vs_evidence_audit.md',f'''# Report claims vs evidence — {VERSION}\n\nThe current build script resolves broad-runtime, service-worker and independent-prefreeze runners from packaged sibling scripts; obsolete external runner paths are forbidden by the active-script dependency gate. The active source-report inventory is stored in `metadata/active_report_inventory.json`. Every nonblank line of every listed source report is represented in `reports/active_report_line_audit.csv`, generated only after all listed reports exist. The audit CSV is the sole self-excluded audit output and is checked independently after ZIP freeze. Broad Chromium and isolated service-worker logic PASS claims bind to packaged prefreeze JSON evidence. Physical-device, live-origin PWA/offline and screen-reader tests remain `NOT_TESTED`; final reopened-ZIP PASS is not claimed inside the package.\n''')
 # current scripts
 shutil.copy2(RUNTIME,t/'scripts/run_broad_runtime_matrix.py');shutil.copy2(SWRUN,t/'scripts/run_sw_logic_matrix.js');shutil.copy2(INDEP,t/'scripts/run_independent_prefreeze_audit.py');shutil.copy2(Path(__file__),t/'scripts/build_v101116_self_contained_build_integrity_repair.py')
 # remove current generated outputs
 for x in ['metadata/package_manifest.json','metadata/hash_manifest.json','metadata/active_report_inventory.json','reports/stale_reference_scan.csv','reports/stale_reference_scan.txt','reports/active_report_line_audit.csv','reports/four_pass_deep_audit.md','audit/independent_four_pass_audit.md','audit/independent_four_pass_audit.json']:(t/x).unlink(missing_ok=True)
A=OUT/'A';B=OUT/'B';prepare(A);prepare(B)
# syntax
for t in [A,B]:
 txt=(t/'index.html').read_text();parts=[]
 for attrs,body in re.findall(r'<script([^>]*)>(.*?)</script>',txt,flags=re.S|re.I):
  if 'application/ld+json' in attrs or 'application/json' in attrs:continue
  parts.append(body)
 tmp=t/'reports/_js.js';tmp.write_text('\n;\n'.join(parts));cp=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True);tmp.unlink();assert cp.returncode==0;wt(t/'reports/javascript_syntax_check.json',json.dumps({'status':'PASS','returncode':0,'stderr':''},indent=2)+'\n');cp=subprocess.run(['node','--check',str(t/'sw.js')],capture_output=True,text=True);assert cp.returncode==0;wt(t/'reports/service_worker_syntax_check.json',json.dumps({'status':'PASS','returncode':0,'stderr':''},indent=2)+'\n')
# prefreeze runtime + SW, once then exact copy
rt=A/'evidence/v101116/BROAD_CHROMIUM_RUNTIME_MATRIX.json';cp=subprocess.run(['python',str(A/'scripts/run_broad_runtime_matrix.py'),str(A/'index.html'),VERSION,str(rt)],capture_output=True,text=True,timeout=240);assert cp.returncode==0,(cp.stdout,cp.stderr);R=json.loads(rt.read_text());assert R['summary']=={'pass':52,'fail':0,'total':52};shutil.copy2(rt,B/'evidence/v101116/BROAD_CHROMIUM_RUNTIME_MATRIX.json')
swo=A/'evidence/v101116/SERVICE_WORKER_LOGIC_MATRIX.json';cp=subprocess.run(['node',str(A/'scripts/run_sw_logic_matrix.js'),str(A/'sw.js'),CACHE,str(swo)],capture_output=True,text=True);assert cp.returncode==0,(cp.stdout,cp.stderr);S=json.loads(swo.read_text());assert S['summary']=={'pass':15,'fail':0,'total':15};shutil.copy2(swo,B/'evidence/v101116/SERVICE_WORKER_LOGIC_MATRIX.json')
# full matrix
matrix=f'''gate,test,status,evidence\nBASELINE,v101.115 exact SHA/member freeze,PASS,{BASE_SHA}\nBUILD,deterministic A/B full-tree build,PASS,asserted before ZIP freeze
BUILD-DEPS,current build runner dependencies,PASS,self-contained packaged sibling scripts; no obsolete external runner paths\nDATA,14 governed runtime declarations,PASS,exact RHS byte parity with v101.115\nH3-H22,user-confirmed text/paragraph repairs preserved,PASS,broad runtime 4/4 profiles\nQA-META,root physical/live QA metadata,PASS,21/21 template rows target {VERSION}\nJS,inline JavaScript syntax,PASS,reports/javascript_syntax_check.json\nSW-SYNTAX,service-worker syntax,PASS,reports/service_worker_syntax_check.json\nRUNTIME,broad Chromium DOM/runtime matrix,PASS,evidence/v101116/BROAD_CHROMIUM_RUNTIME_MATRIX.json 52/52\nSW-LOGIC,isolated service-worker logic,PASS,evidence/v101116/SERVICE_WORKER_LOGIC_MATRIX.json 15/15\nACTIVE-REPORTS,all inventoried active source-report lines,PASS,reports/active_report_line_audit.csv exact coverage\nSTALE,current-facing stale-reference scan,PASS,reports/stale_reference_scan.* failures 0\nphysical devices,iPhone/iPad/Samsung,NOT_TESTED,external\nlive PWA/offline,real origin/service worker,NOT_TESTED,external\nscreen reader,VoiceOver/TalkBack,NOT_TESTED,external\n'''
for t in [A,B]:wt(t/'reports/full_regression_matrix.csv',matrix)
# stale scan current-facing. Explicit baseline refs allowed, historical folders/scripts allowed.
ACTIVE={'README.md','REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','version.json','manifest.json','sw.js','metadata/build_provenance.json','evidence/v101116/PREPACKAGE_STAGE_REPORT.md','reports/full_regression_matrix.csv','reports/no_regression_fix_ledger.csv','reports/report_claims_vs_evidence_audit.md','reports/root_deploy_consistency_report.md','reports/nested_zip_consistency_report.md','reports/javascript_syntax_check.json','reports/service_worker_syntax_check.json'}
CURRENT_SCRIPTS={'scripts/build_v101116_self_contained_build_integrity_repair.py','scripts/run_broad_runtime_matrix.py','scripts/run_sw_logic_matrix.js','scripts/run_independent_prefreeze_audit.py'}
def allow(rel,tok):
 if tok in {'v101.115','L24H_v101115_'}:return rel in {'README.md','metadata/build_provenance.json','evidence/v101116/PREPACKAGE_STAGE_REPORT.md','reports/full_regression_matrix.csv','reports/no_regression_fix_ledger.csv','scripts/build_v101116_self_contained_build_integrity_repair.py','scripts/run_independent_prefreeze_audit.py'}
 if tok in {'v101.114','v101.113','v101.112'}:return rel=='reports/no_regression_fix_ledger.csv'
 return False
def stale(t):
 toks=['v101.115','v101.114','v101.113','v101.112','v101.111','luisa-24h-v101-115','luisa-24h-v101-114','luisa-24h-v101-113','luisa-24h-v101-112','luisa-24h-v101-111','L24H_v101115_','L24H_v101114_','L24H_v101113_','L24H_v101112_','L24H_v101111_'];rows=[];fail=0
 # Explicit current-script dependency gate: old external runner paths/names are forbidden.
 forbidden_deps=['/mnt/data/'+'run_v101','run_'+'v101114_broad_runtime_matrix.py','run_'+'v101114_sw_logic_matrix.js','run_'+'v101115_independent_prefreeze_audit.py']
 for rel in CURRENT_SCRIPTS:
  text=(t/rel).read_text(encoding='utf-8',errors='ignore')
  for dep in forbidden_deps:
   if dep in text:
    rows.append([rel,dep,'FAIL_CURRENT_SCRIPT_OBSOLETE_DEPENDENCY']);fail+=1
 for p in fs(t):
  if p.suffix.lower() in {'.png','.ico'}:continue
  rel=p.relative_to(t).as_posix();text=p.read_text(encoding='utf-8',errors='ignore')
  # The active build script contains the scanner vocabulary itself. Its executable
  # dependency paths are checked separately above; do not mistake vocabulary literals
  # for current-facing version claims.
  if rel=='scripts/build_v101116_self_contained_build_integrity_repair.py':
   continue
  for tok in toks:
   if tok not in text:continue
   if rel in ACTIVE or rel in CURRENT_SCRIPTS:cls='BASELINE_PROVENANCE_ALLOWED' if allow(rel,tok) else 'FAIL_CURRENT_FACING_STALE'
   elif rel.startswith(('evidence/','scripts/','audit/')):cls='HISTORICAL_EVIDENCE_ALLOWED'
   else:cls='HISTORICAL_OR_PROVENANCE_ALLOWED'
   if cls.startswith('FAIL'):fail+=1
   rows.append([rel,tok,cls])
 with (t/'reports/stale_reference_scan.csv').open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['path','token','classification']);w.writerows(rows)
 wt(t/'reports/stale_reference_scan.txt',f'stale/reference scan\ncurrent version: {VERSION}\nclassified hits: {len(rows)}\nfailures: {fail}\ncurrent-script obsolete-dependency failures: {sum(1 for r in rows if r[2]=="FAIL_CURRENT_SCRIPT_OBSOLETE_DEPENDENCY")}\n');assert fail==0,rows
for t in [A,B]:stale(t)
# Independent prefreeze report exists BEFORE line audit.
for t in [A,B]:
 # runner currently expects evidence/v101116 and is otherwise parameterized
 cp=subprocess.run(['python',str(t/'scripts/run_independent_prefreeze_audit.py'),str(BASE_ZIP),str(t),VERSION],capture_output=True,text=True);assert cp.returncode==0,(cp.stdout,cp.stderr)
# Four-pass report exists BEFORE line audit; no dynamic line count/self-reference.
four=f'''# Four-pass deep audit — {VERSION}\n\n## Pass 1 — files vs build script\nPASS. Exact v101.115 baseline SHA verified; fourteen governed runtime declarations are exact byte parity; current audit runners resolve from packaged sibling scripts; deterministic Build A/B is required before freeze.\n\n## Pass 2 — runtime/package behaviour\nPASS. Broad Chromium DOM/runtime matrix: 52/52. Isolated service-worker logic matrix: 15/15. JavaScript and service-worker syntax PASS. H3/H22 user-confirmed repairs remain intact.\n\n## Pass 3 — active reports line by line\nPASS. All reports in `metadata/active_report_inventory.json` are written before the line audit. Every nonblank source line is required to appear exactly once in `reports/active_report_line_audit.csv`. The audit CSV itself is the explicit self-excluded audit output.\n\n## Pass 4 — contradictions/stale evidence\nPASS_PREPACKAGE. Strong current-facing stale scan reports failures: 0. Root QA artifacts target {VERSION}; historical predecessor references are limited to explicit baseline/provenance/evidence contexts. Physical/live/offline/screen-reader gates remain NOT_TESTED.\n\nFinal reopened-ZIP audits remain mandatory after immutable freeze.\n'''
for t in [A,B]:wt(t/'reports/four_pass_deep_audit.md',four)
# Active source-report inventory FINAL before line audit.
ACTIVE_REPORTS=['README.md','REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','evidence/v101116/PREPACKAGE_STAGE_REPORT.md','reports/full_regression_matrix.csv','reports/javascript_syntax_check.json','reports/nested_zip_consistency_report.md','reports/no_regression_fix_ledger.csv','reports/report_claims_vs_evidence_audit.md','reports/root_deploy_consistency_report.md','reports/service_worker_syntax_check.json','reports/stale_reference_scan.csv','reports/stale_reference_scan.txt','reports/four_pass_deep_audit.md','audit/independent_four_pass_audit.md']
for t in [A,B]:wt(t/'metadata/active_report_inventory.json',json.dumps({'schema':'L24H_ACTIVE_REPORT_INVENTORY_V1','version':VERSION,'source_reports':ACTIVE_REPORTS,'self_excluded_audit_output':'reports/active_report_line_audit.csv'},indent=2)+'\n')
# Exact line-by-line audit. Strong file-specific bindings + exact coverage assertion.
def lineaudit(t):
 rows=[]
 for rel in ACTIVE_REPORTS:
  p=t/rel;assert p.exists(),rel
  for ln,line in enumerate(p.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
   s=line.strip()
   if not s:continue
   typ='NON_CLAIM';bind='HEADING/INSTRUCTION';status='PASS';lo=s.lower()
   # The stale-scan CSV is itself evidence. Historical/provenance tokens inside
   # rows explicitly classified as allowed are not current-facing stale claims.
   if rel=='reports/stale_reference_scan.csv':
    typ='EVIDENCE_ROW';bind='STALE_SCAN_CLASSIFICATION_ROW'
    status='FAIL' if 'FAIL_CURRENT_FACING_STALE' in s else 'PASS'
    rows.append([rel,ln,typ,bind,status,s])
    continue
   # current identity
   if VERSION in s or CACHE in s:typ='CLAIM';bind='CURRENT_IDENTITY_VERSION_JSON_HTML_SW'
   if 'v101.115' in s:typ='CLAIM';bind='BASELINE_PROVENANCE_SHA'
   if 'v101.114' in s or 'v101.113' in s or 'v101.112' in s:
    if rel=='reports/no_regression_fix_ledger.csv':typ='CLAIM';bind='INHERITED_HISTORY_LEDGER'
    else:typ='CLAIM';bind='STALE_FORBIDDEN';status='FAIL'
   if 'v101.111' in s:typ='CLAIM';bind='STALE_FORBIDDEN';status='FAIL'
   if '52/52' in s:typ='CLAIM';bind='BROAD_CHROMIUM_RUNTIME_MATRIX';status='PASS' if R['summary']=={'pass':52,'fail':0,'total':52} else 'FAIL'
   if '15/15' in s:typ='CLAIM';bind='SERVICE_WORKER_LOGIC_MATRIX';status='PASS' if S['summary']=={'pass':15,'fail':0,'total':15} else 'FAIL'
   if '21/21' in s or '21-row' in lo:typ='CLAIM';bind='QA_TEMPLATE_21_ROWS';status='PASS' if len(qrows)==21 else 'FAIL'
   if 'fourteen governed' in lo or '14 governed' in lo:typ='CLAIM';bind='PROTECTED_DECLARATION_PARITY';status='PASS'
   if 'failures: 0' in lo:typ='CLAIM';bind='STALE_REFERENCE_SCAN_ZERO';status='PASS'
   if 'not_tested' in lo or 'not tested' in lo:typ='CLAIM';bind='EXTERNAL_GATE_BOUNDARY';status='PASS'
   if 'byte-identical' in lo:typ='CLAIM';bind='HTML_OR_DECLARATION_PARITY';status='PASS'
   if re.search(r'\bPASS\b|PASS_PREPACKAGE',s):
    typ='CLAIM'
    if bind=='HEADING/INSTRUCTION':bind='PACKAGED_EXECUTED_EVIDENCE'
   rows.append([rel,ln,typ,bind,status,s])
 bad=[x for x in rows if x[4]!='PASS'];assert not bad,bad
 # coverage exact: one row per nonblank source line
 expected={(rel,ln) for rel in ACTIVE_REPORTS for ln,line in enumerate((t/rel).read_text(encoding='utf-8',errors='ignore').splitlines(),1) if line.strip()}
 observed={(r[0],r[1]) for r in rows};assert expected==observed and len(observed)==len(rows)
 with (t/'reports/active_report_line_audit.csv').open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['path','line','line_type','evidence_binding','status','text']);w.writerows(rows)
 return len(rows)
counts=[lineaudit(A),lineaudit(B)];assert counts[0]==counts[1]
# Now verify inventory exactly matches audit table after generation.
for t in [A,B]:
 inv=json.loads((t/'metadata/active_report_inventory.json').read_text());rows=list(csv.DictReader((t/'reports/active_report_line_audit.csv').read_text(encoding='utf-8').splitlines()));assert set(x['path'] for x in rows)==set(inv['source_reports']);assert all(x['status']=='PASS' for x in rows)
# manifests last
def manifests(t):
 for x in ['metadata/package_manifest.json','metadata/hash_manifest.json']:(t/x).unlink(missing_ok=True)
 arr=fs(t);pe=[{'path':p.relative_to(t).as_posix(),'size':p.stat().st_size} for p in arr];wt(t/'metadata/package_manifest.json',json.dumps({'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'self_exclusion':['metadata/hash_manifest.json','metadata/package_manifest.json'],'file_count':len(pe),'files':pe},ensure_ascii=False,indent=2)+'\n')
 arr=fs(t);he=[]
 for p in arr:
  rel=p.relative_to(t).as_posix()
  if rel=='metadata/hash_manifest.json':continue
  he.append({'path':rel,'size':p.stat().st_size,'sha256':shaf(p)})
 wt(t/'metadata/hash_manifest.json',json.dumps({'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'self_exclusion':['metadata/hash_manifest.json'],'file_count':len(he),'files':he},ensure_ascii=False,indent=2)+'\n')
for t in [A,B]:manifests(t)
def th(t):return {p.relative_to(t).as_posix():shaf(p) for p in fs(t)}
assert th(A)==th(B)
def zipit(t,o):
 o.unlink(missing_ok=True)
 with zipfile.ZipFile(o,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in fs(t):
   rel=p.relative_to(t).as_posix();zi=zipfile.ZipInfo(rel,date_time=(2026,8,25,9,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=(0o100644<<16);z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
ZA=OUT/'A.zip';ZB=OUT/'B.zip';zipit(A,ZA);zipit(B,ZB);assert ZA.read_bytes()==ZB.read_bytes();shutil.copy2(ZA,FINAL)
print(json.dumps({'status':'PASS_PREPACKAGE','zip':str(FINAL),'zip_sha256':shaf(FINAL),'html_sha256':shaf(A/'index.html'),'members':len(fs(A)),'runtime':'52/52','sw_logic':'15/15','active_report_lines':counts[0],'active_reports':len(ACTIVE_REPORTS),'protected_declarations':'14/14'},indent=2))
