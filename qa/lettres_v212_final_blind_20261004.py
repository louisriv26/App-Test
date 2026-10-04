from playwright.sync_api import sync_playwright, expect
import urllib.request, hashlib, json, math, re

PUBLIC='https://louisriv26.github.io/App-Test/lettres-v2.12-b1-darkmode/'
EXPECTED={
 'index.html':'0a06cd637d0a6bccbc05e68d8d58e0cf590bc9a3b440049af6950e467f3e2d57',
 'sw.js':'276aed0fb82c242ca8b2586dc8b9f672367b37159fae43a9130a0c43906af76a',
 'corpus.json':'362e763684e19d818722082b88348d912f06f434d8960e2a278db07b7f63f8ec',
 'manifest.json':'887794bf32fb8b2813924caea2002bc40964c7d0ecbc4d5b2cf80d2d1c9d62d2',
}
FILTER_COUNTS={'all':136,'fav':0,'unread':136,'Divine Volonté':17,'Croix':8,'Paix':12,'Prêtres':7,'Deuil':4,'Confiance':10,'Propagation des écrits':14}
PATHS={
 'paix':[7,55,53,50,57,12,18],
 'divine-volonte':[21,19,44,67,110,101,113],
 'croix':[9,13,15,17,42,103,124],
 'saintete':[2,5,61,78,85,120,127],
 'propagation':[35,36,47,67,75,87,116],
 'abandon':[44,50,58,74,93,107,131],
}
R=[]
def rec(name,ok,detail=None):
    R.append({'name':name,'ok':bool(ok),'detail':detail})
    print('CHECK',name,'PASS' if ok else 'FAIL',repr(detail),flush=True)
    if not ok: raise AssertionError(f'{name}: {detail}')
def ready(pg):
    pg.locator('#loading').wait_for(state='detached',timeout=20000)
    expect(pg.locator('#list-title')).to_have_text('136 Lettres')
    expect(pg.locator('.build-meta').first).to_contain_text('v2.12')
    expect(pg.locator('.error-state')).to_have_count(0)
    pg.wait_for_timeout(1200)
    if pg.locator('#help-overlay').is_visible():
        pg.locator('#help-close-btn').click()
        expect(pg.locator('#help-overlay')).to_be_hidden()
def attach_errors(pg):
    c=[]; e=[]
    pg.on('console',lambda m:c.append(m.text) if m.type=='error' else None)
    pg.on('pageerror',lambda x:e.append(str(x)))
    return c,e
def assert_clean(name,c,e):
    bad=[x for x in c if 'Content Security Policy' in x or 'Refused to' in x or 'Uncaught' in x]
    rec(name+':pageerrors',not e,e); rec(name+':console_errors',not c,c); rec(name+':csp',not bad,bad)
def rgb(s):
    m=re.search(r'rgba?\((\d+)[, ]+\s*(\d+)[, ]+\s*(\d+)',s)
    return tuple(map(int,m.groups())) if m else None
def lum(c):
    a=[]
    for x in c:
        z=x/255
        a.append(z/12.92 if z<=0.04045 else ((z+0.055)/1.055)**2.4)
    return .2126*a[0]+.7152*a[1]+.0722*a[2]
def contrast(a,b):
    x,y=lum(a),lum(b)
    return (max(x,y)+.05)/(min(x,y)+.05)

for name,want in EXPECTED.items():
    req=urllib.request.Request(PUBLIC+name+'?blind=20261004',headers={'Cache-Control':'no-cache','Pragma':'no-cache','User-Agent':'Lettres-v2.12-final-blind'})
    with urllib.request.urlopen(req,timeout=30) as r:
        data=r.read(); status=r.status
    got=hashlib.sha256(data).hexdigest()
    rec('edge:'+name+':http',status==200,status)
    rec('edge:'+name+':sha256',got==want,{'got':got,'want':want})

