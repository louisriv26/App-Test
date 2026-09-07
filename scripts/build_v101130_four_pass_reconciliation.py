#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, zipfile, shutil, sys, os
BASE_SHA='8160f3133eb6d486c2109ea34911dfb13382c08d9f03883e2117cab90f01f6f0'
BASE_MEMBERS=551
VERSION='v101.130'
STAGE='FOUR_PASS_FINAL_PACKAGE_METADATA_EVIDENCE_RECONCILIATION_R1'
BUILD_DATE='2026-09-03'
CACHE='luisa-24h-v101-130'
PREV_VERSION='v101.129'
PREV_STAGE='INTRA_RECORD_QUOTE_HOST_SENTENCE_CONTINUITY_R1'
REPORT_MOVES={
 'reports/CONTINUITY_PRODUCT_CONTRACT.md':'reports/historical/v101125/CONTINUITY_PRODUCT_CONTRACT.md',
 'reports/EVIDENCE_SCHEMA_AND_BINDING_RECONCILIATION.md':'reports/historical/v101125/EVIDENCE_SCHEMA_AND_BINDING_RECONCILIATION.md',
 'reports/active_report_line_audit.csv':'reports/historical/v101125/active_report_line_audit.csv',
 'reports/build_script_vs_files_audit.md':'reports/historical/v101125/build_script_vs_files_audit.md',
 'reports/current_metadata_semantic_consistency.md':'reports/historical/v101125/current_metadata_semantic_consistency.md',
 'reports/four_pass_deep_audit.md':'reports/historical/v101125/four_pass_deep_audit.md',
 'reports/full_regression_matrix.csv':'reports/historical/v101125/full_regression_matrix.csv',
 'reports/protected_declaration_parity.csv':'reports/historical/v101125/protected_declaration_parity.csv',
 'reports/report_claims_vs_evidence_audit.md':'reports/historical/v101125/report_claims_vs_evidence_audit.md',
 'reports/semantic_stale_scan.txt':'reports/historical/v101125/semantic_stale_scan.txt',
 'reports/stale_reference_scan.txt':'reports/historical/v101125/stale_reference_scan.txt',
 'reports/DUAL_SUCCESSOR_MUTATION_REPORT.md':'reports/historical/v101126/DUAL_SUCCESSOR_MUTATION_REPORT.md',
 'reports/CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR.md':'reports/historical/v101127/CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR.md',
 'reports/MEDITEE_RECOVERY_ACCESS.md':'reports/historical/v101128/MEDITEE_RECOVERY_ACCESS.md',
 'reports/QUOTE_HOST_SENTENCE_CONTINUITY.md':'reports/historical/v101129/QUOTE_HOST_SENTENCE_CONTINUITY.md',
}
META_MOVES={
 'metadata/scope_escalation_authority.md':'metadata/historical/v101127/scope_escalation_authority.md',
 'metadata/full_build_overlay_manifest.json':'metadata/historical/v101128/full_build_overlay_manifest.json',
}
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY','SPEECH_END_VISUAL_BREAKS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY']

def sha_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def write_json(p,o): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def extract_raw(text,name):
 marker=f'const {name} = '; st=text.index(marker)+len(marker)
 try:
  obj,end=json.JSONDecoder().raw_decode(text[st:]); return text[st:st+end]
 except json.JSONDecodeError:
  en=text.index(';',st); return text[st:en]
def files(root): return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}
def move(root,src,dst):
 s=root/src
 if not s.exists(): raise AssertionError('missing move source '+src)
 d=root/dst; d.parent.mkdir(parents=True,exist_ok=True)
 if d.exists(): raise AssertionError('move destination exists '+dst)
 shutil.move(str(s),str(d))

