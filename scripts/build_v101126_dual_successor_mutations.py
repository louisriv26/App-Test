#!/usr/bin/env python3
from pathlib import Path
import csv, json, hashlib, shutil, zipfile, difflib, copy, sys

BASE_ZIP=Path('/mnt/data/L24H_v101125_GITHUB_DEPLOY_EVIDENCE_SCHEMA_AND_DIRECT_REPORT_BINDING_RECONCILIATION_R1_LOCKED.zip')
EXPECTED_BASE_SHA='e227ae618fef06de784f9ba6b5b5a6a55ae8618e54f7a7841b7ba7b571e48a90'
EXPECTED_BASE_MEMBERS=428
LDC_ZIP_SHA='3e1d234c2de11ea8032cb7d56c3e5eb0d5faac1c8858e227fd730db61481eb50'
LDC_CORPUS_MANIFEST_SHA='76895194f21e21c058d8c7f1547977abad220caa501406b97ac4b4e05f1772e7'
VERSION='v101.126'
BUILD_DATE='2026-08-31'
STAGE='DUAL_SUCCESSOR_R5_15_LDC_SYNC_PLUS_19_NATIVE_R1'
CACHE='luisa-24h-v101-126'
FIXED=(2026,8,31,0,0,0)

LINKED=[
('OP-BEN-121-01','PASSION24.SECTION.BENEFITS.P121','Je ressens, sa tendresse','Je ressens sa tendresse'),
('OP-BEN-146-01','PASSION24.SECTION.BENEFITS.P146','Ce que le Père trouvait en Moi : Gloire, Délices, Amour, satisfactions complètes pour le Bien de tous Il le trouve en ces âmes.','Ce que le Père trouvait en Moi — Gloire, Délices, Amour, satisfactions complètes pour le Bien de tous — Il le trouve en ces âmes.'),
('OP-L17-072-01','PASSION24.TEXT.RELATED_HOUR_17.BODY.P072','Ce cris de mort','Ce cri de mort'),
('OP-L17-084-01','PASSION24.TEXT.RELATED_HOUR_17.BODY.P084','Tandis que où Elle ne règne pas','Tandis que là où Elle ne règne pas'),
('OP-L17-087-01','PASSION24.TEXT.RELATED_HOUR_17.BODY.P087',"C'est pourquoi, le peu de bien qu'Ils font, est laborieux, se sentant écrasés par le peu de bien accompli.","C'est pourquoi le peu de bien qu'ils font est laborieux ; ils se sentent écrasés par le peu de bien accompli."),
('OP-L17-088-01','PASSION24.TEXT.RELATED_HOUR_17.BODY.P088','la remplisse de Force','la remplit de Force'),
('OP-L17-089-01','PASSION24.TEXT.RELATED_HOUR_17.BODY.P089','en elle, fait le Bien','en elle fait le Bien'),
('OP-L17-097-01','PASSION24.TEXT.RELATED_HOUR_17.BODY.P097',"d'Amour Il me serra","d'Amour, Il me serra"),
('OP-L21-119-01','PASSION24.TEXT.RELATED_HOUR_21.BODY.P119',"Et Je suis la Tête d'où proviennent tous les bienfaits qui descendent sur toutes les générations, Maintenant Je cherche des âmes qui Me ressemblent par leurs souffrances et par leurs œuvres pour les faire participer à la grande gloire et au bonheur que porte Mon Humanité. Puisque ce ne sont pas toutes les âmes qui veulent profiter de cela et qui sont vidées d'elles-mêmes et des choses de la terre, J'en cherche avec lesquelles Je puisse devenir intimes et chez lesquelles Je puisse créer la souffrance d'être privées de Ma Présence.","Et Je suis la Tête d'où proviennent tous les bienfaits qui descendent sur toutes les générations. Maintenant, Je cherche des âmes qui Me ressemblent par leurs souffrances et par leurs œuvres, pour les faire participer à la grande gloire et au bonheur que porte Mon Humanité. Puisque ce ne sont pas toutes les âmes qui veulent en profiter et qui sont vidées d'elles-mêmes et des choses de la terre, J'en cherche avec lesquelles Je puisse devenir intime et chez lesquelles Je puisse créer la souffrance d'être privées de Ma Présence."),
('OP-LMARY-180-01','PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P180','Ainsi, d\'après le coût, ils puissent réaliser à quel point Je désire qu\'ils l’acquissent, qu’ils puissent l\'aimer, l\'apprécier qu’ils aspirent à vivre dans ce Règne de Ma Volonté Suprême."','Ainsi, à partir de ce coût, ils pourront connaître combien Je désire qu’ils l’acquièrent ; ils pourront l’apprécier, l’aimer et aspirer à entrer et à vivre dans le Règne de Ma Volonté Suprême. »'),
('OP-LMARY-211-01','PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P211','peines mortelles, est donc','peines mortelles est donc'),
('OP-L22-010-01','PASSION24.TEXT.RELATED_HOUR_22.BODY.P010',"ne prêtre l'oreille","ne prête l'oreille"),
('OP-L17-218-01','PASSION24.TEXT.RELATED_HOUR_17.BODY.P218','nausée S’il prend','nausée. S’il prend'),
('OP-L15-163-01','PASSION24.TEXT.RELATED_HOUR_15.BODY.P163','apporte avec elles, est absente','apporte avec elles est absente'),
('OP-LDIV-120-01','PASSION24.TEXT.PART_III_DIVINE_PASSION.BODY.P120','incapables, de multiplier','incapables de multiplier'),
]
NATIVE=[
('OP-H03-003-01','PASSION24.HOUR.03.P003','bien, est perdue','bien est perdue'),
('OP-H06-004-01','PASSION24.HOUR.06.P004','et qui soit à cause','et qui, soit à cause'),
('OP-H06-022-01','PASSION24.HOUR.06.P022','délices visuels','délices visuelles'),
('OP-H11-034-01','PASSION24.HOUR.11.P034','donnent, sont tels','donnent sont tels'),
('OP-H16-010-01','PASSION24.HOUR.16.P010','rendent assoiffées','rendent assoiffés'),
('OP-H16-036-01','PASSION24.HOUR.16.P036','soit marqués','soit marquée'),
('OP-H16-045-01','PASSION24.HOUR.16.P045','Tu souffres, est si grand','Tu souffres est si grand'),
('OP-H18R-001-01','PASSION24.HOUR.18.REF.P001','sauver les âmes, sont immenses','sauver les âmes sont immenses'),
('OP-H19-073-01','PASSION24.HOUR.19.P073','sois brûlé le cœur de toutes les créatures et détruits tous les amours profanes','soient brûlés les cœurs de toutes les créatures et détruits tous les amours profanes'),
('OP-H19-124-01','PASSION24.HOUR.19.P124','n’écoutes pas','n’écoute pas'),
('OP-H19-145-01','PASSION24.HOUR.19.P145','plus touchante que jamais qui','plus touchante que jamais, qui'),
('OP-H19-147-01','PASSION24.HOUR.19.P147','Tu ne T’apaise pas','Tu ne T’apaises pas'),
('OP-H19-147-02','PASSION24.HOUR.19.P147','qu’est-ce qui ne pourrait jamais Te calmer','qu’est-ce qui pourra jamais Te calmer'),
('OP-H19-199-01','PASSION24.HOUR.19.P199','Les anges, pleurent','Les anges pleurent'),
('OP-H21-046-01','PASSION24.HOUR.21.P046','dans l’amour partage avec moi','dans l’amour : partage avec moi'),
('OP-H21-082-01','PASSION24.HOUR.21.P082','ton cri, est extrêmement','ton cri est extrêmement'),
('OP-PR-004-01','PASSION24.PRAYER.HOLY_HOUR_THANKSGIVING.P004','avec Toi souffrant, de goûter','avec Toi souffrant et de goûter'),
('OP-PR-004-02','PASSION24.PRAYER.HOLY_HOUR_THANKSGIVING.P004','ton divin Cœur, est le plus','ton divin Cœur est le plus'),
('OP-PR-009-01','PASSION24.PRAYER.HOLY_HOUR_THANKSGIVING.P009','Croix de Jésus, et de savoir','Croix de Jésus et à savoir'),
]
OPS=[('LDC_SYNC',)+x for x in LINKED]+[('NATIVE_24H',)+x for x in NATIVE]
assert len(OPS)==34

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def jdump(o): return json.dumps(o,ensure_ascii=False,separators=(',',':'))
def extract_json_const(text,name):
    marker=f'const {name} = '
    st=text.index(marker)+len(marker)
    obj,end=json.JSONDecoder().raw_decode(text[st:])
    return obj,st,st+end
