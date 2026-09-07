#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,zipfile,shutil,sys,csv,re,os
BASE_SHA='fe6433248c94da3629110976fd190ed0263368ecf9057a437c3d6ef166517c72'
BASE_MEMBERS=486
VERSION='v101.129'; STAGE='INTRA_RECORD_QUOTE_HOST_SENTENCE_CONTINUITY_R1'; BUILD_DATE='2026-09-03'; CACHE='luisa-24h-v101-129'
LEDGER_SHA='c6bf93b6f7af4707f93628ab41dfa02acd89db112a048a8cbd54c0a81acc5341'
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY']
AUTH_MUTABLE=['SPEECH_END_VISUAL_BREAKS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY']

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def write_json(p,o): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def extract_obj_raw(text,name):
 marker=f'const {name} = '; st=text.index(marker)+len(marker)
 try:
  obj,end=json.JSONDecoder().raw_decode(text[st:]); return obj,st,st+end,text[st:st+end]
 except json.JSONDecodeError:
  en=text.index(';',st); return None,st,en,text[st:en]
def replace_obj(text,name,obj):
 cur,st,en,_=extract_obj_raw(text,name)
 if cur is None: raise AssertionError(f'{name} is not JSON-serialisable authority')
 raw=json.dumps(obj,ensure_ascii=False,separators=(',',':')); return text[:st]+raw+text[en:]
def list_files(root):return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}
def mutate_break_list(vals,old,new):
 vals=list(vals or [])
 if old not in vals: raise AssertionError(f'expected old break {old} missing from {vals}')
 vals.remove(old)
 if new is not None:
  if new in vals: raise AssertionError(f'new break {new} already present')
  vals.append(new);vals=sorted(vals)
 return vals

