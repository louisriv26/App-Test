from playwright.sync_api import sync_playwright, expect
import json,re,urllib.request,hashlib

BASE='https://louisriv26.github.io/Les-lettres-de-Luisa/'
URL=BASE+'index.html'
EXPECTED={
'index.html':'1034efd29bd5c93021cb0a68cb3bc9c7e0fc48f3bb4e3a3a3b7e17181369de95',
'sw.js':'42203358031e1d710db5610fd1b21af8ab40f7f88a0dcdec72a346235edc3797',
'corpus.json':'362e763684e19d818722082b88348d912f06f434d8960e2a278db07b7f63f8ec',
'manifest.json':'6ac8e12e1f037b5920a1c274866fa393b5c49c5e52fb18cf922f92c17881ad48'}
R=[]
def rec(n,ok=True,d=None):
    R.append({'name':n,'ok':bool(ok),'detail':d})
    print('CHECK',n,'PASS' if ok else 'FAIL',repr(d),flush=True)
    if not ok: raise AssertionError(f'{n}: {d}')
def ready(pg):
    pg.locator('#loading').wait_for(state='detached',timeout=20000)
    expect(pg.locator('#list-title')).to_have_text('136 Lettres')
    expect(pg.locator('.build-meta').first).to_have_text('v2.4 · 2026-09-29')
    expect(pg.locator('.error-state')).to_have_count(0)
    # Fresh storage intentionally opens onboarding after a short delay.
    pg.wait_for_timeout(1000)
    overlay=pg.locator('#help-overlay')
    onboard=overlay.is_visible()
    if onboard:
        expect(pg.locator('#help-slide-label')).to_have_text('1 / 12')
        pg.locator('#help-close-btn').click()
        expect(overlay).to_be_hidden()
    return onboard
def errs(pg):
    c=[]; e=[]
    pg.on('console',lambda m:c.append(m.text) if m.type=='error' else None)
    pg.on('pageerror',lambda x:e.append(str(x)))
    return c,e
def clean(c,e,w):
    rec(w+':pageerrors',not e,e)
    bad=[x for x in c if 'Content Security Policy' in x or 'Refused to' in x]
    rec(w+':csp',not bad,bad)
def num(pg,wide=False):
    s=pg.locator('#wr-pos' if wide else '#pr-pos').inner_text()
    m=re.search(r'(\d+)',s); return int(m.group(1)) if m else None
def waitnum(pg,n,wide=False):
    loc=pg.locator('#wr-pos' if wide else '#pr-pos')
    expect(loc).to_have_text(f'{n} / 136',timeout=10000)
    return num(pg,wide)
def store(ctx):
    for o in ctx.storage_state().get('origins',[]):
        if o['origin']=='https://louisriv26.github.io':
            return {x['name']:x['value'] for x in o.get('localStorage',[])}
    return {}

for name,want in EXPECTED.items():
    req=urllib.request.Request(BASE+name,headers={'Cache-Control':'no-cache','Pragma':'no-cache','User-Agent':'Lettres-v24-Full-Audit'})
    with urllib.request.urlopen(req,timeout=30) as r:data=r.read()
    got=hashlib.sha256(data).hexdigest()
    rec('served:'+name,got==want,{'got':got,'want':want})

