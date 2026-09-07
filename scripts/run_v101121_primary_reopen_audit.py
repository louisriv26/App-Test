#!/usr/bin/env python3
from pathlib import Path
import sys,zipfile,hashlib,json,csv,subprocess,shutil,re
ZIP=Path(sys.argv[1]); BASE=Path(sys.argv[2]); OUT=Path(sys.argv[3]); VER=sys.argv[4]; STAGE=sys.argv[5]
OUT.mkdir(parents=True,exist_ok=True); EXT=OUT/'extract'; shutil.rmtree(EXT,ignore_errors=True); EXT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
def ck(n,o,d=''): rows.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
with zipfile.ZipFile(ZIP) as z:
 ck('zip_test',z.testzip() is None); names=z.namelist(); z.extractall(EXT)
ck('root_html_twins',(EXT/'index.html').read_bytes()==(EXT/'luisa_24_heures.html').read_bytes())
html=(EXT/'index.html').read_text(encoding='utf-8'); ck('identity',f"const APP_VERSION = '{VER}';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html)
# manifests
pm=json.loads((EXT/'metadata/package_manifest.json').read_text()); actual=[p.relative_to(EXT).as_posix() for p in EXT.rglob('*') if p.is_file() and p.relative_to(EXT).as_posix() not in pm['self_exclusion']]
exp=[x['path'] for x in pm['files']]; ck('package_manifest_paths',sorted(actual)==sorted(exp),{'actual':len(actual),'expected':len(exp)}); ck('package_manifest_sizes',all((EXT/x['path']).stat().st_size==x['size'] for x in pm['files']))
hm=json.loads((EXT/'metadata/hash_manifest.json').read_text()); actual2=[p.relative_to(EXT).as_posix() for p in EXT.rglob('*') if p.is_file() and p.relative_to(EXT).as_posix() not in hm['self_exclusion']]; exp2=[x['path'] for x in hm['files']]; ck('hash_manifest_paths',sorted(actual2)==sorted(exp2),{'actual':len(actual2),'expected':len(exp2)}); ck('hash_manifest_values',all((EXT/x['path']).stat().st_size==x['size'] and sha(EXT/x['path'])==x['sha256'] for x in hm['files']))
# syntax
scripts='\n'.join(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',html,re.S|re.I)); (OUT/'inline.js').write_text(scripts,encoding='utf-8'); r=subprocess.run(['node','--check',str(OUT/'inline.js')],capture_output=True,text=True); ck('js_syntax',r.returncode==0,r.stderr.strip()); r=subprocess.run(['node','--check',str(EXT/'sw.js')],capture_output=True,text=True); ck('sw_syntax',r.returncode==0,r.stderr.strip())
# fresh matrices
def run(cmd):
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=180); return r
r=run(['python',str(EXT/'scripts/run_v101121_help_browser_matrix.py'),str(EXT/'index.html'),str(OUT/'HELP_BROWSER_RERUN.json')]); ck('help_rerun',r.returncode==0,r.stdout[-500:]+r.stderr[-500:])
r=run(['python',str(EXT/'scripts/run_broad_runtime_matrix.py'),str(EXT/'index.html'),VER,str(OUT/'BROAD_RUNTIME_RERUN.json')]); ck('broad_rerun',r.returncode==0,r.stdout[-500:]+r.stderr[-500:])
fp=OUT/'FIXED_POINT_RERUN'; r=run(['python',str(EXT/'scripts/run_v101119_quoted_span_fixed_point.py'),str(EXT/'index.html'),str(fp)]); ck('fixed_point_rerun',r.returncode==0,r.stdout[-500:]+r.stderr[-500:])
r=run(['python',str(EXT/'scripts/run_v101119_exhaustive_presentation_matrix.py'),str(EXT/'index.html'),str(fp/'M1_QUOTED_SPAN_PRESENTATION_LEDGER.csv'),str(OUT/'PRESENTATION_RERUN.json'),VER]); ck('presentation_rerun',r.returncode==0,r.stdout[-500:]+r.stderr[-500:])
r=run(['node',str(EXT/'scripts/run_sw_logic_matrix.js'),str(EXT/'sw.js'),f'luisa-24h-v101-{VER.split(".")[-1]}',str(OUT/'SW_RERUN.json')]); ck('sw_logic_rerun',r.returncode==0,r.stdout[-500:]+r.stderr[-500:])
# packaged independent prefreeze checker rerun on fresh extraction, output external
r=run(['python',str(EXT/'scripts/run_independent_prefreeze_audit_v101121.py'),str(BASE),str(EXT),str(OUT/'INDEPENDENT_PREFREEZE_RERUN.json'),str(OUT/'INDEPENDENT_PREFREEZE_RERUN.md'),VER,STAGE]); ck('packaged_independent_prefreeze_rerun',r.returncode==0,r.stdout[-700:]+r.stderr[-700:])
# line audit exact/direct
inv=json.loads((EXT/'metadata/active_report_inventory.json').read_text()); la=list(csv.DictReader((EXT/'reports/active_report_line_audit.csv').open(encoding='utf-8-sig'))); expected=[]
for rel in inv['source_reports']:
 for i,line in enumerate((EXT/rel).read_text(encoding='utf-8',errors='ignore').splitlines(),1):
  if line.strip(): expected.append((rel,str(i)))
ck('active_line_coverage',[(x['path'],x['line']) for x in la]==expected,{'expected':len(expected),'got':len(la)})
ck('active_line_direct_evidence',all(x['status']=='PASS' and x.get('evidence_type') and x.get('evidence_path') and 'current authority line present' not in x.get('evidence_detail','') for x in la),{'rows':len(la)})
# current tooling sanity
ct=json.loads((EXT/'metadata/current_tooling_inventory.json').read_text()); ck('current_tools_exist',all((EXT/p).exists() for p in ct['current_tools']),ct['current_tools']); ck('obsolete_checker_removed',not (EXT/'scripts/run_independent_prefreeze_audit.py').exists())
# deterministic rebuild exact bytes
reb=OUT/'rebuild.zip'
with zipfile.ZipFile(reb,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted([p for p in EXT.rglob('*') if p.is_file()],key=lambda p:p.relative_to(EXT).as_posix()):
  rel=p.relative_to(EXT).as_posix(); zi=zipfile.ZipInfo(rel,date_time=(2026,8,25,0,0,0)); zi.compress_type=zipfile.ZIP_DEFLATED; zi.external_attr=(0o100644 & 0xffff)<<16; z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
ck('deterministic_rebuild_byte_identical',reb.read_bytes()==ZIP.read_bytes(),{'orig':sha(ZIP),'rebuilt':sha(reb)})
status='PASS' if all(x['status']=='PASS' for x in rows) else 'FAIL'
obj={'schema':'L24H_V101121_PRIMARY_FINAL_REOPEN_AUDIT_V1','version':VER,'stage':STAGE,'status':status,'zip_sha256':sha(ZIP),'html_sha256':sha(EXT/'index.html'),'checks_pass':sum(x['status']=='PASS' for x in rows),'checks_total':len(rows),'checks_fail':sum(x['status']=='FAIL' for x in rows),'checks':rows}
(OUT/'PRIMARY_FINAL_REOPEN_AUDIT_v101121.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'PRIMARY_FINAL_REOPEN_AUDIT_v101121.md').open('w',encoding='utf-8') as f:
 f.write(f'# Primary final reopened-ZIP audit — {VER}\n\n**Status: {status}**\n\n')
 for i,x in enumerate(rows,1): f.write(f'- {i:02d}. `{x["check"]}` — **{x["status"]}**'+(f' — `{str(x["detail"])[:800]}`' if x['detail'] not in ('',None) else '')+'\n')
print(json.dumps({'status':status,'checks':f"{obj['checks_pass']}/{obj['checks_total']}",'zip_sha256':sha(ZIP)})); raise SystemExit(0 if status=='PASS' else 2)
