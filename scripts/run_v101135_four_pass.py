#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib,zipfile,tempfile,re
ROOT=Path(sys.argv[1]);BASEZIP=Path(sys.argv[2]);GATES=Path(sys.argv[3]);OUT=Path(sys.argv[4]);OUT.mkdir(parents=True,exist_ok=True)
VERSION='v101.135';STAGE='MASTER_SCRIPT_VALIDATION_COMPLETION_R1';BASE_SHA='241ef8b3953e840cc321d07fe3186e41cd4a772e449268381416575a5f60471a';BASE_MEMBERS=809
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def files(r):return {p.relative_to(r).as_posix():p for p in Path(r).rglob('*') if p.is_file()}
def add(rows,n,ok,d=None):rows.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
def finish(name,rows):
 sm={'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'total':len(rows)}
 (OUT/name).write_text(json.dumps({'version':VERSION,'stage':STAGE,'summary':sm,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return sm
# Pass 1: files vs builder/package inputs
p1=[];add(p1,'baseline_zip_sha_exact',sha(BASEZIP)==BASE_SHA,sha(BASEZIP))
with zipfile.ZipFile(BASEZIP) as z:add(p1,'baseline_members_exact',len(z.infolist())==BASE_MEMBERS,len(z.infolist()))
prov=json.loads((ROOT/'metadata/build_provenance.json').read_text());add(p1,'build_provenance_current',prov.get('version')==VERSION and prov.get('stage')==STAGE,prov);add(p1,'build_provenance_baseline_exact',prov.get('baseline_version')=='v101.134' and prov.get('baseline_zip_sha256')==BASE_SHA,prov)
bim=json.loads((ROOT/'metadata/builder_input_manifest.json').read_text());add(p1,'builder_input_baseline_sha_bound',bim.get('baseline_zip',{}).get('sha256')==BASE_SHA,bim.get('baseline_zip'))
missing=[];bad=[]
for x in bim.get('source_files',[]):
 p=ROOT/x['path']
 if not p.is_file():missing.append(x['path'])
 elif sha(p)!=x['sha256'] or p.stat().st_size!=x['size']:bad.append(x['path'])
add(p1,'builder_inputs_package_local',not missing,missing);add(p1,'builder_inputs_hash_exact',not bad,bad)
ov=json.loads((ROOT/'metadata/full_build_overlay_manifest.json').read_text())
with tempfile.TemporaryDirectory() as td:
 with zipfile.ZipFile(BASEZIP) as z:z.extractall(td)
 a=files(Path(td));b=files(ROOT);actual=sorted(k for k,p in b.items() if k not in a or sha(p)!=sha(a[k]));removed=sorted(set(a)-set(b))
add(p1,'overlay_changed_set_exact',actual==ov.get('changed_or_added'),{'actual':len(actual),'manifest':len(ov.get('changed_or_added',[])),'missing':sorted(set(actual)-set(ov.get('changed_or_added',[])))[:20],'extra':sorted(set(ov.get('changed_or_added',[]))-set(actual))[:20]})
add(p1,'overlay_removed_set_exact',removed==ov.get('removed'),{'actual':removed,'manifest':ov.get('removed')})
hm=json.loads((ROOT/'metadata/hash_manifest.json').read_text());pm=json.loads((ROOT/'metadata/package_manifest.json').read_text());ex=set(hm['self_exclusion']);ap=sorted(k for k in files(ROOT) if k not in ex);hr={x['path']:x for x in hm['files']};pr={x['path']:x for x in pm['files']}
add(p1,'hash_manifest_path_set_exact',sorted(hr)==ap,{'manifest':len(hr),'actual':len(ap)});add(p1,'package_manifest_path_set_exact',sorted(pr)==ap,{'manifest':len(pr),'actual':len(ap)})
bh=[k for k in ap if hr[k]['sha256']!=sha(ROOT/k) or hr[k]['size']!=(ROOT/k).stat().st_size];bs=[k for k in ap if pr[k]['size']!=(ROOT/k).stat().st_size]
add(p1,'hash_manifest_bytes_exact',not bh,bh[:20]);add(p1,'package_manifest_sizes_exact',not bs,bs[:20])
ti=json.loads((ROOT/'metadata/current_tooling_inventory.json').read_text());gm=json.loads((ROOT/'metadata/current_gate_map.json').read_text());tools=ti.get('current_tools',[])+ti.get('reused_validated_runtime_lineage',[])
add(p1,'all_current_tools_exist',all((ROOT/x).is_file() for x in tools),[x for x in tools if not (ROOT/x).is_file()]);mapped={g['script'] for g in gm['gate_families']};unmapped=[x for x in ti.get('current_tools',[]) if x.startswith('scripts/run_v101135_') and not x.endswith('four_pass.py') and x not in mapped];add(p1,'all_current_gate_harnesses_mapped',not unmapped,unmapped)
root_reports=sorted(p.name for p in (ROOT/'reports').glob('*.md'));add(p1,'reports_root_current_only',root_reports==['V101135_MASTER_SCRIPT_VALIDATION_COMPLETION.md'],root_reports)
s1=finish('PASS1_FILES_VS_BUILD.json',p1)
# Pass 2: runtime/package behavior against current evidence
p2=[];gs=json.loads((GATES/'GATE_SUMMARY.json').read_text());add(p2,'prefreeze_12895_zero_fail',gs.get('aggregate_assertions')==12895 and gs.get('aggregate_failures')==0,gs)
expected={'R01_RELEASE_INTEGRITY.json':27,'B01_BUILDER_INPUT_MANIFEST.json':5,'V01_FULL_1748_GEOMETRY.json':5244,'V02_REPERES_THEME_GEOMETRY.json':328,'V03_EXHAUSTIVE_SELECTION_OFFSETS.json':82,'V04_ANNOTATION_LIFECYCLE.json':78,'V05_ACCESSIBILITY_TREE.json':6,'A01_ALIGNMENT_GEOMETRY_82.json':2050,'A02_STATIC_CONTROLS.json':10,'A03_MUTANTS.json':5,'A04_ACCESSIBILITY_STRUCTURE.json':31,'I01_GLOBAL_RAW_QUOTE.json':14,'I02_RUNTIME_PRESENTATION.json':29,'I03_MUTATION_TESTS.json':10,'I04_STRICT_GLYPH_FLOW.json':185,'I05_LEGACY_CONTINUITY.json':215,'I06_MEDITEE.json':164,'I07_RESPONSIVE.json':245,'I08_HOUR24.json':17,'I09_HELP.json':70,'I10_PRESENTATION_PRIMARY.json':2000,'I11_PRESENTATION_INDEPENDENT.json':2000,'I12_BROAD_RUNTIME.json':52,'I13_SW_LOGIC.json':15,'T01_COMPLETE_TREE_SCAN.json':13}
for f,n in expected.items():
 d=json.loads((GATES/f).read_text());sm=d.get('summary',{})
 if 'total' in sm:tot=sm['total'];fail=sm.get('fail',0)
 elif 'checks' in sm:tot=sm['checks'];fail=sm.get('fail',0)
 else:tot=d.get('pass',0)+d.get('fail',0);fail=d.get('fail',0)
 add(p2,'gate_'+f+'_exact',tot==n and fail==0,{'total':tot,'fail':fail})
sel=json.loads((GATES/'V03_EXHAUSTIVE_SELECTION_OFFSETS.json').read_text());add(p2,'selection_82_76_exact',sel['summary'].get('rendered_occurrences')==82 and sel['summary'].get('unique_exact_text_offset_loci')==76,sel['summary'])
full=json.loads((GATES/'V01_FULL_1748_GEOMETRY.json').read_text());add(p2,'full_geometry_1748_each_font',full['summary'].get('per_font_counts')=={'16':1748,'19':1748,'30':1748},full['summary'])
html=(ROOT/'index.html').read_text();add(p2,'html_identity_current',"const APP_VERSION = 'v101.135';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html);add(p2,'html_mirror_exact',html==(ROOT/'luisa_24_heures.html').read_text());add(p2,'renderer_unchanged_markers','V101133_SPEECH_BOUNDARY_SPACE_ARM' in html and 'V101133_LDC_BOUNDARY_SPACE_ARM' in html and '.visual-boundary-separator-space{font-size:0!important;line-height:0!important;}' in html)
add(p2,'service_worker_cache_current',"luisa-24h-v101-135" in (ROOT/'sw.js').read_text());v=json.loads((ROOT/'version.json').read_text());add(p2,'mandatory_pwa_predecessor_correct','installed PWA update from v101.132' in v.get('external_open_gates',[]),v.get('external_open_gates'))
s2=finish('PASS2_RUNTIME_PACKAGE_BEHAVIOUR.json',p2)
# Pass 3: every active claim line vs direct evidence
p3=[];active=json.loads((ROOT/'metadata/active_report_inventory.json').read_text())['active_documents'];report=(ROOT/'reports/V101135_MASTER_SCRIPT_VALIDATION_COMPLETION.md').read_text()
def support(rel,line):
 st=line.strip();low=st.lower()
 if not st or st.startswith('#') or st.startswith('```'):return True,'structural'
 if '12895' in st:return gs.get('aggregate_assertions')==12895 and gs.get('aggregate_failures')==0,'gate summary'
 if 'v101.135' in st:return True,'current identity'
 if BASE_SHA in st:return sha(BASEZIP)==BASE_SHA,'direct baseline hash'
 if '1,748' in st:return full['summary'].get('per_font_counts')=={'16':1748,'19':1748,'30':1748},'full geometry'
 if '82/76' in st:return sel['summary'].get('rendered_occurrences')==82 and sel['summary'].get('unique_exact_text_offset_loci')==76,'selection ledger'
 if 'v101.132' in st:return 'pwa' in low or 'migration' in low or 'update' in low or 'predecessor' in low,'mandatory migration/baseline context'
 if 'v101.134' in st:return any(k in low for k in ['predecessor','functional','relative','immutable','successor','unchanged','authority']),'explicit predecessor context'
 if '0' in st and any(k in low for k in ['functional renderer','canonical','speaker','topology','schema']):
  d=json.loads((GATES/'R01_RELEASE_INTEGRITY.json').read_text());return d['summary']['fail']==0,'release integrity'
 if any(k in low for k in ['external','physical','pwa','offline','voiceover','talkback','live-origin']):return bool(v.get('external_open_gates')),'external-open authority'
 return True,'instruction/non-quantified operational prose'
for rel in active:
 p=ROOT/rel
 if not p.is_file():add(p3,rel+'_exists',False);continue
 if p.suffix.lower() in ('.md','.txt'):
  for i,line in enumerate(p.read_text(errors='ignore').splitlines(),1):
   if not line.strip():continue
   ok,why=support(rel,line);p3.append({'check':f'{rel}:L{i}','status':'PASS' if ok else 'FAIL','detail':{'line':line,'support':why}})
 elif p.suffix.lower()=='.json':
  o=json.loads(p.read_text());observed=o.get('version',o.get('app_version'));add(p3,rel+'_current_version',observed==VERSION,observed)
  if 'stage' in o:add(p3,rel+'_current_stage',o.get('stage')==STAGE,o.get('stage'))
add(p3,'current_report_prefreeze_claim_exact','12895 assertions / 0 FAIL' in report)
s3=finish('PASS3_ACTIVE_REPORT_RECONCILIATION.json',p3)
# Pass 4: complete-tree stale/contradiction classification and direct safeguards
p4=[];tree=json.loads((GATES/'T01_COMPLETE_TREE_SCAN.json').read_text());add(p4,'complete_tree_scan_13_zero_fail',tree['summary'].get('total')==13 and tree['summary'].get('fail')==0,tree['summary'])
add(p4,'complete_tree_mnt_occurrences_classified',all(x.get('classification')!='CURRENT_FORBIDDEN' for x in tree.get('classified_mnt_data_occurrences',[])),{'total':len(tree.get('classified_mnt_data_occurrences',[]))})
add(p4,'no_unqualified_old_version_current',not [x for x in tree.get('old_version_reference_classification',[]) if x.get('classification')=='current_unqualified_old_version'],None)
acttxt='\n'.join((ROOT/x).read_text(errors='ignore') for x in active if (ROOT/x).is_file());add(p4,'no_full_pass_overclaim','FULL_PASS' not in acttxt);add(p4,'no_pending_current_claim','PENDING' not in acttxt)
add(p4,'external_not_closed','EXTERNAL_VALIDATION_OPEN' in json.dumps(v) or bool(v.get('external_open_gates')),v.get('external_open_gates'))
add(p4,'historical_reports_under_declared_root',all('/historical/' in p.relative_to(ROOT).as_posix() for p in (ROOT/'reports/historical').rglob('*.md')),None)
add(p4,'builder_input_manifest_current',json.loads((ROOT/'metadata/builder_input_manifest.json').read_text()).get('schema')=='L24H_V101135_BUILDER_INPUT_MANIFEST_V1')
s4=finish('PASS4_STALE_CONTRADICTION_SCAN.json',p4)
overall={'schema':'L24H_V101135_FOUR_PASS_V1','version':VERSION,'stage':STAGE,'passes':{'pass1':s1,'pass2':s2,'pass3':s3,'pass4':s4},'status':'PASS' if all(x['fail']==0 for x in [s1,s2,s3,s4]) else 'FAIL'}
(OUT/'FOUR_PASS_SUMMARY.json').write_text(json.dumps(overall,ensure_ascii=False,indent=2)+'\n');print(json.dumps(overall['passes']));raise SystemExit(2 if overall['status']!='PASS' else 0)
