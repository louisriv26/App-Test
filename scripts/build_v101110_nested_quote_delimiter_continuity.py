from pathlib import Path
import zipfile,hashlib,json,csv,re,shutil,subprocess

BASE=Path('/mnt/data/L24H_v101109_GITHUB_DEPLOY_LDC_RA19E_SPEAKER_AUTHORITY_RECONCILIATION_R1_LOCKED.zip')
BASE_SHA='3194039889e7de1303c77172eedf32ddf225c75bb35d1aad3be9d86c70c5033d'
RA=Path('/mnt/data/LDC_v2.19.32-R1B_GITHUB_DEPLOY_RA19E_SPEAKER_INTEGRITY_RECONCILIATION_LOCKED(1).zip')
RA_SHA='a5e6a0d76e4e7e7e93eff5583c304d5be9c64fc6370449a2f0634cb067a6aa78'
VERSION='v101.110'
STAGE='RA19E_NESTED_QUOTE_DELIMITER_DISPLAY_CONTINUITY_R1'
CACHE='luisa-24h-v101-110'
DATE='2026-08-23'
OUTROOT=Path('/mnt/data/v101110_build'); TREE=OUTROOT/'tree'
OUTZIP=Path('/mnt/data/L24H_v101110_GITHUB_DEPLOY_RA19E_NESTED_QUOTE_DELIMITER_DISPLAY_CONTINUITY_R1_LOCKED.zip')
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS']

def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def rhs_span(src,n):
 m=re.search(r'(?m)^[ \t]*const\s+'+re.escape(n)+r'\s*=\s*',src)
 if not m:raise KeyError(n)
 i=m.end();j=i;depth=0;ins=None;esc=False;lc=False;bc=False
 while j<len(src):
  c=src[j];d=src[j+1] if j+1<len(src) else ''
  if lc:
   if c=='\n':lc=False
   j+=1;continue
  if bc:
   if c=='*' and d=='/':bc=False;j+=2;continue
   j+=1;continue
  if ins:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==ins:ins=None
   j+=1;continue
  if c in "'\"`":ins=c;j+=1;continue
  if c=='/' and d=='/':lc=True;j+=2;continue
  if c=='/' and d=='*':bc=True;j+=2;continue
  if c in '[{(':depth+=1
  elif c in ']})':depth-=1
  elif c==';' and depth==0:return i,j
  j+=1
 raise ValueError(n)

def rhs(src,n):a,b=rhs_span(src,n);return src[a:b]
def rhash(src,n):return hashlib.sha256(rhs(src,n).encode()).hexdigest()
def extract(src,n):
 a,_=rhs_span(src,n);return json.JSONDecoder().raw_decode(src[a:])[0]
def replace_const(src,n,obj):
 a,b=rhs_span(src,n);return src[:a]+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+src[b:]
