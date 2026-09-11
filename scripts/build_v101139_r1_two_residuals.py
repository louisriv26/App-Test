from pathlib import Path
import json, hashlib, zipfile, shutil, re, csv, sys, copy

BASE_SHA='14538b7e7294b77282ad40a4efae76df070ee32325752d79965a2be41aaca1ef'
GATE_SHA='309ff5de13c669a9a1df5390a225abb716957203eacfcfe6c98cb3bb9499fc41'
AUTH_SHA='a11430e23addc8ec6d86c93ab5eada74c461205fab58e1af1692cd056c5dc215'
PARENT_LEDGER_SHA='f9a9c4c74df33b3f96909e3611acb74c448deed5fa367fa86072d2e27cbfef49'
VERSION='v101.139'; REV='R1'; DATE='2026-09-08'; CACHE='luisa-24h-v101-139-r1'
STAGE='TWO_RESIDUAL_FRENCH_SOURCE_FIDELITY_SUCCESSOR_R1'
BASE_VERSION='v101.138 R2'
PROTECTED_PRESENTATION=[
 'TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS',
 'LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA',
 'VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_PROJECTION',
 'SPEECH_PRESENTATION_ADJUDICATIONS'
]
AFFECTED_IDS=['PASSION24.HOUR.01.P027','PASSION24.HOUR.24.DESOL.P081']
EXPECTED_CURRENT={
 'PASSION24.HOUR.01.P027':'c94005064df666aeb762839e5d9a69fbb1390fc0a232b2677fdd1441569379e7',
 'PASSION24.HOUR.24.DESOL.P081':'5b2be922ae0443e7991740bb90e239059979779dd327cd0036d4ed9ed72cf0af'
}
EXPECTED_FINAL={
 'PASSION24.HOUR.01.P027':'258887a4526d0f873ca08772ae891c6cd8374ae9b8bc564f06d8d8376d9f0fea',
 'PASSION24.HOUR.24.DESOL.P081':'3e602dd9e83c78cc53b898b8dbf5bacb1f97a4fcbd3144994bf18bb5f79004cb'
}

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_text(s): return sha_bytes(s.encode('utf-8'))
def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def files(root): return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}
def jdump(o): return json.dumps(o,ensure_ascii=False,separators=(',',':'))
def writej(p,o):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def raw_const(text,name):
    m=re.search(rf'const\s+{re.escape(name)}\s*=\s*',text); assert m,name
    start=m.end()
    while start<len(text) and text[start].isspace(): start+=1
    opener=text[start]; assert opener in '[{',(name,repr(text[start:start+20]))
    pairs={'[':']','{':'}'}; stack=[]; quote=None; esc=False; j=start
    while j<len(text):
        ch=text[j]
        if quote:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: quote=None
        else:
            if ch in ('"',"'",'`'): quote=ch
            elif ch in '[{': stack.append(pairs[ch])
            elif ch in ']}':
                assert stack and ch==stack[-1],(name,j,ch)
                stack.pop()
                if not stack:
                    raw=text[start:j+1]
                    try: obj=json.loads(raw)
                    except Exception: obj=None
                    return raw,obj,start,j+1
        j+=1
    raise AssertionError(('unterminated',name))
def replace_const(text,name,obj):
    raw,_,s,e=raw_const(text,name); new=jdump(obj)
    return text[:s]+new+text[e:]
def exact_replace(s,old,new,label,count=1):
    c=s.count(old); assert c==count,(label,c,count)
    return s.replace(old,new,count)
def canonical_records(c):
    d={}; order=[]
    def add(p):
        sid=p['id']; assert sid not in d,sid; d[sid]=p; order.append(sid)
    for h in c['hours']:
        for k in ('paragraphs','reflections'):
            for p in h.get(k,[]): add(p)
        for sub in h.get('subsections',[]):
            for p in sub.get('paragraphs',[]): add(p)
    for k in ('prayers','sections'):
        for q in c.get(k,[]):
            for p in q.get('paragraphs',[]): add(p)
    return d,order
