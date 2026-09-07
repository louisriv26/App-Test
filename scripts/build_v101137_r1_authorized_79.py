from pathlib import Path
import csv, json, hashlib, zipfile, shutil, re, copy, difflib, sys

BASE_SHA='7ef830738ff5665ae5b880d52bde029e4b9ba092d834f81b008d24615e1ab9e7'
LEDGER_SHA='f9a9c4c74df33b3f96909e3611acb74c448deed5fa367fa86072d2e27cbfef49'
ITALIAN_R3_SHA='bab1e4de16137577c9a100127509ff307b0532f13ad545bb9b6a61e7141041b8'
R4_SHA='2534e383966d60b462c81ab3a48143a916b2141cdc732fca9450e26b9157afe6'
VERSION='v101.137'; REV='R1'; DATE='2026-09-08'; CACHE='luisa-24h-v101-137-r1'
STAGE='AUTHORIZED_79_MEDITATION_REFLECTION_SUCCESSOR_R1'


def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def jdump(o): return json.dumps(o,ensure_ascii=False,separators=(',',':'))
def writej(p,o):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def files(root): return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}

def extract(t,n):
    m=re.search(rf'const\s+{re.escape(n)}\s*=\s*',t); assert m,n
    o,e=json.JSONDecoder().raw_decode(t[m.end():]); return o,m.end(),m.end()+e

def repl(t,n,o):
    _,s,e=extract(t,n);return t[:s]+jdump(o)+t[e:]

def canonical_records(c):
    d={}
    loc={}
    for hi,h in enumerate(c['hours']):
        for k in ('paragraphs','reflections'):
            for pi,p in enumerate(h.get(k,[])):
                assert p['id'] not in d,p['id'];d[p['id']]=p;loc[p['id']]=('hours',hi,k,pi)
        for si,sub in enumerate(h.get('subsections',[])):
            for pi,p in enumerate(sub.get('paragraphs',[])):
                assert p['id'] not in d,p['id'];d[p['id']]=p;loc[p['id']]=('hours',hi,'subsections',si,pi)
    for pri,pr in enumerate(c.get('prayers',[])):
        for pi,p in enumerate(pr.get('paragraphs',[])):
            assert p['id'] not in d,p['id'];d[p['id']]=p;loc[p['id']]=('prayers',pri,'paragraphs',pi)
    for sei,sec in enumerate(c.get('sections',[])):
        for pi,p in enumerate(sec.get('paragraphs',[])):
            assert p['id'] not in d,p['id'];d[p['id']]=p;loc[p['id']]=('sections',sei,'paragraphs',pi)
    return d,loc

def hour_layer_records(c):
    d={}
    for h in c['hours']:
        for k in ('paragraphs','reflections'):
            for p in h.get(k,[]): d[p['id']]=p['t']
        for sub in h.get('subsections',[]):
            for p in sub.get('paragraphs',[]): d[p['id']]=p['t']
    return d

def hour_original_locations(c):
    loc={}
    for h in c['hours']:
        for k in ('paragraphs','reflections'):
            for i,p in enumerate(h.get(k,[])):
                loc[p['id']]={'hour':h['hour_number'],'container':k,'subsection_id':None,'index':i}
        for sub in h.get('subsections',[]):
            for i,p in enumerate(sub.get('paragraphs',[])):
                loc[p['id']]={'hour':h['hour_number'],'container':'subsections','subsection_id':sub.get('id') or sub.get('subsection_id'),'index':i}
    return loc

def remove_record(c,sid):
    for h in c['hours']:
        for k in ('paragraphs','reflections'):
            a=h.get(k,[])
            for i,p in enumerate(a):
                if p['id']==sid:
                    obj=copy.deepcopy(p); del a[i]
                    return obj, {'hour':h['hour_number'],'container':k,'subsection_id':None,'index':i}
        for sub in h.get('subsections',[]):
            a=sub.get('paragraphs',[])
            for i,p in enumerate(a):
                if p['id']==sid:
                    obj=copy.deepcopy(p); del a[i]
                    return obj, {'hour':h['hour_number'],'container':'subsections','subsection_id':sub.get('id') or sub.get('subsection_id'),'index':i}
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
            if k in ('start','end') and isinstance(v,int): d[k]=mb(old,new,v)
            elif k=='breaks' and isinstance(v,list): d[k]=[mb(old,new,x) for x in v]
            else:d[k]=remap(v,old,new)
        return d
    return o

def removed_span(old,new):
    sm=difflib.SequenceMatcher(None,old,new,autojunk=False)
    out=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag in ('delete','replace') and i2>i1: out.append(old[i1:i2])
    return ''.join(out)

def validate_derived_offsets(text_by_id, O):
    errs=[]
    def walk_ranges(x,L,path):
        if isinstance(x,dict):
            if isinstance(x.get('start'),int) and isinstance(x.get('end'),int):
                if not (0 <= x['start'] <= x['end'] <= L): errs.append((path,x['start'],x['end'],L))
            for k,v in x.items(): walk_ranges(v,L,path+'.'+str(k))
        elif isinstance(x,list):
            for i,v in enumerate(x): walk_ranges(v,L,path+f'[{i}]')
    for n in ['SPEECH_DATA','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS']:
        obj=O[n]
        if isinstance(obj,dict):
            for sid,val in obj.items():
                if sid in text_by_id: walk_ranges(val,len(text_by_id[sid]),n+'.'+sid)
    for n in ['SPEECH_END_VISUAL_BREAKS']:
        obj=O[n]
        for sid,vals in obj.items():
            if sid in text_by_id:
                L=len(text_by_id[sid])
                for x in vals:
                    if not (0 < x < L): errs.append((n+'.'+sid,x,L))
    for sid,vals in O['VISIBLE_PARAGRAPH_TOPOLOGY'].get('local_breaks',{}).items():
        if sid in text_by_id:
            L=len(text_by_id[sid])
            for x in vals:
                if not (0 < x < L): errs.append(('VPT.'+sid,x,L))
    assert not errs, errs[:20]


