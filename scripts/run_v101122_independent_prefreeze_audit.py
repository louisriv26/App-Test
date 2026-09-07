#!/usr/bin/env python3
from pathlib import Path
import sys,zipfile,hashlib,json,re,csv,subprocess
BASE=Path(sys.argv[1]);ROOT=Path(sys.argv[2]);OJ=Path(sys.argv[3]);OM=Path(sys.argv[4]);VER=sys.argv[5];STAGE=sys.argv[6]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();C=[]
def ck(n,o,d=''):C.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
ck('baseline_hash',sha(BASE)=='e22782a8dd73fb54287cd13d61b3ff217c4d24f33702bd1397dc1b4df5c34d3a',sha(BASE))
html=(ROOT/'index.html').read_text(encoding='utf-8');ck('root_twins',(ROOT/'index.html').read_bytes()==(ROOT/'luisa_24_heures.html').read_bytes());ck('identity',f"const APP_VERSION = '{VER}';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html)
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
with zipfile.ZipFile(BASE) as z:base=z.read('index.html').decode('utf-8')
prot=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_PROJECTION','SPEECH_PRESENTATION_ADJUDICATIONS']
ck('protected_14',all(expr(base,n)==expr(html,n) for n in prot),'14 governed declarations')
def funblock(t,a,b):s=t.index('function '+a+'(');e=t.index('function '+b+'(',s);return t[s:e]
ck('help_unchanged',funblock(base,'showHelp','showProvenance')==funblock(html,'showHelp','showProvenance'))
v=json.loads((ROOT/'version.json').read_text());m=json.loads((ROOT/'manifest.json').read_text());sw=(ROOT/'sw.js').read_text();ck('release_metadata',v['app_version']==VER and m['version']==VER and 'luisa-24h-v101-122' in sw and v['storage_schema']==8 and v['personal_snapshot']==5)
# product contract independent static inspection
def fblock(name):
 s=html.index('function '+name+'(')
 # Find the function-body brace after the complete parameter list; defaults may contain `{}`.
 op=html.index('(',s);k=op+1;pd=1;q=None;esc=False
 while pd and k<len(html):
  c=html[k]
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==q:q=None
  else:
   if c in "'\"`":q=c
   elif c=='(':pd+=1
   elif c==')':pd-=1
  k+=1
 i=html.index('{',k);d=1;q=None;esc=False;j=i+1
 while d and j<len(html):
  c=html[j]
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==q:q=None
  else:
   if c in "'\"`":q=c
   elif c=='{':d+=1
   elif c=='}':d-=1
  j+=1
 return html[s:j]
a=fblock('buildHourEndActions');p=fblock('buildHour24CyclePanel');rs=fblock('restartTwentyFourHours');rr=fblock('renderReader');mm=fblock('markMeditee')
ck('hour24_contract_static',all(x in a for x in ['Réflexion et pratique','Approfondir','Revenir au début']) and 'showProgressView()' not in a and 'if (!p.complete)' in p and 'restartTwentyFourHours({requireComplete:true' in p and 'requireComplete && !p.complete' in rs and 'openHour(1, false)' in rs and 'refreshHourEndCycleUI();' in mm and '${next ? `<button class="nav-btn"' in rr and 'Revenir à l’Accueil' not in html)
# evidence files
def j(rel):return json.loads((ROOT/rel).read_text())
checks=[
 ('build_runtime_parity','evidence/v101122/BUILD_RUNTIME_PARITY.json',lambda d:d.get('status')=='PASS'),
 ('js_syntax','evidence/v101122/JAVASCRIPT_SYNTAX_CHECK.json',lambda d:d.get('status')=='PASS'),
 ('sw_syntax','evidence/v101122/SERVICE_WORKER_SYNTAX_CHECK.json',lambda d:d.get('status')=='PASS'),
 ('state_16','evidence/v101122/HOUR24_STATE_TRANSITION_MATRIX.json',lambda d:d['summary']=={'pass':16,'fail':0,'total':16}),
 ('ux_70','evidence/v101122/HOUR24_FIVE_PROFILE_UX_MATRIX.json',lambda d:d['summary']['pass']==70 and d['summary']['fail']==0),
 ('help_70','evidence/v101122/HELP_BROWSER_MATRIX.json',lambda d:d['summary']['pass']==70 and d['summary']['fail']==0),
 ('broad_52','evidence/v101122/BROAD_CHROMIUM_RUNTIME_MATRIX.json',lambda d:d['summary']=={'pass':52,'fail':0,'total':52}),
 ('fixed_point','evidence/v101122/post_hour24_fixed_point/M1_FIXED_POINT_SUMMARY.json',lambda d:d['scanner_a_valid_defects']==0 and d['scanner_b_valid_defects']==0 and d['presentation_relevant_spans']==398),
 ('presentation_1990','evidence/v101122/EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX.json',lambda d:d['summary']['pass']==1990 and d['summary']['fail']==0),
 ('sw_15','evidence/v101122/SERVICE_WORKER_LOGIC_MATRIX.json',lambda d:d['summary']=={'pass':15,'fail':0,'total':15}),
 ('mutation_12','evidence/v101122/MUTATION_TEST_MATRIX.json',lambda d:d['summary']=={'pass':12,'fail':0,'total':12}),
]
for n,r,fn in checks:
 try:d=j(r);ck(n,fn(d),d.get('summary',d.get('status')))
 except Exception as e:ck(n,False,str(e))
# independent hour24 evidence generated separately
ip=Path('/mnt/data/v101122_run/final_prefreeze/INDEPENDENT_HOUR24_PROBE.json')
if ip.exists():d=json.loads(ip.read_text());ck('independent_hour24_55',d['summary']['pass']==55 and d['summary']['fail']==0,d['summary'])
else:ck('independent_hour24_55',False,'missing external prefreeze probe')
# current tooling exists
ct=json.loads((ROOT/'metadata/current_tooling_inventory.json').read_text());ck('current_tools_exist',all((ROOT/x).exists() for x in ct['current_tools']),{'count':len(ct['current_tools'])})
# stale/line evidence if already generated
for rel,n,key in [('evidence/v101122/VERSION_STALE_SCAN.json','version_stale_zero','unexplained_count'),('evidence/v101122/SEMANTIC_STALE_SCAN.json','semantic_stale_zero','unexplained_count')]:
 pth=ROOT/rel
 if pth.exists():d=json.loads(pth.read_text());ck(n,d.get(key)==0,d)
 else:ck(n,False,'missing '+rel)
la=ROOT/'reports/active_report_line_audit.csv'
if la.exists():
 rows=list(csv.DictReader(la.open(encoding='utf-8-sig')));ck('active_line_direct',bool(rows) and all(x['status']=='PASS' and x.get('evidence_type') and x.get('evidence_path') and 'line present' not in x.get('evidence_detail','').lower() for x in rows),{'rows':len(rows)})
else:ck('active_line_direct',False,'missing')
status='PASS_PREFREEZE_INDEPENDENT_FOUR_PASS' if all(x['status']=='PASS' for x in C) else 'FAIL';obj={'schema':'L24H_V101122_INDEPENDENT_PREFREEZE_V1','version':VER,'stage':STAGE,'status':status,'checks_pass':sum(x['status']=='PASS' for x in C),'checks_total':len(C),'checks_fail':sum(x['status']=='FAIL' for x in C),'checks':C};OJ.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');OM.write_text('# Independent prefreeze audit — v101.122\n\n**'+status+'**\n\n'+'\n'.join(f'- `{x["check"]}` — **{x["status"]}** — `{str(x["detail"])[:700]}`' for x in C)+'\n');print(json.dumps({'status':status,'pass':obj['checks_pass'],'fail':obj['checks_fail'],'total':obj['checks_total']}));raise SystemExit(0 if status.startswith('PASS') else 2)
