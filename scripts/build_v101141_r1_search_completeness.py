from pathlib import Path
import zipfile, hashlib, json, shutil, re, sys, os

VERSION='v101.141'; REV='R1'; STAGE='SEARCH_COMPLETENESS_SUCCESSOR_R1'; DATE='2026-09-09'; CACHE='luisa-24h-v101-141-r1'
BASE_VERSION='v101.140 R1'; BASE_SHA='c84f2266e82de38b2adb70873f15f4da9046d504ff02a7cb93e389aec7bd7835'
AUTH_SHA='4bd256323432c4c86bf665a0de4912d6c82d610001e0af3178d453bcc977ac42'
PROTECTED_CONSTS=['CORPUS','TEXT_LIBRARY','SPEECH_DATA','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS','VISIBLE_PARAGRAPH_TOPOLOGY','LDC_LIBRARY_FLOW_LAYOUT','INTERNAL_SUBHEADINGS','CONTINUITY_GROUPS','HOUR_LINKED_TEXTS','PASSION24_RELATED_BY_HOUR']

def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def files(root):
    root=Path(root); return {p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file()}

def writej(path,obj):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

def exact_replace(s,old,new,label):
    n=s.count(old)
    assert n==1,(label,n)
    return s.replace(old,new,1)

def raw_const(text,name):
    marker='const '+name+' = '
    i=text.find(marker); assert i>=0,name
    start=i+len(marker)
    while start<len(text) and text[start].isspace(): start+=1
    # support object/array/string/scalar up to semicolon while respecting quotes/brackets
    if text[start] in '[{':
        stack=[]; ins=None; esc=False
        pairs={'{':'}','[':']'}
        for j in range(start,len(text)):
            ch=text[j]
            if ins:
                if esc: esc=False
                elif ch=='\\': esc=True
                elif ch==ins: ins=None
                continue
            if ch in "'\"`": ins=ch; continue
            if ch in pairs: stack.append(pairs[ch])
            elif ch in ']}':
                assert stack and ch==stack[-1],(name,j,ch); stack.pop()
                if not stack: return text[start:j+1], start, j+1
        raise AssertionError(('unterminated',name))
    # scalar/string expression to semicolon
    j=text.find(';',start); assert j>=0,name
    return text[start:j], start, j

