#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib,csv,re
C=Path(sys.argv[1]); P=Path(sys.argv[2]); G=Path(sys.argv[3]); OUT=Path(sys.argv[4]);OUT.mkdir(parents=True,exist_ok=True)
VERSION='v101.132';STAGE='DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION_R1'
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()
def add(rows,c,ok,d=None):rows.append({'case':c,'status':'PASS' if ok else 'FAIL','detail':d})
def sm(rows):return {'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'total':len(rows)}
def wj(name,o):(OUT/name).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Pass 1
r1=[];v=json.loads((C/'version.json').read_text());add(r1,'version_stage_current',v.get('app_version')==VERSION and json.loads((C/'metadata/active_report_inventory.json').read_text()).get('stage')==STAGE,[v.get('app_version'),json.loads((C/'metadata/active_report_inventory.json').read_text()).get('stage')])
add(r1,'html_mirror_identical',(C/'index.html').read_bytes()==(C/'luisa_24_heures.html').read_bytes())
add(r1,'execution_spec_current',VERSION in (C/'scripts/EXECUTION_SPEC.md').read_text() and STAGE in (C/'scripts/EXECUTION_SPEC.md').read_text() and 'v101.122' not in (C/'scripts/EXECUTION_SPEC.md').read_text())
add(r1,'real_device_checklist_current',VERSION in (C/'REAL_DEVICE_QA_CHECKLIST.md').read_text() and 'v101.122' not in (C/'REAL_DEVICE_QA_CHECKLIST.md').read_text())
frozen=C/'evidence/v101132/authority/02_ALL_TEXT_RECORD_UNIVERSE.csv'; bm=json.loads((C/'evidence/v101132/authority/BLIND_FREEZE_MANIFEST.json').read_text());add(r1,'frozen_raw_authority_embedded_and_hash_bound',frozen.exists() and sha(frozen)==bm['files']['02_ALL_TEXT_RECORD_UNIVERSE.csv'],sha(frozen) if frozen.exists() else None)
inv=json.loads((C/'metadata/current_tooling_inventory.json').read_text());gm=json.loads((C/'metadata/current_gate_map.json').read_text());listed=set(inv['current_tools']+inv['reused_validated_runtime_lineage']);scripts=[x['script'] for x in gm['gate_families']];add(r1,'all_14_gate_scripts_in_inventory',len(scripts)==14 and all(x in listed for x in scripts),[x for x in scripts if x not in listed])
add(r1,'all_inventoried_tools_resolve',all((C/x).is_file() for x in listed),[x for x in listed if not (C/x).is_file()])
# package-local inputs
missing=[]
for g in gm['gate_families']:
 for x in g['inputs']:
  if x.startswith('predecessor '):continue
  if x in ['index.html','sw.js']:q=C/x
  elif x.startswith('evidence/'):q=C/x
  else:continue
  if not q.exists():missing.append(x)
add(r1,'all_package_local_gate_inputs_resolve',not missing,missing)
hm=json.loads((C/'metadata/hash_manifest.json').read_text());pm=json.loads((C/'metadata/package_manifest.json').read_text());exc=set(hm['self_exclusion']);actual={p.relative_to(C).as_posix():sha(p) for p in C.rglob('*') if p.is_file() and p.relative_to(C).as_posix() not in exc};listedh={x['path']:x['sha256'] for x in hm['files']};add(r1,'hash_manifest_universe_exact',set(actual)==set(listedh),[len(actual),len(listedh)]);add(r1,'hash_manifest_bytes_exact',all(listedh[k]==h for k,h in actual.items()),None);add(r1,'package_manifest_count_exact',pm.get('file_count')==len(actual),[pm.get('file_count'),len(actual)])
# overlay exact vs predecessor root
pa={p.relative_to(P).as_posix():sha(p) for p in P.rglob('*') if p.is_file()};ca={p.relative_to(C).as_posix():sha(p) for p in C.rglob('*') if p.is_file()};chg=sorted(k for k in ca if k not in pa or ca[k]!=pa[k]);rem=sorted(set(pa)-set(ca));ov=json.loads((C/'metadata/full_build_overlay_manifest.json').read_text());add(r1,'full_overlay_changed_exact',chg==ov['changed_or_added'],{'missing':sorted(set(chg)-set(ov['changed_or_added'])),'extra':sorted(set(ov['changed_or_added'])-set(chg))});add(r1,'full_overlay_removed_exact',rem==ov['removed'],[rem,ov['removed']])
# Pass2 gate evidence
r2=[];gate_files=sorted(G.glob('[0-9][0-9]_*.json'));summ=[]
for f in gate_files:
 o=json.loads(f.read_text());s=o.get('summary') or {'pass':o.get('pass'),'fail':o.get('fail'),'total':len(o.get('rows',[]))};summ.append((f.name,s));add(r2,'gate_'+f.stem,s.get('fail')==0,s)
add(r2,'14_gate_files_exact',len(gate_files)==14,[f.name for f in gate_files]);agg=sum(s.get('total',s.get('pass',0)+s.get('fail',0)) for _,s in summ);fail=sum(s.get('fail',0) for _,s in summ);add(r2,'aggregate_zero_fail',fail==0,{'assertions':agg,'failures':fail})
# Pass3 active report
r3=[];ari=json.loads((C/'metadata/active_report_inventory.json').read_text());add(r3,'single_active_report',ari.get('source_reports')==['reports/DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION.md'],ari.get('source_reports'))
rep=(C/ari['source_reports'][0]).read_text().splitlines();
for i,line in enumerate(rep,1):
 if not line.strip():continue
 ok=True;ev='direct current package/evidence'
 if i==1:ok=VERSION in line
 elif 'Immutable predecessor' in line:ok='v101.131' in line and '2932131da56ed1c02efb1507b5529f4cbb51bfa370691944cf0bd6c34fb01fa2' in line
 elif 'Functional/display/canonical mutations' in line:ok='**0**' in line
 elif 'five release-engineering defects' in line:ok=all(x in line for x in ['incomplete full-overlay','stale v101.122 execution','stale v101.122 real-device','missing frozen raw-text','incomplete current tooling'])
 elif 'All five defects are corrected' in line:ok=sm(r1)['fail']==0
 elif '02_ALL_TEXT_RECORD_UNIVERSE.csv' in line:ok=frozen.exists() and sha(frozen)==bm['files']['02_ALL_TEXT_RECORD_UNIVERSE.csv']
 elif 'current_gate_map.json' in line:ok=len(gm['gate_families'])==14 and all(x in listed for x in scripts)
 elif 'Current prefreeze gate evidence' in line:ok=str(agg) in line and '0 FAIL' in line
 elif 'Physical-device' in line:ok='external and open' in line
 add(r3,f'report_line_{i}',ok,line)
# Pass4
r4=[];active_text='\n'.join([(C/'README.md').read_text(),(C/'REAL_DEVICE_QA_CHECKLIST.md').read_text(),(C/'scripts/EXECUTION_SPEC.md').read_text(),(C/'reports/DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION.md').read_text(),(C/'metadata/current_tooling_inventory.json').read_text(),(C/'metadata/current_gate_map.json').read_text()])
add(r4,'no_stale_v101122_active_bindings','v101.122' not in active_text.replace('stale v101.122',''),None)
add(r4,'runtime_identity_current',"const APP_VERSION = 'v101.132';" in (C/'index.html').read_text() and "const APP_EVIDENCE_STAGE = 'DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION_R1';" in (C/'index.html').read_text())
add(r4,'sw_cache_current',"luisa-24h-v101-132" in (C/'sw.js').read_text() and "luisa-24h-v101-131" not in (C/'sw.js').read_text())
add(r4,'root_current_report_universe_exact',sorted(p.name for p in (C/'reports').glob('*.md'))==['DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION.md'],sorted(p.name for p in (C/'reports').glob('*.md')))
add(r4,'gate_count_number_current',len(gate_files)==14,len(gate_files));add(r4,'assertion_number_current',fail==0,{'assertions':agg,'failures':fail})
add(r4,'tooling_inventory_no_missing_actual_harnesses',all(x in listed for x in ['scripts/run_broad_runtime_matrix.py','scripts/run_v101119_exhaustive_presentation_matrix.py']),None)
add(r4,'frozen_dependency_no_missing',frozen.exists(),None)
add(r4,'external_open_gates_exact',len(v.get('external_open_gates',[]))==5,v.get('external_open_gates'))
# write
for n,rows in [('01_PASS1_FILES_VS_BUILD',r1),('02_PASS2_RUNTIME_PACKAGE',r2),('03_PASS3_ACTIVE_REPORT',r3),('04_PASS4_STALE_CONTRADICTION',r4)]:wj(n+'.json',{'version':VERSION,'stage':STAGE,'summary':sm(rows),'rows':rows})
allpass=all(sm(x)['fail']==0 for x in [r1,r2,r3,r4]);(OUT/'05_FOUR_PASS.md').write_text('# v101.132 Deep Four-Pass\n\n'+''.join(f"- {n}: {sm(r)['pass']}/{sm(r)['total']} PASS; {sm(r)['fail']} FAIL\n" for n,r in [('Pass 1',r1),('Pass 2',r2),('Pass 3',r3),('Pass 4',r4)])+f"\n**OVERALL: {'PASS' if allpass else 'FAIL'}**\n",encoding='utf-8')
print(json.dumps({'pass1':sm(r1),'pass2':sm(r2),'pass3':sm(r3),'pass4':sm(r4),'aggregate_assertions':agg,'overall':'PASS' if allpass else 'FAIL'},indent=2));raise SystemExit(0 if allpass else 2)
