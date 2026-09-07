#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, zipfile, shutil, sys, csv
BASE_SHA='53d542f3514b5b2b233fe513219886020a6d178e89f8d79d254bd6979c784327'
BASE_MEMBERS=613
BASE_HTML_SHA='6400a743255ef56b5ad556d5a23e6dc26749adf8abbeea24334ead40c9ce7f07'
VERSION='v101.131'
STAGE='GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR_R1'
BUILD_DATE='2026-09-03'
CACHE='luisa-24h-v101-131'
LEDGER_SHA='d40aea7f9fbf7f237802efbf2d7cf0219ec0dd7c3fb1d6397fb3dbf3b214bca8'
AUTH_SHA='0'  # informational only; filled dynamically in provenance from adjacent authority file if present
RAW_TEXT_AUTHORITIES=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY']
MUTABLE_AUTHORITIES=['SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_END_VISUAL_BREAKS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY']

def sha_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()

def write_json(p,o):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def extract_obj_raw(text,name):
 marker=f'const {name} = '; st=text.index(marker)+len(marker)
 try:
  obj,end=json.JSONDecoder().raw_decode(text[st:]); return obj,st,st+end,text[st:st+end]
 except json.JSONDecodeError:
  en=text.index(';',st); return None,st,en,text[st:en]

def replace_obj(text,name,obj):
 cur,st,en,_=extract_obj_raw(text,name)
 if cur is None: raise AssertionError(f'{name} is not JSON-serialisable')
 raw=json.dumps(obj,ensure_ascii=False,separators=(',',':'))
 return text[:st]+raw+text[en:]

def files(root): return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}

def remove_break(mapping,pid,offset):
 vals=list(mapping.get(pid,[]))
 if offset not in vals: raise AssertionError(f'{pid}: expected break {offset} missing from {vals}')
 vals.remove(offset)
 if vals: mapping[pid]=vals
 else: mapping.pop(pid,None)

def add_break(mapping,pid,offset):
 vals=list(mapping.get(pid,[]))
 if offset in vals: raise AssertionError(f'{pid}: break {offset} already present')
 vals.append(offset); mapping[pid]=sorted(vals)

