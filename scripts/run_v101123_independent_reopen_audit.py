#!/usr/bin/env python3
from pathlib import Path
import sys,subprocess,hashlib,json,csv,re,shutil,tempfile,zipfile
ZIP=Path(sys.argv[1]);BASE=Path(sys.argv[2]);OUT=Path(sys.argv[3]);EXPECTED=sys.argv[4]
VER='v101.123';STAGE='FOUR_PASS_BUILD_REPRODUCIBILITY_AND_SELF_AUDIT_RECONCILIATION_R1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[]
def ck(n,o,d=''):rows.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
def run(cmd,t=420):return subprocess.run(cmd,capture_output=True,text=True,timeout=t)
shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir(parents=True);EXT=OUT/'extract';EXT.mkdir()
p=run(['unzip','-q',str(ZIP),'-d',str(EXT)],120);ck('system_unzip',p.returncode==0,p.stderr[-500:]);ck('zip_sha',sha(ZIP)==EXPECTED,sha(ZIP))
# independently validate current manifest without using primary code
hm=json.loads((EXT/'metadata/hash_manifest.json').read_text());ex=set(hm['self_exclusion']);l={x['path']:(x['size'],x['sha256']) for x in hm['files']};a={}
for pth in EXT.rglob('*'):
 if pth.is_file():
  rel=pth.relative_to(EXT).as_posix()
  if rel not in ex:a[rel]=(pth.stat().st_size,sha(pth))
ck('ind_hash_manifest',a==l,{'actual':len(a),'listed':len(l)})
# full builder execution independently required
reb=OUT/'reb';p=run(['python',str(EXT/'scripts/build_v101123_full_package_reconciliation.py'),str(BASE),str(reb),str(EXT)],180);ck('ind_full_builder',p.returncode==0,{'rc':p.returncode,'out':p.stdout[-700:],'err':p.stderr[-700:]})
# current tooling must contain no transient working-run dependency
depfiles=[p for p in list((EXT/'metadata').glob('*'))+list((EXT/'scripts').glob('*v101123*')) if p.is_file() and p.name!='run_v101123_stale_scans.py'];bad=[]
for fp in depfiles:
 s=fp.read_text(encoding='utf-8',errors='ignore')
 if re.search(r"(?:Path\s*\(\s*)?['\"]/(?:mnt|tmp)/[^'\"]*(?:run|work|deep4)[^'\"]*['\"]",s):bad.append(fp.relative_to(EXT).as_posix())
ck('ind_no_transient_paths',not bad,bad)
# active report inventory and line coverage independent
inv=json.loads((EXT/'metadata/active_report_inventory.json').read_text());decl=set(inv['source_reports']);actual=set(p.relative_to(EXT).as_posix() for p in (EXT/'reports').glob('*') if p.is_file() and p.name!='active_report_line_audit.csv');ck('ind_active_inventory',decl==actual,{'missing':sorted(actual-decl),'extra':sorted(decl-actual)})
ar=list(csv.DictReader((EXT/'reports/active_report_line_audit.csv').open(encoding='utf-8-sig')));exp=[]
for rel in sorted(decl):
 for i,line in enumerate((EXT/rel).read_text(encoding='utf-8-sig').splitlines(),1):
  if line.strip():exp.append((rel,str(i),line))
got={(r['path'],r['line'],r['line_text']) for r in ar};ck('ind_line_coverage',got==set(exp) and all(r['status']=='PASS' and r['evidence_path'] for r in ar),{'rows':len(ar),'expected':len(exp)})
# independent stage behaviour probes
p=run(['python',str(EXT/'scripts/run_v101123_independent_hour24_probe.py'),str(EXT/'index.html'),str(OUT/'hour24.json'),VER],240);ck('ind_hour24_55',p.returncode==0,json.loads((OUT/'hour24.json').read_text()).get('summary') if (OUT/'hour24.json').exists() else p.stderr[-500:])
p=run(['python',str(EXT/'scripts/run_v101123_independent_runtime_smoke.py'),str(EXT/'index.html'),str(OUT/'runtime.json'),VER],240);ck('ind_runtime_50',p.returncode==0,json.loads((OUT/'runtime.json').read_text()).get('summary') if (OUT/'runtime.json').exists() else p.stderr[-500:])
# fresh fixed ledger + independent presentation
p=run(['python',str(EXT/'scripts/run_v101119_quoted_span_fixed_point.py'),str(EXT/'index.html'),str(OUT/'fixed')],180);ck('ind_fixed_point',p.returncode==0,p.stdout[-500:])
p=run(['python',str(EXT/'scripts/run_v101123_independent_presentation_matrix.py'),str(EXT/'index.html'),str(OUT/'fixed/M1_QUOTED_SPAN_PRESENTATION_LEDGER.csv'),str(OUT/'presentation.json'),VER],300);pres=json.loads((OUT/'presentation.json').read_text()) if (OUT/'presentation.json').exists() else {};ck('ind_presentation_1990',p.returncode==0 and pres.get('summary',{}).get('pass')==1990 and pres.get('summary',{}).get('fail')==0,pres.get('summary',p.stderr[-500:]))
summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)};obj={'schema':'L24H_V101123_INDEPENDENT_REOPEN_V1','version':VER,'zip_sha256':sha(ZIP),'summary':summary,'checks':rows};(OUT/'INDEPENDENT_FINAL_REOPEN_AUDIT_v101123.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');(OUT/'INDEPENDENT_FINAL_REOPEN_AUDIT_v101123.md').write_text('# Independent final reopened-ZIP audit — v101.123\n\n**'+('PASS' if summary['fail']==0 else 'FAIL')+'**\n\n'+'\n'.join(f'- `{r["check"]}` — **{r["status"]}** — `{str(r["detail"])[:1000]}`' for r in rows)+'\n');print(json.dumps(summary));raise SystemExit(0 if summary['fail']==0 else 2)