def build(base_zip,out,ledger_path,tools_dir=None,evidence_dir=None):
 base_zip=Path(base_zip);out=Path(out);ledger_path=Path(ledger_path)
 if sha_file(base_zip)!=BASE_SHA: raise AssertionError('baseline SHA mismatch')
 if sha_file(ledger_path)!=LEDGER_SHA: raise AssertionError('ledger SHA mismatch')
 with zipfile.ZipFile(base_zip) as z:
  if len(z.infolist())!=BASE_MEMBERS: raise AssertionError('baseline member count mismatch')
  if z.testzip() is not None: raise AssertionError('baseline corrupt')
  shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True);z.extractall(out)
 baseline=list_files(out)
 src=(out/'index.html').read_text(encoding='utf-8')
 if src!=(out/'luisa_24_heures.html').read_text(encoding='utf-8'):raise AssertionError('HTML mirrors diverged at baseline')
 if "const APP_VERSION = 'v101.128';" not in src or "const APP_EVIDENCE_STAGE = 'MEDITEE_RECOVERY_ACCESS_AND_SINGLE_STATE_SYNC_R1';" not in src:raise AssertionError('baseline app identity mismatch')
 before_protected={n:extract_obj_raw(src,n)[3] for n in PROTECTED}
 before_auth={n:extract_obj_raw(src,n)[0] for n in AUTH_MUTABLE}
 SEB=json.loads(json.dumps(before_auth['SPEECH_END_VISUAL_BREAKS']))
 SPP=json.loads(json.dumps(before_auth['SPEECH_PRESENTATION_PROJECTION']))
 VPT=json.loads(json.dumps(before_auth['VISIBLE_PARAGRAPH_TOPOLOGY']))
 rows=list(csv.DictReader(ledger_path.open(encoding='utf-8')))
 if len(rows)!=8 or any(r['status']!='FROZEN_AUTHORISED_USER_VALIDATED' for r in rows):raise AssertionError('ledger authority incomplete')
 actual_ops=[]
 for r in rows:
  pid=r['paragraph_id'];old=int(r['old_break_offset']);new=int(r['new_break_offset']) if r['new_break_offset'] else None
  # Speech-end map: remove old only; relocated host sentence break is NOT a speech-end break.
  if pid not in SEB or old not in SEB[pid]:raise AssertionError(f'{pid} old break missing speech-end map')
  SEB[pid]=[x for x in SEB[pid] if x!=old]
  if not SEB[pid]:del SEB[pid]
  # Projection and visible topology: remove old and optionally add relocated host-sentence boundary.
  SPP[pid]['breaks']=mutate_break_list(SPP[pid].get('breaks',[]),old,new)
  if pid not in VPT['local_breaks']:raise AssertionError(f'{pid} missing topology entry')
  nv=mutate_break_list(VPT['local_breaks'][pid],old,new)
  if nv:VPT['local_breaks'][pid]=nv
  else:del VPT['local_breaks'][pid]
  actual_ops.append({'operation_id':r['operation_id'],'paragraph_id':pid,'old':old,'new':new})
 new=src
 new=replace_obj(new,'SPEECH_END_VISUAL_BREAKS',SEB)
 new=replace_obj(new,'SPEECH_PRESENTATION_PROJECTION',SPP)
 new=replace_obj(new,'VISIBLE_PARAGRAPH_TOPOLOGY',VPT)
 # release identity only
 reps=[
  ("const APP_VERSION = 'v101.128';",f"const APP_VERSION = '{VERSION}';"),
  ("const APP_EVIDENCE_STAGE = 'MEDITEE_RECOVERY_ACCESS_AND_SINGLE_STATE_SYNC_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';"),
  ("const BUILD_DATE = '2026-09-02'; // v101.128 / Méditée recovery access; no canonical text mutation",f"const BUILD_DATE = '{BUILD_DATE}'; // {VERSION} / intra-record quote host-sentence continuity; no canonical text mutation"),
 ]
 for old,repl in reps:
  if new.count(old)!=1:raise AssertionError('release replacement cardinality '+old)
  new=new.replace(old,repl,1)
 after_protected={n:extract_obj_raw(new,n)[3] for n in PROTECTED}
 if before_protected!=after_protected:raise AssertionError('protected declaration changed')
 (out/'index.html').write_text(new,encoding='utf-8');(out/'luisa_24_heures.html').write_text(new,encoding='utf-8')
 # release bindings
 v=json.loads((out/'version.json').read_text(encoding='utf-8'))
 v.update({'app_version':VERSION,'build_date':BUILD_DATE,'cache_name':CACHE,
   'release_scope':'Presentation-topology-only successor of immutable v101.128. Reconciles eight user-validated intra-record quote/host-sentence break defects (3 relocations, 5 removals). Canonical text, speaker spans, paragraph IDs/order, search text, storage schema, personal snapshot schema and v101.128 Méditée semantics are unchanged.',
   'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live GitHub Pages exact-byte binding NOT_TESTED for v101.129.',
   'overall_release_status':'LIMITED_PASS_STATIC_PENDING_FINAL_REOPEN_AUDIT',
   'external_open_gates':['physical iPad/iPhone/Samsung','live GitHub Pages exact-byte binding','installed PWA update from v101.128','true offline cold reopen','VoiceOver/TalkBack representative testing']})
 write_json(out/'version.json',v)
 m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));m['version']=VERSION;write_json(out/'manifest.json',m)
 sw=(out/'sw.js').read_text(encoding='utf-8')
 if not sw.startswith('/* v101.128 */') or "const CACHE_NAME = 'luisa-24h-v101-128';" not in sw:raise AssertionError('SW baseline mismatch')
 sw=sw.replace('/* v101.128 */','/* v101.129 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-128';",f"const CACHE_NAME = '{CACHE}';",1)
 (out/'sw.js').write_text(sw,encoding='utf-8')
 (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION}\n\nPresentation-topology-only successor of immutable v101.128.\n\n## Intra-record quote / host-sentence continuity\n\n- Corrects eight user-validated visual-break defects: three breaks are relocated to the true end of Luisa's host sentence and five false quote-close breaks are removed.\n- Direct words of Jesus retain their speaker presentation; outer Luisa text resumes inline when the containing sentence continues.\n- Canonical text operations: **0**. Speaker-span changes: **0**. Storage/schema changes: **0**.\n- v101.127 cross-record continuity and v101.128 Méditée recovery UX remain protected regression authorities.\n\n## Validation boundary\n\nStatic/package gates may close in this build. Physical-device, installed-PWA, true offline, VoiceOver/TalkBack and live-origin exact-byte validation remain external.\n''',encoding='utf-8')
 report=out/'reports'/'QUOTE_HOST_SENTENCE_CONTINUITY.md'
 report.write_text(f'''# {VERSION} Intra-record Quote / Host-Sentence Continuity\n\n- Predecessor: immutable `v101.128` / `{BASE_SHA}` / {BASE_MEMBERS} members.\n- Frozen mutation ledger SHA-256: `{LEDGER_SHA}`.\n- User-authorised topology operations: **8** = 3 relocations + 5 removals.\n- Governing rule: a speaker-run boundary is not automatically a visible-paragraph boundary; host-sentence syntax governs paragraph topology.\n- Canonical text changes: **0**. Speaker semantic/span changes: **0**. Character-offset migrations: **0**.\n- Authorised mutable layers: `SPEECH_END_VISUAL_BREAKS`, `SPEECH_PRESENTATION_PROJECTION.breaks`, `VISIBLE_PARAGRAPH_TOPOLOGY.local_breaks`.\n- Relocated host-sentence breaks are represented in projection/topology only; they are not falsely added to `SPEECH_END_VISUAL_BREAKS`.\n- Physical-device/PWA/offline/screen-reader/live-origin validation remains external.\n''',encoding='utf-8')
 # Current metadata, leaving predecessor evidence as lineage.
 write_json(out/'metadata'/'active_report_inventory.json',{'version':VERSION,'stage':STAGE,'source_reports':['reports/QUOTE_HOST_SENTENCE_CONTINUITY.md'],'historical_reports_root':'reports/historical/','inherited_nonactive_reports':['reports/MEDITEE_RECOVERY_ACCESS.md','reports/CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR.md','reports/DUAL_SUCCESSOR_MUTATION_REPORT.md'],'rule':'Only QUOTE_HOST_SENTENCE_CONTINUITY.md is current for v101.129; v101.128 and earlier reports are predecessor/historical lineage.'})
 write_json(out/'metadata'/'current_evidence_lineage.json',{'version':VERSION,'stage':STAGE,'current_evidence_root':'evidence/v101129','predecessor_24h':{'version':'v101.128','sha256':BASE_SHA},'mutation_ledger_sha256':LEDGER_SHA,'rule':'v101.128 evidence remains predecessor lineage; v101.129 current evidence binds the quote/host-sentence topology successor.'})
 current_tools=[]
 if tools_dir:
  current_tools=['scripts/'+x.name for x in sorted(Path(tools_dir).glob('*.py'))]
 else:
  current_tools=['scripts/build_v101129_quote_host_topology.py','scripts/run_v101129_quote_host_matrices.py','scripts/run_v101129_independent_quote_host_probe.py']
 write_json(out/'metadata'/'current_tooling_inventory.json',{'version':VERSION,'stage':STAGE,'current_tools':current_tools,'reused_validated_runtime_lineage':['v101.127 strict continuity','v101.128 Méditée/Hour24/Help/runtime/SW harnesses'],'historical_or_superseded_tools':['scripts/build_v101128_meditee_recovery_access.py']})
 write_json(out/'metadata'/'release_evidence_lifecycle.json',{'version':VERSION,'stage':STAGE,'prefreeze_package_reports':'may claim only directly executed current static/runtime facts','postfreeze_final_reopen_reports':'external to immutable ZIP unless included before deterministic freeze','physical_device_claims':'NOT_TESTED until direct evidence','immutable_package_rule':'decision lock is written last after reopen/meta-audit','current_evidence_rule':'evidence/v101129 is current; older evidence is predecessor lineage','active_report_rule':'current active report claims bind directly to evidence/v101129 or current package bytes'})
 write_json(out/'metadata'/'build_provenance.json',{'version':VERSION,'stage':STAGE,'build_date':BUILD_DATE,'baseline_version':'v101.128','baseline_zip_sha256':BASE_SHA,'mutation_ledger_sha256':LEDGER_SHA,'candidate_html_sha256':sha_file(out/'index.html'),'mutation_scope':'eight user-validated presentation-topology operations + release identity/evidence bindings','canonical_text_changed':False,'speaker_spans_changed':False,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True})
 # Copy current tool scripts if supplied.
 if tools_dir:
  td=Path(tools_dir)
  for p in td.glob('*.py'):
   d=out/'scripts'/p.name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
 # Copy current evidence if supplied.
 if evidence_dir:
  ed=Path(evidence_dir);dest=out/'evidence'/'v101129';shutil.rmtree(dest,ignore_errors=True);shutil.copytree(ed,dest)
 # Regenerate self-excluding manifests after all overlays.
 exclude={'metadata/hash_manifest.json','metadata/package_manifest.json'}
 files=[]
 for p in sorted(x for x in out.rglob('*') if x.is_file()):
  rel=p.relative_to(out).as_posix()
  if rel in exclude:continue
  files.append({'path':rel,'size':p.stat().st_size,'sha256':sha_file(p)})
 write_json(out/'metadata'/'package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(files),'files':[{'path':x['path'],'size':x['size']} for x in files]})
 write_json(out/'metadata'/'hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':sorted(exclude),'file_count':len(files),'files':files})
 return {'version':VERSION,'stage':STAGE,'files_total':len(list_files(out)),'html_sha256':sha_file(out/'index.html'),'operations':actual_ops,'protected_sha256':{n:sha_bytes(before_protected[n].encode()) for n in PROTECTED}}

if __name__=='__main__':
 if len(sys.argv)<4:raise SystemExit('usage: build_v101129_quote_host_topology.py BASE_ZIP OUTDIR LEDGER [TOOLS_DIR] [EVIDENCE_DIR]')
 r=build(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else None,sys.argv[5] if len(sys.argv)>5 else None)
 print(json.dumps(r,ensure_ascii=False,indent=2))
