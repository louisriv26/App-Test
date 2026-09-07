#!/usr/bin/env python3
from pathlib import Path
import sys,zipfile,hashlib,json,subprocess,tempfile,shutil,csv
ZIP=Path(sys.argv[1]);BASE=Path(sys.argv[2]);OJ=Path(sys.argv[3]);OM=Path(sys.argv[4]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();C=[]
def ck(n,o,d=''):C.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
td=Path(tempfile.mkdtemp(prefix='v101124_primary_reopen_'));root=td/'root';root.mkdir()
try:
 with zipfile.ZipFile(ZIP) as z:
  bad=z.testzip(); z.extractall(root); names=[x.filename for x in z.infolist() if not x.is_dir()]
 ck('zip_crc_and_paths',bad is None and len(names)==len(set(names)) and not any(n.startswith('/') or '..' in Path(n).parts for n in names),{'members':len(names),'bad':bad})
 html=(root/'index.html').read_text();ck('current_identity',"const APP_VERSION = 'v101.124';" in html and "const APP_EVIDENCE_STAGE = 'CROSS_RECORD_CONTINUITY_INLINE_FLOW_CLOSURE_R1';" in html)
 # manifest/hash exact
 pm=json.loads((root/'metadata/package_manifest.json').read_text());hm=json.loads((root/'metadata/hash_manifest.json').read_text());ex=set(hm['self_exclusion']);actual={}
 for p in root.rglob('*'):
  if p.is_file():
   rel=p.relative_to(root).as_posix()
   if rel not in ex:actual[rel]=(p.stat().st_size,sha(p))
 listed={x['path']:(x['size'],x['sha256']) for x in hm['files']};ck('manifests',listed==actual and pm['file_count']==len(pm['files'])==len(actual),{'listed':len(listed),'actual':len(actual)})
 # prefreeze all substantive matrices freshly
 pj=td/'prefreeze.json';pmf=td/'prefreeze.md';p=subprocess.run(['python',str(root/'scripts/run_v101124_independent_prefreeze_audit.py'),str(BASE),str(root),str(pj),str(pmf)],capture_output=True,text=True,timeout=1800);po=json.loads(pj.read_text()) if pj.exists() else {};ck('fresh_prefreeze',p.returncode==0 and po.get('status')=='PASS_PREFREEZE_INDEPENDENT_FOUR_PASS',{'returncode':p.returncode,'summary':{k:po.get(k) for k in ['checks_pass','checks_fail','checks_total']},'stderr':p.stderr[-500:]})
 # exact full builder + deterministic rebuild
 rebuilt=td/'rebuilt';rz=td/'rebuilt.zip';p=subprocess.run(['python',str(root/'scripts/build_v101124_full_package_reconciliation.py'),str(BASE),str(rebuilt),str(root),str(rz)],capture_output=True,text=True,timeout=300);ck('full_builder_reproduction',p.returncode==0,{'returncode':p.returncode,'stderr':p.stderr[-500:]});ck('deterministic_zip_rebuild',p.returncode==0 and sha(rz)==sha(ZIP),{'frozen':sha(ZIP),'rebuilt':sha(rz) if rz.exists() else None})
 # direct current report exactness independent of prefreeze status
 inv=json.loads((root/'metadata/active_report_inventory.json').read_text());rows=list(csv.DictReader((root/'reports/active_report_line_audit.csv').open(encoding='utf-8-sig')));exp=[]
 for rel in inv['source_reports']:
  for i,line in enumerate((root/rel).read_text(encoding='utf-8-sig').splitlines(),1):
   if line.strip():exp.append((rel,str(i),line))
 got={(r['path'],r['line'],r['line_text']) for r in rows};ck('active_report_exact_coverage',got==set(exp) and all(r['status']=='PASS' and r['evidence_type'] and r['evidence_path'] for r in rows),{'rows':len(rows),'expected':len(exp)})
 status='PASS' if all(x['status']=='PASS' for x in C) else 'FAIL';obj={'schema':'L24H_V101124_PRIMARY_FINAL_REOPEN_V1','version':'v101.124','status':status,'zip_sha256':sha(ZIP),'html_sha256':sha(root/'index.html'),'checks_pass':sum(x['status']=='PASS' for x in C),'checks_total':len(C),'checks':C};OJ.parent.mkdir(parents=True,exist_ok=True);OJ.write_text(json.dumps(obj,indent=2)+'\n');OM.write_text('# Primary final reopened-ZIP audit — v101.124\n\n**'+status+'**\n\n'+'\n'.join(f'- `{x["check"]}` — **{x["status"]}** — `{str(x["detail"])[:800]}`' for x in C)+'\n');print(json.dumps({'status':status,'pass':obj['checks_pass'],'total':obj['checks_total'],'zip_sha256':obj['zip_sha256']}));raise SystemExit(0 if status=='PASS' else 2)
finally:shutil.rmtree(td,ignore_errors=True)
