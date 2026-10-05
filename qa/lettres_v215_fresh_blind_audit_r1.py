from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json, hashlib

BASE='http://127.0.0.1:8120/lettres-v2.15-b2-contrast-repair/index.html'
PUBLIC='https://louisriv26.github.io/App-Test/lettres-v2.15-b2-contrast-repair/index.html'
OUT=[]
FAIL=[]

def rec(name,ok,detail=None):
    row={'name':name,'ok':bool(ok),'detail':detail}
    OUT.append(row)
    print('BLIND',name,'PASS' if ok else 'FAIL',repr(detail),flush=True)
    if not ok:
        FAIL.append(row)
        raise AssertionError(f'{name}: {detail}')

def trap(page,label):
    errors=[]
    page.on('pageerror',lambda e: errors.append('page:'+str(e)))
    page.on('console',lambda m: errors.append('console:'+m.text) if m.type=='error' else None)
    return lambda: rec(label+':no_runtime_errors',len(errors)==0,errors)

def ready(p):
    p.locator('#loading').wait_for(state='detached',timeout=30000)
    expect(p.locator('#letter-list .letter-item')).to_have_count(136)
    expect(p.locator('.build-meta').first).to_contain_text('v2.15')
    p.wait_for_timeout(700)
    if p.locator('#help-overlay').is_visible():
        p.evaluate("()=>{try{closeHelp(true)}catch(e){}}")