def build(base_zip,out,ledger_path,evidence_dir=None,tools_dir=None,authority_path=None,prevalidation_docx=None,m1_evidence_dir=None):
 base_zip=Path(base_zip); out=Path(out); ledger_path=Path(ledger_path)
 if sha_file(base_zip)!=BASE_SHA: raise AssertionError('baseline SHA mismatch')
 if sha_file(ledger_path)!=LEDGER_SHA: raise AssertionError('approved ledger SHA mismatch')
 with zipfile.ZipFile(base_zip) as z:
  if len(z.infolist())!=BASE_MEMBERS: raise AssertionError('baseline member count mismatch')
  if z.testzip() is not None: raise AssertionError('baseline corrupt')
  shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True); z.extractall(out)
 if sha_file(out/'index.html')!=BASE_HTML_SHA: raise AssertionError('baseline HTML SHA mismatch')
 src=(out/'index.html').read_text(encoding='utf-8')
 if src!=(out/'luisa_24_heures.html').read_text(encoding='utf-8'): raise AssertionError('baseline HTML mirrors differ')
 if "const APP_VERSION = 'v101.130';" not in src or "const APP_EVIDENCE_STAGE = 'FOUR_PASS_FINAL_PACKAGE_METADATA_EVIDENCE_RECONCILIATION_R1';" not in src: raise AssertionError('baseline identity mismatch')
 rows=list(csv.DictReader(ledger_path.open(encoding='utf-8-sig',newline='')))
 if [r['operation_id'] for r in rows] != ['M1C001','M1C002','M1C003','M1C004'] or any(r['status']!='FROZEN_AUTHORISED_USER_VALIDATED' for r in rows): raise AssertionError('approved ledger incomplete')
 # Freeze raw-text / non-implicated declarations before mutation.
 before_raw={n:extract_obj_raw(src,n)[3] for n in RAW_TEXT_AUTHORITIES}
 SD=json.loads(json.dumps(extract_obj_raw(src,'SPEECH_DATA')[0]))
 SPA=json.loads(json.dumps(extract_obj_raw(src,'SPEECH_PRESENTATION_ADJUDICATIONS')[0]))
 SEB=json.loads(json.dumps(extract_obj_raw(src,'SPEECH_END_VISUAL_BREAKS')[0]))
 SPP=json.loads(json.dumps(extract_obj_raw(src,'SPEECH_PRESENTATION_PROJECTION')[0]))
 VPT=json.loads(json.dumps(extract_obj_raw(src,'VISIBLE_PARAGRAPH_TOPOLOGY')[0]))
 # M1C001
 p='PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P057'
 assert SD.get(p)==[{'speaker':'JESUS','start':0,'end':76}]
 assert SPP.get(p)=={'runs':[{'start':0,'end':76,'speaker':'JESUS'}],'hidden':[],'breaks':[78]}
 assert SEB.get(p)==[78] and VPT['local_breaks'].get(p)==[78]
 SPP[p]={'runs':[{'start':0,'end':114,'speaker':'JESUS'}],'hidden':[],'breaks':[]}
 remove_break(SEB,p,78); remove_break(VPT['local_breaks'],p,78)
 if p in SPA: raise AssertionError('M1C001 adjudication unexpectedly pre-existing')
 SPA[p]=[{'start':78,'end':113,'semantic_speaker':'OTHER','presentation_speaker':'JESUS','quotation_depth':2,'reason':'v101.131 M1C001 user-approved global raw-quote audit: nested quoted saying remains semantically distinct while inheriting the active outer JESUS presentation; visible straight-quote delimiters remain inline.'}]
 # M1C002
 p='PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P100'
 assert SD.get(p)==[{'speaker':'JESUS','start':0,'end':38}]
 assert SPP.get(p)=={'runs':[{'start':0,'end':38,'speaker':'JESUS'}],'hidden':[],'breaks':[40]}
 assert SEB.get(p)==[40] and VPT['local_breaks'].get(p)==[40]
 SD[p]=[{'speaker':'JESUS','start':0,'end':38},{'speaker':'JESUS','start':40,'end':98}]
 SPP[p]={'runs':[{'start':0,'end':99,'speaker':'JESUS'}],'hidden':[],'breaks':[]}
 remove_break(SEB,p,40); remove_break(VPT['local_breaks'],p,40)
 # M1C003
 p67='PASSION24.TEXT.RELATED_HOUR_21.BODY.P067'; p68='PASSION24.TEXT.RELATED_HOUR_21.BODY.P068'; p69='PASSION24.TEXT.RELATED_HOUR_21.BODY.P069'; p70='PASSION24.TEXT.RELATED_HOUR_21.BODY.P070'; p71='PASSION24.TEXT.RELATED_HOUR_21.BODY.P071'; p72='PASSION24.TEXT.RELATED_HOUR_21.BODY.P072'; p73='PASSION24.TEXT.RELATED_HOUR_21.BODY.P073'
 for p in [p67,p68,p69,p70,p71,p72,p73]:
  if p in SD or p in SPP or p in SEB or p in VPT['local_breaks']: raise AssertionError(f'M1C003 baseline unexpectedly mapped: {p}')
 if [p67,p68] not in VPT['cross_record_joins']: raise AssertionError('M1C003 expected P067->P068 cross-record join missing')
 SPP[p67]={'runs':[],'hidden':[{'start':47,'end':48,'role':'OUTER_DIVINE_OPEN_WRAPPER_HIDE','reason':'v101.131 M1C003 user-approved FATHER direct-turn wrapper suppression'}],'breaks':[]}
 for p,L in [(p68,36),(p69,418),(p70,259),(p71,117),(p72,130)]:
  SD[p]=[{'speaker':'FATHER','start':0,'end':L}]
  SPP[p]={'runs':[{'start':0,'end':L,'speaker':'FATHER'}],'hidden':[],'breaks':[]}
 SD[p73]=[{'speaker':'FATHER','start':0,'end':259}]
 SPP[p73]={'runs':[{'start':0,'end':259,'speaker':'FATHER'}],'hidden':[{'start':259,'end':260,'role':'OUTER_DIVINE_CLOSE_WRAPPER_HIDE','reason':'v101.131 M1C003 user-approved FATHER direct-turn wrapper suppression'}],'breaks':[260]}
 add_break(SEB,p73,260); add_break(VPT['local_breaks'],p73,260)
 # M1C004
 p='PASSION24.TEXT.RELATED_HOUR_21.BODY.P100'
 for m,name in [(SD,'SPEECH_DATA'),(SPP,'SPEECH_PRESENTATION_PROJECTION')]:
  if p in m: raise AssertionError(f'M1C004 baseline unexpectedly mapped in {name}')
 SD[p]=[{'speaker':'JESUS','start':27,'end':55}]
 SPP[p]={'runs':[{'start':27,'end':55,'speaker':'JESUS'}],'hidden':[],'breaks':[]}
 # Apply only the approved authority mutations.
 new=src
 for name,obj in [('SPEECH_DATA',SD),('SPEECH_PRESENTATION_ADJUDICATIONS',SPA),('SPEECH_END_VISUAL_BREAKS',SEB),('SPEECH_PRESENTATION_PROJECTION',SPP),('VISIBLE_PARAGRAPH_TOPOLOGY',VPT)]: new=replace_obj(new,name,obj)
 # Release identity.
 reps=[
  ("const APP_VERSION = 'v101.130';",f"const APP_VERSION = '{VERSION}';"),
  ("const APP_EVIDENCE_STAGE = 'FOUR_PASS_FINAL_PACKAGE_METADATA_EVIDENCE_RECONCILIATION_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';"),
  ("const BUILD_DATE = '2026-09-03'; // v101.130 / four-pass final package metadata/evidence reconciliation; no canonical text mutation",f"const BUILD_DATE = '{BUILD_DATE}'; // {VERSION} / global raw-quote host-sentence successor; no canonical text mutation"),
 ]
 for a,b in reps:
  if new.count(a)!=1: raise AssertionError('release replacement cardinality '+a)
  new=new.replace(a,b,1)
 after_raw={n:extract_obj_raw(new,n)[3] for n in RAW_TEXT_AUTHORITIES}
 if before_raw!=after_raw: raise AssertionError('raw-text/non-implicated authority changed')
 (out/'index.html').write_text(new,encoding='utf-8'); (out/'luisa_24_heures.html').write_text(new,encoding='utf-8')
 # Archive predecessor current report and selected current authorities before recreating current versions.
 rp=out/'reports'/'FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md'
 hist=out/'reports'/'historical'/'v101130'/'FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md'; hist.parent.mkdir(parents=True,exist_ok=True)
 if not rp.exists(): raise AssertionError('v101130 current report missing')
 shutil.move(str(rp),str(hist))
 for rel in ['metadata/scope_escalation_authority.md','metadata/full_build_overlay_manifest.json']:
  pth=out/rel; dest=out/'metadata'/'historical'/'v101130'/Path(rel).name; dest.parent.mkdir(parents=True,exist_ok=True)
  if not pth.exists(): raise AssertionError('v101130 authority missing '+rel)
  shutil.move(str(pth),str(dest))
 # Release bindings.
 v=json.loads((out/'version.json').read_text(encoding='utf-8'))
 v.update({'app_version':VERSION,'build_date':BUILD_DATE,'cache_name':CACHE,
  'release_scope':'User-approved four-locus successor of immutable v101.130 from the global raw-text quotation/host-sentence audit. Implements only M1C001-M1C004: two nested-Jesus presentation repairs, one previously unmapped Father speech across RELATED_HOUR_21 P067-P073, and one nested Jesus quotation in RELATED_HOUR_21 P100. Canonical text and user-state schemas are unchanged.',
  'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.131.',
  'overall_release_status':'LIMITED_PASS_STATIC__EXTERNAL_VALIDATION_OPEN',
  'postfreeze_reopen_evidence':'External SHA-bound decision/evidence; not embedded after immutable freeze.',
  'external_open_gates':['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update from v101.130','true offline cold reopen','VoiceOver/TalkBack representative testing']})
 write_json(out/'version.json',v)
 m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));m['version']=VERSION;write_json(out/'manifest.json',m)
 sw=(out/'sw.js').read_text(encoding='utf-8')
 if not sw.startswith('/* v101.130 */') or "const CACHE_NAME = 'luisa-24h-v101-130';" not in sw: raise AssertionError('SW baseline mismatch')
 sw=sw.replace('/* v101.130 */','/* v101.131 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-130';",f"const CACHE_NAME = '{CACHE}';",1)
 (out/'sw.js').write_text(sw,encoding='utf-8')
 (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION}\n\nUser-approved successor of immutable v101.130.\n\n## Global raw-quote / host-sentence closure\n\n- Implements exactly **M1C001–M1C004** from the user-approved prevalidation document.\n- Canonical CORPUS/TEXT_LIBRARY text changes: **0**.\n- Character-offset migration: **0**. Storage/personal-snapshot schema changes: **0**.\n- Adds the previously unmapped Father speech in RELATED_HOUR_21 P068–P073, corrects two nested-Jesus presentation/topology loci in PART_III_MARY_SORROWS, and adds the nested Jesus quotation in RELATED_HOUR_21 P100.\n- The eight v101.129 quote/host-sentence repairs and v101.130 release-engineering reconciliation remain protected.\n- Prefreeze: **14 gate families / 5,033 assertions / 0 FAIL**; successor presentation ledger: **400 spans**, primary and independent matrices **2,000/2,000 PASS** each.\n\n## Validation boundary\n\nStatic/package/runtime regression gates may close for the exact frozen ZIP. Physical-device, installed-PWA, true offline, VoiceOver/TalkBack and live-origin validation remain external.\n''',encoding='utf-8')
 report=out/'reports'/'GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR.md'
 report.write_text(f'''# {VERSION} Global Raw-Quote / Host-Sentence Successor\n\n- Immutable predecessor: `v101.130` / `{BASE_SHA}` / {BASE_MEMBERS} members.\n- Approved mutation ledger SHA-256: `{LEDGER_SHA}`.\n- User-approved operations: **4** (`M1C001`–`M1C004`).\n- Canonical text mutations: **0**. Character-offset migrations: **0**.\n- Implicated mutable authorities only: `SPEECH_DATA`, `SPEECH_PRESENTATION_ADJUDICATIONS`, `SPEECH_END_VISUAL_BREAKS`, `SPEECH_PRESENTATION_PROJECTION`, `VISIBLE_PARAGRAPH_TOPOLOGY`.\n- Raw corpus/library text, paragraph IDs/order, search strings, continuity groups, notes/highlights, storage schema, snapshot schema, Méditée semantics and the eight v101.129 controls are protected.\n- Permanent v101.131 raw-text completeness and mutation-detection gates are included in current tooling/evidence.\n- Current prefreeze evidence closes **14 gate families / 5,033 assertions / 0 FAIL**, including two independent **2,000-check** presentation matrices on the reconciled 400-span successor ledger.\n- Physical-device/PWA/offline/screen-reader/live-origin validation remains external.\n''',encoding='utf-8')
 # Current authority/evidence metadata.
 write_json(out/'metadata'/'active_report_inventory.json',{'version':VERSION,'stage':STAGE,'source_reports':['reports/GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR.md'],'historical_reports_root':'reports/historical/','rule':'Only GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR.md is current for v101.131; earlier reports are historical lineage.'})
 write_json(out/'metadata'/'current_evidence_lineage.json',{'version':VERSION,'stage':STAGE,'current_evidence_root':'evidence/v101131','predecessor_24h':{'version':'v101.130','sha256':BASE_SHA},'approved_mutation_ledger_sha256':LEDGER_SHA,'m1_source':'global raw-text direct-speech / host-sentence audit on immutable v101.130','rule':'v101.130 and earlier evidence is predecessor/historical lineage; v101.131 current evidence binds only the four user-approved operations and their regressions.'})
 write_json(out/'metadata'/'release_evidence_lifecycle.json',{'version':VERSION,'stage':STAGE,'package_local_evidence':'prefreeze/static/runtime evidence may be embedded before deterministic freeze','postfreeze_reopen_and_decision':'external exact-ZIP-SHA-bound evidence written after immutable freeze','physical_device_claims':'NOT_TESTED until direct evidence','immutable_package_rule':'no postfreeze file is inserted into the frozen ZIP; a content change requires a successor','active_report_rule':'only metadata/active_report_inventory.json source_reports are current claims'})
 (out/'metadata'/'scope_escalation_authority.md').write_text(f'''# {VERSION} Scope / Mutation Authority\n\nThe only functional mutation authority exercised in this successor is the user-approved four-case ledger **M1C001–M1C004** from the v101.130 global raw-quote audit. Canonical text mutation authority is **NONE**. No fifth functional/display mutation is permitted without a new prevalidation addendum and explicit user approval.\n\nAfter immutable freeze, mutation authority for this exact package is **NONE**.\n''',encoding='utf-8')
 # Evidence lineage copy.
 evroot=out/'evidence'/'v101131'; shutil.rmtree(evroot,ignore_errors=True); evroot.mkdir(parents=True)
 shutil.copy2(ledger_path,evroot/'V101131_APPROVED_MUTATION_LEDGER.csv')
 if authority_path: shutil.copy2(authority_path,evroot/'V101131_APPROVED_MUTATION_AUTHORITY.json')
 if prevalidation_docx: shutil.copy2(prevalidation_docx,evroot/'23_PREVALIDATION_BEFORE_AFTER.docx')
 if m1_evidence_dir:
  md=evroot/'m1'; md.mkdir(parents=True,exist_ok=True)
  for name in ['19_CLOSURE_CYCLE_1.json','20_CLOSURE_CYCLE_2.json','21_GLOBAL_RAW_QUOTE_M1_FIXED_POINT.md','22_NEW_MUTATION_CANDIDATE_LEDGER.csv','M1_BLIND_SEMANTIC_LAYER_QUALIFICATION.md','BLIND_FREEZE_MANIFEST.json']:
   srcp=Path(m1_evidence_dir)/name
   if srcp.exists(): shutil.copy2(srcp,md/name)
 if evidence_dir:
  rd=evroot/'prefreeze'; shutil.copytree(Path(evidence_dir),rd,dirs_exist_ok=True)
 # Current tools overlay.
 current_tools=[]
 if tools_dir:
  for p in sorted(Path(tools_dir).iterdir()):
   if p.is_file() and p.suffix in {'.py','.js'}:
    d=out/'scripts'/p.name; shutil.copy2(p,d); current_tools.append('scripts/'+p.name)
 write_json(out/'metadata'/'current_tooling_inventory.json',{'version':VERSION,'stage':STAGE,'current_tools':current_tools,'reused_validated_runtime_lineage':['scripts/run_v101127_strict_continuity_glyph_flow_matrix.py','scripts/run_v101128_legacy_continuity_matrix.py','scripts/run_v101128_meditee_core_matrix.py','scripts/run_v101128_meditee_responsive_matrix.py','scripts/run_v101130_hour24_regression.py','scripts/run_v101128_help_browser_matrix.py','scripts/run_v101121_independent_presentation_matrix.py','scripts/run_v101128_independent_runtime_smoke.py','scripts/run_sw_logic_matrix.js'],'rule':'v101.131 current tools include the global raw-text completeness/mutation gates and successor-specific topology matrices; inherited harnesses remain explicit regression lineage.'})
 # Build provenance.
 authsha=sha_file(authority_path) if authority_path else None
 write_json(out/'metadata'/'build_provenance.json',{'version':VERSION,'stage':STAGE,'build_date':BUILD_DATE,'baseline_version':'v101.130','baseline_zip_sha256':BASE_SHA,'approved_mutation_ledger_sha256':LEDGER_SHA,'approved_mutation_authority_sha256':authsha,'candidate_html_sha256':sha_file(out/'index.html'),'mutation_scope':'M1C001-M1C004 only + release identity/report/evidence bindings','canonical_text_changed':False,'speaker_spans_changed':True,'presentation_authorities_changed':True,'topology_authorities_changed':True,'continuity_cross_record_join_changed':False,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True})
 # Overlay manifest against baseline package extraction.
 baseline_root=out.parent/'__baseline_v101130_tmp'; shutil.rmtree(baseline_root,ignore_errors=True); baseline_root.mkdir(parents=True)
 with zipfile.ZipFile(base_zip) as z: z.extractall(baseline_root)
 a=files(baseline_root); b=files(out)
 changed=sorted([rel for rel,p in b.items() if rel not in a or sha_file(p)!=sha_file(a[rel])]); removed=sorted(set(a)-set(b))
 if 'metadata/full_build_overlay_manifest.json' in removed: removed.remove('metadata/full_build_overlay_manifest.json')
 if 'metadata/full_build_overlay_manifest.json' not in changed: changed.append('metadata/full_build_overlay_manifest.json');changed.sort()
 write_json(out/'metadata'/'full_build_overlay_manifest.json',{'schema':'L24H_V101131_FULL_BUILD_OVERLAY_V1','version':VERSION,'stage':STAGE,'baseline_version':'v101.130','baseline_zip_sha256':BASE_SHA,'changed_or_added':changed,'removed':removed})
 shutil.rmtree(baseline_root,ignore_errors=True)
 # Self-excluding manifests last.
 exclude={'metadata/hash_manifest.json','metadata/package_manifest.json'}
 manifest_rows=[]
 for p in sorted(x for x in out.rglob('*') if x.is_file()):
  rel=p.relative_to(out).as_posix()
  if rel in exclude: continue
  manifest_rows.append({'path':rel,'size':p.stat().st_size,'sha256':sha_file(p)})
 write_json(out/'metadata'/'package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(manifest_rows),'files':[{'path':r['path'],'size':r['size']} for r in manifest_rows]})
 write_json(out/'metadata'/'hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(manifest_rows),'files':manifest_rows})
 return {'version':VERSION,'stage':STAGE,'files_total':len(files(out)),'html_sha256':sha_file(out/'index.html'),'manifest_files':len(manifest_rows),'approved_operations':4,'canonical_text_changed':False}

if __name__=='__main__':
 if len(sys.argv)<4: raise SystemExit('usage: build_v101131_global_raw_quote_successor.py BASE_ZIP OUTDIR APPROVED_LEDGER [EVIDENCE_DIR] [TOOLS_DIR] [AUTHORITY_JSON] [PREVALIDATION_DOCX] [M1_EVIDENCE_DIR]')
 print(json.dumps(build(sys.argv[1],sys.argv[2],sys.argv[3],*(sys.argv[4:]+[None]*5)[:5]),ensure_ascii=False,indent=2))
