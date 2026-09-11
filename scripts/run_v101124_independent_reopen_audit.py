#!/usr/bin/env python3
from pathlib import Path
import sys,hashlib,json,subprocess,tempfile,shutil,csv,os
ZIP=Path(sys.argv[1]);BASE=Path(sys.argv[2]);OJ=Path(sys.argv[3]);OM=Path(sys.argv[4]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();C=[]
def ck(n,o,d=''):C.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
td=Path(tempfile.mkdtemp(prefix='v101124_independent_reopen_'));root=td/'root';root.mkdir()
try:
 p=subprocess.run(['unzip','-qq',str(ZIP),'-d',str(root)],capture_output=True,text=True);ck('system_unzip',p.returncode==0,p.stderr[-500:])
 html=(root/'index.html').read_text();ck('identity_and_twins',"const APP_VERSION = 'v101.124';" in html and html==(root/'luisa_24_heures.html').read_text())
 # independent hash-manifest reconciliation
 hm=json.loads((root/'metadata/hash_manifest.json').read_text());ex=set(hm['self_exclusion']);act={}
 for f in root.rglob('*'):
  if f.is_file() and f.relative_to(root).as_posix() not in ex:act[f.relative_to(root).as_posix()]=(f.stat().st_size,sha(f))
 lis={x['path']:(x['size'],x['sha256']) for x in hm['files']};ck('hash_manifest',act==lis,{'actual':len(act),'listed':len(lis)})
 # full builder executed independently
 reb=td/'reb';p=subprocess.run(['python',str(root/'scripts/build_v101124_full_package_reconciliation.py'),str(BASE),str(reb),str(root)],capture_output=True,text=True,timeout=300);ck('full_builder',p.returncode==0,{'returncode':p.returncode,'stderr':p.stderr[-500:]})
 # independent continuity browser probe
 def rr(name,cmd,out,expect,timeout=600):
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout);d=json.loads(out.read_text()) if out.exists() else {};ck(name,p.returncode==0 and expect(d),{'returncode':p.returncode,'summary':d.get('summary'),'stderr':p.stderr[-300:]})
 rr('independent_continuity', ['python',str(root/'scripts/run_v101124_independent_continuity_probe.py'),str(root/'index.html'),str(td/'ic.json'),'v101.124'],td/'ic.json',lambda d:d.get('summary',{}).get('fail')==0 and d.get('summary',{}).get('pass')==205)
 rr('independent_hour24',['python',str(root/'scripts/run_v101124_independent_hour24_probe.py'),str(root/'index.html'),str(td/'ih.json'),'v101.124'],td/'ih.json',lambda d:d.get('summary',{}).get('pass')==55 and d.get('summary',{}).get('fail')==0)
 rr('independent_runtime',['python',str(root/'scripts/run_v101124_independent_runtime_smoke.py'),str(root/'index.html'),str(td/'ir.json'),'v101.124'],td/'ir.json',lambda d:d.get('summary',{}).get('pass')==50 and d.get('summary',{}).get('fail')==0)
 # independently generate fixed ledger then independent presentation
 p=subprocess.run(['python',str(root/'scripts/run_v101119_quoted_span_fixed_point.py'),str(root/'index.html'),str(td/'fixed')],capture_output=True,text=True,timeout=300);summ=json.loads((td/'fixed/M1_FIXED_POINT_SUMMARY.json').read_text()) if (td/'fixed/M1_FIXED_POINT_SUMMARY.json').exists() else {};ck('fixed_point',p.returncode==0 and summ.get('scanner_a_valid_defects')==0 and summ.get('scanner_b_valid_defects')==0 and summ.get('presentation_relevant_spans')==398,summ)
 rr('independent_presentation',['python',str(root/'scripts/run_v101124_independent_presentation_matrix.py'),str(root/'index.html'),str(td/'fixed/M1_QUOTED_SPAN_PRESENTATION_LEDGER.csv'),str(td/'ip.json'),'v101.124'],td/'ip.json',lambda d:d.get('summary',{}).get('pass')==1990 and d.get('summary',{}).get('fail')==0,900)
 # current report line coverage, independently reconstructed
 inv=json.loads((root/'metadata/active_report_inventory.json').read_text());rows=list(csv.DictReader((root/'reports/active_report_line_audit.csv').open(encoding='utf-8-sig')));exp=[]
 for rel in inv['source_reports']:
  for i,line in enumerate((root/rel).read_text(encoding='utf-8-sig').splitlines(),1):
   if line.strip():exp.append((rel,str(i),line))
 got={(r['path'],r['line'],r['line_text']) for r in rows};ck('report_line_coverage',got==set(exp) and all(r['status']=='PASS' and r['evidence_path'] for r in rows),{'rows':len(rows),'expected':len(exp)})
 # stale scans freshly executed
 p=subprocess.run(['python',str(root/'scripts/run_v101124_stale_scans.py'),str(root),str(td/'vs.json'),str(td/'ss.json')],capture_output=True,text=True);vs=json.loads((td/'vs.json').read_text()) if (td/'vs.json').exists() else {};ss=json.loads((td/'ss.json').read_text()) if (td/'ss.json').exists() else {};ck('stale_scans',p.returncode==0 and vs.get('status')=='PASS' and ss.get('status')=='PASS',{'version':vs.get('status'),'semantic':ss.get('status')})
 status='PASS' if all(x['status']=='PASS' for x in C) else 'FAIL';obj={'schema':'L24H_V101124_INDEPENDENT_FINAL_REOPEN_V1','version':'v101.124','status':status,'zip_sha256':sha(ZIP),'html_sha256':sha(root/'index.html'),'checks_pass':sum(x['status']=='PASS' for x in C),'checks_total':len(C),'checks':C};OJ.parent.mkdir(parents=True,exist_ok=True);OJ.write_text(json.dumps(obj,indent=2)+'\n');OM.write_text('# Independent final reopened-ZIP audit — v101.124\n\n**'+status+'**\n\n'+'\n'.join(f'- `{x["check"]}` — **{x["status"]}** — `{str(x["detail"])[:800]}`' for x in C)+'\n');print(json.dumps({'status':status,'pass':obj['checks_pass'],'total':obj['checks_total'],'zip_sha256':obj['zip_sha256']}));raise SystemExit(0 if status=='PASS' else 2)
finally:shutil.rmtree(td,ignore_errors=True)
