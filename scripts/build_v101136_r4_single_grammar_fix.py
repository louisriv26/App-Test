from pathlib import Path
import csv,json,hashlib,zipfile,shutil,re,os
BASE=Path('/mnt/data/appcheck136/v101136_R3_A.zip')
BASE_SHA='994e7a76ecc1947f150d68c5d01d36fdeaca96574ae459787fd845fd82b59f14'
CONTENT_PREDECESSOR_SHA='cf8b688e649b2ef3f7c36768691c6a647d9d1e9eec85c90ba697dc2a05ef26fc'
OLD_LEDGER=Path('/mnt/data/appcheck136/r3A/evidence/v101136/AUTHORIZED_MUTATION_UNIVERSE_96.csv')
OLD_LEDGER_SHA='6bce9bad3c0c3be87beaa95e987a3a3f0ada2c8ac6a4209ba6ca788698f9737d'
VERSION='v101.136'; REV='R4'; DATE='2026-09-07'; CACHE='luisa-24h-v101-136-r4'; STAGE='INTERIM_CLOSED_97_SUCCESSOR_R4_SINGLE_GRAMMAR_FIX'
RID='PASSION24.TEXT.RELATED_HOUR_13.BODY.P124'
OLD='C’était comme pour leur donner le premier salut de sa venue sur la terre le premier toc-toc frappé à la porte leur cœur, pour qu’elles Lui ouvrent et Le laissent entrer.'
NEW='C’était comme pour leur donner le premier salut de sa venue sur la terre le premier toc-toc frappé à la porte de leur cœur, pour qu’elles Lui ouvrent et Le laissent entrer.'
R6_SHA='35ee5c69fe0468d2e3ee2d963a7fa6667169c24d6c8023da2726b4cd8b50ed20'
R6_MAN='0d04190b166932086ed45141368bd4ae88b5a22806ca1e525a3e6a60a267f3ad'

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def files(root): return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}
def writej(p,o): p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def extract(t,n):
    m=re.search(rf'const\s+{re.escape(n)}\s*=\s*',t); assert m,n
    o,e=json.JSONDecoder().raw_decode(t[m.end():]); return o,m.end(),m.end()+e
def repl(t,n,o):
    old,s,e=extract(t,n); return t[:s]+json.dumps(o,ensure_ascii=False,separators=(',',':'))+t[e:]
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