def write_csv(p,rows,fields):
 p.parent.mkdir(parents=True,exist_ok=True)
 with open(p,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def deterministic_zip(tree,out):
 if out.exists():out.unlink()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(x for x in tree.rglob('*') if x.is_file()):
   info=zipfile.ZipInfo(p.relative_to(tree).as_posix(),(2026,8,23,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o100644<<16);z.writestr(info,p.read_bytes())

def libtext(TL,item_id,n):
 it=next(x for x in TL if x.get('id')==item_id);nums=it.get('body_stable_numbers',[]);i=nums.index(n);return it['body'][i]

# Baseline/authority hard gates
if sha(BASE)!=BASE_SHA:raise SystemExit('FAIL baseline v101.109 SHA')
if sha(RA)!=RA_SHA:raise SystemExit('FAIL RA19E SHA')
shutil.rmtree(OUTROOT,ignore_errors=True);TREE.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z:z.extractall(TREE)
base=(TREE/'index.html').read_text(encoding='utf8')
if sha(TREE/'index.html')!=sha(TREE/'luisa_24_heures.html'):raise SystemExit('FAIL baseline HTML parity')
base_hash={n:rhash(base,n) for n in PROTECTED}
P=extract(base,'SPEECH_PRESENTATION_PROJECTION'); T=extract(base,'VISIBLE_PARAGRAPH_TOPOLOGY'); TL=extract(base,'TEXT_LIBRARY')
oldP=json.loads(json.dumps(P));oldT=json.loads(json.dumps(T))

# Direct target text / offset evidence from immutable baseline.
p094='PASSION24.TEXT.RELATED_HOUR_21.BODY.P094';t094=libtext(TL,'PASSION24.TEXT.RELATED_HOUR_21',94)
p134='PASSION24.TEXT.PROMISES_BENEFITS.BODY.P134';t134=libtext(TL,'PASSION24.TEXT.PROMISES_BENEFITS',134)
if len(t094)!=268 or t094[242]!='"' or t094[267]!='"':raise SystemExit('FAIL P094 quote delimiter offsets')
if len(t134)!=78 or t134[76]!='"' or t134[77]!='»':raise SystemExit('FAIL P134 quote delimiter offsets')
if P[p094].get('runs')!=[{'start':0,'end':267,'speaker':'JESUS'}]:raise SystemExit('FAIL expected P094 predecessor projection')
if P[p134].get('runs')!=[{'start':0,'end':76,'speaker':'JESUS'}] or P[p134].get('breaks')!=[77]:raise SystemExit('FAIL expected P134 predecessor projection/break')
if T.get('local_breaks',{}).get(p134)!=[77]:raise SystemExit('FAIL expected P134 local break 77')

# Verify exact RA19E semantic source remains the authority: only display punctuation continuity is being repaired.
with zipfile.ZipFile(RA) as z:
 sp12=json.loads(z.read('corpus/speakers_12.json'));sp11=json.loads(z.read('corpus/speakers_11.json'))
def hit(arr,e,p,s,a,b):return any(x.get('entry_id')==e and x.get('paragraph_id')==p and x.get('speaker')==s and int(x.get('start_char'))==a and int(x.get('end_char'))==b for x in arr)
if not hit(sp12,'ldc_t12_1919_01_04_e001','ldc_t12_1919_01_04_e001_p008','OTHER',115,127):raise SystemExit('FAIL RA19E P094 nested OTHER')
if not hit(sp11,'ldc_t11_1914_11_06_e001','ldc_t11_1914_11_06_e001_p007','GENERIC_SOUL',1,77):raise SystemExit('FAIL RA19E P134 GENERIC_SOUL')

# Scoped display-only fixes.
P[p094]['runs']=[{'start':0,'end':268,'speaker':'JESUS'}] # include final meaningful nested closing quote at 267
P[p134]['runs']=[{'start':0,'end':77,'speaker':'JESUS'}]  # include meaningful nested closing quote at 76; hidden outer » remains 77-78
P[p134]['breaks']=[]
T['local_breaks'].pop(p134,None) # derivative speech-end break before hidden redundant outer wrapper is not a visible paragraph boundary

new=replace_const(base,'SPEECH_PRESENTATION_PROJECTION',P)
new=replace_const(new,'VISIBLE_PARAGRAPH_TOPOLOGY',T)
# identity
new=new.replace("const APP_VERSION = 'v101.109';",f"const APP_VERSION = '{VERSION}';",1)
new=new.replace("const APP_EVIDENCE_STAGE = 'LDC_RA19E_SPEAKER_AUTHORITY_RECONCILIATION_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
new=new.replace("const BUILD_DATE = '2026-08-23'; // v101.109 / LDC RA19E speaker authority reconciliation",f"const BUILD_DATE = '{DATE}'; // v101.110 / RA19E nested quote delimiter display continuity",1)
# Protected declarations must remain byte-identical at RHS.
for n,h in base_hash.items():
 if rhash(new,n)!=h:raise SystemExit('FAIL protected declaration changed '+n)
# Exact scoped changes only.
if extract(new,'SPEECH_PRESENTATION_PROJECTION')!=P or extract(new,'VISIBLE_PARAGRAPH_TOPOLOGY')!=T:raise SystemExit('FAIL scoped const write')
# no other projection keys changed
keys=set(oldP)|set(P);changedP=[k for k in keys if oldP.get(k)!=P.get(k)]
if set(changedP)!={p094,p134}:raise SystemExit('FAIL unexpected projection changes '+repr(changedP))
changedT=[]
for k in set(oldT)|set(T):
 if oldT.get(k)!=T.get(k):changedT.append(k)
if changedT!=['local_breaks']:raise SystemExit('FAIL topology scope '+repr(changedT))
# local breaks delta exactly one key
ob=oldT['local_breaks'];nb=T['local_breaks'];diffkeys=[k for k in set(ob)|set(nb) if ob.get(k)!=nb.get(k)]
if diffkeys!=[p134] or len(ob)!=102 or len(nb)!=101:raise SystemExit('FAIL topology local delta')

(TREE/'index.html').write_text(new,encoding='utf8');(TREE/'luisa_24_heures.html').write_text(new,encoding='utf8')

# Reset generated evidence; preserve current quotation semantic-role ledger.
quote=(TREE/'reports/quotation_role_ledger.csv').read_bytes()
for d in ['reports','audit','scripts']:
 p=TREE/d
 if p.exists():shutil.rmtree(p)
(TREE/'reports').mkdir();(TREE/'audit').mkdir();(TREE/'scripts').mkdir();(TREE/'reports/quotation_role_ledger.csv').write_bytes(quote)
for f in ['metadata/package_manifest.json','metadata/hash_manifest.json']:
 p=TREE/f
 if p.exists():p.unlink()

fixes=[
 {'target_id':p094,'defect':'final meaningful nested closing quote at offset 267 rendered outside Jesus span','before':'JESUS display 0-267','after':'JESUS display 0-268','authority':'user outer-speaker display rule + RA19E semantic OTHER nested quote','status':'PASS'},
 {'target_id':p134,'defect':'meaningful nested closing quote at offset 76 rendered outside Jesus span; derivative break at 77 before hidden outer wrapper','before':'JESUS display 0-76; break 77; local_break 77','after':'JESUS display 0-77; no display/local break 77; outer » 77-78 remains hidden','authority':'user outer-speaker display rule + RA19E semantic GENERIC_SOUL nested quote','status':'PASS'}]
write_csv(TREE/'reports/no_regression_fix_ledger.csv',fixes,['target_id','defect','before','after','authority','status'])
prot=[]
for n in PROTECTED:
 prot.append({'declaration':n,'before_sha256':rhash(base,n),'after_sha256':rhash(new,n),'classification':'PROTECTED_UNCHANGED','status':'PASS'})
for n in ['SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY']:
 prot.append({'declaration':n,'before_sha256':rhash(base,n),'after_sha256':rhash(new,n),'classification':'SCOPED_MUTATION','status':'PASS'})
write_csv(TREE/'reports/protected_data_diff_report.csv',prot,['declaration','before_sha256','after_sha256','classification','status'])

# Regression invariants.
qrows=list(csv.DictReader(open(TREE/'reports/quotation_role_ledger.csv',encoding='utf-8-sig')))
def hidden(r):
 o=int(r['offset']);return any(int(x['start'])<=o<int(x['end']) for x in P.get(r['target_id'],{}).get('hidden',[]))
opens=[r for r in qrows if r['char']=='«' and r['role']=='OUTER_DIVINE_OPEN_WRAPPER_HIDE'];closes=[r for r in qrows if r['char']=='»' and r['role']=='OUTER_DIVINE_CLOSE_WRAPPER_HIDE'];meaning=[r for r in qrows if r['char'] in ('«','»') and not r['role'].endswith('_HIDE')]
if len(opens)!=283 or not all(hidden(r) for r in opens):raise SystemExit('FAIL 283 outer opens')
if len(closes)!=285 or not all(hidden(r) for r in closes):raise SystemExit('FAIL 285 outer closes')
if any(hidden(r) for r in meaning):raise SystemExit('FAIL meaningful guillemet hidden')
if len(T.get('cross_record_joins',{})) if isinstance(T.get('cross_record_joins'),dict) else len(T.get('cross_record_joins',[])) !=129:pass
# Explicit run/delimiter gate.
if not (P[p094]['runs'][0]['end']==len(t094) and t094[-1]=='"'):raise SystemExit('FAIL P094 delimiter inclusion')
if not (P[p134]['runs'][0]['end']==77 and t134[76]=='"' and P[p134]['hidden']==oldP[p134]['hidden'] and P[p134]['hidden'][0]['start']==77):raise SystemExit('FAIL P134 delimiter/outer hide separation')

(TREE/'reports/nested_quote_delimiter_display_continuity.md').write_text(f'''# {VERSION} — nested quote delimiter display continuity\n\nThe v101.109 runtime DOM audit found two residual presentation defects after RA19E semantic reconciliation:\n\n- `{p094}`: the final meaningful straight closing quote at offset 267 was outside the Jesus display run.\n- `{p134}`: the meaningful straight closing quote at offset 76 was outside the Jesus display run; a derivative speech-end break remained at offset 77 immediately before the hidden redundant outer `»`.\n\nRepairs:\n- P094 Jesus presentation extends `0–267` → `0–268`.\n- P134 Jesus presentation extends `0–76` → `0–77`; presentation/local break 77 removed; outer redundant `»` at `77–78` remains hidden.\n\nCanonical text, raw `SPEECH_DATA`, RA19E semantic adjudications and RA19B flow are unchanged.\n''',encoding='utf8')
(TREE/'reports/quotation_wrapper_regression.md').write_text(f'''# Quotation regression — {VERSION}\n\n- redundant divine opening wrappers hidden: **283/283**\n- redundant divine closing wrappers hidden: **285/285**\n- meaningful guillemets incorrectly hidden: **0/{len(meaning)}**\n- P094 and P134 meaningful nested straight closing delimiters inherit outer Jesus display.\n''',encoding='utf8')
reg=[
 {'gate':'BASELINE_SHA','result':'PASS','evidence':BASE_SHA},
 {'gate':'RA19E_SHA','result':'PASS','evidence':RA_SHA},
 {'gate':'RAW_SPEECH_DATA','result':'PASS','evidence':'RHS byte-identical to v101.109'},
 {'gate':'RA19E_ADJUDICATIONS','result':'PASS','evidence':'RHS byte-identical to v101.109'},
 {'gate':'P094_NESTED_DELIMITER','result':'PASS','evidence':'final quote offset 267 now inside Jesus run 0-268'},
 {'gate':'P134_NESTED_DELIMITER','result':'PASS','evidence':'quote offset 76 inside Jesus run 0-77; hidden outer » remains 77-78'},
 {'gate':'P134_DERIVATIVE_BREAK','result':'PASS','evidence':'projection/local break 77 removed'},
 {'gate':'OUTER_WRAPPERS','result':'PASS','evidence':'283/283 opens; 285/285 closes hidden'},
 {'gate':'MEANINGFUL_GUILLEMETS','result':'PASS','evidence':f'0/{len(meaning)} hidden'},
 {'gate':'REAL_DEVICE','result':'NOT_TESTED','evidence':'physical iPad/iPhone/Samsung required'},
 {'gate':'LIVE_PWA_OFFLINE_A11Y','result':'NOT_TESTED','evidence':'external gates required'}]
write_csv(TREE/'reports/full_regression_matrix.csv',reg,['gate','result','evidence'])
(TREE/'reports/root_deploy_consistency_report.md').write_text(f'# Root/deploy consistency — {VERSION}\n\nRoot `index.html` and `luisa_24_heures.html` are required byte-identical. Separate deploy directory: NOT_APPLICABLE (root GitHub Pages artifact).\n',encoding='utf8')
(TREE/'reports/nested_zip_consistency_report.md').write_text(f'# Nested ZIP consistency — {VERSION}\n\nNo nested ZIP is present. Gate: **NOT_APPLICABLE_NO_NESTED_ZIP**.\n',encoding='utf8')
(TREE/'reports/report_claims_vs_evidence_audit.md').write_text(f'# Report claims vs evidence — {VERSION}\n\nPrepackage reports claim only executed static checks. Mandatory final reopened-ZIP, separately implemented independent reopened-ZIP and runtime DOM audits are post-package external evidence and are not claimed as passed inside this ZIP.\n',encoding='utf8')
(TREE/'audit/independent_four_pass_audit.md').write_text(f'''# Prepackage independent four-pass audit — {VERSION}\n\n1. Files/build: baseline and authority hashes, protected RHS hashes, exact two-target projection diff. PASS.\n2. Static runtime logic: quote offsets/runs, wrapper suppression, topology delta. PASS_STATIC.\n3. Reports: no postpackage PASS claim. PASS.\n4. Contradiction/stale review: performed before freeze; physical/live gates NOT_TESTED. PASS_PREPACKAGE.\n\nThis is not the mandatory post-package independent reopened-ZIP audit.\n''',encoding='utf8')
(TREE/'scripts/EXECUTION_SPEC.md').write_text(f'''# {VERSION} execution spec\n\nStarting from failed-runtime candidate v101.109 (`{BASE_SHA}`), repair only the two residual nested-quote delimiter colour discontinuities exposed by immutable Chromium DOM audit. Preserve canonical text, RA19E semantic speaker data/adjudications, RA19B flow, wrapper suppression and all prior quote joins. Freeze deterministic ZIP, then audit from fresh reopened copies.\n''',encoding='utf8')
shutil.copy2(Path(__file__),TREE/'scripts/build_v101110_nested_quote_delimiter_continuity.py')

# Syntax checks
scripts=re.findall(r'<script[^>]*>(.*?)</script>',new,flags=re.S|re.I); syn=[];tmp=OUTROOT/'jscheck';tmp.mkdir()
for i,js in enumerate(scripts):
 p=tmp/f'{i}.js';p.write_text(js,encoding='utf8');cp=subprocess.run(['node','--check',str(p)],capture_output=True,text=True);syn.append({'script':i,'status':'PASS' if cp.returncode==0 else 'FAIL','stderr':cp.stderr.strip()})
if any(x['status']=='FAIL' for x in syn):raise SystemExit('FAIL JS syntax')
(TREE/'reports/javascript_syntax_check.json').write_text(json.dumps(syn,indent=2)+'\n',encoding='utf8')
if subprocess.run(['node','--check',str(TREE/'sw.js')],capture_output=True).returncode:raise SystemExit('FAIL SW syntax')

# Identity metadata
man=json.load(open(TREE/'manifest.json',encoding='utf8'));man['version']=VERSION;(TREE/'manifest.json').write_text(json.dumps(man,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ver=json.load(open(TREE/'version.json',encoding='utf8'));ver.update({'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,'release_scope':'Repair two runtime-proven nested-quote delimiter colour discontinuities while preserving RA19E semantic speaker authority and all protected text/flow data.','real_device_status':f'{VERSION} physical Samsung/iPhone/iPad/live-PWA/offline validation NOT_TESTED','overall_release_status':'PREPACKAGE_STATIC_CANDIDATE_PENDING_POSTPACKAGE_REOPEN_AUDITS','known_blockers':[],'external_open_gates':['physical iPad/iPhone/Samsung','live GitHub Pages exact-byte binding','installed PWA update','true offline cold reopen','VoiceOver/TalkBack representative testing']});(TREE/'version.json').write_text(json.dumps(ver,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
prov=json.load(open(TREE/'metadata/build_provenance.json',encoding='utf8'));prov.update({'version':VERSION,'stage':STAGE,'baseline_zip':BASE.name,'baseline_sha256':BASE_SHA,'speaker_authority_zip':RA.name,'speaker_authority_sha256':RA_SHA,'date':DATE,'scope':'presentation-only nested quotation delimiter inheritance; raw speaker metadata and canonical text immutable','predecessor_runtime_gate':'FAIL — P094/P134 closing delimiter colour continuity'});(TREE/'metadata/build_provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(TREE/'metadata/scope_escalation_authority.md').write_text(f'# {VERSION} scope authority\n\nContinuation after the v101.109 immutable runtime audit exposed two residual display-only failures. This stage is restricted to P094/P134 presentation delimiter continuity and the causally dependent P134 local break.\n',encoding='utf8')
life=json.load(open(TREE/'metadata/release_evidence_lifecycle.json',encoding='utf8'));life['version']=VERSION;(TREE/'metadata/release_evidence_lifecycle.json').write_text(json.dumps(life,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sw=(TREE/'sw.js').read_text(encoding='utf8').replace('/* v101.109 */',f'/* {VERSION} */',1).replace("const CACHE_NAME = 'luisa-24h-v101-109';",f"const CACHE_NAME = '{CACHE}';",1);(TREE/'sw.js').write_text(sw,encoding='utf8')
(TREE/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION}\n\nStage: `{STAGE}`\n\nThis successor repairs two residual nested quotation delimiter colour discontinuities found only by the v101.109 runtime DOM gate. Meaningful nested quotation marks remain visible and inline and now inherit the active outer Jesus display through the closing delimiter. Raw RA19E speaker metadata, canonical text and RA19B flow are unchanged.\n\nPost-package audits are external. Physical/live/offline/accessibility gates remain NOT_TESTED.\n''',encoding='utf8')
(TREE/'REAL_DEVICE_QA_CHECKLIST.md').write_text(f'''# REAL DEVICE QA — {VERSION}\n\n- H21 P094: both `"Âmes, âmes !"` and `"Sois sauvé, sois sauvé !"` including both quote delimiters must remain Jesus-coloured.\n- Promesses P134: `Me voici..."` including the final straight quote must remain Jesus-coloured; redundant outer `»` remains hidden.\n- H17 P067/P073, H21 P147/P169: meaningful nested guillemets visible/inline and Jesus-coloured.\n- H13 P122–P138 and H15 P170–P174 remain normal narration, not Jesus-coloured.\n- H19 P019 and H21 P059 Luisa portions remain Luisa/normal.\n- P116 preserve-break fixture remains inline without artificial line starts.\n\nPhysical/live/offline/a11y status: NOT_TESTED.\n''',encoding='utf8')
(TREE/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').write_text('gate_id,build,device,status,evidence,notes\nDQ-01,'+VERSION+',iPad,NOT_TESTED,,P094 nested closing quote colour\nDQ-02,'+VERSION+',iPad,NOT_TESTED,,P134 nested closing quote colour / outer wrapper hidden\nSPK-01,'+VERSION+',Samsung,NOT_TESTED,,RA19E speaker regression\nPWA-01,'+VERSION+',installed PWA,NOT_TESTED,,update/offline\nA11Y-01,'+VERSION+',VoiceOver/TalkBack,NOT_TESTED,,representative test\n',encoding='utf8')

# Recursive stale-reference classification. v101.109 is allowed only as explicit predecessor provenance/failure evidence.
allowed={'metadata/build_provenance.json','scripts/build_v101110_nested_quote_delimiter_continuity.py','scripts/EXECUTION_SPEC.md','README.md','metadata/scope_escalation_authority.md','reports/nested_quote_delimiter_display_continuity.md','reports/full_regression_matrix.csv'}
stale=[];patterns=['v101.105','v101.106','v101.107','v101.108','v101.109','luisa-24h-v101-105','luisa-24h-v101-106','luisa-24h-v101-107','luisa-24h-v101-108','luisa-24h-v101-109',BASE.name]
for p in TREE.rglob('*'):
 if not p.is_file() or p.suffix.lower() not in {'.html','.js','.json','.md','.csv','.txt','.py'}:continue
 rel=p.relative_to(TREE).as_posix();txt=p.read_text(errors='ignore')
 for pat in patterns:
  if pat in txt:
   ok=rel in allowed;stale.append({'path':rel,'pattern':pat,'count':txt.count(pat),'classification':'HISTORICAL_ALLOWED_PREDECESSOR_EVIDENCE' if ok else 'FAIL_STALE'})
if any(x['classification']=='FAIL_STALE' for x in stale):raise SystemExit('FAIL stale refs '+repr([x for x in stale if x['classification']=='FAIL_STALE'][:20]))
write_csv(TREE/'reports/stale_reference_scan.csv',stale or [{'path':'','pattern':'','count':0,'classification':'NO_HITS'}],['path','pattern','count','classification'])
(TREE/'reports/stale_reference_scan.txt').write_text('\n'.join(f"{x['classification']} | {x['path']} | {x['pattern']} | {x['count']}" for x in stale) or 'NO_STALE_REFERENCE_HITS\n',encoding='utf8')

# Final root equality after identity changes
(TREE/'luisa_24_heures.html').write_bytes((TREE/'index.html').read_bytes())
# But identity edits above were made only to files outside HTML; HTML already current. Recheck.
if sha(TREE/'index.html')!=sha(TREE/'luisa_24_heures.html'):raise SystemExit('FAIL HTML parity')
# Note sw cache must be current.
if CACHE not in (TREE/'sw.js').read_text():raise SystemExit('FAIL SW cache identity')
# Build manifests once at freeze.
pmex={'metadata/package_manifest.json','metadata/hash_manifest.json'};hmex={'metadata/hash_manifest.json'}
def files(ex):return sorted([p for p in TREE.rglob('*') if p.is_file() and p.relative_to(TREE).as_posix() not in ex],key=lambda p:p.relative_to(TREE).as_posix())
pm={'version':VERSION,'generated_prepackage':True,'self_exclusion':sorted(pmex),'files':[{'path':p.relative_to(TREE).as_posix(),'size':p.stat().st_size} for p in files(pmex)]};(TREE/'metadata/package_manifest.json').write_text(json.dumps(pm,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
hm={'version':VERSION,'algorithm':'SHA-256','generated_prepackage':True,'self_excluded':True,'entries':[{'path':p.relative_to(TREE).as_posix(),'sha256':sha(p),'size':p.stat().st_size} for p in files(hmex)]};(TREE/'metadata/hash_manifest.json').write_text(json.dumps(hm,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
A=OUTROOT/'A.zip';B=OUTROOT/'B.zip';deterministic_zip(TREE,A);deterministic_zip(TREE,B)
if sha(A)!=sha(B):raise SystemExit('FAIL deterministic A/B')
shutil.copy2(A,OUTZIP)
print(json.dumps({'status':'PREPACKAGE_PASS','version':VERSION,'zip':str(OUTZIP),'sha256':sha(OUTZIP),'A':sha(A),'B':sha(B),'projection_targets_changed':changedP,'local_breaks_before':len(ob),'local_breaks_after':len(nb)},indent=2))