with sync_playwright() as p:
    b=p.chromium.launch(headless=True)

    # PHONE normal/alternative/edge paths
    ctx=b.new_context(viewport={'width':390,'height':844},locale='fr-FR')
    pg=ctx.new_page(); c,e=errs(pg); resp=pg.goto(URL+'?qa=full-phone',wait_until='domcontentloaded')
    rec('phone:http',resp and resp.ok,resp.status if resp else None); onboard=ready(pg)
    rec('onboarding:auto_help_and_close',onboard,onboard)
    rec('phone:nav5',pg.locator('.pnav-item').count()==5,pg.locator('.pnav-item').count())
    pg.locator('#pnav-list').click(); rec('phone:list136',pg.locator('#letter-list .letter-item').count()==136,pg.locator('#letter-list .letter-item').count())
    pg.locator('#letter-list .letter-item[data-n="1"]').click(); rec('phone:open1',num(pg)==1,num(pg))
    expect(pg.locator('#pr-btn-prev')).to_be_disabled(); rec('phone:prev_boundary_disabled',num(pg)==1,num(pg))
    pg.locator('#pr-btn-next').click(); pg.wait_for_timeout(100); rec('phone:next2',num(pg)==2,num(pg))
    pg.locator('#pr-fav-btn').click(); expect(pg.locator('#pr-fav-btn')).to_have_attribute('aria-pressed','true')
    pg.locator('#pr-read-btn').click(); expect(pg.locator('#pr-read-btn')).to_have_attribute('aria-label','Marquer comme non lu')
    rec('phone:fav_read',True)

    # Note create
    pg.get_by_role('button',name='Ajouter une note').click(); expect(pg.locator('#note-sheet')).to_be_visible()
    pg.locator('#note-input').fill('QA note initiale — blind challenge'); pg.locator('#note-save-btn').click()
    expect(pg.locator('#note-sheet')).to_be_hidden()

    # Highlight create from actual Reader selection
    dps=pg.locator('#phone-reader-scroll [data-dp-id]')
    dp=None
    for i in range(dps.count()):
        cand=dps.nth(i)
        if len(cand.inner_text().strip())>=8:
            dp=cand
            break
    rec('highlight:text_paragraph_found',dp is not None,dps.count())
    ok=dp.evaluate("""el=>{const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){let t=n.nodeValue||'';let a=t.search(/\\S/);if(a>=0&&t.slice(a).trim().length>=8){let z=Math.min(t.length,a+8);let r=document.createRange();r.setStart(n,a);r.setEnd(n,z);let s=window.getSelection();s.removeAllRanges();s.addRange(r);return s.toString();}}return '';}""")
    rec('highlight:selection_created',len(ok.strip())>=2,ok)
    pg.locator('#phone-reader-scroll').dispatch_event('mouseup'); expect(pg.locator('#hl-popup')).to_have_class(re.compile('show'))
    pg.get_by_role('button',name='Surligner').click(); pg.get_by_role('button',name='Jaune').click(); pg.wait_for_timeout(200)
    rec('highlight:create',True)

    # Settings persistence
    pg.get_by_role('button',name='Réglages').last.click(); expect(pg.locator('#text-size-bar')).to_be_visible()
    pg.locator('[data-text-level="xlarge"]').click(); pg.locator('[data-theme-choice="dark"]').click()
    pg.get_by_role('button',name='Fermer les réglages').click()
    pg.reload(wait_until='domcontentloaded'); ready(pg)
    rec('persist:xlarge',pg.locator('html').get_attribute('data-text-level')=='xlarge',pg.locator('html').get_attribute('data-text-level'))
    rec('persist:dark',pg.locator('html').get_attribute('data-theme')=='dark',pg.locator('html').get_attribute('data-theme'))
    pg.locator('#pnav-list').click(); pg.locator('#letter-list .letter-item[data-n="2"]').click()
    expect(pg.locator('#pr-fav-btn')).to_have_attribute('aria-pressed','true'); expect(pg.locator('#pr-read-btn')).to_have_attribute('aria-label','Marquer comme non lu')
    rec('persist:fav_read',True)

    # Note edit/delete/undo + highlight delete/undo
    pg.get_by_role('button',name='Retour à la liste').click(); pg.locator('#pnav-notes').click(); pg.locator('#tab-notes').click()
    expect(pg.locator('#t-notes')).to_contain_text('QA note initiale')
    pg.get_by_role('button',name='Modifier la note').click(); pg.locator('#note-input').fill('QA note modifiée — blind challenge'); pg.locator('#note-save-btn').click()
    expect(pg.locator('#t-notes')).to_contain_text('QA note modifiée')
    pg.get_by_role('button',name='Supprimer la note').click(); expect(pg.locator('#toast .undo-toast-btn')).to_be_visible(); pg.locator('#toast .undo-toast-btn').click()
    expect(pg.locator('#t-notes')).to_contain_text('QA note modifiée'); rec('D1_D2:note_edit_delete_undo',True)
    pg.locator('#tab-highlights').click(); rec('highlight:workspace_present',pg.locator('#t-highlights .hl-item').count()==1,pg.locator('#t-highlights').inner_text()[:250])
    pg.get_by_role('button',name='Supprimer le surlignage').click(); expect(pg.locator('#toast .undo-toast-btn')).to_be_visible(); pg.locator('#toast .undo-toast-btn').click()
    expect(pg.locator('#t-highlights .hl-item')).to_have_count(1)
    rec('D1:highlight_undo',True,pg.locator('#t-highlights').inner_text()[:250])

    # Search paths
    pg.locator('#pnav-search').click(); q=pg.locator('#search-input')
    q.fill('10'); pg.wait_for_timeout(500); rec('search:number',pg.locator('#search-results [data-action="search-result"]').count()>0,pg.locator('#search-results').inner_text()[:250])
    pg.locator('#search-results [data-action="search-result"]').first.click(); rec('search:open10',num(pg)==10,num(pg))
    pg.get_by_role('button',name='Retour à la liste').click(); rec('search:return_state',pg.locator('#search-input').input_value()=='10',pg.locator('#search-input').input_value())
    q=pg.locator('#search-input'); q.fill('volonté'); pg.wait_for_timeout(500); rec('search:text',pg.locator('#search-results [data-action="search-result"]').count()>0,pg.locator('#search-results').inner_text()[:250])
    q.fill('x'); pg.wait_for_timeout(500); rec('search:short','au moins 2 caractères' in pg.locator('#search-results').inner_text(),pg.locator('#search-results').inner_text())
    q.fill('31/02/1930'); pg.wait_for_timeout(500); rec('search:invalid_date','Date invalide' in pg.locator('#search-results').inner_text(),pg.locator('#search-results').inner_text())
    q.fill('zzzzqwertynonexistent'); pg.wait_for_timeout(500); rec('search:none',pg.locator('#search-results [data-action="search-result"]').count()==0,pg.locator('#search-results').inner_text()[:250])

    # Backup export + self import preview/merge
    pg.locator('#pnav-home').click(); pg.locator('#home-settings-btn').click()
    with pg.expect_download(timeout=10000) as di: pg.locator('#settings-export-btn').click()
    path=di.value.path(); data=json.load(open(path,encoding='utf-8'))
    rec('backup:format',data.get('format')=='luisa-letters-user-data',data.get('format'))
    rec('backup:version',data.get('app_version')=='2.4',data.get('app_version'))
    rec('backup:state',2 in data.get('data',{}).get('favourites',[]) and 2 in data.get('data',{}).get('read_state',[]),data.get('data',{}))
    pg.locator('#import-input').set_input_files(path); expect(pg.locator('#import-sheet')).to_be_visible(); rec('backup:preview',True,pg.locator('#import-preview-summary').inner_text())
    pg.locator('#import-merge-btn').click(); expect(pg.locator('#import-sheet')).to_be_hidden(); rec('backup:self_merge',True)
    pg.get_by_role('button',name='Fermer les réglages').click()

    # Reader source representative special mapping
    pg.locator('#pnav-list').click(); pg.locator('#letter-list .letter-item[data-n="122"]').click(); pg.locator('#pr-source-btn').click()
    expect(pg.locator('#reader-info-sheet')).to_be_visible(); rec('source:122_nonempty',len(pg.locator('#reader-info-content').inner_text().strip())>20,pg.locator('#reader-info-content').inner_text()[:400])
    pg.locator('#reader-info-close').click()
    st=store(ctx); rec('storage:schema',st.get('lp_state_schema')=='5',st.get('lp_state_schema')); rec('storage:note','QA note modifiée' in st.get('lp_notes',''),st.get('lp_notes','')[:300])
    clean(c,e,'phone'); ctx.close()

    # WIDE: D3 cross-letter interaction + keyboard guard + responsive boundary
    ctx=b.new_context(viewport={'width':1280,'height':900},locale='fr-FR'); pg=ctx.new_page(); c,e=errs(pg); pg.goto(URL+'?qa=full-wide',wait_until='domcontentloaded'); ready(pg)
    pg.locator('#snav-list').click(); rec('wide:list136',pg.locator('#letter-list .letter-item').count()==136,pg.locator('#letter-list .letter-item').count())
    pg.locator('#letter-list .letter-item[data-n="5"]').click(); waitnum(pg,5,True); rec('wide:open5',num(pg,True)==5,num(pg,True))
    pg.get_by_role('button',name='Ajouter une note').click(); pg.locator('#note-input').fill('D3 letter 5'); pg.locator('#note-save-btn').click()
    pg.locator('#letter-list .letter-item[data-n="10"]').click(); waitnum(pg,10,True); rec('wide:open10',num(pg,True)==10,num(pg,True))
    pg.locator('#snav-notes').click(); pg.locator('#tab-notes').click(); pg.get_by_role('button',name='Modifier la note').click(); pg.locator('#note-input').fill('D3 edited while 10 visible'); pg.locator('#note-save-btn').click()
    pg.locator('#wr-btn-next').click(); waitnum(pg,11,True); rec('D3:next_is_11',num(pg,True)==11,num(pg,True))
    pg.locator('#snav-list').click(); pg.locator('#letter-list .letter-item[data-n="20"]').click(); waitnum(pg,20,True); pg.locator('#wide-reader-scroll').click(position={'x':20,'y':80}); pg.keyboard.press('ArrowRight'); waitnum(pg,21,True)
    rec('wide:key_next',num(pg,True)==21,num(pg,True)); pg.locator('#wr-fav-btn').focus(); pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(100); rec('wide:key_guard',num(pg,True)==21,num(pg,True))
    pg.set_viewport_size({'width':768,'height':900}); pg.wait_for_timeout(250); rec('layout:768','wide'==pg.locator('html').get_attribute('data-layout'),pg.locator('html').get_attribute('data-layout'))
    pg.set_viewport_size({'width':767,'height':900}); pg.wait_for_timeout(250); rec('layout:767','phone'==pg.locator('html').get_attribute('data-layout'),pg.locator('html').get_attribute('data-layout'))
    clean(c,e,'wide'); ctx.close()

    # Exhaustive 136 render at narrow + Très grand
    ctx=b.new_context(viewport={'width':320,'height':740},locale='fr-FR'); pg=ctx.new_page(); c,e=errs(pg); pg.goto(URL+'?qa=all136',wait_until='domcontentloaded'); ready(pg)
    pg.locator('#home-settings-btn').click(); pg.locator('[data-text-level="xlarge"]').click(); pg.get_by_role('button',name='Fermer les réglages').click(); pg.locator('#pnav-list').click()
    fail=[]
    for n in range(1,137):
        pg.locator(f'#letter-list .letter-item[data-n="{n}"]').click()
        try: waitnum(pg,n,False)
        except Exception as ex: fail.append((n,'number_wait',repr(ex)))
        if num(pg)!=n: fail.append((n,'number',num(pg)))
        m=pg.locator('#phone-reader-scroll').evaluate('(el)=>({sw:el.scrollWidth,cw:el.clientWidth})')
        if m['sw']>m['cw']+2: fail.append((n,'overflow',m))
        if n<136: pg.get_by_role('button',name='Retour à la liste').click()
    rec('all136:320_xlarge',not fail,fail[:15]); clean(c,e,'all136'); ctx.close()

    # Cold offline reopen/deep link after first online install/cache
    ctx=b.new_context(viewport={'width':390,'height':844},locale='fr-FR',service_workers='allow'); pg=ctx.new_page(); c,e=errs(pg)
    pg.goto(URL+'?qa=offline-prep',wait_until='networkidle'); ready(pg); pg.wait_for_timeout(4500); pg.reload(wait_until='networkidle'); ready(pg); pg.close()
    ctx.set_offline(True); pg=ctx.new_page(); c2,e2=errs(pg)
    try:
        pg.goto(URL+'?letter=LP.LETTER.010',wait_until='domcontentloaded',timeout=15000); ready(pg); pg.wait_for_timeout(300)
        rec('offline:cold_reopen',True); waitnum(pg,10); rec('offline:deep10',num(pg)==10,num(pg))
    except Exception as ex: rec('offline:cold_reopen',False,repr(ex))
    clean(c2,e2,'offline'); ctx.set_offline(False); ctx.close(); b.close()

    # Independent WebKit challenge
    wb=p.webkit.launch(headless=True); ctx=wb.new_context(viewport={'width':390,'height':844},locale='fr-FR'); pg=ctx.new_page(); c,e=errs(pg)
    resp=pg.goto(URL+'?qa=webkit',wait_until='domcontentloaded'); rec('webkit:http',resp and resp.ok,resp.status if resp else None); ready(pg)
    pg.locator('#pnav-list').click(); pg.locator('#letter-list .letter-item[data-n="33"]').click(); waitnum(pg,33); rec('webkit:open33',num(pg)==33,num(pg))
    pg.locator('#pr-source-btn').click(); expect(pg.locator('#reader-info-sheet')).to_be_visible(); pg.locator('#reader-info-methodology').click(); expect(pg.locator('#provenance-screen')).to_be_visible()
    pg.locator('#provenance-back').click(); expect(pg.locator('#reader-info-sheet')).to_be_visible(); pg.locator('#reader-info-close').click(); rec('webkit:provenance_return',True)
    pg.get_by_role('button',name='Retour à la liste').click(); pg.locator('#pnav-search').click(); pg.locator('#search-input').fill('10'); pg.wait_for_timeout(600); pg.locator('#search-results [data-action="search-result"]').first.click(); waitnum(pg,10)
    rec('webkit:search_open10',num(pg)==10,num(pg)); pg.get_by_role('button',name='Retour à la liste').click(); rec('webkit:search_return',pg.locator('#search-input').input_value()=='10',pg.locator('#search-input').input_value())
    clean(c,e,'webkit'); ctx.close(); wb.close()

print('AUDIT_RESULTS='+json.dumps(R,ensure_ascii=False))
print('PASS_COUNT',sum(1 for x in R if x['ok']),'TOTAL',len(R))
