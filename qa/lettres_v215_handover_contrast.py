from playwright.sync_api import sync_playwright
from pathlib import Path
import json, re

BASE='http://127.0.0.1:8120/lettres-v2.15-b1-contrast-closure/'
AXE=Path('node_modules/axe-core/axe.min.js')
OUT=[]; FAIL=[]
MODES=[
 {'name':'explicit-light','stored':'light','scheme':'light'},
 {'name':'explicit-dark','stored':'dark','scheme':'dark'},
 {'name':'system-light','stored':'system','scheme':'light'},
 {'name':'system-dark','stored':'system','scheme':'dark'}]
VPS=[
 {'name':'phone','width':390,'height':844},
 {'name':'ipad','width':820,'height':1180},
 {'name':'desktop','width':1535,'height':959}]

def lum(c):
    vals=[]
    for v in c[:3]:
        x=v/255
        vals.append(x/12.92 if x<=.03928 else ((x+.055)/1.055)**2.4)
    return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
def ratio(a,b):
    A,B=lum(a),lum(b);return (max(A,B)+.05)/(min(A,B)+.05)
def blend(fg,bg,alpha=None):
    a=fg[3] if alpha is None else alpha
    return [fg[i]*a+bg[i]*(1-a) for i in range(3)]+[1]
def direct(page,sel):
    d=page.locator(sel).first.evaluate("""el=>{
      const P=s=>{const m=(s||'').match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(',').map(x=>+x.trim());return [a[0],a[1],a[2],a.length>3?a[3]:1]};
      function nearest(node){let n=node;while(n){const c=P(getComputedStyle(n).backgroundColor);if(c&&c[3]>0)return c;n=n.parentElement}return [255,255,255,1]}
      const cs=getComputedStyle(el),fg=P(cs.color),own=P(cs.backgroundColor),under=nearest(el.parentElement),bg=own&&own[3]>0?own:under;
      return {text:(el.textContent||'').trim(),color:cs.color,bg:cs.backgroundColor,opacity:+cs.opacity,fg,bgResolved:bg,under,fontSize:cs.fontSize,display:cs.display};
    }""")
    fg=d['fg'];bg=d['bgResolved'];under=d['under'];op=d['opacity']
    if fg is None:return {**d,'ratio':None}
    fg=blend(fg,bg) if fg[3]<1 else fg[:3]+[1]
    bg=blend(bg,under) if bg[3]<1 else bg[:3]+[1]
    if op<1:
        fg=blend(fg,under,op);bg=blend(bg,under,op)
    d['ratio']=ratio(fg,bg);return d
def ready(p):
    p.wait_for_function("window.__LET_F_TEST && document.querySelectorAll('.letter-item').length===136",timeout=30000)
    p.wait_for_timeout(650)
    if p.locator('#help-overlay').is_visible():
        p.evaluate("()=>{try{closeHelp(true)}catch(e){}}");p.wait_for_timeout(250)
def axe_scan(p,label,context):
    p.wait_for_timeout(420)
    if not p.evaluate("()=>typeof axe!=='undefined'"):p.add_script_tag(path=str(AXE))
    r=p.evaluate("""async()=>await axe.run(document,{runOnly:{type:'rule',values:['color-contrast']}})""")
    nodes=[]
    for v in r.get('violations',[]):
        for n in v.get('nodes',[]):nodes.append({'target':n.get('target'),'html':n.get('html','')[:300],'failureSummary':n.get('failureSummary')})
    OUT.append({'context':context,'scene':label,'axe_failures':nodes})
    if nodes:FAIL.append({'context':context,'scene':label,'axe_failures':nodes})
def check_direct(name,d,context,min_ratio=4.5):
    item={'context':context,'direct':name,**d};OUT.append(item)
    if d.get('ratio') is None or d['ratio']+1e-9<min_ratio:FAIL.append(item)

