from playwright.sync_api import sync_playwright, expect
from pathlib import Path
from html.parser import HTMLParser
import urllib.request, hashlib, json, os, shutil, time, re, base64, subprocess, sys

ROOT=Path('lettres-v2.15-b1-contrast-closure')
PRE14=Path('lettres-v2.14-b1-csp-repair')
PRE24=Path('lettres-r9')
PUBLIC='https://louisriv26.github.io/App-Test/lettres-v2.15-b1-contrast-closure/'
R=[]

def rec(name,ok,detail=None):
    R.append({'name':name,'ok':bool(ok),'detail':detail})
    print('CHECK',name,'PASS' if ok else 'FAIL',repr(detail),flush=True)
    if not ok: raise AssertionError(f'{name}: {detail}')

class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.csp=None;self.active=None;self.buf=[];self.scripts=[];self.styles=[]
    def handle_starttag(self,tag,attrs):
        d={k.lower():v for k,v in attrs}
        if tag.lower()=='meta' and (d.get('http-equiv') or '').lower()=='content-security-policy': self.csp=d.get('content')
        if tag.lower() in ('script','style') and not (tag.lower()=='script' and 'src' in d):
            self.active=tag.lower();self.buf=[]
    def handle_data(self,data):
        if self.active:self.buf.append(data)
    def handle_entityref(self,name):
        if self.active:self.buf.append('&'+name+';')
    def handle_charref(self,name):
        if self.active:self.buf.append('&#'+name+';')
    def handle_endtag(self,tag):
        if self.active==tag.lower():
            s=''.join(self.buf)
            (self.scripts if self.active=='script' else self.styles).append(s)
            self.active=None;self.buf=[]

def htoken(s): return "'sha256-"+base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()+"'"

# Static boundary and exact protected bytes.
af={p.relative_to(PRE14).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in PRE14.rglob('*') if p.is_file()}
bf={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file()}
rec('static:file_set_22',set(af)==set(bf) and len(bf)==22,{'pre':len(af),'new':len(bf)})
changed=sorted(k for k in af if af[k]!=bf[k])
rec('static:changed_exactly_three',changed==['index.html','manifest.json','sw.js'],changed)
rec('static:corpus_sha256',bf['corpus.json']=='362e763684e19d818722082b88348d912f06f434d8960e2a278db07b7f63f8ec',bf['corpus.json'])
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
rec('static:manifest_identity',(manifest.get('version'),manifest.get('build_revision'),manifest.get('release_id'))==('2.15','B1','lettres-v2.15-b1-contrast-closure'),manifest)
sw=(ROOT/'sw.js').read_text(encoding='utf-8')
rec('static:sw_identity','v2.14' not in sw and 'shell-v2.15-b1' in sw and 'corpus-v2.15-b1' in sw,None)
index=(ROOT/'index.html').read_text(encoding='utf-8')
rec('static:no_current_v214_identity','v2.14' not in index and "APP_VERSION = '2.15'" in index,None)

# Structural CSP verification from parsed HTML, not regex.
doc=Doc();doc.feed(index)
rec('csp:meta_present',bool(doc.csp),None)
rec('csp:inline_counts',(len(doc.scripts),len(doc.styles))==(1,2),{'scripts':len(doc.scripts),'styles':len(doc.styles)})
dirs={}
for raw in (doc.csp or '').split(';'):
    p=raw.strip().split()
    if p:dirs[p[0]]=p[1:]
mh=htoken(doc.scripts[0]);sh=[htoken(x) for x in doc.styles]
rec('csp:script_elem_exact',dirs.get('script-src-elem')==[mh],dirs.get('script-src-elem'))
rec('csp:script_src_contains_main',mh in dirs.get('script-src',[]),mh)
rec('csp:style_elem_exact',dirs.get('style-src-elem')==sh,{'actual':dirs.get('style-src-elem'),'expected':sh})
rec('csp:style_inline_contract',dirs.get('style-src')==["'unsafe-inline'"],dirs.get('style-src'))

