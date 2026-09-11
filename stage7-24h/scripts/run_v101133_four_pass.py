#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib,zipfile,re
ROOT=Path(sys.argv[1]);BASEZIP=Path(sys.argv[2]);GATES=Path(sys.argv[3]);OUT=Path(sys.argv[4]);OUT.mkdir(parents=True,exist_ok=True)
VERSION='v101.133';STAGE='VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_R1';BASE_SHA='5a529f8bfee3022fe03da02f42f843d40482a287fbfd61bcb3e0a1bcb8e5bf75'
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()
def add(rows,n,ok,d=None):rows.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
def wr(name,rows):
 sm={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
 (OUT/name).write_text(json.dumps({'version':VERSION,'stage':STAGE,'summary':sm,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return sm
# Pass1
p1=[];add(p1,'baseline_sha',sha(BASEZIP)==BASE_SHA,sha(BASEZIP));
with zipfile.ZipFile(BASEZIP) as z:add(p1,'baseline_members_701',len(z.infolist())==701,len(z.infolist()));add(p1,'baseline_zip_clean',z.testzip() is None)
for rel in ['index.html','luisa_24_heures.html','version.json','manifest.json','sw.js','metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json','metadata/current_tooling_inventory.json','metadata/current_gate_map.json','README.md','REAL_DEVICE_QA_CHECKLIST.md','scripts/EXECUTION_SPEC.md']:
 add(p1,'exists_'+rel,(ROOT/rel).is_file())
# manifests self-consistent
hm=json.loads((ROOT/'metadata/hash_manifest.json').read_text());pm=json.loads((ROOT/'metadata/package_manifest.json').read_text())
for row in hm['files']:
 p=ROOT/row['path'];
 if not p.is_file() or sha(p)!=row['sha256'] or p.stat().st_size!=row['size']: add(p1,'hash_manifest_'+row['path'],False);break
else:add(p1,'hash_manifest_all_rows_match',True,hm['file_count'])
for row in pm['files']:
 p=ROOT/row['path'];
 if not p.is_file() or p.stat().st_size!=row['size']:add(p1,'package_manifest_'+row['path'],False);break
else:add(p1,'package_manifest_all_rows_match',True,pm['file_count'])
# gate map dependencies
gm=json.loads((ROOT/'metadata/current_gate_map.json').read_text());missing=[]
for g in gm['gate_families']:
 if not (ROOT/g['script']).is_file():missing.append(g['script'])
 for x in g.get('inputs',[]):
  if x.startswith('predecessor '):continue
  if x in ('index.html','sw.js'):p=ROOT/x
  else:p=ROOT/x
  if not p.exists():missing.append(x)
add(p1,'all_gate_map_dependencies_resolve',not missing,missing[:20])
# exact overlay accounting vs baseline
with zipfile.ZipFile(BASEZIP) as z:
 base={i.filename:hashlib.sha256(z.read(i.filename)).hexdigest() for i in z.infolist()}
cur={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()}
actual=sorted(k for k,v in cur.items() if k not in base or base[k]!=v);removed=sorted(set(base)-set(cur));ov=json.loads((ROOT/'metadata/full_build_overlay_manifest.json').read_text());decl=sorted(ov['changed_or_added']);
# manifests list themselves and are regenerated after overlay, so compare the explicit set exactly
add(p1,'overlay_changed_set_exact',actual==decl,{'actual_only':sorted(set(actual)-set(decl))[:20],'declared_only':sorted(set(decl)-set(actual))[:20],'actual':len(actual),'declared':len(decl)})
add(p1,'overlay_removed_exact',removed==sorted(ov['removed']),{'actual':removed,'declared':ov['removed']})
s1=wr('PASS1_FILES_VS_BUILD.json',p1)
# Pass2
p2=[];gs=json.loads((GATES/'GATE_SUMMARY.json').read_text());add(p2,'prefreeze_gate_summary_zero_fail',gs['aggregate_failures']==0,gs);add(p2,'prefreeze_gate_assertions_7131',gs['aggregate_assertions']==7131,gs['aggregate_assertions'])
required=['M2_01_V101133_MUTATION_INTEGRITY.json','M3_01_ALIGNMENT_GEOMETRY_FULL.json','M3_03_ALIGNMENT_NEGATIVE_CONTROL_RESULTS.json','M3_04_MUTANT_SENSITIVITY.json','M3_05_TEXT_SELECTION_OFFSET_PRESERVATION.json','I01_GLOBAL_RAW_QUOTE.json','I02_RUNTIME_PRESENTATION.json','I03_MUTATION_TESTS.json','I04_STRICT_GLYPH_FLOW.json','I05_LEGACY_CONTINUITY.json','I06_MEDITEE.json','I07_RESPONSIVE.json','I08_HOUR24.json','I09_HELP.json','I10_PRESENTATION_PRIMARY.json','I11_PRESENTATION_INDEPENDENT.json','I12_BROAD_RUNTIME.json','I13_SW_LOGIC.json']
for f in required:
 q=json.loads((GATES/f).read_text()); sm=q.get('summary'); fail=sm.get('fail',0) if sm else q.get('fail',0);add(p2,'gate_'+f,fail==0,fail)
# identity/runtime static
html=(ROOT/'index.html').read_text();add(p2,'html_identity_current',"const APP_VERSION = 'v101.133';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html);add(p2,'html_mirror_exact',html==(ROOT/'luisa_24_heures.html').read_text());add(p2,'separator_rule_present','.visual-boundary-separator-space{font-size:0!important;line-height:0!important;}' in html);add(p2,'both_renderer_arms_present','V101133_SPEECH_BOUNDARY_SPACE_ARM' in html and 'V101133_LDC_BOUNDARY_SPACE_ARM' in html)
s2=wr('PASS2_RUNTIME_PACKAGE_BEHAVIOUR.json',p2)
# Pass3 active reports line claims
p3=[];inv=json.loads((ROOT/'metadata/active_report_inventory.json').read_text());add(p3,'one_active_report',inv['source_reports']==['reports/V101133_VISUAL_BOUNDARY_ALIGNMENT_REPAIR.md'],inv['source_reports']);rp=ROOT/inv['source_reports'][0];txt=rp.read_text();
claims=[('baseline_sha',BASE_SHA in txt),('baseline_members','701 members' in txt),('raw_count','4,613 raw text records' in txt),('boundary_count','1,748 runtime synthetic boundaries' in txt),('defect_count','82 visible alignment failures' in txt),('unique_count','76 unique exact text+offset loci' in txt),('zero_text_ops','Canonical text operations: **0**' in txt),('external_open','remains external and open' in txt),('prefreeze_assertions',('7,131 assertions / 0 FAIL' in txt or '7131 assertions / 0 FAIL' in txt))]
for n,o in claims:add(p3,'report_'+n,o)
# active metadata versions
for rel in ['metadata/current_tooling_inventory.json','metadata/current_gate_map.json','metadata/active_report_inventory.json','metadata/current_evidence_lineage.json','metadata/release_evidence_lifecycle.json','metadata/build_provenance.json']:
 o=json.loads((ROOT/rel).read_text());add(p3,'current_'+rel,o.get('version')==VERSION and o.get('stage')==STAGE,{'version':o.get('version'),'stage':o.get('stage')})
s3=wr('PASS3_ACTIVE_REPORT_RECONCILIATION.json',p3)
# Pass4 stale/contradiction scan
p4=[];active=['README.md','REAL_DEVICE_QA_CHECKLIST.md','scripts/EXECUTION_SPEC.md','version.json','metadata/current_tooling_inventory.json','metadata/current_gate_map.json','metadata/active_report_inventory.json','metadata/current_evidence_lineage.json','metadata/release_evidence_lifecycle.json','metadata/build_provenance.json','metadata/scope_escalation_authority.md','reports/V101133_VISUAL_BOUNDARY_ALIGNMENT_REPAIR.md']
alltxt='\n'.join((ROOT/r).read_text(encoding='utf-8') for r in active)
add(p4,'current_version_present',VERSION in alltxt);add(p4,'current_stage_present',STAGE in alltxt);add(p4,'no_stale_current_v101122','v101.122' not in (ROOT/'REAL_DEVICE_QA_CHECKLIST.md').read_text() and 'v101.122' not in (ROOT/'README.md').read_text());add(p4,'external_boundary_not_overclaimed','NOT_TESTED' in (ROOT/'version.json').read_text() and 'external and open' in (ROOT/'reports/V101133_VISUAL_BOUNDARY_ALIGNMENT_REPAIR.md').read_text());fullpass_lines=[ln.strip() for ln in alltxt.splitlines() if 'FULL_PASS' in ln];add(p4,'no_full_pass_overclaim',all(('Do **not** use `FULL_PASS`' in ln or 'do not use' in ln.lower()) for ln in fullpass_lines),fullpass_lines);add(p4,'no_temp_mnt_dependency','/mnt/data/' not in alltxt);add(p4,'tool_inventory_contains_alignment_harness','scripts/run_v101133_alignment_geometry.py' in json.loads((ROOT/'metadata/current_tooling_inventory.json').read_text())['current_tools']);add(p4,'gate_map_contains_both_presentation_harnesses',all(x in [g['script'] for g in gm['gate_families']] for x in ['scripts/run_v101119_exhaustive_presentation_matrix.py','scripts/run_v101121_independent_presentation_matrix.py']));add(p4,'real_device_checklist_targets_v101133','v101.133' in (ROOT/'REAL_DEVICE_QA_CHECKLIST.md').read_text())
s4=wr('PASS4_STALE_CONTRADICTION_SCAN.json',p4)
overall={'schema':'L24H_V101133_FOUR_PASS_V1','version':VERSION,'stage':STAGE,'passes':{'pass1':s1,'pass2':s2,'pass3':s3,'pass4':s4},'status':'PASS' if all(x['fail']==0 for x in [s1,s2,s3,s4]) else 'FAIL'}
(OUT/'FOUR_PASS_SUMMARY.json').write_text(json.dumps(overall,indent=2)+'\n');print(json.dumps(overall));raise SystemExit(2 if overall['status']=='FAIL' else 0)