def collect_ids(obj):
    out=[]
    def walk(x):
        if isinstance(x,dict):
            if isinstance(x.get('id'),str): out.append(x['id'])
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(obj); return out
def freeze(root,zp):
    root=Path(root);zp=Path(zp);zp.unlink(missing_ok=True)
    with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(root.rglob('*')):
            if not p.is_file(): continue
            rel=p.relative_to(root).as_posix()
            info=zipfile.ZipInfo(rel,(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16)
            z.writestr(info,p.read_bytes())
    return sha_file(zp)

def build(base_zip,gate_json,auth_json,out):
    base_zip=Path(base_zip);gate_json=Path(gate_json);auth_json=Path(auth_json);out=Path(out)
    assert sha_file(base_zip)==BASE_SHA,(sha_file(base_zip),BASE_SHA)
    assert sha_file(gate_json)==GATE_SHA,(sha_file(gate_json),GATE_SHA)
    assert sha_file(auth_json)==AUTH_SHA,(sha_file(auth_json),AUTH_SHA)
    gate=json.loads(gate_json.read_text(encoding='utf-8')); auth=json.loads(auth_json.read_text(encoding='utf-8'))
    assert gate['base_app_zip_sha256']==BASE_SHA and gate['authorized_79_ledger_sha256']==PARENT_LEDGER_SHA
    assert auth['base_app_zip_sha256']==BASE_SHA and auth['decision_gate_sha256']==GATE_SHA and auth['parent_79_ledger_sha256']==PARENT_LEDGER_SHA
    proposals={x['record_id']:x for x in gate['proposals']}
    assert set(proposals)==set(AFFECTED_IDS)
    for sid in AFFECTED_IDS:
        assert proposals[sid]['current_sha256']==EXPECTED_CURRENT[sid]
        assert proposals[sid]['proposed_sha256']==EXPECTED_FINAL[sid]
        assert sha_text(proposals[sid]['proposed_text'])==EXPECTED_FINAL[sid]
    shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
    with zipfile.ZipFile(base_zip) as z:
        assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
        z.extractall(out)
    base_hash={k:sha_file(p) for k,p in files(out).items()}; base_paths=set(base_hash)
    src=(out/'index.html').read_text(encoding='utf-8'); assert src==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
    rawC,C,_,_=raw_const(src,'CORPUS'); assert jdump(C)==rawC
    C0=copy.deepcopy(C); cm0,order0=canonical_records(C0)
    for sid in AFFECTED_IDS:
        assert sid in cm0
        assert sha_text(cm0[sid]['t'])==EXPECTED_CURRENT[sid]
        assert cm0[sid]['t']==proposals[sid]['current_text']
    # Protected presentation/speech/topology declarations must not depend on these two IDs.
    protected_raw_before={}
    affected_metadata_hits={}
    for n in PROTECTED_PRESENTATION:
        raw,obj,_,_=raw_const(src,n); protected_raw_before[n]=raw
        s=json.dumps(obj,ensure_ascii=False) if obj is not None else raw
        affected_metadata_hits[n]=[sid for sid in AFFECTED_IDS if sid in s]
    offset_layers=['DISPLAY_SEGMENTS','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_PROJECTION','SPEECH_PRESENTATION_ADJUDICATIONS']
    assert all(not affected_metadata_hits[n] for n in offset_layers),affected_metadata_hits
    # Exact bounded mutation.
    for sid in AFFECTED_IDS: cm0[sid]['t']=proposals[sid]['proposed_text']
    # Same fingerprint algorithm, newly computed content fingerprint.
    old_fp=C0['fingerprint_sha256']; tmp={k:v for k,v in C0.items() if k!='fingerprint_sha256'}; C0['fingerprint_sha256']=sha_text(jdump(tmp))
    new_fp=C0['fingerprint_sha256']; assert new_fp!=old_fp
    cm1,order1=canonical_records(C0); assert order1==order0
    changed_records=[]
    for sid in order0:
        a=cm0[sid]; b=cm1[sid]
        if a!=b:
            changed_records.append(sid)
    # cm0 objects were deep-copied through C0? rebuild baseline map to avoid aliasing confusion.
    base_cm,_=canonical_records(C)
    changed_records=[sid for sid in order0 if base_cm[sid]!=cm1[sid]]
    assert changed_records==AFFECTED_IDS,changed_records
    for sid in AFFECTED_IDS:
        assert sha_text(cm1[sid]['t'])==EXPECTED_FINAL[sid]
        # only t field changes inside records
        aa=copy.deepcopy(base_cm[sid]);bb=copy.deepcopy(cm1[sid]);aa.pop('t');bb.pop('t');assert aa==bb
    # Replace CORPUS only, then runtime identity.
    s=replace_const(src,'CORPUS',C0)
    s=exact_replace(s,"const APP_VERSION = 'v101.138';",f"const APP_VERSION = '{VERSION}';",'app version')
    s=exact_replace(s,"const BUILD_REVISION = 'R2';",f"const BUILD_REVISION = '{REV}';",'build revision')
    s=exact_replace(s,"const APP_EVIDENCE_STAGE = 'RELEASE_ACCESSIBILITY_CLEANUP_R2';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",'stage')
    s=re.sub(r"const BUILD_DATE = '2026-09-08';[^\n]*",f"const BUILD_DATE = '{DATE}'; // {VERSION} {REV} / exactly two authorized residual French source-fidelity corrections",s,count=1)
    (out/'index.html').write_text(s,encoding='utf-8');(out/'luisa_24_heures.html').write_text(s,encoding='utf-8')
    # Version/cache identity.
    sw=(out/'sw.js').read_text(encoding='utf-8')
    sw=exact_replace(sw,'/* v101.138 R2 */','/* v101.139 R1 */','sw version')
    sw=exact_replace(sw,"const CACHE_NAME = 'luisa-24h-v101-138-r2';",f"const CACHE_NAME = '{CACHE}';",'sw cache')
    (out/'sw.js').write_text(sw,encoding='utf-8')
    man=json.loads((out/'manifest.json').read_text(encoding='utf-8')); assert man['version']=='v101.138' and man['build_revision']=='R2'
    man['version']=VERSION;man['build_revision']=REV;writej(out/'manifest.json',man)
    gates=['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update to v101.139 R1 from the currently deployed build','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing']
    v=json.loads((out/'version.json').read_text(encoding='utf-8')); assert v['app_version']=='v101.138' and v['build_revision']=='R2'
    v.update({
      'app_version':VERSION,'build_revision':REV,'build_date':DATE,'cache_name':CACHE,
      'release_scope':f"Textual successor of exact immutable v101.138 R2 SHA-256 {BASE_SHA}. Applies exactly two hash-bound French source-fidelity REPLACE_RECORD corrections: PASSION24.HOUR.01.P027 and PASSION24.HOUR.24.DESOL.P081. No third canonical record, TEXT_LIBRARY, stable ID/order, H23 Form A/B governance, H24 burial/deposition placement, H8 strapazzi decision, 79-row parent ledger, storage schema, personal snapshot schema or unrelated UI feature is changed.",
      'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update/persistence, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.139 R1.',
      'overall_release_status':'V101139_R1_TWO_RESIDUAL_TEXTUAL_SUCCESSOR_CONTROLLED_DEVICE_TEST_CANDIDATE__FINAL_PUBLIC_DEPLOYMENT_UNAUTHORIZED',
      'known_blockers':gates,'external_open_gates':gates,
      'postfreeze_reopen_evidence':'Exact v101.139 R1 successor ZIP requires external SHA-bound final recheck before controlled device testing.'
    })
    writej(out/'version.json',v)
    # Active human-facing release files.
    (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION} {REV}\n\nControlled device-test candidate and separately governed textual successor of exact immutable v101.138 R2 SHA-256 `{BASE_SHA}`.\n\nExactly two French source-fidelity records are changed: `PASSION24.HOUR.01.P027` and `PASSION24.HOUR.24.DESOL.P081`. Both are bound to decision-gate SHA-256 `{GATE_SHA}` and exact post-mutation record hashes.\n\nThe prior 79-row authority remains unchanged (`{PARENT_LEDGER_SHA}`). `TEXT_LIBRARY`, stable IDs/order, H23 Form A/B governance, H24 burial/deposition placement, H8 `strapazzi`, storage schema, personal snapshot schema and unrelated UI are unchanged.\n\nFinal public deployment remains unauthorized until live-origin/device/PWA/offline/accessibility gates pass.\n''',encoding='utf-8')
    (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(f'''# Real-device QA checklist — {VERSION} {REV}\n\nUse only the exact {VERSION} {REV} candidate identified by the external SHA-bound receipt.\n\n## Identity\n- app_version = {VERSION}\n- build_revision = {REV}\n- cache_name = {CACHE}\n- APP_EVIDENCE_STAGE = {STAGE}\n- corpus fingerprint = {new_fp}\n\n## Text-specific checks\n- Hour 1 `PASSION24.HOUR.01.P027` ends `scelle le salut de leur âme par ta bénédiction.`\n- Hour 24 Desolation `PASSION24.HOUR.24.DESOL.P081` ends `Mère crucifiée, en te regardant, je compatis à tes Douleurs : elles sont indicibles ! ...` (typographic narrow no-break spaces preserved in app).\n- Search finds the restored terminal wording in both loci.\n- Notes/highlights can be created, persisted, edited/deleted on both changed records and adjacent records.\n\n## Regression\n- Hours 1 and 24 render correctly in light/dark mode on phone/tablet/desktop.\n- Search/direct-speech search, Mon Espace, Méditée, last-position and personal snapshot persistence behave normally.\n- Assistance quick-nav focus remains repaired.\n- Installed-PWA update preserves existing user data.\n- True offline cold reopen succeeds after update.\n- Representative VoiceOver/TalkBack checks pass.\n\nFinal public deployment remains unauthorized until all external gates are evidenced.\n''',encoding='utf-8')
    (out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').write_text('test_id,platform,required,expected,actual,status,notes\n'+
      f'LIVE-01,browser,YES,Aide shows {VERSION} {REV} and current corpus fingerprint,,,\n'+
      'TEXT-01,iPhone;iPad;Samsung,YES,Hour 1 P027 contains terminal par ta bénédiction,,,\n'+
      'TEXT-02,iPhone;iPad;Samsung,YES,Hour 24 DESOL P081 contains Mère crucifiée and Douleurs indicibles,,,\n'+
      'STATE-01,iPhone;iPad;Samsung,YES,Existing notes highlights Méditée last-place theme and font survive update,,,\n'+
      'OFFLINE-01,iPhone;iPad;Samsung,YES,True offline cold reopen succeeds after installed-PWA update,,,\n'+
      'A11Y-01,iPhone;iPad;Samsung,YES,Representative VoiceOver or TalkBack navigation is usable,,,\n',encoding='utf-8')
    # Historical placement of predecessor report.
    hist=out/'reports/historical/v101138_r2';hist.mkdir(parents=True,exist_ok=True)
    oldrep=out/'reports/V101138_R2_RELEASE_ACCESSIBILITY_CLEANUP.md';assert oldrep.exists();shutil.move(str(oldrep),str(hist/oldrep.name))
    report=out/'reports/V101139_R1_TWO_RESIDUAL_TEXTUAL_SUCCESSOR.md'
    report.write_text(f'''# {VERSION} {REV} — two residual French source-fidelity successor\n\n## Authority\nBase: exact v101.138 R2 SHA-256 `{BASE_SHA}`. Decision gate: `{GATE_SHA}`. Parent 79-row ledger remains `{PARENT_LEDGER_SHA}`.\n\n## Exact canonical delta\n- `PASSION24.HOUR.01.P027`: REPLACE_RECORD, `{EXPECTED_CURRENT[AFFECTED_IDS[0]]}` → `{EXPECTED_FINAL[AFFECTED_IDS[0]]}`.\n- `PASSION24.HOUR.24.DESOL.P081`: REPLACE_RECORD, `{EXPECTED_CURRENT[AFFECTED_IDS[1]]}` → `{EXPECTED_FINAL[AFFECTED_IDS[1]]}`.\n\nExactly two canonical records change. `TEXT_LIBRARY` and stable-ID order are unchanged. No affected record appears in offset-bearing speech/display/topology metadata, so no presentation remap is required.\n\nCorpus fingerprint: `{old_fp}` → `{new_fp}`. The fingerprint algorithm is unchanged.\n\nFinal public deployment remains unauthorized pending the external live/device/PWA/offline/accessibility gates.\n''',encoding='utf-8')
    # Evidence.
    ev=out/'evidence/v101139_r1';ev.mkdir(parents=True,exist_ok=True)
    shutil.copy2(gate_json,ev/'TWO_RESIDUAL_FRENCH_SOURCE_FIDELITY_DECISION_GATE.json')
    shutil.copy2(auth_json,ev/'EXPLICIT_USER_AUTHORITY_TWO_RESIDUALS.json')
    with (ev/'AUTHORIZED_TWO_ROW_LEDGER.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['record_id','operation','pre_sha256','post_sha256','decision_gate_sha256','base_zip_sha256'])
        for sid in AFFECTED_IDS:w.writerow([sid,'REPLACE_RECORD',EXPECTED_CURRENT[sid],EXPECTED_FINAL[sid],GATE_SHA,BASE_SHA])
    ledger_sha=sha_file(ev/'AUTHORIZED_TWO_ROW_LEDGER.csv')
    writej(ev/'PREAPPLY_BINDING.json',{'schema':'L24H_V101139_R1_PREAPPLY_BINDING_V1','status':'PASS','base_zip_sha256':BASE_SHA,'decision_gate_sha256':GATE_SHA,'user_authority_sha256':AUTH_SHA,'parent_79_ledger_sha256':PARENT_LEDGER_SHA,'two_row_ledger_sha256':ledger_sha,'current_record_hashes':EXPECTED_CURRENT,'proposed_record_hashes':EXPECTED_FINAL})
    writej(ev/'CANONICAL_DELTA_PROOF.json',{'schema':'L24H_V101139_R1_CANONICAL_DELTA_PROOF_V1','status':'PASS','changed_canonical_record_count':2,'changed_record_ids':AFFECTED_IDS,'operations':{'REPLACE_RECORD':2,'TRIM_RECORD':0,'MOVE_OUT_OF_CANONICAL_LAYER':0,'DELETE_FROM_CANONICAL_LAYER':0},'zero_unlisted_canonical_text_mutations':True,'text_library_changes':0,'stable_id_sequence_identical':True,'corpus_fingerprint_before':old_fp,'corpus_fingerprint_after':new_fp})
    writej(ev/'PROTECTED_PRESENTATION_PARITY.json',{'schema':'L24H_V101139_R1_PROTECTED_PRESENTATION_PARITY_V1','status':'PASS','presentation_declarations_checked':len(PROTECTED_PRESENTATION),'all_byte_identical':True,'affected_record_offset_metadata_hits':affected_metadata_hits,'remap_required':False})
    writej(ev/'INTERNAL_BUILD_RECEIPT.json',{'schema':'L24H_V101139_R1_INTERNAL_BUILD_RECEIPT_V1','status':'PASS','base_sha_verified':True,'gate_sha_verified':True,'authority_sha_verified':True,'current_record_hashes_verified':True,'proposed_record_hashes_verified':True,'exact_canonical_changed_records':2,'zero_unlisted_canonical_mutations':True,'text_library_byte_identical':True,'stable_ids_order_identical':True,'protected_presentation_byte_identical':True,'storage_schema_unchanged':v['storage_schema']==8,'personal_snapshot_schema_unchanged':v['personal_snapshot']==5,'html_mirror_identical':True})
    shutil.copy2(Path(__file__),out/'scripts/build_v101139_r1_two_residuals.py')
    # Metadata current authority.
    writej(out/'metadata/build_provenance.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,'baseline_version':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,'decision_gate_sha256':GATE_SHA,'explicit_user_authority_sha256':AUTH_SHA,'parent_79_ledger_sha256':PARENT_LEDGER_SHA,'authorized_two_row_ledger_sha256':ledger_sha,'canonical_record_changes_v101138_r2_to_v101139_r1':2,'text_library_changes_v101138_r2_to_v101139_r1':0,'stable_id_changes_v101138_r2_to_v101139_r1':0,'protected_presentation_declaration_changes_v101138_r2_to_v101139_r1':0,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'corpus_fingerprint_sha256':new_fp,'final_validation':'EXTERNAL_EXACT_ZIP_RECHECK_REQUIRED'})
    writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_evidence_root':'evidence/v101139_r1','immediate_build_predecessor':{'version':BASE_VERSION,'sha256':BASE_SHA},'decision_gate_sha256':GATE_SHA,'explicit_user_authority_sha256':AUTH_SHA,'parent_79_ledger_sha256':PARENT_LEDGER_SHA,'content_authority_evidence_root':'evidence/v101137_r1','release_ui_predecessor_evidence_root':'evidence/v101138_r2','preserve_move_visibility':'EVIDENCE_ONLY_NOT_UI'})
    writej(out/'metadata/current_gate_map.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'internal_gates':['exact R2 SHA binding','decision-gate and user-authority SHA binding','both current and proposed record hash binding','exactly two canonical records changed','zero unlisted canonical mutations','TEXT_LIBRARY byte identity','stable IDs/order identity','protected presentation/speech/topology byte parity','H1/H24 render/search/state regression','HTML mirror identity','JS syntax','service-worker/cache identity','deterministic rebuild','four-pass adversarial package audit','fresh ZIP reopen integrity'],'external_open_gates':gates,'public_release':'UNAUTHORIZED'})
    writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'package_rule':'Package does not self-certify final ZIP bytes; exact frozen v101.139 R1 ZIP must receive an external SHA-bound final validation receipt.','immediate_build_predecessor':BASE_VERSION,'immediate_build_predecessor_sha256':BASE_SHA,'canonical_content_changed':True,'authorized_canonical_record_changes':2,'text_library_changed':False,'stable_ids_changed':False,'physical_device_claims':'NOT_TESTED','public_deployment_authorized':False})
    (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} Scope Authority\n\nAuthorized canonical content scope is exactly two `REPLACE_RECORD` operations bound to decision-gate SHA-256 `{GATE_SHA}` and predecessor SHA-256 `{BASE_SHA}`: `PASSION24.HOUR.01.P027` and `PASSION24.HOUR.24.DESOL.P081`.\n\nThe parent 79-row ledger `{PARENT_LEDGER_SHA}` remains immutable. Forbidden: any third canonical mutation; `TEXT_LIBRARY` or stable-ID/order changes; H23 Form A/B synthesis; H24 burial/deposition relocation; H8 `strapazzi`; AFLP alternative-edition features; unrelated UI; schema changes without separately demonstrated mechanical necessity.\n\nNecessary version/cache/build/provenance/evidence metadata may change. Final public deployment remains externally gated.\n''',encoding='utf-8')
    writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_builder':'scripts/build_v101139_r1_two_residuals.py','builder_contract':'Exact SHA-bound v101.138 R2 predecessor plus exact gate and user-authority files; exactly two canonical REPLACE_RECORD operations; no unrelated mutation.'})
    writej(out/'metadata/builder_input_manifest.json',{'version':VERSION,'build_revision':REV,'predecessor_v101138_r2_zip_sha256':BASE_SHA,'decision_gate_sha256':GATE_SHA,'explicit_user_authority_sha256':AUTH_SHA,'parent_79_ledger_sha256':PARENT_LEDGER_SHA})
    writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'active_documents':['README.md','REAL_DEVICE_QA_CHECKLIST.md','reports/V101139_R1_TWO_RESIDUAL_TEXTUAL_SUCCESSOR.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md'],'active_test_artifacts':['REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'],'historical_reports_root':'reports/historical/','rule':'Only listed active documents are current; predecessor/superseded reports and tooling are historical within original scope.'})
    # Deep post-write invariants before manifests.
    final=(out/'index.html').read_text(encoding='utf-8');assert final==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
    _,Cf,_,_=raw_const(final,'CORPUS');fcm,forder=canonical_records(Cf);assert forder==order0
    diffs=[sid for sid in order0 if canonical_records(C)[0][sid]!=fcm[sid]];assert diffs==AFFECTED_IDS,diffs
    for sid in AFFECTED_IDS: assert sha_text(fcm[sid]['t'])==EXPECTED_FINAL[sid]
    for n in PROTECTED_PRESENTATION:
        r,_,_,_=raw_const(final,n); assert r==protected_raw_before[n],n
    assert json.loads((out/'version.json').read_text(encoding='utf-8'))['storage_schema']==8
    assert json.loads((out/'version.json').read_text(encoding='utf-8'))['personal_snapshot']==5
    assert CACHE in (out/'sw.js').read_text(encoding='utf-8')
    assert "const APP_VERSION = 'v101.139';" in final and "const BUILD_REVISION = 'R1';" in final and STAGE in final
    # Predecessor evidence roots remain byte-identical.
    for root in ['evidence/v101137_r1','evidence/v101137_r2','evidence/v101138_r1','evidence/v101138_r2']:
        for k,p in files(out/root).items():
            basep=Path('/nonexistent')
            rel=root+'/'+k
            if rel in base_hash: assert sha_file(p)==base_hash[rel],rel
    # Path scope: no removals except predecessor current report relocation.
    cur=files(out); removed=sorted(base_paths-set(cur)); assert removed==['reports/V101138_R2_RELEASE_ACCESSIBILITY_CLEANUP.md'],removed
    # Manifests.
    changed=sorted(k for k,p in cur.items() if k not in base_hash or sha_file(p)!=base_hash[k])
    changed_for_overlay=sorted(set(changed)|{'metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json'})
    writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101139_R1_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,'changed_or_added':changed_for_overlay,'removed':removed,'canonical_text_delta':'EXACTLY_2_REPLACE_RECORD','text_library_delta':'ZERO','stable_id_delta':'ZERO','presentation_topology_delta':'ZERO'})
    ex={'metadata/hash_manifest.json','metadata/package_manifest.json'};lst=[]
    for k,p in sorted(files(out).items()):
        if k in ex: continue
        lst.append({'path':k,'size':p.stat().st_size,'sha256':sha_file(p)})
    writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
    writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
    return {'version':VERSION,'revision':REV,'stage':STAGE,'base_sha256':BASE_SHA,'decision_gate_sha256':GATE_SHA,'two_row_ledger_sha256':ledger_sha,'changed_canonical_records':AFFECTED_IDS,'corpus_fingerprint_before':old_fp,'corpus_fingerprint_after':new_fp,'files':len(files(out)),'manifested_nonself_files':len(lst),'cache':CACHE}

if __name__=='__main__':
    if len(sys.argv)!=6: raise SystemExit('Usage: build.py <v101138_R2.zip> <decision_gate.json> <authority.json> <out_dir> <out.zip>')
    info=build(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]); zsha=freeze(sys.argv[4],sys.argv[5]);info['zip_sha256']=zsha;info['zip_size']=Path(sys.argv[5]).stat().st_size
    print(json.dumps(info,ensure_ascii=False,indent=2))