# Public served-edge byte parity for all packaged members.
for rel,want in sorted(bf.items()):
    req=urllib.request.Request(PUBLIC+rel+'?v215edge=20261005',headers={'Cache-Control':'no-cache','Pragma':'no-cache','User-Agent':'Lettres-v215-release-integrity'})
    with urllib.request.urlopen(req,timeout=40) as resp:
        data=resp.read();status=resp.status
    got=hashlib.sha256(data).hexdigest()
    rec('edge:'+rel,status==200 and got==want,{'status':status,'got':got,'want':want})

def ready(pg,version='2.15'):
    pg.locator('#loading').wait_for(state='detached',timeout=25000)
    expect(pg.locator('#list-title')).to_have_text('136 Lettres')
    expect(pg.locator('.build-meta').first).to_contain_text('v'+version)
    pg.wait_for_timeout(800)
    if pg.locator('#help-overlay').is_visible():
        pg.locator('#help-close-btn').click();expect(pg.locator('#help-overlay')).to_be_hidden()

def errors(pg):
    c=[];e=[]
    pg.on('console',lambda m:c.append(m.text) if m.type=='error' else None)
    pg.on('pageerror',lambda x:e.append(str(x)))
    return c,e

def clean(name,c,e):
    bad=[x for x in c if 'Content Security Policy' in x or 'Refused to' in x or 'Uncaught' in x]
    rec(name+':pageerrors',not e,e);rec(name+':csp_console',not bad,bad)

def storage(pg):
    keys=['lp_favs','lp_notes','lp_highlights','lp_read','lp_positions','lp_last','lp_size','lp_theme','lp_state_schema','lp_paths']
    return pg.evaluate("(ks)=>Object.fromEntries(ks.map(k=>[k,localStorage.getItem(k)]))",keys)

def overwrite_scope(scope):
    tmp=Path(str(scope)+'-successor')
    if tmp.exists():shutil.rmtree(tmp)
    shutil.copytree(ROOT,tmp)
    for child in list(scope.iterdir()):
        if child.is_dir():shutil.rmtree(child)
        else:child.unlink()
    for child in tmp.iterdir():
        dst=scope/child.name
        if child.is_dir():shutil.copytree(child,dst)
        else:shutil.copy2(child,dst)
    shutil.rmtree(tmp)
    stamp=time.time()+12
    for fp in scope.rglob('*'):
        if fp.is_file():os.utime(fp,(stamp,stamp))

