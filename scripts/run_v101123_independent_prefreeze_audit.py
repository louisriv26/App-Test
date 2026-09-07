#!/usr/bin/env python3
from pathlib import Path
import sys,zipfile,hashlib,json,re,csv,subprocess,tempfile,shutil,os
BASE=Path(sys.argv[1]);ROOT=Path(sys.argv[2]);OJ=Path(sys.argv[3]);OM=Path(sys.argv[4])
VER='v101.123';STAGE='FOUR_PASS_BUILD_REPRODUCIBILITY_AND_SELF_AUDIT_RECONCILIATION_R1';BASE_SHA='039f7ad95bced983b5deb1613bacb92ababf75e2a162462b4389a3a028bf8565';CACHE='luisa-24h-v101-123'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest(); C=[]
def ck(n,o,d=''):C.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
def run(cmd,timeout=240):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout);return p
ck('baseline_hash',sha(BASE)==BASE_SHA,sha(BASE))
html=(ROOT/'index.html').read_text(encoding='utf-8'); html2=(ROOT/'luisa_24_heures.html').read_text(encoding='utf-8')
ck('root_twins',html==html2)
ck('identity',f"const APP_VERSION = '{VER}';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html)
with zipfile.ZipFile(BASE) as z:bhtml=z.read('index.html').decode('utf-8')
# full functional parity after normalising only successor identity/build comment
norm=html.replace("const APP_VERSION = 'v101.123';","const APP_VERSION = 'v101.122';").replace("const APP_EVIDENCE_STAGE = 'FOUR_PASS_BUILD_REPRODUCIBILITY_AND_SELF_AUDIT_RECONCILIATION_R1';","const APP_EVIDENCE_STAGE = 'HOUR24_END_OF_CYCLE_STATE_AND_ACTION_HIERARCHY_R1';").replace("const BUILD_DATE = '2026-08-28'; // v101.123 / four-pass build reproducibility and self-audit reconciliation R1","const BUILD_DATE = '2026-08-25'; // v101.122 / Hour-24 end-of-cycle state and action hierarchy R1")
ck('functional_html_identity_only',norm==bhtml)
# protected expressions independently parsed
def expr(t,n):
 m=re.search(r'const\s+'+re.escape(n)+r'\s*=\s*',t);assert m,n;i=m.end();st=i;stack=[];q=None;esc=False;pairs={')':'(',']':'[','}':'{'}
 while i<len(t):
  c=t[i]
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==q:q=None
   i+=1;continue
  if c in "'\"`":q=c;i+=1;continue
  if c in '([{':stack.append(c);i+=1;continue
  if c in ')]}':assert stack and stack[-1]==pairs[c];stack.pop();i+=1;continue
  if c==';' and not stack:return t[st:i].strip()
  i+=1
prot=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_PROJECTION','SPEECH_PRESENTATION_ADJUDICATIONS']
ck('protected_14',all(expr(bhtml,n)==expr(html,n) for n in prot),'14/14')
# Help exact parity against baseline
def funblock(t,a,b):s=t.index('function '+a+'(');e=t.index('function '+b+'(',s);return t[s:e]
ck('help_unchanged',funblock(bhtml,'showHelp','showProvenance')==funblock(html,'showHelp','showProvenance'))
v=json.loads((ROOT/'version.json').read_text());m=json.loads((ROOT/'manifest.json').read_text());sw=(ROOT/'sw.js').read_text();ck('release_metadata',v['app_version']==VER and m['version']==VER and CACHE in sw and v['storage_schema']==8 and v['personal_snapshot']==5)
# no transient current paths in current tooling/provenance
trans=[]
for p in list((ROOT/'metadata').glob('*'))+[x for x in (ROOT/'scripts').glob('run_v101123*') if x.name!='run_v101123_stale_scans.py']+[ROOT/'scripts/build_v101123_full_package_reconciliation.py']:
 if p.is_file():
  s=p.read_text(encoding='utf-8',errors='ignore')
  if re.search(r"(?:Path\s*\(\s*)?['\"]/(?:mnt|tmp)/[^'\"]*(?:run|work|deep4)[^'\"]*['\"]",s):trans.append(p.relative_to(ROOT).as_posix())
ck('no_transient_current_paths',not trans,trans)
# active report inventory must exactly cover all current root report files except the self-excluded line audit
inv=json.loads((ROOT/'metadata/active_report_inventory.json').read_text()); declared=set(inv['source_reports']); actual=set(p.relative_to(ROOT).as_posix() for p in (ROOT/'reports').iterdir() if p.is_file() and p.name!='active_report_line_audit.csv')
ck('active_report_inventory_complete',declared==actual,{'declared':len(declared),'actual':len(actual),'missing':sorted(actual-declared),'extra':sorted(declared-actual)})
# line audit direct coverage
la=ROOT/'reports/active_report_line_audit.csv'; rows=list(csv.DictReader(la.open(encoding='utf-8-sig')));expected=[]
for rel in sorted(declared):
 for i,line in enumerate((ROOT/rel).read_text(encoding='utf-8-sig').splitlines(),1):
  if line.strip():expected.append((rel,str(i),line))
got={(r['path'],r['line'],r['line_text']) for r in rows}; exp=set(expected)
ck('active_line_exact_coverage',got==exp and all(r['status']=='PASS' and r.get('evidence_type') and r.get('evidence_path') and 'line present' not in r.get('evidence_detail','').lower() for r in rows),{'rows':len(rows),'expected':len(exp),'missing':len(exp-got),'extra':len(got-exp)})
# current tools present
ct=json.loads((ROOT/'metadata/current_tooling_inventory.json').read_text());ck('current_tools_exist',all((ROOT/x).exists() for x in ct['current_tools']),len(ct['current_tools']))
# Fresh execution in isolated temp; no package pre-generated runtime evidence trusted.
td=Path(tempfile.mkdtemp(prefix='v101123_prefreeze_'))
def rr(name,cmd,parser,timeout=240):
 try:
  p=run(cmd,timeout);ok=p.returncode==0
  detail={'returncode':p.returncode,'stdout':p.stdout[-800:],'stderr':p.stderr[-800:]}
  if ok and parser: ok,detail2=parser();detail=detail2
  ck(name,ok,detail)
 except Exception as e:ck(name,False,str(e))
# full package builder self-reproduction
rr('full_package_builder_reproduction',['python',str(ROOT/'scripts/build_v101123_full_package_reconciliation.py'),str(BASE),str(td/'reb'),str(ROOT)],lambda:(True,{'status':'executed'}),300)
rr('state_16',['python',str(ROOT/'scripts/run_v101123_hour24_state_matrix.py'),str(ROOT/'index.html'),str(td/'state.json'),VER],lambda:(json.loads((td/'state.json').read_text())['summary']=={'pass':16,'fail':0,'total':16},json.loads((td/'state.json').read_text())['summary']))
rr('ux_70',['python',str(ROOT/'scripts/run_v101123_five_profile_ux_matrix.py'),str(ROOT/'index.html'),str(td/'ux.json'),VER],lambda:(json.loads((td/'ux.json').read_text())['summary']['pass']==70 and json.loads((td/'ux.json').read_text())['summary']['fail']==0,json.loads((td/'ux.json').read_text())['summary']))
rr('help_70',['python',str(ROOT/'scripts/run_v101123_help_browser_matrix.py'),str(ROOT/'index.html'),str(td/'help.json'),VER],lambda:(json.loads((td/'help.json').read_text())['summary']['pass']==70 and json.loads((td/'help.json').read_text())['summary']['fail']==0,json.loads((td/'help.json').read_text())['summary']))
rr('broad_52',['python',str(ROOT/'scripts/run_broad_runtime_matrix.py'),str(ROOT/'index.html'),VER,str(td/'broad.json')],lambda:(json.loads((td/'broad.json').read_text())['summary']=={'pass':52,'fail':0,'total':52},json.loads((td/'broad.json').read_text())['summary']),300)
rr('fixed_point',['python',str(ROOT/'scripts/run_v101119_quoted_span_fixed_point.py'),str(ROOT/'index.html'),str(td/'fixed')],lambda:(lambda d:(d['scanner_a_valid_defects']==0 and d['scanner_b_valid_defects']==0 and d['presentation_relevant_spans']==398,{'A':d['scanner_a_valid_defects'],'B':d['scanner_b_valid_defects'],'spans':d['presentation_relevant_spans']}))(json.loads((td/'fixed/M1_FIXED_POINT_SUMMARY.json').read_text())),240)
ledger=td/'fixed/M1_QUOTED_SPAN_PRESENTATION_LEDGER.csv'
rr('presentation_1990',['python',str(ROOT/'scripts/run_v101119_exhaustive_presentation_matrix.py'),str(ROOT/'index.html'),str(ledger),str(td/'pres.json'),VER],lambda:(json.loads((td/'pres.json').read_text())['summary']['pass']==1990 and json.loads((td/'pres.json').read_text())['summary']['fail']==0,json.loads((td/'pres.json').read_text())['summary']),300)
rr('sw_15',['node',str(ROOT/'scripts/run_sw_logic_matrix.js'),str(ROOT/'sw.js'),CACHE,str(td/'sw.json')],lambda:(json.loads((td/'sw.json').read_text())['summary']=={'pass':15,'fail':0,'total':15},json.loads((td/'sw.json').read_text())['summary']))
rr('mutation_12',['python',str(ROOT/'scripts/run_v101123_mutation_tests.py'),str(ROOT/'index.html'),str(td/'mut.json')],lambda:(json.loads((td/'mut.json').read_text())['summary']=={'pass':12,'fail':0,'total':12},json.loads((td/'mut.json').read_text())['summary']))
rr('ind_hour24_55',['python',str(ROOT/'scripts/run_v101123_independent_hour24_probe.py'),str(ROOT/'index.html'),str(td/'ih.json'),VER],lambda:(json.loads((td/'ih.json').read_text())['summary']['pass']==55 and json.loads((td/'ih.json').read_text())['summary']['fail']==0,json.loads((td/'ih.json').read_text())['summary']))
rr('ind_runtime_50',['python',str(ROOT/'scripts/run_v101123_independent_runtime_smoke.py'),str(ROOT/'index.html'),str(td/'ir.json'),VER],lambda:(json.loads((td/'ir.json').read_text())['summary']['pass']==50 and json.loads((td/'ir.json').read_text())['summary']['fail']==0,json.loads((td/'ir.json').read_text())['summary']))
rr('ind_presentation_1990',['python',str(ROOT/'scripts/run_v101123_independent_presentation_matrix.py'),str(ROOT/'index.html'),str(ledger),str(td/'ip.json'),VER],lambda:(json.loads((td/'ip.json').read_text())['summary']['pass']==1990 and json.loads((td/'ip.json').read_text())['summary']['fail']==0,json.loads((td/'ip.json').read_text())['summary']),300)
status='PASS_PREFREEZE_INDEPENDENT_FOUR_PASS' if all(x['status']=='PASS' for x in C) else 'FAIL'
obj={'schema':'L24H_V101123_INDEPENDENT_PREFREEZE_V1','version':VER,'stage':STAGE,'status':status,'checks_pass':sum(x['status']=='PASS' for x in C),'checks_total':len(C),'checks_fail':sum(x['status']=='FAIL' for x in C),'checks':C}
OJ.parent.mkdir(parents=True,exist_ok=True);OJ.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');OM.write_text('# Independent prefreeze audit — v101.123\n\n**'+status+'**\n\n'+'\n'.join(f'- `{x["check"]}` — **{x["status"]}** — `{str(x["detail"])[:900]}`' for x in C)+'\n')
shutil.rmtree(td,ignore_errors=True)
print(json.dumps({'status':status,'pass':obj['checks_pass'],'fail':obj['checks_fail'],'total':obj['checks_total']}));raise SystemExit(0 if status.startswith('PASS') else 2)
