from pathlib import Path
import zipfile,hashlib,json,re,shutil,csv,subprocess,time,urllib.request,websocket,itertools
Z=Path('/mnt/data/L24H_v10185_GITHUB_DEPLOY_USER_FEEDBACK_CORRECTED_HARDENED_R4_AUDIT_RECONCILED.zip')
O=Path('/mnt/data/l24h_v10185_r4_audit_reconciliation_outputs/independent_reopen_audit');E=O/'independent_extract'
EXPECTED_HTML='c43ff8934c12b24668c9c0cf55ebb12a9eb6ecd8ed265e68e4d78aaf0fd86050'
rows=[]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(n,c,p):rows.append({'check':n,'status':'PASS' if c else 'FAIL','proof':p});assert c,(n,p)
def jc(t,n):
    x='const '+n+' = ';i=t.index(x)+len(x);return json.JSONDecoder().raw_decode(t[i:])[0]
def para(c,pid):
    for h in c['hours']:
        for p in h.get('paragraphs',[]):
            if p['id']==pid:return p['t']

def chrome_check(t):
    prof='/tmp/l24h-r4-independent';shutil.rmtree(prof,ignore_errors=True);pr=subprocess.Popen(['/usr/bin/chromium','--headless','--no-sandbox','--disable-gpu','--remote-debugging-port=9281','--remote-allow-origins=*',f'--user-data-dir={prof}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);out=[]
    try:
        li=None
        for _ in range(60):
            try:
                li=json.load(urllib.request.urlopen('http://127.0.0.1:9281/json/list',timeout=1))
                if li:break
            except:time.sleep(.1)
        pg=next(q for q in li if q['type']=='page');w=websocket.create_connection(pg['webSocketDebuggerUrl'],timeout=10,origin='http://127.0.0.1:9281');ctr=itertools.count(1)
        def C(m,p=None):
            i=next(ctr);w.send(json.dumps({'id':i,'method':m,'params':p or {}}))
            while 1:
                z=json.loads(w.recv())
                if z.get('id')==i:return z
        def V(x):
            z=C('Runtime.evaluate',{'expression':x,'returnByValue':True,'awaitPromise':True})['result']
            if 'exceptionDetails'in z:raise Exception(z['exceptionDetails'])
            return z['result'].get('value')
        C('Page.enable');f=C('Page.getFrameTree')['result']['frameTree']['frame']['id'];C('Page.setDocumentContent',{'frameId':f,'html':t});time.sleep(.35)
        V("window.__m={lp24_r41_text_anchor_reset:R41_TEXT_ANCHOR_RESET_VERSION};storageRead=k=>({ok:true,value:Object.prototype.hasOwnProperty.call(__m,k)?__m[k]:null,error:null});storageWrite=(k,v)=>(__m[k]=String(v),{ok:true,error:null});storageRemove=k=>(delete __m[k],{ok:true,error:null});")
        id='PASSION24.TEXT.HOW_TO_PRACTICE'
        tests=[('version',V("APP_VERSION==='v101.85'&&STORAGE_SCHEMA_VERSION===8&&PERSONAL_SNAPSHOT_VERSION===5")),('bad colour',V(f"Object.keys(sanitizeLibraryMarksStore({{'{id}':{{color:'orange'}}}})).length===0")),('proto safe',V("(()=>{delete Object.prototype.x;const q=JSON.parse('{\"__proto__\":{\"x\":1}}');return Object.keys(sanitizeLibraryMarksStore(q)).length===0&&!Object.prototype.x})()"))]
        V(f"openLibraryText('{id}',false);openLibraryMarkerPicker('{id}',document.getElementById('libraryTitleMarkBtn'));applyLibraryMarkerColor('green')");tests.append(('mark',V(f"state.libraryMarks['{id}'].color==='green'")))
        V("showSearchView(false);performSearch('humilié par ton silence')");tests.append(('search H15',V("document.getElementById('homeSearchResults').innerHTML.includes('PASSION24.HOUR.15.P014')")))
        V('openHour(17,false)');tests.append(('H17',V("document.getElementById('PASSION24.HOUR.17.P027').innerText.includes('contiennent, et constitue-Moi')")))
        V('openHour(15,false)');tests.append(('H15',V("document.getElementById('PASSION24.HOUR.15.P014').innerText.endsWith('silence,')&&document.getElementById('PASSION24.HOUR.15.P015').innerText.startsWith('il proclame')")))
        out=[{'name':n,'ok':bool(v)} for n,v in tests];w.close()
    finally:
        pr.terminate()
        try:pr.wait(timeout=5)
        except:pr.kill()
    return out
status='FAIL';error=None
try:
    shutil.rmtree(O,ignore_errors=True);E.mkdir(parents=True)
    u=subprocess.run(['unzip','-tqq',str(Z)],capture_output=True,text=True);add('CLI archive integrity',u.returncode==0,(u.stdout+u.stderr).strip() or 'PASS')
    with zipfile.ZipFile(Z) as z:
        ns=z.namelist();add('unique safe names',len(ns)==len(set(ns)) and not any(n.startswith('/') or '..' in Path(n).parts for n in ns),len(ns));z.extractall(E)
    f={p.relative_to(E).as_posix():p for p in E.rglob('*') if p.is_file()};add('extracted count',len(f)==len(ns),len(f));add('no nested ZIP',not [n for n in f if n.lower().endswith('.zip')],'none')
    pm=json.loads(f['metadata/package_manifest.json'].read_text());pmd={q['path']:q for q in pm['files']};add('package manifest coverage',set(pmd)|{'metadata/package_manifest.json'}==set(f),len(pmd));add('package manifest exact',not [n for n,q in pmd.items() if digest(f[n])!=q['sha256'] or f[n].stat().st_size!=q['bytes']],'exact')
    hm=json.loads(f['metadata/hash_manifest.json'].read_text());hmd={q['path']:q for q in hm['files']};add('hash manifest coverage',set(hmd)==set(f)-{'metadata/hash_manifest.json','metadata/package_manifest.json'},len(hmd));add('hash manifest exact',not [n for n,q in hmd.items() if digest(f[n])!=q['sha256'] or f[n].stat().st_size!=q['bytes']],'exact')
    b=f['index.html'].read_bytes();text=b.decode();add('runtime twins frozen',hashlib.sha256(b).hexdigest()==EXPECTED_HTML and b==f['luisa_24_heures.html'].read_bytes(),hashlib.sha256(b).hexdigest())
    ids=(re.search(r"const APP_VERSION = '([^']+)'",text).group(1),int(re.search(r'const STORAGE_SCHEMA_VERSION=(\d+)',text).group(1)),int(re.search(r'const PERSONAL_SNAPSHOT_VERSION = (\d+)',text).group(1)));add('identity tuple',ids==('v101.85',8,5),ids)
    # independent provenance / false-independence detection
    ap=json.loads(f['metadata/auditor_provenance.json'].read_text());aud='scripts/'+ap['independent_four_pass_auditor'];ah=digest(f[aud]);four=f['audit/independent_four_pass_audit.md'].read_text();add('four-pass generator bound',ah==ap['independent_four_pass_auditor_sha256'] and ah in four and 'FOUR_PASS_PREPACKAGE_GATE = PASS' in four,ah)
    build=f['scripts/l24h_v10185_r4_audit_reconciliation_build.py'].read_text();add('builder does not author independent report',"independent_four_pass_audit.md').write_text" not in build,'separate generator')
    # syntax/data/speech
    js='\n'.join(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',text,re.S|re.I));tmp=O/'independent_runtime.js';tmp.write_text(js);n=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True);add('independent JS syntax',n.returncode==0,(n.stdout+n.stderr).strip() or 'PASS')
    c=jc(text,'CORPUS');lib=jc(text,'TEXT_LIBRARY');sp=jc(text,'SPEECH_DATA');tg={}
    for h in c['hours']:
        for k in ('paragraphs','reflections'):
            for p in h.get(k,[]) or []:tg[p['id']]=p['t']
        for sub in h.get('subsections',[]) or []:
            for p in sub.get('paragraphs',[]):tg[p['id']]=p['t']
    for prr in c.get('prayers',[]):
        for p in prr.get('paragraphs',[]):tg[p['id']]=p['t']
    for sec in c.get('sections',[]):
        for p in sec.get('paragraphs',[]):tg[p['id']]=p['t']
    for it in lib:
        if it.get('type')=='library_group':continue
        for i,x in enumerate(it.get('body',[]) or []):tg[f"{it['id']}.BODY.P{i+1:03d}"]=str(x)
        for i,x in enumerate(it.get('practice_options',[]) or []):tg[f"{it['id']}.PRACTICE.P{i+1:03d}"]=str(x)
    er=[];seg=0
    for pid,a in sp.items():
        if pid not in tg:er.append(('missing',pid));continue
        last=-1
        for q in sorted(a,key=lambda z:(z['start'],z['end'])):
            seg+=1;s0,e0=q['start'],q['end'];
            if not 0<=s0<e0<=len(tg[pid]):er.append(('bounds',pid,s0,e0))
            if s0<last:er.append(('overlap',pid))
            last=max(last,e0)
    add('speech render-target validation',not er,{'targets':len(tg),'segments':seg,'errors':er[:3]})
    br=jc(text,'SPEECH_END_VISUAL_BREAKS');bad=[]
    for pid,ps in br.items():
        for i in ps:
            q=tg.get(pid,'');
            if not(0<i<len(q)) or (q[i-1].isalpha() and q[i].isalpha()):bad.append((pid,i))
    add('visual breaks safe',not bad,bad);add('H15 exact',para(c,'PASSION24.HOUR.15.P014').endswith('silence,') and para(c,'PASSION24.HOUR.15.P015').startswith('il proclame'),'approved');add('H17 exact',br.get('PASSION24.HOUR.17.P027')==[155] and 'contiennent, et constitue-Moi' in para(c,'PASSION24.HOUR.17.P027'),br.get('PASSION24.HOUR.17.P027'))
    # reports
    rm=list(csv.DictReader(f['reports/full_regression_matrix.csv'].open()));ct={x:sum(r['status']==x for r in rm) for x in ['PASS','NOT_TESTED','FAIL']};add('regression counts',ct['FAIL']==0 and ct['NOT_TESTED']==11 and ct['PASS']>0,{'rows':len(rm),**ct});rb=list(csv.DictReader(f['reports/runtime_behaviour_matrix.csv'].open()));add('runtime matrix all PASS',rb and all(r['status']=='PASS' for r in rb),len(rb));cl=list(csv.DictReader(f['reports/pass3_claim_ledger.csv'].open()));add('claim ledger all supported',cl and not [r for r in cl if r['classification']=='FAIL'],len(cl));add('stale scan no unjustified','|UNJUSTIFIED|' not in f['reports/stale_reference_scan.txt'].read_text(),'0 unjustified');add('pass4 explicit clean',all(x in f['reports/pass4_contradiction_stale_scan.txt'].read_text() for x in ['status=PASS','unjustified=0','active_contradictions=0']),'clean')
    lk=json.loads(f['metadata/final_decision_lock.json'].read_text());add('decision lock',lk['final_status']=='LIMITED_PASS' and not lk['public_release_ready'] and len(lk['external_gates_not_tested'])==11,lk['final_status'])
    cr=chrome_check(text);add('independent Chromium',all(x['ok'] for x in cr),cr)
    status='PASS'
except Exception as e:error=repr(e)
summary={'audit':'INDEPENDENT_REOPEN_GATE','status':status,'zip_sha256':digest(Z) if Z.exists() else None,'runtime_html_sha256':digest(E/'index.html') if (E/'index.html').exists() else None,'checks':rows}
if error:summary['error']=error
O.mkdir(parents=True,exist_ok=True);(O/'V10185_R4_INDEPENDENT_REOPENED_ZIP_AUDIT.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
md=['# v101.85 R4 — Independent reopened-ZIP audit','',f'**INDEPENDENT_REOPEN_GATE = {status}**','',f'- ZIP SHA-256: `{summary["zip_sha256"]}`',f'- Runtime HTML SHA-256: `{summary["runtime_html_sha256"]}`','','| Check | Status | Proof |','|---|---|---|']
for r in rows:md.append('| '+r['check'].replace('|','¦')+' | '+r['status']+' | '+str(r['proof']).replace('|','¦').replace('\n',' ')[:800]+' |')
if error:md+=['','## Blocking failure','',f'`{error}`']
else:md+=['','## Decision','','A separately implemented reopened-ZIP auditor independently reproduces PASS on R4. Runtime HTML is unchanged from R3; 11 external gates remain NOT_TESTED, so overall status remains LIMITED_PASS.']
(O/'V10185_R4_INDEPENDENT_REOPENED_ZIP_AUDIT.md').write_text('\n'.join(md)+'\n');print(json.dumps(summary,ensure_ascii=False,indent=2));raise SystemExit(0 if status=='PASS' else 1)
