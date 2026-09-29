from playwright.sync_api import sync_playwright, expect
import urllib.request,hashlib,json,re,subprocess,time,shutil,os

BASE='https://louisriv26.github.io/Les-lettres-de-Luisa/'
URL=BASE+'index.html'
EXPECTED={
'corpus.json':'362e763684e19d818722082b88348d912f06f434d8960e2a278db07b7f63f8ec',
'fonts/OFL-Crimson-Text.txt':'168f7f27a2b6b737827a0dcf4cac71914d4fb370d83d16d1156e2956a377f766',
'fonts/OFL-IM-Fell-English.txt':'e1025338fa4769414d66a20af47f29482263929537ff3be0bccc1f13efbd415e',
'fonts/crimson-text-400-italic.woff2':'01f6ca6adafc5049720d579cb70d8eb322460bdff3283da029fb2d479213eb8f',
'fonts/crimson-text-400.woff2':'135ed9f97138b094f406b7ede6c50b33c028a3125be81d21c09847eabd837453',
'fonts/crimson-text-600.woff2':'98efdcf22d7862d2fec70d05d8d77aafacfe62d325e588859a6f68dbb8bdaf30',
'fonts/im-fell-english-400-italic.woff2':'e0e73494e38aafdd9c1506001fabc03e73b029a97ae31143cd89840f0cdaf16e',
'fonts/im-fell-english-400.woff2':'0aa92ef9faca61c105739bbcf52b2faa62e0e74291b1f658a2f9861390531334',
'icons/apple-touch-icon.png':'38e42d54be67cdf5c402961c739f6a1942671555089e5f525ce188bfdb0735ef',
'icons/favicon-16.png':'1f3a31780a045323d1ad5edcc59ece6a3e3ca5f3b1ff19fa3c4c8e62caedbf7e',
'icons/favicon-32.png':'e508a4b1f3e4c7223de0acad47e45a5064924dcf6a554563f05247380b8720e5',
'icons/favicon.ico':'fe9780795ac64f18c07de91b122959d0972e84478978fcb89dbfa1115a3ee257',
'icons/icon-120.png':'7761c15fc28829003d021ffd408c03fa7263e93481487b786871479c7079fba9',
'icons/icon-192.png':'1c6f4ce9ae75adfb800ce23f2ad1a48ff0a478c14dd0b11f31b1c2f9690751aa',
'icons/icon-512.png':'6f6912ce95300e2952d3eca59928619553033315615ea5010e4b0f04b9191fa4',
'icons/icon-60.png':'433507a2746253190fdfcbe645ac82d7a9ea14a77e1938011b910bb4708e4ebc',
'icons/icon-maskable-512.png':'1aa6e7f4d14c8b98375c97616dce4ff92a7e01835fa69a0c8e838e6b9b48cba7',
'index.html':'1034efd29bd5c93021cb0a68cb3bc9c7e0fc48f3bb4e3a3a3b7e17181369de95',
'manifest.json':'6ac8e12e1f037b5920a1c274866fa393b5c49c5e52fb18cf922f92c17881ad48',
'sw.js':'42203358031e1d710db5610fd1b21af8ab40f7f88a0dcdec72a346235edc3797',
'vendor/tabler/LICENSE.txt':'b740a1d46122672da62833e97f7e7c8a13fa85cbc7445b584b297cc00dde93db',
'vendor/tabler/tabler-sprite.svg':'51bab6fa61b2a527793e0a5f41b2ab065e52d1d1e4e91283554aa7a9456d7118'}
R=[]
def rec(n,ok,d=None):
    R.append({'name':n,'ok':bool(ok),'detail':d}); print('BLIND',n,'PASS' if ok else 'FAIL',repr(d),flush=True)
    if not ok: raise AssertionError(f'{n}: {d}')
def ls(ctx):
    for o in ctx.storage_state().get('origins',[]):
        if o['origin'] in ('https://louisriv26.github.io','http://127.0.0.1:8777'):
            return {x['name']:x['value'] for x in o.get('localStorage',[])}
    return {}
def ready(pg,version='v2.4 · 2026-09-29'):
    pg.locator('#loading').wait_for(state='detached',timeout=20000)
    if version: expect(pg.locator('.build-meta').first).to_have_text(version)
    expect(pg.locator('#list-title')).to_have_text('136 Lettres')
    pg.wait_for_timeout(1000)
    if pg.locator('#help-overlay').is_visible():
        pg.locator('#help-close-btn').click(); expect(pg.locator('#help-overlay')).to_be_hidden()
def waitnum(pg,n,wide=False):
    expect(pg.locator('#wr-pos' if wide else '#pr-pos')).to_have_text(f'{n} / 136',timeout=10000)
