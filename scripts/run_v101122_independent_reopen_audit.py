#!/usr/bin/env python3
from pathlib import Path
import sys,subprocess,shutil,hashlib,json,csv,re,zipfile
ZIP=Path(sys.argv[1]);BASE=Path(sys.argv[2]);OUT=Path(sys.argv[3]);VER=sys.argv[4];STAGE=sys.argv[5]
shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir(parents=True);EXT=OUT/'extract';EXT.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();C=[]
def ck(n,o,d=''):C.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
r=subprocess.run(['unzip','-t',str(ZIP)],capture_output=True,text=True);ck('system_unzip_test',r.returncode==0,r.stdout[-500:]);r=subprocess.run(['unzip','-q',str(ZIP),'-d',str(EXT)],capture_output=True,text=True);ck('system_unzip_extract',r.returncode==0,r.stderr[-500:])
html=(EXT/'index.html').read_text();ck('identity',f"const APP_VERSION = '{VER}';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html);ck('root_twins',(EXT/'index.html').read_bytes()==(EXT/'luisa_24_heures.html').read_bytes())
# manifests independent
for name in ['package_manifest','hash_manifest']:
 d=json.loads((EXT/f'metadata/{name}.json').read_text());actual=sorted(p.relative_to(EXT).as_posix() for p in EXT.rglob('*') if p.is_file() and p.relative_to(EXT).as_posix() not in d['self_exclusion']);exp=sorted(x['path'] for x in d['files']);ok=actual==exp and all((EXT/x['path']).stat().st_size==x['size'] and (name!='hash_manifest' or sha(EXT/x['path'])==x['sha256']) for x in d['files']);ck(name,ok,{'actual':len(actual),'expected':len(exp)})
# protected directly from baseline unzip-p
base=subprocess.run(['unzip','-p',str(BASE),'index.html'],capture_output=True,check=True).stdout.decode()
def expr(t,n):
 m=re.search(r'const\s+'+re.escape(n)+r'\s*=\s*',t);assert m;i=m.end();st=i;stack=[];q=None;esc=False;pairs={')':'(',']':'[','}':'{'}
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
prot=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_PROJECTION','SPEECH_PRESENTATION_ADJUDICATIONS'];ck('protected_14',all(expr(base,n)==expr(html,n) for n in prot),'14/14')
def fun(t,a,b):s=t.index('function '+a+'(');e=t.index('function '+b+'(',s);return t[s:e]
ck('help_unchanged',fun(base,'showHelp','showProvenance')==fun(html,'showHelp','showProvenance'))
# independent browser paths
def run(n,cmd,timeout=240):
 try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout);ck(n,r.returncode==0,(r.stdout+r.stderr)[-800:])
 except Exception as e:ck(n,False,str(e))
run('independent_hour24_55',['python',str(EXT/'scripts/run_v101122_independent_hour24_probe.py'),str(EXT/'index.html'),str(OUT/'IND_H24.json'),VER])
run('independent_runtime_50',['python',str(EXT/'scripts/run_v101122_independent_runtime_smoke.py'),str(EXT/'index.html'),str(OUT/'IND_RUNTIME.json'),VER])
ledger=EXT/'evidence/v101122/post_hour24_fixed_point/M1_QUOTED_SPAN_PRESENTATION_LEDGER.csv';run('independent_presentation_1990',['python',str(EXT/'scripts/run_v101122_independent_presentation_matrix.py'),str(EXT/'index.html'),str(ledger),str(OUT/'IND_PRESENTATION.json'),VER])
# exact output counts
for f,n,expect in [('IND_H24.json','ind_h24_count',55),('IND_RUNTIME.json','ind_runtime_count',50),('IND_PRESENTATION.json','ind_presentation_count',1990)]:
 p=OUT/f
 if p.exists():d=json.loads(p.read_text());s=d.get('summary',{});ck(n,s.get('pass')==expect and s.get('fail')==0,s)
 else:ck(n,False,'missing')
# current line/stale evidence
inv=json.loads((EXT/'metadata/active_report_inventory.json').read_text());ar=list(csv.DictReader((EXT/'reports/active_report_line_audit.csv').open(encoding='utf-8-sig')));expected=[]
for rel in inv['source_reports']:
 for i,line in enumerate((EXT/rel).read_text(encoding='utf-8',errors='ignore').splitlines(),1):
  if line.strip():expected.append((rel,str(i)))
ck('active_line_exact',[(x['path'],x['line']) for x in ar]==expected,{'expected':len(expected),'got':len(ar)});ck('active_line_direct',all(x['status']=='PASS' and x.get('evidence_type') and x.get('evidence_path') and 'line present' not in x.get('evidence_detail','').lower() for x in ar),{'rows':len(ar)})
vs=json.loads((EXT/'evidence/v101122/VERSION_STALE_SCAN.json').read_text());ss=json.loads((EXT/'evidence/v101122/SEMANTIC_STALE_SCAN.json').read_text());ck('version_stale_zero',vs.get('unexplained_count')==0,vs);ck('semantic_stale_zero',ss.get('unexplained_count')==0,ss)
# no premature final PASS claims in claim-bearing package artifacts
claim=[]
for p in [EXT/'README.md',EXT/'version.json']+list((EXT/'metadata').rglob('*'))+list((EXT/'reports').rglob('*'))+list((EXT/'audit').rglob('*')):
 if p.is_file() and p.suffix.lower() not in {'.png','.ico','.zip'}:claim.append(p.read_text(encoding='utf-8',errors='ignore'))
t='\n'.join(claim);ck('no_premature_final_pass','FINAL_PACKAGE_REOPEN_GATE = PASS' not in t and 'INDEPENDENT_REOPENED_ZIP_AUDIT_GATE = PASS' not in t)
status='PASS' if all(x['status']=='PASS' for x in C) else 'FAIL';obj={'schema':'L24H_V101122_INDEPENDENT_FINAL_REOPEN_AUDIT_V1','version':VER,'stage':STAGE,'status':status,'implementation':'system unzip + independent manifests/protected/line/stale scans + separately coded Hour24/runtime/presentation probes','zip_sha256':sha(ZIP),'html_sha256':sha(EXT/'index.html'),'checks_pass':sum(x['status']=='PASS' for x in C),'checks_total':len(C),'checks_fail':sum(x['status']=='FAIL' for x in C),'checks':C};(OUT/'INDEPENDENT_FINAL_REOPEN_AUDIT_v101122.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');(OUT/'INDEPENDENT_FINAL_REOPEN_AUDIT_v101122.md').write_text(f'# Independent final reopened-ZIP audit — {VER}\n\n**Status: {status}**\n\n'+'\n'.join(f'- `{x["check"]}` — **{x["status"]}** — `{str(x["detail"])[:800]}`' for x in C)+'\n');print(json.dumps({'status':status,'checks':f"{obj['checks_pass']}/{obj['checks_total']}",'zip_sha256':sha(ZIP)}));raise SystemExit(0 if status=='PASS' else 2)