def replace_json_const(text,name,obj):
    old,st,en=extract_json_const(text,name)
    assert jdump(old)==text[st:en], f'noncanonical declaration {name}'
    return text[:st]+jdump(obj)+text[en:]

def corpus_record_map(c):
    out={}
    for h in c['hours']:
        for p in h.get('paragraphs',[]):out[p['id']]=p
        for p in h.get('reflections',[]):out[p['id']]=p
    for pr in c.get('prayers',[]):
        for p in pr.get('paragraphs',[]):out[p['id']]=p
    for s in c.get('sections',[]):
        for p in s.get('paragraphs',[]):out[p['id']]=p
    return out

def tl_index(tl):
    out={}
    for item in tl:
        body=item.get('body') or []; nums=item.get('body_stable_numbers') or []
        for i,s in enumerate(body):
            n=nums[i] if i<len(nums) else i+1
            try: ns=f'{int(n):03d}'
            except: ns=str(n)
            out[f"{item['id']}.BODY.P{ns}"]=(item,i)
    return out

def map_boundary(old,new,pos):
    if pos<=0:return 0
    if pos>=len(old):return len(new)
    sm=difflib.SequenceMatcher(None,old,new,autojunk=False)
    ops=sm.get_opcodes()
    # Prefer exact/equal and opcode boundaries.
    for tag,i1,i2,j1,j2 in ops:
        if pos==i1:return j1
        if pos==i2:return j2
        if i1<pos<i2:
            if tag=='equal': return j1+(pos-i1)
            if i2==i1:return j1
            return round(j1+(pos-i1)*(j2-j1)/(i2-i1))
    # monotone fallback from matching blocks
    blocks=sm.get_matching_blocks()
    left=(0,0); right=(len(old),len(new))
    for b in blocks:
        if b.a+b.size<=pos:left=(b.a+b.size,b.b+b.size)
        if b.a>=pos: right=(b.a,b.b);break
    if right[0]==left[0]:return left[1]
    return round(left[1]+(pos-left[0])*(right[1]-left[1])/(right[0]-left[0]))

