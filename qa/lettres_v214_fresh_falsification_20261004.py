from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import urllib.request, hashlib, json, os, shutil, time, re

PUBLIC='https://louisriv26.github.io/App-Test/lettres-v2.14-b1-csp-repair/'
ROOT=Path('lettres-v2.14-b1-csp-repair')
PRE=Path('lettres-v2.12-b1-darkmode')
SCOPE=Path('/tmp/lettres-v214-fresh-scope')
LOCAL='http://127.0.0.1:8132/index.html'
R=[]

def rec(name, ok, detail=None):
    item={'name':name,'ok':bool(ok),'detail':detail}
    R.append(item)
    print('CHECK',name,'PASS' if ok else 'FAIL',repr(detail),flush=True)
    if not ok:
        raise AssertionError(f'{name}: {detail}')

def ready(pg, version='2.13'):
    pg.locator('#loading').wait_for(state='detached',timeout=25000)
    expect(pg.locator('#list-title')).to_have_text('136 Lettres')
    expect(pg.locator('.build-meta').first).to_contain_text('v'+version)
    expect(pg.locator('.error-state')).to_have_count(0)
    pg.wait_for_timeout(800)
    if pg.locator('#help-overlay').is_visible():
        pg.locator('#help-close-btn').click()
        expect(pg.locator('#help-overlay')).to_be_hidden()

def errors(pg):
    c=[]; e=[]
    pg.on('console',lambda m:c.append(m.text) if m.type=='error' else None)
    pg.on('pageerror',lambda x:e.append(str(x)))
    return c,e

def clean(name,c,e):
    bad=[x for x in c if 'Content Security Policy' in x or 'Refused to' in x or 'Uncaught' in x]
    rec(name+':pageerrors',not e,e)
    rec(name+':console_errors',not c,c)
    rec(name+':csp',not bad,bad)

def protected_storage(pg):
    keys=['lp_favs','lp_notes','lp_highlights','lp_read','lp_positions','lp_last','lp_size','lp_theme','lp_state_schema','lp_paths']
    return pg.evaluate("(ks)=>Object.fromEntries(ks.map(k=>[k,localStorage.getItem(k)]))",keys)

# PASS 1 / public delivered bytes: compare every package member, not only core files.
files=sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file())
rec('package:file_count',len(files)==22,len(files))
for rel in files:
    local=(ROOT/rel).read_bytes()
    want=hashlib.sha256(local).hexdigest()
    req=urllib.request.Request(PUBLIC+rel+'?freshqa=20261004b',headers={'Cache-Control':'no-cache','Pragma':'no-cache','User-Agent':'Lettres-v2.14-fresh-falsification'})
    with urllib.request.urlopen(req,timeout=40) as resp:
        data=resp.read(); status=resp.status
    got=hashlib.sha256(data).hexdigest()
    rec('edge22:'+rel+':http',status==200,status)
    rec('edge22:'+rel+':sha256',got==want,{'got':got,'want':want})

manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
rec('manifest:identity',(manifest.get('version'),manifest.get('build_revision'),manifest.get('release_id'))==('2.12','B1','lettres-v2.14-b1-csp-repair'),{k:manifest.get(k) for k in ('version','build_revision','release_id')})
sw=(ROOT/'sw.js').read_text(encoding='utf-8')
rec('sw:no_predecessor_runtime_token','v2.13' not in sw and 'v2.12' not in sw,{'v213':sw.count('v2.13'),'v212':sw.count('v2.12')})
rec('sw:successor_cache_ids',sw.count('shell-v2.14-b1')>=1 and sw.count('corpus-v2.14-b1')>=1,None)
index_text=(ROOT/'index.html').read_text(encoding='utf-8')
STALE_CSP=[
"'sha256-5f7hkRF7W/iK5De4fekXDFX5QLBdvzg+24Ynn7Kg1J0='",
"'sha256-EsFT1O/naZelunScCVdb0tL5ruF0UOnBO1yhoLcieeY='",
"'sha256-KbOnILe3AvDAjicxs+Uo8W4hxfqGINcDwFYp8pvDrWQ='",
"'sha256-ugrsOjEHVa7sYJzyVQnFDOk46B8+0QDCLn4IrrHG9gg='",
]
rec('csp:historical_hashes_removed',all(h not in index_text for h in STALE_CSP),[h for h in STALE_CSP if h in index_text])
main_script=re.findall(r'<script(?![^>]*\\bsrc=)[^>]*>(.*?)</script>',index_text,re.S|re.I)[0]
main_hash="'sha256-"+__import__('base64').b64encode(hashlib.sha256(main_script.encode()).digest()).decode()+"'"
rec('csp:main_hash_bound_twice',index_text.count(main_hash)==2,{'hash':main_hash,'count':index_text.count(main_hash)})
m=re.search(r"script-src-elem\\s+('sha256-[^']+')",index_text)
rec('csp:script_src_elem_exact',bool(m and m.group(1)==main_hash),m.group(1) if m else None)