with sync_playwright() as pw:
  for mode in MODES:
    for vp in VPS:
      b=pw.chromium.launch(headless=True)
      ctx=b.new_context(viewport={'width':vp['width'],'height':vp['height']},locale='fr-FR',color_scheme=mode['scheme'],bypass_csp=True)
      ctx.add_init_script(f"""(()=>{{localStorage.setItem('lp_theme',{json.dumps(mode['stored'])});localStorage.setItem('lp_size','normal');localStorage.setItem('lp_onboarded','1');}})()""")
      p=ctx.new_page();context=f"{vp['name']}/{mode['name']}"
      p.goto(BASE+'?contrast=1',wait_until='domcontentloaded',timeout=30000);ready(p);p.add_script_tag(path=str(AXE))
      for panel in ['p-home','p-list','p-search','p-notes','p-explore']:
        p.evaluate("(id)=>switchPanel(id)",panel);axe_scan(p,panel,context)
      if p.locator('#snav-list').is_visible():
        p.evaluate("()=>switchPanel('p-home')");p.wait_for_timeout(250)
        check_direct('sidebar-inactive',direct(p,'#snav-list'),context)
        check_direct('sidebar-build-meta',direct(p,'.sidebar-bottom .build-meta'),context)
        p.locator('#snav-list').hover();p.wait_for_timeout(220);axe_scan(p,'sidebar-hover',context)
        p.locator('#snav-search').focus();p.wait_for_timeout(220);axe_scan(p,'sidebar-focus',context)
        p.evaluate("()=>switchPanel('p-list')");p.wait_for_timeout(220);check_direct('sidebar-active',direct(p,'#snav-list'),context)
      p.evaluate("()=>switchPanel('p-home')");p.wait_for_timeout(220);check_direct('home-build-meta',direct(p,'#home-scroll .build-meta'),context)
      p.evaluate("()=>openTextBar('data')");p.wait_for_timeout(450);axe_scan(p,'settings-data',context)
      check_direct('export-text',direct(p,'#settings-export-btn'),context);check_direct('export-icon',direct(p,'#settings-export-btn .ti'),context)
      p.locator('#settings-export-btn').hover();p.wait_for_timeout(220)
      check_direct('export-hover-text',direct(p,'#settings-export-btn'),context);check_direct('export-hover-icon',direct(p,'#settings-export-btn .ti'),context)
      axe_scan(p,'settings-export-hover',context)
      p.locator('#settings-export-btn').focus();p.wait_for_timeout(220);axe_scan(p,'settings-export-focus',context)
      p.evaluate("()=>closeTextBar(true)");p.wait_for_timeout(220)
      p.evaluate("()=>{localStorage.setItem('lp_read','[1]');location.reload()}");ready(p);p.add_script_tag(path=str(AXE));p.evaluate("()=>switchPanel('p-list')");p.wait_for_timeout(420)
      axe_scan(p,'list-read-state',context)
      if p.locator('.li-read').count():check_direct('read-title',direct(p,'.li-read'),context)
      p.evaluate("()=>switchPanel('p-explore')");p.wait_for_timeout(250)
      first=p.locator('[data-path-id]').first
      if first.count():
        pid=first.get_attribute('data-path-id');p.evaluate("(id)=>openPath(id)",pid);p.wait_for_timeout(250)
        if p.locator('.path-letter-item').count():
          n=int(p.locator('.path-letter-item').first.get_attribute('data-n'))
          p.evaluate("(n)=>{let a=JSON.parse(localStorage.getItem('lp_read')||'[]');if(!a.includes(n))a.push(n);localStorage.setItem('lp_read',JSON.stringify(a));location.reload()}",n)
          ready(p);p.add_script_tag(path=str(AXE));p.evaluate("(id)=>{switchPanel('p-explore');openPath(id)}",pid);p.wait_for_timeout(420)
          axe_scan(p,'path-done-state',context)
          if p.locator('.path-letter-item.done').count():
            check_direct('path-done-title',direct(p,'.path-letter-item.done .path-letter-title'),context)
            check_direct('path-done-meta',direct(p,'.path-letter-item.done .path-letter-meta'),context)
      p.evaluate("()=>{sessionStorage.clear();location.href=location.pathname+'?screen=list&contrast-empty=1'}");ready(p);p.add_script_tag(path=str(AXE));p.wait_for_timeout(420);axe_scan(p,'empty-reader',context)
      if p.locator('#reader-empty small').is_visible():check_direct('empty-reader-small',direct(p,'#reader-empty small'),context)
      p.evaluate("async()=>{if(typeof openLetter==='function')await openLetter(1)}");p.wait_for_timeout(420);axe_scan(p,'reader-letter-1',context)
      ctx.close();b.close()

summary={'candidate':'lettres-v2.15-b1-contrast-closure','matrix_contexts':len(MODES)*len(VPS),'checks':len(OUT),'failure_count':len(FAIL)}
Path('LETTRES_V2_15_CONTRAST_QUALIFICATION_2026-10-05.json').write_text(json.dumps({'summary':summary,'failures':FAIL,'results':OUT},ensure_ascii=False,indent=2),encoding='utf-8')
print('CONTRAST_CONTEXTS',summary['matrix_contexts']);print('CONTRAST_CHECKS',len(OUT));print('CONTRAST_FAILURES',len(FAIL))
if FAIL:
    print(json.dumps(FAIL[:20],ensure_ascii=False,indent=2));raise SystemExit(2)
print('CONTRAST_QUALIFICATION_PASS')