def build(base_zip,ledger_csv,out):
    base_zip=Path(base_zip);ledger_csv=Path(ledger_csv);out=Path(out)
    assert sha_file(base_zip)==BASE_SHA,(sha_file(base_zip),BASE_SHA)
    assert sha_file(ledger_csv)==LEDGER_SHA,(sha_file(ledger_csv),LEDGER_SHA)
    shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
    with zipfile.ZipFile(base_zip) as z:
        assert z.testzip() is None;z.extractall(out)
    basehash={k:sha_file(p) for k,p in files(out).items()}
    src=(out/'index.html').read_text(encoding='utf-8'); assert src==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
    C,_,_=extract(src,'CORPUS'); C0=copy.deepcopy(C)
    base_hour_text=hour_layer_records(C0)
    base_hour_locations=hour_original_locations(C0)
    rows=list(csv.DictReader(ledger_csv.open(encoding='utf-8-sig')))
    assert len(rows)==79 and len({r['candidate_id'] for r in rows})==79 and len({r['r5_record_id'] for r in rows})==79
    from collections import Counter
    assert Counter(r['final_operation'] for r in rows)==Counter({'REPLACE_RECORD':41,'TRIM_RECORD':12,'MOVE_OUT_OF_CANONICAL_LAYER':24,'DELETE_FROM_CANONICAL_LAYER':2})
    cm,_=canonical_records(C)
    for r in rows:
        sid=r['r5_record_id']; assert sid in cm,(r['candidate_id'],sid); assert cm[sid]['t']==r['current_text'],(r['candidate_id'],'CURRENT_TEXT_MISMATCH')
    names=['SPEECH_DATA','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY','DISPLAY_SEGMENTS']
    O={n:extract(src,n)[0] for n in names}
    affected_text={}; applied=[]; preserved=[]; trimmed=[]; deleted=[]
    # Text replacements/trims first.
    cm,_=canonical_records(C)
    for r in rows:
        sid=r['r5_record_id']; op=r['final_operation']; old=cm[sid]['t']
        if op in ('REPLACE_RECORD','TRIM_RECORD'):
            new=r['final_proposed_french']; assert new and new!='∅' and new!=old
            cm[sid]['t']=new; affected_text[sid]=(old,new)
            if op=='TRIM_RECORD':
                trimmed.append({'candidate_id':r['candidate_id'],'record_id':sid,'hour':int(r['hour']),'layer':r['layer'],'original_text':old,'canonical_text_after_trim':new,'removed_or_replaced_span':removed_span(old,new),'preservation_requirement':r['preservation_requirement'],'aflp27_evidence':r['aflp27_evidence']})
            applied.append({'candidate_id':r['candidate_id'],'record_id':sid,'operation':op,'pre_sha256':sha_bytes(old.encode()),'post_sha256':sha_bytes(new.encode()),'status':'APPLIED_EXACT_AUTHORIZED_TEXT_OPERATION'})
    # Remap offset-bearing derived presentation metadata for the 53 changed texts.
    remap_log=[]
    for sid,(old,new) in affected_text.items():
        for n in ['SPEECH_DATA','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS']:
            obj=O[n]
            if isinstance(obj,dict) and sid in obj:
                b=copy.deepcopy(obj[sid]);obj[sid]=remap(obj[sid],old,new);remap_log.append({'record_id':sid,'layer':n,'before':b,'after':obj[sid]})
        topo=O['VISIBLE_PARAGRAPH_TOPOLOGY']
        if sid in topo.get('local_breaks',{}):
            b=copy.deepcopy(topo['local_breaks'][sid]);topo['local_breaks'][sid]=remap(topo['local_breaks'][sid],old,new);remap_log.append({'record_id':sid,'layer':'VISIBLE_PARAGRAPH_TOPOLOGY.local_breaks','before':b,'after':topo['local_breaks'][sid]})
        L=len(new)
        if sid in O['SPEECH_END_VISUAL_BREAKS']:
            O['SPEECH_END_VISUAL_BREAKS'][sid]=sorted(set(x for x in O['SPEECH_END_VISUAL_BREAKS'][sid] if isinstance(x,int) and 0<x<L))
            if not O['SPEECH_END_VISUAL_BREAKS'][sid]: O['SPEECH_END_VISUAL_BREAKS'].pop(sid,None)
        if sid in O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS']:
            q=[x for x in O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS'][sid] if x.get('end',0)>x.get('start',0) and x.get('end',0)<=L]
            if q: O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS'][sid]=q
            else: O['SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS'].pop(sid,None)
        if sid in O['SPEECH_PRESENTATION_PROJECTION']:
            q=O['SPEECH_PRESENTATION_PROJECTION'][sid]
            q['hidden']=[x for x in q.get('hidden',[]) if x.get('end',0)>x.get('start',0) and x.get('end',0)<=L]
            q['breaks']=sorted(set(x for x in q.get('breaks',[]) if isinstance(x,int) and 0<x<L))
        if sid in topo.get('local_breaks',{}):
            topo['local_breaks'][sid]=sorted(set(x for x in topo['local_breaks'][sid] if isinstance(x,int) and 0<x<L))
            if not topo['local_breaks'][sid]: topo['local_breaks'].pop(sid,None)
    # Move/delete exactly the authorized 26 records. Preserve MOVE bytes in evidence only, not UI/runtime.
    for r in rows:
        sid=r['r5_record_id'];op=r['final_operation']
        if op not in ('MOVE_OUT_OF_CANONICAL_LAYER','DELETE_FROM_CANONICAL_LAYER'): continue
        obj,_shifted_loc=remove_record(C,sid)
        loc=copy.deepcopy(base_hour_locations[sid])
        assert obj['t']==r['current_text']
        entry={'candidate_id':r['candidate_id'],'record_id':sid,'hour':int(r['hour']),'layer':r['layer'],'original_record':obj,'original_location':loc,'classification':r['classification'],'decision_basis':r['decision_basis'],'aflp27_status':r['aflp27_status'],'aflp27_evidence':r['aflp27_evidence'],'preservation_requirement':r['preservation_requirement']}
        if op=='MOVE_OUT_OF_CANONICAL_LAYER':
            entry['successor_visibility']='PRESERVED_IN_PACKAGE_EVIDENCE_ONLY__NOT_RENDERED_IN_V101137_R1'
            entry['future_ui_disposition']='DEFERRED_TO_LATER_VERSION_BY_USER_DECISION_2026_09_08'
            preserved.append(entry)
        else:
            entry['successor_visibility']='REMOVED_FROM_CANONICAL_LAYER_PER_EXACT_AUTHORIZATION'
            deleted.append(entry)
        applied.append({'candidate_id':r['candidate_id'],'record_id':sid,'operation':op,'pre_sha256':sha_bytes(obj['t'].encode()),'post_sha256':None,'status':'APPLIED_EXACT_AUTHORIZED_STRUCTURAL_OPERATION'})
        # Prune derived presentation entries for records no longer rendered.
        for n in ['SPEECH_DATA','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS']:
            if isinstance(O[n],dict): O[n].pop(sid,None)
        O['VISIBLE_PARAGRAPH_TOPOLOGY'].get('local_breaks',{}).pop(sid,None)
        for k in ('cross_record_breaks','cross_record_joins'):
            if isinstance(O['VISIBLE_PARAGRAPH_TOPOLOGY'].get(k),list):
                O['VISIBLE_PARAGRAPH_TOPOLOGY'][k]=[pair for pair in O['VISIBLE_PARAGRAPH_TOPOLOGY'][k] if sid not in pair]
    assert len(preserved)==24 and len(deleted)==2 and len(trimmed)==12 and len(applied)==79
    # Corpus fingerprint after exact authorized canonical operations.
    C['fingerprint_algorithm']='sha256_canonical_json_without_fingerprint_sha256_v101137'
    tmp={k:v for k,v in C.items() if k!='fingerprint_sha256'}
    C['fingerprint_sha256']=sha_bytes(jdump(tmp).encode('utf-8'))
    t=src
    for n,o in [('CORPUS',C)]+[(n,O[n]) for n in names]: t=repl(t,n,o)
    old="const APP_VERSION = 'v101.136';";assert t.count(old)==1;t=t.replace(old,f"const APP_VERSION = '{VERSION}';",1)
    old="const APP_EVIDENCE_STAGE = 'INTERIM_CLOSED_97_SUCCESSOR_R5_FOUR_PASS_RELEASE_RECONCILED';";assert t.count(old)==1;t=t.replace(old,f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
    t=re.sub(r"const BUILD_DATE = '2026-09-07';[^\n]*",f"const BUILD_DATE = '{DATE}'; // {VERSION} {REV} / exact authorized 79-row meditation-reflection successor",t,count=1)
    (out/'index.html').write_text(t,encoding='utf-8');(out/'luisa_24_heures.html').write_text(t,encoding='utf-8')
    # Version/cache identity. Public version bump is required for the existing update checker to detect successor.
    sw=(out/'sw.js').read_text(encoding='utf-8')
    assert "const CACHE_NAME = 'luisa-24h-v101-136-r5';" in sw
    sw=sw.replace('/* v101.136 R5 */','/* v101.137 R1 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-136-r5';",f"const CACHE_NAME = '{CACHE}';",1)
    (out/'sw.js').write_text(sw,encoding='utf-8')
    v=json.loads((out/'version.json').read_text(encoding='utf-8'))
    gates=['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update v101.136 R5→v101.137 R1','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing']
    v.update({'app_version':VERSION,'build_revision':REV,'build_date':DATE,'cache_name':CACHE,
      'release_scope':'Authorized meditation/reflection source-alignment successor of immutable v101.136 R5. Applies exactly the hash-bound 79-row universe: 41 replacements + 12 trims + 24 preserve-moves + 2 canonical deletions. PRESERVE_MOVE material is retained in package evidence only and intentionally not exposed in the v101.137 R1 UI; future user-facing placement is deferred. Deferred/recension-sensitive loci remain unchanged; H23 A/B synthesis is forbidden; H24 burial placement is unchanged; Desolation remains within H24 meditation scope.',
      'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.137 R1.',
      'overall_release_status':'R1_CONTROLLED_DEVICE_TEST_CANDIDATE__FINAL_PUBLIC_DEPLOYMENT_UNAUTHORIZED','known_blockers':gates,'external_open_gates':gates,
      'postfreeze_reopen_evidence':'Exact successor ZIP requires external SHA-bound final recheck before controlled device testing.'})
    writej(out/'version.json',v)
    m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));m['version']=VERSION;m['build_revision']=REV;writej(out/'manifest.json',m)
    # Evidence and authorization artifacts.
    ev=out/'evidence/v101137_r1';ev.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ledger_csv,ev/'AUTHORIZED_MUTATION_UNIVERSE_79.csv')
    # Copy exact user gate artifact generated preauthorization.
    auth_src=ledger_csv.parent/'FINAL_AUTHORIZATION_STATEMENT.md'
    if auth_src.exists(): shutil.copy2(auth_src,ev/'PREAUTHORIZATION_GATE_STATEMENT.md')
    with (ev/'APPLY_LEDGER_79.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['candidate_id','record_id','operation','pre_sha256','post_sha256','status']);w.writeheader();w.writerows(applied)
    writej(ev/'PRESERVE_MOVE_ARCHIVE_24.json',{'schema':'L24H_V101137_R1_PRESERVE_MOVE_ARCHIVE_V1','count':24,'visibility_policy':'PACKAGE_EVIDENCE_ONLY__NOT_USER_VISIBLE_IN_THIS_VERSION','user_decision':'Keep a record now; user-facing placement may be implemented in a later version.','records':preserved})
    writej(ev/'TRIMMED_PARATEXT_ARCHIVE_12.json',{'schema':'L24H_V101137_R1_TRIMMED_PARATEXT_ARCHIVE_V1','count':12,'purpose':'Preserve evidence of removed/non-core spans without exposing a new UI layer in this version.','records':trimmed})
    writej(ev/'CANONICAL_DELETE_RECEIPT_2.json',{'schema':'L24H_V101137_R1_CANONICAL_DELETE_RECEIPT_V1','count':2,'records':deleted})
    writej(ev/'DERIVED_PRESENTATION_REMAP.json',{'schema':'L24H_V101137_R1_DERIVED_PRESENTATION_REMAP_V1','text_changed_records':53,'remap_actions':remap_log,'removed_runtime_records':26,'rule':'Only offsets for authorized changed texts were remapped; derived entries for authorized removed canonical records were pruned.'})
    (ev/'USER_AUTHORIZATION_2026-09-08.md').write_text('''# User authorization — 2026-09-08\n\nThe user explicitly authorized the exact 79-row mutation universe in `FINAL_AUTHORIZATION_READY_LEDGER.csv`, SHA-256 `f9a9c4c74df33b3f96909e3611acb74c448deed5fa367fa86072d2e27cbfef49`, and no other textual mutation, starting only from immutable v101.136 R5 SHA-256 `7ef830738ff5665ae5b880d52bde029e4b9ba092d834f81b008d24615e1ab9e7`.\n\nAuthorized safeguards: preserve all `PRESERVE_MOVE` material outside the canonical layer; leave all deferred/recension-sensitive loci unchanged; do not synthesize H23 Forms A and B; do not move the H24 burial/deposition block; keep the Desolation of Mary within H24 meditation scope.\n\n## Subsequent implementation clarification\n\nFor this version, the user explicitly decided **not** to create a new visible destination for the 24 `PRESERVE_MOVE` records because that would complicate the release. Keep a record of them now, but they do **not** need to be visible in the app at this stage. User-facing placement is deferred to a later version.\n''',encoding='utf-8')
    writej(ev/'AUTHORIZATION_RECEIPT.json',{'schema':'L24H_V101137_R1_AUTHORIZATION_RECEIPT_V1','authorization_date':DATE,'predecessor_version':'v101.136 R5','predecessor_sha256':BASE_SHA,'authorized_ledger_sha256':LEDGER_SHA,'italian_r3_authority_sha256':ITALIAN_R3_SHA,'frozen_r4_authority_sha256':R4_SHA,'authorized_rows':79,'operations':{'REPLACE_RECORD':41,'TRIM_RECORD':12,'MOVE_OUT_OF_CANONICAL_LAYER':24,'DELETE_FROM_CANONICAL_LAYER':2},'preserve_move_visibility':'EVIDENCE_ONLY_NOT_UI_THIS_VERSION','deferred_recension_loci_changed':False,'h23_ab_synthesis':False,'h24_burial_block_moved':False,'h24_desolation_in_scope':True})
    # Report and active metadata.
    hist=out/'reports/historical/v101136_r5';hist.mkdir(parents=True,exist_ok=True)
    oldrep=out/'reports/V101136_R5_FOUR_PASS_RELEASE_RECONCILIATION.md'
    if oldrep.exists(): shutil.move(str(oldrep),str(hist/oldrep.name))
    report=out/'reports/V101137_R1_AUTHORIZED_79_MUTATION.md'
    report.write_text(f'''# v101.137 R1 — Authorized 79-row meditation/reflection successor\n\n- Immutable predecessor: v101.136 R5 `{BASE_SHA}`.\n- Exact authorization ledger: `{LEDGER_SHA}`.\n- Applied universe: **79/79** = 41 `REPLACE_RECORD` + 12 `TRIM_RECORD` + 24 `MOVE_OUT_OF_CANONICAL_LAYER` + 2 `DELETE_FROM_CANONICAL_LAYER`.\n- The 24 preserve-move records are retained byte-for-byte in `evidence/v101137_r1/PRESERVE_MOVE_ARCHIVE_24.json` and are **not user-visible in this version**, by explicit user decision. Their later UI placement is deferred.\n- Trimmed non-core spans are retained in `TRIMMED_PARATEXT_ARCHIVE_12.json`.\n- Deferred/recension-sensitive loci are unchanged. H23 Forms A/B are not synthesized. H24 burial/deposition placement is unchanged. Desolation remains inside H24 meditation scope.\n- Public app version advances to **v101.137** so the existing in-app update checker can detect the successor from v101.136. Cache generation is `{CACHE}`.\n- Stable IDs of retained canonical records are unchanged. No storage or personal-snapshot schema change is introduced.\n- Final public deployment remains unauthorized until the exact frozen ZIP has passed package/runtime checks and controlled real-device testing.\n''',encoding='utf-8')
    (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — v101.137 R1\n\nControlled device-test candidate built only from immutable v101.136 R5 SHA-256 `{BASE_SHA}` and exact authorized 79-row ledger SHA-256 `{LEDGER_SHA}`.\n\nThe canonical meditation/reflection corpus applies exactly 79 authorized operations. The 24 preserve-move records are retained in package evidence for later use but are intentionally not displayed in the current UI. No deferred/recension-sensitive locus is moved or changed beyond the exact authorized text-only rows.\n\nFinal public deployment remains unauthorized pending exact-package validation and controlled device/PWA/offline/accessibility checks.\n''',encoding='utf-8')
    # Current real-device QA instructions for this successor. Write explicitly rather than
    # mechanically replacing predecessor strings, because update origin and targeted controls changed.
    q=out/'REAL_DEVICE_QA_CHECKLIST.md'
    q.write_text("""# Real-device QA checklist — v101.137 R1

Use only the exact **v101.137 R1** controlled device-test candidate whose SHA-256 is supplied in the external final-validation receipt.

Package identity to verify before testing:
- `app_version = v101.137`
- `build_revision = R1`
- `cache_name = luisa-24h-v101-137-r1`
- `APP_EVIDENCE_STAGE = AUTHORIZED_79_MEDITATION_REFLECTION_SUCCESSOR_R1`

The immutable update predecessor for this test is **v101.136 R5**. Do not substitute v101.135 or an earlier v101.136 revision when testing the in-place update path.

## A. Live-origin binding immediately after test deployment
- Confirm the deployed ZIP SHA-256 matches the external **v101.137 R1** final-validation receipt.
- Open the site normally and confirm **v101.137** in Aide / À propos.
- Confirm `version.json` reports `app_version = v101.137`, `build_revision = R1`, and `cache_name = luisa-24h-v101-137-r1`.
- Hard refresh once and confirm the same identity.
- Confirm no blank/stuck/bootstrap screen.

## B. Existing-PWA update — mandatory
Test an installation currently running **v101.136 R5**; do not uninstall first.
- Before update record: at least one Heure méditée, one note, one highlight, one favourite/library mark if used, last reading position, theme and font size.
- Open installed v101.136 R5 online and trigger/allow the normal update.
- Confirm it becomes **v101.137 / R1**.
- Close completely and reopen **three times**.
- Confirm no fallback to v101.136 R5 or an older cache, blank screen, or repair loop.
- Confirm all pre-existing user data and last-place state remain coherent.

## C. Core functional smoke on each physical device
Run on iPhone, iPad portrait, iPad landscape, and Samsung/Android. On each:
- home renders/scrolls; all 24 Heures open; search works; Mon Espace opens; Aide opens;
- light/dark theme and normal/large font work;
- Méditée top/bottom controls remain synchronized;
- notes/highlights can be created and persist after close/reopen;
- no horizontal clipping/overflow; back navigation and last-place restore work.

## D. Targeted v101.137 R1 corpus controls
These are representative physical-device checks of the newly authorized 79-row universe; the package validator separately checks all 79 rows exactly.
- H1: the first meditation includes `Afflictions, tes Affections et tes Réparations`; the standalone final `Gloire au Père,…` record is absent.
- H7 reflection: `Terminer par la prière de remerciement de l’Heure Sainte.` is not displayed as reflection prose in this version.
- H15: the authorized angel-defense wording is visible; the moved body-part devotional expansion is not displayed.
- H16: the moved body-part flagellation-prayer block is not displayed.
- H18 reflection: the corrected sentence ends `afin qu’elles soient comme un voile qui essuie ses Sueurs et Le réconforte` without malformed syntax.
- H19 reflection: it ends before the documentary letters; the ten moved documentary records are not displayed in the reflection.
- H20 meditation: the Psalm 116 / `Gloire au Père` insertion is absent from canonical meditation prose.
- H23: representative corrected wording includes `Défends-Moi, fais-Moi réparation, conduis-les tous dans mon Cœur`; no Form-A/Form-B synthesis is visible.
- H24: the burial/deposition block is still located in H24; the authorized burial wording corrections render normally; Desolation remains present; the leading duplicate Desolation sentence and final Latin Marian paratext are not displayed.

## E. Inherited regression controls from v101.136 R5
- H19 P118 repaired French sentence: no truncation/garbling.
- H22 authorized quote/punctuation loci: no stale period after the closing guillemet where v101.136 removed it.
- `RELATED_HOUR_06.P013`: paragraph flow normal; historical breaks preserved.
- `RELATED_HOUR_16.P038`: no break splitting the word `en`.
- `RELATED_HOUR_04.P127`: remapped break visually natural.
- H24 end-of-cycle panel, Méditée toggle and restart behaviour correct.
- Tome 20 — 25 décembre 1926 linked text: verify `à la porte de leur cœur` (with `de`).

## F. Offline gate
After a complete online load of v101.137 R1:
- close the PWA, disconnect network/enable airplane mode, cold-open it;
- confirm **v101.137 R1** opens normally; open two Heures, one linked text, Mon Espace and Aide;
- close/reopen once more offline; restore network and confirm no downgrade or repair loop.

## G. Accessibility gate
- iPhone/iPad: representative VoiceOver navigation of main nav, Aide, Méditée, search and back controls.
- Samsung: corresponding TalkBack checks.
- No visible actionable button unnamed; focus restoration after modal/Aide closure sensible.

## Release rule
Any failure involving version/update identity, user-data loss, blank/stuck startup, true-offline cold reopen, text corruption, H23 recension contamination, H24 scope/placement, or persistent navigation/rendering regression is a **release blocker**. Final public release remains unauthorized until all mandatory physical/live gates are closed.
""",encoding='utf-8')
    q=out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'
    q.write_text("""section,test_id,devices,release_blocker_if_fail,expected,result,notes,package_sha256
LIVE,LIVE-01,browser,YES,Aide shows v101.137,,,
LIVE,LIVE-02,browser,YES,version.json = v101.137; build_revision R1; cache luisa-24h-v101-137-r1,,,
UPDATE,UPD-01,iPhone;iPad;Samsung,YES,installed v101.136 R5 updates in place to v101.137 R1,,,
UPDATE,UPD-02,iPhone;iPad;Samsung,YES,notes/highlights/read state/last place/theme/font preserved,,,
UPDATE,UPD-03,iPhone;iPad;Samsung,YES,3 close/reopen cycles stay on v101.137 R1; no repair loop,,,
CORE,iPhone:CORE-01,iPhone,YES,home renders/scrolls,,,
CORE,iPhone:CORE-02,iPhone,YES,all 24 hours open,,,
CORE,iPhone:CORE-03,iPhone,NO,search works,,,
CORE,iPhone:CORE-04,iPhone,NO,Mon Espace works,,,
CORE,iPhone:CORE-05,iPhone,NO,Aide shows v101.137,,,
CORE,iPhone:CORE-06,iPhone,NO,theme/font controls work,,,
CORE,iPhone:CORE-07,iPhone,NO,Méditée controls synchronized,,,
CORE,iPhone:CORE-08,iPhone,YES,notes/highlights persist,,,
CORE,iPhone:CORE-09,iPhone,NO,no horizontal overflow,,,
CORE,iPhone:CORE-10,iPhone,YES,back/last-place restore coherent,,,
CORE,iPad portrait:CORE-01,iPad portrait,YES,home renders/scrolls,,,
CORE,iPad portrait:CORE-02,iPad portrait,YES,all 24 hours open,,,
CORE,iPad portrait:CORE-03,iPad portrait,NO,search works,,,
CORE,iPad portrait:CORE-04,iPad portrait,NO,Mon Espace works,,,
CORE,iPad portrait:CORE-05,iPad portrait,NO,Aide shows v101.137,,,
CORE,iPad portrait:CORE-06,iPad portrait,NO,theme/font controls work,,,
CORE,iPad portrait:CORE-07,iPad portrait,NO,Méditée controls synchronized,,,
CORE,iPad portrait:CORE-08,iPad portrait,YES,notes/highlights persist,,,
CORE,iPad portrait:CORE-09,iPad portrait,NO,no horizontal overflow,,,
CORE,iPad portrait:CORE-10,iPad portrait,YES,back/last-place restore coherent,,,
CORE,iPad landscape:CORE-01,iPad landscape,YES,home renders/scrolls,,,
CORE,iPad landscape:CORE-02,iPad landscape,YES,all 24 hours open,,,
CORE,iPad landscape:CORE-03,iPad landscape,NO,search works,,,
CORE,iPad landscape:CORE-04,iPad landscape,NO,Mon Espace works,,,
CORE,iPad landscape:CORE-05,iPad landscape,NO,Aide shows v101.137,,,
CORE,iPad landscape:CORE-06,iPad landscape,NO,theme/font controls work,,,
CORE,iPad landscape:CORE-07,iPad landscape,NO,Méditée controls synchronized,,,
CORE,iPad landscape:CORE-08,iPad landscape,YES,notes/highlights persist,,,
CORE,iPad landscape:CORE-09,iPad landscape,NO,no horizontal overflow,,,
CORE,iPad landscape:CORE-10,iPad landscape,YES,back/last-place restore coherent,,,
CORE,Samsung:CORE-01,Samsung,YES,home renders/scrolls,,,
CORE,Samsung:CORE-02,Samsung,YES,all 24 hours open,,,
CORE,Samsung:CORE-03,Samsung,NO,search works,,,
CORE,Samsung:CORE-04,Samsung,NO,Mon Espace works,,,
CORE,Samsung:CORE-05,Samsung,NO,Aide shows v101.137,,,
CORE,Samsung:CORE-06,Samsung,NO,theme/font controls work,,,
CORE,Samsung:CORE-07,Samsung,NO,Méditée controls synchronized,,,
CORE,Samsung:CORE-08,Samsung,YES,notes/highlights persist,,,
CORE,Samsung:CORE-09,Samsung,NO,no horizontal overflow,,,
CORE,Samsung:CORE-10,Samsung,YES,back/last-place restore coherent,,,
TARGETED,NEW-01,at least iPhone + Samsung,YES,H1 corrected Affections triad visible and standalone final Gloria absent,,,
TARGETED,NEW-02,at least iPhone + Samsung,YES,H7 closing instruction not displayed as reflection prose,,,
TARGETED,NEW-03,at least iPhone + Samsung,YES,H15 angel correction visible and moved devotional block hidden,,,
TARGETED,NEW-04,at least iPhone + Samsung,YES,H16 moved devotional block hidden,,,
TARGETED,NEW-05,at least iPhone + Samsung,YES,H18 corrected reflection syntax renders normally,,,
TARGETED,NEW-06,at least iPhone + Samsung,YES,H19 documentary letters absent from reflection,,,
TARGETED,NEW-07,at least iPhone + Samsung,YES,H20 Psalm/Gloria insertion absent from canonical meditation,,,
TARGETED,NEW-08,at least iPhone + Samsung,YES,H23 corrected reparative wording visible; no A/B synthesis,,,
TARGETED,NEW-09,at least iPhone + Samsung,YES,H24 burial remains in H24; Desolation present; moved/deleted paratext absent,,,
REGRESSION,REG-01,at least iPhone + Samsung,YES,H19 P118 repaired sentence intact,,,
REGRESSION,REG-02,at least iPhone + Samsung,YES,H22 authorized punctuation displayed correctly,,,
REGRESSION,REG-03,at least iPhone + Samsung,YES,RELATED_HOUR_06 P013 flow preserved,,,
REGRESSION,REG-04,at least iPhone + Samsung,YES,RELATED_HOUR_16 P038 no split inside “en”,,,
REGRESSION,REG-05,at least iPhone + Samsung,YES,RELATED_HOUR_04 P127 break visually natural,,,
REGRESSION,REG-06,at least iPhone + Samsung,YES,H24 cycle controls correct,,,
REGRESSION,REG-07,at least iPhone + Samsung,YES,Tome 20 — 25 décembre 1926 linked text displays “à la porte de leur cœur”,,,
OFFLINE,OFF-01,iPhone;iPad;Samsung,YES,true offline cold reopen works after online load,,,
OFFLINE,OFF-02,iPhone;iPad;Samsung,YES,v101.137 R1 hours/linked text/space/help usable offline,,,
ACCESS,ACC-01,iPhone/iPad VoiceOver,YES,representative controls named and navigable,,,
ACCESS,ACC-02,Samsung TalkBack,YES,representative controls named and navigable,,,
""",encoding='utf-8-sig')
    (ev/'EVIDENCE_README.md').write_text("""# v101.137 R1 evidence reading order

`PREAUTHORIZATION_GATE_STATEMENT.md` is an immutable historical snapshot of the gate **before** the user authorized mutation. It is intentionally retained for provenance and is superseded for current state by `USER_AUTHORIZATION_2026-09-08.md`, `AUTHORIZATION_RECEIPT.json`, and `INTERNAL_VALIDATION_RECEIPT.json`.

The 24 `PRESERVE_MOVE` records are retained in `PRESERVE_MOVE_ARCHIVE_24.json` and intentionally are not rendered in the v101.137 R1 UI, by explicit user decision.
""",encoding='utf-8')
    active=['README.md','REAL_DEVICE_QA_CHECKLIST.md','reports/V101137_R1_AUTHORIZED_79_MUTATION.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md']
    writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'active_documents':active,'active_test_artifacts':['REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'],'historical_reports_root':'reports/historical/','rule':'Only listed active documents are current; predecessor/superseded reports are historical.'})
    writej(out/'metadata/build_provenance.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,'baseline_version':'v101.136 R5','baseline_zip_sha256':BASE_SHA,'authorized_ledger_sha256':LEDGER_SHA,'italian_r3_authority_sha256':ITALIAN_R3_SHA,'frozen_r4_authority_sha256':R4_SHA,'canonical_authorized_operations':79,'text_replace_or_trim_records':53,'canonical_records_removed':26,'preserve_move_records_archived':24,'preserve_move_user_visible':False,'stable_retained_record_ids_unchanged':True,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'corpus_fingerprint_sha256':C['fingerprint_sha256'],'final_validation':'EXTERNAL_EXACT_ZIP_RECHECK_REQUIRED'})
    writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_evidence_root':'evidence/v101137_r1','predecessor_24h':{'version':'v101.136 R5','sha256':BASE_SHA},'authorized_ledger_sha256':LEDGER_SHA,'governing_italian_r3_sha256':ITALIAN_R3_SHA,'frozen_r4_source_review_sha256':R4_SHA,'preserve_move_visibility':'EVIDENCE_ONLY_NOT_UI'})
    (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} Scope Authority\n\nThe only authorized meditation/reflection corpus operations are the exact 79 rows in ledger SHA-256 `{LEDGER_SHA}` applied to immutable v101.136 R5 `{BASE_SHA}`. The 24 `PRESERVE_MOVE` records must be retained in evidence but need not be user-visible in this version. Deferred/recension-sensitive loci remain unchanged; H23 Forms A/B must not be synthesized; H24 burial/deposition placement must not move; Desolation remains within H24 meditation scope. No associated Livre du Ciel or unrelated UI text mutation is authorized.\n''',encoding='utf-8')
    writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'package_rule':'Package does not self-certify final ZIP bytes; exact frozen ZIP must receive an external SHA-bound final validation receipt.','preserve_move_visibility':'EVIDENCE_ONLY_NOT_UI','physical_device_claims':'NOT_TESTED','public_deployment_authorized':False})
    writej(out/'metadata/current_gate_map.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'internal_gates':['79/79 exact authorized operations','zero unlisted canonical text mutations','24/24 preserve-move evidence retention','deferred/recension locks','derived-offset integrity','HTML mirror identity','deterministic A/B freeze','exact ZIP reopen integrity'],'external_open_gates':gates,'public_release':'UNAUTHORIZED'})
    shutil.copy2(Path(__file__),out/'scripts/build_v101137_r1_authorized_79.py')
    writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_builder':'scripts/build_v101137_r1_authorized_79.py','builder_contract':'Explicit SHA-bound v101.136 R5 predecessor ZIP + exact authorization ledger; no other corpus input.'})
    writej(out/'metadata/builder_input_manifest.json',{'version':VERSION,'build_revision':REV,'predecessor_zip_sha256':BASE_SHA,'authorized_ledger_sha256':LEDGER_SHA,'italian_r3_authority_sha256':ITALIAN_R3_SHA,'frozen_r4_authority_sha256':R4_SHA})
    # Deep internal validation before manifests.
    cand=(out/'index.html').read_text(encoding='utf-8'); assert cand==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
    C1,_,_=extract(cand,'CORPUS');after=hour_layer_records(C1)
    row_by_id={r['r5_record_id']:r for r in rows}
    observed=[]
    for sid,old in base_hour_text.items():
        if sid in after:
            if after[sid]!=old: observed.append(sid)
        else: observed.append(sid)
    assert set(observed)==set(row_by_id),(len(observed),set(observed)^set(row_by_id))
    for sid,r in row_by_id.items():
        op=r['final_operation']
        if op in ('REPLACE_RECORD','TRIM_RECORD'):
            assert after.get(sid)==r['final_proposed_french'],(sid,after.get(sid),r['final_proposed_french'])
        else: assert sid not in after,sid
    # All non-target existing hour texts unchanged.
    for sid,old in base_hour_text.items():
        if sid not in row_by_id: assert after.get(sid)==old,sid
    assert len(preserved)==24 and all(x['original_record']['t']==row_by_id[x['record_id']]['current_text'] for x in preserved)
    assert all(x['original_location']==base_hour_locations[x['record_id']] for x in preserved), 'PRESERVE_MOVE original location drift'
    assert all(x['original_location']==base_hour_locations[x['record_id']] for x in deleted), 'DELETE original location drift'
    # Specific recension/scope gates.
    for cid in ('C0095','C0096','C0097','C0098'):
        r=next(x for x in rows if x['candidate_id']==cid);assert r['r5_record_id'] in after and '.DESOL.' not in r['r5_record_id']
    for cid in ('C0091','C0092'):
        r=next(x for x in rows if x['candidate_id']==cid);assert '.DESOL.' in r['r5_record_id'] and r['r5_record_id'] in after
    # No H23 Form-B insertion marker/source change: only the exact 9 H23 meditation rows + 1 reflection row may differ.
    h23obs=[sid for sid in observed if sid.startswith('PASSION24.HOUR.23.')]
    h23auth=[r['r5_record_id'] for r in rows if r['hour']=='23']
    assert set(h23obs)==set(h23auth) and len(h23auth)==10
    text_by_id=after.copy()
    validate_derived_offsets(text_by_id,{n:extract(cand,n)[0] for n in names})
    # Ensure preserve archive is not wired into runtime UI/assets.
    assert 'PRESERVE_MOVE_ARCHIVE_24.json' not in cand
    assert 'PRESERVE_MOVE_ARCHIVE_24.json' not in (out/'sw.js').read_text(encoding='utf-8')
    # New version identity/cache.
    assert "const APP_VERSION = 'v101.137';" in cand and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in cand
    assert CACHE in (out/'sw.js').read_text(encoding='utf-8')
    assert json.loads((out/'version.json').read_text())['app_version']==VERSION
    qa_text=(out/'REAL_DEVICE_QA_CHECKLIST.md').read_text(encoding='utf-8')
    assert '`app_version = v101.137`' in qa_text and 'Aide / À propos.\n- Confirm `version.json` reports `app_version = v101.137`' in qa_text
    assert 'currently running **v101.136 R5**' in qa_text and 'confirm **v101.137 R1** opens normally' in qa_text
    qa_csv=(out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').read_text(encoding='utf-8-sig')
    assert 'Aide shows v101.136' not in qa_csv and 'installed v101.135 updates' not in qa_csv
    assert 'Aide shows v101.137' in qa_csv and 'installed v101.136 R5 updates in place to v101.137 R1' in qa_csv
    # Internal validation receipt.
    writej(ev/'INTERNAL_VALIDATION_RECEIPT.json',{'schema':'L24H_V101137_R1_INTERNAL_VALIDATION_RECEIPT_V1','status':'PASS','checks':{'baseline_sha256':BASE_SHA,'ledger_sha256':LEDGER_SHA,'authorized_rows':79,'observed_canonical_delta_ids':79,'replacement_trim_exact':53,'removed_from_canonical_exact':26,'preserve_move_archived_exact':24,'delete_exact':2,'unlisted_hour_text_mutations':0,'h23_authorized_delta_rows':10,'h23_ab_synthesis':False,'h24_burial_moved':False,'h24_desolation_scope_preserved':True,'derived_offsets_valid':True,'html_mirror_identical':True,'preserve_move_not_user_visible':True,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True},'corpus_fingerprint_sha256':C1['fingerprint_sha256']})
    # Overlay + manifests.
    cur=files(out);changed=sorted(k for k,p in cur.items() if k not in basehash or sha_file(p)!=basehash[k]);removed=sorted(set(basehash)-set(cur))
    for x in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
        if x not in changed:changed.append(x)
    writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101137_R1_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':'v101.136 R5','baseline_zip_sha256':BASE_SHA,'changed_or_added':sorted(changed),'removed':removed})
    ex={'metadata/hash_manifest.json','metadata/package_manifest.json'};lst=[]
    for k,p in sorted(files(out).items()):
        if k in ex:continue
        lst.append({'path':k,'size':p.stat().st_size,'sha256':sha_file(p)})
    writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
    writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
    return {'version':VERSION,'revision':REV,'files':len(files(out)),'authorized_rows':79,'text_replace_trim':53,'preserve_move':24,'delete':2,'corpus_fingerprint_sha256':C['fingerprint_sha256'],'cache':CACHE,'stage':STAGE}

def freeze(root,zp):
    root=Path(root);zp=Path(zp);zp.unlink(missing_ok=True)
    with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(root.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(root).as_posix();info=zipfile.ZipInfo(rel,(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16);z.writestr(info,p.read_bytes())
    return sha_file(zp)

if __name__=='__main__':
    if len(sys.argv)!=5: raise SystemExit('Usage: build.py <R5_base.zip> <ledger.csv> <out_dir> <out_zip>')
    r=build(sys.argv[1],sys.argv[2],sys.argv[3]);h=freeze(sys.argv[3],sys.argv[4]);print(json.dumps(r,indent=2,ensure_ascii=False));print('ZIP',h)
