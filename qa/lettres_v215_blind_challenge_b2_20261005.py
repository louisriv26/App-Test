from playwright.sync_api import sync_playwright, expect
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,difflib

PRE=Path('lettres-v2.14-b1-csp-repair')
CUR=Path('lettres-v2.15-b2-contrast-repair')
BASE='http://127.0.0.1:8120/lettres-v2.15-b2-contrast-repair/'
R=[]
def rec(n,ok,d=None):
    R.append({'name':n,'ok':bool(ok),'detail':d});print('CHALLENGE',n,'PASS' if ok else 'FAIL',repr(d),flush=True)
    if not ok:raise AssertionError(f'{n}: {d}')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

# Attempt to falsify mutation boundary.
af={p.relative_to(PRE).as_posix():sha(p) for p in PRE.rglob('*') if p.is_file()}
bf={p.relative_to(CUR).as_posix():sha(p) for p in CUR.rglob('*') if p.is_file()}
rec('same_member_set',set(af)==set(bf),{'pre_only':sorted(set(af)-set(bf)),'cur_only':sorted(set(bf)-set(af))})
rec('member_count_22',len(bf)==22,len(bf))
changed=sorted(k for k in af if af[k]!=bf[k])
rec('only_three_members_changed',changed==['index.html','manifest.json','sw.js'],changed)
rec('protected_corpus_exact',bf['corpus.json']=='362e763684e19d818722082b88348d912f06f434d8960e2a278db07b7f63f8ec',bf['corpus.json'])

# Structural CSP verification from actual final bytes.
class P(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=False);self.csp=None;self.scripts=[];self.styles=[];self._tag=None;self._buf=[]
    def handle_starttag(self,tag,attrs):
        d={k.lower():v for k,v in attrs}
        if tag.lower()=='meta' and (d.get('http-equiv') or '').lower()=='content-security-policy':self.csp=d.get('content')
        if tag.lower() in ('script','style') and not (tag.lower()=='script' and d.get('src')):
            self._tag=tag.lower();self._buf=[]
    def handle_data(self,data):
        if self._tag:self._buf.append(data)
    def handle_endtag(self,tag):
        if self._tag==tag.lower():
            s=''.join(self._buf)
            (self.scripts if self._tag=='script' else self.styles).append(s)
            self._tag=None;self._buf=[]
html=CUR.joinpath('index.html').read_text(encoding='utf-8')
p=P();p.feed(html);rec('csp_meta_present',bool(p.csp));rec('one_inline_script',len(p.scripts)==1,len(p.scripts));rec('two_inline_styles',len(p.styles)==2,len(p.styles))
import base64
tok=lambda s:"'sha256-"+base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()+"'"
dirs={}
for d in (p.csp or '').split(';'):
    z=d.strip().split()
    if z:dirs[z[0]]=z[1:]
main=tok(p.scripts[0]);styles=[tok(x) for x in p.styles]
rec('script_src_elem_exact',dirs.get('script-src-elem')==[main],dirs.get('script-src-elem'))
rec('script_src_authorizes_main',main in dirs.get('script-src',[]),dirs.get('script-src',[])[:4])
rec('style_src_elem_exact',dirs.get('style-src-elem')==styles,dirs.get('style-src-elem'))

# Attempt to find stale successor identity and over-broad palette mutation.
rec('no_v214_identity_token',not re.search(r'v?2\.14\b',html),[x for x in re.findall(r'.{0,40}v?2\.14.{0,40}',html)][:5])
rec('muted_variable_unchanged',re.findall(r'--muted\s*:[^;]+;',PRE.joinpath('index.html').read_text(encoding='utf-8'))==re.findall(r'--muted\s*:[^;]+;',html))
manifest=json.loads(CUR.joinpath('manifest.json').read_text(encoding='utf-8'))
rec('manifest_identity',(manifest.get('version'),manifest.get('build_revision'),manifest.get('release_id'))==('2.15','B2','lettres-v2.15-b2-contrast-repair'),manifest)
sw=CUR.joinpath('sw.js').read_text(encoding='utf-8')
rec('sw_identity','v2.14' not in sw and 'shell-v2.15-b2' in sw and 'corpus-v2.15-b2' in sw,None)

# Diff whitelist challenge: every non-CSP index change must map to the authorized semantic repair or version identity.
pre=PRE.joinpath('index.html').read_text(encoding='utf-8').splitlines()
cur=html.splitlines()
allowed=[
 'li-read','path-letter-item.done','export-btn.primary','rgba(255,255,255,.45)','rgba(255,255,255,.55)',
 'reader-empty small','v2.14','v2.15','2026-10-04','2026-10-05','APP_VERSION','shell-v2.14-b1','shell-v2.15-b2','corpus-v2.14-b1','corpus-v2.15-b2',
 "const APP_BUILD = 'B1';","const APP_BUILD = 'B2';",'Content-Security-Policy','sha256-'
]
bad=[]
for line in difflib.unified_diff(pre,cur,n=0):
    if line.startswith(('---','+++','@@')):continue
    if line.startswith(('+','-')) and not any(x in line for x in allowed):bad.append(line[:300])
rec('index_diff_whitelisted',not bad,bad[:20])

# Runtime falsification in Chromium and WebKit.
with sync_playwright() as pw:
  for engine,name in [(pw.chromium,'chromium'),(pw.webkit,'webkit')]:
    b=engine.launch(headless=True);c=b.new_context(viewport={'width':834,'height':1112},locale='fr-FR')
    p=c.new_page();errs=[];p.on('pageerror',lambda e:errs.append(str(e)))
    p.goto(BASE+'index.html?screen=search&q=confiance',wait_until='domcontentloaded',timeout=30000)
    p.locator('#loading').wait_for(state='detached',timeout=30000);expect(p.locator('#letter-list .letter-item')).to_have_count(136);p.wait_for_timeout(700)
    if p.locator('#help-overlay').is_visible():p.evaluate("()=>{try{closeHelp(true)}catch(e){}}")
    expect(p.locator('.build-meta').first).to_contain_text('v2.15')
    expect(p.locator('#search-input')).to_have_value('confiance')
    rec(name+':search_results',p.locator('#search-results [data-action="search-result"]').count()>0,p.locator('#search-results').inner_text()[:200])
    p.goto(BASE+'index.html?letter=LP.LETTER.136&dp=LP.LETTER.136.DP999',wait_until='domcontentloaded');p.locator('#loading').wait_for(state='detached',timeout=30000)
    p.wait_for_timeout(500)
    pos=p.locator('#wr-pos' if p.locator('html').get_attribute('data-layout')=='wide' else '#pr-pos')
    expect(pos).to_have_text('136 / 136')
    rec(name+':invalid_dp_fallback',True,p.url)
    rec(name+':no_pageerrors',not errs,errs)
    c.close();b.close()

print('BLIND_CHALLENGE_PASS',len(R))
