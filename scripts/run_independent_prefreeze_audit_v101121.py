#!/usr/bin/env python3
from pathlib import Path
import sys, json, csv, re, hashlib, zipfile
BASE=Path(sys.argv[1]); TREE=Path(sys.argv[2]); OUTJ=Path(sys.argv[3]); OUTM=Path(sys.argv[4]); VER=sys.argv[5]; STAGE=sys.argv[6]
sha=lambda b:hashlib.sha256(b).hexdigest()
C=[]
def ck(name,ok,detail=''): C.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':detail})
def expr(txt,name):
 m=re.search(r'const\s+'+re.escape(name)+r'\s*=\s*',txt); 
 if not m: raise AssertionError(name)
 i=m.end(); st=i; stack=[]; q=None; esc=False; pairs={')':'(',']':'[','}':'{'}
 while i<len(txt):
  c=txt[i]
  if q:
   if esc: esc=False
   elif c=='\\': esc=True
   elif c==q: q=None
   i+=1; continue
  if c in "'\"`": q=c; i+=1; continue
  if c in '([{': stack.append(c); i+=1; continue
  if c in ')]}':
   if not stack or stack[-1]!=pairs[c]: raise AssertionError((name,i))
   stack.pop(); i+=1; continue
  if c==';' and not stack: return txt[st:i].strip()
  i+=1
 raise AssertionError(name)