with sync_playwright() as p:
    for engine_name,launcher in [('chromium',p.chromium),('webkit',p.webkit)]:
        browser=launcher.launch(headless=True)
        ctx=browser.new_context(viewport={'width':390,'height':844},locale='fr-FR',service_workers='allow')
        pg=ctx.new_page(); c,e=attach_errors(pg)
        resp=pg.goto(PUBLIC+'index.html?blind='+engine_name,wait_until='domcontentloaded',timeout=30000)
        rec(engine_name+':http',bool(resp and resp.ok),resp.status if resp else None)
        ready(pg); rec(engine_name+':identity',True,pg.locator('.build-meta').first.inner_text())
        if engine_name=='chromium':
            pg.get_by_role('button',name='Réglages').last.click()
            pg.locator('[data-theme-choice="dark"]').click()
            pg.get_by_role('button',name='Fermer les réglages').click()
            pg.reload(wait_until='domcontentloaded'); ready(pg)
            rec('dark:persist',pg.locator('html').get_attribute('data-theme')=='dark',pg.locator('html').get_attribute('data-theme'))
            pg.locator('#pnav-list').click()
            for key,want in FILTER_COUNTS.items():
                b=pg.locator('.chip[data-filter="'+key.replace('"','\\"')+'"]')
                expect(b).to_have_count(1); b.click(); pg.wait_for_timeout(80)
                got=pg.locator('#letter-list .letter-item').count()
                rec('filter:'+key,got==want,{'got':got,'want':want})
            pg.locator('#pnav-explore').click(); pg.wait_for_timeout(100)
            for pid,want in PATHS.items():
                card=pg.locator('#exp-paths-grid [data-path-id="'+pid+'"]')
                expect(card).to_have_count(1); card.click()
                expect(pg.locator('#path-modal')).to_have_class(re.compile('show'))
                got=[int(x) for x in pg.locator('#path-letter-list .path-letter-item').evaluate_all("els=>els.map(e=>e.dataset.n)")]
                rec('path:'+pid,got==want,{'got':got,'want':want})
                if pid=='abandon':
                    pg.locator('#path-letter-list .path-letter-item').first.click(); pg.wait_for_timeout(250)
                    expect(pg.locator('#pr-pos')).to_have_text('44 / 136'); rec('path:abandon:open44',True)
                    pg.get_by_role('button',name='Retour à la liste').click(); pg.locator('#pnav-explore').click()
                else:
                    pg.locator('#path-modal-back').click()
                    expect(pg.locator('#path-modal')).not_to_have_class(re.compile('show'))
            pg.evaluate('openHelp(0)'); expect(pg.locator('#help-overlay')).to_be_visible()
            for bid in ['help-prev','help-next']:
                data=pg.locator('#'+bid).evaluate("el=>{let s=getComputedStyle(el);return {fg:s.color,bg:s.backgroundColor,disp:s.display,vis:s.visibility,op:s.opacity}}")
                fg,bg=rgb(data['fg']),rgb(data['bg']); ratio=contrast(fg,bg) if fg and bg else 0
                rec('help_dark:'+bid+':visible',data['disp']!='none' and data['vis']!='hidden' and float(data['op'] or 1)>0,data)
                rec('help_dark:'+bid+':contrast',ratio>=4.5,round(ratio,2))
            for i in range(11): pg.locator('#help-next').click()
            expect(pg.locator('#help-slide-label')).to_have_text('12 / 12')
            for i in range(11): pg.locator('#help-prev').click()
            expect(pg.locator('#help-slide-label')).to_have_text('1 / 12')
            rec('help_dark:12_forward_back',True); pg.locator('#help-close-btn').click()
            pg.goto(PUBLIC+'index.html?offline-prep=1',wait_until='networkidle',timeout=30000); ready(pg)
            pg.evaluate("navigator.serviceWorker.ready.then(()=>true)"); pg.wait_for_timeout(4500)
            pg.reload(wait_until='networkidle'); ready(pg); ctx.set_offline(True)
            off=ctx.new_page(); c2,e2=attach_errors(off)
            off.goto(PUBLIC+'index.html?letter=LP.LETTER.010',wait_until='domcontentloaded',timeout=20000); ready(off)
            expect(off.locator('#pr-pos')).to_have_text('10 / 136'); rec('edge_offline:deep10',True)
            assert_clean('edge_offline',c2,e2); off.close(); ctx.set_offline(False)
        assert_clean(engine_name,c,e)
        ctx.close(); browser.close()

print('BLIND_RESULTS='+json.dumps(R,ensure_ascii=False))
print('PASS_COUNT',sum(1 for x in R if x['ok']),'TOTAL',len(R))
