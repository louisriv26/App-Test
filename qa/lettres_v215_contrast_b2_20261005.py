from playwright.sync_api import sync_playwright
from pathlib import Path
import json,re,math

BASE='http://127.0.0.1:8120/lettres-v2.15-b2-contrast-repair/'
OUT=[]; FAIL=[]
MODES=[
 ('explicit-light','light','light'),('explicit-dark','dark','dark'),
 ('system-light','system','light'),('system-dark','system','dark')
]
VPS=[('phone',390,844),('ipad',820,1180),('desktop',1535,959)]

def parse_rgb(s):
    m=re.match(r'rgba?\\(([^)]+)\\)',s or '')
    if not m:return None
    a=[float(x.strip()) for x in m.group(1).split(',')]
    return [a[0],a[1],a[2],a[3] if len(a)>3 else 1.0]
def L(c):
    z=[]
    for v in c[:3]:
        x=v/255.0; z.append(x/12.92 if x<=.03928 else ((x+.055)/1.055)**2.4)
    return .2126*z[0]+.7152*z[1]+.0722*z[2]
def cr(a,b):
    A,B=L(a),L(b);return (max(A,B)+.05)/(min(A,B)+.05)
def blend(f,b,a):return [f[i]*a+b[i]*(1-a) for i in range(3)]+[1]
def measure(p,sel):
    d=p.locator(sel).first.evaluate("""el=>{
      const P=s=>{const m=(s||'').match(/rgba?\\(([^)]+)\\)/);if(!m)return null;const a=m[1].split(',').map(x=>+x.trim());return [a[0],a[1],a[2],a.length>3?a[3]:1]};
      function bg(n){while(n){const x=P(getComputedStyle(n).backgroundColor);if(x&&x[3]>0)return x;n=n.parentElement}return [255,255,255,1]}
      const cs=getComputedStyle(el),f=P(cs.color),own=P(cs.backgroundColor),under=bg(el.parentElement);
      return {text:(el.textContent||'').trim(),color:cs.color,background:cs.backgroundColor,opacity:+cs.opacity,fontSize:cs.fontSize,fg:f,bg:(own&&own[3]>0)?own:under,under};
    }""")
    f,b,u=d['fg'],d['bg'],d['under']
    if not f:return {**d,'ratio':None}
    if f[3]<1:f=blend(f,b,f[3])
    else:f=f[:3]+[1]
    if b[3]<1:b=blend(b,u,b[3])
    else:b=b[:3]+[1]
    if d['opacity']<1:
        f=blend(f,u,d['opacity']);b=blend(b,u,d['opacity'])
    d['ratio']=cr(f,b);return d
def chk(name,d,ctx,minimum=4.5):
    row={'context':ctx,'check':name,**d};OUT.append(row)
    if d.get('ratio') is None or d['ratio']+1e-9<minimum:FAIL.append(row)
def ready(p):
    p.wait_for_function("window.__LET_F_TEST && document.querySelectorAll('.letter-item').length===136",timeout=30000)
    p.wait_for_timeout(650)
    if p.locator('#help-overlay').is_visible():p.evaluate("()=>{try{closeHelp(true)}catch(e){}}")
def axe(p,label,ctx):
    r=p.evaluate("""async()=>await axe.run(document,{runOnly:{type:'rule',values:['color-contrast']}})""")
    nodes=[]
    for v in r.get('violations',[]):
        for n in v.get('nodes',[]):nodes.append({'target':n.get('target'),'html':n.get('html','')[:240],'failureSummary':n.get('failureSummary')})
    OUT.append({'context':ctx,'scene':label,'axe_failures':nodes})
    if nodes:FAIL.append({'context':ctx,'scene':label,'axe_failures':nodes})