with sync_playwright() as p:
    # FRESH PUBLIC CHROMIUM CHALLENGE — different routes and failure modes from prior campaign.
    browser=p.chromium.launch(headless=True)
    ctx=browser.new_context(viewport={'width':390,'height':844},locale='fr-FR',service_workers='allow')
    pg=ctx.new_page(); c,e=errors(pg)
    resp=pg.goto(PUBLIC+'index.html?letter=LP.LETTER.002&dp=LP.LETTER.002.DP002',wait_until='domcontentloaded',timeout=30000)
    rec('route:letter_dp:http',bool(resp and resp.ok),resp.status if resp else None)
    ready(pg)
    expect(pg.locator('#pr-pos')).to_have_text('2 / 136')
    rec('route:letter_dp:open2',True)
    expect(pg.locator('[data-dp-id="LP.LETTER.002.DP002"]')).to_have_count(1)
    rec('route:letter_dp:paragraph',True)

    # Direct router sanitation / invalid route safety.
    parsed=pg.evaluate("""()=>window.__LET_H_TEST.parseInitialRoute('?screen=evil&letter=BAD&dp=LP.LETTER.002.DP002&q=a%00b&path=../escape')""")
    rec('route:parser_rejects_invalid',parsed.get('screen')=='' and parsed.get('letter')=='' and parsed.get('dp')=='' and parsed.get('path')=='' and parsed.get('q')=='a b',parsed)
    pg.goto(PUBLIC+'index.html?letter=LP.LETTER.999&dp=LP.LETTER.999.DP001',wait_until='domcontentloaded',timeout=30000); ready(pg)
    rec('route:noncanonical_999_safe',not pg.locator('#phone-reader').evaluate("el=>el.classList.contains('open')"),pg.url)

    # Search normalization: accentless/accented forms must agree; exact-date route must resolve.
    pg.locator('#pnav-search').click(); q=pg.locator('#search-input')
    q.fill('volonte'); pg.wait_for_timeout(600)
    n1=pg.locator('#search-results [data-action="search-result"]').count()
    q.fill('volonté'); pg.wait_for_timeout(600)
    n2=pg.locator('#search-results [data-action="search-result"]').count()
    rec('search:accent_normalization',n1>0 and n1==n2,{'volonte':n1,'volonté':n2})
    q.fill('24/02/1932'); pg.wait_for_timeout(600)
    rows=pg.locator('#search-results [data-action="search-result"]')
    rec('search:exact_date_has_result',rows.count()>0,pg.locator('#search-results').inner_text()[:500])
    first_n=rows.first.get_attribute('data-n') if rows.count() else None
    rec('search:exact_date_letter1',first_n=='1',first_n)

    # Direct path route — challenge startup path application, not manual Explorer navigation.
    pg.goto(PUBLIC+'index.html?screen=explore&path=abandon',wait_until='domcontentloaded',timeout=30000); ready(pg)
    expect(pg.locator('#path-modal')).to_have_class(re.compile('show'))
    nums=pg.locator('#path-letter-list .path-letter-item').evaluate_all("els=>els.map(e=>Number(e.dataset.n))")
    rec('route:path_abandon_direct',nums==[44,50,58,74,93,107,131],nums)
    pg.locator('#path-modal-back').click()

    # Cross-tab state propagation on same public origin.
    pg.goto(PUBLIC+'index.html?letter=LP.LETTER.005',wait_until='domcontentloaded'); ready(pg)
    p2=ctx.new_page(); c2,e2=errors(p2)
    p2.goto(PUBLIC+'index.html?letter=LP.LETTER.005',wait_until='domcontentloaded'); ready(p2)
    pg.locator('#pr-fav-btn').click()
    expect(pg.locator('#pr-fav-btn')).to_have_attribute('aria-pressed','true')
    p2.wait_for_timeout(500)
    fav_raw=p2.evaluate("localStorage.getItem('lp_favs')")
    rec('cross_tab:favourite_storage',fav_raw is not None and 5 in json.loads(fav_raw),fav_raw)
    # Force a UI reconciliation path by reopening the same reader on peer.
    p2.get_by_role('button',name='Retour à la liste').click()
    p2.locator('#letter-list .letter-item[data-n="5"]').click()
    expect(p2.locator('#pr-fav-btn')).to_have_attribute('aria-pressed','true')
    rec('cross_tab:favourite_ui',True)
    clean('public_peer',c2,e2); p2.close()

    # Backup parser and transactional rejection: invalid payloads must not mutate protected storage.
    before=protected_storage(pg)
    outcomes=pg.evaluate("""()=>{
      const T=window.__LET_A_TEST;
      function thrown(s){try{T.parseImportPayload(s);return '';}catch(e){return String(e&&e.message||e);}}
      const unsupported=JSON.stringify({format:'luisa-letters-user-data',app_id:'lettres-de-luisa-piccarreta',schema_version:999,data:{}});
      const incomplete=JSON.stringify({format:'luisa-letters-user-data',app_id:'lettres-de-luisa-piccarreta',schema_version:5,data:{favourites:[]}});
      const dangerous='{"app":"Lettres de Luisa Piccarreta","version":"1.0","__proto__":{"x":1}}';
      const legacy=JSON.stringify({app:'Lettres de Luisa Piccarreta',version:'1.0',favs:[2,999],readSet:[3],readerSize:18,theme:'dark'});
      let lp=T.parseImportPayload(legacy);
      return {unsupported:thrown(unsupported),incomplete:thrown(incomplete),dangerous:thrown(dangerous),legacy:{ok:lp.ok,favourites:lp.data.favourites,read_state:lp.data.read_state,text_size:lp.data.text_size,theme:lp.data.theme}};
    }""")
    rec('backup:unsupported_schema_rejected',outcomes['unsupported']=='UNSUPPORTED_SCHEMA',outcomes)
    rec('backup:incomplete_modern_rejected',outcomes['incomplete']=='INCOMPLETE_MODERN_BACKUP',outcomes)
    rec('backup:dangerous_key_rejected',outcomes['dangerous']=='MALICIOUS_OR_INVALID_OBJECT',outcomes)
    rec('backup:legacy_validated',outcomes['legacy']['ok'] and outcomes['legacy']['favourites']==[2] and outcomes['legacy']['read_state']==[3] and outcomes['legacy']['theme']=='dark',outcomes['legacy'])
    after=protected_storage(pg)
    rec('backup:rejection_no_mutation',before==after,{'before':before,'after':after})

    clean('public_chromium',c,e)
    ctx.close(); browser.close()

    # Future-schema fail-closed preservation: v2.14 must not silently downgrade newer personal state.
    browser=p.chromium.launch(headless=True)
    ctx=browser.new_context(viewport={'width':390,'height':844},locale='fr-FR')
    ctx.add_init_script("""(()=>{
      localStorage.setItem('lp_state_schema','999');
      localStorage.setItem('lp_favs','[2]');
      localStorage.setItem('lp_theme','dark');
      localStorage.setItem('lp_notes','[]');
      localStorage.setItem('lp_highlights','[]');
      localStorage.setItem('lp_read','[]');
      localStorage.setItem('lp_positions','{}');
    })()""")
    pg=ctx.new_page(); c,e=errors(pg)
    pg.goto(PUBLIC+'index.html?future-schema=1',wait_until='domcontentloaded',timeout=30000); ready(pg)
    fs=pg.evaluate("""()=>({
      schema:localStorage.getItem('lp_state_schema'),
      favs:localStorage.getItem('lp_favs'),
      guard:window.__LET_A_TEST.futureSchemaWriteGuard('lp_theme'),
      loadedFuture:window.__CONC_LETTRES_01_TEST.loadState()._futureStateSchema
    })""")
    rec('future_schema:preserved',fs['schema']=='999' and fs['favs']=='[2]' and fs['loadedFuture'] is True and fs['guard']['phase']=='future_schema',fs)
    clean('future_schema',c,e); ctx.close(); browser.close()

    # WebKit alternate entry: direct search route + invalid paragraph fallback.
    wb=p.webkit.launch(headless=True)
    ctx=wb.new_context(viewport={'width':834,'height':1112},locale='fr-FR')
    pg=ctx.new_page(); c,e=errors(pg)
    pg.goto(PUBLIC+'index.html?screen=search&q=confiance',wait_until='domcontentloaded',timeout=30000); ready(pg)
    expect(pg.locator('#search-input')).to_have_value('confiance')
    pg.wait_for_timeout(700)
    rec('webkit:direct_search_results',pg.locator('#search-results [data-action="search-result"]').count()>0,pg.locator('#search-results').inner_text()[:400])
    pg.goto(PUBLIC+'index.html?letter=LP.LETTER.010&dp=LP.LETTER.010.DP999',wait_until='domcontentloaded',timeout=30000); ready(pg)
    # Invalid-but-well-formed paragraph must not prevent the canonical letter opening.
    pos=pg.locator('#wr-pos' if pg.locator('html').get_attribute('data-layout')=='wide' else '#pr-pos')
    expect(pos).to_have_text('10 / 136')
    rec('webkit:invalid_dp_letter_survives',True,pg.url)
    clean('public_webkit',c,e); ctx.close(); wb.close()

    # SAME-SCOPE PWA UPDATE — rebuild actual predecessor->successor behavior from fresh bytes.
    if SCOPE.exists(): shutil.rmtree(SCOPE)
    shutil.copytree(PRE,SCOPE)
    browser=p.chromium.launch(headless=True)
    ctx=browser.new_context(viewport={'width':390,'height':844},locale='fr-FR',service_workers='allow')
    pg=ctx.new_page(); c,e=errors(pg)
    pg.goto(LOCAL+'?update-predecessor=1',wait_until='networkidle',timeout=30000); ready(pg,'2.12')
    pg.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.controller")
    # Create user state through UI on predecessor.
    pg.locator('#pnav-list').click(); pg.locator('#letter-list .letter-item[data-n="2"]').click()
    pg.locator('#pr-fav-btn').click(); pg.locator('#pr-read-btn').click()
    pg.get_by_role('button',name='Ajouter une note').click(); pg.locator('#note-input').fill('fresh update sentinel'); pg.locator('#note-save-btn').click()
    pg.get_by_role('button',name='Réglages').last.click(); pg.locator('[data-theme-choice="dark"]').click(); pg.get_by_role('button',name='Fermer les réglages').click()
    pred_state=protected_storage(pg)
    pred_caches=pg.evaluate("caches.keys()")
    rec('update:predecessor_cache_ids',any('shell-v2.12-b1' in x for x in pred_caches) and any('corpus-v2.12-b1' in x for x in pred_caches),pred_caches)

    # Atomically replace server bytes with exact successor while retaining URL/scope.
    tmp=Path('/tmp/lettres-v214-successor-copy')
    if tmp.exists(): shutil.rmtree(tmp)
    shutil.copytree(ROOT,tmp)
    for child in list(SCOPE.iterdir()):
        if child.is_dir(): shutil.rmtree(child)
        else: child.unlink()
    for child in tmp.iterdir():
        dst=SCOPE/child.name
        if child.is_dir(): shutil.copytree(child,dst)
        else: shutil.copy2(child,dst)
    shutil.rmtree(tmp)
    # Test-lab transport hygiene: http.server uses Last-Modified conditional responses.
    # Git checkouts can give predecessor/successor files identical mtimes even when bytes differ.
    # Advance mtimes only (never bytes) so the synthetic server cannot answer 304 for changed successor files.
    stamp=time.time()+10
    for fp in SCOPE.rglob('*'):
        if fp.is_file(): os.utime(fp,(stamp,stamp))

    pg.evaluate("""async()=>{const r=await navigator.serviceWorker.getRegistration(); await r.update();}""")
    pg.wait_for_function("""async()=>{const r=await navigator.serviceWorker.getRegistration();return !!(r&&(r.waiting||r.installing));}""",timeout=20000)
    worker_state=pg.evaluate("""async()=>{const r=await navigator.serviceWorker.getRegistration();return {waiting:r&&r.waiting&&r.waiting.state,installing:r&&r.installing&&r.installing.state,active:r&&r.active&&r.active.state};}""")
    rec('update:successor_worker_detected',bool(worker_state.get('waiting') or worker_state.get('installing')),worker_state)
    expect(pg.locator('#update-banner')).to_be_visible(timeout=20000)
    rec('update:banner_visible',True,pg.locator('#update-banner-message').inner_text())
    pg.locator('#update-apply-btn').click()
    expect(pg.locator('.build-meta').first).to_contain_text('v2.14',timeout=25000)
    ready(pg,'2.13')
    succ_state=protected_storage(pg)
    rec('update:state_exactly_preserved',all(succ_state.get(k)==pred_state.get(k) for k in ['lp_favs','lp_notes','lp_read','lp_theme','lp_state_schema']),{'before':pred_state,'after':succ_state})
    succ_caches=pg.evaluate("caches.keys()")
    rec('update:successor_cache_ids',any('shell-v2.14-b1' in x for x in succ_caches) and any('corpus-v2.14-b1' in x for x in succ_caches),succ_caches)
    rec('update:predecessor_caches_removed',not any('v2.12-b1' in x for x in succ_caches),succ_caches)
    pg.close(); ctx.set_offline(True); off=ctx.new_page(); c2,e2=errors(off)
    off.goto(LOCAL+'?letter=LP.LETTER.002',wait_until='domcontentloaded',timeout=20000); ready(off,'2.13')
    expect(off.locator('#pr-pos')).to_have_text('2 / 136')
    fav=off.evaluate("JSON.parse(localStorage.getItem('lp_favs')||'[]')")
    note=off.evaluate("localStorage.getItem('lp_notes')||''")
    rec('update:offline_successor_state',2 in fav and 'fresh update sentinel' in note,{'favs':fav,'notes':note[:250]})
    clean('update_offline',c2,e2)
    ctx.set_offline(False); clean('update_online',c,e); ctx.close(); browser.close()

print('FRESH_AUDIT_RESULTS='+json.dumps(R,ensure_ascii=False))
print('PASS_COUNT',sum(1 for x in R if x['ok']),'TOTAL',len(R))
