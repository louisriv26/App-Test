from __future__ import annotations
from pathlib import Path
import csv,hashlib,json,re,shutil,subprocess,zipfile,time,urllib.request,websocket,itertools
ZIP=Path('/mnt/data/L24H_v10185_GITHUB_DEPLOY_USER_FEEDBACK_CORRECTED_HARDENED_R4_AUDIT_RECONCILED.zip')
OUT=Path('/mnt/data/l24h_v10185_r4_audit_reconciliation_outputs/final_reopen_audit');X=OUT/'fresh_extract'
RUNTIME_SHA='c43ff8934c12b24668c9c0cf55ebb12a9eb6ecd8ed265e68e4d78aaf0fd86050';R3_SHA='98852b3e347d0754fbf48c42c356e88bcb41301527f9a43308f73f00e7caf522'
checks=[]
def h(b):return hashlib.sha256(b).hexdigest()
def hf(p):return h(Path(p).read_bytes())
def gate(name,ok,evidence):
    checks.append({'gate':name,'status':'PASS' if ok else 'FAIL','evidence':evidence})
    if not ok:raise RuntimeError(f'{name}: {evidence}')
def jconst(s,n):
    m='const '+n+' = ';i=s.index(m)+len(m);return json.JSONDecoder().raw_decode(s[i:])[0]
def targets(c,l):
    o={}
    for hh in c['hours']:
        for k in ('paragraphs','reflections'):
            for p in hh.get(k,[]) or []:o[p['id']]=p['t']
        for sub in hh.get('subsections',[]) or []:
            for p in sub.get('paragraphs',[]) or []:o[p['id']]=p['t']
    for pr in c.get('prayers',[]):
        for p in pr.get('paragraphs',[]):o[p['id']]=p['t']
    for sec in c.get('sections',[]):
        for p in sec.get('paragraphs',[]):o[p['id']]=p['t']
    for item in l:
        if item.get('type')=='library_group':continue
        for i,t in enumerate(item.get('body',[]) or []):o[f"{item['id']}.BODY.P{i+1:03d}"]=str(t)
        for i,t in enumerate(item.get('practice_options',[]) or []):o[f"{item['id']}.PRACTICE.P{i+1:03d}"]=str(t)
    return o
def ptext(c,pid):
    for hh in c['hours']:
        for p in hh.get('paragraphs',[]):
            if p['id']==pid:return p['t']
    return None