with sync_playwright() as pw:
  for name,stored,scheme in MODES:
    for vpn,w,h in VPS:
      b=pw.chromium.launch(headless=True);c=b.new_context(viewport={'width':w,'height':h},locale='fr-FR',color_scheme=scheme,bypass_csp=True)
      c.add_init_script(f"localStorage.setItem('lp_theme',{json.dumps(stored)});localStorage.setItem('lp_size','normal');localStorage.setItem('lp_onboarded','1');")
      p=c.new_page();ctx=f'{vpn}/{name}';p.goto(BASE+'?contrast=1',wait_until='domcontentloaded');ready(p)
      p.add_script_tag(path='node_modules/axe-core/axe.min.js')
      for panel in ['p-home','p-list','p-search','p-notes','p-explore']:
        p.evaluate("(x)=>switchPanel(x)",panel);p.wait_for_timeout(180);axe(p,panel,ctx)
      if p.locator('#snav-list').is_visible():
        p.evaluate("()=>switchPanel('p-home')");p.wait_for_timeout(150)
        chk('sidebar-inactive',measure(p,'#snav-list'),ctx);chk('sidebar-version',measure(p,'.sidebar-bottom .build-meta'),ctx)
        p.locator('#snav-list').hover();p.wait_for_timeout(120);axe(p,'sidebar-hover',ctx)
        p.locator('#snav-search').focus();p.wait_for_timeout(120);axe(p,'sidebar-focus',ctx)
        p.evaluate("()=>switchPanel('p-list')");p.wait_for_timeout(120);chk('sidebar-active',measure(p,'#snav-list'),ctx)
      p.evaluate("()=>switchPanel('p-home')");p.wait_for_timeout(120);chk('home-version',measure(p,'#home-scroll .build-meta'),ctx)
      p.evaluate("()=>openTextBar('data')");p.wait_for_timeout(250);axe(p,'settings-data',ctx)
      chk('export-text',measure(p,'#settings-export-btn'),ctx);chk('export-icon',measure(p,'#settings-export-btn .ti'),ctx)
      p.locator('#settings-export-btn').hover();p.wait_for_timeout(100);chk('export-hover-text',measure(p,'#settings-export-btn'),ctx);chk('export-hover-icon',measure(p,'#settings-export-btn .ti'),ctx);axe(p,'export-hover',ctx)
      p.evaluate("()=>closeTextBar(true)")
      p.evaluate("()=>{localStorage.setItem('lp_read','[1]');location.reload()}");ready(p);p.add_script_tag(path='node_modules/axe-core/axe.min.js')
      p.evaluate("()=>switchPanel('p-list')");p.wait_for_timeout(200);axe(p,'list-read-state',ctx);chk('read-title',measure(p,'.li-read'),ctx)
      p.evaluate("()=>switchPanel('p-explore')");p.wait_for_timeout(150)
      pid=p.locator('[data-path-id]').first.get_attribute('data-path-id')
      if pid:
        p.evaluate("(x)=>openPath(x)",pid);p.wait_for_timeout(150);n=int(p.locator('.path-letter-item').first.get_attribute('data-n'))
        p.evaluate("(n)=>{let a=JSON.parse(localStorage.getItem('lp_read')||'[]');if(!a.includes(n))a.push(n);localStorage.setItem('lp_read',JSON.stringify(a));location.reload()}",n)
        ready(p);p.add_script_tag(path='node_modules/axe-core/axe.min.js');p.evaluate("(x)=>{switchPanel('p-explore');openPath(x)}",pid);p.wait_for_timeout(200)
        axe(p,'path-done-state',ctx);chk('path-done-title',measure(p,'.path-letter-item.done .path-letter-title'),ctx);chk('path-done-meta',measure(p,'.path-letter-item.done .path-letter-meta'),ctx)
      p.evaluate("()=>{sessionStorage.clear();location.href=location.pathname+'?screen=list&empty=1'}");ready(p);p.add_script_tag(path='node_modules/axe-core/axe.min.js');p.wait_for_timeout(200);axe(p,'empty-reader',ctx)
      if p.locator('#reader-empty small').is_visible():chk('empty-reader-small',measure(p,'#reader-empty small'),ctx)
      c.close();b.close()

Path('LETTRES_V2_15_CONTRAST_QUALIFICATION_2026-10-05.json').write_text(json.dumps({'candidate':'B2_RUNTIME_TREE','checks':OUT,'failures':FAIL},ensure_ascii=False,indent=2),encoding='utf-8')
print('CONTRAST_CONTEXTS',len(MODES)*len(VPS));print('CONTRAST_FAILURES',len(FAIL))
if FAIL:
    print(json.dumps(FAIL[:20],ensure_ascii=False,indent=2));raise SystemExit(2)
print('CONTRAST_QUALIFICATION_PASS')
