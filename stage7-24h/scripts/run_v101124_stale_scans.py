#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(sys.argv[1]); VOUT=Path(sys.argv[2]); SOUT=Path(sys.argv[3])
VER='v101.124'; STAGE='CROSS_RECORD_CONTINUITY_INLINE_FLOW_CLOSURE_R1'
# Current-facing scope only. Historical/superseded tools and reports remain provenance, not current claims.
files=[]
for p in [ROOT/'README.md',ROOT/'index.html',ROOT/'luisa_24_heures.html',ROOT/'manifest.json',ROOT/'sw.js',ROOT/'version.json']:
 if p.is_file(): files.append(p)
for base in [ROOT/'metadata',ROOT/'reports']:
 for p in base.rglob('*'):
  if p.is_file() and 'historical' not in p.parts and p.name not in {'hash_manifest.json','package_manifest.json'}: files.append(p)
for p in (ROOT/'scripts').glob('*v101124*'):
 if p.is_file() and p.name!='run_v101124_stale_scans.py': files.append(p)
# reused current generic tools are also current dependencies; scan only for transient path use, not historical version literals.
for rel in ['scripts/run_broad_runtime_matrix.py','scripts/run_sw_logic_matrix.js','scripts/run_v101119_quoted_span_fixed_point.py','scripts/run_v101119_exhaustive_presentation_matrix.py']:
 p=ROOT/rel
 if p.is_file(): files.append(p)
files=list(dict.fromkeys(files))
version_hits=[]; transient=[]
for p in files:
 s=p.read_text(encoding='utf-8',errors='ignore'); rel=p.relative_to(ROOT).as_posix()
 for m in re.finditer(r'v101\.(?:123|122|121|120|119|118)',s):
  val=m.group(0)
  # explicitly allowed lineage/baseline cases
  line=s[:m.start()].count('\n')+1
  txt=s.splitlines()[line-1] if s.splitlines() else ''
  allowed=(val=='v101.123' and (rel in {'README.md','metadata/build_provenance.json','metadata/full_build_overlay_manifest.json','metadata/current_tooling_inventory.json','reports/build_script_vs_files_audit.md','reports/current_metadata_semantic_consistency.md','reports/active_report_line_audit.csv'} or rel.startswith('scripts/build_v101124') or rel.startswith('scripts/run_v101124_independent_') or rel.startswith('scripts/run_v101124_primary_'))) or (val=='v101.119' and (rel in {'scripts/run_v101119_quoted_span_fixed_point.py','scripts/run_v101119_exhaustive_presentation_matrix.py'} or (rel in {'index.html','luisa_24_heures.html'} and 'SPEECH_PRESENTATION_ADJUDICATIONS' in txt)))
  if not allowed: version_hits.append({'path':rel,'line':line,'value':val,'text':txt[:300]})
 # transient paths in current dependencies
 for pat in [r'/mnt/data/v101124',r'/mnt/data/v101123',r'/tmp/v101124',r'v101124_work',r'v101124_continuity_audit']:
  if re.search(pat,s):
   transient.append({'path':rel,'pattern':pat})
   break
vobj={'schema':'L24H_V101124_VERSION_STALE_SCAN_V1','version':VER,'stage':STAGE,'status':'PASS' if not version_hits else 'FAIL','current_files_scanned':len(files),'unexplained_hits':version_hits}
VOUT.parent.mkdir(parents=True,exist_ok=True);VOUT.write_text(json.dumps(vobj,indent=2)+'\n')
html=(ROOT/'index.html').read_text(encoding='utf-8')
expected=["['PASSION24.HOUR.03.P012','PASSION24.HOUR.03.P013']","['PASSION24.HOUR.13.P011','PASSION24.HOUR.13.P013']","['PASSION24.HOUR.15.P014','PASSION24.HOUR.15.P015']","['PASSION24.HOUR.19.P183','PASSION24.HOUR.19.P184']","['PASSION24.HOUR.19.P185','PASSION24.HOUR.19.P186']"]
checks={
 'exact_five_groups':all(x in html for x in expected) and html[html.index('const CONTINUITY_GROUPS'):html.index('function getContinuationLeader')].count("'PASSION24.HOUR.")==10,
 'group_renderer_active':'? buildMeditationParagraphHtml(displayParagraphs, hour.hour_number)' in html,
 'inline_fragment_css':'.continuity-flow-surface .continuity-flow-fragment { display:inline!important;' in html,
 'inline_text_css':'.continuity-flow-surface .continuity-flow-fragment .para-text { display:inline!important;' in html,
 'single_space_joiner':'<span class="continuity-flow-joiner" aria-hidden="true"> </span>' in html,
 'stable_id_preserved':'id="${p.id}"' in html[html.index('function buildContinuityFragment'):html.index('function buildContinuityFlowSurface')],
 'data_para_id_preserved':'data-para-id="${p.id}"' in html[html.index('function buildContinuityFragment'):html.index('function buildContinuityFlowSurface')],
 'adjacency_fail_closed':'if (next && next.id===followerId)' in html,
 'no_transient_current_dependency':not transient,
 'current_identity':"const APP_VERSION = 'v101.124';" in html and "const APP_EVIDENCE_STAGE = 'CROSS_RECORD_CONTINUITY_INLINE_FLOW_CLOSURE_R1';" in html,
 'cache_identity':'luisa-24h-v101-124' in (ROOT/'sw.js').read_text(encoding='utf-8'),
}
sobj={'schema':'L24H_V101124_SEMANTIC_STALE_SCAN_V1','version':VER,'stage':STAGE,'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'transient_hits':transient}
SOUT.write_text(json.dumps(sobj,indent=2)+'\n')
print(json.dumps({'version_stale':vobj['status'],'semantic_stale':sobj['status'],'version_hits':len(version_hits),'transient_hits':len(transient)}))
raise SystemExit(0 if vobj['status']=='PASS' and sobj['status']=='PASS' else 2)
