#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, shutil, zipfile, csv, os

BASE_ZIP=Path('/mnt/data/L24H_v101119_GITHUB_DEPLOY_QUOTED_SPAN_PRESENTATION_CLOSURE_R1_LOCKED.zip')
WORK=Path('/mnt/data/l24h_v101120_build')
BASE=WORK/'baseline'
CAND=WORK/'candidate'
HELP_TEMPLATE=Path('/mnt/data/help_stage/help_v101120_template.html')
VERSION='v101.120'
STAGE='HELP_INFORMATION_ARCHITECTURE_AND_ATTRIBUTION_CLARITY_R1'
CACHE='luisa-24h-v101-120'
BASE_SHA='012adf876ac2e7a97a4ba325b4a44c4cc05dea902530a21f96e80422495c859d'
BASE_HTML_SHA='afbebba6ebbc07375aa9cb5ef3edcd9ea0030dd988b72897aa231cd2e0ccb9af'
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_PROJECTION','SPEECH_PRESENTATION_ADJUDICATIONS']

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(p.read_bytes())
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8',newline='\n')
def extract_const(src,name):
    token='const '+name
    st=src.find(token)
    if st<0: raise RuntimeError(f'missing const {name}')
    eq=src.find('=',st)
    i=eq+1; depth=0; quote=None; esc=False
    while i<len(src):
        ch=src[i]
        if quote:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: quote=None
        else:
            if ch in "'\"`": quote=ch
            elif ch in '[{(': depth+=1
            elif ch in ']})': depth-=1
            elif ch==';' and depth==0: return src[st:i+1]
        i+=1
    raise RuntimeError(f'unterminated const {name}')

def replace_help(src,new_inner):
    marker='overlay.innerHTML = `'
    fun=src.index('function showHelp()')
    st=src.index(marker,fun)+len(marker)
    en=src.index('`;',st)
    return src[:st]+'\n'+new_inner.rstrip()+'\n  '+src[en:]