def remap_ranges(obj,old,new):
    if isinstance(obj,list):
        # scalar break offset lists
        if all(isinstance(x,int) for x in obj): return [map_boundary(old,new,x) for x in obj]
        return [remap_ranges(x,old,new) for x in obj]
    if isinstance(obj,dict):
        d={}
        for k,v in obj.items():
            if k in ('start','end') and isinstance(v,int):d[k]=map_boundary(old,new,v)
            elif k=='breaks' and isinstance(v,list):d[k]=[map_boundary(old,new,x) for x in v]
            else:d[k]=remap_ranges(v,old,new)
        return d
    return obj

def get_text(sid,corpus,tl):
    rm=corpus_record_map(corpus)
    if sid in rm:return rm[sid]['t']
    ti=tl_index(tl)
    if sid in ti:
        item,i=ti[sid];return item['body'][i]
    raise KeyError(sid)

def set_text(sid,new,corpus,tl):
    rm=corpus_record_map(corpus)
    if sid in rm:rm[sid]['t']=new;return
    ti=tl_index(tl)
    if sid in ti:
        item,i=ti[sid];item['body'][i]=new;return
    raise KeyError(sid)

def text_surfaces(corpus,tl):
    yield from ((sid,p['t'],'CORPUS') for sid,p in corpus_record_map(corpus).items())
    for sid,(item,i) in tl_index(tl).items(): yield sid,item['body'][i],'TEXT_LIBRARY'