def browser(html):
    profile='/tmp/l24h-r4-primary';shutil.rmtree(profile,ignore_errors=True);p=subprocess.Popen(['/usr/bin/chromium','--headless','--no-sandbox','--disable-gpu','--remote-debugging-port=9271','--remote-allow-origins=*',f'--user-data-dir={profile}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);out=[]
    try:
        ts=None
        for _ in range(80):
            try:
                with urllib.request.urlopen('http://127.0.0.1:9271/json/list',timeout=1) as r:ts=json.load(r)
                if ts:break
            except:time.sleep(.1)
        pg=next(x for x in ts if x.get('type')=='page');ws=websocket.create_connection(pg['webSocketDebuggerUrl'],timeout=10,origin='http://127.0.0.1:9271');seq=itertools.count(1)
        def call(m,pa=None):
            i=next(seq);ws.send(json.dumps({'id':i,'method':m,'params':pa or {}}))
            while 1:
                x=json.loads(ws.recv())
                if x.get('id')==i:return x
        def e(ex):
            r=call('Runtime.evaluate',{'expression':ex,'returnByValue':True,'awaitPromise':True})['result']
            if 'exceptionDetails'in r:raise RuntimeError(r['exceptionDetails'])
            return r['result'].get('value')
        def t(n,ok,proof):out.append({'test':n,'status':'PASS' if ok else 'FAIL','evidence':proof})
        call('Page.enable');fr=call('Page.getFrameTree')['result']['frameTree']['frame']['id'];call('Page.setDocumentContent',{'frameId':fr,'html':html});time.sleep(.4)
        e("window.__s={lp24_r41_text_anchor_reset:R41_TEXT_ANCHOR_RESET_VERSION};storageRead=k=>({ok:true,value:Object.prototype.hasOwnProperty.call(__s,k)?__s[k]:null,error:null});storageWrite=(k,v)=>(__s[k]=String(v),{ok:true,error:null});storageRemove=k=>(delete __s[k],{ok:true,error:null});")
        item='PASSION24.TEXT.HOW_TO_PRACTICE';t('identity',e("APP_VERSION==='v101.85'&&STORAGE_SCHEMA_VERSION===8&&PERSONAL_SNAPSHOT_VERSION===5"),e('APP_VERSION'))
        pp=json.loads(e("(()=>{delete Object.prototype.polluted;const q=JSON.parse('{\"__proto__\":{\"polluted\":1}}');const c=sanitizeLibraryMarksStore(q);return JSON.stringify({keys:Object.keys(c),polluted:!!Object.prototype.polluted})})()"));t('prototype pollution rejection',pp['keys']==[] and not pp['polluted'],pp)
        e(f"openLibraryText('{item}',false);openLibraryMarkerPicker('{item}',document.getElementById('libraryTitleMarkBtn'));applyLibraryMarkerColor('blue')");t('title mark stored/rendered',e(f"state.libraryMarks['{item}'].color")=='blue' and 'library-title-mark-blue' in e("document.getElementById('libraryReaderTitle').className"),'blue')
        e('showEspaceView(false)');t('Mon Espace marked reading','Lectures marquées' in e("document.querySelector('.content').innerText"),'Lectures marquées')
        exp=json.loads(e('JSON.stringify(buildPersonalDataExport())'));t('export carries mark',exp.get('libraryMarks',{}).get(item,{}).get('color')=='blue',exp.get('libraryMarks'))
        old=json.loads(e("(()=>{const x=buildPersonalDataExport();x.schema_version=7;x.app_version='v101.84';delete x.libraryMarks;x.readHours=[4];return JSON.stringify(validatePersonalDataImport(x))})()"));t('schema7 migration',old.get('libraryMarks')=={} and old.get('readHours')==[4],{'marks':old.get('libraryMarks'),'read':old.get('readHours')})
        e("showSearchView(false);performSearch('humilié par ton silence')");st=e("document.getElementById('homeSearchResults').innerText");sh=e("document.getElementById('homeSearchResults').innerHTML");t('H15 search target','silence' in st and 'PASSION24.HOUR.15.P014' in sh,st[:180])
        e('openHour(15,false)');a=e("document.getElementById('PASSION24.HOUR.15.P014').innerText");b=e("document.getElementById('PASSION24.HOUR.15.P015').innerText");t('H15 render',a.endswith('silence,') and b.startswith('il proclame'),a+' / '+b[:50])
        e('openHour(17,false)');z=e("document.getElementById('PASSION24.HOUR.17.P027').innerText");cnt=e("document.getElementById('PASSION24.HOUR.17.P027').querySelectorAll('.speech-end-visual-break').length");t('H17 render','contiennent, et constitue-Moi' in z and 'e\nt constitue-Moi' not in z and cnt==1,{'breaks':cnt,'text':z[:180]})
        ws.close()
    finally:
        p.terminate()
        try:p.wait(timeout=5)
        except:p.kill()
    return out

status='FAIL';err=None
try:
    shutil.rmtree(OUT,ignore_errors=True);X.mkdir(parents=True)
    gate('ZIP exists',ZIP.exists(),str(ZIP));cp=subprocess.run(['unzip','-tqq',str(ZIP)],capture_output=True,text=True);gate('archive integrity',cp.returncode==0,(cp.stdout+cp.stderr).strip() or 'unzip -tqq PASS')
    with zipfile.ZipFile(ZIP) as z:
        names=z.namelist();gate('duplicate member names',len(names)==len(set(names)),{'members':len(names),'unique':len(set(names))});gate('path safety',not [n for n in names if n.startswith('/') or '..' in Path(n).parts],[]);z.extractall(X)
    fs={p.relative_to(X).as_posix():p for p in X.rglob('*') if p.is_file()};gate('member/file count',len(fs)==len(names),len(fs))
    required=['index.html','luisa_24_heures.html','metadata/hash_manifest.json','metadata/package_manifest.json','metadata/final_decision_lock.json','metadata/auditor_provenance.json','audit/independent_four_pass_audit.md','reports/full_regression_matrix.csv','reports/runtime_behaviour_matrix.csv','reports/pass3_claim_ledger.csv','reports/pass4_contradiction_stale_scan.txt','reports/stale_reference_scan.txt','scripts/l24h_v10185_r4_audit_reconciliation_build.py','scripts/l24h_v10185_r4_independent_four_pass_audit.py','scripts/l24h_v10185_r4_final_reopen_audit.py','scripts/l24h_v10185_r4_independent_reopen_audit.py']
    gate('required evidence universe',not [x for x in required if x not in fs],[x for x in required if x not in fs])
    pm=json.loads(fs['metadata/package_manifest.json'].read_text('utf-8'));pmr={r['path']:(r['sha256'],r['bytes']) for r in pm['files']};gate('package manifest set',set(pmr)|{'metadata/package_manifest.json'}==set(fs),{'manifest':len(pmr),'actual':len(fs)});gate('package manifest values',not [n for n,(d,s) in pmr.items() if hf(fs[n])!=d or fs[n].stat().st_size!=s],[])
    hm=json.loads(fs['metadata/hash_manifest.json'].read_text('utf-8'));hmr={r['path']:(r['sha256'],r['bytes']) for r in hm['files']};scope=set(fs)-{'metadata/hash_manifest.json','metadata/package_manifest.json'};gate('hash manifest set',set(hmr)==scope,{'manifest':len(hmr),'scope':len(scope)});gate('hash manifest values',not [n for n,(d,s) in hmr.items() if hf(fs[n])!=d or fs[n].stat().st_size!=s],[])
    idx=fs['index.html'].read_bytes();gate('runtime twins and frozen hash',idx==fs['luisa_24_heures.html'].read_bytes() and h(idx)==RUNTIME_SHA,h(idx));s=idx.decode('utf-8')
    # independent auditor provenance: report cannot be build-generated.
    ap=json.loads(fs['metadata/auditor_provenance.json'].read_text('utf-8'));four=fs['audit/independent_four_pass_audit.md'].read_text('utf-8');ia='scripts/'+ap['independent_four_pass_auditor'];actual=hf(fs[ia]);gate('four-pass auditor hash provenance',actual==ap['independent_four_pass_auditor_sha256'] and f'Generator SHA-256: `{actual}`' in four,{'declared':ap['independent_four_pass_auditor_sha256'],'actual':actual})
    buildtxt=fs['scripts/l24h_v10185_r4_audit_reconciliation_build.py'].read_text('utf-8');gate('build script does not generate independent four-pass report',"independent_four_pass_audit.md').write_text" not in buildtxt and 'independent_four_pass_audit.md\").write_text' not in buildtxt,'no report writer in build')
    gate('four-pass prepackage result','**FOUR_PASS_PREPACKAGE_GATE = PASS**' in four,'PASS')
    # runtime/package data
    scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S|re.I);tmp=OUT/'runtime.js';tmp.write_text('\n;\n'.join(scripts),'utf-8');cp=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True);gate('runtime JS syntax',cp.returncode==0,(cp.stdout+cp.stderr).strip() or 'PASS');cp=subprocess.run(['node','--check',str(fs['sw.js'])],capture_output=True,text=True);gate('SW syntax',cp.returncode==0,(cp.stdout+cp.stderr).strip() or 'PASS')
    c=jconst(s,'CORPUS');l=jconst(s,'TEXT_LIBRARY');sp=jconst(s,'SPEECH_DATA');tg=targets(c,l);e=[];seg=0
    for pid,arr in sp.items():
        if pid not in tg:e.append(('missing',pid));continue
        last=-1
        for q in sorted(arr,key=lambda x:(x['start'],x['end'])):
            seg+=1;a=int(q['start']);b=int(q['end']);
            if not 0<=a<b<=len(tg[pid]):e.append(('bounds',pid,a,b))
            if a<last:e.append(('overlap',pid,a,last))
            last=max(last,b)
    gate('speech actual render targets/offsets',not e,{'targets':len(tg),'speech_targets':len(sp),'segments':seg,'errors':e[:3]})
    br=jconst(s,'SPEECH_END_VISUAL_BREAKS');bad=[]
    for pid,ps in br.items():
        for p in ps:
            t=tg.get(pid,'');p=int(p)
            if not 0<p<len(t):bad.append(('bounds',pid,p))
            elif t[p-1].isalpha() and t[p].isalpha():bad.append(('midword',pid,p))
    gate('visual-break validity',not bad,bad);gate('H15 exact',ptext(c,'PASSION24.HOUR.15.P014').endswith('ton silence,') and ptext(c,'PASSION24.HOUR.15.P015').startswith('il proclame devant tous que Tu es un fou.'),'approved comma/lowercase');gate('H17 text/break', 'contiennent, et constitue-Moi' in ptext(c,'PASSION24.HOUR.17.P027') and br.get('PASSION24.HOUR.17.P027')==[155],br.get('PASSION24.HOUR.17.P027'))
    # current report truth + line-by-line coverage
    reg=list(csv.DictReader(fs['reports/full_regression_matrix.csv'].open(encoding='utf-8')));counts={k:sum(r['status']==k for r in reg) for k in ['PASS','NOT_TESTED','FAIL']};gate('regression status truth',counts['FAIL']==0 and counts['NOT_TESTED']==11 and counts['PASS']>0,{'rows':len(reg),**counts});runtime=list(csv.DictReader(fs['reports/runtime_behaviour_matrix.csv'].open(encoding='utf-8')));gate('runtime matrix truth',runtime and all(r['status']=='PASS' for r in runtime),{'rows':len(runtime),'fail':sum(r['status']!='PASS' for r in runtime)})
    ledger=list(csv.DictReader(fs['reports/pass3_claim_ledger.csv'].open(encoding='utf-8')));gate('Pass3 ledger no unsupported lines',ledger and not [r for r in ledger if r['classification']=='FAIL'],{'rows':len(ledger),'verified':sum(r['classification']=='VERIFIED' for r in ledger),'nonclaim':sum(r['classification']=='NONCLAIM' for r in ledger)})
    active=['audit/independent_four_pass_audit.md','reports/no_regression_fix_ledger.csv','reports/full_regression_matrix.csv','reports/runtime_behaviour_matrix.csv','reports/root_deploy_consistency_report.md','reports/nested_zip_consistency_report.md','reports/report_claims_vs_evidence_audit.md','reports/pass4_contradiction_stale_scan.txt','reports/stale_reference_scan.txt']
    expected={(rel,n) for rel in active for n,_ in enumerate(fs[rel].read_text('utf-8').splitlines(),1)};actual={(r['file'],int(r['line'])) for r in ledger};gate('Pass3 line-by-line coverage',actual==expected,{'expected':len(expected),'ledger':len(actual),'missing':list(expected-actual)[:5],'extra':list(actual-expected)[:5]})
    stale=fs['reports/stale_reference_scan.txt'].read_text('utf-8').splitlines();un=[x for x in stale if '|UNJUSTIFIED|' in x];gate('packaged stale scan no unjustified',not un,{'rows':max(0,len(stale)-2),'unjustified':len(un)});p4=fs['reports/pass4_contradiction_stale_scan.txt'].read_text('utf-8');gate('Pass4 status','status=PASS' in p4 and 'unjustified=0' in p4 and 'active_contradictions=0' in p4,p4[:500])
    lock=json.loads(fs['metadata/final_decision_lock.json'].read_text('utf-8'));gate('decision lock content',lock.get('final_status')=='LIMITED_PASS' and lock.get('final_package_reopen_gate')=='PASS' and lock.get('independent_reopen_gate')=='PASS' and lock.get('public_release_ready') is False and len(lock.get('external_gates_not_tested',[]))==11,lock)
    bt=browser(s);gate('reopened Chromium scenarios',all(r['status']=='PASS' for r in bt),{'tests':len(bt),'failures':[r for r in bt if r['status']!='PASS']});(OUT/'browser_runtime_test.json').write_text(json.dumps({'status':'PASS','tests':bt},ensure_ascii=False,indent=2)+'\n','utf-8')
    status='PASS'
