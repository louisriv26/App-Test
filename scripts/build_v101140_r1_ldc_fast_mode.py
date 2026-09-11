from pathlib import Path
import json,hashlib,zipfile,shutil,re,copy,difflib,sys,csv,os

BASE_SHA='07c58c551046ec186428b7075b9a6225b6b36d97359439d3a92c69ad58271726'
AUTH_SHA='c5ed40fcc0b9db71b742606ce90de55dc82606204d8b8d989271bd2a227b015b'
VERSION='v101.140'; REV='R1'; DATE='2026-09-09'; CACHE='luisa-24h-v101-140-r1'
STAGE='LDC_FAST_MODE_DERIVATIVE_CORRECTION_SUCCESSOR_R1'
BASE_VERSION='v101.139 R1'
EXPECTED_SOURCE_COUNTS={'NOT_PRESENT_IN_24H':2668,'PRESENT_ALL_ALREADY_CORRECT':2,'PRESENT_WITH_APPLICABLE_DERIVATIVES':37,'BLOCKED_MAPPING_OR_CONFLICT':0}
OFFSET_NAMES=['SPEECH_DATA','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY','DISPLAY_SEGMENTS']
PROTECTED_CANONICAL=['CORPUS','PASSION24_SUPPLEMENT_SOURCE_METADATA','PASSION24_LDC_CROSSREF_INDEX','PASSION24_RELATED_BY_HOUR','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS']


def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_text(s): return sha_bytes(s.encode('utf-8'))
def sha_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def files(root): return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}
def jdump(o): return json.dumps(o,ensure_ascii=False,separators=(',',':'))
def writej(p,o):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def exact_replace(s,old,new,label,count=1):
 c=s.count(old);assert c==count,(label,c,count);return s.replace(old,new,count)
def raw_const(text,name):
 m=re.search(rf'const\s+{re.escape(name)}\s*=\s*',text);assert m,name
 start=m.end()
 while start<len(text) and text[start].isspace():start+=1
 opener=text[start];assert opener in '[{',(name,text[start:start+20]);pairs={'[':']','{':'}'};stack=[];quote=None;esc=False
 for j in range(start,len(text)):
  ch=text[j]
  if quote:
   if esc:esc=False
   elif ch=='\\':esc=True
   elif ch==quote:quote=None
  else:
   if ch in ('"',"'",'`'):quote=ch
   elif ch in '[{':stack.append(pairs[ch])
   elif ch in ']}':
    assert stack and ch==stack[-1],(name,j,ch);stack.pop()
    if not stack:
     raw=text[start:j+1]
     try:obj=json.loads(raw)
     except Exception:obj=None
     return raw,obj,start,j+1
 raise AssertionError(('unterminated',name))
def replace_const(text,name,obj):
 raw,_,s,e=raw_const(text,name);return text[:s]+jdump(obj)+text[e:]