def freeze(root,zp):
    root=Path(root); zp=Path(zp); zp.unlink(missing_ok=True)
    with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(root.rglob('*')):
            if not p.is_file(): continue
            rel=p.relative_to(root).as_posix()
            info=zipfile.ZipInfo(rel,(2026,9,9,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=(0o644<<16)
            z.writestr(info,p.read_bytes())
    return sha_file(zp)

def build(base_zip,authority_json,out_dir):
    base_zip=Path(base_zip); authority_json=Path(authority_json); out=Path(out_dir)
    assert sha_file(base_zip)==BASE_SHA,(sha_file(base_zip),BASE_SHA)
    assert sha_file(authority_json)==AUTH_SHA,(sha_file(authority_json),AUTH_SHA)
    auth=json.loads(authority_json.read_text(encoding='utf-8'))
    assert auth['immutable_predecessor_zip_sha256']==BASE_SHA
    shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
    with zipfile.ZipFile(base_zip) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))
        z.extractall(out)
    base_files=files(out); base_hash={k:sha_file(v) for k,v in base_files.items()}
    idx=(out/'index.html').read_text(encoding='utf-8')
    mir=(out/'luisa_24_heures.html').read_text(encoding='utf-8')
    assert idx==mir
    protected_before={n:raw_const(idx,n)[0] for n in PROTECTED_CONSTS}

    t=idx
    # 1. Title-index helper. Query-dependent only; never adds title rows during empty direct-speech browsing.
    old="""  function addResult(label, para, type, kindLabel, target) {\n    if (!para || !para.t) return;\n    if (!norm(para.t).includes(q)) return;\n    results.push({label, para, type, kindLabel, target});\n  }\n  function addSpeechResults(label, para, target) {"""
    new="""  function addResult(label, para, type, kindLabel, target) {\n    if (!para || !para.t) return;\n    if (!norm(para.t).includes(q)) return;\n    results.push({label, para, type, kindLabel, target});\n  }\n  function addTitleResult(label, titleText, type, kindLabel, target, stableId) {\n    if (!hasQuery || !titleText || !norm(titleText).includes(q)) return;\n    results.push({label, para:{id:stableId || target.anchor || target.id || '', t:titleText}, type, kindLabel, target});\n  }\n  function addSpeechResults(label, para, target) {"""
    t=exact_replace(t,old,new,'addTitleResult helper')

    # 2. Hour titles explicitly indexed and routed to first visible meditation paragraph.
    old="""  for (const hour of CORPUS.hours) {\n    for (const p of getDisplayParagraphsForHour(hour)) {"""
    new="""  for (const hour of CORPUS.hours) {\n    const hourDisplayParagraphs = getDisplayParagraphsForHour(hour);\n    const hourTitleTarget = hourDisplayParagraphs[0] || (hour.paragraphs || [])[0] || null;\n    if (hourTitleTarget) addTitleResult(`${hour.hour_number}e Heure — ${hour.title}`, hour.title, 'hour', 'Heure', {kind:'hour', n:hour.hour_number, paraId:hourTitleTarget.id, tab:'meditation'}, hourTitleTarget.id);\n    for (const p of hourDisplayParagraphs) {"""
    t=exact_replace(t,old,new,'hour title index')

    # 3. Prayer titles explicitly indexed and routed to prayer top.
    old="""  for (const pr of CORPUS.prayers) {\n    for (const p of (pr.paragraphs||[])) {"""
    new="""  for (const pr of CORPUS.prayers) {\n    addTitleResult(pr.title, pr.title, 'prayer', 'Prière', {kind:'prayer', id:pr.prayer_id, anchor:null}, pr.prayer_id);\n    for (const p of (pr.paragraphs||[])) {"""
    t=exact_replace(t,old,new,'prayer title index')

    # 4. Section titles explicitly indexed and routed to section top.
    old="""  for (const s of CORPUS.sections) {\n    // Structured-paragraph sections (e.g. BENEFITS) — search paragraphs directly so anchors match rendered DOM"""
    new="""  for (const s of CORPUS.sections) {\n    addTitleResult(s.title, s.title, 'section', 'Complément', {kind:'section', id:s.section_id, anchor:null}, s.section_id);\n    // Structured-paragraph sections (e.g. BENEFITS) — search paragraphs directly so anchors match rendered DOM"""
    t=exact_replace(t,old,new,'section title index')

    # 5. Add direct-speech extraction for visible library bodies. Only needed under the speech filter,
    # avoiding duplicate speech rows flooding ordinary Tout results while all library prose remains ordinarily searchable.
    old="""    (item.body || []).forEach((t, i) => {\n      if (!t) return;\n      const nt = norm(t);\n      if (!nt.includes(q)) return;\n      const skipLine = isLibraryOldIndexLine(t) || isLibraryTextesLabelLine(t);\n      const anchor = skipLine ? null : makeLibraryParaId(item.id, i);\n      const idx = nt.indexOf(q);\n      const snip = t.slice(Math.max(0, idx - 55), Math.min(t.length, idx + q.length + 90));\n      results.push({label:item.title, para:{id:anchor || item.id, t:snip}, type:'section', kindLabel:'Complément', target:{kind:'library', id:item.id, anchor}});\n    });"""
    new="""    (item.body || []).forEach((t, i) => {\n      if (!t) return;\n      const skipLine = isLibraryOldIndexLine(t) || isLibraryTextesLabelLine(t);\n      const anchor = skipLine ? null : makeLibraryParaId(item.id, i);\n      if (currentFilter === 'speech' && anchor) addSpeechResults(item.title, {id:anchor, t}, {kind:'library', id:item.id, anchor});\n      const nt = norm(t);\n      if (!nt.includes(q)) return;\n      const idx = nt.indexOf(q);\n      const snip = t.slice(Math.max(0, idx - 55), Math.min(t.length, idx + q.length + 90));\n      results.push({label:item.title, para:{id:anchor || item.id, t:snip}, type:'section', kindLabel:'Complément', target:{kind:'library', id:item.id, anchor}});\n    });"""
    t=exact_replace(t,old,new,'library direct speech')

    # 6. Exact total is already computed; remove misleading + suffix while retaining explicit 60-item display note.
    old="""  const countLabel = hasQuery ? `${allFiltered.length}${allFiltered.length>SEARCH_RESULT_LIMIT?'+':''} résultat${allFiltered.length>1?'s':''} pour « ${escHtml(query)} »` : `${allFiltered.length}${allFiltered.length>SEARCH_RESULT_LIMIT?'+':''} parole${allFiltered.length>1?'s':''} directe${allFiltered.length>1?'s':''}`;"""
    new="""  const countLabel = hasQuery ? `${allFiltered.length} résultat${allFiltered.length>1?'s':''} pour « ${escHtml(query)} »` : `${allFiltered.length} parole${allFiltered.length>1?'s':''} directe${allFiltered.length>1?'s':''}`;"""
    t=exact_replace(t,old,new,'exact result count')

    # Release identity only.
    t=exact_replace(t,"const APP_VERSION = 'v101.140';",f"const APP_VERSION = '{VERSION}';",'APP_VERSION')
    t=exact_replace(t,"const BUILD_REVISION = 'R1';",f"const BUILD_REVISION = '{REV}';",'BUILD_REVISION')
    t=exact_replace(t,"const APP_EVIDENCE_STAGE = 'LDC_FAST_MODE_DERIVATIVE_CORRECTION_SUCCESSOR_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",'stage')
    t=re.sub(r"const BUILD_DATE = '2026-09-09';[^\n]*",f"const BUILD_DATE = '{DATE}'; // {VERSION} {REV} / search-completeness successor; corpus and speaker authority unchanged",t,count=1)
    assert t!=idx
    (out/'index.html').write_text(t,encoding='utf-8'); (out/'luisa_24_heures.html').write_text(t,encoding='utf-8')

    # PWA/update identity.
    sw=(out/'sw.js').read_text(encoding='utf-8')
    sw=exact_replace(sw,'/* v101.140 R1 */','/* v101.141 R1 */','sw version')
    sw=exact_replace(sw,"const CACHE_NAME = 'luisa-24h-v101-140-r1';",f"const CACHE_NAME = '{CACHE}';",'sw cache')
    (out/'sw.js').write_text(sw,encoding='utf-8')
    man=json.loads((out/'manifest.json').read_text(encoding='utf-8')); assert man['version']=='v101.140' and man['build_revision']=='R1'; man['version']=VERSION; man['build_revision']=REV; writej(out/'manifest.json',man)
    v=json.loads((out/'version.json').read_text(encoding='utf-8')); assert v['app_version']=='v101.140' and v['build_revision']=='R1'
    gates=['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update to v101.141 R1 from the currently deployed build','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing']
    v.update({
      'app_version':VERSION,'build_revision':REV,'build_date':DATE,'cache_name':CACHE,
      'release_scope':'Search-only completeness successor of exact immutable v101.140 R1. Extends Paroles directes to visible linked-library/LDC body records using existing SPEECH_DATA, explicitly indexes Hour/Prayer/Section titles, and displays exact search-result totals without a misleading plus suffix. CORPUS, TEXT_LIBRARY, speaker authority, stable IDs, search normalizer, personal-data schemas and unrelated UI are unchanged.',
      'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update/persistence, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.141 R1.',
      'overall_release_status':'V101141_R1_SEARCH_COMPLETENESS_CONTROLLED_DEVICE_TEST_CANDIDATE__FINAL_PUBLIC_DEPLOYMENT_UNAUTHORIZED',
      'known_blockers':gates,'external_open_gates':gates,
      'postfreeze_reopen_evidence':'Exact v101.141 R1 successor ZIP requires external SHA-bound final recheck before controlled device testing.'
    })
    writej(out/'version.json',v)

    # Current report and evidence. Retain predecessor reports as historical evidence unchanged.
    ev=out/'evidence/v101141_r1'; ev.mkdir(parents=True,exist_ok=True)
    shutil.copy2(authority_json,ev/'V101141_R1_SEARCH_COMPLETENESS_AUTHORITY.json')
    report=f'''# {VERSION} {REV} — Search completeness successor\n\n- Immutable predecessor: `{BASE_VERSION}` SHA-256 `{BASE_SHA}`.\n- Search authority SHA-256: `{AUTH_SHA}`.\n- Scope: three search-only repairs — library/LDC direct-speech coverage, explicit Hour/Prayer/Section title indexing, exact result-count display.\n- Corpus text mutations: **0**. `TEXT_LIBRARY` mutations: **0**. `SPEECH_DATA` mutations: **0**. Stable-ID mutations: **0**. Search-normalizer mutations: **0**.\n- Storage schema: **{v.get('storage_schema',8)} unchanged**. Personal snapshot schema: **{v.get('personal_snapshot',5)} unchanged**.\n- Final public deployment remains **UNAUTHORIZED** pending external device/live-origin/PWA/offline/accessibility gates.\n'''
    (out/'reports/V101141_R1_SEARCH_COMPLETENESS_SUCCESSOR.md').write_text(report,encoding='utf-8')
    writej(ev/'SEARCH_CODE_CHANGE_LEDGER.json',{
      'schema':'L24H_V101141_R1_SEARCH_CODE_CHANGE_LEDGER_V1','status':'BUILT_PENDING_EXTERNAL_VALIDATION','predecessor_zip_sha256':BASE_SHA,'authority_sha256':AUTH_SHA,
      'changes':[
        {'id':'SEARCH.DIRECT_SPEECH.LIBRARY','description':'Under Paroles directes, enumerate visible TEXT_LIBRARY body paragraphs with existing SPEECH_DATA and route to exact library stable anchors.'},
        {'id':'SEARCH.TITLES.HOUR_PRAYER_SECTION','description':'Add explicit title results for Hour, Prayer and Section titles, routed to owning item.'},
        {'id':'SEARCH.RESULT_COUNT.EXACT','description':'Remove plus suffix because allFiltered.length is exact; retain 60-item display-limit note.'}
      ],
      'forbidden_mutations_observed':0
    })

    # Protected corpus/speaker parity after code changes.
    final=(out/'index.html').read_text(encoding='utf-8'); assert final==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
    parity={n:(raw_const(final,n)[0]==protected_before[n]) for n in PROTECTED_CONSTS}; assert all(parity.values()),[n for n,vv in parity.items() if not vv]
    writej(ev/'PROTECTED_CORPUS_AND_SPEAKER_PARITY.json',{
      'schema':'L24H_V101141_R1_PROTECTED_CORPUS_AND_SPEAKER_PARITY_V1','status':'PASS','constants':parity,
      'corpus_text_delta':0,'text_library_delta':0,'speech_data_delta':0,'stable_id_delta':0,'search_normalizer_delta':0
    })

    # README, QA and current metadata.
    (out/'README.md').write_text(f'''# {VERSION} {REV} — current controlled device-test candidate\n\nCurrent stage: `{STAGE}`. Exact predecessor `{BASE_VERSION}` SHA-256 `{BASE_SHA}`. Search-only successor authorized by `{AUTH_SHA}`: linked-library/LDC direct-speech coverage, explicit Hour/Prayer/Section title indexing, and exact search-result totals. Corpus, `TEXT_LIBRARY`, speaker attribution, stable IDs and personal-data schemas are unchanged. Final public deployment remains unauthorized.\n''',encoding='utf-8')
    qa=f'''# Real-device QA checklist — {VERSION} {REV}\n\nUse only the exact externally SHA-bound {VERSION} {REV} candidate. Internal browser evidence does not substitute for physical-device/PWA/accessibility gates.\n\n## Search completeness\n- Search each of the 24 exact Hour titles; confirm the owning Hour appears and opens correctly.\n- Search each of the 5 exact Prayer titles; confirm the owning prayer appears and opens correctly.\n- Search each Section title; confirm the owning complement appears and opens correctly.\n- Under `Paroles directes`, verify representative linked-LDC/library speech for Jésus, Marie and Père appears and opens at the exact stable paragraph.\n- With no query under `Paroles directes`, verify speaker filters Tous/Jésus/Père/Marie operate normally.\n- Run a query with more than 60 matches; verify the exact total is displayed without `+` and the UI still states that only the first 60 are shown.\n- Verify accent/ligature folding, search highlighting, category filters and search deep links remain correct.\n\n## Protected regression\n- Canonical Hours, Réflexions, Prières, Compléments and linked-LDC ordinary text search remain correct.\n- All 36 v101.140 linked-LDC corrected records remain searchable under corrected wording.\n- Existing notes/highlights/progression/last-place/theme/font survive installed-PWA update.\n\n## External gates\n- Physical iPhone validation.\n- Physical iPad portrait and landscape validation.\n- Physical Samsung/Android validation.\n- Live-origin exact-byte binding.\n- Installed-PWA update and three close/reopen cycles.\n- True offline cold reopen.\n- Representative VoiceOver and TalkBack navigation.\n\nFinal public deployment remains unauthorized until all external gates are evidenced.\n'''
    (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(qa,encoding='utf-8')
    rows=[
      'test_id,platform,required,expected,actual,status,notes',
      f'ID-01,browser,YES,Aide shows {VERSION} {REV} and stage {STAGE},,,',
      'SEARCH-TITLE-HOUR,iPhone;iPad;Samsung,YES,24/24 exact Hour titles return and open owning Hour,,,',
      'SEARCH-TITLE-PRAYER,iPhone;iPad;Samsung,YES,5/5 exact Prayer titles return and open owning prayer,,,',
      'SEARCH-TITLE-SECTION,iPhone;iPad;Samsung,YES,All exact Section titles return and open owning complement,,,',
      'SEARCH-SPEECH-LDC,iPhone;iPad;Samsung,YES,Representative Jésus Marie Père linked-library speech appears under Paroles directes and opens exact anchor,,,',
      'SEARCH-COUNT,iPhone;iPad;Samsung,YES,Exact total shown without plus when more than 60 results and limit note remains,,,',
      'SEARCH-REGRESSION,iPhone;iPad;Samsung,YES,Normalization filters highlighting deep links and 36 corrected LDC searches remain correct,,,',
      'STATE-01,iPhone;iPad;Samsung,YES,Existing notes highlights progression last-place theme and font survive installed-PWA update,,,',
      'PWA-01,iPhone;iPad;Samsung,YES,Installed-PWA update reaches exact SHA-bound v101.141 R1 and survives three close/reopen cycles,,,',
      'OFFLINE-01,iPhone;iPad;Samsung,YES,True offline cold reopen succeeds after update,,,',
      'A11Y-01,iPhone;iPad;Samsung,YES,Representative VoiceOver or TalkBack navigation is usable,,,'
    ]
    (out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').write_text('\n'.join(rows)+'\n',encoding='utf-8')

    writej(out/'metadata/build_provenance.json',{
      'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,'baseline_version':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,'search_authority_sha256':AUTH_SHA,
      'search_changes':3,'corpus_text_changes':0,'text_library_changes':0,'speech_data_changes':0,'stable_id_changes':0,'search_normalizer_changes':0,
      'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'final_validation':'EXTERNAL_EXACT_ZIP_RECHECK_REQUIRED'
    })
    writej(out/'metadata/current_evidence_lineage.json',{
      'version':VERSION,'build_revision':REV,'stage':STAGE,'current_evidence_root':'evidence/v101141_r1','immediate_build_predecessor':{'version':BASE_VERSION,'sha256':BASE_SHA},
      'search_authority_sha256':AUTH_SHA,'content_authority':'v101.140 R1 corpus and speaker metadata inherited byte-for-byte','search_scope':'three authorized search-completeness repairs only'
    })
    writej(out/'metadata/current_gate_map.json',{
      'version':VERSION,'build_revision':REV,'stage':STAGE,
      'internal_gates':['exact v101.140 R1 SHA binding','protected corpus/TEXT_LIBRARY/SPEECH_DATA parity','search title coverage','library/LDC direct-speech coverage','exact result-count display','search normalization/filter/deep-link regression','full app regression','deterministic rebuild','four-pass adversarial audit','fresh ZIP reopen'],
      'external_open_gates':gates,'public_release':'UNAUTHORIZED'
    })
    writej(out/'metadata/release_evidence_lifecycle.json',{
      'version':VERSION,'build_revision':REV,'stage':STAGE,'package_rule':'Package does not self-certify final ZIP bytes; exact frozen v101.141 R1 ZIP must receive external SHA-bound final validation receipt.',
      'immediate_build_predecessor':BASE_VERSION,'immediate_build_predecessor_sha256':BASE_SHA,'corpus_text_changed':False,'search_code_changed':True,'physical_device_claims':'NOT_TESTED','public_deployment_authorized':False
    })
    (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} scope authority\n\nAuthorized scope is exclusively the three search-completeness repairs in SHA-256 `{AUTH_SHA}` against immutable `{BASE_VERSION}` SHA-256 `{BASE_SHA}`.\n\nForbidden: corpus or `TEXT_LIBRARY` text mutation; `SPEECH_DATA`/speaker reinterpretation; stable-ID mutation; search-normalizer change; personal-data schema change; unrelated UI change.\n\nFinal public deployment remains externally gated.\n''',encoding='utf-8')
    writej(out/'metadata/current_tooling_inventory.json',{
      'version':VERSION,'build_revision':REV,'stage':STAGE,'current_builder':'scripts/build_v101141_r1_search_completeness.py',
      'builder_contract':'Exact SHA-bound v101.140 R1 predecessor + exact search authority; three search-only code repairs; protected corpus/speaker constants exact parity.'
    })
    writej(out/'metadata/builder_input_manifest.json',{
      'version':VERSION,'build_revision':REV,'predecessor_v101140_r1_zip_sha256':BASE_SHA,'search_authority_sha256':AUTH_SHA
    })
    writej(out/'metadata/active_report_inventory.json',{
      'version':VERSION,'build_revision':REV,'stage':STAGE,
      'active_documents':['README.md','REAL_DEVICE_QA_CHECKLIST.md','reports/V101141_R1_SEARCH_COMPLETENESS_SUCCESSOR.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md'],
      'active_test_artifacts':['REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'],'historical_reports_root':'reports/historical/','rule':'Only listed active documents are current.'
    })

    # Embed current builder.
    shutil.copy2(Path(__file__),out/'scripts/build_v101141_r1_search_completeness.py')

    # Final protected checks and exact search code assertions.
    final=(out/'index.html').read_text(encoding='utf-8'); assert final==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
    for n in PROTECTED_CONSTS: assert raw_const(final,n)[0]==protected_before[n],n
    assert "function addTitleResult" in final
    assert "currentFilter === 'speech' && anchor" in final
    assert "allFiltered.length>SEARCH_RESULT_LIMIT?'+':''" not in final
    assert "const APP_VERSION = 'v101.141';" in final and STAGE in final
    assert CACHE in (out/'sw.js').read_text(encoding='utf-8')
    vv=json.loads((out/'version.json').read_text(encoding='utf-8')); assert vv['storage_schema']==8 and vv['personal_snapshot']==5

    # Overlay scope before manifests.
    cur=files(out); removed=sorted(set(base_files)-set(cur)); assert removed==[],removed
    changed_or_added=sorted(k for k,p in cur.items() if k not in base_hash or sha_file(p)!=base_hash[k])
    writej(out/'metadata/full_build_overlay_manifest.json',{
      'schema':'L24H_V101141_R1_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,
      'changed_or_added':sorted(set(changed_or_added)|{'metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json'}),'removed':[],
      'corpus_text_delta':'ZERO','text_library_delta':'ZERO','speech_data_delta':'ZERO','stable_id_delta':'ZERO','search_code_changes':3
    })
    ex={'metadata/hash_manifest.json','metadata/package_manifest.json'}; lst=[]
    for k,p in sorted(files(out).items()):
        if k in ex: continue
        lst.append({'path':k,'size':p.stat().st_size,'sha256':sha_file(p)})
    writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
    writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
    return {'version':VERSION,'revision':REV,'stage':STAGE,'base_sha256':BASE_SHA,'authority_sha256':AUTH_SHA,'files':len(files(out)),'manifested_nonself_files':len(lst),'cache':CACHE}

if __name__=='__main__':
    if len(sys.argv)!=5: raise SystemExit('Usage: build.py <v101140_R1.zip> <authority.json> <out_dir> <out.zip>')
    info=build(sys.argv[1],sys.argv[2],sys.argv[3]); zsha=freeze(sys.argv[3],sys.argv[4]); info['zip_sha256']=zsha; info['zip_size']=Path(sys.argv[4]).stat().st_size; print(json.dumps(info,ensure_ascii=False,indent=2))