def build(base_zip,out,evidence_dir=None,tools_dir=None):
 base_zip=Path(base_zip); out=Path(out)
 if sha_file(base_zip)!=BASE_SHA: raise AssertionError('baseline SHA mismatch')
 with zipfile.ZipFile(base_zip) as z:
  if len(z.infolist())!=BASE_MEMBERS: raise AssertionError('baseline member count mismatch')
  if z.testzip() is not None: raise AssertionError('baseline corrupt')
  shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True); z.extractall(out)
 baseline_root=out.parent/'__baseline_extract_for_v101130'
 shutil.rmtree(baseline_root,ignore_errors=True); baseline_root.mkdir(parents=True)
 with zipfile.ZipFile(base_zip) as z:z.extractall(baseline_root)
 src=(out/'index.html').read_text(encoding='utf-8')
 if src!=(out/'luisa_24_heures.html').read_text(encoding='utf-8'): raise AssertionError('baseline HTML mirrors differ')
 if "const APP_VERSION = 'v101.129';" not in src or "const APP_EVIDENCE_STAGE = 'INTRA_RECORD_QUOTE_HOST_SENTENCE_CONTINUITY_R1';" not in src: raise AssertionError('baseline identity mismatch')
 before={n:extract_raw(src,n) for n in PROTECTED}
 new=src
 reps=[
  ("const APP_VERSION = 'v101.129';",f"const APP_VERSION = '{VERSION}';"),
  ("const APP_EVIDENCE_STAGE = 'INTRA_RECORD_QUOTE_HOST_SENTENCE_CONTINUITY_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';"),
  ("const BUILD_DATE = '2026-09-03'; // v101.129 / intra-record quote host-sentence continuity; no canonical text mutation",f"const BUILD_DATE = '{BUILD_DATE}'; // {VERSION} / four-pass final package metadata/evidence reconciliation; no canonical text mutation"),
 ]
 for a,b in reps:
  if new.count(a)!=1: raise AssertionError('release binding cardinality: '+a)
  new=new.replace(a,b,1)
 after={n:extract_raw(new,n) for n in PROTECTED}
 if before!=after: raise AssertionError('functional/protected authority changed')
 (out/'index.html').write_text(new,encoding='utf-8'); (out/'luisa_24_heures.html').write_text(new,encoding='utf-8')
 # Move obsolete current-root reports/metadata into explicit historical namespaces.
 for s,d in REPORT_MOVES.items(): move(out,s,d)
 for s,d in META_MOVES.items(): move(out,s,d)
 # Current release identity.
 v=json.loads((out/'version.json').read_text(encoding='utf-8'))
 v.update({
   'app_version':VERSION,'build_date':BUILD_DATE,'cache_name':CACHE,
   'release_scope':'Release-engineering-only successor of immutable v101.129. Repairs stale current-root report/metadata classification and final static-status semantics discovered by a fresh four-pass audit. The eight v101.129 quote/host-sentence topology corrections and all devotional/runtime authorities are unchanged.',
   'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live GitHub Pages exact-byte binding NOT_TESTED for v101.130.',
   'overall_release_status':'LIMITED_PASS_STATIC__EXTERNAL_VALIDATION_OPEN',
   'postfreeze_reopen_evidence':'External SHA-bound decision/evidence; not embedded after immutable freeze.',
   'external_open_gates':['physical iPad/iPhone/Samsung','live GitHub Pages exact-byte binding','installed PWA update from v101.129','true offline cold reopen','VoiceOver/TalkBack representative testing']})
 write_json(out/'version.json',v)
 m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));m['version']=VERSION;write_json(out/'manifest.json',m)
 sw=(out/'sw.js').read_text(encoding='utf-8')
 if not sw.startswith('/* v101.129 */') or "const CACHE_NAME = 'luisa-24h-v101-129';" not in sw: raise AssertionError('SW baseline mismatch')
 sw=sw.replace('/* v101.129 */','/* v101.130 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-129';",f"const CACHE_NAME = '{CACHE}';",1)
 (out/'sw.js').write_text(sw,encoding='utf-8')
 (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION}\n\nRelease-engineering-only reconciliation successor of immutable v101.129.\n\n## Four-pass final package reconciliation\n\n- The eight user-approved v101.129 quote/host-sentence topology corrections are preserved byte-for-byte as functional authorities.\n- No canonical devotional text, speaker span, display topology, continuity group, user-state schema or Méditée behaviour changes in v101.130.\n- Stale v101.125–v101.129 reports that remained in the current report root are moved to explicit historical namespaces.\n- Stale current metadata authorities from v101.127/v101.128 are archived and replaced with current v101.130 authorities.\n- `version.json` no longer embeds a permanently stale “pending final reopen” state; post-freeze reopen/decision evidence is external and SHA-bound by design.\n\n## Validation boundary\n\nStatic/package gates can be closed for the exact frozen ZIP. Physical-device, installed-PWA, true offline, VoiceOver/TalkBack and live-origin exact-byte validation remain external.\n''',encoding='utf-8')
 # Current report.
 rp=out/'reports'/'FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md'; rp.write_text(f'''# {VERSION} Four-pass Final Package / Metadata / Evidence Reconciliation\n\n- Predecessor: immutable `v101.129` / `{BASE_SHA}` / {BASE_MEMBERS} members.\n- Trigger: fresh adversarial four-pass audit of v101.129 found release-engineering/documentary defects while all rerun functional/runtime matrices remained PASS.\n- Functional change in v101.130: **none** beyond release identity/cache binding.\n- Canonical devotional text changes: **0**. Speaker/span/topology/continuity/user-state authority changes: **0**.\n- Repair A: stale v101.125–v101.129 root reports are reclassified under explicit `reports/historical/v.../` namespaces.\n- Repair B: stale current metadata authorities (`scope_escalation_authority`, `full_build_overlay_manifest`) are archived under explicit historical metadata namespaces and replaced with v101.130 current authorities.\n- Repair C: current release-status semantics no longer claim a permanently pending final-reopen state; post-freeze reopen/meta-audit/decision evidence is external and exact-ZIP-SHA-bound.\n- The eight user-validated v101.129 quote/host-sentence topology operations remain unchanged and protected.\n- Physical-device/PWA/offline/screen-reader/live-origin validation remains external.\n''',encoding='utf-8')
 # Current metadata.
 write_json(out/'metadata'/'active_report_inventory.json',{
   'version':VERSION,'stage':STAGE,'source_reports':['reports/FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md'],
   'historical_reports_root':'reports/historical/','rule':'Only FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md is current for v101.130; all earlier version reports are explicitly historical.'})
 write_json(out/'metadata'/'current_evidence_lineage.json',{
   'version':VERSION,'stage':STAGE,'current_evidence_root':'evidence/v101130',
   'predecessor_24h':{'version':'v101.129','sha256':BASE_SHA},
   'protected_functional_authority':'v101.129 runtime/topology bytes except release identity bindings',
   'rule':'v101.129 and earlier evidence is predecessor/historical lineage; v101.130 current evidence binds only the final package/report/metadata reconciliation successor.'})
 write_json(out/'metadata'/'release_evidence_lifecycle.json',{
   'version':VERSION,'stage':STAGE,
   'package_local_evidence':'prefreeze/static evidence may be embedded before deterministic freeze',
   'postfreeze_reopen_and_decision':'external exact-ZIP-SHA-bound evidence written after immutable freeze',
   'physical_device_claims':'NOT_TESTED until direct evidence',
   'immutable_package_rule':'no postfreeze file is inserted into the frozen ZIP; a content change requires a successor',
   'active_report_rule':'only metadata/active_report_inventory.json source_reports are current claims'})
 (out/'metadata'/'scope_escalation_authority.md').write_text(f'''# {VERSION} Scope / Mutation Authority\n\nCurrent package scope is release-engineering reconciliation only. The v101.129 eight-operation quote/host-sentence topology fixed point is protected and unchanged. Canonical text, speaker spans, topology data, continuity groups, notes/highlights authorities, storage schema and Méditée semantics have **no mutation authority** in v101.130. Any further functional/content change requires a separately authorised successor.\n\nAfter immutable freeze, mutation authority for this exact package is **NONE**.\n''',encoding='utf-8')
 # Current tooling/evidence overlays.
 current_tools=[]
 if tools_dir:
  for p in sorted(Path(tools_dir).glob('*.py')):
   d=out/'scripts'/p.name; d.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,d); current_tools.append('scripts/'+p.name)
 write_json(out/'metadata'/'current_tooling_inventory.json',{
   'version':VERSION,'stage':STAGE,'current_tools':current_tools,
   'reused_validated_runtime_lineage':['scripts/run_v101129_quote_host_matrices.py','scripts/run_v101129_independent_quote_host_probe.py','scripts/run_v101129_anchor_selection.py','scripts/run_v101127_strict_continuity_glyph_flow_matrix.py','scripts/run_v101128_legacy_continuity_matrix.py','scripts/run_v101128_help_browser_matrix.py','scripts/run_v101128_independent_runtime_smoke.py','scripts/run_sw_logic_matrix.js'],
   'rule':'Current tools are the v101.130 build/audit/reopen tools; inherited harnesses are explicitly reused regression lineage.'})
 if evidence_dir:
  dest=out/'evidence'/'v101130'; shutil.rmtree(dest,ignore_errors=True); shutil.copytree(Path(evidence_dir),dest)
 # Build provenance before overlay manifest; html functional hash is release-bound hash.
 write_json(out/'metadata'/'build_provenance.json',{
   'version':VERSION,'stage':STAGE,'build_date':BUILD_DATE,'baseline_version':PREV_VERSION,'baseline_zip_sha256':BASE_SHA,
   'candidate_html_sha256':sha_file(out/'index.html'),'mutation_scope':'release identity/cache + report/metadata historical reclassification only',
   'canonical_text_changed':False,'speaker_spans_changed':False,'topology_authorities_changed':False,'continuity_authorities_changed':False,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True})
 # Compute overlay paths vs baseline, then write current overlay manifest. Include its own path as changed.
 a=files(baseline_root); b=files(out)
 changed_or_added=sorted([rel for rel,p in b.items() if rel not in a or sha_file(p)!=sha_file(a[rel])])
 removed=sorted(set(a)-set(b))
 # The old overlay authority was archived, but the same current path is recreated below; it is changed, not removed.
 if 'metadata/full_build_overlay_manifest.json' in removed: removed.remove('metadata/full_build_overlay_manifest.json')
 if 'metadata/full_build_overlay_manifest.json' not in changed_or_added: changed_or_added.append('metadata/full_build_overlay_manifest.json'); changed_or_added.sort()
 write_json(out/'metadata'/'full_build_overlay_manifest.json',{
   'schema':'L24H_V101130_FULL_BUILD_OVERLAY_V1','version':VERSION,'stage':STAGE,'baseline_version':PREV_VERSION,'baseline_zip_sha256':BASE_SHA,
   'changed_or_added':changed_or_added,'removed':removed})
 # Self-excluding manifests last.
 exclude={'metadata/hash_manifest.json','metadata/package_manifest.json'}
 rows=[]
 for p in sorted(x for x in out.rglob('*') if x.is_file()):
  rel=p.relative_to(out).as_posix()
  if rel in exclude: continue
  rows.append({'path':rel,'size':p.stat().st_size,'sha256':sha_file(p)})
 write_json(out/'metadata'/'package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(rows),'files':[{'path':r['path'],'size':r['size']} for r in rows]})
 write_json(out/'metadata'/'hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(rows),'files':rows})
 shutil.rmtree(baseline_root,ignore_errors=True)
 return {'version':VERSION,'stage':STAGE,'files_total':len(files(out)),'html_sha256':sha_file(out/'index.html'),'manifest_files':len(rows),'moved_reports':len(REPORT_MOVES),'moved_metadata':len(META_MOVES),'protected_authorities_unchanged':True}

if __name__=='__main__':
 if len(sys.argv)<3: raise SystemExit('usage: build_v101130_four_pass_reconciliation.py BASE_ZIP OUTDIR [EVIDENCE_DIR] [TOOLS_DIR]')
 print(json.dumps(build(sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None,sys.argv[4] if len(sys.argv)>4 else None),ensure_ascii=False,indent=2))
