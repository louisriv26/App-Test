#!/usr/bin/env python3
from pathlib import Path
import sys,re,json
ROOT=Path(sys.argv[1]);OV=Path(sys.argv[2]);OS=Path(sys.argv[3]);VER='v101.123';STAGE='FOUR_PASS_BUILD_REPRODUCIBILITY_AND_SELF_AUDIT_RECONCILIATION_R1'
# Current-facing text only. Historical directories are intentionally excluded.
paths=[ROOT/'README.md',ROOT/'version.json',ROOT/'manifest.json',ROOT/'sw.js',ROOT/'index.html']
paths += [p for p in (ROOT/'metadata').glob('*') if p.is_file()]
paths += [p for p in (ROOT/'reports').glob('*') if p.is_file()]
paths += [p for p in (ROOT/'scripts').glob('*') if p.is_file() and ('v101123' in p.name or p.name in {'run_broad_runtime_matrix.py','run_sw_logic_matrix.js','run_v101119_quoted_span_fixed_point.py','run_v101119_exhaustive_presentation_matrix.py'})]
hits=[];un=[]
for p in paths:
 s=p.read_text(encoding='utf-8',errors='ignore')
 for i,line in enumerate(s.splitlines(),1):
  for tok in sorted(set(re.findall(r'v101\.\d+',line))):
   if tok==VER:cl='CURRENT'
   elif tok=='v101.122' and (p.name in {'README.md','version.json','build_v101123_full_package_reconciliation.py','run_v101123_independent_prefreeze_audit.py','run_v101123_stale_scans.py'} or p.name.startswith('build_provenance') or 'baseline' in line.lower() or 'v101.122' in line and any(w in line.lower() for w in ['supersed','parity','unchanged','historical','re-audit','reproduced','omitted','depended','allowed transient','functional html','byte-identical'])):cl='IMMUTABLE_BASELINE_OR_REAUDIT_REFERENCE_ALLOWED'
   elif tok=='v101.119' and (p.name.startswith('run_v101119_') or p.name=='run_v101123_stale_scans.py'):cl='REUSED_VALIDATED_LINEAGE_ALLOWED'
   elif p.name in {'index.html','sw.js'} and tok!=VER:cl='INHERITED_IMPLEMENTATION_OR_PROTECTED_PROVENANCE_ALLOWED'
   else:cl='UNEXPLAINED'
   rec={'path':p.relative_to(ROOT).as_posix(),'line':i,'token':tok,'classification':cl,'excerpt':line[:700]};hits.append(rec)
   if cl=='UNEXPLAINED':un.append(rec)
# runtime identity checks
html=(ROOT/'index.html').read_text();sw=(ROOT/'sw.js').read_text();v=json.loads((ROOT/'version.json').read_text());m=json.loads((ROOT/'manifest.json').read_text())
identity=[
 {'check':'html_app_version','status':'PASS' if "const APP_VERSION = 'v101.123';" in html else 'FAIL'},
 {'check':'html_stage','status':'PASS' if f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html else 'FAIL'},
 {'check':'sw_cache','status':'PASS' if "luisa-24h-v101-123" in sw else 'FAIL'},
 {'check':'version_json','status':'PASS' if v.get('app_version')==VER else 'FAIL'},
 {'check':'manifest_json','status':'PASS' if m.get('version')==VER else 'FAIL'}]
vo={'schema':'L24H_V101123_VERSION_STALE_SCAN_V1','version':VER,'stage':STAGE,'status':'PASS' if not un and all(x['status']=='PASS' for x in identity) else 'FAIL','classified_count':len(hits),'unexplained_count':len(un),'runtime_identity_checks':identity,'hits':hits,'unexplained':un}
OV.parent.mkdir(parents=True,exist_ok=True);OV.write_text(json.dumps(vo,ensure_ascii=False,indent=2)+'\n')
# semantic/current-tool assumptions
checks=[]
def ck(n,o,d=''):checks.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
dependency_paths=[ROOT/'metadata/build_provenance.json',ROOT/'metadata/current_tooling_inventory.json',ROOT/'scripts/build_v101123_full_package_reconciliation.py',ROOT/'scripts/run_v101123_independent_prefreeze_audit.py',ROOT/'scripts/run_v101123_primary_reopen_audit.py',ROOT/'scripts/run_v101123_independent_reopen_audit.py']
dependency_text='\n'.join(p.read_text(encoding='utf-8',errors='ignore') for p in dependency_paths if p.exists())
# No transient prior working-tree/run assumptions in current executable/provenance dependencies.
trans=[x for x in ['/mnt/data/v101122_run/','/mnt/data/v101123_run/','/mnt/data/v101122_deep4/','/mnt/data/v101123_work/'] if x in dependency_text]
ck('no_transient_working_paths',not trans,trans)
# Builder must explicitly assert full-tree reproduction, not six runtime files only.
b=(ROOT/'scripts/build_v101123_full_package_reconciliation.py').read_text();ck('full_package_builder_contract','PASS_FULL_PACKAGE_REPRODUCTION' in b and 'FAIL_FULL_TREE_REPRODUCTION' in b and 'metadata/full_build_overlay_manifest.json' in b)
ip=(ROOT/'scripts/run_v101123_independent_prefreeze_audit.py').read_text();ck('prefreeze_self_contained',"Path('/mnt/data" not in ip and 'run_v101123_independent_hour24_probe.py' in ip and "td/'ih.json'" in ip)
# Active report inventory exact root current files except self-excluded line audit.
inv=json.loads((ROOT/'metadata/active_report_inventory.json').read_text());decl=set(inv['source_reports']);act=set(p.relative_to(ROOT).as_posix() for p in (ROOT/'reports').glob('*') if p.is_file() and p.name!='active_report_line_audit.csv');ck('active_report_universe_complete',decl==act,{'missing':sorted(act-decl),'extra':sorted(decl-act)})
# Product semantics remain correct.
ck('hour24_completion_authority','if (!p.complete)' in html and 'requireComplete && !p.complete' in html and 'Recommencer depuis la 1re Heure' in html)
ck('hours_1_23_no_cycle_controls','showProgressView()' not in html[html.index('function buildHourEndActions('):html.index('function buildHour24CyclePanel(')])
# Current reports must not claim v101.122 is current PASS.
root_reports='\n'.join(p.read_text(encoding='utf-8',errors='ignore') for p in (ROOT/'reports').glob('*') if p.is_file());ck('no_v101122_current_pass_claim',not re.search(r'(CURRENT(?:\s+CONTINUATION|\s+AUTHORITY|\s+VERSION)[^\n]{0,80}v101\.122|v101\.122[^\n]{0,80}(?:IS CURRENT|PASS_PREFREEZE_CURRENT|FINAL STATUS\s*[:=]\s*PASS))',root_reports,re.I))
so={'schema':'L24H_V101123_SEMANTIC_STALE_SCAN_V1','version':VER,'stage':STAGE,'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','obsolete_current_tool_assumptions':sum(x['status']=='FAIL' for x in checks),'unexplained_count':sum(x['status']=='FAIL' for x in checks),'checks':checks}
OS.write_text(json.dumps(so,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version_status':vo['status'],'version_unexplained':len(un),'semantic_status':so['status'],'semantic_fail':so['unexplained_count']}));raise SystemExit(0 if vo['status']=='PASS' and so['status']=='PASS' else 2)