def apply_html(src):
    text=src
    corpus,_,_=extract_json_const(text,'CORPUS')
    tl,_,_=extract_json_const(text,'TEXT_LIBRARY')
    sd,_,_=extract_json_const(text,'SPEECH_DATA')
    adj,_,_=extract_json_const(text,'SPEECH_PRESENTATION_ADJUDICATIONS')
    proj,_,_=extract_json_const(text,'SPEECH_PRESENTATION_PROJECTION')
    topo,_,_=extract_json_const(text,'VISIBLE_PARAGRAPH_TOPOLOGY')
    endbreaks,_,_=extract_json_const(text,'SPEECH_END_VISUAL_BREAKS')
    flow,_,_=extract_json_const(text,'LDC_LIBRARY_FLOW_LAYOUT')
    ldc_auth,_,_=extract_json_const(text,'LDC_CURRENT_SYNC_AUTHORITY')
    corpus_before=copy.deepcopy(corpus);tl_before=copy.deepcopy(tl)
    old_texts={sid:s for sid,s,_ in text_surfaces(corpus,tl)}
    mutation_rows=[]; mirror_rows=[]; affected_texts={}
    # Primary operations exact-bound first.
    grouped={}
    for cls,oid,sid,old,repl in OPS: grouped.setdefault(sid,[]).append((cls,oid,old,repl))
    for sid,items in grouped.items():
        cur=get_text(sid,corpus,tl); original=cur
        for cls,oid,old,repl in items:
            assert cur.count(old)==1, f'{oid} primary count {cur.count(old)} in {sid}'
            before=cur;cur=cur.replace(old,repl,1)
            mutation_rows.append({'operation_id':oid,'class':cls,'stable_id':sid,'exact_span':old,'replacement':repl,'pre_text_sha256':sha_bytes(before.encode()),'post_step_text_sha256':sha_bytes(cur.encode()),'status':'APPLIED_EXACT_SCOPE'})
        set_text(sid,cur,corpus,tl); affected_texts[sid]=(original,cur)
    # Governed LDC mirrors: exact old span occurrences outside primary targets, plus Benefits display aggregate.
    primary=set(grouped)
    for cls,oid,sid,old,repl in [x for x in OPS if x[0]=='LDC_SYNC']:
        # Find only current matching text surfaces excluding primary. Each governed duplicate is byte-exact span-bound.
        for msid,s,surface in list(text_surfaces(corpus,tl)):
            if msid==sid: continue
            if old in s:
                assert s.count(old)==1, f'{oid} mirror duplicate span count in {msid}'
                new=s.replace(old,repl,1)
                set_text(msid,new,corpus,tl)
                if msid in affected_texts:
                    # Multiple operations in same mirror are supported.
                    affected_texts[msid]=(affected_texts[msid][0],new)
                else: affected_texts[msid]=(s,new)
                mirror_rows.append({'operation_id':oid,'primary_stable_id':sid,'mirror_id':msid,'surface':surface,'pre_text_sha256':sha_bytes(s.encode()),'post_text_sha256':sha_bytes(new.encode()),'status':'SYNCED_GOVERNED_MIRROR'})
        for sec in corpus.get('sections',[]):
            d=sec.get('display_text')
            if isinstance(d,str) and old in d:
                assert d.count(old)==1
                sec['display_text']=d.replace(old,repl,1)
                mirror_rows.append({'operation_id':oid,'primary_stable_id':sid,'mirror_id':sec['section_id'],'surface':'CORPUS_SECTION_DISPLAY_TEXT','pre_text_sha256':sha_bytes(d.encode()),'post_text_sha256':sha_bytes(sec['display_text'].encode()),'status':'REBUILT_RENDERED_AGGREGATE'})
    # Remap speech/projection/topology offsets for every changed stable text record.
    remap_log=[]
    for sid,(old,new) in affected_texts.items():
        if old==new:continue
        for name,obj in [('SPEECH_DATA',sd),('SPEECH_PRESENTATION_ADJUDICATIONS',adj),('SPEECH_PRESENTATION_PROJECTION',proj),('SPEECH_END_VISUAL_BREAKS',endbreaks)]:
            if sid in obj:
                before=copy.deepcopy(obj[sid]);obj[sid]=remap_ranges(obj[sid],old,new)
                remap_log.append({'stable_id':sid,'layer':name,'before':before,'after':obj[sid]})
        for k in ('local_breaks','cross_record_breaks','cross_record_joins'):
            if isinstance(topo.get(k),dict) and sid in topo[k]:
                before=copy.deepcopy(topo[k][sid]);topo[k][sid]=remap_ranges(topo[k][sid],old,new)
                remap_log.append({'stable_id':sid,'layer':'VISIBLE_PARAGRAPH_TOPOLOGY.'+k,'before':before,'after':topo[k][sid]})
    # Rebuild LDC library intra-paragraph flow offsets from final text for changed library records.
    flow_remaps=[]
    ti_after=tl_index(tl)
    for sid,(old,new) in affected_texts.items():
        if sid not in ti_after or old==new: continue
        item,idx=ti_after[sid]
        nums=item.get('body_stable_numbers') or []
        n=nums[idx] if idx<len(nums) else idx+1
        try:key=str(int(n))
        except:key=str(n)
        for ent in flow.get(item['id'],[]):
            intra=ent.get('intra',{})
            if key in intra:
                oldcuts=list(intra[key]); newcuts=[map_boundary(old,new,x) for x in oldcuts]
                intra[key]=newcuts
                acts=ent.get('intra_actions',{}).get(key)
                if isinstance(acts,dict):
                    ent['intra_actions'][key]={str(map_boundary(old,new,int(k))):v for k,v in acts.items()}
                flow_remaps.append({'stable_id':sid,'entry_id':ent.get('entry_id'),'old_cuts':oldcuts,'new_cuts':newcuts})
    # Current LDC authority is explicitly hybrid: inherited RA19B flow topology plus the bounded R5 sync.
    old_auth=copy.deepcopy(ldc_auth)
    ldc_auth={
      'authority_model':'BASE_FLOW_RA19B_PLUS_TARGETED_R5_SYNC',
      'base_flow_source_public_version':old_auth.get('source_public_version'),
      'base_flow_source_app_version':old_auth.get('source_app_version'),
      'base_flow_source_package_sha256':old_auth.get('source_package_sha256'),
      'base_flow_sync_date':old_auth.get('sync_date'),
      'base_flow_mapped_source_blocks':old_auth.get('mapped_source_blocks'),
      'base_flow_ra19b_changed_blocks_vs_ra18':old_auth.get('ra19b_changed_blocks_vs_ra18'),
      'base_flow_explicit_preserve_breaks':old_auth.get('explicit_preserve_breaks'),
      'base_flow_explicit_preserve_list_breaks':old_auth.get('explicit_preserve_list_breaks'),
      'base_flow_runtime_flow_overrides':old_auth.get('runtime_flow_overrides'),
      'targeted_successor_source_public_version':'62',
      'targeted_successor_source_app_version':'v2.19.62-R1B',
      'targeted_successor_align_generation':'G036-AFLP-R5-UWR2',
      'targeted_successor_enriched_generation':'G036-AFLP-R5-SUP-T4',
      'targeted_successor_package_sha256':LDC_ZIP_SHA,
      'targeted_successor_corpus_manifest_sha256':LDC_CORPUS_MANIFEST_SHA,
      'targeted_sync_date':BUILD_DATE,
      'targeted_operation_count':15,
      'targeted_scope':'ONLY_THE_15_GOVERNED_LINKED_CORRECTIONS; no claim of full 115-block reimport from v62'
    }
    # Add bounded sync provenance to affected library items without rewriting inherited whole-item provenance.
    op_by_item={}
    for cls,oid,sid,old,repl in [x for x in OPS if x[0]=='LDC_SYNC']:
        if sid in ti_after:
            item,_=ti_after[sid];op_by_item.setdefault(item['id'],[]).append(oid)
    for mr in mirror_rows:
        mid=mr['mirror_id']
        if mid in ti_after:
            item,_=ti_after[mid];op_by_item.setdefault(item['id'],[]).append(mr['operation_id'])
    for item in tl:
        if item['id'] in op_by_item:
            item['targeted_successor_sync']={
              'source_app_version':'v2.19.62-R1B','align_generation':'G036-AFLP-R5-UWR2','enriched_generation':'G036-AFLP-R5-SUP-T4',
              'operation_ids':sorted(set(op_by_item[item['id']])),
              'scope':'bounded corrected paragraphs/mirrors only; inherited item provenance remains base-flow lineage'
            }

    # Corpus fingerprint: current deterministic contract, explicitly declared.
    corpus['fingerprint_algorithm']='sha256_canonical_json_without_fingerprint_sha256_v101126'
    tmp={k:v for k,v in corpus.items() if k!='fingerprint_sha256'}
    corpus['fingerprint_sha256']=sha_bytes(jdump(tmp).encode('utf-8'))
    # Serialize governed declarations.
    for name,obj in [('CORPUS',corpus),('SPEECH_DATA',sd),('SPEECH_END_VISUAL_BREAKS',endbreaks),('SPEECH_PRESENTATION_ADJUDICATIONS',adj),('SPEECH_PRESENTATION_PROJECTION',proj),('VISIBLE_PARAGRAPH_TOPOLOGY',topo),('LDC_LIBRARY_FLOW_LAYOUT',flow),('LDC_CURRENT_SYNC_AUTHORITY',ldc_auth),('TEXT_LIBRARY',tl)]:
        text=replace_json_const(text,name,obj)
    # Identity only; data/storage schemas unchanged.
    for old,new in [
        ("const APP_VERSION = 'v101.125';",f"const APP_VERSION = '{VERSION}';"),
        ("const APP_EVIDENCE_STAGE = 'FOUR_PASS_EVIDENCE_SCHEMA_AND_DIRECT_REPORT_BINDING_RECONCILIATION_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';"),
        ("const BUILD_DATE = '2026-08-30'; // v101.125 / evidence-schema and direct-report-binding reconciliation R1",f"const BUILD_DATE = '{BUILD_DATE}'; // {VERSION} / governed 15 LDC synchronizations + 19 native repairs"),
    ]:
        assert text.count(old)==1,old;text=text.replace(old,new,1)
    return text,mutation_rows,mirror_rows,remap_log,flow_remaps,corpus['fingerprint_sha256'],affected_texts

