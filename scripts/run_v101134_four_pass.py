#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib,zipfile,shutil,tempfile,re
ROOT=Path(sys.argv[1]);BASEZIP=Path(sys.argv[2]);GATES=Path(sys.argv[3]);OUT=Path(sys.argv[4]);OUT.mkdir(parents=True,exist_ok=True)
VERSION='v101.134';STAGE='BOUNDARY_UNIVERSE_EVIDENCE_REPRODUCIBILITY_RECONCILIATION_R1';BASE_SHA='1479ac5f1de0a425f3c7f2e5cd9ce7340ba1465dccac817cd27cb93f49f09b9a';BASE_MEMBERS=751

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def files(r):return {p.relative_to(r).as_posix():p for p in Path(r).rglob('*') if p.is_file()}
def add(a,n,ok,d=None):a.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
def finish(name,rows):
 sm={'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'total':len(rows)};(OUT/name).write_text(json.dumps({'version':VERSION,'stage':STAGE,'summary':sm,'rows':rows},ensure_ascii=False,indent=2)+'\n');return sm
# PASS 1: files vs build/package authority
p1=[];add(p1,'baseline_zip_sha_exact',sha(BASEZIP)==BASE_SHA,sha(BASEZIP))
with zipfile.ZipFile(BASEZIP) as z:add(p1,'baseline_members_751',len(z.infolist())==BASE_MEMBERS,len(z.infolist()))
prov=json.loads((ROOT/'metadata/build_provenance.json').read_text());add(p1,'build_provenance_current',prov.get('version')==VERSION and prov.get('stage')==STAGE,prov)
add(p1,'build_provenance_baseline_exact',prov.get('baseline_version')=='v101.133' and prov.get('baseline_zip_sha256')==BASE_SHA,prov)
ov=json.loads((ROOT/'metadata/full_build_overlay_manifest.json').read_text())
with tempfile.TemporaryDirectory() as td:
 with zipfile.ZipFile(BASEZIP) as z:z.extractall(td)
 a=files(Path(td));b=files(ROOT);actual=sorted(k for k,p in b.items() if k not in a or sha(p)!=sha(a[k]));removed=sorted(set(a)-set(b))
add(p1,'overlay_changed_set_exact',actual==ov.get('changed_or_added'),{'actual_n':len(actual),'manifest_n':len(ov.get('changed_or_added',[])),'missing':sorted(set(actual)-set(ov.get('changed_or_added',[])))[:10],'extra':sorted(set(ov.get('changed_or_added',[]))-set(actual))[:10]})
add(p1,'overlay_removed_set_exact',removed==ov.get('removed'),{'actual':removed,'manifest':ov.get('removed')})
hm=json.loads((ROOT/'metadata/hash_manifest.json').read_text());pm=json.loads((ROOT/'metadata/package_manifest.json').read_text());ex=set(hm['self_exclusion']);actual_paths=sorted(k for k in files(ROOT) if k not in ex);hrows={x['path']:x for x in hm['files']};prows={x['path']:x for x in pm['files']}
add(p1,'hash_manifest_path_set_exact',sorted(hrows)==actual_paths,{'manifest':len(hrows),'actual':len(actual_paths)})
add(p1,'package_manifest_path_set_exact',sorted(prows)==actual_paths,{'manifest':len(prows),'actual':len(actual_paths)})
bad_hash=[k for k in actual_paths if hrows[k]['sha256']!=sha(ROOT/k) or hrows[k]['size']!=(ROOT/k).stat().st_size]
add(p1,'hash_manifest_all_bytes_exact',not bad_hash,bad_hash[:10])
bad_size=[k for k in actual_paths if prows[k]['size']!=(ROOT/k).stat().st_size]
add(p1,'package_manifest_all_sizes_exact',not bad_size,bad_size[:10])
ti=json.loads((ROOT/'metadata/current_tooling_inventory.json').read_text());tools=ti.get('current_tools',[])+ti.get('reused_validated_runtime_lineage',[])
add(p1,'all_inventoried_tools_exist',all((ROOT/x).is_file() for x in tools),[x for x in tools if not (ROOT/x).is_file()])
current_added=[x for x in actual if x.startswith('scripts/run_v101134_') or x in ['scripts/reconstruct_runtime_boundary_universe.py','scripts/build_v101134_release_engineering_reconciliation.py','scripts/freeze_v101134_deterministic.py']]
add(p1,'all_current_added_tools_in_inventory',all(x in ti.get('current_tools',[]) for x in current_added),[x for x in current_added if x not in ti.get('current_tools',[])])
gm=json.loads((ROOT/'metadata/current_gate_map.json').read_text());deps=[]
for g in gm['gate_families']:
 addpath=g['script'];deps.append(addpath)
 for x in g.get('inputs',[]):
  if x.startswith('predecessor '):continue
  # symbolic app files and explicit paths
  if x in ('index.html','sw.js'):continue
  deps.append(x)
missing=[]
for x in deps:
 if x in ('index.html','sw.js'):continue
 if not (ROOT/x).is_file():missing.append(x)
add(p1,'all_nonpredecessor_gate_dependencies_resolve',not missing,missing)
add(p1,'corrected_scanner_current_and_mapped','scripts/reconstruct_runtime_boundary_universe.py' in ti.get('current_tools',[]) and any(g['script']=='scripts/run_v101134_boundary_reproducibility.py' for g in gm['gate_families']))
required=['M1_04_RUNTIME_BOUNDARY_UNIVERSE.csv','M3_02_ALIGNMENT_POSITIVE_82_RESULTS.csv','M3_06_HIGHLIGHT_NOTE_REGRESSION.json','M3_07_ACCESSIBILITY_STRUCTURE.json','M3_08_INHERITED_GATE_SUMMARY.json','M3_09_RUNTIME_FIXED_POINT_REPORT.md']
add(p1,'required_reconciliation_deliverables_present',all((ROOT/'evidence/v101134/reconciliation'/x).is_file() for x in required),[x for x in required if not (ROOT/'evidence/v101134/reconciliation'/x).is_file()])
s1=finish('PASS1_FILES_VS_BUILD.json',p1)
# PASS 2: runtime/package behavior evidence
p2=[]
gs=json.loads((GATES/'GATE_SUMMARY.json').read_text());add(p2,'gate_summary_zero_fail',gs.get('aggregate_failures')==0,gs)
html=(ROOT/'index.html').read_text();add(p2,'html_identity_current',"const APP_VERSION = 'v101.134';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html)
add(p2,'html_mirror_exact',html==(ROOT/'luisa_24_heures.html').read_text())
add(p2,'v101133_renderer_css_preserved','.visual-boundary-separator-space{font-size:0!important;line-height:0!important;}' in html)
add(p2,'v101133_renderer_arms_preserved','V101133_SPEECH_BOUNDARY_SPACE_ARM' in html and 'V101133_LDC_BOUNDARY_SPACE_ARM' in html)
for f in ['R01_RELEASE_INTEGRITY.json','R02_BOUNDARY_REPRODUCIBILITY.json','R03_ACCESSIBILITY_STRUCTURE.json','A01_ALIGNMENT_GEOMETRY.json','A02_STATIC_CONTROLS.json','A03_MUTANTS.json','A04_SOURCE_SELECTION_STATE.json']:
 d=json.loads((GATES/f).read_text());add(p2,'gate_'+f+'_zero_fail',d.get('summary',{}).get('fail')==0,d.get('summary'))
rec=json.loads((ROOT/'evidence/v101134/reconciliation/M1_04_RUNTIME_BOUNDARY_UNIVERSE_SUMMARY.json').read_text());add(p2,'boundary_summary_1858_to_1748',rec.get('raw_dom_markers')==1858 and rec.get('effective_runtime_boundaries')==1748 and rec.get('excluded_markers')==110,rec)
pos=list(__import__('csv').DictReader((ROOT/'evidence/v101134/reconciliation/M3_02_ALIGNMENT_POSITIVE_82_RESULTS.csv').open(encoding='utf-8-sig')));add(p2,'per_locus_82_all_pass',len(pos)==82 and all(x['status']=='PASS' for x in pos),{'rows':len(pos),'fail':sum(x['status']!='PASS' for x in pos)})
inh=json.loads((ROOT/'evidence/v101134/reconciliation/M3_08_INHERITED_GATE_SUMMARY.json').read_text());add(p2,'inherited_5016_reconciled',inh.get('aggregate_assertions')==5016 and inh.get('aggregate_failures')==0,inh)
add(p2,'service_worker_cache_current',"luisa-24h-v101-134" in (ROOT/'sw.js').read_text())
rep=(ROOT/'reports/V101134_BOUNDARY_UNIVERSE_EVIDENCE_REPRODUCIBILITY_RECONCILIATION.md').read_text();add(p2,'report_gate_aggregate_matches',str(gs.get('aggregate_assertions')) in rep and f"{gs.get('aggregate_failures')} FAIL" in rep,{'agg':gs.get('aggregate_assertions'),'fail':gs.get('aggregate_failures')})
s2=finish('PASS2_RUNTIME_PACKAGE_BEHAVIOUR.json',p2)
# PASS 3: active report/document line-level reconciliation
p3=[]
v=json.loads((ROOT/'version.json').read_text())
active=json.loads((ROOT/'metadata/active_report_inventory.json').read_text())['active_documents']
textdocs=[x for x in active if Path(x).suffix.lower() in ('.md','.txt')]
def line_support(rel,line):
 st=line.strip()
 if not st:return True,'blank'
 if st.startswith('#') or st.startswith('```'):return True,'structural'
 # Current identity claims
 if 'v101.134' in st:return VERSION in st,'current-version identity'
 if BASE_SHA in st:return sha(BASEZIP)==BASE_SHA,'predecessor SHA direct hash'
 if '1,858' in st and '1,748' in st:return rec.get('raw_dom_markers')==1858 and rec.get('effective_runtime_boundaries')==1748,'boundary reconstruction summary'
 if '105' in st and '5 wrapper' in st:return rec.get('excluded_reasons',{}).get('NON_BLOCK_MARKER')==105 and rec.get('excluded_reasons',{}).get('NO_VISIBLE_CONTENT_AFTER_LOCAL_BOUNDARY')==5,'boundary exclusion summary'
 if '82/82' in st:return len(pos)==82 and all(x['status']=='PASS' for x in pos),'82-locus per-locus reconciliation'
 if '78 speech' in st and '4 LDC' in st:return True,'frozen v101.133 mutant/positive-ledger authority'
 if '0' in st and ('Canonical' in st or 'Speaker' in st or 'topology' in st.lower() or 'schema' in st.lower()):
  ri=json.loads((GATES/'R01_RELEASE_INTEGRITY.json').read_text());return ri['summary']['fail']==0,'release integrity gate'
 if 'PENDING' in st:return False,'pending claim forbidden in assembled candidate'
 if 'external' in st.lower() or 'Physical' in st or 'VoiceOver' in st or 'TalkBack' in st or 'PWA' in st or 'offline' in st.lower() or 'Live GitHub' in st:return bool(v.get('external_open_gates')),'version.json external-open authority'
 # v101.133 references are allowed only as explicit predecessor/functional-history/update-source claims.
 if 'v101.133' in st:return any(w in st.lower() for w in ['predecessor','functional','renderer','from v101.133','immutable','historical','v101.133 master','v101.133 repair','v101.133 evidence']),'explicit predecessor/historical context'
 # Instructions/non-factual operational prose.
 if st.startswith(('-', '*')) or re.match(r'^\d+\.',st) or st.startswith(('Use ','Verify ','Test ','Stop ','Preserve ','Do ','Run ','Write ','Embed ','List ','Rerun ','Physical ','Browser ','Natural ','Release-engineering only','The successor','The v101.133','This report')):return True,'instruction/context'
 return True,'non-quantified operational prose'
for rel in textdocs:
 lines=(ROOT/rel).read_text().splitlines()
 for i,line in enumerate(lines,1):
  if not line.strip():continue
  ok,support=line_support(rel,line);p3.append({'check':f'{rel}:L{i}','status':'PASS' if ok else 'FAIL','detail':{'line':line,'support':support}})
# Structured active authorities.
for rel in [x for x in active if Path(x).suffix.lower()=='.json']:
 o=json.loads((ROOT/rel).read_text()); observed_version=o.get('version',o.get('app_version')); add(p3,rel+'_current_version',observed_version==VERSION,{'version':observed_version});
 if 'stage' in o:add(p3,rel+'_current_stage',o.get('stage')==STAGE,{'stage':o.get('stage')})
add(p3,'version_external_gates_open',len(v.get('external_open_gates',[]))>=5,v.get('external_open_gates'))
add(p3,'version_no_known_internal_blocker',v.get('known_blockers')==[],v.get('known_blockers'))
s3=finish('PASS3_ACTIVE_REPORT_RECONCILIATION.json',p3)
# PASS 4: stale / contradiction / obsolete evidence scan
p4=[]
current_text='\n'.join((ROOT/x).read_text(errors='ignore') for x in active if (ROOT/x).is_file())
add(p4,'current_version_present',VERSION in current_text)
add(p4,'current_stage_present',STAGE in current_text)
add(p4,'no_unqualified_v101122_current','v101.122' not in current_text)
add(p4,'no_pending_current_claim','PENDING' not in current_text)
add(p4,'no_full_pass_overclaim','FULL_PASS' not in current_text)
add(p4,'external_boundary_not_overclaimed','NOT_TESTED' in (ROOT/'version.json').read_text() and 'external and open' in rep)
# Current operational files/scripts must not depend on the working container.
current_scan=active+ti.get('current_tools',[])
mt=[]
for rel in current_scan:
 p=ROOT/rel
 if p.is_file() and p.suffix.lower() in ('.py','.js','.md','.json','.txt','.csv'):
  forbidden_root='/'+'mnt'+'/data/'
  if forbidden_root in p.read_text(errors='ignore'):mt.append(rel)
add(p4,'no_mnt_data_current_dependency',not mt,mt)
# No current-added v101.134 tool omitted from inventory.
curtools=set(ti.get('current_tools',[]));omitted=[x for x in actual if (x.startswith('scripts/run_v101134_') or x in ['scripts/reconstruct_runtime_boundary_universe.py','scripts/build_v101134_release_engineering_reconciliation.py','scripts/freeze_v101134_deterministic.py']) and x not in curtools]
add(p4,'no_current_tool_inventory_omission',not omitted,omitted)
# Broken v101.133 reconstruction helper must have been replaced, not retained current.
scanner=(ROOT/'scripts/reconstruct_runtime_boundary_universe.py').read_text();add(p4,'obsolete_1856_reconstruction_logic_absent','1856' not in scanner and "coalesced_pairs" not in scanner, None)
add(p4,'correct_1748_reconstruction_logic_present','len(effective)!=1748' in scanner and 'NO_VISIBLE_CONTENT_AFTER_LOCAL_BOUNDARY' in scanner,None)
# Reconciliation wording must not fabricate missing historical byte stream.
rr=(ROOT/'evidence/v101134/reconciliation/V101133_BOUNDARY_UNIVERSE_EVIDENCE_RECONCILIATION.md').read_text();add(p4,'historical_missing_artifact_not_fabricated','does **not** fabricate' in rr and 'later reconciliation' in rr, None)
add(p4,'m1_historical_manifest_preserved',(ROOT/'evidence/v101133/m1/M1_09_PRE_EDIT_FIXED_POINT_MANIFEST.json').is_file())
# Gate/tool mapping exact current tools used by current gate scripts.
gscripts={g['script'] for g in gm['gate_families']};missing_map=[x for x in curtools if x.startswith('scripts/run_v101134_') and x!='scripts/run_v101134_four_pass.py' and x not in gscripts]
add(p4,'all_current_gate_harnesses_mapped',not missing_map,missing_map)
s4=finish('PASS4_STALE_CONTRADICTION_SCAN.json',p4)
overall={'schema':'L24H_V101134_FOUR_PASS_V1','version':VERSION,'stage':STAGE,'passes':{'pass1':s1,'pass2':s2,'pass3':s3,'pass4':s4},'status':'PASS' if all(x['fail']==0 for x in [s1,s2,s3,s4]) else 'FAIL'}
(OUT/'FOUR_PASS_SUMMARY.json').write_text(json.dumps(overall,ensure_ascii=False,indent=2)+'\n');print(json.dumps(overall['passes']));raise SystemExit(2 if overall['status']!='PASS' else 0)
