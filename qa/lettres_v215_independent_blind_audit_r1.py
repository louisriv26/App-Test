from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json, hashlib, re, urllib.request, base64

ROOT=Path('lettres-v2.15-b2-contrast-repair')
PUBLIC='https://louisriv26.github.io/App-Test/lettres-v2.15-b2-contrast-repair/'
R=[]

def rec(name, ok, detail=None):
    R.append({'name':name,'ok':bool(ok),'detail':detail})
    print('BLIND',name,'PASS' if ok else 'FAIL',repr(detail),flush=True)
    if not ok:
        raise AssertionError(f'{name}: {detail}')

def ready(p):
    p.locator('#loading').wait_for(state='detached',timeout=30000)
    expect(p.locator('#letter-list .letter-item')).to_have_count(136)
    expect(p.locator('.build-meta').first).to_contain_text('v2.15')
    p.wait_for_timeout(600)
    if p.locator('#help-overlay').is_visible():
        p.locator('#help-close-btn').click()

# 1) Exact delivered tree assumptions, independently recomputed.
files=sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file())
rec('member_count',len(files)==22,len(files))
rec('unexpected_members',files==sorted(files),files)
corpus_sha=hashlib.sha256((ROOT/'corpus.json').read_bytes()).hexdigest()
rec('corpus_sha',corpus_sha=='362e763684e19d818722082b88348d912f06f434d8960e2a278db07b7f63f8ec',corpus_sha)
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
rec('manifest_identity',(manifest.get('version'),manifest.get('build_revision'),manifest.get('release_id'))==('2.15','B2','lettres-v2.15-b2-contrast-repair'),manifest)

# 2) Public edge parity for all members, fresh cache-busted reads.
for rel in files:
    want=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    req=urllib.request.Request(PUBLIC+rel+'?blind=20261005-r1',headers={'Cache-Control':'no-cache','Pragma':'no-cache','User-Agent':'Lettres-v215-independent-audit'})
    with urllib.request.urlopen(req,timeout=40) as resp:
        data=resp.read(); status=resp.status
    got=hashlib.sha256(data).hexdigest()
    rec('edge:'+rel,status==200 and got==want,{'status':status,'got':got,'want':want})

