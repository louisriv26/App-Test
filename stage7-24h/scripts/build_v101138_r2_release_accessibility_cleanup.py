from pathlib import Path
import hashlib, json, zipfile, shutil, re, sys

R1_ZIP_SHA='a1b996c766e5b912f0eceb88ff9b4a1c38c3f7c2bf296f2c7d4f7c3f666d373a'
OBSERVED_LIVE_R2_ZIP_SHA='0ae4e7da4ec034952e0e596bb2c5ded947f7c7fade21c8974783de7308b0dbc5'
CONTENT_R1_SHA='b63fe5e224cf28be53c59eb9098fb561b746c0b8bbc892d07ce203475c1bf65d'
VERSION='v101.138'; REV='R2'; DATE='2026-09-08'; CACHE='luisa-24h-v101-138-r2'
STAGE='RELEASE_ACCESSIBILITY_CLEANUP_R2'
LEDGER_SHA='f9a9c4c74df33b3f96909e3611acb74c448deed5fa367fa86072d2e27cbfef49'
R5_SHA='7ef830738ff5665ae5b880d52bde029e4b9ba092d834f81b008d24615e1ab9e7'
CORPUS_FP='87733d22b5e899e23da263c37a2c2b30d85585b7a40f3dbf5b9ab4c05ae496d7'
PROTECTED=[
 'CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS',
 'LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA',
 'VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_PROJECTION',
 'SPEECH_PRESENTATION_ADJUDICATIONS'
]
ABOUT_TEXTS=[
 "L’intégralité du corpus des 24 méditations et des 24 « Réflexions et pratiques », y compris la Désolation de Marie de la 24e Heure, a été soumise à une validation source-critique approfondie. Cette validation s’appuie sur un corpus critique italien de référence établi pour ce projet à partir de plusieurs témoins italiens. Le corpus a également été comparé intégralement, Heure par Heure, à la 27e édition de l’AFLP.",
 "Lorsque les sources divergent et que la question peut être tranchée avec suffisamment de certitude, le corpus critique italien retenu guide le texte de l’application. Les rares divergences historiques qui restent incertaines ont été laissées inchangées.",
 "Cette validation concerne les 24 méditations et les 24 « Réflexions et pratiques ». Les textes du Livre du Ciel proposés dans « Approfondir » relèvent d’un programme de validation distinct."
]

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def files(root):
 root=Path(root)
 return {p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file()}
def writej(p,o):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def raw_const(text,name):
 m=re.search(rf'const\s+{re.escape(name)}\s*=\s*',text); assert m,name
 start=m.end(); i=start
 while i<len(text) and text[i].isspace(): i+=1
 opener=text[i]; assert opener in '[{',(name,opener)
 pairs={'[':']','{':'}'}; stack=[]; quote=None; esc=False; j=i
 while j<len(text):
  ch=text[j]
  if quote:
   if esc: esc=False
   elif ch=='\\': esc=True
   elif ch==quote: quote=None
  else:
   if ch in ('"',"'",'`'): quote=ch
   elif ch in '[{': stack.append(pairs[ch])
   elif ch in ']}':
    assert stack and ch==stack[-1],(name,j,ch)
    stack.pop()
    if not stack:
     raw=text[start:j+1]
     try: obj=json.loads(raw)
     except Exception: obj=None
     return raw,obj
  j+=1
 raise AssertionError(('unterminated',name))
def exact_replace(s,old,new,label,count=1):
 c=s.count(old); assert c==count,(label,c,count)
 return s.replace(old,new,count)
def collect_ids(obj):
 out=[]
 def walk(x):
  if isinstance(x,dict):
   if 'id' in x: out.append(str(x['id']))
   for v in x.values(): walk(v)
  elif isinstance(x,list):
   for v in x: walk(v)
 walk(obj); return out
