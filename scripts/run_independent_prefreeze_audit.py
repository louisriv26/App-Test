from pathlib import Path
import zipfile,hashlib,re,json,csv,sys
BASE=Path(sys.argv[1]);TREE=Path(sys.argv[2]);VERSION=sys.argv[3]
def sha(b):return hashlib.sha256(b).hexdigest()
def ex(txt,name):
 m=re.search(r'const\s+'+re.escape(name)+r'\s*=\s*',txt);assert m,name
 i=m.end();st=i;d=0;q=None;esc=False
 while i<len(txt):
  c=txt[i]
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==q:q=None
  else:
   if c in "'\"`":q=c
   elif c in '[{(':d+=1
   elif c in ']})':d-=1
   elif c==';' and d==0:return txt[st:i].strip()
  i+=1
 raise AssertionError(name)
with zipfile.ZipFile(BASE) as z: btxt=z.read('index.html').decode()
txt=(TREE/'index.html').read_text()
prot=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS']
checks=[]
def ck(n,o,d=''):checks.append((n,bool(o),d))
ck('html_twins',(TREE/'index.html').read_bytes()==(TREE/'luisa_24_heures.html').read_bytes())
ck('version',f"const APP_VERSION = '{VERSION}';" in txt)
for n in prot:ck('decl_'+n,ex(btxt,n)==ex(txt,n),sha(ex(txt,n).encode()))
qa=(TREE/'REAL_DEVICE_QA_CHECKLIST.md').read_text();qt=(TREE/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').read_text();ck('qa_checklist_current',VERSION in qa.splitlines()[0]);qrows=list(csv.DictReader(qt.splitlines()));ck('qa_template_21',len(qrows)==21 and all(r['app_version']==VERSION for r in qrows),len(qrows))
evdir=TREE/('evidence/'+VERSION.replace('.',''))
r=json.loads((evdir/'BROAD_CHROMIUM_RUNTIME_MATRIX.json').read_text());ck('broad_runtime',r['summary']=={'pass':52,'fail':0,'total':52},r['summary'])
s=json.loads((evdir/'SERVICE_WORKER_LOGIC_MATRIX.json').read_text());ck('sw_logic',s['summary']=={'pass':15,'fail':0,'total':15},s['summary'])
st=(TREE/'reports/stale_reference_scan.txt').read_text();ck('stale_failures_zero','failures: 0' in st,st.strip())
ck('semantic_metadata_zero','semantic current-metadata failures: 0' in st,st.strip())
sc=(TREE/'metadata/scope_escalation_authority.md').read_text();ck('scope_authority_current',VERSION in sc and 'exact ten-action RA19E.2 speaker/presentation ledger plus release-shell version propagation' not in sc,sc.splitlines()[0] if sc else '')
vj=json.loads((TREE/'version.json').read_text());ck('release_scope_current','semantic current-metadata' in vj.get('release_scope','').lower(),vj.get('release_scope',''))
# exact user-fix preservation from baseline declaration parity is enough; add explicit runtime evidence marker.
ck('h3_h22_runtime_rows',sum(1 for x in r['results'] if x['check']=='v101112_user_fixes_preserved' and x['status']=='PASS')==4)
status=all(x[1] for x in checks)
report=['# Independent prefreeze four-pass audit — '+VERSION,'',f'**Status: {"PASS_PREPACKAGE" if status else "FAIL"}**','']
for i,(n,o,d) in enumerate(checks,1):report.append(f'- {i:02d}. `{n}`: **{"PASS" if o else "FAIL"}**'+(f' — `{d}`' if d else ''))
report+=['','This independently implemented checker does not claim final-ZIP reopen, physical-device, live-origin, installed-PWA, true-offline or screen-reader evidence.']
(TREE/'audit/independent_four_pass_audit.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
(TREE/'audit/independent_four_pass_audit.json').write_text(json.dumps({'status':'PASS_PREPACKAGE' if status else 'FAIL','checks_total':len(checks),'checks_pass':sum(x[1] for x in checks),'checks':[{'check':n,'status':'PASS' if o else 'FAIL','detail':d} for n,o,d in checks]},indent=2)+'\n')
if not status:raise SystemExit(2)
print(json.dumps({'status':'PASS_PREPACKAGE','checks':len(checks)}))