with sync_playwright() as pw:
    # 1) Feature-interaction challenge: filters, paths, read/favourite state.
    b=pw.chromium.launch(headless=True)
    c=b.new_context(viewport={'width':390,'height':844},locale='fr-FR',service_workers='allow')
    c.add_init_script("localStorage.setItem('lp_onboarded','1')")
    p=c.new_page(); done=trap(p,'chromium:interaction')
    p.goto(BASE+'?blind=interaction',wait_until='domcontentloaded',timeout=30000); ready(p)
    p.locator('#pnav-list').click()
    chips=p.evaluate("()=>FILTER_CHIPS.map(x=>({id:x.id,label:x.label}))")
    rec('filters:count_10',len(chips)==10,chips)
    expected_topics={'Divine Volonté','Croix','Paix','Prêtres','Deuil','Confiance','Propagation des écrits'}
    rec('filters:topic_set',set(x['id'] for x in chips if x['id'] not in {'all','fav','unread'})==expected_topics,chips)
    for item in chips:
        fid=item['id']
        p.locator(f'[data-action="filter"][data-filter="{fid}"]').click()
        p.wait_for_timeout(180)
        n=p.locator('#letter-list .letter-item').count()
        if fid=='all':
            rec('filter:all_136',n==136,n)
        elif fid=='fav':
            rec('filter:fav_initial_empty',n==0,n)
        elif fid=='unread':
            rec('filter:unread_initial_136',n==136,n)
        else:
            rec('filter:'+fid+':nonempty',n>0,n)

    # State interaction from a path member used in the historical Abandon defect.
    p.locator('[data-action="filter"][data-filter="all"]').click(); p.wait_for_timeout(100)
    p.locator('#letter-list .letter-item[data-n="44"]').click()
    p.locator('#pr-fav-btn').click(); p.locator('#pr-read-btn').click()
    p.get_by_role('button',name='Retour à la liste').click()
    p.locator('[data-action="filter"][data-filter="fav"]').click(); p.wait_for_timeout(150)
    rec('filter:fav_reflects_reader_state',p.locator('#letter-list .letter-item[data-n="44"]').count()==1,p.locator('#letter-list .letter-item').count())
    p.locator('[data-action="filter"][data-filter="unread"]').click(); p.wait_for_timeout(150)
    rec('filter:unread_excludes_44',p.locator('#letter-list .letter-item[data-n="44"]').count()==0,p.locator('#letter-list .letter-item').count())

    # All six parcours, including Abandon, must be structurally present and usable.
    p.locator('#pnav-explore').click(); p.wait_for_timeout(150)
    paths=p.evaluate("()=>PATHS.map(x=>({id:x.id,label:x.label,letters:x.letters.slice()}))")
    rec('paths:count_6',len(paths)==6,paths)
    rec('paths:all_seven',all(len(x['letters'])==7 for x in paths),paths)
    abandon=next((x for x in paths if x['id']=='abandon'),None)
    rec('paths:abandon_exact',abandon is not None and abandon['letters']==[44,50,58,74,93,107,131],abandon)
    for path in paths:
        p.evaluate("(id)=>openPath(id)",path['id']); p.wait_for_timeout(100)
        rec('path:'+path['id']+':seven_items',p.locator('.path-letter-item').count()==7,p.locator('.path-letter-item').count())
        p.evaluate("()=>closePath()")
    p.evaluate("()=>openPath('abandon')"); p.wait_for_timeout(120)
    rec('path:abandon_read_state_visible',p.locator('.path-letter-item.done[data-n="44"]').count()==1,p.locator('.path-letter-item.done').count())
    p.evaluate("()=>closePath()")

    # Import parser challenge: unsupported/incomplete/dangerous payloads must reject without mutation.
    before=p.evaluate("()=>Object.fromEntries(['lp_favs','lp_notes','lp_highlights','lp_read','lp_state_schema'].map(k=>[k,localStorage.getItem(k)]))")
    rejects=p.evaluate("""()=>{
      const base={format:'luisa-letters-user-data',app_id:'lettres-de-luisa-piccarreta'};
      const cases={
        unsupported:JSON.stringify({...base,schema_version:999,data:{}}),
        incomplete:JSON.stringify({...base,schema_version:5,data:{favourites:[]}}),
        dangerous:'{"format":"luisa-letters-user-data","app_id":"lettres-de-luisa-piccarreta","schema_version":5,"data":{"__proto__":{"polluted":true}}}'
      };
      const out={};
      for(const [k,v] of Object.entries(cases)){try{parseImportPayload(v);out[k]='ACCEPTED'}catch(e){out[k]=String(e.message||e)}}
      return out;
    }""")
    rec('import:unsupported_rejected',rejects['unsupported']=='UNSUPPORTED_SCHEMA',rejects)
    rec('import:incomplete_rejected',rejects['incomplete']=='INCOMPLETE_MODERN_BACKUP',rejects)
    rec('import:dangerous_rejected',rejects['dangerous'] in ['MALICIOUS_OR_INVALID_OBJECT','INVALID_DATA_OBJECT'],rejects)
    after=p.evaluate("()=>Object.fromEntries(['lp_favs','lp_notes','lp_highlights','lp_read','lp_state_schema'].map(k=>[k,localStorage.getItem(k)]))")
    rec('import:rejections_no_mutation',after==before,{'before':before,'after':after})
    done(); c.close()

    # 2) Cross-tab propagation.
    c=b.new_context(viewport={'width':390,'height':844},locale='fr-FR')
    c.add_init_script("localStorage.setItem('lp_onboarded','1')")
    p1=c.new_page();p2=c.new_page();d1=trap(p1,'chromium:cross_tab_1');d2=trap(p2,'chromium:cross_tab_2')
    p1.goto(BASE+'?blind=tab1',wait_until='domcontentloaded');ready(p1)
    p2.goto(BASE+'?blind=tab2',wait_until='domcontentloaded');ready(p2)
    p1.locator('#pnav-list').click();p1.locator('#letter-list .letter-item[data-n="5"]').click();p1.locator('#pr-fav-btn').click()
    p2.wait_for_function("()=>JSON.parse(localStorage.getItem('lp_favs')||'[]').includes(5)",timeout=10000)
    p2.locator('#pnav-list').click();p2.locator('[data-action="filter"][data-filter="fav"]').click();p2.wait_for_timeout(200)
    rec('cross_tab:favourite_ui',p2.locator('#letter-list .letter-item[data-n="5"]').count()==1,p2.locator('#letter-list').inner_text()[:200])
    d1();d2();c.close()

    # 3) Future-schema write guard must fail safe, preserving unknown newer state.
    c=b.new_context(viewport={'width':390,'height':844},locale='fr-FR')
    c.add_init_script("""localStorage.setItem('lp_onboarded','1');localStorage.setItem('lp_state_schema','999');localStorage.setItem('lp_favs','[2]');""")
    p=c.new_page();done=trap(p,'chromium:future_schema')
    p.goto(BASE+'?blind=future',wait_until='domcontentloaded');ready(p)
    p.locator('#pnav-list').click();p.locator('#letter-list .letter-item[data-n="3"]').click();p.locator('#pr-fav-btn').click();p.wait_for_timeout(200)
    fs=p.evaluate("()=>({schema:localStorage.getItem('lp_state_schema'),favs:localStorage.getItem('lp_favs')})")
    rec('future_schema:preserved',fs=={'schema':'999','favs':'[2]'},fs)
    done();c.close()

    # 4) Cache identity + offline deep-link on the exact B2 worker.
    c=b.new_context(viewport={'width':390,'height':844},locale='fr-FR',service_workers='allow')
    c.add_init_script("localStorage.setItem('lp_onboarded','1')")
    p=c.new_page();done=trap(p,'chromium:pwa')
    p.goto(BASE+'?blind=pwa',wait_until='networkidle',timeout=30000);ready(p)
    p.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.controller",timeout=20000)
    p.wait_for_timeout(3000)
    caches=p.evaluate("()=>caches.keys()")
    rec('pwa:b2_cache_ids',any('shell-v2.15-b2' in x for x in caches) and any('corpus-v2.15-b2' in x for x in caches),caches)
    rec('pwa:no_b1_or_v214_cache',not any(('v2.15-b1' in x or 'v2.14-b1' in x) for x in caches),caches)
    p.close();c.set_offline(True)
    q=c.new_page();q.goto(BASE+'?letter=LP.LETTER.131',wait_until='domcontentloaded',timeout=20000);ready(q)
    expect(q.locator('#pr-pos')).to_have_text('131 / 136')
    rec('pwa:offline_deeplink_131',True,q.url)
    c.set_offline(False);done();c.close()

    # 5) Invalid routing should degrade safely.
    c=b.new_context(viewport={'width':390,'height':844},locale='fr-FR')
    c.add_init_script("localStorage.setItem('lp_onboarded','1')")
    p=c.new_page();done=trap(p,'chromium:invalid_routes')
    p.goto(BASE+'?screen=bogus&action=evil&letter=LP.LETTER.999&dp=LP.LETTER.999.DP999&q=%20%20',wait_until='domcontentloaded',timeout=30000);ready(p)
    rec('route:invalid_safe',p.locator('#letter-list .letter-item').count()==136,p.url)
    done();c.close();b.close()

    # 6) WebKit public-edge challenge with a different path and export.
    wb=pw.webkit.launch(headless=True)
    c=wb.new_context(viewport={'width':834,'height':1112},locale='fr-FR',color_scheme='dark',accept_downloads=True)
    c.add_init_script("localStorage.setItem('lp_onboarded','1');localStorage.setItem('lp_theme','system')")
    p=c.new_page();done=trap(p,'webkit:public')
    p.goto(PUBLIC+'?screen=search&q=abandon&blind=webkit',wait_until='domcontentloaded',timeout=30000);ready(p)
    rec('webkit:search_abandon',p.locator('#search-results [data-action="search-result"]').count()>0,p.locator('#search-results').inner_text()[:200])
    p.locator('#snav-explore').click();p.evaluate("()=>openPath('abandon')");p.wait_for_timeout(150)
    rec('webkit:abandon_path_seven',p.locator('.path-letter-item').count()==7,p.locator('.path-letter-item').count())
    p.evaluate("()=>closePath()");p.locator('#snav-settings').click();expect(p.locator('#settings-export-btn')).to_be_visible()
    with p.expect_download(timeout=10000) as di:p.locator('#settings-export-btn').click()
    env=json.load(open(di.value.path(),encoding='utf-8'))
    rec('webkit:actual_export_identity',env.get('format')=='luisa-letters-user-data' and env.get('app_version')=='2.15',{'format':env.get('format'),'version':env.get('app_version')})
    done();c.close();wb.close()

Path('/tmp/LETTRES_V2_15_FRESH_BLIND_AUDIT_R1.json').write_text(json.dumps({'status':'PASS' if not FAIL else 'FAIL','results':OUT,'failures':FAIL},ensure_ascii=False,indent=2),encoding='utf-8')
print('FRESH_BLIND_PASS',len(OUT))