def freeze(root,zp):
 root=Path(root); zp=Path(zp); zp.unlink(missing_ok=True)
 with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(root.rglob('*')):
   if not p.is_file(): continue
   rel=p.relative_to(root).as_posix()
   info=zipfile.ZipInfo(rel,(2026,9,8,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=(0o644<<16)
   z.writestr(info,p.read_bytes())
 return sha_file(zp)

def build(r1_zip,out):
 r1_zip=Path(r1_zip); out=Path(out)
 actual=sha_file(r1_zip); assert actual==R1_ZIP_SHA,(actual,R1_ZIP_SHA)
 shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
 with zipfile.ZipFile(r1_zip) as z:
  assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
  z.extractall(out)
 basehash={k:sha_file(p) for k,p in files(out).items()}
 basepaths=set(basehash)
 r1=(out/'index.html').read_text(encoding='utf-8')
 assert r1==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 protected_before={n:sha_bytes(raw_const(r1,n)[0].encode()) for n in PROTECTED}
 corpus_before=raw_const(r1,'CORPUS')[1]; textlib_before=raw_const(r1,'TEXT_LIBRARY')[1]
 assert corpus_before['fingerprint_sha256']==CORPUS_FP
 ids_before={'CORPUS':collect_ids(corpus_before),'TEXT_LIBRARY':collect_ids(textlib_before)}
 ev137r1={k:sha_file(p) for k,p in files(out/'evidence/v101137_r1').items()}
 ev137r2={k:sha_file(p) for k,p in files(out/'evidence/v101137_r2').items()}
 ev138r1={k:sha_file(p) for k,p in files(out/'evidence/v101138_r1').items()}
 for t in ABOUT_TEXTS: assert r1.count(t)==1,('about text count',r1.count(t),t[:40])

 s=r1
 s=exact_replace(s,"const BUILD_REVISION = 'R1';",f"const BUILD_REVISION = '{REV}';",'runtime revision')
 s=exact_replace(s,"const APP_EVIDENCE_STAGE = 'HELP_SUPPORT_ABOUT_LAYOUT_SUCCESSOR_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",'runtime stage')
 s=exact_replace(s,"const BUILD_DATE = '2026-09-08'; // v101.138 R1 / Help assistance and À propos layout successor; canonical corpus byte-identical to v101.137 R2/R1", "const BUILD_DATE = '2026-09-08'; // v101.138 R2 / release-accessibility cleanup; canonical corpus byte-identical to v101.138 R1 and v101.137 R2/R1",'build comment')
 s=exact_replace(s,"const heading=target.querySelector('.help-section-hd');","const heading=target.querySelector('.help-section-hd, .help-feature-title');",'Help quick-nav focus selector')
 (out/'index.html').write_text(s,encoding='utf-8'); (out/'luisa_24_heures.html').write_text(s,encoding='utf-8')

 sw=(out/'sw.js').read_text(encoding='utf-8')
 sw=exact_replace(sw,'/* v101.138 R1 */','/* v101.138 R2 */','sw revision')
 sw=exact_replace(sw,"const CACHE_NAME = 'luisa-24h-v101-138-r1';",f"const CACHE_NAME = '{CACHE}';",'sw cache')
 (out/'sw.js').write_text(sw,encoding='utf-8')

 man=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
 assert man['version']==VERSION and man['build_revision']=='R1'
 man['build_revision']=REV; writej(out/'manifest.json',man)

 v=json.loads((out/'version.json').read_text(encoding='utf-8'))
 assert v['app_version']==VERSION and v['build_revision']=='R1'
 v['build_revision']=REV; v['cache_name']=CACHE
 v['release_scope']=(
   f"Release/accessibility-cleanup successor of exact v101.138 R1 SHA-256 {R1_ZIP_SHA}. "
   f"v101.137 R2 was the observed live predecessor to R1; the exact SHA-bound v101.137 R2 package {OBSERVED_LIVE_R2_ZIP_SHA} was the immutable R1 builder input. "
   "Exact byte-binding of the live origin itself remains an external gate unless independently closed. "
   "R2 fixes Help quick-navigation focus for the Assistance heading and refreshes lineage/release evidence only. CORPUS, TEXT_LIBRARY, stable IDs/order, protected presentation/topology declarations, storage schema, personal snapshot schema, source-critical decisions and approved À propos textual-provenance wording are unchanged."
 )
 v['real_device_status']='Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.138 R2.'
 v['overall_release_status']='V101138_R2_RELEASE_ACCESSIBILITY_CLEANUP_CONTROLLED_DEVICE_TEST_CANDIDATE__FINAL_PUBLIC_DEPLOYMENT_UNAUTHORIZED'
 gates=['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update from observed live v101.137 R2 to v101.138 R2','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing']
 v['known_blockers']=gates; v['external_open_gates']=gates
 v['postfreeze_reopen_evidence']='Exact v101.138 R2 successor ZIP requires external SHA-bound final recheck before controlled device testing.'
 writej(out/'version.json',v)

 # Historical placement for predecessor active report.
 hist=out/'reports/historical/v101138_r1'; hist.mkdir(parents=True,exist_ok=True)
 r1rep=out/'reports/V101138_R1_HELP_SUPPORT_ABOUT_LAYOUT.md'
 assert r1rep.exists()
 shutil.move(str(r1rep),str(hist/r1rep.name))
 report=out/'reports/V101138_R2_RELEASE_ACCESSIBILITY_CLEANUP.md'
 report.write_text(f'''# {VERSION} {REV} — release/accessibility cleanup\n\n## Scope\nThis build is a narrowly bounded successor of exact v101.138 R1 SHA-256 `{R1_ZIP_SHA}`. No corpus/source-critical mutation is authorized or introduced.\n\n## Implemented repairs\n1. `helpJumpTo()` now resolves either `.help-section-hd` or `.help-feature-title`, so activating **Signaler un problème** scrolls to Assistance and transfers keyboard/screen-reader focus to `#help-support-title`. Existing Help sections continue to use `.help-section-hd`.\n2. Six stale `_r2_to_r3` keys in `metadata/build_provenance.json` are replaced with final v101.137 R2 → v101.138 R2 lineage names; all six values remain zero.\n3. Active provenance wording distinguishes the **observed live predecessor** from the **exact SHA-bound immutable builder input**. Live-origin exact-byte binding remains an external gate.\n4. Version/build/cache/release evidence is refreshed to v101.138 R2.\n\n## Protected invariants\n- CORPUS and TEXT_LIBRARY are byte-identical to v101.138 R1.\n- all 14 protected declarations are byte-identical.\n- corpus fingerprint remains `{CORPUS_FP}`.\n- stable IDs and record order are unchanged.\n- `evidence/v101137_r1`, `evidence/v101137_r2`, and predecessor `evidence/v101138_r1` remain byte-identical.\n- storage schema 8 and personal snapshot schema 5 are unchanged.\n- exact 79-row source-critical authority and PRESERVE_MOVE evidence-only visibility remain unchanged.\n- approved `Validation textuelle`, `Principe de référence`, and `Portée de cette validation` wording is unchanged.\n\nFinal public deployment remains unauthorized pending the external live/device/PWA/offline/accessibility gates.\n''',encoding='utf-8')

 (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION} {REV}\n\nControlled device-test candidate and narrowly bounded release/accessibility-cleanup successor of exact v101.138 R1 SHA-256 `{R1_ZIP_SHA}`.\n\nv101.137 R2 was the **observed live predecessor** to R1. The exact SHA-bound v101.137 R2 package `{OBSERVED_LIVE_R2_ZIP_SHA}` was the immutable R1 builder input; exact byte-binding of the live origin itself remains an external gate unless independently closed.\n\nR2 fixes Help quick-navigation focus on the Assistance heading and refreshes lineage/release evidence. The complete canonical meditation/reflection corpus, linked TEXT_LIBRARY, stable IDs/order, source-critical decisions, storage/personal-data schemas and approved À propos textual-provenance wording remain unchanged.\n\nFinal public deployment remains unauthorized pending live-origin, installed-PWA, physical-device, true-offline and accessibility gates.\n''',encoding='utf-8')

 (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(f'''# Real-device QA checklist — {VERSION} {REV}\n\nUse only the exact v101.138 R2 candidate identified by the external SHA-bound receipt.\n\n## Identity\n- app_version = v101.138\n- build_revision = R2\n- cache_name = {CACHE}\n- APP_EVIDENCE_STAGE = {STAGE}\n- corpus fingerprint begins `87733d22b5e899e2` and is unchanged\n\n## A. Aide / Assistance focus\n- Open Aide et À propos.\n- Activate quick navigation **Signaler un problème** using keyboard and representative screen-reader navigation.\n- It must scroll to Assistance and active focus must land on heading `#help-support-title` (`.help-feature-title`).\n- Activate at least one pre-existing quick-nav target (for example Rechercher un texte); focus must still land on its `.help-section-hd`.\n- Assistance controls remain styled, usable, and correctly named.\n- Both support payloads identify `Version : v101.138 R2`.\n\n## B. Layout\nCheck light and dark modes on phone/tablet/desktop widths: no horizontal overflow; Assistance stacks on phone and uses two columns when space permits; Vie privée and À propos des textes remain separate.\n\n## C. Existing-PWA update\nUnder the governing handover assumption that v101.138 R1 was not deployed, test the observed live v101.137 R2 installation → v101.138 R2 without uninstalling. Preserve at least one note, highlight, meditated Hour, last place, theme and font size. Close/reopen three times.\n\n## D. Corpus regression\n- canonical CORPUS and TEXT_LIBRARY match certified R1 bytes; fingerprint unchanged.\n- stable IDs/order unchanged.\n- 24 PRESERVE_MOVE records remain evidence-only/not visible.\n- no H23/H24 governance or source-critical changes.\n\n## E. Physical/offline/accessibility\nRun iPhone, iPad portrait/landscape and Samsung/Android; verify normal navigation, persistence, true offline cold reopen, representative VoiceOver/TalkBack, Help focus behavior and close/focus return.\n\nFinal public deployment remains unauthorized until all mandatory external gates pass.\n''',encoding='utf-8')

 (out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').write_text(
 'gate_id,profile,required,expected,actual,status,notes\n'
 'LIVE-01,browser,YES,Aide shows v101.138 R2 and structured Assistance/Vie privée/À propos des textes,,,\n'
 'HELP-FOCUS-01,keyboard,YES,Signaler un problème quick-nav focuses #help-support-title after scroll,,,\n'
 'HELP-FOCUS-02,keyboard,YES,Existing quick-nav target still focuses .help-section-hd,,,\n'
 'HELP-03,browser,YES,Signaler un problème de texte control remains functional,,,\n'
 'HELP-04,browser,YES,Copier les diagnostics control remains functional,,,\n'
 'HELP-05,browser,YES,Both support payloads contain Version : v101.138 R2,,,\n'
 'UPDATE-01,iPhone;iPad;Samsung,YES,observed live v101.137 R2 updates in place to v101.138 R2,,,\n'
 'UPDATE-02,iPhone;iPad;Samsung,YES,notes/highlights/read state/last place/theme/font preserved,,,\n'
 'CORPUS-01,browser,YES,CORPUS/TEXT_LIBRARY/fingerprint/stable IDs unchanged,,,\n'
 'OFFLINE-01,iPhone;iPad;Samsung,YES,true offline cold reopen works after online load,,,\n'
 'ACCESS-01,iPhone/iPad VoiceOver,YES,Assistance focus and controls are named/navigable,,,\n'
 'ACCESS-02,Samsung TalkBack,YES,Assistance focus and controls are named/navigable,,,\n',encoding='utf-8')

 # New R2 evidence; preserve all predecessor evidence byte-for-byte.
 ev=out/'evidence/v101138_r2'; ev.mkdir(parents=True,exist_ok=True)
 writej(ev/'R1_PREDECESSOR_BINDING.json',{
   'version':VERSION,'build_revision':REV,'predecessor':'v101.138 R1','predecessor_zip_sha256':R1_ZIP_SHA,
   'observed_live_predecessor':'v101.137 R2','v101137_r2_immutable_builder_input_sha256':OBSERVED_LIVE_R2_ZIP_SHA,
   'live_origin_exact_byte_binding':'EXTERNAL_GATE_OPEN','content_predecessor':'v101.137 R1','content_predecessor_sha256':CONTENT_R1_SHA,
   'authorized_79_ledger_sha256':LEDGER_SHA,'immutable_r5_source_baseline_sha256':R5_SHA,
   'scope':'release/accessibility cleanup only; zero corpus/source-critical mutation'})
 (ev/'ACCESSIBILITY_FOCUS_REPAIR.md').write_text('''# v101.138 R2 Help quick-navigation focus repair\n\nR1 scrolled correctly to `#help-support` but `helpJumpTo()` searched only `.help-section-hd`. Assistance uses `.help-feature-title`, so focus stayed on the source quick-navigation button.\n\nR2 changes only the target selector to `.help-section-hd, .help-feature-title`. Existing Help headings remain eligible, and the Assistance heading becomes focusable temporarily (`tabindex=-1`) through the existing focus-transfer logic.\n''',encoding='utf-8')

 writej(out/'metadata/active_report_inventory.json',{
   'version':VERSION,'build_revision':REV,'stage':STAGE,
   'active_documents':['README.md','REAL_DEVICE_QA_CHECKLIST.md','reports/V101138_R2_RELEASE_ACCESSIBILITY_CLEANUP.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md'],
   'active_test_artifacts':['REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'],'historical_reports_root':'reports/historical/',
   'rule':'Only listed active documents are current; predecessor/superseded reports and tooling are historical within original scope.'})
 writej(out/'metadata/build_provenance.json',{
   'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,
   'baseline_version':'v101.138 R1','baseline_zip_sha256':R1_ZIP_SHA,
   'observed_live_predecessor':'v101.137 R2','observed_live_predecessor_exact_package_sha256':OBSERVED_LIVE_R2_ZIP_SHA,
   'observed_live_predecessor_exact_byte_binding':'EXTERNAL_GATE_OPEN',
   'content_predecessor':'v101.137 R1','content_predecessor_sha256':CONTENT_R1_SHA,
   'inherited_authorized_ledger_sha256':LEDGER_SHA,'immutable_v101136_r5_sha256':R5_SHA,
   'canonical_corpus_changes_v101137_r2_to_v101138_r2':0,
   'text_library_changes_v101137_r2_to_v101138_r2':0,
   'stable_id_changes_v101137_r2_to_v101138_r2':0,
   'protected_declaration_changes_v101137_r2_to_v101138_r2':0,
   'evidence_v101137_r1_changes_v101137_r2_to_v101138_r2':0,
   'evidence_v101137_r2_changes_v101137_r2_to_v101138_r2':0,
   'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,
   'corpus_fingerprint_sha256':CORPUS_FP,
   'user_facing_scope':'Help quick-navigation focus repair only; release/provenance evidence cleanup',
   'final_validation':'EXTERNAL_EXACT_ZIP_RECHECK_REQUIRED'})
 writej(out/'metadata/current_evidence_lineage.json',{
   'version':VERSION,'build_revision':REV,'stage':STAGE,'current_evidence_root':'evidence/v101138_r2',
   'immediate_build_predecessor':{'version':'v101.138 R1','sha256':R1_ZIP_SHA},
   'observed_live_predecessor':{'version':'v101.137 R2','immutable_builder_input_sha256':OBSERVED_LIVE_R2_ZIP_SHA,'live_origin_exact_byte_binding':'EXTERNAL_GATE_OPEN'},
   'content_authority_evidence_root':'evidence/v101137_r1','provenance_evidence_root':'evidence/v101137_r2','ui_predecessor_evidence_root':'evidence/v101138_r1',
   'content_predecessor_24h':{'version':'v101.137 R1','sha256':CONTENT_R1_SHA},'inherited_authorized_ledger_sha256':LEDGER_SHA,
   'preserve_move_visibility':'EVIDENCE_ONLY_NOT_UI'})
 writej(out/'metadata/current_gate_map.json',{
   'version':VERSION,'build_revision':REV,'stage':STAGE,
   'internal_gates':['exact R1 SHA binding','R1→R2 file-diff scope','protected declarations byte-identical','CORPUS/TEXT_LIBRARY byte-identical','stable IDs/order identical','corpus fingerprint identical','v101137 R1/R2 and v101138 R1 evidence identical','Assistance quick-nav focus selector repaired','approved About textual provenance unchanged','support payload revision identity','HTML mirror identity','JS syntax','responsive Help layout','deterministic rebuild','exact ZIP reopen integrity'],
   'external_open_gates':gates,'public_release':'UNAUTHORIZED'})
 writej(out/'metadata/release_evidence_lifecycle.json',{
   'version':VERSION,'build_revision':REV,'stage':STAGE,
   'package_rule':'Package does not self-certify final ZIP bytes; exact frozen v101.138 R2 ZIP must receive an external SHA-bound final validation receipt.',
   'immediate_build_predecessor':'v101.138 R1','immediate_build_predecessor_sha256':R1_ZIP_SHA,
   'observed_live_predecessor':'v101.137 R2','observed_live_predecessor_exact_package_sha256':OBSERVED_LIVE_R2_ZIP_SHA,
   'live_origin_exact_byte_binding':'EXTERNAL_GATE_OPEN','content_predecessor':'v101.137 R1','content_predecessor_sha256':CONTENT_R1_SHA,
   'canonical_content_changed':False,'preserve_move_visibility':'EVIDENCE_ONLY_NOT_UI','physical_device_claims':'NOT_TESTED','public_deployment_authorized':False})
 (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} Scope Authority\n\nv101.138 R2 is authorized only for the four agreed release/accessibility cleanup items from the continuation package. Immediate immutable build predecessor: v101.138 R1 SHA-256 `{R1_ZIP_SHA}`.\n\nv101.137 R2 was the observed live predecessor; exact package SHA-256 `{OBSERVED_LIVE_R2_ZIP_SHA}` was the immutable R1 builder input. Live-origin exact-byte binding remains an external gate.\n\nForbidden: any CORPUS/TEXT_LIBRARY/stable-ID/order/presentation-topology/storage/personal-data/source-critical change; any change to the 79-row authority, H23/H24 governance, PRESERVE_MOVE visibility, or approved substantive À propos textual-provenance wording.\n\nAllowed: Help quick-navigation focus selector repair, lineage-accurate provenance-key names, precise observed-live/builder-input wording, v101.138 R2 build/cache identity, and corresponding release evidence.\n''',encoding='utf-8')
 writej(out/'metadata/current_tooling_inventory.json',{
   'version':VERSION,'build_revision':REV,'stage':STAGE,'current_builder':'scripts/build_v101138_r2_release_accessibility_cleanup.py',
   'builder_contract':'Exact SHA-bound v101.138 R1 predecessor; four-item agreed release/accessibility cleanup only; protected corpus declarations and predecessor evidence remain byte-identical.'})
 writej(out/'metadata/builder_input_manifest.json',{
   'version':VERSION,'build_revision':REV,'predecessor_v101138_r1_zip_sha256':R1_ZIP_SHA,
   'observed_live_v101137_r2_immutable_builder_input_sha256':OBSERVED_LIVE_R2_ZIP_SHA,
   'live_origin_exact_byte_binding':'EXTERNAL_GATE_OPEN','content_predecessor_v101137_r1_sha256':CONTENT_R1_SHA,
   'inherited_authorized_ledger_sha256':LEDGER_SHA,'immutable_v101136_r5_sha256':R5_SHA})
 shutil.copy2(Path(__file__),out/'scripts/build_v101138_r2_release_accessibility_cleanup.py')

 # Deep invariants before writing manifests.
 r2=(out/'index.html').read_text(encoding='utf-8')
 assert r2==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 protected_after={n:sha_bytes(raw_const(r2,n)[0].encode()) for n in PROTECTED}
 assert protected_after==protected_before
 corpus_after=raw_const(r2,'CORPUS')[1]; textlib_after=raw_const(r2,'TEXT_LIBRARY')[1]
 assert raw_const(r2,'CORPUS')[0]==raw_const(r1,'CORPUS')[0]
 assert raw_const(r2,'TEXT_LIBRARY')[0]==raw_const(r1,'TEXT_LIBRARY')[0]
 assert corpus_after['fingerprint_sha256']==CORPUS_FP
 ids_after={'CORPUS':collect_ids(corpus_after),'TEXT_LIBRARY':collect_ids(textlib_after)}
 assert ids_after==ids_before
 assert ev137r1=={k:sha_file(p) for k,p in files(out/'evidence/v101137_r1').items()}
 assert ev137r2=={k:sha_file(p) for k,p in files(out/'evidence/v101137_r2').items()}
 assert ev138r1=={k:sha_file(p) for k,p in files(out/'evidence/v101138_r1').items()}
 for t in ABOUT_TEXTS: assert r2.count(t)==1
 assert "const APP_VERSION = 'v101.138';" in r2 and "const BUILD_REVISION = 'R2';" in r2 and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in r2
 assert "target.querySelector('.help-section-hd, .help-feature-title')" in r2
 assert r2.count("target.querySelector('.help-section-hd, .help-feature-title')")==1
 assert CACHE in (out/'sw.js').read_text(encoding='utf-8')
 assert json.loads((out/'version.json').read_text(encoding='utf-8'))['build_revision']==REV
 assert json.loads((out/'manifest.json').read_text(encoding='utf-8'))['build_revision']==REV
 bp=json.loads((out/'metadata/build_provenance.json').read_text(encoding='utf-8'))
 assert not any('_r2_to_r3' in k for k in bp)
 assert sum(bp[k] for k in bp if k.endswith('_v101137_r2_to_v101138_r2'))==0
 assert json.loads((out/'version.json').read_text(encoding='utf-8'))['storage_schema']==8
 assert json.loads((out/'version.json').read_text(encoding='utf-8'))['personal_snapshot']==5

 writej(ev/'R1_TO_R2_PROTECTED_PARITY_RECEIPT.json',{
   'schema':'L24H_V101138_R2_R1_PARITY_RECEIPT_V1','status':'PASS','r1_zip_sha256':R1_ZIP_SHA,
   'protected_declarations':{n:{'r1_sha256':protected_before[n],'r2_sha256':protected_after[n],'identical':True} for n in PROTECTED},
   'corpus_raw_sha256':protected_after['CORPUS'],'text_library_raw_sha256':protected_after['TEXT_LIBRARY'],
   'corpus_fingerprint_sha256':CORPUS_FP,'stable_id_sequences_identical':True,
   'v101137_r1_evidence_files_checked':len(ev137r1),'v101137_r1_evidence_byte_mismatches':0,
   'v101137_r2_evidence_files_checked':len(ev137r2),'v101137_r2_evidence_byte_mismatches':0,
   'v101138_r1_evidence_files_checked':len(ev138r1),'v101138_r1_evidence_byte_mismatches':0,
   'approved_about_textual_provenance_unchanged':True})
 writej(ev/'INTERNAL_BUILD_RECEIPT.json',{
   'schema':'L24H_V101138_R2_INTERNAL_BUILD_RECEIPT_V1','status':'PASS',
   'checks':{'r1_sha256_bound':R1_ZIP_SHA,'help_focus_selector_repaired':True,'canonical_corpus_changes':0,'text_library_changes':0,'stable_id_changes':0,'protected_declaration_changes':0,'v101137_r1_evidence_changes':0,'v101137_r2_evidence_changes':0,'v101138_r1_evidence_changes':0,'corpus_fingerprint_unchanged':True,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'approved_about_textual_provenance_unchanged':True,'html_mirror_identical':True,'stale_r2_to_r3_keys_remaining':0}})

 # Strict changed-path scope before manifest self-updates.
 cur=files(out)
 changed=sorted(k for k,p in cur.items() if k not in basehash or sha_file(p)!=basehash[k])
 removed=sorted(basepaths-set(cur))
 allowed_prefixes=('evidence/v101138_r2/','reports/historical/v101138_r1/')
 allowed_exact={
  'index.html','luisa_24_heures.html','sw.js','manifest.json','version.json','README.md','REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv',
  'reports/V101138_R2_RELEASE_ACCESSIBILITY_CLEANUP.md','scripts/build_v101138_r2_release_accessibility_cleanup.py',
  'metadata/active_report_inventory.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/current_gate_map.json','metadata/current_tooling_inventory.json','metadata/builder_input_manifest.json','metadata/release_evidence_lifecycle.json','metadata/scope_escalation_authority.md'
 }
 unexpected=[x for x in changed if x not in allowed_exact and not x.startswith(allowed_prefixes)]
 assert not unexpected,unexpected
 assert removed==['reports/V101138_R1_HELP_SUPPORT_ABOUT_LAYOUT.md'],removed

 # Manifests are release metadata and are expected to change.
 changed_for_overlay=sorted(set(changed)|{'metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json'})
 writej(out/'metadata/full_build_overlay_manifest.json',{
   'schema':'L24H_V101138_R2_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':'v101.138 R1','baseline_zip_sha256':R1_ZIP_SHA,
   'changed_or_added':changed_for_overlay,'removed':removed,'content_semantic_delta':'ZERO','ui_delta':'HELP_QUICK_NAV_FOCUS_ONLY','release_evidence_delta':'R2_REFRESH'})
 ex={'metadata/hash_manifest.json','metadata/package_manifest.json'}; lst=[]
 for k,p in sorted(files(out).items()):
  if k in ex: continue
  lst.append({'path':k,'size':p.stat().st_size,'sha256':sha_file(p)})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
 writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
 return {
  'version':VERSION,'revision':REV,'stage':STAGE,'files':len(files(out)),'corpus_fingerprint_sha256':CORPUS_FP,
  'protected_declarations_identical':len(PROTECTED),'stable_id_sequences_identical':True,
  'v101137_r1_evidence_files_identical':len(ev137r1),'v101137_r2_evidence_files_identical':len(ev137r2),'v101138_r1_evidence_files_identical':len(ev138r1),
  'cache':CACHE,'changed_paths_before_manifests':changed,'removed_paths':removed
 }

if __name__=='__main__':
 if len(sys.argv)!=4: raise SystemExit('Usage: build.py <v101138_R1.zip> <out_dir> <out.zip>')
 info=build(sys.argv[1],sys.argv[2]); sha=freeze(sys.argv[2],sys.argv[3]); info['zip_sha256']=sha; info['zip_size']=Path(sys.argv[3]).stat().st_size
 print(json.dumps(info,ensure_ascii=False,indent=2))
