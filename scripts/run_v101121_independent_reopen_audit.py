#!/usr/bin/env python3
from pathlib import Path
import sys,subprocess,shutil,hashlib,json,csv,re
ZIP=Path(sys.argv[1]); BASE=Path(sys.argv[2]); OUT=Path(sys.argv[3]); VER=sys.argv[4]; STAGE=sys.argv[5]
shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir(parents=True);EXT=OUT/'extract';EXT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
C=[]
def ck(n,o,d=''): C.append({'name':n,'status':'PASS' if o else 'FAIL','detail':d})
r=subprocess.run(['unzip','-t',str(ZIP)],capture_output=True,text=True);ck('system_unzip_test',r.returncode==0,r.stdout[-500:]+r.stderr[-500:]);r=subprocess.run(['unzip','-q',str(ZIP),'-d',str(EXT)],capture_output=True,text=True);ck('system_unzip_extract',r.returncode==0,r.stderr[-500:])
html=(EXT/'index.html').read_text(encoding='utf-8');ck('identity',f"const APP_VERSION = '{VER}';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html);ck('root_twins',(EXT/'index.html').read_bytes()==(EXT/'luisa_24_heures.html').read_bytes())
# independent manifest checks
pm=json.loads((EXT/'metadata/package_manifest.json').read_text()); actual=sorted(p.relative_to(EXT).as_posix() for p in EXT.rglob('*') if p.is_file() and p.relative_to(EXT).as_posix() not in pm['self_exclusion']); exp=sorted(x['path'] for x in pm['files']);ck('package_manifest',actual==exp and all((EXT/x['path']).stat().st_size==x['size'] for x in pm['files']),{'actual':len(actual),'expected':len(exp)})
hm=json.loads((EXT/'metadata/hash_manifest.json').read_text()); actual2=sorted(p.relative_to(EXT).as_posix() for p in EXT.rglob('*') if p.is_file() and p.relative_to(EXT).as_posix() not in hm['self_exclusion']);exp2=sorted(x['path'] for x in hm['files']);ck('hash_manifest',actual2==exp2 and all((EXT/x['path']).stat().st_size==x['size'] and sha(EXT/x['path'])==x['sha256'] for x in hm['files']),{'actual':len(actual2),'expected':len(exp2)})
# independently parse protected declarations from system-unzipped baseline
def getexpr(txt,name):
 m=re.search(r'const\s+'+re.escape(name)+r'\s*=\s*',txt); assert m,name
 i=m.end();st=i;stack=[];q=None;esc=False;pairs={')':'(',']':'[','}':'{'}
 while i<len(txt):
  c=txt[i]
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==q:q=None
   i+=1;continue
  if c in "'\"`":q=c;i+=1;continue
  if c in '([{':stack.append(c);i+=1;continue
  if c in ')]}':
   if not stack or stack[-1]!=pairs[c]:raise AssertionError((name,i))
   stack.pop();i+=1;continue
  if c==';' and not stack:return txt[st:i].strip()
  i+=1
 raise AssertionError(name)
basehtml=subprocess.run(['unzip','-p',str(BASE),'index.html'],capture_output=True,check=True).stdout.decode('utf-8')
prot=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_PROJECTION','SPEECH_PRESENTATION_ADJUDICATIONS']
par=[n for n in prot if getexpr(basehtml,n)==getexpr(html,n)];ck('protected_14',len(par)==14,{'pass':len(par),'fail':[n for n in prot if n not in par]})
# Help block unchanged to v101.120 baseline
def funblock(txt,name,next_name):
 s=txt.index('function '+name+'(');e=txt.index('function '+next_name+'(',s);return txt[s:e]
ck('help_unchanged',funblock(basehtml,'showHelp','showProvenance')==funblock(html,'showHelp','showProvenance'))
# independent browser probes, separate implementations
cmds=[
 ('help',['python',str(EXT/'scripts/run_v101121_independent_help_probe.py'),str(EXT/'index.html'),str(OUT/'INDEPENDENT_HELP.json')],50),
 ('runtime',['python',str(EXT/'scripts/run_v101121_independent_runtime_smoke.py'),str(EXT/'index.html'),str(OUT/'INDEPENDENT_RUNTIME.json'),VER],50),
 ('presentation',['python',str(EXT/'scripts/run_v101121_independent_presentation_matrix.py'),str(EXT/'index.html'),str(EXT/'evidence/v101121/post_tooling_fixed_point/M1_QUOTED_SPAN_PRESENTATION_LEDGER.csv'),str(OUT/'INDEPENDENT_PRESENTATION.json'),VER],1990),
]
for name,cmd,total in cmds:
 rr=subprocess.run(cmd,capture_output=True,text=True,timeout=180);ok=rr.returncode==0
 if ok:
  d=json.loads(Path(cmd[3] if name!='presentation' else cmd[4]).read_text()) if False else None
 ck('independent_'+name,ok,rr.stdout[-500:]+rr.stderr[-500:])
# verify outputs explicitly
ih=json.loads((OUT/'INDEPENDENT_HELP.json').read_text());ir=json.loads((OUT/'INDEPENDENT_RUNTIME.json').read_text());ip=json.loads((OUT/'INDEPENDENT_PRESENTATION.json').read_text());ck('ind_help_50',ih['summary'].get('pass')==50 and ih['summary'].get('fail')==0,ih['summary']);ck('ind_runtime_50',ir['summary']=={'pass':50,'fail':0,'total':50},ir['summary']);ck('ind_presentation_1990',ip['summary'].get('pass')==1990 and ip['summary'].get('fail')==0 and ip['summary'].get('cross_record_spans')==257,ip['summary'])
# semantic tooling/current assumptions independent scan
ct=json.loads((EXT/'metadata/current_tooling_inventory.json').read_text());bad=[]
for rel in ct['current_tools']:
 txt=(EXT/rel).read_text(encoding='utf-8',errors='ignore')
 for token in ['qa_'+'template_21','len(qrows)'+'==21','semantic current-metadata '+'failures: 0',"'semantic current-metadata' "+"in vj.get('release_scope','').lower()"]:
  if token in txt: bad.append((rel,token))
ck('no_obsolete_current_tool_assumptions',not bad,bad)
ck('obsolete_checker_not_current',not (EXT/'scripts/run_independent_prefreeze_audit.py').exists())
# packaged semantic/version stale evidence
ss=json.loads((EXT/'evidence/v101121/SEMANTIC_STALE_SCAN.json').read_text());vs=json.loads((EXT/'evidence/v101121/VERSION_STALE_SCAN.json').read_text());ck('packaged_semantic_stale_zero',ss.get('unexplained_count')==0 and ss.get('obsolete_current_tool_assumptions')==0,ss);ck('packaged_version_stale_zero',vs.get('unexplained_count')==0,vs)
# active line audit exact/direct
inv=json.loads((EXT/'metadata/active_report_inventory.json').read_text());ar=list(csv.DictReader((EXT/'reports/active_report_line_audit.csv').open(encoding='utf-8-sig')));expected=[]
for rel in inv['source_reports']:
 for i,line in enumerate((EXT/rel).read_text(encoding='utf-8',errors='ignore').splitlines(),1):
  if line.strip(): expected.append((rel,str(i)))
ck('active_line_exact',[(r['path'],r['line']) for r in ar]==expected,{'expected':len(expected),'got':len(ar)});ck('active_line_direct',all(r['status']=='PASS' and r.get('evidence_type') and r.get('evidence_path') and 'current authority line present' not in r.get('evidence_detail','') for r in ar),{'rows':len(ar)})
# report claims and no internal final-pass overclaim
rc=json.loads((EXT/'evidence/v101121/REPORT_CLAIMS_AUDIT.json').read_text());ck('report_claims_zero_fail',rc.get('status')=='PASS' and rc.get('claims_fail')==0,rc)
claim_roots=[EXT/'README.md',EXT/'version.json']+list((EXT/'metadata').rglob('*'))+list((EXT/'reports').rglob('*'))+list((EXT/'audit').rglob('*')); claimtxt='\n'.join(x.read_text(encoding='utf-8',errors='ignore') for x in claim_roots if x.is_file() and x.suffix.lower() not in {'.png','.ico','.zip'}); final_token='FINAL_PACKAGE_REOPEN_GATE'+' = PASS'; independent_token='INDEPENDENT_REOPENED_ZIP_AUDIT_GATE'+' = PASS'; ck('no_final_reopen_pass_inside_package',final_token not in claimtxt and independent_token not in claimtxt)
status='PASS' if all(x['status']=='PASS' for x in C) else 'FAIL';obj={'schema':'L24H_V101121_INDEPENDENT_FINAL_REOPEN_AUDIT_V1','version':VER,'stage':STAGE,'status':status,'implementation':'system unzip + independent manifest/protected/tooling/report scans + separately implemented Help/runtime/presentation probes','zip_sha256':sha(ZIP),'html_sha256':sha(EXT/'index.html'),'checks_pass':sum(x['status']=='PASS' for x in C),'checks_total':len(C),'checks_fail':sum(x['status']=='FAIL' for x in C),'help':ih['summary'],'runtime':ir['summary'],'presentation':ip['summary'],'checks':C,'physical_live_pwa_accessibility':'NOT_TESTED'}
(OUT/'INDEPENDENT_FINAL_REOPEN_AUDIT_v101121.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'INDEPENDENT_FINAL_REOPEN_AUDIT_v101121.md').open('w',encoding='utf-8') as f:
 f.write(f'# Independent final reopened-ZIP audit — {VER}\n\n**Status: {status}**\n\n')
 for i,x in enumerate(C,1):f.write(f'- {i:02d}. `{x["name"]}` — **{x["status"]}**'+(f' — `{str(x["detail"])[:800]}`' if x['detail'] not in ('',None) else '')+'\n')
print(json.dumps({'status':status,'checks':f"{obj['checks_pass']}/{obj['checks_total']}",'help':ih['summary'],'runtime':ir['summary'],'presentation':ip['summary'],'zip_sha256':sha(ZIP)}));raise SystemExit(0 if status=='PASS' else 2)
