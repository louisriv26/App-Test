from pathlib import Path
import csv,json,hashlib,zipfile,shutil,difflib,re,copy,os
BASE=Path('/mnt/data/24h_m0m5_work/r4/immutable_authority/L24H_v101135_LOCKED.zip')
LEDGER=Path('/mnt/data/24H_V101135_INTERIM_M0_M5_RECONCILIATION_2026-09-07/02_INTERIM_CLOSED_MUTATION_UNIVERSE_96_CANDIDATE.csv')
BASE_SHA='cf8b688e649b2ef3f7c36768691c6a647d9d1e9eec85c90ba697dc2a05ef26fc'
LEDGER_SHA='6bce9bad3c0c3be87beaa95e987a3a3f0ada2c8ac6a4209ba6ca788698f9737d'
VERSION='v101.136'; STAGE='INTERIM_CLOSED_96_SUCCESSOR_R2'; DATE='2026-09-07'; CACHE='luisa-24h-v101-136-r2'
R6_ZIP='35ee5c69fe0468d2e3ee2d963a7fa6667169c24d6c8023da2726b4cd8b50ed20'; R6_MAN='0d04190b166932086ed45141368bd4ae88b5a22806ca1e525a3e6a60a267f3ad'
def sha(b):return hashlib.sha256(b).hexdigest()
def jdump(o):return json.dumps(o,ensure_ascii=False,separators=(',',':'))
def extract(t,n):
 m=re.search(rf'const\s+{re.escape(n)}\s*=\s*',t); assert m,n
 o,e=json.JSONDecoder().raw_decode(t[m.end():]); return o,m.end(),m.end()+e
def repl(t,n,o):
 old,s,e=extract(t,n); return t[:s]+jdump(o)+t[e:]
def cmap(c):
 d={}
 for h in c['hours']:
  for k in ('paragraphs','reflections'):
   for p in h.get(k,[]):d[p['id']]=p
  for sub in h.get('subsections',[]):
   for p in sub.get('paragraphs',[]):d[p['id']]=p
 for pr in c.get('prayers',[]):
  for p in pr.get('paragraphs',[]):d[p['id']]=p
 for sec in c.get('sections',[]):
  for p in sec.get('paragraphs',[]):d[p['id']]=p
 return d
def tlmap(tl):
 d={}
 for it in tl:
  body=it.get('body') or []; nums=it.get('body_stable_numbers') or []
  for i,x in enumerate(body):
   n=nums[i] if i<len(nums) else i+1
   try:n=f'{int(n):03d}'
   except:n=str(n)
   d[f"{it['id']}.BODY.P{n}"]=(it,i)
 return d
def get(sid,c,tl):
 cm=cmap(c);tm=tlmap(tl)
 if sid in cm:return cm[sid]['t']
 if sid in tm:return tm[sid][0]['body'][tm[sid][1]]
 raise KeyError(sid)
def setv(sid,v,c,tl):
 cm=cmap(c);tm=tlmap(tl)
 if sid in cm:cm[sid]['t']=v;return
 if sid in tm:tm[sid][0]['body'][tm[sid][1]]=v;return
 raise KeyError(sid)
