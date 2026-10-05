from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import shutil,os,time,hashlib,urllib.request,json

PRE=Path('lettres-v2.14-b1-csp-repair')
CUR=Path('lettres-v2.15-b2-contrast-repair')
SCOPE=Path('/tmp/lettres-v215-update-diag')
URL='http://127.0.0.1:8136/index.html'
EXPECTED='47903e6260918d8180b7b947067e8ce8a9f80ddb8c3202a79d966c326923620a'

def ready(p,v):
    p.locator('#loading').wait_for(state='detached',timeout=30000)
    expect(p.locator('#letter-list .letter-item')).to_have_count(136)
    expect(p.locator('.build-meta').first).to_contain_text('v'+v)
    p.wait_for_timeout(500)
    if p.locator('#help-overlay').is_visible():p.evaluate("()=>{try{closeHelp(true)}catch(e){}}")

with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True)
    c=b.new_context(viewport={'width':390,'height':844},locale='fr-FR',service_workers='allow')
    c.add_init_script("localStorage.setItem('lp_onboarded','1')")
    p=c.new_page()
    errs=[]
    p.on('pageerror',lambda e:errs.append('page:'+str(e)))
    p.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' else None)
    p.goto(URL+'?diag=pre',wait_until='networkidle',timeout=30000);ready(p,'2.14')
    p.wait_for_function("()=>!!(navigator.serviceWorker.controller && window._swReg)",timeout=20000)
    pre=p.evaluate("""()=>({controller:navigator.serviceWorker.controller&&navigator.serviceWorker.controller.scriptURL,
      active:window._swReg.active&&window._swReg.active.state,
      waiting:window._swReg.waiting&&window._swReg.waiting.state,
      installing:window._swReg.installing&&window._swReg.installing.state,
      updateViaCache:window._swReg.updateViaCache})""")
    print('DIAG_PRE',json.dumps(pre),flush=True)
    print('DIAG_PRE_CACHES',p.evaluate("()=>caches.keys()"),flush=True)

    tmp=Path('/tmp/lettres-v215-update-diag-copy')
    if tmp.exists():shutil.rmtree(tmp)
    shutil.copytree(CUR,tmp)
    for ch in list(SCOPE.iterdir()):
        if ch.is_dir():shutil.rmtree(ch)
        else:ch.unlink()
    for ch in tmp.iterdir():
        dst=SCOPE/ch.name
        if ch.is_dir():shutil.copytree(ch,dst)
        else:shutil.copy2(ch,dst)
    shutil.rmtree(tmp)
    stamp=time.time()+30
    for fp in SCOPE.rglob('*'):
        if fp.is_file():os.utime(fp,(stamp,stamp))

    raw=urllib.request.urlopen('http://127.0.0.1:8136/sw.js?outside='+str(time.time()),timeout=10).read()
    print('DIAG_SERVER_SW_SHA256',hashlib.sha256(raw).hexdigest(),flush=True)
    assert hashlib.sha256(raw).hexdigest()==EXPECTED
    probe=p.evaluate("""async()=>{let r=await fetch('./sw.js?browserprobe='+Date.now(),{cache:'no-store'});let t=await r.text();
      return {status:r.status,hasB2:t.includes('shell-v2.15-b2'),hasV214:t.includes('shell-v2.14-b1'),len:t.length};}""")
    print('DIAG_BROWSER_FETCH',json.dumps(probe),flush=True)

    p.evaluate("""()=>{
      window.__UPD_AUDIT=[];
      const r=window._swReg;
      const snap=(tag,w)=>window.__UPD_AUDIT.push({tag,state:w&&w.state||null,at:Date.now()});
      r.addEventListener('updatefound',()=>{let w=r.installing;snap('updatefound',w);if(w)w.addEventListener('statechange',()=>snap('statechange',w));});
    }""")
    result=p.evaluate("""async()=>{try{await window._swReg.update();return {ok:true}}catch(e){return {ok:false,error:String(e)}}}""")
    print('DIAG_UPDATE_CALL',json.dumps(result),flush=True)
    timeline=[]
    for i in range(61):
        st=p.evaluate("""()=>({i:0,active:window._swReg&&window._swReg.active&&window._swReg.active.state,
          activeUrl:window._swReg&&window._swReg.active&&window._swReg.active.scriptURL,
          installing:window._swReg&&window._swReg.installing&&window._swReg.installing.state,
          waiting:window._swReg&&window._swReg.waiting&&window._swReg.waiting.state,
          banner:getComputedStyle(document.getElementById('update-banner')).display,
          events:window.__UPD_AUDIT||[]})""")
        st['i']=i;timeline.append(st)
        if st['waiting'] or st['banner']=='flex':break
        time.sleep(1)
    print('DIAG_FINAL',json.dumps(timeline[-1]),flush=True)
    print('DIAG_EVENTS',json.dumps(timeline[-1]['events']),flush=True)
    print('DIAG_CACHES',p.evaluate("()=>caches.keys()"),flush=True)
    print('DIAG_ERRORS',json.dumps(errs),flush=True)
    print('DIAG_WAITING',bool(timeline[-1]['waiting']),'BANNER',timeline[-1]['banner'],flush=True)
    Path('/tmp/LETTRES_V215_UPDATE_DIAGNOSTIC.json').write_text(json.dumps({'pre':pre,'browser_probe':probe,'timeline':timeline,'errors':errs},indent=2),encoding='utf-8')
    c.close();b.close()