def init_storage(ctx,items):
    js="if(location.origin.indexOf('louisriv26.github.io')>=0||location.origin==='http://127.0.0.1:8777'){"+''.join([f"localStorage.setItem({json.dumps(k)},{json.dumps(v)});" for k,v in items.items()])+"}"
    ctx.add_init_script(js)

# Independent all-member served-byte binding
corpus_bytes=None
for name,want in EXPECTED.items():
    req=urllib.request.Request(BASE+name,headers={'Cache-Control':'no-cache','Pragma':'no-cache','User-Agent':'Lettres-v24-Blind'})
    with urllib.request.urlopen(req,timeout=30) as rr: data=rr.read()
    got=hashlib.sha256(data).hexdigest(); rec('served22:'+name,got==want,got)
    if name=='corpus.json': corpus_bytes=data
corpus=json.loads(corpus_bytes)['letters']

with sync_playwright() as p:
    b=p.chromium.launch(headless=True)

    # Future-schema fail-closed: readable, but current app must not overwrite newer state.
    ctx=b.new_context(viewport={'width':390,'height':844},locale='fr-FR')
    init_storage(ctx,{'lp_onboarded':'1','lp_state_schema':'99','lp_favs':'[1]'})
    pg=ctx.new_page(); errors=[]; pg.on('pageerror',lambda e:errors.append(str(e)))
    pg.goto(URL+'?letter=LP.LETTER.001&qa=future',wait_until='domcontentloaded'); ready(pg); waitnum(pg,1)
    expect(pg.locator('#pr-fav-btn')).to_have_attribute('aria-pressed','true')
    pg.locator('#pr-fav-btn').click()
    expect(pg.locator('#toast')).to_contain_text('version plus récente')
    expect(pg.locator('#pr-fav-btn')).to_have_attribute('aria-pressed','true')
    st=ls(ctx); rec('future_schema:preserved',st.get('lp_state_schema')=='99' and st.get('lp_favs')=='[1]',st)
    rec('future_schema:no_pageerror',not errors,errors); ctx.close()

    # Legacy migration: numeric text size + legacy path progress → schema 5, semantic size, read set.
    ctx=b.new_context(viewport={'width':390,'height':844},locale='fr-FR')
    init_storage(ctx,{'lp_onboarded':'1','lp_state_schema':'1','lp_size':'22','lp_paths':'{"abandon":[44,50]}','lp_read':'[]'})
    pg=ctx.new_page(); errors=[]; pg.on('pageerror',lambda e:errors.append(str(e)))
    pg.goto(URL+'?qa=legacy',wait_until='domcontentloaded'); ready(pg); pg.wait_for_timeout(500)
    st=ls(ctx); read=json.loads(st.get('lp_read','[]'))
    rec('legacy:schema5',st.get('lp_state_schema')=='5',st.get('lp_state_schema'))
    rec('legacy:size_large',st.get('lp_size')=='large' and pg.locator('html').get_attribute('data-text-level')=='large',(st.get('lp_size'),pg.locator('html').get_attribute('data-text-level')))
    rec('legacy:path_to_read',44 in read and 50 in read,read)
    rec('legacy:path_removed','lp_paths' not in st,st.get('lp_paths'))
    rec('legacy:no_pageerror',not errors,errors); ctx.close()

    # Malformed personal JSON/schema must not crash startup or discard unrelated valid state.
    ctx=b.new_context(viewport={'width':390,'height':844},locale='fr-FR')
    init_storage(ctx,{'lp_onboarded':'1','lp_state_schema':'broken','lp_notes':'{bad','lp_favs':'[3]'})
    pg=ctx.new_page(); errors=[]; pg.on('pageerror',lambda e:errors.append(str(e)))
    pg.goto(URL+'?letter=LP.LETTER.003&qa=malformed',wait_until='domcontentloaded'); ready(pg); waitnum(pg,3)
    expect(pg.locator('#pr-fav-btn')).to_have_attribute('aria-pressed','true')
    rec('malformed:startup_and_valid_state_survive',True)
    rec('malformed:no_pageerror',not errors,errors); ctx.close()

    # Rare UI paths: filters, curated Abandon path, and provenance open/closed distinction.
    ctx=b.new_context(viewport={'width':390,'height':844},locale='fr-FR')
    init_storage(ctx,{'lp_onboarded':'1'})
    pg=ctx.new_page(); errors=[]; pg.on('pageerror',lambda e:errors.append(str(e)))
    pg.goto(URL+'?qa=rare',wait_until='domcontentloaded'); ready(pg)
    pg.locator('#pnav-list').click()
    pg.locator('#filter-row [data-filter="fav"]').click(); rec('filter:fav_empty',pg.locator('#letter-list .letter-item').count()==0,pg.locator('#letter-list').inner_text()[:100])
    pg.locator('#filter-row [data-filter="unread"]').click(); rec('filter:unread136',pg.locator('#letter-list .letter-item').count()==136,pg.locator('#letter-list .letter-item').count())
    for topic in ['Divine Volonté','Croix','Paix','Prêtres','Deuil','Confiance','Propagation des écrits']:
        exp=sum(1 for l in corpus if topic in (l.get('topics_fr') or []))
        pg.locator(f'#filter-row [data-filter="{topic}"]').click()
        got=pg.locator('#letter-list .letter-item').count()
        rec('filter:'+topic,got==exp,{'got':got,'expected':exp})
    pg.locator('#pnav-explore').click()
    pg.locator('[data-action="path"][data-path-id="abandon"]').click()
    expect(pg.locator('#path-modal')).to_have_class(re.compile('show'))
    nums=[int(pg.locator('#path-modal [data-action="path-letter"]').nth(i).get_attribute('data-n')) for i in range(pg.locator('#path-modal [data-action="path-letter"]').count())]
    rec('path:abandon_exact7',nums==[44,50,58,74,93,107,131],nums)
    pg.locator('#path-modal-back').click()
    pg.locator('#pnav-list').click(); pg.locator('#filter-row [data-filter="all"]').click()
    pg.locator('#letter-list .letter-item[data-n="48"]').click(); waitnum(pg,48); rec('provenance:open_chip48',pg.locator('#pr-source-open-chip').is_visible(),pg.locator('#pr-source-open-chip').get_attribute('class'))
    pg.get_by_role('button',name='Retour à la liste').click(); pg.locator('#letter-list .letter-item[data-n="49"]').click(); waitnum(pg,49); rec('provenance:no_false_chip49',not pg.locator('#pr-source-open-chip').is_visible(),pg.locator('#pr-source-open-chip').get_attribute('class'))
    rec('rare:no_pageerror',not errors,errors); ctx.close()

    # Real SW update lifecycle from rollback production commit to exact v2.4 tree.
    site='/tmp/lettres-site'; old='/tmp/lettres-old'; new='/tmp/lettres-new'
    if os.path.exists(site): shutil.rmtree(site)
    shutil.copytree(old,site)
    server=subprocess.Popen(['python3','-m','http.server','8777','--bind','127.0.0.1','--directory',site],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        time.sleep(1)
        ctx=b.new_context(viewport={'width':390,'height':844},locale='fr-FR',service_workers='allow')
        init_storage(ctx,{'lp_onboarded':'1'})
        pg=ctx.new_page(); errors=[]; pg.on('pageerror',lambda e:errors.append(str(e)))
        pg.goto('http://127.0.0.1:8777/index.html',wait_until='networkidle'); ready(pg,version=None)
        rec('update:old_version',pg.locator('.build-meta').first.inner_text().startswith('v2.3'),pg.locator('.build-meta').first.inner_text())
        pg.locator('#pnav-list').click(); pg.locator('#letter-list .letter-item[data-n="2"]').click(); waitnum(pg,2)
        pg.locator('#pr-fav-btn').click(); expect(pg.locator('#pr-fav-btn')).to_have_attribute('aria-pressed','true')
        pg.wait_for_timeout(2500); pg.reload(wait_until='networkidle'); ready(pg,version=None)
        # Replace origin bytes under the already-established old SW scope.
        for entry in os.listdir(site):
            path=os.path.join(site,entry)
            if os.path.isdir(path): shutil.rmtree(path)
            else: os.remove(path)
        shutil.copytree(new,site,dirs_exist_ok=True)
        pg.reload(wait_until='domcontentloaded'); ready(pg)
        expect(pg.locator('#update-banner')).to_be_visible(timeout=15000)
        rec('update:waiting_banner',True,pg.locator('#update-banner-message').inner_text())
        with pg.expect_navigation(timeout=20000):
            pg.locator('#update-apply-btn').click()
        ready(pg)
        rec('update:new_version',pg.locator('.build-meta').first.inner_text()=='v2.4 · 2026-09-29',pg.locator('.build-meta').first.inner_text())
        pg.locator('#pnav-list').click(); pg.locator('#letter-list .letter-item[data-n="2"]').click(); waitnum(pg,2)
        expect(pg.locator('#pr-fav-btn')).to_have_attribute('aria-pressed','true')
        rec('update:state_survives',True)
        rec('update:no_pageerror',not errors,errors)
        ctx.close()
    finally:
        server.terminate(); server.wait(timeout=5)
    b.close()

print('BLIND_RESULTS='+json.dumps(R,ensure_ascii=False))
print('BLIND_PASS_COUNT',sum(1 for x in R if x['ok']),'TOTAL',len(R))
