#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,zipfile,shutil,sys,re,csv
BASE_SHA='5a529f8bfee3022fe03da02f42f843d40482a287fbfd61bcb3e0a1bcb8e5bf75';BASE_MEMBERS=701
VERSION='v101.133';STAGE='VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_R1';DATE='2026-09-04';CACHE='luisa-24h-v101-133'
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()
def writej(p,o):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def files(root):return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}
def patch_html(s):
 assert "const APP_VERSION = 'v101.132';" in s
 s=s.replace("const APP_VERSION = 'v101.132';",f"const APP_VERSION = '{VERSION}';",1)
 s=s.replace("const APP_EVIDENCE_STAGE = 'DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
 s=s.replace("const BUILD_DATE = '2026-09-03'; // v101.132 / deep four-pass release-engineering reconciliation; no functional or canonical text mutation",f"const BUILD_DATE = '{DATE}'; // {VERSION} / visual-boundary leading-whitespace alignment repair; no canonical text mutation",1)
 css='''.visual-boundary-separator-space{font-size:0!important;line-height:0!important;}\n'''
 anchor='.ref-para .speech-end-visual-break {\n  margin-top: 0.82em;\n}\n'
 assert anchor in s;s=s.replace(anchor,anchor+'''/* v101.133: preserve the source U+0020 at synthetic block starts while giving it zero visual advance. */\n'''+css,1)
 old='''function renderQuoteSuppressedChunk(text, from, to, suppressionRanges) {\n  let html = '', pos = from;\n  for (const r of suppressionRanges || []) {\n    if (r.end <= from || r.start >= to) continue;\n    const a = Math.max(from, r.start), b = Math.min(to, r.end);\n    if (a > pos) html += escHtml(text.slice(pos, a));\n    if (b > a) html += `<span class="speech-quote-hidden" aria-hidden="true" data-speech-quote-suppressed="${escHtml(r.reason)}">${escHtml(text.slice(a, b))}</span>`;\n    pos = Math.max(pos, b);\n  }\n  if (pos < to) html += escHtml(text.slice(pos, to));\n  return html;\n}\n'''
 new='''function renderQuoteSuppressedChunk(text, from, to, suppressionRanges, zeroLeadingBoundarySpace) {\n  let html = '', pos = from;\n  const suppressedAtStart = (suppressionRanges || []).some(r => Number(r.start) <= from && Number(r.end) > from);\n  if (zeroLeadingBoundarySpace && from < to && text[from] === ' ' && !suppressedAtStart) {\n    html += `<span class="visual-boundary-separator-space" data-visual-boundary-separator="u0020">${escHtml(text[from])}</span>`;\n    pos = from + 1;\n  }\n  for (const r of suppressionRanges || []) {\n    if (r.end <= pos || r.start >= to) continue;\n    const a = Math.max(pos, r.start), b = Math.min(to, r.end);\n    if (a > pos) html += escHtml(text.slice(pos, a));\n    if (b > a) html += `<span class="speech-quote-hidden" aria-hidden="true" data-speech-quote-suppressed="${escHtml(r.reason)}">${escHtml(text.slice(a, b))}</span>`;\n    pos = Math.max(pos, b);\n  }\n  if (pos < to) html += escHtml(text.slice(pos, to));\n  return html;\n}\n'''
 assert old in s;s=s.replace(old,new,1)
 oldfast="  if (!hls.length && !speechSegs.length && !visualBreaks.length && !quoteSuppressions.length) return escHtml(text.slice(start, end));"
 newfast="  if (!hls.length && !speechSegs.length && !visualBreaks.length && !quoteSuppressions.length && !(opts && opts.zeroLeadingBoundarySpace && text[start] === ' ')) return escHtml(text.slice(start, end));"
 assert oldfast in s;s=s.replace(oldfast,newfast,1)
 old="  const events = [];\n  let speechCls = null, hlCls = null, hlId = null;"
 new="  const events = [];\n  let speechCls = null, hlCls = null, hlId = null;\n  let zeroBoundarySpacePending = !!(opts && opts.zeroLeadingBoundarySpace);"
 assert old in s;s=s.replace(old,new,1)
 old="""    let chunk = renderQuoteSuppressedChunk(text, pos, to, quoteSuppressions);\n    if (!chunk) { pos = to; return; }"""
 new="""    const boundaryPending = zeroBoundarySpacePending;\n    const zeroLeadingBoundarySpace = boundaryPending && text[pos] === ' ';\n    let chunk = renderQuoteSuppressedChunk(text, pos, to, quoteSuppressions, zeroLeadingBoundarySpace);\n    if (boundaryPending) zeroBoundarySpacePending = false;\n    if (!chunk) { pos = to; return; }"""
 assert old in s;s=s.replace(old,new,1)
 old="""    if (ev.kind === 'speechVisualBreak') {\n      out += '<span class="speech-end-visual-break speech-presentation-visual-break" aria-hidden="true" data-presentation-boundary="true"></span>';"""
 new="""    if (ev.kind === 'speechVisualBreak') {\n      out += '<span class="speech-end-visual-break speech-presentation-visual-break" aria-hidden="true" data-presentation-boundary="true"></span>';\n      /* V101133_SPEECH_BOUNDARY_SPACE_ARM */ zeroBoundarySpacePending = true;"""
 assert old in s;s=s.replace(old,new,1)
 old='''  let out='', pos=0;\n  for (const cut of cuts) {\n    out += renderParaTextRange(text, paraId, pos, cut, { dropTrailingBreak:true });\n    const action = String((actionMap || {})[String(cut)] || (actionMap || {})[cut] || 'paragraph_break');\n    out += `<span class="ldc-visual-paragraph-break ldc-ra18-boundary ldc-ra18-${escHtml(action)}" aria-hidden="true" data-ldc-boundary-action="${escHtml(action)}"></span>`;\n    pos = cut;\n  }\n  out += renderParaTextRange(text, paraId, pos, text.length, { dropTrailingBreak:true });\n'''
 new='''  let out='', pos=0, zeroLeadingBoundarySpace=false;\n  for (const cut of cuts) {\n    out += renderParaTextRange(text, paraId, pos, cut, { dropTrailingBreak:true, zeroLeadingBoundarySpace });\n    const action = String((actionMap || {})[String(cut)] || (actionMap || {})[cut] || 'paragraph_break');\n    out += `<span class="ldc-visual-paragraph-break ldc-ra18-boundary ldc-ra18-${escHtml(action)}" aria-hidden="true" data-ldc-boundary-action="${escHtml(action)}"></span>`;\n    pos = cut;\n    /* V101133_LDC_BOUNDARY_SPACE_ARM */ zeroLeadingBoundarySpace = action !== 'preserve_break';\n  }\n  out += renderParaTextRange(text, paraId, pos, text.length, { dropTrailingBreak:true, zeroLeadingBoundarySpace });\n'''
 assert old in s;s=s.replace(old,new,1)
 return s

def build(base_zip,out,m1dir,tools,prefreeze=None,fourpass=None):
 base_zip=Path(base_zip);out=Path(out);m1dir=Path(m1dir);tools=Path(tools)
 assert sha(base_zip)==BASE_SHA
 with zipfile.ZipFile(base_zip) as z:
  assert len(z.infolist())==BASE_MEMBERS and z.testzip() is None
  shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True);z.extractall(out)
 base=(out/'index.html').read_text(encoding='utf-8');assert base==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 new=patch_html(base);(out/'index.html').write_text(new,encoding='utf-8');(out/'luisa_24_heures.html').write_text(new,encoding='utf-8')
 # release files
 v=json.loads((out/'version.json').read_text());v.update({'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,'release_scope':'Presentation-renderer-only successor of immutable v101.132. Repairs the bounded synthetic visual-boundary U+0020 horizontal-alignment defect across speech/presentation and LDC intra-record renderer paths. Canonical text, semantic speaker authorities, topology, offsets, continuity and storage/user-state schemas are unchanged.','overall_release_status':'LIMITED_PASS_STATIC__EXTERNAL_VALIDATION_OPEN','real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update from v101.132, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.133.','known_blockers':[],'external_open_gates':['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update from v101.132','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'],'postfreeze_reopen_evidence':'External SHA-bound decision/evidence; not embedded after immutable freeze.'});writej(out/'version.json',v)
 m=json.loads((out/'manifest.json').read_text());m['version']=VERSION;writej(out/'manifest.json',m)
 sw=(out/'sw.js').read_text();sw=sw.replace('/* v101.132 */','/* v101.133 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-132';",f"const CACHE_NAME = '{CACHE}';",1);(out/'sw.js').write_text(sw,encoding='utf-8')
 (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION}\n\nPresentation-renderer-only successor of immutable v101.132.\n\n- Repairs the bounded one-space horizontal misalignment at renderer-generated intra-record visual paragraph starts.\n- Production logic is rule-based; no paragraph-ID patch list is used.\n- Canonical text, semantic speaker data, presentation/topology offsets, continuity authority, stable IDs and storage schemas are unchanged.\n- The repair preserves the valid U+0020 source separator in DOM text/selection/source-offset streams while giving it zero visual advance at the synthetic block start.\n- Physical-device/PWA/offline/screen-reader/live-origin validation remains external.\n''',encoding='utf-8')
 (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(f'''# Real-device QA checklist — {VERSION}\n\nTest only the exact SHA-bound locked v101.133 package and confirm `{VERSION}` in Aide.\n\n## Alignment controls\nVerify native left-edge alignment at: Hour 8 P007, P008 and P009; Hour 5 reflection P005; one Promesses main case and its Library mirror; one linked-LDC case; `RELATED_HOUR_21.P073`; `PART_III_MARY_SORROWS.BODY.P212`.\n\n## Platforms / release gates\n- iPhone; iPad portrait; iPad landscape; Samsung/Android.\n- Installed-PWA update from v101.132 and close/reopen persistence.\n- True offline cold reopen.\n- Representative VoiceOver/TalkBack reading order and speech labels.\n- Live GitHub Pages exact-byte binding.\n\nCheck ordinary/minimum/maximum reading sizes, light/dark, and Repères where applicable. Natural wrapping is valid; a synthetic one-space left indent is not. Browser emulation is supporting evidence only.\n''',encoding='utf-8')
 (out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').write_text('device,profile,test_id,result,notes,package_sha256\n',encoding='utf-8')
 (out/'scripts/EXECUTION_SPEC.md').write_text(Path('/mnt/data/L24H_V101133_VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_MASTER_EXECUTION_SCRIPT_R1_2026-09-03.md').read_text(encoding='utf-8'),encoding='utf-8')
 # current evidence
 ev=out/'evidence/v101133';shutil.rmtree(ev,ignore_errors=True);(ev/'m1').mkdir(parents=True)
 for p in m1dir.iterdir():
  if p.is_file():shutil.copy2(p,ev/'m1'/p.name)
 if prefreeze:shutil.copytree(Path(prefreeze),ev/'prefreeze',dirs_exist_ok=True)
 if fourpass:shutil.copytree(Path(fourpass),ev/'prefreeze_four_pass',dirs_exist_ok=True)
 # tools
 for p in tools.iterdir():
  if p.is_file() and p.suffix in ('.py','.js'):shutil.copy2(p,out/'scripts'/p.name)
 current=[
 'scripts/build_v101133_alignment_repair.py','scripts/freeze_v101133_deterministic.py','scripts/run_v101133_mutation_integrity.py','scripts/run_v101133_alignment_geometry.py','scripts/run_v101133_static_controls.py','scripts/run_v101133_mutant_sensitivity.py','scripts/run_v101133_source_selection_state.py','scripts/run_v101133_four_pass.py','scripts/run_v101133_global_raw_quote_gate.py','scripts/run_v101133_runtime_presentation.py','scripts/run_v101133_mutation_tests.py','scripts/run_v101133_meditee_regression.py','scripts/run_v101133_meditee_responsive_regression.py','scripts/run_v101133_hour24_regression.py','scripts/run_v101133_help_browser_matrix.py']
 reused=['scripts/run_v101127_strict_continuity_glyph_flow_matrix.py','scripts/run_v101128_legacy_continuity_matrix.py','scripts/run_v101119_exhaustive_presentation_matrix.py','scripts/run_v101121_independent_presentation_matrix.py','scripts/run_broad_runtime_matrix.py','scripts/run_sw_logic_matrix.js']
 # copy builder under canonical name
 shutil.copy2(Path(__file__),out/'scripts/build_v101133_alignment_repair.py')
 writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'stage':STAGE,'current_tools':current,'reused_validated_runtime_lineage':reused,'rule':'Every harness used by the current v101.133 renderer-repair validation is listed; required package-local inputs are mapped by current_gate_map.json.'})
 gm=[
 {'gate':'M2-1','script':'scripts/run_v101133_mutation_integrity.py','inputs':['predecessor v101.132 index.html','index.html']},
 {'gate':'M3-1','script':'scripts/run_v101133_alignment_geometry.py','inputs':['index.html','evidence/v101133/m1/M1_05_ALIGNMENT_POSITIVE_82_LEDGER.csv']},
 {'gate':'M3-2','script':'scripts/run_v101133_static_controls.py','inputs':['index.html']},
 {'gate':'M3-3','script':'scripts/run_v101133_mutant_sensitivity.py','inputs':['index.html','evidence/v101133/m1/M1_05_ALIGNMENT_POSITIVE_82_LEDGER.csv']},
 {'gate':'M3-4','script':'scripts/run_v101133_source_selection_state.py','inputs':['index.html','evidence/v101133/m1/M1_05_ALIGNMENT_POSITIVE_82_LEDGER.csv','predecessor v101.132 index.html']},
 {'gate':'I-1','script':'scripts/run_v101133_global_raw_quote_gate.py','inputs':['index.html','evidence/v101132/authority/02_ALL_TEXT_RECORD_UNIVERSE.csv']},
 {'gate':'I-2','script':'scripts/run_v101133_runtime_presentation.py','inputs':['index.html']},
 {'gate':'I-3','script':'scripts/run_v101133_mutation_tests.py','inputs':['index.html','evidence/v101132/authority/02_ALL_TEXT_RECORD_UNIVERSE.csv']},
 {'gate':'I-4','script':'scripts/run_v101127_strict_continuity_glyph_flow_matrix.py','inputs':['index.html']},
 {'gate':'I-5','script':'scripts/run_v101128_legacy_continuity_matrix.py','inputs':['index.html']},
 {'gate':'I-6','script':'scripts/run_v101133_meditee_regression.py','inputs':['index.html']},
 {'gate':'I-7','script':'scripts/run_v101133_meditee_responsive_regression.py','inputs':['index.html']},
 {'gate':'I-8','script':'scripts/run_v101133_hour24_regression.py','inputs':['index.html']},
 {'gate':'I-9','script':'scripts/run_v101133_help_browser_matrix.py','inputs':['index.html']},
 {'gate':'I-10','script':'scripts/run_v101119_exhaustive_presentation_matrix.py','inputs':['index.html','evidence/v101131/prefreeze/V101131_PRESENTATION_LEDGER.csv']},
 {'gate':'I-11','script':'scripts/run_v101121_independent_presentation_matrix.py','inputs':['index.html','evidence/v101131/prefreeze/V101131_PRESENTATION_LEDGER.csv']},
 {'gate':'I-12','script':'scripts/run_broad_runtime_matrix.py','inputs':['index.html']},
 {'gate':'I-13','script':'scripts/run_sw_logic_matrix.js','inputs':['sw.js']},]
 writej(out/'metadata/current_gate_map.json',{'version':VERSION,'stage':STAGE,'gate_families':gm,'package_local_dependency_rule':'All non-predecessor gate inputs resolve inside this package.'})
 writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'stage':STAGE,'source_reports':['reports/V101133_VISUAL_BOUNDARY_ALIGNMENT_REPAIR.md'],'historical_reports_root':'reports/historical/','rule':'Only the listed report is current for v101.133; earlier reports are predecessor/historical lineage.'})
 writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'stage':STAGE,'current_evidence_root':'evidence/v101133','predecessor_24h':{'version':'v101.132','sha256':BASE_SHA},'m1_fixed_point':'evidence/v101133/m1','rule':'v101.132 and earlier evidence is predecessor/historical lineage; v101.133 current evidence closes only the bounded renderer alignment repair.'})
 writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'stage':STAGE,'package_local_evidence':'M1 fixed point plus candidate prefreeze/four-pass evidence may be embedded before deterministic freeze','postfreeze_reopen_and_decision':'external exact-ZIP-SHA-bound evidence written after immutable freeze','physical_device_claims':'NOT_TESTED until direct evidence','immutable_package_rule':'no postfreeze file is inserted into the frozen ZIP; any byte change requires a successor'})
 (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} Scope / Mutation Authority\n\nUser explicitly authorised only the bounded renderer repair defined by the v101.133 master execution script. No canonical text, speaker adjudication, topology/offset, continuity, schema or content-specific exception is authorised.\n\nAfter immutable freeze, mutation authority for this exact package is **NONE**.\n''',encoding='utf-8')
 # current report
 agg='PENDING';fail='PENDING'
 if prefreeze:
  sp=Path(prefreeze)/'GATE_SUMMARY.json'
  if sp.exists():
   q=json.loads(sp.read_text());agg=q.get('aggregate_assertions','PENDING');fail=q.get('aggregate_failures','PENDING')
 (out/'reports/V101133_VISUAL_BOUNDARY_ALIGNMENT_REPAIR.md').write_text(f'''# v101.133 Visual-Boundary Leading-Whitespace Alignment Repair\n\n- Immutable predecessor: `v101.132` / `{BASE_SHA}` / 701 members.\n- M1 reproduced 4,613 raw text records, 1,748 runtime synthetic boundaries, 82 visible alignment failures and 76 unique exact text+offset loci.\n- Defect mechanism: exactly one valid U+0020 immediately after a renderer-generated intra-record block boundary under `white-space: pre-wrap`.\n- Functional mutation: renderer-only zero visual advance for that single separator at the two authorised pathways; the source character remains in DOM text and source-offset/selection streams.\n- Canonical text operations: **0**. Speaker adjudication changes: **0**. Topology/offset changes: **0**. Schema changes: **0**.\n- Current prefreeze evidence: **{agg} assertions / {fail} FAIL**.\n- Physical-device/PWA/true-offline/screen-reader/live-origin validation remains external and open.\n''',encoding='utf-8')
 writej(out/'metadata/build_provenance.json',{'version':VERSION,'stage':STAGE,'build_date':DATE,'baseline_version':'v101.132','baseline_zip_sha256':BASE_SHA,'mutation_scope':'bounded presentation-renderer-only U+0020 visual-advance repair','canonical_text_changed':False,'speaker_adjudication_changed':False,'topology_offsets_changed':False,'continuity_changed':False,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'candidate_html_sha256':sha(out/'index.html')})
 # manifests; determine changed vs baseline
 tmp=out.parent/'__basecheck';shutil.rmtree(tmp,ignore_errors=True);tmp.mkdir(parents=True)
 with zipfile.ZipFile(base_zip) as z:z.extractall(tmp)
 a=files(tmp);b=files(out);changed=sorted(k for k,p in b.items() if k not in a or sha(p)!=sha(a[k]));removed=sorted(set(a)-set(b));shutil.rmtree(tmp)
 for rel in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
  if rel not in changed:changed.append(rel)
 changed.sort();writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101133_FULL_BUILD_OVERLAY_V1','version':VERSION,'stage':STAGE,'baseline_version':'v101.132','baseline_zip_sha256':BASE_SHA,'changed_or_added':changed,'removed':removed})
 exclude={'metadata/hash_manifest.json','metadata/package_manifest.json'};rows=[]
 for p in sorted(x for x in out.rglob('*') if x.is_file()):
  rel=p.relative_to(out).as_posix()
  if rel in exclude:continue
  rows.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p)})
 writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(rows),'files':[{'path':r['path'],'size':r['size']} for r in rows]})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(rows),'files':rows})
 return {'version':VERSION,'stage':STAGE,'files_total':len(files(out)),'html_sha256':sha(out/'index.html')}
if __name__=='__main__':
 if len(sys.argv)<5:raise SystemExit('usage: build BASE_ZIP OUT M1DIR TOOLS [PREFREEZE] [FOURPASS]')
 print(json.dumps(build(*sys.argv[1:]),indent=2))