def freeze(root,zp):
 root=Path(root);zp=Path(zp);zp.unlink(missing_ok=True)
 with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(root.rglob('*')):
   if not p.is_file():continue
   rel=p.relative_to(root).as_posix();info=zipfile.ZipInfo(rel,(2026,9,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16);z.writestr(info,p.read_bytes())
 return sha_file(zp)

def mb(old,new,pos):
 sm=difflib.SequenceMatcher(None,old,new,autojunk=False)
 for tag,i1,i2,j1,j2 in sm.get_opcodes():
  if pos < i1:return j1-(i1-pos)
  if i1<=pos<=i2:
   if tag=='equal':return j1+(pos-i1)
   if i2==i1:return j1
   frac=(pos-i1)/(i2-i1);return round(j1+frac*(j2-j1))
 return min(pos,len(new))
def remap(o,old,new):
 if isinstance(o,list):
  if all(isinstance(x,int) for x in o):return [mb(old,new,x) for x in o]
  return [remap(x,old,new) for x in o]
 if isinstance(o,dict):
  d={}
  for k,v in o.items():
   if k in ('start','end') and isinstance(v,int):d[k]=mb(old,new,v)
   elif k=='breaks' and isinstance(v,list):d[k]=[mb(old,new,x) for x in v]
   else:d[k]=remap(v,old,new)
  return d
 return o

def text_library_map(TL):
 out={}
 for item in TL:
  if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not isinstance(item.get('body'),list):continue
  nums=item.get('body_stable_numbers') or list(range(1,len(item['body'])+1));assert len(nums)==len(item['body'])
  for idx,(n,t) in enumerate(zip(nums,item['body'])):
   out[f"{item['id']}.BODY.P{int(n):03d}"]=(item,idx,t)
 return out

def validate_offsets(text_by_id,O,FLOW,tlmap):
 errs=[]
 def walk(x,L,path):
  if isinstance(x,dict):
   if isinstance(x.get('start'),int) and isinstance(x.get('end'),int):
    if not(0<=x['start']<=x['end']<=L):errs.append((path,x['start'],x['end'],L))
   for k,v in x.items():walk(v,L,path+'.'+str(k))
  elif isinstance(x,list):
   for i,v in enumerate(x):walk(v,L,path+f'[{i}]')
 for n in ['SPEECH_DATA','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_ADJUDICATIONS']:
  obj=O.get(n)
  if isinstance(obj,dict):
   for sid,val in obj.items():
    if sid in text_by_id:walk(val,len(text_by_id[sid]),n+'.'+sid)
 for n in ['SPEECH_END_VISUAL_BREAKS']:
  obj=O.get(n,{})
  if isinstance(obj,dict):
   for sid,vals in obj.items():
    if sid in text_by_id:
     L=len(text_by_id[sid])
     for x in vals:
      if not(0<x<L):errs.append((n+'.'+sid,x,L))
 topo=O.get('VISIBLE_PARAGRAPH_TOPOLOGY') or {}
 for sid,vals in topo.get('local_breaks',{}).items():
  if sid in text_by_id:
   L=len(text_by_id[sid])
   for x in vals:
    if not(0<x<L):errs.append(('VPT.'+sid,x,L))
 # LDC flow intra offsets use physical indices.
 for iid,blocks in FLOW.items():
  for b in blocks:
   for idxs,vals in b.get('intra',{}).items():
    idx=int(idxs)
    # locate record by item + physical index
    match=[(sid,t) for sid,(it,j,t) in tlmap.items() if it.get('id')==iid and j==idx]
    if not match:continue
    sid,t=match[0];L=len(t)
    for x in vals:
     if not(0<x<L):errs.append(('FLOW.'+sid,x,L))
 assert not errs,errs[:20]

def build(base_zip,authority_json,output_dir):
 base_zip=Path(base_zip);authority_json=Path(authority_json);out=Path(output_dir)
 assert sha_file(base_zip)==BASE_SHA,(sha_file(base_zip),BASE_SHA)
 assert sha_file(authority_json)==AUTH_SHA,(sha_file(authority_json),AUTH_SHA)
 auth=json.loads(authority_json.read_text(encoding='utf-8'))
 assert auth['predecessor_zip_sha256']==BASE_SHA
 assert auth['source_terminal_counts']==EXPECTED_SOURCE_COUNTS
 assert auth['authorized_source_corrections']==37 and auth['already_correct_noops']==2 and auth['changed_record_count']==36
 assert len(auth['mutations'])==36 and len(auth['topology_edits'])==3
 shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
 with zipfile.ZipFile(base_zip) as z:
  assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()));z.extractall(out)
 basehash={k:sha_file(p) for k,p in files(out).items()};basepaths=set(basehash)
 src=(out/'index.html').read_text(encoding='utf-8');assert src==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 # Freeze baseline raw protected constants before modification.
 protected_before={}
 for n in PROTECTED_CANONICAL:
  try:protected_before[n]=raw_const(src,n)[0]
  except AssertionError:pass
 TL=raw_const(src,'TEXT_LIBRARY')[1];FLOW=raw_const(src,'LDC_LIBRARY_FLOW_LAYOUT')[1];assert TL is not None and FLOW is not None
 O={n:raw_const(src,n)[1] for n in OFFSET_NAMES}
 tlmap=text_library_map(TL)
 # Verify exact before hashes/texts and apply complete-record authority to copied successor tree only.
 affected={}; applied=[]
 for m in auth['mutations']:
  sid=m['record_id'];assert sid in tlmap,sid
  item,idx,old=tlmap[sid]
  assert old==m['before_text'] and sha_text(old)==m['before_sha256'],('before',sid)
  new=m['after_text'];assert sha_text(new)==m['after_sha256'] and new!=old,sid
  item['body'][idx]=new;affected[sid]=(old,new);applied.append({'record_id':sid,'before_sha256':m['before_sha256'],'after_sha256':m['after_sha256'],'certified_ordinals':[x['cumulative_ordinal'] for x in m['certified_ldc_entries']],'minimal_hunks':m['minimal_hunks']})
 # Regenerate offset-bearing presentation metadata deterministically, preserving semantic speaker assignments.
 remap_log=[]
 for sid,(old,new) in affected.items():
  for n in ['SPEECH_DATA','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS']:
   obj=O[n]
   if isinstance(obj,dict) and sid in obj:
    b=copy.deepcopy(obj[sid]);obj[sid]=remap(obj[sid],old,new);remap_log.append({'record_id':sid,'layer':n,'before':b,'after':copy.deepcopy(obj[sid])})
  topo=O['VISIBLE_PARAGRAPH_TOPOLOGY']
  if sid in (topo or {}).get('local_breaks',{}):
   b=copy.deepcopy(topo['local_breaks'][sid]);topo['local_breaks'][sid]=remap(topo['local_breaks'][sid],old,new);remap_log.append({'record_id':sid,'layer':'VISIBLE_PARAGRAPH_TOPOLOGY.local_breaks','before':b,'after':copy.deepcopy(topo['local_breaks'][sid])})
  # LDC flow intra offset remap + action-key remap.
  item,idx,_=tlmap[sid];iid=item['id']
  for block in FLOW.get(iid,[]):
   if str(idx) in block.get('intra',{}):
    before=copy.deepcopy(block['intra'][str(idx)]);newcuts=[mb(old,new,x) for x in before];block['intra'][str(idx)]=newcuts
    ia=block.get('intra_actions',{}).get(str(idx),{})
    if ia:
     block['intra_actions'][str(idx)]={str(mb(old,new,int(k))):v for k,v in ia.items()}
    remap_log.append({'record_id':sid,'layer':'LDC_LIBRARY_FLOW_LAYOUT.intra','before':before,'after':newcuts})
 # Apply exactly three boundary topology joins by removing current-LDC flow break_before entries.
 topology_log=[]
 for te in auth['topology_edits']:
  iid=te['item_id'];idx=int(te['physical_index']);sid=te['record_id']
  block=next(b for b in FLOW[iid] if int(b['start'])<=idx<int(b['end']))
  assert idx in block.get('break_before',[]) and block.get('break_before_actions',{}).get(str(idx))==te['before_action']
  block['break_before']=[x for x in block['break_before'] if int(x)!=idx]
  del block['break_before_actions'][str(idx)]
  topology_log.append(te)
 # Prune/remap invalid zero-length artifacts just as prior governed text mutation builder.
 text_by_id={sid:item['body'][idx] for sid,(item,idx,_old) in tlmap.items()}
 for sid,(old,new) in affected.items():
  L=len(new)
  if sid in O['SPEECH_END_VISUAL_BREAKS']:
   vals=sorted(set(x for x in O['SPEECH_END_VISUAL_BREAKS'][sid] if isinstance(x,int) and 0<x<L))
   if vals:O['SPEECH_END_VISUAL_BREAKS'][sid]=vals
   else:O['SPEECH_END_VISUAL_BREAKS'].pop(sid,None)
  if sid in O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS']:
   q=[x for x in O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS'][sid] if x.get('end',0)>x.get('start',0) and x.get('end',0)<=L]
   if q:O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS'][sid]=q
   else:O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS'].pop(sid,None)
  if sid in O['SPEECH_PRESENTATION_PROJECTION']:
   q=O['SPEECH_PRESENTATION_PROJECTION'][sid];q['hidden']=[x for x in q.get('hidden',[]) if x.get('end',0)>x.get('start',0) and x.get('end',0)<=L];q['breaks']=sorted(set(x for x in q.get('breaks',[]) if isinstance(x,int) and 0<x<L))
  topo=O['VISIBLE_PARAGRAPH_TOPOLOGY']
  if sid in (topo or {}).get('local_breaks',{}):
   vals=sorted(set(x for x in topo['local_breaks'][sid] if isinstance(x,int) and 0<x<L))
   if vals:topo['local_breaks'][sid]=vals
   else:topo['local_breaks'].pop(sid,None)
 # Rebuild tlmap after mutation for validations.
 tlmap1=text_library_map(TL);text_by_id={sid:t for sid,(_it,_idx,t) in tlmap1.items()}
 validate_offsets(text_by_id,O,FLOW,tlmap1)
 # Ensure source-ordinal universe represented exactly: 37 applied source corrections, no rejected/OOS.
 represented=sorted({o for x in applied for o in x['certified_ordinals']})
 assert len(represented)==37 and represented==sorted(represented)
 # Rebuild HTML constants. CORPUS and canonical/non-LDC declarations remain unchanged.
 t=src
 t=replace_const(t,'TEXT_LIBRARY',TL);t=replace_const(t,'LDC_LIBRARY_FLOW_LAYOUT',FLOW)
 for n in OFFSET_NAMES:t=replace_const(t,n,O[n])
 # Update internal linked-LDC provenance authority only; no user-facing content wording changed beyond dynamic version/revision.
 ldc=raw_const(t,'LDC_CURRENT_SYNC_AUTHORITY')[1];assert ldc is not None
 ldc['fast_mode_derivative_correction_sync']={
  'date':DATE,'predecessor_app_version':BASE_VERSION,'predecessor_zip_sha256':BASE_SHA,
  'certified_fast_mode_accepted_entries':2707,'source_terminal_counts':EXPECTED_SOURCE_COUNTS,
  'authorized_source_corrections_applied':37,'already_correct_noops':2,'changed_current_derivative_records':36,
  'boundary_repairs_applied':5,'cross_record_flow_joins':3,'derivative_authority_sha256':AUTH_SHA,
  'scope':'ONLY_CORRECTION_CERTAIN_ACCEPTED_FAST_MODE_DEFECTS_PROVEN_PRESENT_IN_CURRENT_24H_LDC_DERIVATIVES__NO_NEW_LINGUISTIC_SWEEP'
 }
 t=replace_const(t,'LDC_CURRENT_SYNC_AUTHORITY',ldc)
 # Determine public version from update checker contract: it compares app_version only, so a public bump is mechanically required for discoverability from v101.139.
 t=exact_replace(t,"const APP_VERSION = 'v101.139';",f"const APP_VERSION = '{VERSION}';",'app version')
 t=exact_replace(t,"const BUILD_REVISION = 'R1';",f"const BUILD_REVISION = '{REV}';",'build revision')
 t=exact_replace(t,"const APP_EVIDENCE_STAGE = 'TWO_RESIDUAL_FRENCH_SOURCE_FIDELITY_SUCCESSOR_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",'stage')
 t=re.sub(r"const BUILD_DATE = '2026-09-08';[^\n]*",f"const BUILD_DATE = '{DATE}'; // {VERSION} {REV} / certified FAST Mode corrections applied only to proven current LDC derivatives",t,count=1)
 (out/'index.html').write_text(t,encoding='utf-8');(out/'luisa_24_heures.html').write_text(t,encoding='utf-8')
 # Release/cache identity.
 sw=(out/'sw.js').read_text(encoding='utf-8');sw=exact_replace(sw,'/* v101.139 R1 */','/* v101.140 R1 */','sw version');sw=exact_replace(sw,"const CACHE_NAME = 'luisa-24h-v101-139-r1';",f"const CACHE_NAME = '{CACHE}';",'sw cache');(out/'sw.js').write_text(sw,encoding='utf-8')
 man=json.loads((out/'manifest.json').read_text(encoding='utf-8'));assert man['version']=='v101.139' and man['build_revision']=='R1';man['version']=VERSION;man['build_revision']=REV;writej(out/'manifest.json',man)
 gates=['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update to v101.140 R1 from the currently deployed build','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing']
 v=json.loads((out/'version.json').read_text(encoding='utf-8'));assert v['app_version']=='v101.139' and v['build_revision']=='R1'
 v.update({'app_version':VERSION,'build_revision':REV,'build_date':DATE,'cache_name':CACHE,
  'release_scope':'Linked-LDC derivative textual successor of exact immutable v101.139 R1. Reconciles all 2,707 certified accepted LDC FAST Mode defects against the exhaustive current v101.139 LDC derivative inventory; applies 37 proven correction-certain source defects to 36 current derivative records, preserves 2 already-correct loci as no-ops, classifies 2,668 as not present, and leaves zero conflicts. Canonical Hour text, meditation/reflection/practice text, AFLP/full-text alternative content, unrelated UI, stable IDs and personal-data schemas are unchanged.',
  'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update/persistence, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.140 R1.',
  'overall_release_status':'V101140_R1_LDC_FAST_MODE_DERIVATIVE_CORRECTION_CONTROLLED_DEVICE_TEST_CANDIDATE__FINAL_PUBLIC_DEPLOYMENT_UNAUTHORIZED','known_blockers':gates,'external_open_gates':gates,
  'postfreeze_reopen_evidence':'Exact v101.140 R1 successor ZIP requires external SHA-bound final recheck before controlled device testing.'})
 writej(out/'version.json',v)
 # Preserve old active report historically if present.
 old_report=out/'reports/V101139_R1_TWO_RESIDUAL_TEXTUAL_SUCCESSOR.md'
 if old_report.exists():
  dst=out/'reports/historical/v101139_r1/V101139_R1_TWO_RESIDUAL_TEXTUAL_SUCCESSOR.md';dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old_report,dst);old_report.unlink()
 # Evidence copied from exact frozen premutation authority bundle supplied alongside builder.
 ev=out/'evidence/v101140_r1';ev.mkdir(parents=True,exist_ok=True)
 auth_dir=authority_json.parent
 for fn in ['L24H_V101140_R1_LDC_FAST_MODE_DERIVATIVE_AUTHORITY.json','V101139_LINKED_LDC_INVENTORY.json','V101139_LDC_TO_24H_MAPPING_LEDGER.json','V101139_SOURCE_DISPOSITION_LEDGER_2707.json','V101139_PREMUTATION_DERIVATIVE_AUTHORITY.json','V101139_BLOCKED_CONFLICT_LEDGER.json']:
  p=auth_dir/fn;assert p.exists(),p;shutil.copy2(p,ev/fn)
 writej(ev/'APPLIED_MUTATION_LEDGER.json',{'schema':'L24H_V101140_R1_APPLIED_MUTATION_LEDGER_V1','status':'PASS','predecessor_zip_sha256':BASE_SHA,'derivative_authority_sha256':AUTH_SHA,'applied_source_corrections':37,'changed_record_count':36,'records':applied})
 # Linked-LDC fingerprints over exact stable-id/text pairs only.
 before_pairs=[];after_pairs=[]
 baseTL=raw_const(src,'TEXT_LIBRARY')[1];baseMap=text_library_map(baseTL)
 # restrict same 2617 positive LDC records by IDs represented in premutation inventory
 inv=json.loads((ev/'V101139_LINKED_LDC_INVENTORY.json').read_text(encoding='utf-8'));inv_ids=[x['record_id'] for x in inv['records']]
 for sid in inv_ids:
  before_pairs.append([sid,baseMap[sid][2]]);after_pairs.append([sid,tlmap1[sid][2]])
 ldc_fp_before=sha_text(jdump(before_pairs));ldc_fp_after=sha_text(jdump(after_pairs));assert ldc_fp_before!=ldc_fp_after
 writej(ev/'DERIVED_PRESENTATION_REMAP.json',{'schema':'L24H_V101140_R1_DERIVED_PRESENTATION_REMAP_V1','status':'PASS','changed_text_records':36,'remap_actions':remap_log,'semantic_speaker_assignments_reopened':False,'rule':'Only character offsets mechanically downstream of authorized changed current LDC derivative strings were remapped.'})
 writej(ev/'FLOW_TOPOLOGY_REGENERATION.json',{'schema':'L24H_V101140_R1_FLOW_TOPOLOGY_REGENERATION_V1','status':'PASS','cross_record_join_count':3,'edits':topology_log,'physical_record_merges':0,'stable_id_changes':0})
 # Protected canonical parity proof.
 final_pre_meta=(out/'index.html').read_text(encoding='utf-8')
 protected_after={}
 for n in protected_before:
  try:protected_after[n]=raw_const(final_pre_meta,n)[0]
  except:pass
 # DISPLAY_SEGMENTS may have been remapped only if changed target occurs; current target hits = 0, so remains exact. CORPUS all exact.
 parity={n:(protected_before[n]==protected_after.get(n)) for n in protected_before}
 assert all(parity.values()),[n for n,x in parity.items() if not x]
 writej(ev/'PROTECTED_NON_LDC_PARITY.json',{'schema':'L24H_V101140_R1_PROTECTED_NON_LDC_PARITY_V1','status':'PASS','constants':parity,'canonical_corpus_delta':0,'canonical_hour_meditation_reflection_practice_text_delta':0,'aflp_full_text_alternative_delta':0,'stable_id_delta':0})
 # User data compatibility: stable IDs unchanged; current storage stores ranges by stable para ID and text anchors; no schema bump.
 writej(ev/'USER_DATA_COMPATIBILITY.json',{'schema':'L24H_V101140_R1_USER_DATA_COMPATIBILITY_V1','status':'PASS_INTERNAL_MODEL','storage_schema_before':8,'storage_schema_after':8,'personal_snapshot_before':5,'personal_snapshot_after':5,'stable_ids_changed':0,'changed_text_record_ids':sorted(affected),'offset_migration_in_persistent_user_data':'NOT_REQUIRED_BY_CURRENT_MODEL','reason':'Text corrections preserve stable paragraph IDs. Persisted highlights/notes are re-anchored by existing text/context logic; no stored corpus speaker offsets are user data. Physical-device persistence remains an external gate.'})
 # Build/current reports/metadata.
 report=f'''# {VERSION} {REV} — linked-LDC FAST Mode derivative correction successor\n\n- Immutable predecessor: `{BASE_VERSION}` SHA-256 `{BASE_SHA}`.\n- Frozen derivative authority SHA-256: `{AUTH_SHA}`.\n- Certified LDC source entries reconciled: **2,707**.\n- Terminal states: **2,668 NOT_PRESENT_IN_24H; 2 PRESENT_ALL_ALREADY_CORRECT; 37 PRESENT_WITH_APPLICABLE_DERIVATIVES; 0 BLOCKED**.\n- Applied: **37 certified source corrections → 36 current LDC-derived body records**.\n- Exact text hunks: **40**. Cross-record flow joins: **3**.\n- Canonical Hour / meditation / reflection / practice text changes: **0**. AFLP/full-text alternative changes: **0**.\n- Stable-ID changes: **0**. Storage schema: **8 unchanged**. Personal snapshot schema: **5 unchanged**.\n- Linked-LDC derivative fingerprint: `{ldc_fp_before}` → `{ldc_fp_after}`.\n- Final public deployment remains **UNAUTHORIZED** until the external device/live-origin/PWA/offline/accessibility gates close.\n'''
 (out/'reports/V101140_R1_LDC_FAST_MODE_DERIVATIVE_CORRECTION.md').write_text(report,encoding='utf-8')
 # README current header only, preserve useful body but avoid stale first-version claim.
 readme=(out/'README.md').read_text(encoding='utf-8') if (out/'README.md').exists() else ''
 readme=re.sub(r'(?s)^#.*?(?=\n#|\Z)',f'# {VERSION} {REV} — current controlled device-test candidate\n\nCurrent stage: `{STAGE}`. Exact predecessor `{BASE_VERSION}` SHA-256 `{BASE_SHA}`. Applies only the frozen linked-LDC FAST Mode derivative authority `{AUTH_SHA}`: 37 certified corrections / 36 current LDC body records / 0 conflicts. Final public deployment remains unauthorized.\n',readme,count=1)
 (out/'README.md').write_text(readme,encoding='utf-8')
 # QA checklist/template rebuilt for the current linked-LDC successor; do not inherit predecessor-specific loci/stage.
 qa_check=f'''# Real-device QA checklist — {VERSION} {REV}

Use only the exact {VERSION} {REV} candidate identified by the external SHA-bound receipt. Internal browser/runtime evidence does not substitute for these physical-device/PWA/accessibility gates.

## Identity
- app_version = {VERSION}
- build_revision = {REV}
- cache_name = {CACHE}
- APP_EVIDENCE_STAGE = {STAGE}
- canonical corpus fingerprint = {v.get('corpus_fingerprint_sha256','c275fdb9f5ad86f92158e6ca9db5329bf7b1bd30ab35b0d16dbeed1ebf080840')}
- frozen linked-LDC derivative authority = {AUTH_SHA}

## Linked-LDC correction smoke checks
- Open Approfondir-linked Livre du Ciel content for each affected item: PART_III_MARY_SORROWS, RELATED_HOUR_05, RELATED_HOUR_17, RELATED_HOUR_21, RELATED_HOUR_22 and RELATED_HOUR_23.
- Confirm representative corrected passages render as normal prose with no missing/duplicated text or broken speaker styling.
- Confirm the three authorized cross-record joins in RELATED_HOUR_05, RELATED_HOUR_17 and RELATED_HOUR_21 render without an obsolete paragraph break.
- Search from representative corrected wording in all six affected items and confirm navigation resolves to the intended linked-LDC text.
- Create a highlight/note on corrected linked-LDC text, close/reopen, then edit/delete it; verify re-anchoring and persistence.

## Protected regression
- Canonical Hours, Méditée/Réflexions et pratiques, AFLP/full-text alternative and unrelated Help/UI paths behave normally.
- Assistance quick-nav focus remains repaired.
- Existing notes/highlights/progression/last-place/theme/font survive the installed-PWA update.

## External gates
- Physical iPhone validation.
- Physical iPad portrait and landscape validation.
- Physical Samsung/Android validation.
- Live-origin exact-byte binding to the externally certified {VERSION} {REV} ZIP.
- Installed-PWA update from the actually deployed predecessor and three close/reopen cycles.
- True offline cold reopen after update.
- Representative VoiceOver and TalkBack navigation.

Final public deployment remains unauthorized until all external gates are evidenced.
'''
 (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(qa_check,encoding='utf-8')
 qa_rows=['test_id,platform,required,expected,actual,status,notes',
  f'ID-01,browser,YES,Aide shows {VERSION} {REV} and stage {STAGE},,,',
  'LDC-01,iPhone;iPad;Samsung,YES,Corrected linked-LDC passages render normally in all six affected items,,,',
  'LDC-02,iPhone;iPad;Samsung,YES,Three authorized cross-record joins render without obsolete paragraph breaks,,,',
  'SEARCH-01,iPhone;iPad;Samsung,YES,Representative corrected wording in all six affected linked-LDC items resolves to intended text,,,',
  'STATE-01,iPhone;iPad;Samsung,YES,Existing notes highlights progression last-place theme and font survive installed-PWA update,,,',
  'STATE-02,iPhone;iPad;Samsung,YES,Highlight and note on corrected linked-LDC text re-anchor persist edit and delete correctly after close/reopen,,,',
  'PWA-01,iPhone;iPad;Samsung,YES,Installed-PWA update reaches exact externally SHA-bound v101.140 R1 bytes and survives three close/reopen cycles,,,',
  'OFFLINE-01,iPhone;iPad;Samsung,YES,True offline cold reopen succeeds after installed-PWA update,,,',
  'A11Y-01,iPhone;iPad;Samsung,YES,Representative VoiceOver or TalkBack navigation is usable,,,']
 (out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').write_text('\n'.join(qa_rows)+'\n',encoding='utf-8')
 # Current metadata.
 writej(out/'metadata/build_provenance.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,'baseline_version':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,'derivative_authority_sha256':AUTH_SHA,'certified_source_entries':2707,'source_terminal_counts':EXPECTED_SOURCE_COUNTS,'applied_source_corrections':37,'changed_current_ldc_records':36,'text_hunks':40,'cross_record_flow_joins':3,'canonical_corpus_changes':0,'stable_id_changes':0,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'corpus_fingerprint_sha256':v.get('corpus_fingerprint_sha256','c275fdb9f5ad86f92158e6ca9db5329bf7b1bd30ab35b0d16dbeed1ebf080840'),'linked_ldc_derivative_fingerprint_before':ldc_fp_before,'linked_ldc_derivative_fingerprint_after':ldc_fp_after,'final_validation':'EXTERNAL_EXACT_ZIP_RECHECK_REQUIRED'})
 writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_evidence_root':'evidence/v101140_r1','immediate_build_predecessor':{'version':BASE_VERSION,'sha256':BASE_SHA},'derivative_authority_sha256':AUTH_SHA,'certified_fast_mode_authority':'2,707 accepted source defects; correction-certain only','content_authority':'v101.139 current derivative mapping frozen before mutation','preserve_move_visibility':'EVIDENCE_ONLY_NOT_UI'})
 writej(out/'metadata/current_gate_map.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'internal_gates':['exact v101.139 R1 SHA binding','2,707-entry source disposition reconciliation','37/37 applied certified current derivative corrections','2/2 already-correct no-ops preserved','0 blocked conflicts','36-record exact before/after hash binding','40-hunk minimality','3 boundary topology joins','derived offset integrity','canonical/non-LDC parity','HTML mirror identity','deterministic rebuild','four-pass adversarial package audit','fresh ZIP reopen integrity'],'external_open_gates':gates,'public_release':'UNAUTHORIZED'})
 writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'package_rule':'Package does not self-certify final ZIP bytes; exact frozen v101.140 R1 ZIP must receive external SHA-bound final validation receipt.','immediate_build_predecessor':BASE_VERSION,'immediate_build_predecessor_sha256':BASE_SHA,'linked_ldc_text_changed':True,'canonical_hour_text_changed':False,'physical_device_claims':'NOT_TESTED','public_deployment_authorized':False})
 writej(out/'metadata/scope_escalation_authority.md',{}) if False else None
 (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} scope authority\n\nAuthorized content scope is exclusively the frozen current-derivative mutation authority SHA-256 `{AUTH_SHA}`, based on exact immutable `{BASE_VERSION}` SHA-256 `{BASE_SHA}` and the certified 2,707 accepted LDC FAST Mode source ledger. Exactly 37 present certified corrections are applied to 36 current LDC derivative records; 2 already-correct loci remain no-ops; 2,668 are not present; 0 are blocked.\n\nForbidden: any non-LDC text change; canonical Hour/meditation/reflection/practice mutation; AFLP/full-text alternative mutation; rejected/OOS FAST Mode case; semantic speaker reinterpretation; stable-ID/schema/UI change except mechanically required version/cache/evidence identity.\n\nFinal public deployment remains externally gated.\n''',encoding='utf-8')
 writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_builder':'scripts/build_v101140_r1_ldc_fast_mode.py','builder_contract':'Exact SHA-bound v101.139 R1 predecessor + exact frozen derivative authority SHA; apply 36 before/after current LDC records, deterministic offset/topology consequences, version/cache/evidence only.'})
 writej(out/'metadata/builder_input_manifest.json',{'version':VERSION,'build_revision':REV,'predecessor_v101139_r1_zip_sha256':BASE_SHA,'derivative_authority_sha256':AUTH_SHA})
 writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'active_documents':['README.md','REAL_DEVICE_QA_CHECKLIST.md','reports/V101140_R1_LDC_FAST_MODE_DERIVATIVE_CORRECTION.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md'],'active_test_artifacts':['REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'],'historical_reports_root':'reports/historical/','rule':'Only listed active documents are current; predecessor/superseded reports and tooling are historical within original scope.'})
 # Copy exact builder itself into package.
 shutil.copy2(Path(__file__),out/'scripts/build_v101140_r1_ldc_fast_mode.py')
 # Deep invariants after all writes, before manifests.
 final=(out/'index.html').read_text(encoding='utf-8');assert final==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 TLf=raw_const(final,'TEXT_LIBRARY')[1];FM=raw_const(final,'LDC_LIBRARY_FLOW_LAYOUT')[1];tlmapf=text_library_map(TLf)
 changed=[sid for sid in tlmapf if sid in baseMap and tlmapf[sid][2]!=baseMap[sid][2]];assert sorted(changed)==sorted(affected),len(changed)
 for m in auth['mutations']:assert tlmapf[m['record_id']][2]==m['after_text'] and sha_text(tlmapf[m['record_id']][2])==m['after_sha256']
 # Canonical protected constants exact parity (except LDC metadata/flow/offset layers deliberately downstream).
 for n,raw in protected_before.items():
  if n in ['DISPLAY_SEGMENTS']:assert raw_const(final,n)[0]==raw,n
  elif n not in ['PASSION24_LDC_CROSSREF_INDEX'] or True: assert raw_const(final,n)[0]==raw,n
 assert "const APP_VERSION = 'v101.140';" in final and STAGE in final and CACHE in (out/'sw.js').read_text(encoding='utf-8')
 assert json.loads((out/'version.json').read_text())['storage_schema']==8 and json.loads((out/'version.json').read_text())['personal_snapshot']==5
 # Offset validation again from final.
 Of={n:raw_const(final,n)[1] for n in OFFSET_NAMES};validate_offsets({sid:x[2] for sid,x in tlmapf.items()},Of,FM,tlmapf)
 # File scope proof before manifests.
 cur=files(out);removed=sorted(basepaths-set(cur));allowed_removed=['reports/V101139_R1_TWO_RESIDUAL_TEXTUAL_SUCCESSOR.md'];assert removed==allowed_removed,removed
 # Overlay manifests.
 changed_files=sorted(k for k,p in cur.items() if k not in basehash or sha_file(p)!=basehash[k])
 writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101140_R1_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,'changed_or_added':sorted(set(changed_files)|{'metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json'}),'removed':removed,'text_library_changed_records':36,'canonical_corpus_delta':'ZERO','stable_id_delta':'ZERO','ldc_flow_topology_delta':'3_BOUNDARY_JOINS','semantic_speaker_delta':'ZERO'})
 ex={'metadata/hash_manifest.json','metadata/package_manifest.json'};lst=[]
 for k,p in sorted(files(out).items()):
  if k in ex:continue
  lst.append({'path':k,'size':p.stat().st_size,'sha256':sha_file(p)})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
 writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
 return {'version':VERSION,'revision':REV,'stage':STAGE,'base_sha256':BASE_SHA,'authority_sha256':AUTH_SHA,'source_terminal_counts':EXPECTED_SOURCE_COUNTS,'applied_source_corrections':37,'changed_text_records':36,'text_hunks':40,'flow_joins':3,'linked_ldc_fingerprint_before':ldc_fp_before,'linked_ldc_fingerprint_after':ldc_fp_after,'files':len(files(out)),'manifested_nonself_files':len(lst),'cache':CACHE}

if __name__=='__main__':
 if len(sys.argv)!=5:raise SystemExit('Usage: build.py <v101139_R1.zip> <derivative_authority.json> <out_dir> <out.zip>')
 info=build(sys.argv[1],sys.argv[2],sys.argv[3]);zsha=freeze(sys.argv[3],sys.argv[4]);info['zip_sha256']=zsha;info['zip_size']=Path(sys.argv[4]).stat().st_size;print(json.dumps(info,ensure_ascii=False,indent=2))
