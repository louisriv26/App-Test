#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,json,csv,tempfile,hashlib
HTML=Path(sys.argv[1]); SCANNER=Path(sys.argv[2]); FROZEN=Path(sys.argv[3]); POS=Path(sys.argv[4]); OUT=Path(sys.argv[5]);OUT.parent.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rs=[]
def add(n,ok,d=None):rs.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
with tempfile.TemporaryDirectory() as td:
 cur=Path(td)/'M1_04_RUNTIME_BOUNDARY_UNIVERSE.csv'
 q=subprocess.run([sys.executable,str(SCANNER),str(HTML),str(cur)],capture_output=True,text=True)
 add('scanner_exit_zero',q.returncode==0,{'stdout':q.stdout[-2000:],'stderr':q.stderr[-2000:]})
 summ=json.loads(cur.with_name(cur.stem+'_SUMMARY.json').read_text()) if cur.with_name(cur.stem+'_SUMMARY.json').exists() else {}
 add('raw_markers_1858',summ.get('raw_dom_markers')==1858,summ)
 add('effective_boundaries_1748',summ.get('effective_runtime_boundaries')==1748,summ)
 add('excluded_markers_110',summ.get('excluded_markers')==110,summ)
 add('excluded_nonblock_105',summ.get('excluded_reasons',{}).get('NON_BLOCK_MARKER')==105,summ)
 add('excluded_wrapper_only_5',summ.get('excluded_reasons',{}).get('NO_VISIBLE_CONTENT_AFTER_LOCAL_BOUNDARY')==5,summ)
 exp={'speech_presentation_break':80,'display_segment':122,'ldc_cross_record':1467,'ldc_intra_break':78,'speech_cross_record':1}
 add('effective_family_decomposition_exact',summ.get('effective_families')==exp,summ.get('effective_families'))
 add('page_errors_zero',not summ.get('page_errors'),summ.get('page_errors'))
 # Byte-exact package-local reproducibility of corrected R2 artifact.
 add('effective_csv_byte_exact_package_authority',cur.read_bytes()==FROZEN.read_bytes(),{'current_sha':sha(cur),'frozen_sha':sha(FROZEN)})
 # All 82 positive loci must be present in effective universe.
 with cur.open(encoding='utf-8-sig',newline='') as f: eff={(r['record_id'],int(r['source_offset'])) for r in csv.DictReader(f) if r['record_id'] and r['source_offset'] not in ('',None)}
 with POS.open(encoding='utf-8-sig',newline='') as f: pos=[(r['record_id'],int(r['source_offset'])) for r in csv.DictReader(f)]
 missing=[x for x in pos if x not in eff]
 add('positive_82_all_contained',len(pos)==82 and not missing,{'positive':len(pos),'missing':missing[:10]})
 # Required named reconciliation artifacts package-local.
 root=HTML.parent
 required=['evidence/v101134/reconciliation/M1_04_RUNTIME_BOUNDARY_UNIVERSE.csv','evidence/v101134/reconciliation/M1_04_RUNTIME_BOUNDARY_UNIVERSE_RAW_MARKERS.csv','evidence/v101134/reconciliation/M1_04_RUNTIME_BOUNDARY_UNIVERSE_EXCLUSIONS.csv','evidence/v101134/reconciliation/M1_04_RUNTIME_BOUNDARY_UNIVERSE_SUMMARY.json','evidence/v101134/reconciliation/M3_02_ALIGNMENT_POSITIVE_82_RESULTS.csv','evidence/v101134/reconciliation/M3_06_HIGHLIGHT_NOTE_REGRESSION.json','evidence/v101134/reconciliation/M3_07_ACCESSIBILITY_STRUCTURE.json','evidence/v101134/reconciliation/M3_08_INHERITED_GATE_SUMMARY.json','evidence/v101134/reconciliation/M3_09_RUNTIME_FIXED_POINT_REPORT.md','evidence/v101134/reconciliation/V101133_BOUNDARY_UNIVERSE_EVIDENCE_RECONCILIATION.md']
 add('required_reconciliation_artifacts_present',all((root/x).is_file() for x in required),[x for x in required if not (root/x).is_file()])
 ti=json.loads((root/'metadata/current_tooling_inventory.json').read_text()); gm=json.loads((root/'metadata/current_gate_map.json').read_text())
 add('scanner_explicitly_in_tool_inventory','scripts/reconstruct_runtime_boundary_universe.py' in ti.get('current_tools',[]))
 add('boundary_gate_explicitly_in_tool_inventory','scripts/run_v101134_boundary_reproducibility.py' in ti.get('current_tools',[]))
 scripts=[g.get('script') for g in gm.get('gate_families',[])]
 add('boundary_gate_mapped','scripts/run_v101134_boundary_reproducibility.py' in scripts)
 add('accessibility_gate_mapped','scripts/run_v101134_accessibility_structure.py' in scripts)
sm={'pass':sum(x['status']=='PASS' for x in rs),'fail':sum(x['status']=='FAIL' for x in rs),'total':len(rs)}
OUT.write_text(json.dumps({'schema':'L24H_V101134_BOUNDARY_REPRODUCIBILITY_V1','version':'v101.134','summary':sm,'rows':rs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