def mutate_html(src):
    x=src
    x=x.replace("const APP_VERSION = 'v101.119';", "const APP_VERSION = 'v101.120';",1)
    x=x.replace("const APP_EVIDENCE_STAGE = 'QUOTED_SPAN_PRESENTATION_CLOSURE_R1';", f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
    x=x.replace("const BUILD_DATE = '2026-08-25'; // v101.119 / quoted-span presentation closure R1", "const BUILD_DATE = '2026-08-25'; // v101.120 / help information architecture and attribution clarity R1",1)
    x=replace_help(x,HELP_TEMPLATE.read_text(encoding='utf-8'))
    return x

def verify_html_scope(base,cand):
    # Reverse the exact authorized mutations; result must equal baseline byte-for-byte.
    x=cand
    x=x.replace("const APP_VERSION = 'v101.120';", "const APP_VERSION = 'v101.119';",1)
    x=x.replace(f"const APP_EVIDENCE_STAGE = '{STAGE}';", "const APP_EVIDENCE_STAGE = 'QUOTED_SPAN_PRESENTATION_CLOSURE_R1';",1)
    x=x.replace("const BUILD_DATE = '2026-08-25'; // v101.120 / help information architecture and attribution clarity R1", "const BUILD_DATE = '2026-08-25'; // v101.119 / quoted-span presentation closure R1",1)
    marker='overlay.innerHTML = `'; f1=base.index('function showHelp()'); st1=base.index(marker,f1)+len(marker); en1=base.index('`;',st1)
    f2=x.index('function showHelp()'); st2=x.index(marker,f2)+len(marker); en2=x.index('`;',st2)
    x=x[:st2]+base[st1:en1]+x[en2:]
    return x==base

if WORK.exists(): shutil.rmtree(WORK)
WORK.mkdir(parents=True)
actual=sha_file(BASE_ZIP)
if actual!=BASE_SHA: raise SystemExit(f'BASE HASH FAIL {actual}')
with zipfile.ZipFile(BASE_ZIP) as z: z.extractall(BASE)
shutil.copytree(BASE,CAND)
base_html=(BASE/'index.html').read_text(encoding='utf-8')
if sha_bytes(base_html.encode())!=BASE_HTML_SHA: raise SystemExit('BASE HTML HASH FAIL')
if (BASE/'luisa_24_heures.html').read_bytes()!=(BASE/'index.html').read_bytes(): raise SystemExit('BASE ROOT HTML MISMATCH')
new_html=mutate_html(base_html)
if not verify_html_scope(base_html,new_html): raise SystemExit('HTML SCOPE REVERSE-DIFF FAIL')
write(CAND/'index.html',new_html); write(CAND/'luisa_24_heures.html',new_html)

# Protected declarations must remain byte-identical.
rows=[]
for name in PROTECTED:
    b=extract_const(base_html,name); c=extract_const(new_html,name)
    ok=b==c
    rows.append([name,'PASS' if ok else 'FAIL',sha_bytes(b.encode()),sha_bytes(c.encode())])
    if not ok: raise SystemExit(f'PROTECTED DECLARATION CHANGED: {name}')

# Release identity only.
sw=(CAND/'sw.js').read_text(encoding='utf-8')
sw=sw.replace('/* v101.119 */','/* v101.120 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-119';",f"const CACHE_NAME = '{CACHE}';",1)
write(CAND/'sw.js',sw)
manifest=json.loads((CAND/'manifest.json').read_text(encoding='utf-8')); manifest['version']=VERSION; write(CAND/'manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
ver=json.loads((CAND/'version.json').read_text(encoding='utf-8'))
ver.update({
 'app_version':VERSION,'cache_name':CACHE,
 'release_scope':'Help-only successor: practice-first information architecture; semantic speaker versus visual presentation continuity clarified; stale personal-highlight meaning and stable-link sharing documented; annotation duplication reduced. Corpus, speech/presentation data, topology, storage schema and reader logic unchanged.',
 'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA, true offline cold reopen, VoiceOver/TalkBack and live GitHub Pages exact-byte binding NOT_TESTED for v101.120.',
 'overall_release_status':'LIMITED_PASS_STATIC_IF_FINAL_REOPEN_AUDITS_PASS',
 'known_blockers':[],
 'external_open_gates':['physical iPad/iPhone/Samsung','help modal real-device readability/scroll','live GitHub Pages exact-byte binding','installed PWA update','true offline cold reopen','VoiceOver/TalkBack representative testing']
})
write(CAND/'version.json',json.dumps(ver,ensure_ascii=False,indent=2)+'\n')

write(CAND/'README.md',f'''# Les 24 Heures de la Passion — {VERSION}\n\nStage: `{STAGE}`\n\nImmutable baseline: v101.119 / `{BASE_SHA}`.\n\nThis successor changes **Aide content/information architecture and release identity only**. It makes devotional practice the first help task, consolidates annotation guidance, explains that “Passages à vérifier” concerns stale personal highlight anchors rather than corpus doubt, documents stable-link sharing, and clarifies the distinction between semantic Jésus/Père/Marie attribution and outer visual presentation continuity for nested quotations.\n\nProtected and byte-identical to v101.119 inside the app HTML: `CORPUS`, `TEXT_LIBRARY`, `HOUR_LINKED_TEXTS`, paragraph IDs/order, `SPEECH_DATA`, `SPEECH_PRESENTATION_PROJECTION`, `SPEECH_PRESENTATION_ADJUDICATIONS`, `DISPLAY_SEGMENTS`, `VISIBLE_PARAGRAPH_TOPOLOGY`, RA19B flow and all previously validated devotional text/reader behaviour.\n\nPhysical-device/live-origin gates remain external and NOT_TESTED.\n''')
write(CAND/'metadata/scope_escalation_authority.md',f'''# Scope authority — {VERSION}\n\nCurrent stage: `{STAGE}`.\n\nThe immutable v101.119 ZIP `{BASE_SHA}` is the executable baseline. Authorized app mutation is restricted to the `showHelp()` modal template plus required release identity (`APP_VERSION`, `APP_EVIDENCE_STAGE`, build comment, service-worker cache identity, manifest/version metadata). No corpus, speech data, presentation projection/adjudication, display segmentation, paragraph topology, storage schema, navigation, highlighting or reader logic mutation is authorized. Any such difference is a blocking failure.\n''')
write(CAND/'metadata/release_evidence_lifecycle.json',json.dumps({'version':VERSION,'prefreeze_evidence':'PACKAGED','final_reopen_evidence':'EXTERNAL_AFTER_ZIP_FREEZE','physical_device_evidence':'DEFERRED_UNTIL_STATIC_CLOSURE_PASS'},indent=2)+'\n')

# QA assets are current-facing, so update them rather than carrying stale version identity.
write(CAND/'REAL_DEVICE_QA_CHECKLIST.md',f'''# Real-device QA checklist — {VERSION}\n\nPackage under test must match the final locked ZIP SHA-256 and report `{VERSION}` in Aide.\n\n## Help modal\n- Open Aide from Accueil, Reader and Réglages; close it and confirm the previous screen/place is preserved.\n- Confirm “Comment pratiquer les 24 Heures” is the first quick action.\n- Confirm all nine quick actions jump to visible sections.\n- Confirm “Passages à vérifier” clearly refers to personal highlight placement, not doubtful Luisa text.\n- Confirm the direct-speech explanation distinguishes Jésus/Père/Marie attribution badges from visual dialogue continuity.\n- In a Reader, confirm Aide documents Réglages → Référence du passage → Partager / Copier le lien.\n- Confirm Aide scrolls to the final About information on iPhone, iPad portrait/landscape and Samsung.\n\n## Regression\n- Samsung: whole-paragraph highlighting, persistence and Mon Espace.\n- iPhone/iPad: exact selected-text highlighting and title highlighting.\n- Reader scroll/orientation, search, notes, Mon Espace, update/Actualiser.\n- Quoted-span presentation controls, including P053/P068 and nested P090.\n- Installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and exact live GitHub Pages byte binding.\n''')
write(CAND/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','device,profile,test_id,result,notes,package_sha256\n')
write(CAND/'scripts/EXECUTION_SPEC.md',f'''# Execution specification — {VERSION}\n\nStage: `{STAGE}`\n\nCycle: BASELINE FREEZE → HELP LEDGER → IMPLEMENT → EXACT REVERSE-DIFF → PROTECTED DECLARATION PARITY → JS/SW SYNTAX → HELP BROWSER MATRIX → BROAD RUNTIME MATRIX → EXHAUSTIVE PRESENTATION MATRIX → SW LOGIC → FOUR-PASS AUDIT → REPORT/EVIDENCE RECONCILIATION → MANIFESTS → DETERMINISTIC BUILD A/B → FRESH PRIMARY REOPEN AUDIT → SEPARATELY IMPLEMENTED INDEPENDENT REOPEN AUDIT → EXTERNAL DECISION LOCK.\n\nNo corpus/data/reader logic mutation is authorized. Physical-device/live-origin evidence remains external.\n''')
# Preserve executed build script inside package as historical/current tooling.
shutil.copy2(Path(__file__),CAND/'scripts/build_v101120_help_information_architecture.py')

# Reset current report/audit namespaces; historical evidence/* remains untouched.
shutil.rmtree(CAND/'reports',ignore_errors=True); (CAND/'reports').mkdir()
shutil.rmtree(CAND/'audit',ignore_errors=True); (CAND/'audit').mkdir()
E=CAND/'evidence/v101120'; E.mkdir(parents=True,exist_ok=True)
with (E/'HELP_MUTATION_LEDGER.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f); w.writerow(['item','baseline','successor','status','scope'])
    w.writerow(['HELP_STRUCTURE','14 sections / 46 rows / 9 quick links / ~1377 text words','12 sections / 36 rows / 9 quick links / ~1157 text words','PASS','showHelp template only'])
    w.writerow(['PRACTICE_PRIORITY','practice section 11/14; no quick action','practice section 1/12; first quick action','PASS','help wording/order'])
    w.writerow(['ATTRIBUTION_CLARITY','badges and visual presentation not distinguished','semantic badges/search distinguished from visual dialogue continuity','PASS','help wording'])
    w.writerow(['STALE_HIGHLIGHT_CLARITY','Passages à vérifier unexplained','explicitly personal-highlight anchor state, not corpus doubt','PASS','help wording'])
    w.writerow(['SHARING_GUIDANCE','sharing only incidental in privacy text','dedicated Partager/Copier le lien section','PASS','help wording'])
    w.writerow(['ANNOTATION_DUPLICATION','3 overlapping sections','1 consolidated section','PASS','help wording/order'])
with (CAND/'reports/protected_declaration_parity.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f); w.writerow(['declaration','status','baseline_sha256','candidate_sha256']); w.writerows(rows)

# Static help audit.
help_inner=HELP_TEMPLATE.read_text(encoding='utf-8')
quick_targets=re.findall(r"helpJumpTo\('([^']+)'\)",help_inner)
section_ids=set(re.findall(r'class="help-section" id="([^"]+)"',help_inner))
checks={
 'sections_12':len(section_ids)==12,
 'rows_36':help_inner.count('class="help-row"')==36,
 'quick_links_9':len(quick_targets)==9,
 'quick_targets_resolve':all(x in section_ids for x in quick_targets),
 'practice_first_quick':'Comment pratiquer les 24 Heures' in help_inner.split('help-quick-grid',1)[1].split('</button>',1)[0],
 'semantic_vs_visual_explained':'sans être attribuée' in help_inner and 'Badges Jésus / Père / Marie' in help_inner,
 'stale_highlight_not_corpus_doubt':'Cela ne signifie pas que le texte de Luisa est signalé comme douteux' in help_inner,
 'sharing_documented':'Référence du passage → Partager' in help_inner and '<strong>Copier le lien</strong>' in help_inner,
 'backup_before_import':'exporter votre sauvegarde actuelle avant une importation' in help_inner,
 'misleading_three_usages_removed':'Trois usages distincts' not in help_inner,
}
if not all(checks.values()): raise SystemExit('HELP STATIC AUDIT FAIL '+repr(checks))
write(E/'HELP_CONTENT_AUDIT.json',json.dumps({'version':VERSION,'stage':STAGE,'checks':checks,'summary':{'pass':sum(checks.values()),'fail':sum(not v for v in checks.values())}},ensure_ascii=False,indent=2)+'\n')
write(E/'HELP_CONTENT_AUDIT.md','# v101.120 Help content audit\n\n**Status: PASS (static pre-browser)**\n\n'+''.join(f'- {k}: PASS\n' for k in checks))
write(CAND/'metadata/build_provenance.json',json.dumps({'version':VERSION,'stage':STAGE,'build_date':'2026-08-25','baseline_version':'v101.119','baseline_role':'IMMUTABLE_BASELINE','baseline_zip_sha256':BASE_SHA,'baseline_html_sha256':BASE_HTML_SHA,'candidate_html_sha256':sha_bytes(new_html.encode()),'authorized_app_mutations':['showHelp modal template','APP_VERSION','APP_EVIDENCE_STAGE','BUILD_DATE comment','service-worker cache identity','release metadata'],'protected_declarations_unchanged':len(PROTECTED),'final_reopen_evidence':'EXTERNAL_AFTER_IMMUTABLE_ZIP_FREEZE'},indent=2)+'\n')
print(json.dumps({'status':'PREFREEZE_CANDIDATE_BUILT','version':VERSION,'candidate_html_sha256':sha_bytes(new_html.encode()),'protected':len(PROTECTED),'help_checks':sum(checks.values())},indent=2))
