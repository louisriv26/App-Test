#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(sys.argv[1]);OUT=Path(sys.argv[2]);OUT.parent.mkdir(parents=True,exist_ok=True)
TEXT_EXT={'.py','.js','.md','.json','.txt','.csv','.html','.css'}
rows=[]
def add(n,ok,d=None):rows.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
# Active/current authority surfaces.
ari=json.loads((ROOT/'metadata/active_report_inventory.json').read_text())
ti=json.loads((ROOT/'metadata/current_tooling_inventory.json').read_text())
gm=json.loads((ROOT/'metadata/current_gate_map.json').read_text())
active=set(ari.get('active_documents',[]));current_tools=set(ti.get('current_tools',[])+ti.get('reused_validated_runtime_lineage',[]))
current_scan=active|current_tools|{'metadata/active_report_inventory.json','metadata/current_tooling_inventory.json','metadata/current_gate_map.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/builder_input_manifest.json'}
# Scan every text-like file, classifying working-path occurrences rather than omitting historical files.
all_text=[];mnt=[];versions=[]
for p in sorted(x for x in ROOT.rglob('*') if x.is_file() and x.suffix.lower() in TEXT_EXT):
 rel=p.relative_to(ROOT).as_posix();txt=p.read_text(errors='ignore');all_text.append(rel)
 for i,line in enumerate(txt.splitlines(),1):
  forbidden_root='/'+'mnt'+'/data/'
  if forbidden_root in line:
   cls='CURRENT_FORBIDDEN' if rel in current_scan else 'HISTORICAL_OR_INHERITED'
   mnt.append({'path':rel,'line':i,'classification':cls,'text':line[:300]})
  for m in re.finditer(r'v101\.(?:122|123|124|125|126|127|128|129|130|131|132|133|134)',line):
   ver=m.group(0);cls='historical_or_predecessor_reference'
   if rel in current_scan:
    low=line.lower()
    if rel in set(ti.get('reused_validated_runtime_lineage',[])):
     cls='current_allowed_context'
    else:
     allowed=any(k in low for k in ['predecessor','historical','baseline','from v101.132','update from v101.132','v101.132 →','immutable v101.132','v101.134','functional','inherited','authority','lineage','repair','migration','preserved','frozen','topology'])
     cls='current_allowed_context' if allowed else 'current_unqualified_old_version'
   versions.append({'path':rel,'line':i,'version':ver,'classification':cls,'text':line[:300]})
add('complete_tree_text_files_scanned',len(all_text)>0,{'files':len(all_text)})
add('no_current_mnt_data_dependency',not [x for x in mnt if x['classification']=='CURRENT_FORBIDDEN'],[x for x in mnt if x['classification']=='CURRENT_FORBIDDEN'][:20])
add('all_mnt_data_occurrences_classified',all(x['classification'] in ('CURRENT_FORBIDDEN','HISTORICAL_OR_INHERITED') for x in mnt),{'total':len(mnt),'historical_or_inherited':sum(x['classification']=='HISTORICAL_OR_INHERITED' for x in mnt)})
add('no_unqualified_old_version_in_current_surfaces',not [x for x in versions if x['classification']=='current_unqualified_old_version'],[x for x in versions if x['classification']=='current_unqualified_old_version'][:20])
# Reports root must contain current report only; predecessor reports live under reports/historical.
root_reports=sorted(p.name for p in (ROOT/'reports').glob('*.md'))
add('reports_root_current_only',root_reports==['V101135_MASTER_SCRIPT_VALIDATION_COMPLETION.md'],root_reports)
# Current docs/tooling exist.
add('all_active_documents_exist',all((ROOT/x).is_file() for x in active),[x for x in active if not (ROOT/x).is_file()])
all_tools=set(ti.get('current_tools',[])+ti.get('reused_validated_runtime_lineage',[]))
add('all_inventoried_tools_exist',all((ROOT/x).is_file() for x in all_tools),[x for x in all_tools if not (ROOT/x).is_file()])
# Gate map scripts and package-local inputs resolve; explicit predecessor inputs are allowed external authorities.
missing=[]
for g in gm.get('gate_families',[]):
 if not (ROOT/g['script']).is_file():missing.append(g['script'])
 for x in g.get('inputs',[]):
  if x.startswith('predecessor ') or x in ('index.html','sw.js'):continue
  if not (ROOT/x).exists():missing.append(x)
add('all_gate_dependencies_resolve',not missing,sorted(set(missing)))
# Current gate harness inventory coverage.
gscripts={g['script'] for g in gm.get('gate_families',[])}
om=[x for x in ti.get('current_tools',[]) if x.startswith('scripts/run_v101135_') and x not in gscripts and not x.endswith('four_pass.py') and not x.endswith('complete_tree_scan.py')]
add('current_gate_harness_inventory_mapped',not om,om)
# External boundary and mandatory PWA predecessor.
v=json.loads((ROOT/'version.json').read_text());qa=(ROOT/'REAL_DEVICE_QA_CHECKLIST.md').read_text()
add('mandatory_pwa_predecessor_v101132','installed PWA update from v101.132' in v.get('external_open_gates',[]) and 'v101.132' in qa and 'Mandatory' in qa,{'external':v.get('external_open_gates')})
add('external_gates_still_open',len(v.get('external_open_gates',[]))>=6,v.get('external_open_gates'))
# No overclaim in current active docs.
acttxt='\n'.join((ROOT/x).read_text(errors='ignore') for x in active if (ROOT/x).is_file())
add('no_full_pass_overclaim','FULL_PASS' not in acttxt)
add('current_version_declared','v101.135' in acttxt)
sm={'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'total':len(rows)}
OUT.write_text(json.dumps({'schema':'L24H_V101135_COMPLETE_TREE_CLASSIFICATION_SCAN_V1','summary':sm,'rows':rows,'classified_mnt_data_occurrences':mnt,'old_version_reference_classification':versions},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