def write_json(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write_csv(p,rows,fields=None):
    p.parent.mkdir(parents=True,exist_ok=True)
    if fields is None:fields=list(rows[0]) if rows else []
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def tree_files(root): return {p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file()}

def build(outdir):
    out=Path(outdir);shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
    assert sha_file(BASE_ZIP)==EXPECTED_BASE_SHA
    with zipfile.ZipFile(BASE_ZIP) as z:
        assert len([i for i in z.infolist() if not i.is_dir()])==EXPECTED_BASE_MEMBERS
        assert z.testzip() is None;z.extractall(out)
    base_hashes={rel:sha_file(p) for rel,p in tree_files(out).items()}
    src=(out/'index.html').read_text(encoding='utf-8');assert src==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
    new,rows,mirrors,remaps,flow_remaps,fp,affected=apply_html(src)
    (out/'index.html').write_text(new,encoding='utf-8');(out/'luisa_24_heures.html').write_text(new,encoding='utf-8')
    # Runtime identities.
    v=json.loads((out/'version.json').read_text(encoding='utf-8'))
    v.update({
      'app_version':VERSION,'build_date':BUILD_DATE,'cache_name':CACHE,
      'ldc_source_public_version':'62','ldc_source_app_version':'v2.19.62-R1B',
      'ldc_source_alignment_generation':'G036-AFLP-R5-UWR2','ldc_source_enriched_generation':'G036-AFLP-R5-SUP-T4',
      'ldc_source_package_sha256':LDC_ZIP_SHA,'ldc_source_corpus_manifest_sha256':LDC_CORPUS_MANIFEST_SHA,
      'release_scope':'Governed dual-successor content successor of immutable v101.125. Applies exactly 15 LDC-governed synchronizations from the frozen R5/v62 successor and 19 authority-completed native 24H/prayer repairs. Rebuilds affected speech/presentation/topology offsets, corpus fingerprint, PWA/version bindings, manifests and evidence. Storage schema, personal snapshot schema, navigation/product behaviour and unrelated corpus text remain unchanged.',
      'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA, true offline cold reopen, VoiceOver/TalkBack and live GitHub Pages exact-byte binding NOT_TESTED for v101.126.',
      'overall_release_status':'LIMITED_PASS_STATIC_PENDING_FINAL_REOPEN_AUDIT',
      'known_blockers':[],
      'external_open_gates':['physical iPad/iPhone/Samsung','live GitHub Pages exact-byte binding','installed PWA update','true offline cold reopen','VoiceOver/TalkBack representative testing']
    })
    # Remove misleading legacy keyed flow field if present; preserve nothing stale as current.
    v.pop('ldc_ra19b_corpus_flow_sha256',None)
    write_json(out/'version.json',v)
    m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));m['version']=VERSION;write_json(out/'manifest.json',m)
    sw=(out/'sw.js').read_text(encoding='utf-8')
    assert sw.startswith('/* v101.125 */') and "const CACHE_NAME = 'luisa-24h-v101-125';" in sw
    sw=sw.replace('/* v101.125 */','/* v101.126 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-125';",f"const CACHE_NAME = '{CACHE}';",1)
    (out/'sw.js').write_text(sw,encoding='utf-8')
    # Current evidence and concise current report.
    ev=out/'evidence'/'v101126';ev.mkdir(parents=True,exist_ok=True)
    write_csv(ev/'APPLY_LEDGER_34.csv',rows)
    write_csv(ev/'GOVERNED_MIRROR_REBUILD_LEDGER.csv',mirrors)
    write_json(ev/'PREAPPLY_BINDING.json',{
      'schema':'L24H_V101126_PREAPPLY_BINDING_V1','version':VERSION,'stage':STAGE,
      'predecessor':{'version':'v101.125','zip_sha256':EXPECTED_BASE_SHA,'members':EXPECTED_BASE_MEMBERS},
      'governed_ldc':{'version':'v2.19.62-R1B','zip_sha256':LDC_ZIP_SHA,'align_generation':'G036-AFLP-R5-UWR2','enriched_generation':'G036-AFLP-R5-SUP-T4','corpus_manifest_sha256':LDC_CORPUS_MANIFEST_SHA},
      'operation_universe':{'total':34,'ldc_sync':15,'native_24h_prayer':19,'unique_primary_stable_ids':len(set(r['stable_id'] for r in rows))},
      'op_l17_109_01':'NO_EDIT_CONTROL_OUTSIDE_34_UNCHANGED_REQUIRED',
      'op_l17_218_01':'FORMALLY_REOPENED_AND_PROMOTED_TO_LDC_UPSTREAM_THEN_24H_SYNC'
    })
    write_json(ev/'DERIVED_LAYER_REBUILD.json',{
      'schema':'L24H_V101126_DERIVED_REBUILD_V1','version':VERSION,'stage':STAGE,
      'changed_stable_text_records':sorted(affected),
      'speech_presentation_topology_remaps':remaps,
      'ldc_library_flow_offset_remaps':flow_remaps,
      'search':'RUNTIME_DERIVED_FROM_FINAL_CORPUS_AND_TEXT_LIBRARY_NO_SERIALIZED_INDEX',
      'corpus_fingerprint_sha256':fp,
      'corpus_fingerprint_algorithm':'sha256_canonical_json_without_fingerprint_sha256_v101126',
      'storage_schema':8,'personal_snapshot':5,
      'highlight_reanchor':'EXISTING_v101.48_SELECTED_TEXT_SNAPSHOT_RECOVERY_PRESERVED; stable paragraph ids unchanged'
    })
    report=f'''# v101.126 Governed Dual-Successor Mutation Report\n\n- Predecessor: `v101.125` / `{EXPECTED_BASE_SHA}` / 428 members.\n- Governed LDC source: `v2.19.62-R1B`, ALIGNÉ `G036-AFLP-R5-UWR2`, ENRICHI `G036-AFLP-R5-SUP-T4`, ZIP `{LDC_ZIP_SHA}`.\n- Mutation universe: **34** = **15 LDC-governed synchronizations + 19 native 24H/prayer repairs**.\n- Unique primary stable records changed: **{len(set(r['stable_id'] for r in rows))}**.\n- `OP-L17-109-01` remains a no-edit control outside the 34-operation apply universe.\n- `OP-L17-218-01` is synchronized as `nausée S’il prend` → `nausée. S’il prend` after formal authority reopen.\n- Governed Benefits mirrors/aggregate were rebuilt; all affected serialized speech/presentation/topology offsets were remapped from final text.\n- Storage schema remains 8 and personal snapshot schema remains 5; stable paragraph IDs are unchanged. Existing selected-text snapshot recovery remains the migration mechanism for highlights affected by editorial text changes.\n- Physical devices, installed-PWA update, true offline cold reopen, accessibility screen readers and live GitHub Pages exact-byte binding remain external/not tested here.\n'''
    (out/'reports'/'DUAL_SUCCESSOR_MUTATION_REPORT.md').write_text(report,encoding='utf-8')
    # Current metadata. Historical/current predecessor evidence remains present but is no longer current active evidence.
    write_json(out/'metadata'/'active_report_inventory.json',{'version':VERSION,'stage':STAGE,'source_reports':['reports/DUAL_SUCCESSOR_MUTATION_REPORT.md'],'historical_reports_root':'reports/historical/','rule':'Only the listed report is current for v101.126; predecessor reports/evidence remain historical lineage.'})
    write_json(out/'metadata'/'current_evidence_lineage.json',{'version':VERSION,'stage':STAGE,'current_evidence_root':'evidence/v101126','governed_ldc_source':{'version':'v2.19.62-R1B','sha256':LDC_ZIP_SHA},'predecessor_24h':{'version':'v101.125','sha256':EXPECTED_BASE_SHA},'rule':'v101.125 and earlier evidence is retained as predecessor/historical evidence and must not be interpreted as current v101.126 execution evidence.'})
    write_json(out/'metadata'/'build_provenance.json',{'version':VERSION,'stage':STAGE,'build_date':BUILD_DATE,'baseline_version':'v101.125','baseline_zip_sha256':EXPECTED_BASE_SHA,'baseline_html_sha256':sha_bytes(src.encode()),'candidate_html_sha256':sha_bytes(new.encode()),'mutation_scope':'exact 34-operation governed universe: 15 LDC sync + 19 native 24H/prayer','canonical_text_changed':True,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'governed_ldc_zip_sha256':LDC_ZIP_SHA,'final_reopen_evidence':'EXTERNAL_AFTER_IMMUTABLE_ZIP_FREEZE'})
    write_json(out/'metadata'/'release_evidence_lifecycle.json',{'version':VERSION,'stage':STAGE,'prefreeze_package_reports':'current package report may claim only directly executed static/build facts','postfreeze_final_reopen_reports':'external only','physical_device_claims':'NOT_TESTED until direct evidence','immutable_package_rule':'do not insert postfreeze PASS reports into frozen ZIP','current_evidence_rule':'evidence/v101126 is current; older evidence is predecessor/historical lineage','active_report_rule':'current active report claims must bind directly to evidence/v101126 or current package bytes'})
    # Add this build script as current reproducibility tooling.
    tool_dst=out/'scripts'/'build_v101126_dual_successor_mutations.py';tool_dst.write_bytes(Path(__file__).read_bytes())
    write_json(out/'metadata'/'current_tooling_inventory.json',{'version':VERSION,'stage':STAGE,'current_tools':['scripts/build_v101126_dual_successor_mutations.py'],'reused_validated_runtime_lineage':['existing v101.125 runtime/search/highlight/PWA infrastructure except governed data/identity rebuild'],'historical_or_superseded_tools':['scripts/build_v101125_full_package_reconciliation.py']})
    scope=(out/'metadata'/'scope_escalation_authority.md')
    scope.write_text(f'''# v101.126 Scope Authority\n\nCurrent authorised mutation scope is exactly 34 operations: 15 governed LDC synchronizations from v2.19.62-R1B/R5 plus 19 native 24H/prayer repairs. No other canonical text mutation is authorised. `OP-L17-109-01` is a mandatory no-edit control. Any further content change requires a new governed authority decision.\n''',encoding='utf-8')
    readme=f'''# Les 24 Heures de la Passion — {VERSION}\n\nGoverned content successor of immutable v101.125.\n\n## Current bounded mutation\n\n- 15 synchronizations from governed LDC v2.19.62-R1B / G036-AFLP-R5-UWR2 / G036-AFLP-R5-SUP-T4.\n- 19 authority-completed native 24H/prayer repairs.\n- Total authorised operation universe: 34.\n- Stable paragraph IDs and personal-data schemas are preserved.\n\n## Validation boundary\n\nThis package is eligible only for static/package/reopen validation in this workflow. Physical iPhone/iPad/Samsung, installed-PWA update, true offline cold reopen, accessibility screen readers and live GitHub Pages exact-byte binding remain external gates.\n'''
    (out/'README.md').write_text(readme,encoding='utf-8')
    # Full-build overlay relative to immutable v101.125; manifests are known changed too.
    current=tree_files(out);changed=sorted(rel for rel,p in current.items() if rel not in base_hashes or sha_file(p)!=base_hashes[rel])
    removed=sorted(set(base_hashes)-set(current))
    for rel in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
        if rel not in changed:changed.append(rel)
    changed=sorted(set(changed))
    write_json(out/'metadata'/'full_build_overlay_manifest.json',{'schema':'L24H_V101126_FULL_BUILD_OVERLAY_V1','version':VERSION,'stage':STAGE,'baseline_version':'v101.125','baseline_zip_sha256':EXPECTED_BASE_SHA,'changed_or_added':changed,'removed':removed})
    # Recompute package/hash manifests, both self-excluded.
    exclusions=['metadata/hash_manifest.json','metadata/package_manifest.json']
    files=[]
    for rel,p in sorted(tree_files(out).items()):
        if rel in exclusions:continue
        files.append({'path':rel,'size':p.stat().st_size,'sha256':sha_file(p)})
    hm={'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':exclusions,'file_count':len(files),'files':files}
    pm={'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':exclusions,'file_count':len(files),'files':[{'path':x['path'],'size':x['size']} for x in files]}
    write_json(out/'metadata'/'hash_manifest.json',hm);write_json(out/'metadata'/'package_manifest.json',pm)
    return {'version':VERSION,'stage':STAGE,'html_sha256':sha_file(out/'index.html'),'corpus_fingerprint_sha256':fp,'operations':len(rows),'unique_primary_ids':len(set(r['stable_id'] for r in rows)),'mirrors_or_aggregates':len(mirrors),'speech_topology_remaps':len(remaps),'ldc_flow_remaps':len(flow_remaps),'file_count':len(tree_files(out))}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: build_l24h_v101126.py OUTDIR')
    print(json.dumps(build(sys.argv[1]),ensure_ascii=False,indent=2))
