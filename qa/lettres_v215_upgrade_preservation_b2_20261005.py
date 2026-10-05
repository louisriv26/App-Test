from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import argparse, json, shutil, os, time

ap=argparse.ArgumentParser()
ap.add_argument('--pre',required=True)
ap.add_argument('--pre-version',required=True)
ap.add_argument('--pre-cache',required=True)
ap.add_argument('--port',type=int,required=True)
ap.add_argument('--label',required=True)
a=ap.parse_args()
ROOT=Path('lettres-v2.15-b2-contrast-repair')
PRE=Path(a.pre)
SCOPE=Path(f'/tmp/lettres-v215-{a.label}-scope')
URL=f'http://127.0.0.1:{a.port}/index.html'
R=[]
def rec(n,ok,d=None):
    R.append({'name':n,'ok':bool(ok),'detail':d});print('CHECK',n,'PASS' if ok else 'FAIL',repr(d),flush=True)
    if not ok:raise AssertionError(f'{n}: {d}')
def ready(pg,v):
    pg.locator('#loading').wait_for(state='detached',timeout=25000)
    expect(pg.locator('#list-title')).to_have_text('136 Lettres')
    expect(pg.locator('.build-meta').first).to_contain_text('v'+v)
    pg.wait_for_timeout(700)
    if pg.locator('#help-overlay').is_visible():
        pg.evaluate("()=>{try{closeHelp(true)}catch(e){}}")
def state(pg):
    keys=['lp_favs','lp_notes','lp_highlights','lp_read','lp_positions','lp_last','lp_size','lp_theme','lp_state_schema','lp_paths']
    return pg.evaluate("(ks)=>Object.fromEntries(ks.map(k=>[k,localStorage.getItem(k)]))",keys)

if SCOPE.exists():shutil.rmtree(SCOPE)
shutil.copytree(PRE,SCOPE)
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True);c=b.new_context(viewport={'width':390,'height':844},locale='fr-FR',service_workers='allow')
    p=c.new_page();p.goto(URL+'?pre=1',wait_until='networkidle',timeout=30000);ready(p,a.pre_version)
    p.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.controller && window._swReg",timeout=20000)
    rec(a.label+':app_update_listener_ready',bool(p.evaluate("()=>!!(window._swReg && navigator.serviceWorker.controller)")),None)
    p.locator('#pnav-list').click();p.locator('#letter-list .letter-item[data-n="2"]').click()
    p.locator('#pr-fav-btn').click();p.locator('#pr-read-btn').click()
    p.get_by_role('button',name='Ajouter une note').click();p.locator('#note-input').fill('v215 preservation sentinel');p.locator('#note-save-btn').click()
    # create a highlight where supported
    dps=p.locator('#phone-reader-scroll [data-dp-id]')
    if dps.count():
        d=dps.first
        d.evaluate("""el=>{let w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),n;while(n=w.nextNode()){let t=n.nodeValue||'';let i=t.search(/\\S/);if(i>=0&&t.slice(i).trim().length>=6){let r=document.createRange();r.setStart(n,i);r.setEnd(n,Math.min(t.length,i+6));let s=getSelection();s.removeAllRanges();s.addRange(r);return true}}return false}""")
        p.locator('#phone-reader-scroll').dispatch_event('mouseup')
        if p.locator('#hl-popup').is_visible():
            p.get_by_role('button',name='Surligner').click();p.get_by_role('button',name='Jaune').click()
    p.get_by_role('button',name='Réglages').last.click();p.locator('[data-theme-choice="dark"]').click()
    if p.locator('[data-text-level="large"]').count():p.locator('[data-text-level="large"]').click()
    p.get_by_role('button',name='Fermer les réglages').click()
    before=state(p);pre_caches=p.evaluate("caches.keys()")
    rec(a.label+':pre_cache',any(a.pre_cache in x for x in pre_caches),pre_caches)

    tmp=Path('/tmp/lettres-v215-successor-copy')
    if tmp.exists():shutil.rmtree(tmp)
    shutil.copytree(ROOT,tmp)
    for ch in list(SCOPE.iterdir()):
        if ch.is_dir():shutil.rmtree(ch)
        else:ch.unlink()
    for ch in tmp.iterdir():
        dst=SCOPE/ch.name
        if ch.is_dir():shutil.copytree(ch,dst)
        else:shutil.copy2(ch,dst)
    shutil.rmtree(tmp)
    stamp=time.time()+10
    for fp in SCOPE.rglob('*'):
        if fp.is_file():os.utime(fp,(stamp,stamp))
    p.evaluate("async()=>{await window._swReg.update()}")
    p.wait_for_function("()=>!!(window._swReg && window._swReg.waiting)",timeout=30000)
    rec(a.label+':waiting_successor_detected',bool(p.evaluate("()=>!!(window._swReg && window._swReg.waiting)")),p.evaluate("()=>({waiting:window._swReg&&window._swReg.waiting&&window._swReg.waiting.state,installing:window._swReg&&window._swReg.installing&&window._swReg.installing.state,banner:getComputedStyle(document.getElementById('update-banner')).display})"))
    expect(p.locator('#update-banner')).to_be_visible(timeout=10000)
    p.locator('#update-apply-btn').click();ready(p,'2.15')
    after=state(p)
    for k in ['lp_favs','lp_notes','lp_highlights','lp_read','lp_positions','lp_size','lp_theme','lp_state_schema','lp_paths']:
        rec(a.label+':preserve:'+k,after.get(k)==before.get(k),{'before':before.get(k),'after':after.get(k)})
    caches=p.evaluate("caches.keys()")
    rec(a.label+':new_shell',any('shell-v2.15-b2' in x for x in caches),caches)
    rec(a.label+':new_corpus',any('corpus-v2.15-b2' in x for x in caches),caches)
    rec(a.label+':old_removed',not any(a.pre_cache in x for x in caches),caches)
    p.close();c.set_offline(True);q=c.new_page();q.goto(URL+'?letter=LP.LETTER.002',wait_until='domcontentloaded',timeout=20000);ready(q,'2.15')
    expect(q.locator('#pr-pos')).to_have_text('2 / 136')
    rec(a.label+':offline_state','v215 preservation sentinel' in (q.evaluate("localStorage.getItem('lp_notes')||''")))
    c.close();b.close()
print('UPGRADE_PASS',a.label,len(R))