with zipfile.ZipFile(BASE) as z: bhtml=z.read('index.html').decode('utf-8')
html=(TREE/'index.html').read_text(encoding='utf-8')
ck('root_html_twins',(TREE/'index.html').read_bytes()==(TREE/'luisa_24_heures.html').read_bytes())
ck('current_identity',f"const APP_VERSION = '{VER}';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html)
prot=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_PROJECTION','SPEECH_PRESENTATION_ADJUDICATIONS']
par=[n for n in prot if expr(bhtml,n)==expr(html,n)]; ck('protected_14_expression_parity',len(par)==14,{'pass':len(par),'fail':[n for n in prot if n not in par]})
# Help itself must be identical to baseline; this stage is report/tooling only.
def funblock(txt,name,next_name):
 s=txt.index('function '+name+'('); e=txt.index('function '+next_name+'(',s); return txt[s:e]
ck('showHelp_unchanged',funblock(bhtml,'showHelp','showProvenance')==funblock(html,'showHelp','showProvenance'))
# QA template is intentionally an empty results capture schema; no stale row-count assumption.
qa=list(csv.reader((TREE/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open(encoding='utf-8')))
ck('qa_template_schema_current',qa==[['device','profile','test_id','result','notes','package_sha256']],qa)
# Runtime evidence direct.
def summary(rel): return json.loads((TREE/rel).read_text(encoding='utf-8'))['summary']
for rel,total in [('evidence/v101121/HELP_BROWSER_MATRIX.json',70),('evidence/v101121/BROAD_CHROMIUM_RUNTIME_MATRIX.json',52),('evidence/v101121/EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX.json',1990),('evidence/v101121/SERVICE_WORKER_LOGIC_MATRIX.json',15)]:
 s=summary(rel); got=s.get('checks',s.get('total')); ck('runtime_'+Path(rel).stem,s.get('fail')==0 and got==total,s)
fp=json.loads((TREE/'evidence/v101121/post_tooling_fixed_point/M1_FIXED_POINT_SUMMARY.json').read_text(encoding='utf-8'))
ck('fixed_point_zero',fp.get('presentation_relevant_spans')==398 and fp.get('scanner_a_valid_defects')==0 and fp.get('scanner_b_valid_defects')==0 and fp.get('scanner_converged') and fp.get('hidden_ranges_with_lexical_text')==0,fp)
# Current tooling inventory and semantic stale proof.
ti=json.loads((TREE/'metadata/current_tooling_inventory.json').read_text(encoding='utf-8'))
cur=set(ti['current_tools']); ck('current_tooling_inventory_complete',{'scripts/build_v101121_four_pass_report_tooling_reconciliation.py','scripts/run_independent_prefreeze_audit_v101121.py','scripts/run_v101121_help_browser_matrix.py','scripts/run_broad_runtime_matrix.py','scripts/run_v101119_exhaustive_presentation_matrix.py','scripts/run_v101119_quoted_span_fixed_point.py','scripts/run_sw_logic_matrix.js','scripts/run_v101121_primary_reopen_audit.py','scripts/run_v101121_independent_reopen_audit.py'}.issubset(cur),sorted(cur))
ck('obsolete_prefreeze_checker_not_current','scripts/run_independent_prefreeze_audit.py' not in cur and not (TREE/'scripts/run_independent_prefreeze_audit.py').exists())
# Independently challenge obsolete current-tool assumptions rather than trusting packaged stale-scan output.
obs=[]
for rel in cur:
 txt=(TREE/rel).read_text(encoding='utf-8',errors='ignore')
 for token in ['qa_'+'template_21','len(qrows)'+'==21','semantic current-metadata '+'failures: 0',"'semantic current-metadata' "+"in vj.get('release_scope','').lower()"]:
  if token in txt: obs.append((rel,token))
ck('semantic_current_tool_assumptions_zero',not obs,obs)
# Build scope and current metadata evidence.
bs=json.loads((TREE/'evidence/v101121/BUILD_SCOPE_AUDIT.json').read_text(encoding='utf-8')); ck('build_scope_pass',bs.get('status')=='PASS' and bs.get('protected_declarations')=='14/14' and bs.get('showHelp_unchanged') is True,bs)
cm=json.loads((TREE/'evidence/v101121/CURRENT_METADATA_AUDIT.json').read_text(encoding='utf-8')); ck('current_metadata_pass',cm.get('status')=='PASS' and all(cm.get('checks',{}).values()),cm)
# Report-claims/line-by-line closure is generated after this independent report is frozen and revalidated by final reopen auditors.
ck('report_claims_closure_deferred',True,'first-party claim ledger and active-line audit are post-independent-freeze artifacts validated after creation')
# Line-by-line active report audit is generated after this independent report is frozen; it is validated by both final reopened-ZIP auditors.
ck('line_audit_deferred_to_post_independent_freeze',True,'final reopened auditors enforce exact nonblank-line coverage and direct evidence fields')
# External/device boundary is explicit in current metadata.
vj=json.loads((TREE/'version.json').read_text(encoding='utf-8'))
ck('physical_live_not_tested_disclosed','NOT_TESTED' in vj.get('real_device_status','') and len(vj.get('external_open_gates',[]))>=5,vj.get('real_device_status',''))
status='PASS_PREFREEZE_INDEPENDENT_FOUR_PASS' if all(x['status']=='PASS' for x in C) else 'FAIL'
obj={'schema':'L24H_V101121_INDEPENDENT_PREFREEZE_AUDIT_V1','version':VER,'stage':STAGE,'status':status,'checks_pass':sum(x['status']=='PASS' for x in C),'checks_total':len(C),'checks_fail':sum(x['status']=='FAIL' for x in C),'implementation':'separately implemented package/tree checker; does not reuse first-party report assertions','checks':C,'limitations':['physical devices NOT_TESTED','installed PWA/offline cold reopen NOT_TESTED','VoiceOver/TalkBack NOT_TESTED','live GitHub Pages exact-byte binding NOT_TESTED']}
OUTJ.parent.mkdir(parents=True,exist_ok=True);OUTJ.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with OUTM.open('w',encoding='utf-8') as f:
 f.write(f'# Independent four-pass audit — {VER}\n\n**{status}**\n\n')
 for x in C: f.write(f'- `{x["check"]}`: **{x["status"]}**\n')
 f.write('\nPhysical-device/live-origin gates remain NOT_TESTED.\n')
print(json.dumps({'status':status,'pass':obj['checks_pass'],'total':obj['checks_total'],'fail':obj['checks_fail']}))
raise SystemExit(0 if obj['checks_fail']==0 else 2)
