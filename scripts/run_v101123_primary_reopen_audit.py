#!/usr/bin/env python3
from pathlib import Path
import sys,zipfile,hashlib,json,subprocess,shutil,tempfile,csv
ZIP=Path(sys.argv[1]);BASE=Path(sys.argv[2]);OUT=Path(sys.argv[3]);EXPECTED=sys.argv[4]
VER='v101.123';STAGE='FOUR_PASS_BUILD_REPRODUCIBILITY_AND_SELF_AUDIT_RECONCILIATION_R1';FIXED=(2026,8,28,0,0,0)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[]
def ck(n,o,d=''):rows.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
def run(cmd,t=600):return subprocess.run(cmd,capture_output=True,text=True,timeout=t)
shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir(parents=True);EXT=OUT/'extract';EXT.mkdir()
ck('zip_sha',sha(ZIP)==EXPECTED,sha(ZIP))
with zipfile.ZipFile(ZIP) as z:
 bad=z.testzip();names=z.namelist();safe=all(not n.startswith('/') and '..' not in Path(n).parts for n in names);ck('archive_crc_path',bad is None and safe,{'bad':bad,'members':len(names)});z.extractall(EXT)
# manifests
hm=json.loads((EXT/'metadata/hash_manifest.json').read_text());listed={x['path']:(x['size'],x['sha256']) for x in hm['files']};ex=set(hm['self_exclusion']);act={}
for p in EXT.rglob('*'):
 if p.is_file():
  rel=p.relative_to(EXT).as_posix()
  if rel not in ex:act[rel]=(p.stat().st_size,sha(p))
ck('hash_manifest',act==listed,{'actual':len(act),'listed':len(listed)})
pm=json.loads((EXT/'metadata/package_manifest.json').read_text());ck('package_manifest',pm['file_count']==len(act) and {x['path']:x['size'] for x in pm['files']}=={k:v[0] for k,v in act.items()},pm['file_count'])
# Fresh independently implemented prefreeze checker (it reruns runtime and full builder reproduction)
p=run(['python',str(EXT/'scripts/run_v101123_independent_prefreeze_audit.py'),str(BASE),str(EXT),str(OUT/'prefreeze.json'),str(OUT/'prefreeze.md')],900);detail={'rc':p.returncode,'stdout':p.stdout[-1000:],'stderr':p.stderr[-1000:]};ck('fresh_independent_prefreeze',p.returncode==0,detail)
# Fresh explicit stale scanners
p=run(['python',str(EXT/'scripts/run_v101123_stale_scans.py'),str(EXT),str(OUT/'version_stale.json'),str(OUT/'semantic_stale.json')],120);ck('fresh_stale_scans',p.returncode==0,{'rc':p.returncode,'stdout':p.stdout[-800:],'stderr':p.stderr[-800:]})
# Current builder exact tree reproduction + deterministic zip from reproduced tree
rebroot=OUT/'builder_rebuild';rebzip=OUT/'builder_rebuild.zip';p=run(['python',str(EXT/'scripts/build_v101123_full_package_reconciliation.py'),str(BASE),str(rebroot),str(EXT),str(rebzip)],180);ck('full_builder_reproduction',p.returncode==0,{'rc':p.returncode,'stdout':p.stdout[-800:],'stderr':p.stderr[-800:]})
ck('builder_zip_byte_identical',rebzip.exists() and rebzip.read_bytes()==ZIP.read_bytes(),{'orig':sha(ZIP),'rebuilt':sha(rebzip) if rebzip.exists() else None})
# exact active line audit coverage one more time
inv=json.loads((EXT/'metadata/active_report_inventory.json').read_text());decl=set(inv['source_reports']);la=list(csv.DictReader((EXT/'reports/active_report_line_audit.csv').open(encoding='utf-8-sig')));exp=[]
for rel in sorted(decl):
 for i,line in enumerate((EXT/rel).read_text(encoding='utf-8-sig').splitlines(),1):
  if line.strip(): exp.append((rel,str(i),line))
got={(r['path'],r['line'],r['line_text']) for r in la};ck('active_report_line_coverage',set(exp)==got and all(r['status']=='PASS' for r in la),{'expected':len(exp),'rows':len(la)})
summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)};obj={'schema':'L24H_V101123_PRIMARY_REOPEN_V1','version':VER,'zip_sha256':sha(ZIP),'summary':summary,'checks':rows};(OUT/'PRIMARY_FINAL_REOPEN_AUDIT_v101123.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');(OUT/'PRIMARY_FINAL_REOPEN_AUDIT_v101123.md').write_text('# Primary final reopened-ZIP audit — v101.123\n\n**'+('PASS' if summary['fail']==0 else 'FAIL')+'**\n\n'+'\n'.join(f'- `{r["check"]}` — **{r["status"]}** — `{str(r["detail"])[:1000]}`' for r in rows)+'\n');print(json.dumps(summary));raise SystemExit(0 if summary['fail']==0 else 2)