except Exception as ex:err=repr(ex)
summary={'audit':'FINAL_PACKAGE_REOPEN_GATE','status':status,'package':ZIP.name,'zip_sha256':hf(ZIP) if ZIP.exists() else None,'bytes':ZIP.stat().st_size if ZIP.exists() else None,'members':len(zipfile.ZipFile(ZIP).namelist()) if ZIP.exists() else None,'runtime_html_sha256':hf(X/'index.html') if (X/'index.html').exists() else None,'checks':checks}
if err:summary['error']=err
OUT.mkdir(parents=True,exist_ok=True);(OUT/'V10185_R4_FINAL_PACKAGE_REOPEN_AUDIT.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf-8')
lines=['# v101.85 R4 — Final immutable reopened-ZIP audit','',f'**FINAL_PACKAGE_REOPEN_GATE = {status}**','',f'- ZIP: `{summary["package"]}`',f'- SHA-256: `{summary["zip_sha256"]}`',f'- Bytes: {summary["bytes"]}',f'- Members: {summary["members"]}',f'- Runtime HTML SHA-256: `{summary["runtime_html_sha256"]}`','','## Evidence gates','','| Gate | Status | Evidence |','|---|---|---|']
for r in checks:lines.append('| '+r['gate'].replace('|','¦')+' | '+r['status']+' | '+str(r['evidence']).replace('|','¦').replace('\n',' ')[:900]+' |')
if err:lines+=['','## Blocking failure','',f'`{err}`']
else:lines+=['','## Decision','','The immutable R4 ZIP passes the primary reopened-package gate. Runtime HTML remains byte-identical to R3. The 11 external device/PWA/AT/live/rollback gates remain NOT_TESTED.']
(OUT/'V10185_R4_FINAL_PACKAGE_REOPEN_AUDIT.md').write_text('\n'.join(lines)+'\n','utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2));raise SystemExit(0 if status=='PASS' else 1)
