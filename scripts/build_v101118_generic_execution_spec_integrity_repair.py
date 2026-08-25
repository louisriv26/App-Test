from __future__ import annotations
import csv,hashlib,json,re,shutil,subprocess,zipfile
from pathlib import Path

BASE_ZIP=Path('/mnt/data/L24H_v101117_GITHUB_DEPLOY_FOUR_PASS_SEMANTIC_CURRENT_METADATA_INTEGRITY_REPAIR_R1_LOCKED.zip')
BASE_SHA='a778b1b821c76b4450796d1b76354fa1aa26fde0c48eb492ea59eaeff3375a9e'
VERSION='v101.118';CACHE='luisa-24h-v101-118';DATE='2026-08-25';STAGE='FOUR_PASS_GENERIC_EXECUTION_SPEC_INTEGRITY_REPAIR_R1'
OUT=Path('/mnt/data/L24H_v101118_BUILD');FINAL=Path('/mnt/data/L24H_v101118_GITHUB_DEPLOY_FOUR_PASS_GENERIC_EXECUTION_SPEC_INTEGRITY_REPAIR_R1_LOCKED.zip')
SCRIPT_DIR=Path(__file__).resolve().parent
RUNTIME=SCRIPT_DIR/'run_broad_runtime_matrix.py';SWRUN=SCRIPT_DIR/'run_sw_logic_matrix.js';INDEP=SCRIPT_DIR/'run_independent_prefreeze_audit.py'
for _p in (RUNTIME,SWRUN,INDEP): assert _p.exists(), f'missing current runner: {_p}'

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
html=base_html.replace("const APP_VERSION = 'v101.117';","const APP_VERSION = 'v101.118';",1).replace("const APP_EVIDENCE_STAGE = 'FOUR_PASS_SEMANTIC_CURRENT_METADATA_INTEGRITY_REPAIR_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
old="const BUILD_DATE = '2026-08-25'; // v101.117 / semantic current-metadata integrity repair";new="const BUILD_DATE = '2026-08-25'; // v101.118 / generic execution-spec integrity repair";assert old in html;html=html.replace(old,new,1)
for n in PROT:assert ex(html,n)==BD[n],n
HTML_SHA=shab(html.encode())
qa=(BASE/'REAL_DEVICE_QA_CHECKLIST.md').read_text(encoding='utf-8').replace('v101.117','v101.118').replace('FOUR_PASS_SEMANTIC_CURRENT_METADATA_INTEGRITY_REPAIR_R1',STAGE).replace('luisa-24h-v101-117',CACHE)
qrows=list(csv.DictReader((BASE/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').read_text(encoding='utf-8-sig').splitlines()));assert len(qrows)==21
for r in qrows:r['app_version']=VERSION

def fs(t):return sorted([p for p in t.rglob('*') if p.is_file()],key=lambda p:p.relative_to(t).as_posix())
def wt(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')

def prepare(t):
 shutil.copytree(BASE,t)
 (t/'index.html').write_text(html,encoding='utf-8');(t/'luisa_24_heures.html').write_text(html,encoding='utf-8')
 wt(t/'README.md',f'''# Les 24 Heures de la Passion — {VERSION}

Stage: `{STAGE}`

This is a narrow evidence-integrity successor to immutable v101.117. Pass 4 of the independent deep audit found that the generic `scripts/EXECUTION_SPEC.md` still contained the historical v101.111 RA19E.2 specification. Because a generic filename is current-facing, v101.118 archives those exact historical bytes under `scripts/historical/EXECUTION_SPEC_v101111.md` and replaces the generic execution specification with the current v101.118 contract.

No governed corpus, text, display, topology, RA19E.2 speaker/presentation or RA19B flow declaration changes. All v101.117 semantic-metadata repairs, the v101.116 self-contained build repair, the Hour-3/Hour-22 fixes and runtime behaviour are inherited unchanged.

The active-report line audit remains pre-freeze; final reopened-ZIP evidence remains external. Physical devices, live origin, installed-PWA/offline and representative screen-reader gates remain external.
''')
 wt(t/'REAL_DEVICE_QA_CHECKLIST.md',qa)
 with (t/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=qrows[0].keys());w.writeheader();w.writerows(qrows)
 v=json.loads((t/'version.json').read_text());v.update({'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,'release_scope':'Four-pass semantic current-metadata/report-integrity repair: replace the stale generic execution specification with the current stage contract while preserving the historical RA19E.2 specification under an explicitly historical path; no governed runtime declaration changes.','real_device_status':f'Physical Samsung/iPhone/iPad and live-origin PWA/offline/accessibility validation NOT_TESTED for {VERSION}.','overall_release_status':'LIMITED_PASS_STATIC_IF_EXTERNAL_FINAL_REOPEN_GATES_PASS','known_blockers':[]});wt(t/'version.json',json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 m=json.loads((t/'manifest.json').read_text());m['version']=VERSION;wt(t/'manifest.json',json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 sw=(t/'sw.js').read_text().replace('/* v101.117 */','/* v101.118 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-117';",f"const CACHE_NAME = '{CACHE}';",1);wt(t/'sw.js',sw)
 prov={'version':VERSION,'build_date':DATE,'stage':STAGE,'baseline_version':'v101.117','baseline_zip_sha256':BASE_SHA,'baseline_html_sha256':BASE_HTML_SHA,'candidate_html_sha256':HTML_SHA,'scope':{'governed_runtime_declarations_changed':0,'semantic_current_metadata_repairs_inherited':3,'generic_execution_spec_repaired':True,'independent_prefreeze_runner_parameterized':True,'active_source_reports_written_before_line_audit':True,'active_report_line_audit_self_exclusion':['reports/active_report_line_audit.csv'],'qa_template_scenarios':21,'build_runner_dependencies':'SELF_CONTAINED_SIBLING_SCRIPTS'},'final_reopen_evidence':'EXTERNAL_AFTER_ZIP_FREEZE'};wt(t/'metadata/build_provenance.json',json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
 wt(t/'metadata/scope_escalation_authority.md',f'''# Scope authority — {VERSION}

Current stage: `{STAGE}`.

This successor is restricted to current execution-spec/evidence integrity, release identity propagation and evidence/manifests. It archives the historical v101.111 RA19E.2 execution specification under an explicitly historical path and makes the generic `scripts/EXECUTION_SPEC.md` describe the current v101.118 stage.

No governed runtime declaration, canonical devotional text, RA19B source-flow decision, RA19E.2 semantic/presentation decision, feature behaviour or UX behaviour is authorised to change. The v101.117 semantic-current-metadata repairs and all inherited content/runtime corrections remain protected. Any future corpus/flow/speaker/UX mutation requires a new explicitly authorised scope.
''')
 ev=t/'evidence/v101118';ev.mkdir(parents=True,exist_ok=True)
 with (ev/'AUDIT_REPAIR_LEDGER.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.writer(f);w.writerow(['action_id','target','finding','correction','status'])
  w.writerow(['AUD-118-001','scripts/EXECUTION_SPEC.md','GENERIC_CURRENT_FACING_SPEC_STALE_V101111','archive old bytes under scripts/historical/EXECUTION_SPEC_v101111.md and write current v101.118 execution spec','PASS'])
  w.writerow(['AUD-118-002','stale/semantic scanner','GENERIC_CURRENT_DOC_ROLE_NOT_ENFORCED','treat scripts/EXECUTION_SPEC.md as current-facing and require current version/stage identity','PASS'])
 wt(ev/'PREPACKAGE_STAGE_REPORT.md',f'''# {VERSION} prepackage stage report

Status: `PASS_PREPACKAGE_PENDING_FINAL_REOPEN`.

Baseline: v101.117 / `{BASE_SHA}`.

All fourteen governed runtime declarations remain exact baseline parity. The generic `scripts/EXECUTION_SPEC.md` now identifies `{VERSION}` / `{STAGE}`; the historical v101.111 RA19E.2 specification is preserved byte-for-byte at `scripts/historical/EXECUTION_SPEC_v101111.md`. Current semantic metadata remains aligned. Broad Chromium and isolated service-worker logic evidence are rerun before freeze. All active reports are finalized before the line audit.

Physical/live/installed-PWA/true-offline/screen-reader gates remain external. Final reopened-ZIP audits remain external after immutable freeze.
''')
 wt(t/'reports/no_regression_fix_ledger.csv','''action_id,target_id,class,authorization,result
AUD-118-001,scripts/EXECUTION_SPEC.md,GENERIC_CURRENT_EXECUTION_SPEC_REPAIR,DEEP_AUDIT,PASS
AUD-118-002,stale/semantic scanner,GENERIC_CURRENT_DOC_ROLE_ENFORCEMENT,DEEP_AUDIT,PASS
AUD-117-INHERITED,current semantic metadata/release-scope/no-regression-ledger repair,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS
AUD-116-INHERITED,current build self-contained sibling runners + dependency gate,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS
AUD-115-INHERITED,active-report exact line coverage,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS
V101114-INHERITED,prefreeze runtime/SW evidence integration,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS
V101113-INHERITED,root QA metadata correction,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS
V101112-INHERITED,H3 + H22 user-confirmed corrections,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS
RA19E2-INHERITED,10 authorised speaker/presentation actions,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS
''')
 wt(t/'reports/root_deploy_consistency_report.md',f'''# Root/deploy consistency — {VERSION}\n\n- Package root is the deploy artifact.\n- `index.html` and `luisa_24_heures.html` are byte-identical.\n- Separate deploy directory: NOT_APPLICABLE.\n- Nested deploy ZIP: NOT_APPLICABLE.\n- Current version: `{VERSION}`.\n''')
 wt(t/'reports/nested_zip_consistency_report.md','# Nested ZIP consistency\n\nNo nested ZIP is part of this deployment architecture. Status: `NOT_APPLICABLE`.\n')
 wt(t/'reports/current_metadata_semantic_consistency.md',f'''# Current metadata semantic consistency — {VERSION}

Status: `PASS_PREPACKAGE`.

- `version.json.release_scope`, `metadata/scope_escalation_authority.md` and the active no-regression ledger identify the current v101.118 evidence-only scope.
- Generic `scripts/EXECUTION_SPEC.md` identifies `{VERSION}` / `{STAGE}`.
- The previous v101.111 execution specification is preserved under the explicit historical path `scripts/historical/EXECUTION_SPEC_v101111.md`.
- `scripts/run_independent_prefreeze_audit.py` remains version-parameterized; it does not hard-code a current evidence version folder.
- Governed runtime declarations remain exact v101.117 parity.
''')
 wt(t/'reports/report_claims_vs_evidence_audit.md',f'''# Report claims vs evidence — {VERSION}

The generic current execution specification, current builder and three audit runners are aligned to v101.118; the superseded v101.111 execution specification is retained only under an explicitly historical path. Current metadata semantic consistency is checked explicitly and by the stale/semantic scanner. Every nonblank line of every active report is represented in the line-audit CSV; the CSV itself is the sole self-excluded audit output and is checked independently after freeze. Broad Chromium and isolated service-worker PASS claims bind to packaged prefreeze JSON evidence. Physical-device, live-origin PWA/offline and screen-reader tests remain `NOT_TESTED`; final reopened-ZIP PASS is not claimed inside the package.
''')
 # Archive the previously generic historical execution spec byte-for-byte, then write the current generic spec.
 old_exec=(t/'scripts/EXECUTION_SPEC.md').read_bytes();assert old_exec.startswith(b'# v101.111 RA19E.2 execution specification')
 hist=t/'scripts/historical/EXECUTION_SPEC_v101111.md';hist.parent.mkdir(parents=True,exist_ok=True);hist.write_bytes(old_exec)
 wt(t/'scripts/EXECUTION_SPEC.md',f'''# Current execution specification — {VERSION}

Stage: `{STAGE}`.

Baseline: immutable v101.117.

Scope: execution-spec/evidence integrity only. No governed runtime declaration, canonical devotional text, RA19B source-flow decision, RA19E.2 semantic/presentation decision, feature behaviour or UX behaviour may change.

Required build lifecycle: exact baseline hash → protected declaration parity → current metadata/spec checks → fresh 52/52 Chromium matrix → fresh 15/15 service-worker logic matrix → independent prefreeze audit → active-report line audit → deterministic A/B package freeze → external primary reopened-ZIP audit → external separately implemented reopened-ZIP audit → external final decision lock.

External physical Samsung/iPhone/iPad, live-origin PWA/offline, and VoiceOver/TalkBack gates remain `NOT_TESTED` until directly executed.
''')
 # Current scripts and runners.
 shutil.copy2(RUNTIME,t/'scripts/run_broad_runtime_matrix.py');shutil.copy2(SWRUN,t/'scripts/run_sw_logic_matrix.js');shutil.copy2(INDEP,t/'scripts/run_independent_prefreeze_audit.py');shutil.copy2(Path(__file__),t/'scripts/build_v101118_generic_execution_spec_integrity_repair.py')
 # remove current generated outputs to rebuild.
 for x in ['metadata/package_manifest.json','metadata/hash_manifest.json','metadata/active_report_inventory.json','reports/stale_reference_scan.csv','reports/stale_reference_scan.txt','reports/active_report_line_audit.csv','reports/four_pass_deep_audit.md','audit/independent_four_pass_audit.md','audit/independent_four_pass_audit.json']:(t/x).unlink(missing_ok=True)

A=OUT/'A';B=OUT/'B';prepare(A);prepare(B)
# broad runtime + SW logic prefreeze
for t in (A,B):
 ev=t/'evidence/v101118'
 cp=subprocess.run(['python',str(t/'scripts/run_broad_runtime_matrix.py'),str(t/'index.html'),VERSION,str(ev/'BROAD_CHROMIUM_RUNTIME_MATRIX.json')],capture_output=True,text=True);assert cp.returncode==0,(cp.stdout,cp.stderr)
 cp=subprocess.run(['node',str(t/'scripts/run_sw_logic_matrix.js'),str(t/'sw.js'),CACHE,str(ev/'SERVICE_WORKER_LOGIC_MATRIX.json')],capture_output=True,text=True);assert cp.returncode==0,(cp.stdout,cp.stderr)
 # syntax reports
 js='\n'.join(re.findall(r'<script[^>]*>(.*?)</script>',(t/'index.html').read_text(),flags=re.S));tmp=OUT/'inline_tmp.js';tmp.write_text(js);cp=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True);wt(t/'reports/javascript_syntax_check.json',json.dumps({'status':'PASS' if cp.returncode==0 else 'FAIL','node_stderr':cp.stderr},indent=2)+'\n');assert cp.returncode==0
 cp=subprocess.run(['node','--check',str(t/'sw.js')],capture_output=True,text=True);wt(t/'reports/service_worker_syntax_check.json',json.dumps({'status':'PASS' if cp.returncode==0 else 'FAIL','node_stderr':cp.stderr},indent=2)+'\n');assert cp.returncode==0
 tmp.unlink(missing_ok=True)
 R=json.loads((t/'evidence/v101118/BROAD_CHROMIUM_RUNTIME_MATRIX.json').read_text());S=json.loads((t/'evidence/v101118/SERVICE_WORKER_LOGIC_MATRIX.json').read_text());assert R['summary']=={'pass':52,'fail':0,'total':52};assert S['summary']=={'pass':15,'fail':0,'total':15}
 # exact protected parity baseline
 h=(t/'index.html').read_text();assert all(ex(h,n)==BD[n] for n in PROT)

matrix=f'''gate,test,status,evidence\nBASELINE,v101.117 exact SHA/member freeze,PASS,{BASE_SHA}\nBUILD,deterministic A/B full-tree build,PASS,asserted before ZIP freeze\nBUILD-DEPS,current build runner dependencies,PASS,self-contained packaged sibling scripts; no obsolete external runner paths\nDATA,14 governed runtime declarations,PASS,exact RHS byte parity with v101.117\nSEMANTIC-META,current scope/release/ledger/runner semantics,PASS,reports/current_metadata_semantic_consistency.md\nH3-H22,user-confirmed text/paragraph repairs preserved,PASS,broad runtime 4/4 profiles\nQA-META,root physical/live QA metadata,PASS,21/21 template rows target {VERSION}\nJS,inline JavaScript syntax,PASS,reports/javascript_syntax_check.json\nSW-SYNTAX,service-worker syntax,PASS,reports/service_worker_syntax_check.json\nRUNTIME,broad Chromium DOM/runtime matrix,PASS,evidence/v101118/BROAD_CHROMIUM_RUNTIME_MATRIX.json 52/52\nSW-LOGIC,isolated service-worker logic,PASS,evidence/v101118/SERVICE_WORKER_LOGIC_MATRIX.json 15/15\nACTIVE-REPORTS,all inventoried active source-report lines,PASS,reports/active_report_line_audit.csv exact coverage\nSTALE,current-facing token + semantic stale scan,PASS,reports/stale_reference_scan.* failures 0\nphysical devices,iPhone/iPad/Samsung,NOT_TESTED,external\nlive PWA/offline,real origin/service worker,NOT_TESTED,external\nscreen reader,VoiceOver/TalkBack,NOT_TESTED,external\n'''
for t in (A,B):wt(t/'reports/full_regression_matrix.csv',matrix)

ACTIVE={'README.md','REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','version.json','manifest.json','sw.js','metadata/build_provenance.json','metadata/scope_escalation_authority.md','scripts/EXECUTION_SPEC.md','evidence/v101118/PREPACKAGE_STAGE_REPORT.md','reports/full_regression_matrix.csv','reports/no_regression_fix_ledger.csv','reports/current_metadata_semantic_consistency.md','reports/report_claims_vs_evidence_audit.md','reports/root_deploy_consistency_report.md','reports/nested_zip_consistency_report.md','reports/javascript_syntax_check.json','reports/service_worker_syntax_check.json'}
CURRENT_SCRIPTS={'scripts/build_v101118_generic_execution_spec_integrity_repair.py','scripts/run_broad_runtime_matrix.py','scripts/run_sw_logic_matrix.js','scripts/run_independent_prefreeze_audit.py'}

def allow(rel,tok):
 if tok in {'v101.117','L24H_v101117_'}:return rel in {'README.md','metadata/build_provenance.json','metadata/scope_escalation_authority.md','scripts/EXECUTION_SPEC.md','evidence/v101118/PREPACKAGE_STAGE_REPORT.md','reports/full_regression_matrix.csv','reports/no_regression_fix_ledger.csv','reports/current_metadata_semantic_consistency.md','scripts/build_v101118_generic_execution_spec_integrity_repair.py','scripts/run_independent_prefreeze_audit.py'}
 if tok=='v101.116':return rel in {'README.md','reports/no_regression_fix_ledger.csv'}
 if tok in {'v101.115','v101.114','v101.113','v101.112'}:return rel=='reports/no_regression_fix_ledger.csv'
 if tok=='v101.111':return rel in {'README.md','version.json','metadata/scope_escalation_authority.md','evidence/v101118/PREPACKAGE_STAGE_REPORT.md','reports/no_regression_fix_ledger.csv','reports/current_metadata_semantic_consistency.md','reports/report_claims_vs_evidence_audit.md'}
 return False

def semantic_checks(t):
 failures=[]
 v=json.loads((t/'version.json').read_text())
 if 'generic execution specification' not in v.get('release_scope','').lower(): failures.append(['version.json.release_scope','CURRENT_EXECUTION_SPEC_SCOPE_MISSING'])
 sc=(t/'metadata/scope_escalation_authority.md').read_text()
 if VERSION not in sc or STAGE not in sc: failures.append(['metadata/scope_escalation_authority.md','CURRENT_IDENTITY_MISSING'])
 led=(t/'reports/no_regression_fix_ledger.csv').read_text()
 for aid in ['AUD-118-001','AUD-118-002','AUD-117-INHERITED']:
  if aid not in led: failures.append(['reports/no_regression_fix_ledger.csv','MISSING_'+aid])
 spec=(t/'scripts/EXECUTION_SPEC.md').read_text()
 if VERSION not in spec or STAGE not in spec: failures.append(['scripts/EXECUTION_SPEC.md','GENERIC_EXECUTION_SPEC_NOT_CURRENT'])
 hist=t/'scripts/historical/EXECUTION_SPEC_v101111.md'
 if not hist.exists() or not hist.read_bytes().startswith(b'# v101.111 RA19E.2 execution specification'): failures.append(['scripts/historical/EXECUTION_SPEC_v101111.md','HISTORICAL_EXECUTION_SPEC_NOT_PRESERVED'])
 indep=(t/'scripts/run_independent_prefreeze_audit.py').read_text()
 if 'evidence/v101116' in indep or 'evidence/v101117' in indep: failures.append(['scripts/run_independent_prefreeze_audit.py','HARDCODED_EVIDENCE_VERSION'])
 if "VERSION.replace('.','')" not in indep: failures.append(['scripts/run_independent_prefreeze_audit.py','VERSION_DERIVED_EVIDENCE_LOOKUP_MISSING'])
 return failures

def stale(t):
 toks=['v101.117','v101.116','v101.115','v101.114','v101.113','v101.112','v101.111','luisa-24h-v101-117','luisa-24h-v101-116','luisa-24h-v101-115','luisa-24h-v101-114','luisa-24h-v101-113','luisa-24h-v101-112','luisa-24h-v101-111','L24H_v101117_','L24H_v101116_','L24H_v101115_','L24H_v101114_','L24H_v101113_','L24H_v101112_','L24H_v101111_'];rows=[];fail=0
 forbidden_deps=['/mnt/data/'+'run_v101','run_'+'v101114_broad_runtime_matrix.py','run_'+'v101114_sw_logic_matrix.js','run_'+'v101115_independent_prefreeze_audit.py']
 for rel in CURRENT_SCRIPTS:
  text=(t/rel).read_text(encoding='utf-8',errors='ignore')
  for dep in forbidden_deps:
   if dep in text:rows.append([rel,dep,'FAIL_CURRENT_SCRIPT_OBSOLETE_DEPENDENCY']);fail+=1
 for p in fs(t):
  if p.suffix.lower() in {'.png','.ico'}:continue
  rel=p.relative_to(t).as_posix();text=p.read_text(encoding='utf-8',errors='ignore')
  if rel=='scripts/build_v101118_generic_execution_spec_integrity_repair.py':continue
  for tok in toks:
   if tok not in text:continue
   if rel in ACTIVE or rel in CURRENT_SCRIPTS:cls='BASELINE_PROVENANCE_ALLOWED' if allow(rel,tok) else 'FAIL_CURRENT_FACING_STALE'
   elif rel.startswith(('evidence/','scripts/','audit/')):cls='HISTORICAL_EVIDENCE_ALLOWED'
   else:cls='HISTORICAL_OR_PROVENANCE_ALLOWED'
   if cls.startswith('FAIL'):fail+=1
   rows.append([rel,tok,cls])
 sem=semantic_checks(t)
 for path,reason in sem: rows.append([path,reason,'FAIL_CURRENT_SEMANTIC_METADATA']);fail+=1
 with (t/'reports/stale_reference_scan.csv').open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['path','token_or_rule','classification']);w.writerows(rows)
 wt(t/'reports/stale_reference_scan.txt',f'stale/reference + semantic scan\ncurrent version: {VERSION}\nclassified hits: {len(rows)}\nfailures: {fail}\ncurrent-script obsolete-dependency failures: {sum(1 for r in rows if r[2]=="FAIL_CURRENT_SCRIPT_OBSOLETE_DEPENDENCY")}\nsemantic current-metadata failures: {len(sem)}\n')
 assert fail==0,rows

for t in (A,B):stale(t)
# independent prefreeze current, after current evidence files exist, before line audit.
for t in (A,B):
 cp=subprocess.run(['python',str(t/'scripts/run_independent_prefreeze_audit.py'),str(BASE_ZIP),str(t),VERSION],capture_output=True,text=True);assert cp.returncode==0,(cp.stdout,cp.stderr)

four=f'''# Four-pass deep audit — {VERSION}

## Pass 1 — files vs build script
PASS. Exact v101.117 baseline SHA verified; fourteen governed runtime declarations remain byte-identical; current builder/runners/specification are packaged current artifacts; deterministic Build A/B is required before freeze.

## Pass 2 — runtime/package behaviour
PASS. Broad Chromium DOM/runtime matrix: 52/52. Isolated service-worker logic matrix: 15/15. JavaScript and service-worker syntax PASS. H3/H22 user-confirmed repairs remain intact.

## Pass 3 — active reports line by line
PASS. Every nonblank line in the active-report inventory is required exactly once in `reports/active_report_line_audit.csv`; the audit CSV itself is the sole self-exclusion.

## Pass 4 — contradictions/stale evidence
PASS_PREPACKAGE. The generic current `scripts/EXECUTION_SPEC.md` identifies v101.118; the old v101.111 specification is stored only under an explicit historical path. Token stale scan + semantic current-metadata scan report failures: 0. Physical/live/offline/screen-reader gates remain NOT_TESTED.

Final reopened-ZIP audits remain mandatory after immutable freeze.
'''
for t in (A,B):wt(t/'reports/four_pass_deep_audit.md',four)

ACTIVE_REPORTS=['README.md','REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','scripts/EXECUTION_SPEC.md','evidence/v101118/PREPACKAGE_STAGE_REPORT.md','reports/full_regression_matrix.csv','reports/javascript_syntax_check.json','reports/nested_zip_consistency_report.md','reports/no_regression_fix_ledger.csv','reports/current_metadata_semantic_consistency.md','reports/report_claims_vs_evidence_audit.md','reports/root_deploy_consistency_report.md','reports/service_worker_syntax_check.json','reports/stale_reference_scan.csv','reports/stale_reference_scan.txt','reports/four_pass_deep_audit.md','audit/independent_four_pass_audit.md']
for t in (A,B):wt(t/'metadata/active_report_inventory.json',json.dumps({'schema':'L24H_ACTIVE_REPORT_INVENTORY_V1','version':VERSION,'source_reports':ACTIVE_REPORTS,'self_excluded_audit_output':'reports/active_report_line_audit.csv'},indent=2)+'\n')

def lineaudit(t):
 R=json.loads((t/'evidence/v101118/BROAD_CHROMIUM_RUNTIME_MATRIX.json').read_text());S=json.loads((t/'evidence/v101118/SERVICE_WORKER_LOGIC_MATRIX.json').read_text())
 rows=[]
 for rel in ACTIVE_REPORTS:
  p=t/rel;assert p.exists(),rel
  for ln,line in enumerate(p.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
   s=line.strip()
   if not s:continue
   typ='NON_CLAIM';bind='HEADING/INSTRUCTION';status='PASS';lo=s.lower()
   if rel=='reports/stale_reference_scan.csv':
    typ='EVIDENCE_ROW';bind='STALE_OR_SEMANTIC_CLASSIFICATION_ROW';status='FAIL' if 'FAIL_CURRENT' in s else 'PASS';rows.append([rel,ln,typ,bind,status,s]);continue
   if VERSION in s or CACHE in s:typ='CLAIM';bind='CURRENT_IDENTITY_VERSION_JSON_HTML_SW'
   if 'v101.117' in s:typ='CLAIM';bind='BASELINE_OR_INHERITED_PROVENANCE'
   for vv in ['v101.116','v101.115','v101.114','v101.113','v101.112','v101.111']:
    if vv in s:
     allowed_line = (rel=='reports/no_regression_fix_ledger.csv' or (vv=='v101.116' and rel=='README.md') or (vv=='v101.111' and rel in {'README.md','evidence/v101118/PREPACKAGE_STAGE_REPORT.md','reports/current_metadata_semantic_consistency.md','reports/report_claims_vs_evidence_audit.md'}))
     if allowed_line:typ='CLAIM';bind='INHERITED_OR_FORENSIC_HISTORY'
     else:typ='CLAIM';bind='STALE_FORBIDDEN';status='FAIL'
   if '52/52' in s:typ='CLAIM';bind='BROAD_CHROMIUM_RUNTIME_MATRIX';status='PASS' if R['summary']=={'pass':52,'fail':0,'total':52} else 'FAIL'
   if '15/15' in s:typ='CLAIM';bind='SERVICE_WORKER_LOGIC_MATRIX';status='PASS' if S['summary']=={'pass':15,'fail':0,'total':15} else 'FAIL'
   if '21/21' in s or '21-row' in lo:typ='CLAIM';bind='QA_TEMPLATE_21_ROWS';status='PASS' if len(qrows)==21 else 'FAIL'
   if 'fourteen governed' in lo or '14 governed' in lo:typ='CLAIM';bind='PROTECTED_DECLARATION_PARITY';status='PASS'
   if 'failures: 0' in lo:typ='CLAIM';bind='STALE_AND_SEMANTIC_SCAN_ZERO';status='PASS'
   if 'not_tested' in lo or 'not tested' in lo:typ='CLAIM';bind='EXTERNAL_GATE_BOUNDARY';status='PASS'
   if 'byte-identical' in lo:typ='CLAIM';bind='HTML_OR_DECLARATION_PARITY';status='PASS'
   if re.search(r'\bPASS\b|PASS_PREPACKAGE',s):typ='CLAIM';bind=bind if bind!='HEADING/INSTRUCTION' else 'PACKAGED_EXECUTED_EVIDENCE'
   rows.append([rel,ln,typ,bind,status,s])
 bad=[x for x in rows if x[4]!='PASS'];assert not bad,bad
 expected={(rel,ln) for rel in ACTIVE_REPORTS for ln,line in enumerate((t/rel).read_text(encoding='utf-8',errors='ignore').splitlines(),1) if line.strip()};observed={(r[0],r[1]) for r in rows};assert expected==observed and len(observed)==len(rows)
 with (t/'reports/active_report_line_audit.csv').open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['path','line','line_type','evidence_binding','status','text']);w.writerows(rows)
 return len(rows)
counts=[lineaudit(A),lineaudit(B)];assert counts[0]==counts[1]
for t in (A,B):
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
for t in (A,B):manifests(t)

def th(t):return {p.relative_to(t).as_posix():shaf(p) for p in fs(t)}
assert th(A)==th(B)

def zipit(t,o):
 o.unlink(missing_ok=True)
 with zipfile.ZipFile(o,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in fs(t):
   rel=p.relative_to(t).as_posix();zi=zipfile.ZipInfo(rel,date_time=(2026,8,25,10,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=(0o100644<<16);z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
ZA=OUT/'A.zip';ZB=OUT/'B.zip';zipit(A,ZA);zipit(B,ZB);assert ZA.read_bytes()==ZB.read_bytes();shutil.copy2(ZA,FINAL)
print(json.dumps({'status':'PASS_PREPACKAGE','zip':str(FINAL),'zip_sha256':shaf(FINAL),'html_sha256':shaf(A/'index.html'),'members':len(fs(A)),'runtime':'52/52','sw_logic':'15/15','active_report_lines':counts[0],'active_reports':len(ACTIVE_REPORTS),'protected_declarations':'14/14','semantic_metadata_failures':0},indent=2))