def mb(old,new,pos):
 if pos<=0:return 0
 if pos>=len(old):return len(new)
 sm=difflib.SequenceMatcher(None,old,new,autojunk=False)
 for tag,i1,i2,j1,j2 in sm.get_opcodes():
  if pos==i1:return j1
  if pos==i2:return j2
  if i1<pos<i2:
   if tag=='equal':return j1+(pos-i1)
   return round(j1+(pos-i1)*(j2-j1)/(i2-i1)) if i2>i1 else j1
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
def writej(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def files(root):return {p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file()}
def build(out):
 out=Path(out);shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
 assert sha(BASE.read_bytes())==BASE_SHA and sha(LEDGER.read_bytes())==LEDGER_SHA
 with zipfile.ZipFile(BASE) as z: assert z.testzip() is None;z.extractall(out)
 basehash={k:sha(p.read_bytes()) for k,p in files(out).items()}
 src=(out/'index.html').read_text(encoding='utf-8');assert src==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 C,_,_=extract(src,'CORPUS');TL,_,_=extract(src,'TEXT_LIBRARY');C0=copy.deepcopy(C)
 names=['SPEECH_DATA','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY','DISPLAY_SEGMENTS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY']
 O={n:extract(src,n)[0] for n in names}
 rows=list(csv.DictReader(LEDGER.open(encoding='utf-8-sig')));assert len(rows)==96 and len({r['record_id'] for r in rows})==96
 affected={};apply=[]
 for r in rows:
  sid=r['record_id'];cur=get(sid,C,TL);assert cur==r['current_text'];assert sha(cur.encode())==r['current_sha256']
  setv(sid,r['target_text'],C,TL);affected[sid]=(cur,r['target_text']);apply.append({'record_id':sid,'lane':r['lane'],'epistemic_class':r['epistemic_class'],'pre_sha256':sha(cur.encode()),'post_sha256':sha(r['target_text'].encode()),'status':'APPLIED_EXACT_AUTHORIZED_RECORD'})
 # deterministic section display aggregate updates by paragraph order, preserving existing display-only whitespace breaks
 disp=[]
 def flexpat(x):
  return r'\s+'.join(re.escape(q) for q in re.split(r'\s+',x.strip()))
 def transform_span(oldp,newp,span):
  sm=difflib.SequenceMatcher(None,oldp,newp,autojunk=False);parts=[]
  for tag,i1,i2,j1,j2 in sm.get_opcodes():
   if tag=='equal':parts.append(span[mb(oldp,span,i1):mb(oldp,span,i2)])
   elif tag in ('replace','insert'):parts.append(newp[j1:j2])
  return ''.join(parts)
 oldsecs={x['section_id']:x for x in C0.get('sections',[])}
 for sec in C.get('sections',[]):
  before=oldsecs.get(sec['section_id'],{}).get('display_text')
  if not isinstance(before,str):continue
  oldps={p['id']:p['t'] for p in oldsecs[sec['section_id']].get('paragraphs',[])}
  changed=[p for p in sec.get('paragraphs',[]) if p['id'] in affected]
  if not changed:continue
  cursor=0;pieces=[]
  for p in changed:
   oldp=oldps[p['id']];m=re.search(flexpat(oldp),before[cursor:]);assert m,(sec['section_id'],p['id'],'aggregate old paragraph not found flexibly')
   a=cursor+m.start();b=cursor+m.end();pieces.append(before[cursor:a]);pieces.append(transform_span(oldp,p['t'],before[a:b]));cursor=b
  pieces.append(before[cursor:]);d=''.join(pieces);sec['display_text']=d
  disp.append({'section_id':sec['section_id'],'changed_paragraphs':[p['id'] for p in changed],'pre_sha256':sha(before.encode()),'post_sha256':sha(d.encode()),'status':'DERIVED_AGGREGATE_REBUILT_PRESERVING_DISPLAY_WHITESPACE'})
 # remap all known offset-bearing authorities
 remaps=[]
 for sid,(old,new) in affected.items():
  if old==new:continue
  for n in ['SPEECH_DATA','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS']:
   obj=O[n]
   if isinstance(obj,dict) and sid in obj:
    b=copy.deepcopy(obj[sid]);obj[sid]=remap(obj[sid],old,new);remaps.append({'record_id':sid,'layer':n,'before':b,'after':obj[sid]})
  topo=O['VISIBLE_PARAGRAPH_TOPOLOGY']
  for k in ('local_breaks','cross_record_breaks','cross_record_joins'):
   if isinstance(topo.get(k),dict) and sid in topo[k]:
    b=copy.deepcopy(topo[k][sid]);topo[k][sid]=remap(topo[k][sid],old,new);remaps.append({'record_id':sid,'layer':'VISIBLE_PARAGRAPH_TOPOLOGY.'+k,'before':b,'after':topo[k][sid]})
  # prune derived artifacts that collapse onto the new paragraph boundary after authorized deletions
  L=len(new)
  if sid in O['SPEECH_END_VISUAL_BREAKS']:
   O['SPEECH_END_VISUAL_BREAKS'][sid]=[x for x in O['SPEECH_END_VISUAL_BREAKS'][sid] if 0<x<L]
   if not O['SPEECH_END_VISUAL_BREAKS'][sid]: del O['SPEECH_END_VISUAL_BREAKS'][sid]
  if sid in O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS']:
   O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS'][sid]=[x for x in O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS'][sid] if x.get('end',0)>x.get('start',0) and x.get('end',0)<=L]
   if not O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS'][sid]: del O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS'][sid]
  if sid in O['SPEECH_PRESENTATION_PROJECTION']:
   q=O['SPEECH_PRESENTATION_PROJECTION'][sid];q['hidden']=[x for x in q.get('hidden',[]) if x.get('end',0)>x.get('start',0) and x.get('end',0)<=L];q['breaks']=[x for x in q.get('breaks',[]) if 0<x<L]
  for k in ('local_breaks','cross_record_breaks'):
   if isinstance(topo.get(k),dict) and sid in topo[k]:
    topo[k][sid]=[x for x in topo[k][sid] if isinstance(x,int) and 0<x<L]
    if not topo[k][sid]: del topo[k][sid]
 # LDC flow offsets. IMPORTANT: renderer keys `intra` by zero-based physical body index,
 # not by stable paragraph number. R1 incorrectly used stable numbers and is invalidated.
 flow=O['LDC_LIBRARY_FLOW_LAYOUT'];tm=tlmap(TL);flowlog=[]
 for sid,(old,new) in affected.items():
  if sid not in tm or old==new:continue
  it,idx=tm[sid];key=str(idx)
  for ent in flow.get(it['id'],[]):
   intra=ent.get('intra',{})
   if key in intra:
    a=list(intra[key]);raw=[mb(old,new,x) for x in a]
    b=sorted(set(x for x in raw if isinstance(x,int) and 0<x<len(new)))
    acts=(ent.get('intra_actions',{}) or {}).get(key)
    mapped_actions={}
    if isinstance(acts,dict):
     for k,v in acts.items():
      nk=mb(old,new,int(k))
      if 0<nk<len(new):
       sk=str(nk)
       if sk in mapped_actions and mapped_actions[sk]!=v: raise AssertionError((sid,key,'flow action collision',mapped_actions[sk],v))
       mapped_actions[sk]=v
    if b: intra[key]=b
    else: intra.pop(key,None)
    ia=ent.get('intra_actions',{})
    if mapped_actions: ia[key]=mapped_actions
    else: ia.pop(key,None)
    flowlog.append({'record_id':sid,'physical_index':idx,'entry_id':ent.get('entry_id'),'old_cuts':a,'raw_mapped_cuts':raw,'new_cuts':b,'old_actions':acts or {},'new_actions':mapped_actions})
 # LDC bounded authority extends to official R6 13 sync, not full reimport
 auth=O['LDC_CURRENT_SYNC_AUTHORITY'];auth['interim_r6_sync']={'source_public_version':'65','source_app_version':'v2.19.65-R1B','corpus_version':'G036-AFLP-R6-SUP-T5','backbone_corpus_version':'G036-AFLP-R6-UWR2','source_package_sha256':R6_ZIP,'source_corpus_manifest_sha256':R6_MAN,'sync_date':DATE,'operation_count':13,'scope':'ONLY_13_OFFICIAL_R6_DERIVATIVE_SYNCHRONIZATIONS__NO_FULL_LINKED_LIBRARY_REIMPORT'};auth['interim_closed_local_qa']={'operation_count':83,'date':DATE,'scope':'ONLY_CLOSED_PREAUTHORIZED_24H_TEXT_RECORDS__H23_SOURCE_CRITICAL_AND_300_LDC_UPSTREAM_FINDINGS_EXCLUDED'}
 # fingerprint
 C['fingerprint_algorithm']='sha256_canonical_json_without_fingerprint_sha256_v101136';tmp={k:v for k,v in C.items() if k!='fingerprint_sha256'};C['fingerprint_sha256']=sha(jdump(tmp).encode())
 t=src
 for n,o in [('CORPUS',C),('TEXT_LIBRARY',TL)]+[(n,O[n]) for n in names]:t=repl(t,n,o)
 old="const APP_VERSION = 'v101.135';";assert t.count(old)==1;t=t.replace(old,f"const APP_VERSION = '{VERSION}';",1)
 old="const APP_EVIDENCE_STAGE = 'MASTER_SCRIPT_VALIDATION_COMPLETION_R1';";assert t.count(old)==1;t=t.replace(old,f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
 t=re.sub(r"const BUILD_DATE = '2026-09-04';[^\n]*",f"const BUILD_DATE = '{DATE}'; // {VERSION} / exact 96-record closed interim successor",t,count=1)
 (out/'index.html').write_text(t,encoding='utf-8');(out/'luisa_24_heures.html').write_text(t,encoding='utf-8')
 v=json.loads((out/'version.json').read_text());v.update({'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,'ldc_source_public_version':'65','ldc_source_app_version':'v2.19.65-R1B','ldc_source_package_sha256':R6_ZIP,'ldc_source_alignment_generation':'G036-AFLP-R6-UWR2','ldc_source_enriched_generation':'G036-AFLP-R6-SUP-T5','ldc_source_corpus_manifest_sha256':R6_MAN,'release_scope':'Governed interim content successor of immutable v101.135. Applies exactly 96 authorized records: 83 closed local 24H mutations + 13 bounded derivative synchronizations to official LDC R6. Excludes 2 challenged flow no-ops, 1 context-only row, all 300 upstream LDC linguistic findings, and all H23 source-critical/recension-sensitive findings.','overall_release_status':'INTERIM_SUCCESSOR_BUILT__POSTFREEZE_INTERNAL_VALIDATION_PENDING__PUBLIC_DEPLOYMENT_UNAUTHORIZED','real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.136.','known_blockers':[],'external_open_gates':['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing']});writej(out/'version.json',v)
 m=json.loads((out/'manifest.json').read_text());m['version']=VERSION;writej(out/'manifest.json',m)
 sw=(out/'sw.js').read_text();sw=sw.replace('/* v101.135 */','/* v101.136 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-135';",f"const CACHE_NAME = '{CACHE}';",1);(out/'sw.js').write_text(sw)
 ev=out/'evidence/v101136';ev.mkdir(parents=True,exist_ok=True);shutil.copy2(LEDGER,ev/'AUTHORIZED_MUTATION_UNIVERSE_96.csv')
 with (ev/'APPLY_LEDGER_96.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(apply[0]));w.writeheader();w.writerows(apply)
 writej(ev/'DERIVED_LAYER_REBUILD.json',{'schema':'L24H_V101136_DERIVED_REBUILD_V1','changed_records':sorted(affected),'offset_topology_remaps':remaps,'ldc_flow_remaps':flowlog,'display_aggregate_rebuilds':disp,'search':'RUNTIME_DERIVED_FROM_FINAL_CORPUS_AND_TEXT_LIBRARY_NO_SERIALIZED_INDEX','corpus_fingerprint_sha256':C['fingerprint_sha256'],'stable_record_ids_unchanged':True,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True})
 writej(ev/'AUTHORIZATION_RECEIPT.json',{'schema':'L24H_V101136_AUTHORIZATION_RECEIPT_V1','authorization':'USER_DO_IT_2026_09_07','predecessor_sha256':BASE_SHA,'authorized_ledger_sha256':LEDGER_SHA,'authorized_records':96,'scope_expansion':False,'excluded':{'flow_noops':2,'context_only':1,'upstream_ldc_linguistic':300,'h23_source_critical':'ALL'}})
 (out/'reports/V101136_INTERIM_CLOSED_SUCCESSOR.md').write_text(f'# v101.136 Interim Closed Successor\n\n- Predecessor: v101.135 `{BASE_SHA}`.\n- Authorized ledger: `{LEDGER_SHA}`.\n- Exact canonical record mutations: **96** = 83 local + 13 official-R6 derivative sync.\n- H23 source-critical findings and all 300 upstream linguistic findings are excluded.\n- Stable record IDs and personal-data schemas are unchanged.\n- Package-internal status is post-freeze validation pending; certification is external to immutable package bytes.\n',encoding='utf-8')
 (out/'README.md').write_text('# Les 24 Heures de la Passion — v101.136\n\nGoverned interim content successor of immutable v101.135. Exact scope: 96 authorized records only. Public deployment is not authorized; external device/PWA/offline/accessibility gates remain open.\n',encoding='utf-8')
 (out/'metadata/scope_escalation_authority.md').write_text(f'# v101.136 Scope Authority\n\nExactly 96 records from ledger SHA-256 `{LEDGER_SHA}` are authorized. No H23 source-critical finding and no upstream LDC linguistic finding is authorized. Any additional canonical text change requires a new authority.\n',encoding='utf-8')
 writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'stage':STAGE,'active_documents':['README.md','reports/V101136_INTERIM_CLOSED_SUCCESSOR.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md'],'historical_reports_root':'reports/historical/'})
 writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'stage':STAGE,'current_evidence_root':'evidence/v101136','predecessor_24h':{'version':'v101.135','sha256':BASE_SHA},'authorized_ledger_sha256':LEDGER_SHA,'governing_ldc_r6':{'version':'v2.19.65-R1B','official_zip_sha256':R6_ZIP,'corpus_manifest_sha256':R6_MAN}})
 writej(out/'metadata/build_provenance.json',{'version':VERSION,'stage':STAGE,'build_date':DATE,'baseline_version':'v101.135','baseline_zip_sha256':BASE_SHA,'baseline_html_sha256':sha(src.encode()),'candidate_html_sha256':sha(t.encode()),'authorized_ledger_sha256':LEDGER_SHA,'mutation_scope':'exact 96 records: 83 local + 13 official R6 derivative sync','canonical_text_changed':True,'stable_record_ids_unchanged':True,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'postfreeze_validation':'EXTERNAL_SHA_BOUND_RECEIPT'})
 writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'stage':STAGE,'immutable_package_rule':'postfreeze validation receipts remain external','physical_device_claims':'NOT_TESTED','public_deployment_authorized':False})
 # include builder
 shutil.copy2(Path(__file__),out/'scripts/build_v101136_interim_closed_96_r2.py')
 writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'stage':STAGE,'current_tools':['scripts/build_v101136_interim_closed_96_r2.py'],'reused_runtime_validation_lineage':'v101.135 runtime harnesses used externally after freeze'})
 writej(out/'metadata/current_gate_map.json',{'version':VERSION,'stage':STAGE,'gates':['authorized raw delta exact 96','derived offset/topology integrity','runtime broad matrix','H23 exclusion','A/B deterministic build','zip reopen exactness'],'postfreeze_receipt':'external'})
 writej(out/'metadata/builder_input_manifest.json',{'version':VERSION,'predecessor_zip_sha256':BASE_SHA,'authorized_ledger_sha256':LEDGER_SHA,'governing_ldc_r6_zip_sha256':R6_ZIP,'governing_ldc_r6_corpus_manifest_sha256':R6_MAN})
 # overlay/manifests
 cur=files(out);changed=sorted(k for k,p in cur.items() if k not in basehash or sha(p.read_bytes())!=basehash[k]);removed=sorted(set(basehash)-set(cur))
 for x in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
  if x not in changed:changed.append(x)
 writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101136_FULL_BUILD_OVERLAY_V1','version':VERSION,'baseline_version':'v101.135','baseline_zip_sha256':BASE_SHA,'changed_or_added':sorted(changed),'removed':removed})
 ex={'metadata/hash_manifest.json','metadata/package_manifest.json'};lst=[]
 for k,p in sorted(files(out).items()):
  if k in ex:continue
  lst.append({'path':k,'size':p.stat().st_size,'sha256':sha(p.read_bytes())})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst});writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
 return {'records':96,'remaps':len(remaps),'flow_remaps':len(flowlog),'display_rebuilds':len(disp),'html_sha256':sha((out/'index.html').read_bytes()),'fingerprint':C['fingerprint_sha256'],'files':len(files(out))}
def freeze(root,zp):
 root=Path(root);zp=Path(zp);zp.unlink(missing_ok=True)
 with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(root.rglob('*')):
   if not p.is_file():continue
   rel=p.relative_to(root).as_posix(); info=zipfile.ZipInfo(rel,(2026,9,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16);z.writestr(info,p.read_bytes())
 return sha(zp.read_bytes())
if __name__=='__main__':
 import sys
 print(json.dumps(build(sys.argv[1]),indent=2));print('ZIP',freeze(sys.argv[1],sys.argv[2]))
