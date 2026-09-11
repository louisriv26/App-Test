#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(sys.argv[1]); VOUT=Path(sys.argv[2]); SOUT=Path(sys.argv[3])
VER='v101.125'; STAGE='FOUR_PASS_EVIDENCE_SCHEMA_AND_DIRECT_REPORT_BINDING_RECONCILIATION_R1'
# Governed current-facing scope includes current evidence. Historical roots are excluded explicitly.
files=[]
for p in [ROOT/'README.md',ROOT/'index.html',ROOT/'luisa_24_heures.html',ROOT/'manifest.json',ROOT/'sw.js',ROOT/'version.json']:
 if p.is_file(): files.append(p)
for base in [ROOT/'metadata',ROOT/'reports',ROOT/'evidence/v101125']:
 if not base.exists(): continue
 for p in base.rglob('*'):
  if p.is_file() and 'historical' not in p.parts and p.name not in {'hash_manifest.json','package_manifest.json','VERSION_STALE_SCAN.json','SEMANTIC_STALE_SCAN.json','REPORT_CLAIM_ASSERTIONS.json','active_report_line_audit.csv'}: files.append(p)
for p in (ROOT/'scripts').glob('*v101125*'):
 if p.is_file() and p.name!='run_v101125_stale_scans.py': files.append(p)
# Reused validated lineage remains current dependency but old identifiers are allowed only in these exact files.
lineage_files={
 'scripts/run_broad_runtime_matrix.py',
 'scripts/run_sw_logic_matrix.js',
 'scripts/run_v101119_quoted_span_fixed_point.py',
 'scripts/run_v101119_exhaustive_presentation_matrix.py',
}
for rel in lineage_files:
 p=ROOT/rel
 if p.is_file(): files.append(p)
files=list(dict.fromkeys(files))
version_hits=[]; transient=[]
old_pat=re.compile(r'v101\.(?:124|123|122|121|120|119|118)')
for p in files:
 s=p.read_text(encoding='utf-8',errors='ignore'); rel=p.relative_to(ROOT).as_posix(); lines=s.splitlines()
 for m in old_pat.finditer(s):
  val=m.group(0); line=s[:m.start()].count('\n')+1; txt=lines[line-1] if lines else ''
  allowed=False
  # v101.124 is the immutable baseline and audited predecessor for this narrow release-engineering successor.
  baseline_124_exact={
    'README.md','version.json','metadata/build_provenance.json','metadata/full_build_overlay_manifest.json','metadata/scope_escalation_authority.md',
    'reports/CONTINUITY_PRODUCT_CONTRACT.md','reports/EVIDENCE_SCHEMA_AND_BINDING_RECONCILIATION.md',
    'reports/build_script_vs_files_audit.md','reports/current_metadata_semantic_consistency.md','reports/four_pass_deep_audit.md',
    'evidence/v101125/FUNCTIONAL_HTML_PARITY.json','evidence/v101125/PROTECTED_DECLARATION_PARITY.json',
    'evidence/v101125/V101124_DEEP_FOUR_PASS_FINDINGS.json','evidence/v101125/FULL_PACKAGE_BUILD_REPRODUCTION.json'
  }
  if val=='v101.124' and (
      rel in baseline_124_exact
      or rel.startswith('scripts/build_v101125')
      or rel.startswith('scripts/run_v101125_independent_prefreeze')
      or rel.startswith('scripts/run_v101125_primary_reopen')
      or rel.startswith('scripts/run_v101125_independent_reopen')
     ):
   allowed=True
  # v101.119 quotation/presentation provenance is an explicitly reused fixed-point authority.
  if val=='v101.119' and (
      rel in lineage_files
      or rel=='metadata/current_evidence_lineage.json'
      or (rel in {'index.html','luisa_24_heures.html'} and 'SPEECH_PRESENTATION_ADJUDICATIONS' in txt)
      or rel.startswith('evidence/v101125/fixed/')
     ):
   allowed=True
  if not allowed: version_hits.append({'path':rel,'line':line,'value':val,'text':txt[:300]})
 for pat in [r'/mnt/data/v101125',r'/mnt/data/v101124',r'/tmp/v101125',r'v101125_work',r'v101124_work',r'v101125_run',r'v101124_run']:
  if re.search(pat,s): transient.append({'path':rel,'pattern':pat}); break
# Current evidence schema/version consistency. Old schema identifiers are allowed only for exact inherited v101.119 fixed-point lineage.
schema_hits=[]; evidence_checked=0
allowed_old_schema={
 'evidence/v101125/fixed/M1_FIXED_POINT_SUMMARY.json':'L24H_V101119_QUOTED_SPAN_FIXED_POINT_R1',
 'evidence/v101125/EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX.json':'L24H_V101119_EXHAUSTIVE_PRESENTATION_MATRIX_V1',
}
evroot=ROOT/'evidence/v101125'
if evroot.exists():
 for p in sorted(evroot.rglob('*.json')):
  rel=p.relative_to(ROOT).as_posix()
  try:d=json.loads(p.read_text(encoding='utf-8'))
  except Exception as e:
   schema_hits.append({'path':rel,'issue':'invalid_json','detail':str(e)}); continue
  evidence_checked+=1
  schema=d.get('schema'); evver=d.get('version')
  if evver is not None and evver!=VER:
   schema_hits.append({'path':rel,'issue':'version_field_mismatch','value':evver})
  if isinstance(schema,str):
   mm=re.search(r'V101(\d{3})',schema)
   if mm and mm.group(1)!='125':
    if allowed_old_schema.get(rel)!=schema:
     schema_hits.append({'path':rel,'issue':'stale_schema_identifier','value':schema})
vobj={'schema':'L24H_V101125_VERSION_STALE_SCAN_V1','version':VER,'stage':STAGE,'status':'PASS' if not version_hits and not schema_hits else 'FAIL','current_files_scanned':len(files),'current_evidence_json_checked':evidence_checked,'unexplained_hits':version_hits,'schema_hits':schema_hits}
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
 'current_identity':"const APP_VERSION = 'v101.125';" in html and "const APP_EVIDENCE_STAGE = 'FOUR_PASS_EVIDENCE_SCHEMA_AND_DIRECT_REPORT_BINDING_RECONCILIATION_R1';" in html,
 'cache_identity':'luisa-24h-v101-125' in (ROOT/'sw.js').read_text(encoding='utf-8'),
 'current_evidence_schema_consistency':not schema_hits,
}
sobj={'schema':'L24H_V101125_SEMANTIC_STALE_SCAN_V1','version':VER,'stage':STAGE,'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'transient_hits':transient,'schema_hits':schema_hits}
SOUT.write_text(json.dumps(sobj,indent=2)+'\n')
print(json.dumps({'version_stale':vobj['status'],'semantic_stale':sobj['status'],'version_hits':len(version_hits),'schema_hits':len(schema_hits),'transient_hits':len(transient)}))
raise SystemExit(0 if vobj['status']=='PASS' and sobj['status']=='PASS' else 2)
