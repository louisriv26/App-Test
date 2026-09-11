#!/usr/bin/env python3
from pathlib import Path
import sys,zipfile,hashlib,json,csv,subprocess,shutil,re
ZIP=Path(sys.argv[1]);BASE=Path(sys.argv[2]);OUT=Path(sys.argv[3]);VER=sys.argv[4];STAGE=sys.argv[5]
shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir(parents=True);EXT=OUT/'extract';EXT.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();C=[]
def ck(n,o,d=''):C.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
with zipfile.ZipFile(ZIP) as z:ck('zip_test',z.testzip() is None);z.extractall(EXT)
html=(EXT/'index.html').read_text();ck('root_twins',(EXT/'index.html').read_bytes()==(EXT/'luisa_24_heures.html').read_bytes());ck('identity',f"const APP_VERSION = '{VER}';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html)
# manifests
for name in ['package_manifest','hash_manifest']:
 d=json.loads((EXT/f'metadata/{name}.json').read_text());actual=sorted(p.relative_to(EXT).as_posix() for p in EXT.rglob('*') if p.is_file() and p.relative_to(EXT).as_posix() not in d['self_exclusion']);exp=sorted(x['path'] for x in d['files']);ok=actual==exp and all((EXT/x['path']).stat().st_size==x['size'] and (name!='hash_manifest' or sha(EXT/x['path'])==x['sha256']) for x in d['files']);ck(name,ok,{'actual':len(actual),'expected':len(exp)})
# syntax
scripts='\n'.join(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',html,re.S|re.I));(OUT/'inline.js').write_text(scripts);r=subprocess.run(['node','--check',str(OUT/'inline.js')],capture_output=True,text=True);ck('js_syntax',r.returncode==0,r.stderr);r=subprocess.run(['node','--check',str(EXT/'sw.js')],capture_output=True,text=True);ck('sw_syntax',r.returncode==0,r.stderr)
def run(n,cmd,timeout=240):
 try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout);ck(n,r.returncode==0,(r.stdout+r.stderr)[-800:])
 except Exception as e:ck(n,False,str(e))
run('state_16',['python',str(EXT/'scripts/run_v101122_hour24_state_matrix.py'),str(EXT/'index.html'),str(OUT/'STATE16.json'),VER])
run('ux_70',['python',str(EXT/'scripts/run_v101122_five_profile_ux_matrix.py'),str(EXT/'index.html'),str(OUT/'UX70.json'),VER])
run('help_70',['python',str(EXT/'scripts/run_v101122_help_browser_matrix.py'),str(EXT/'index.html'),str(OUT/'HELP70.json')])
run('broad_52',['python',str(EXT/'scripts/run_broad_runtime_matrix.py'),str(EXT/'index.html'),VER,str(OUT/'BROAD52.json')])
fp=OUT/'fixed';run('fixed_point',['python',str(EXT/'scripts/run_v101119_quoted_span_fixed_point.py'),str(EXT/'index.html'),str(fp)])
run('presentation_1990',['python',str(EXT/'scripts/run_v101119_exhaustive_presentation_matrix.py'),str(EXT/'index.html'),str(fp/'M1_QUOTED_SPAN_PRESENTATION_LEDGER.csv'),str(OUT/'PRES1990.json'),VER])
run('sw_15',['node',str(EXT/'scripts/run_sw_logic_matrix.js'),str(EXT/'sw.js'),'luisa-24h-v101-122',str(OUT/'SW15.json')])
run('mutation_12',['python',str(EXT/'scripts/run_v101122_mutation_tests.py'),str(EXT/'index.html'),str(OUT/'MUT12.json')])
run('independent_prefreeze',['python',str(EXT/'scripts/run_v101122_independent_prefreeze_audit.py'),str(BASE),str(EXT),str(OUT/'IND_PREFREEZE.json'),str(OUT/'IND_PREFREEZE.md'),VER,STAGE])
# active lines + stale
inv=json.loads((EXT/'metadata/active_report_inventory.json').read_text());la=list(csv.DictReader((EXT/'reports/active_report_line_audit.csv').open(encoding='utf-8-sig')));expected=[]
for rel in inv['source_reports']:
 for i,line in enumerate((EXT/rel).read_text(encoding='utf-8',errors='ignore').splitlines(),1):
  if line.strip():expected.append((rel,str(i)))
ck('active_line_coverage',[(x['path'],x['line']) for x in la]==expected,{'expected':len(expected),'got':len(la)});ck('active_line_direct',all(x['status']=='PASS' and x.get('evidence_type') and x.get('evidence_path') and 'line present' not in x.get('evidence_detail','').lower() for x in la),{'rows':len(la)})
vs=json.loads((EXT/'evidence/v101122/VERSION_STALE_SCAN.json').read_text());ss=json.loads((EXT/'evidence/v101122/SEMANTIC_STALE_SCAN.json').read_text());ck('version_stale_zero',vs.get('unexplained_count')==0,vs);ck('semantic_stale_zero',ss.get('unexplained_count')==0,ss)
# current builder reproduces app runtime files
rebroot=OUT/'builder_rebuild';run('current_builder',['python',str(EXT/'scripts/build_v101122_hour24_end_of_cycle.py'),str(BASE),str(rebroot)],120)
if rebroot.exists():ck('builder_runtime_parity',all((rebroot/f).read_bytes()==(EXT/f).read_bytes() for f in ['index.html','luisa_24_heures.html','sw.js','version.json','manifest.json','README.md']))
# deterministic full ZIP rebuild
reb=OUT/'rebuild.zip'
with zipfile.ZipFile(reb,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted([p for p in EXT.rglob('*') if p.is_file()],key=lambda p:p.relative_to(EXT).as_posix()):
  rel=p.relative_to(EXT).as_posix();zi=zipfile.ZipInfo(rel,date_time=(2026,8,25,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=(0o100644&0xffff)<<16;z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
ck('deterministic_rebuild_byte_identical',reb.read_bytes()==ZIP.read_bytes(),{'orig':sha(ZIP),'rebuilt':sha(reb)})
status='PASS' if all(x['status']=='PASS' for x in C) else 'FAIL';obj={'schema':'L24H_V101122_PRIMARY_FINAL_REOPEN_AUDIT_V1','version':VER,'stage':STAGE,'status':status,'zip_sha256':sha(ZIP),'html_sha256':sha(EXT/'index.html'),'checks_pass':sum(x['status']=='PASS' for x in C),'checks_total':len(C),'checks_fail':sum(x['status']=='FAIL' for x in C),'checks':C};(OUT/'PRIMARY_FINAL_REOPEN_AUDIT_v101122.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');(OUT/'PRIMARY_FINAL_REOPEN_AUDIT_v101122.md').write_text(f'# Primary final reopened-ZIP audit — {VER}\n\n**Status: {status}**\n\n'+'\n'.join(f'- `{x["check"]}` — **{x["status"]}** — `{str(x["detail"])[:800]}`' for x in C)+'\n');print(json.dumps({'status':status,'checks':f"{obj['checks_pass']}/{obj['checks_total']}",'zip_sha256':sha(ZIP)}));raise SystemExit(0 if status=='PASS' else 2)