def upgrade(pw,pre,prever,precache,port,label):
    scope=Path(f'/tmp/lettres-v215-{label}-scope')
    if scope.exists():shutil.rmtree(scope)
    shutil.copytree(pre,scope)
    log=open(f'/tmp/lettres-v215-{label}.log','w')
    proc=subprocess.Popen([sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1'],cwd=scope,stdout=log,stderr=subprocess.STDOUT)
    time.sleep(2)
    try:
        b=pw.chromium.launch(headless=True);ctx=b.new_context(viewport={'width':390,'height':844},locale='fr-FR',service_workers='allow')
        pg=ctx.new_page();c,e=errors(pg);url=f'http://127.0.0.1:{port}/index.html'
        pg.goto(url+'?predecessor='+label,wait_until='networkidle',timeout=30000);ready(pg,prever)
        pg.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.controller")
        pg.locator('#pnav-list').click();pg.locator('#letter-list .letter-item[data-n="2"]').click()
        pg.locator('#pr-fav-btn').click();pg.locator('#pr-read-btn').click()
        pg.get_by_role('button',name='Ajouter une note').click();pg.locator('#note-input').fill('v215 '+label+' preservation sentinel');pg.locator('#note-save-btn').click()
        pg.get_by_role('button',name='Réglages').last.click();pg.locator('[data-theme-choice="dark"]').click();pg.get_by_role('button',name='Fermer les réglages').click()
        before=storage(pg);pre_caches=pg.evaluate("caches.keys()")
        rec(label+':predecessor_cache',any('shell-'+precache in x for x in pre_caches) and any('corpus-'+precache in x for x in pre_caches),pre_caches)
        overwrite_scope(scope)
        pg.evaluate("async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()}")
        pg.wait_for_function("async()=>{const r=await navigator.serviceWorker.getRegistration();return !!(r&&(r.waiting||r.installing))}",timeout=25000)
        expect(pg.locator('#update-banner')).to_be_visible(timeout=25000)
        rec(label+':update_banner',True,pg.locator('#update-banner-message').inner_text())
        pg.locator('#update-apply-btn').click();expect(pg.locator('.build-meta').first).to_contain_text('v2.15',timeout=25000);ready(pg,'2.15')
        after=storage(pg)
        for k in ['lp_favs','lp_notes','lp_read','lp_theme']:
            rec(label+':preserve:'+k,before.get(k)==after.get(k),{'before':before.get(k),'after':after.get(k)})
        rec(label+':schema_not_downgraded',int(after.get('lp_state_schema') or 0)>=int(before.get('lp_state_schema') or 0),{'before':before.get('lp_state_schema'),'after':after.get('lp_state_schema')})
        caches=pg.evaluate("caches.keys()")
        rec(label+':successor_cache',any('shell-v2.15-b1' in x for x in caches) and any('corpus-v2.15-b1' in x for x in caches),caches)
        rec(label+':old_cache_removed',not any(precache in x for x in caches),caches)
        pg.close();ctx.set_offline(True);off=ctx.new_page();c2,e2=errors(off)
        off.goto(url+'?letter=LP.LETTER.002',wait_until='domcontentloaded',timeout=20000);ready(off,'2.15')
        expect(off.locator('#pr-pos')).to_have_text('2 / 136')
        fav=off.evaluate("JSON.parse(localStorage.getItem('lp_favs')||'[]')");notes=off.evaluate("localStorage.getItem('lp_notes')||''")
        rec(label+':offline_state',2 in fav and ('v215 '+label+' preservation sentinel') in notes,{'favs':fav,'notes':notes[:220]})
        clean(label+':offline',c2,e2);ctx.set_offline(False);clean(label+':online',c,e)
        ctx.close();b.close()
    finally:
        proc.terminate()
        try:proc.wait(timeout=5)
        except:proc.kill()
        log.close()

with sync_playwright() as pw:
    # Independent blind challenge uses different entry points from the main 62-check regression.
    b=pw.chromium.launch(headless=True);ctx=b.new_context(viewport={'width':412,'height':915},locale='fr-FR',service_workers='allow')
    pg=ctx.new_page();c,e=errors(pg)
    pg.goto(PUBLIC+'index.html?letter=LP.LETTER.136&dp=LP.LETTER.136.DP999',wait_until='domcontentloaded',timeout=30000);ready(pg)
    expect(pg.locator('#pr-pos')).to_have_text('136 / 136');expect(pg.locator('#pr-btn-next')).to_be_disabled()
    rec('blind:boundary136',True,pg.url)
    pg.get_by_role('button',name='Retour à la liste').click();pg.locator('#pnav-search').click();pg.locator('#search-input').fill('abandon');pg.wait_for_timeout(700)
    rec('blind:search_abandon',pg.locator('#search-results [data-action="search-result"]').count()>0,pg.locator('#search-results').inner_text()[:300])
    pg.locator('#pnav-home').click();pg.locator('#home-settings-btn').click()
    with pg.expect_download(timeout=10000) as di:pg.locator('#settings-export-btn').click()
    data=json.load(open(di.value.path(),encoding='utf-8'))
    rec('blind:export_identity',data.get('app_version')=='2.15' and data.get('format')=='luisa-letters-user-data',{'version':data.get('app_version'),'format':data.get('format')})
    clean('blind:chromium',c,e);ctx.close();b.close()

    wb=pw.webkit.launch(headless=True);ctx=wb.new_context(viewport={'width':834,'height':1112},locale='fr-FR')
    pg=ctx.new_page();c,e=errors(pg);pg.goto(PUBLIC+'index.html?screen=search&q=confiance',wait_until='domcontentloaded',timeout=30000);ready(pg)
    expect(pg.locator('#search-input')).to_have_value('confiance');pg.wait_for_timeout(700)
    rec('blind:webkit_search',pg.locator('#search-results [data-action="search-result"]').count()>0,None)
    clean('blind:webkit',c,e);ctx.close();wb.close()

    upgrade(pw,PRE14,'2.14','v2.14-b1',8132,'upgrade-v214')
    upgrade(pw,PRE24,'2.4','v2.4-b1',8134,'upgrade-v24')

print('RELEASE_INTEGRITY_RESULTS='+json.dumps(R,ensure_ascii=False))
print('PASS_COUNT',sum(1 for x in R if x['ok']),'TOTAL',len(R))