def build(out):
    out=Path(out); shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
    assert sha_file(BASE)==BASE_SHA
    assert sha_file(OLD_LEDGER)==OLD_LEDGER_SHA
    with zipfile.ZipFile(BASE) as z:
        assert z.testzip() is None; z.extractall(out)
    basehash={k:sha_file(p) for k,p in files(out).items()}
    src=(out/'index.html').read_text(encoding='utf-8')
    assert src==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
    assert src.count(OLD)==1 and src.count(NEW)==0
    TL,_,_=extract(src,'TEXT_LIBRARY'); tm=tlmap(TL); assert RID in tm
    it,idx=tm[RID]; assert it['id']=='PASSION24.TEXT.RELATED_HOUR_13' and idx==123
    assert it['body'][idx]==OLD
    it['body'][idx]=NEW
    # prove this record carries no offset-bearing presentation authority requiring remap
    for n in ['SPEECH_DATA','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS']:
        o,_,_=extract(src,n)
        assert not (isinstance(o,dict) and RID in o), (n,'unexpected direct offset authority')
    topo,_,_=extract(src,'VISIBLE_PARAGRAPH_TOPOLOGY')
    for k,v in topo.items():
        if isinstance(v,dict): assert RID not in v,(k,'unexpected topology authority')
    flow,_,_=extract(src,'LDC_LIBRARY_FLOW_LAYOUT')
    # physical index 123 intentionally has no intra-cut; only a break-before at paragraph boundary
    for ent in flow.get(it['id'],[]):
        assert str(idx) not in (ent.get('intra') or {}),('unexpected flow intra',ent.get('entry_id'))
    # Register bounded post-R6 local correction in source-sync authority.
    auth,_,_=extract(src,'LDC_CURRENT_SYNC_AUTHORITY')
    auth['post_r6_local_grammar_corrections']={
        'operation_count':1,'date':DATE,'scope':'ONE_EXPLICIT_USER_AUTHORIZED_FRENCH_GRAMMAR_REPAIR_ONLY',
        'records':[RID],
        'note':'Inherited French-source omission “à la porte leur cœur” repaired to grammatical “à la porte de leur cœur”. Governing LDC R6 source remains unchanged and should receive separate upstream QA.'
    }
    t=repl(src,'TEXT_LIBRARY',TL)
    t=repl(t,'LDC_CURRENT_SYNC_AUTHORITY',auth)
    oldstage="const APP_EVIDENCE_STAGE = 'INTERIM_CLOSED_96_SUCCESSOR_R3_FOUR_PASS_RECONCILED';"; assert t.count(oldstage)==1
    t=t.replace(oldstage,f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
    # Build date comment only; public version stays v101.136.
    t=re.sub(r"const BUILD_DATE = '2026-09-07';[^\n]*",f"const BUILD_DATE = '{DATE}'; // {VERSION} {REV} / 97-record authorized interim successor",t,count=1)
    (out/'index.html').write_text(t,encoding='utf-8'); (out/'luisa_24_heures.html').write_text(t,encoding='utf-8')

    # Create new 97-record authority ledger by exact append to the prior 96.
    oldrows=list(csv.DictReader(OLD_LEDGER.open(encoding='utf-8-sig'))); assert len(oldrows)==96 and len({r['record_id'] for r in oldrows})==96
    fields=list(oldrows[0].keys())
    assert RID not in {r['record_id'] for r in oldrows}
    delta={
        'authority_id':'INTERIM-LOCAL-'+RID,
        'lane':'LOCAL_24H_POST_R3_USER_AUTHORIZED__UPSTREAM_HOLD_EXCEPTION',
        'record_id':RID,
        'epistemic_class':'A_RECENSION_INVARIANT_CLEAR_FRENCH_GRAMMAR_OMISSION',
        'operation_type':'REPLACE_TEXT_SPAN',
        'current_text':OLD,'current_sha256':sha_bytes(OLD.encode()),
        'target_text':NEW,'target_sha256':sha_bytes(NEW.encode()),
        'edit_operations_json':json.dumps([{'op':'insert','at':110,'text':'de '}],ensure_ascii=False,separators=(',',':')),
        'evidence_source':'User-reported 2026-09-07 correction; direct v101.136 R3 locus verification; French GE/Lumen Luminis source carries same inherited omission; Italian/English controls support intended “knock at hearts” semantics.',
        'source_authority':'LDC Tome 20 — 25 décembre 1926; French GE/Lumen Luminis; Italian/English independent controls',
        'known_contradiction_screen':'PASS__SOURCE_TYPO_INHERITED_NOT_SEMANTIC_VARIANT',
        'recension_sensitive':'False','future_dependency':'UPSTREAM_LDC_R6_GRAMMAR_QA_RECOMMENDED__ONE_PRIOR_HOLD_RECORD_EXPLICITLY_OVERRIDDEN_FOR_THIS_EXACT_INSERTION',
        'prior_status':'NEW_USER_REPORTED_CLEAR_GRAMMAR_DEFECT',
        'recommended_action':'AUTHORIZED_BY_USER_DO_IT_2026_09_07__APPLY_NOW',
        'rationale':'French construction “à la porte leur cœur” is grammatically defective; insertion of “de ” restores the required complement without changing meaning. Source witnesses confirm the semantic locus concerns knocking at hearts.'
    }
    allrows=oldrows+[delta]
    ev=out/'evidence/v101136_r4'; ev.mkdir(parents=True,exist_ok=True)
    ledger97=ev/'AUTHORIZED_MUTATION_UNIVERSE_97.csv'
    with ledger97.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(allrows)
    led97sha=sha_file(ledger97)
    with (ev/'AUTHORIZED_MUTATION_DELTA_1.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow(delta)
    writej(ev/'AUTHORIZATION_RECEIPT_R4.json',{
        'schema':'L24H_V101136_R4_AUTHORIZATION_RECEIPT_V1','authorization':'USER_DO_IT_2026_09_07',
        'release_engineering_predecessor':{'version':'v101.136 R3','sha256':BASE_SHA},
        'content_predecessor':{'version':'v101.135','sha256':CONTENT_PREDECESSOR_SHA},
        'prior_authorized_ledger_96_sha256':OLD_LEDGER_SHA,'new_authorized_ledger_97_sha256':led97sha,
        'new_delta_records':1,'total_authorized_records_relative_to_v101135':97,
        'exact_new_record':RID,'old_text':OLD,'new_text':NEW,
        'h23_source_critical_added':False,'upstream_hold_exception_records':1,'other_upstream_findings_consumed':False
    })
    writej(ev/'SOURCE_VERIFICATION_R4.json',{
        'record_id':RID,'locus':'Tome 20 — 25 décembre 1926 / linked text surfaced with Hour 13',
        'finding':'missing French preposition de','current_r3':OLD,'corrected_r4':NEW,
        'french_source_observation':'GE/Lumen Luminis Tome 20 also carries “à la porte leur cœur”; defect is inherited from source rather than introduced by app.',
        'italian_control':'25 Dec 1926 Italian control describes “Il primo picchio per bussare ai cuori”, confirming the semantic construction is a knock directed at hearts.',
        'english_control':'Independent English control renders “the first knock to knock at hearts”.',
        'adjudication':'CLEAR_FRENCH_SYNTAX_OMISSION__INSERT_DE__RECENSION_INVARIANT','confidence':'VERY_HIGH',
        'upstream_action':'Flag same defect separately for LDC corpus; do not mutate official R6 inside 24H workstream.'
    })
    writej(ev/'UPSTREAM_HOLD_EXCEPTION_R4.json',{'schema':'L24H_V101136_R4_UPSTREAM_HOLD_EXCEPTION_V1','record_id':RID,'prior_hold_population':300,'prior_hold_classification':'SOURCE_LAYOUT_NORMALIZATION | UPSTREAM_LDC_REQUIRED','prior_dependency_gate':'BLOCK_24H_UPSTREAM_WORDING_MUTATION_UNTIL_GOVERNED_LDC_SUCCESSOR_CONSUMES_EXACT_CORRECTION','new_authority':'EXPLICIT_USER_DO_IT_2026_09_07_AFTER_DIRECT_LOCUS_AND_SOURCE_RECHECK','exception_scope':'INSERT EXACTLY “de ” AT CHARACTER 110 IN THIS RECORD ONLY','other_upstream_findings_consumed':False,'official_ldc_r6_mutated_in_this_workstream':False,'reason':'New user-supplied concrete defect evidence plus source/grammar verification creates a new bounded authority that supersedes the prior dependency gate only for this one insertion.'})

    # Archive R3 current report and create R4 current report.
    hist=out/'reports/historical/v101136_r3'; hist.mkdir(parents=True,exist_ok=True)
    rp=out/'reports/V101136_R3_FOUR_PASS_RELEASE_RECONCILIATION.md'
    if rp.exists(): shutil.move(str(rp),str(hist/'V101136_R3_FOUR_PASS_RELEASE_RECONCILIATION.md'))
    report=out/'reports/V101136_R4_SINGLE_GRAMMAR_FIX.md'
    report.write_text(f'''# v101.136 R4 — Single Grammar Fix\n\n- Release-engineering predecessor: v101.136 R3 `{BASE_SHA}`.\n- Public app version remains **v101.136**; build revision is **R4**.\n- Exact new authorized mutation: **1 record**, `{RID}`.\n- R3 text: `à la porte leur cœur`.\n- R4 text: `à la porte de leur cœur`.\n- Total canonical delta relative to immutable v101.135 is now **97 records = 84 local + 13 official-R6 sync**.\n- New 97-record authority ledger SHA-256: `{led97sha}`.\n- No H23 source-critical finding is included. This record had previously been under the upstream dependency gate; the user’s new explicit authorization supersedes that gate **only for the exact insertion `de `**. No other upstream finding or action is consumed by R4.\n- The correction is recension-invariant French grammar. The French GE/Lumen Luminis source itself contains the inherited omission; Italian/English controls confirm the intended meaning concerns knocking at hearts.\n- Official LDC R6 is not mutated here; the corresponding source defect is flagged for its separate QA workstream.\n- Physical-device, installed-PWA, true-offline, accessibility and live-origin gates remain open; final public deployment remains unauthorized until those tests pass.\n''',encoding='utf-8')

    # Current documentation / QA identity.
    (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION} {REV}\n\nControlled device-test candidate. Relative to immutable v101.135, canonical devotional content now has exactly **97 authorized changed records = 84 local corrections + 13 official-LDC-R6 derivative synchronizations**.\n\nR4 adds exactly one new local grammar repair to R3: `{RID}`, `à la porte leur cœur` → `à la porte de leur cœur`. No H23 source-critical finding is added. This previously upstream-held locus is explicitly authorized for this exact `de ` insertion only; no other upstream finding or action is consumed.\n\nR4 supersedes R1/R2/R3 for deployment/device testing. Final public release remains unauthorized pending physical-device, installed-PWA update/persistence, true-offline, accessibility and live-origin exact-byte gates.\n''',encoding='utf-8')
    checklist=(out/'REAL_DEVICE_QA_CHECKLIST.md').read_text(encoding='utf-8')
    checklist=checklist.replace('v101.136 R3','v101.136 R4').replace('build_revision = R3','build_revision = R4').replace('luisa-24h-v101-136-r3','luisa-24h-v101-136-r4').replace('INTERIM_CLOSED_96_SUCCESSOR_R3_FOUR_PASS_RECONCILED',STAGE)
    checklist=checklist.replace('Do not use v101.136 R1 or R2 for deployment; R3 supersedes them for device testing. R3 changes no canonical devotional text relative to the corrected R2 content build.',
        'Do not use v101.136 R1, R2 or R3 for deployment; R4 supersedes them for device testing. R4 adds exactly one authorized grammar repair to R3.')
    marker='- H24: end-of-cycle panel, Méditée toggle and restart behaviour correct.'
    assert marker in checklist
    checklist=checklist.replace(marker,marker+'\n- Tome 20 — 25 décembre 1926 linked text: verify `à la porte de leur cœur` (with `de`).')
    (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(checklist,encoding='utf-8')
    # Update device results expected identity and add targeted row.
    p=out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'
    rows=list(csv.reader(p.open(encoding='utf-8-sig'))); header=rows[0]; data=rows[1:]
    for row in data:
        row[:]=[x.replace('R3','R4').replace('luisa-24h-v101-136-r3','luisa-24h-v101-136-r4') for x in row]
    data.append(['TARGETED','REG-08','at least iPhone + Samsung','YES','Tome 20 — 25 décembre 1926 linked text displays “à la porte de leur cœur”','','',''])
    with p.open('w',encoding='utf-8-sig',newline='') as f: csv.writer(f).writerows([header]+data)

    # Runtime identity and cache.
    sw=(out/'sw.js').read_text(encoding='utf-8'); assert "const CACHE_NAME = 'luisa-24h-v101-136-r3';" in sw
    sw=sw.replace("const CACHE_NAME = 'luisa-24h-v101-136-r3';",f"const CACHE_NAME = '{CACHE}';",1).replace('/* v101.136 R3 */','/* v101.136 R4 */',1)
    (out/'sw.js').write_text(sw,encoding='utf-8')
    v=json.loads((out/'version.json').read_text(encoding='utf-8'))
    v.update({'app_version':VERSION,'build_revision':REV,'build_date':DATE,'cache_name':CACHE,
      'release_scope':'Governed v101.136 R4 device-test candidate. Exact canonical delta relative to immutable v101.135: 97 records = 84 local corrections + 13 official-R6 derivative sync. R4 adds one explicit user-authorized French grammar repair at PASSION24.TEXT.RELATED_HOUR_13.BODY.P124. Excludes all H23 source-critical findings and consumes no other upstream finding or action; the sole scope exception is this exact user-authorized grammar insertion at P124.',
      'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.136 R4.',
      'overall_release_status':'R4_INTERNAL_VALIDATION_REQUIRED__CONTROLLED_DEVICE_TESTING_ONLY_AFTER_SHA_BOUND_PASS__FINAL_PUBLIC_DEPLOYMENT_UNAUTHORIZED',
      'external_open_gates':['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update v101.135→v101.136 R4','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'],
      'postfreeze_reopen_evidence':'R4 exact-ZIP validation is external and SHA-bound; package records the one-record R4 mutation authority and leaves device/live gates open.'})
    writej(out/'version.json',v)
    m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));m['version']=VERSION;m['build_revision']=REV;writej(out/'manifest.json',m)

    # Current metadata.
    active=['README.md','REAL_DEVICE_QA_CHECKLIST.md','reports/V101136_R4_SINGLE_GRAMMAR_FIX.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md']
    writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'active_documents':active,'active_test_artifacts':['REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'],'historical_reports_root':'reports/historical/','rule':'Only listed active documents are current; predecessor/superseded reports are historical.'})
    writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'content_authority_root':'evidence/v101136_r4','content_predecessor_24h':{'version':'v101.135','sha256':CONTENT_PREDECESSOR_SHA},'release_engineering_predecessor':{'version':'v101.136 R3','sha256':BASE_SHA},'prior_authorized_ledger_96_sha256':OLD_LEDGER_SHA,'authorized_ledger_97_sha256':led97sha,'governing_ldc_r6':{'version':'v2.19.65-R1B','official_zip_sha256':R6_SHA,'corpus_manifest_sha256':R6_MAN},'r4_delta_records':1,'r4_delta_record_id':RID,'upstream_hold_exception_records':1,'other_upstream_findings_consumed':False,'final_exact_zip_validation':'EXTERNAL_SHA_BOUND'})
    writej(out/'metadata/build_provenance.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,'release_engineering_baseline':'v101.136 R3','release_engineering_baseline_zip_sha256':BASE_SHA,'content_predecessor_version':'v101.135','content_predecessor_zip_sha256':CONTENT_PREDECESSOR_SHA,'prior_authorized_ledger_96_sha256':OLD_LEDGER_SHA,'authorized_ledger_97_sha256':led97sha,'canonical_text_changed_from_r3':True,'canonical_text_delta_from_r3_records':1,'canonical_total_delta_from_v101135_records':97,'upstream_hold_exception_records':1,'other_upstream_findings_consumed':False,'stable_record_ids_unchanged':True,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'r4_record_id':RID,'r4_old_sha256':sha_bytes(OLD.encode()),'r4_new_sha256':sha_bytes(NEW.encode()),'final_validation':'EXTERNAL_SHA_BOUND_EXACT_ZIP'})
    (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} Scope Authority\n\nCanonical content authority is exactly **97 records relative to immutable v101.135**: the prior 96-record ledger plus one explicit user-authorized grammar repair `{RID}`. Combined ledger SHA-256: `{led97sha}`. R4 authorizes no other canonical text mutation. No H23 source-critical finding is authorized. This locus is one explicit exception to the former upstream dependency gate, limited to the exact insertion `de `; no other upstream finding or action is authorized. Any further canonical text change requires new authority.\n''',encoding='utf-8')
    writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'package_rule':'Package does not self-certify final ZIP bytes. R4 post-freeze validation must SHA-bind the exact ZIP.','internal_package_gates':'REQUIRE_EXTERNAL_SHA_BOUND_PASS_BEFORE_DEVICE_TESTING','physical_device_claims':'NOT_TESTED','public_deployment_authorized':False})
    writej(out/'metadata/current_gate_map.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'internal_gates':['exact R3→R4 one-record delta','exact v135→R4 97-record delta','runtime/package regression','active-report consistency','final reopened recheck'],'external_open_gates':['physical devices','live-origin exact-byte binding','installed-PWA update/persistence','true offline cold reopen','VoiceOver/TalkBack'],'public_release':'UNAUTHORIZED'})
    shutil.copy2(Path(__file__),out/'scripts/build_v101136_r4_single_grammar_fix.py')
    writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_builder':'scripts/build_v101136_r4_single_grammar_fix.py','predecessor_builder':'scripts/build_v101136_r3_four_pass_reconciliation.py retained as historical tooling','runtime_validation':'external exact-ZIP v101.136 harnesses; R4 targeted grammar probe required'})
    writej(out/'metadata/builder_input_manifest.json',{'version':VERSION,'build_revision':REV,'release_engineering_predecessor_zip_sha256':BASE_SHA,'content_predecessor_v101135_zip_sha256':CONTENT_PREDECESSOR_SHA,'prior_authorized_ledger_96_sha256':OLD_LEDGER_SHA,'authorized_ledger_97_sha256':led97sha,'governing_ldc_r6_zip_sha256':R6_SHA,'governing_ldc_r6_corpus_manifest_sha256':R6_MAN})

    # Overlay + manifests.
    cur=files(out); changed=sorted(k for k,p in cur.items() if k not in basehash or sha_file(p)!=basehash[k]); removed=sorted(set(basehash)-set(cur))
    for x in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
        if x not in changed: changed.append(x)
    writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101136_R4_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':'v101.136 R3','baseline_zip_sha256':BASE_SHA,'changed_or_added':sorted(changed),'removed':removed})
    ex={'metadata/hash_manifest.json','metadata/package_manifest.json'};lst=[]
    for k,p in sorted(files(out).items()):
        if k in ex:continue
        lst.append({'path':k,'size':p.stat().st_size,'sha256':sha_file(p)})
    writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
    writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
    return {'version':VERSION,'revision':REV,'files':len(files(out)),'r4_new_records':1,'total_authorized_records':97,'ledger97_sha256':led97sha,'r4_record':RID,'old_sha256':sha_bytes(OLD.encode()),'new_sha256':sha_bytes(NEW.encode()),'cache':CACHE,'stage':STAGE}

def freeze(root,zp):
    root=Path(root);zp=Path(zp);zp.unlink(missing_ok=True)
    with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(root.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(root).as_posix();info=zipfile.ZipInfo(rel,(2026,9,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16);z.writestr(info,p.read_bytes())
    return sha_file(zp)
if __name__=='__main__':
    import sys
    r=build(sys.argv[1]);h=freeze(sys.argv[1],sys.argv[2]);print(json.dumps(r,indent=2,ensure_ascii=False));print('ZIP',h)