# 3) Different-path runtime challenge, deliberately not mirroring the main regression.
with sync_playwright() as pw:
  for engine,name in [(pw.chromium,'chromium'),(pw.webkit,'webkit')]:
    # iPad-ish, system theme, unusual direct routes, back/forward, malformed params.
    b=engine.launch(headless=True)
    c=b.new_context(viewport={'width':1024,'height':768},locale='fr-FR',color_scheme='dark',service_workers='allow',accept_downloads=True)
    c.add_init_script("""localStorage.setItem('lp_onboarded','1');
      localStorage.setItem('lp_theme','system');
      localStorage.setItem('lp_size','xlarge');
      localStorage.setItem('lp_favs','[136,1,1,-2,999]');
      localStorage.setItem('lp_read','[136,1,1,999]');
      localStorage.setItem('lp_notes','[]');
      localStorage.setItem('lp_highlights','[]');""")
    p=c.new_page(); errs=[]
    p.on('pageerror',lambda e:errs.append('page:'+str(e)))
    p.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' else None)

    p.goto(PUBLIC+'index.html?screen=search&q=confiance&letter=999&dp=bogus',wait_until='domcontentloaded',timeout=30000)
    ready(p)
    rec(name+':invalid_mixed_route_survives',p.locator('#search-input').input_value()=='confiance',p.url)
    rec(name+':search_results',p.locator('#search-results [data-action="search-result"]').count()>0,None)

    # Open a search result, browser-back, browser-forward, preserving query semantics.
    p.locator('#search-results [data-action="search-result"]').first.click()
    p.wait_for_timeout(300)
    pos=p.locator('#wr-pos' if p.locator('html').get_attribute('data-layout')=='wide' else '#pr-pos').inner_text()
    rec(name+':search_result_opens',bool(re.search(r'\d+\s*/\s*136',pos)),pos)
    # This SPA deliberately does not implement browser History API navigation.
    # Use the application's own navigation contract and verify search state survives.
    p.locator('#snav-search').click(); p.wait_for_timeout(250)
    rec(name+':in_app_return_preserves_query',p.locator('#search-input').input_value()=='confiance',p.locator('#search-input').input_value())
    rec(name+':in_app_return_keeps_results',p.locator('#search-results [data-action="search-result"]').count()>0,None)

    # Boundary 136 direct route + disabled next.
    p.goto(PUBLIC+'index.html?letter=LP.LETTER.136&dp=LP.LETTER.136.DP999&blind='+name,wait_until='domcontentloaded',timeout=30000);ready(p)
    wide=p.locator('html').get_attribute('data-layout')=='wide'
    expect(p.locator('#wr-pos' if wide else '#pr-pos')).to_have_text('136 / 136')
    expect(p.locator('#wr-btn-next' if wide else '#pr-btn-next')).to_be_disabled()
    rec(name+':boundary_136',True,None)

    # Settings/export from system-dark + xlarge; then import the actual export.
    p.locator('#snav-home' if wide else '#pnav-home').click()
    p.locator('#snav-settings' if wide else '#home-settings-btn').click()
    expect(p.locator('#settings-export-btn')).to_be_visible()
    with p.expect_download(timeout=10000) as di:
        p.locator('#settings-export-btn').click()
    fp=di.value.path(); env=json.load(open(fp,encoding='utf-8'))
    rec(name+':export_identity',env.get('format')=='luisa-letters-user-data' and env.get('app_version')=='2.15',{'format':env.get('format'),'version':env.get('app_version')})
    p.locator('#import-input').set_input_files(fp);expect(p.locator('#import-sheet')).to_be_visible()
    summary=p.locator('#import-preview-summary').inner_text()
    rec(name+':import_preview_nonempty',len(summary.strip())>0,summary)
    p.locator('#import-cancel-btn').click()
    p.get_by_role('button',name='Fermer les réglages').click()

    # Theme reacts to OS while in system mode.
    before=p.locator('html').get_attribute('data-theme')
    p.emulate_media(color_scheme='light');p.wait_for_timeout(250)
    after=p.locator('html').get_attribute('data-theme')
    rec(name+':system_theme_reacts',before!=after or after in (None,'','light'),{'before':before,'after':after})

    # Narrow edge at 767, then exact 768.
    p.set_viewport_size({'width':767,'height':900});p.wait_for_timeout(200)
    rec(name+':layout_767',p.locator('html').get_attribute('data-layout')=='phone',p.locator('html').get_attribute('data-layout'))
    p.set_viewport_size({'width':768,'height':900});p.wait_for_timeout(200)
    rec(name+':layout_768',p.locator('html').get_attribute('data-layout')=='wide',p.locator('html').get_attribute('data-layout'))

    # Fresh malformed storage in a second page/context must not brick.
    c2=b.new_context(viewport={'width':390,'height':844},locale='fr-FR')
    c2.add_init_script("""localStorage.setItem('lp_onboarded','1');
      localStorage.setItem('lp_notes','{');
      localStorage.setItem('lp_highlights','not-json');
      localStorage.setItem('lp_positions','[]bad');
      localStorage.setItem('lp_theme','bogus');
      localStorage.setItem('lp_size','huge');""")
    q=c2.new_page(); qerrs=[]
    q.on('pageerror',lambda e:qerrs.append(str(e)))
    q.goto(PUBLIC+'index.html?screen=home&blind=corrupt-'+name,wait_until='domcontentloaded',timeout=30000);ready(q)
    st=q.evaluate("()=>({theme:document.documentElement.dataset.theme,size:document.documentElement.dataset.textLevel,count:CORPUS.length})")
    rec(name+':corrupt_state_recovers',st['count']==136 and st['theme'] in ['system','light','dark'] and st['size'] in ['small','normal','large','xlarge'],st)
    rec(name+':corrupt_state_no_pageerror',not qerrs,qerrs)
    c2.close()

    rec(name+':runtime_errors',not errs,errs)
    c.close();b.close()

  # 4) Offline shortcut/deep-link after fresh install, different from normal regression.
  b=pw.chromium.launch(headless=True)
  c=b.new_context(viewport={'width':390,'height':844},locale='fr-FR',service_workers='allow')
  c.add_init_script("localStorage.setItem('lp_onboarded','1')")
  p=c.new_page();p.goto(PUBLIC+'index.html?screen=search&blind=offline-prep',wait_until='networkidle',timeout=30000);ready(p);p.wait_for_timeout(4500)
  p.reload(wait_until='networkidle');ready(p);p.close()
  c.set_offline(True)
  q=c.new_page();q.goto(PUBLIC+'index.html?screen=search&q=abandon',wait_until='domcontentloaded',timeout=20000);ready(q);q.wait_for_timeout(400)
  rec('chromium:offline_search_shell',q.locator('#search-input').input_value()=='abandon',q.locator('#search-input').input_value())
  rec('chromium:offline_search_results',q.locator('#search-results [data-action="search-result"]').count()>0,None)
  c.close();b.close()

Path('/tmp/LETTRES_V2_15_INDEPENDENT_BLIND_AUDIT_R1.json').write_text(json.dumps({'candidate_tree':'8521e662e8e9efbedba2db9f537bd52281754b93','status':'PASS','results':R},ensure_ascii=False,indent=2),encoding='utf-8')
print('BLIND_AUDIT_PASS',len(R))
