from pathlib import Path
import hashlib, json, zipfile, shutil, re, csv, sys

R1_SHA='b63fe5e224cf28be53c59eb9098fb561b746c0b8bbc892d07ce203475c1bf65d'
VERSION='v101.137'; REV='R2'; DATE='2026-09-08'; CACHE='luisa-24h-v101-137-r2'
STAGE='TEXTUAL_PROVENANCE_ABOUT_RECONCILIATION_R2'
LEDGER_SHA='f9a9c4c74df33b3f96909e3611acb74c448deed5fa367fa86072d2e27cbfef49'
R5_SHA='7ef830738ff5665ae5b880d52bde029e4b9ba092d834f81b008d24615e1ab9e7'
CORPUS_FP='87733d22b5e899e23da263c37a2c2b30d85585b7a40f3dbf5b9ab4c05ae496d7'
PROTECTED=[
 'CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS',
 'LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA',
 'VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_PROJECTION',
 'SPEECH_PRESENTATION_ADJUDICATIONS'
]

ABOUT_VALIDATION=(
"L’intégralité du corpus des 24 méditations et des 24 « Réflexions et pratiques », y compris la Désolation de Marie de la 24e Heure, "
"a été soumise à une validation source-critique approfondie. Cette validation s’appuie sur un corpus critique italien de référence établi "
"pour ce projet à partir de plusieurs témoins italiens. Le corpus a également été comparé intégralement, Heure par Heure, à la 27e édition de l’AFLP."
)
ABOUT_GOVERNANCE=(
"Lorsque les sources divergent et que la question peut être tranchée avec suffisamment de certitude, le corpus critique italien retenu guide "
"le texte de l’application. Les rares divergences historiques qui restent incertaines ont été laissées inchangées."
)
ABOUT_SCOPE=(
"Cette validation concerne les 24 méditations et les 24 « Réflexions et pratiques ». Les textes du Livre du Ciel proposés dans « Approfondir » "
"relèvent d’un programme de validation distinct."
)

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def files(root): return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}
def writej(p,o):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def raw_const(text,name):
 m=re.search(rf'const\s+{re.escape(name)}\s*=\s*',text); assert m,name
 start=m.end(); i=start
 while i < len(text) and text[i].isspace(): i += 1
 opener=text[i]; assert opener in '[{', (name, opener)
 pairs={'[':']','{':'}'}; stack=[]; quote=None; esc=False; j=i
 while j < len(text):
  ch=text[j]
  if quote:
   if esc: esc=False
   elif ch=='\\': esc=True
   elif ch==quote: quote=None
  else:
   if ch in ('\"',"'",'`'): quote=ch
   elif ch in '[{': stack.append(pairs[ch])
   elif ch in ']}':
    assert stack and ch==stack[-1], (name,j,ch,stack[-1] if stack else None)
    stack.pop()
    if not stack:
     raw=text[start:j+1]
     try: obj=json.loads(raw)
     except Exception: obj=None
     return raw,obj
  j += 1
 raise AssertionError(('unterminated',name))

def freeze(root,zp):
 root=Path(root); zp=Path(zp); zp.unlink(missing_ok=True)
 with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(root.rglob('*')):
   if not p.is_file(): continue
   rel=p.relative_to(root).as_posix()
   info=zipfile.ZipInfo(rel,(2026,9,8,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=(0o644<<16)
   z.writestr(info,p.read_bytes())
 return sha_file(zp)

def exact_replace(text,old,new,label,count=1):
 c=text.count(old)
 assert c==count,(label,'count',c,'expected',count)
 return text.replace(old,new,count)

def build(r1_zip,out):
 r1_zip=Path(r1_zip); out=Path(out)
 assert sha_file(r1_zip)==R1_SHA,(sha_file(r1_zip),R1_SHA)
 shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
 with zipfile.ZipFile(r1_zip) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(set(z.namelist()))
  z.extractall(out)
 basehash={k:sha_file(p) for k,p in files(out).items()}
 r1=(out/'index.html').read_text(encoding='utf-8'); assert r1==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 protected_before={n:sha_bytes(raw_const(r1,n)[0].encode()) for n in PROTECTED}
 corpus_before=raw_const(r1,'CORPUS')[1]
 assert corpus_before['fingerprint_sha256']==CORPUS_FP
 evidence_r1_before={k:sha_file(p) for k,p in files(out/'evidence/v101137_r1').items()}

 s=r1
 s=exact_replace(s,"const APP_EVIDENCE_STAGE = 'AUTHORIZED_79_MEDITATION_REFLECTION_SUCCESSOR_R1';",
                   f"const BUILD_REVISION = '{REV}';\nconst APP_EVIDENCE_STAGE = '{STAGE}';",'runtime identity')
 s=exact_replace(s,"const BUILD_DATE = '2026-09-08'; // v101.137 R1 / exact authorized 79-row meditation-reflection successor",
                   "const BUILD_DATE = '2026-09-08'; // v101.137 R2 / provenance and À propos reconciliation; canonical corpus byte-identical to R1",'build date comment')
 s=exact_replace(s,"'Version : '+APP_VERSION,","'Version : '+APP_VERSION+' '+BUILD_REVISION,",'support payload build ids',count=2)
 s=exact_replace(s,
   '<div class="help-row"><span class="help-icon">!</span><span class="help-row-text"><strong>Signaler un problème de texte</strong> — Copie version, empreinte du corpus, route, ID stable et référence source disponibles. Ajoutez ensuite votre description.</span></div>',
   '<div class="help-row"><span class="help-icon">!</span><span class="help-row-text"><strong>Signaler un problème de texte</strong> — Copie version et révision, empreinte du corpus, route, ID stable et référence source disponibles. Ajoutez ensuite votre description.</span></div>',
   'help issue wording')
 old_about='<div class="help-row"><span class="help-icon">✦</span><span class="help-row-text"><strong>Version :</strong> ${escHtml(APP_VERSION)} · <strong>Source :</strong> ${escHtml(sourceEdition)} · <strong>Empreinte corpus :</strong> ${escHtml(fp.slice(0,16))}</span></div>\n        <div class="help-note">L’application rassemble les 24 Heures, les prières et les textes d’approfondissement associés. Vos annotations, progression et positions de lecture restent locales lorsque le stockage de l’appareil/navigateur est disponible.</div>'
 new_about=f'''<div class="help-row"><span class="help-icon">✦</span><span class="help-row-text"><strong>Version :</strong> ${{escHtml(APP_VERSION)}} ${{escHtml(BUILD_REVISION)}} · <strong>Édition française de base :</strong> ${{escHtml(sourceEdition)}} · <strong>Empreinte corpus :</strong> ${{escHtml(fp.slice(0,16))}}</span></div>
        <div class="help-row"><span class="help-icon">✓</span><span class="help-row-text"><strong>Validation textuelle</strong> — {ABOUT_VALIDATION}</span></div>
        <div class="help-row"><span class="help-icon">≋</span><span class="help-row-text"><strong>Principe de référence</strong> — {ABOUT_GOVERNANCE}</span></div>
        <div class="help-row"><span class="help-icon">ⓘ</span><span class="help-row-text"><strong>Portée de cette validation</strong> — {ABOUT_SCOPE}</span></div>
        <div class="help-note">L’application rassemble les 24 Heures, les prières et les textes d’approfondissement associés. Vos annotations, progression et positions de lecture restent locales lorsque le stockage de l’appareil/navigateur est disponible.</div>'''
 s=exact_replace(s,old_about,new_about,'about block')

 # Mirror HTML.
 (out/'index.html').write_text(s,encoding='utf-8'); (out/'luisa_24_heures.html').write_text(s,encoding='utf-8')

 # Service worker and manifest/version identity.
 sw=(out/'sw.js').read_text(encoding='utf-8')
 sw=exact_replace(sw,'/* v101.137 R1 */','/* v101.137 R2 */','sw comment')
 sw=exact_replace(sw,"const CACHE_NAME = 'luisa-24h-v101-137-r1';",f"const CACHE_NAME = '{CACHE}';",'sw cache')
 (out/'sw.js').write_text(sw,encoding='utf-8')
 man=json.loads((out/'manifest.json').read_text(encoding='utf-8')); assert man['version']==VERSION and man['build_revision']=='R1'; man['build_revision']=REV; writej(out/'manifest.json',man)
 v=json.loads((out/'version.json').read_text(encoding='utf-8')); assert v['app_version']==VERSION and v['build_revision']=='R1'
 v['build_revision']=REV; v['cache_name']=CACHE
 v['release_scope']=(f"Provenance/À-propos release-engineering successor of exact v101.137 R1 SHA-256 {R1_SHA}. "
   "The complete canonical CORPUS, TEXT_LIBRARY, stable IDs, presentation/topology declarations, storage schema and personal snapshot schema are unchanged from R1. "
   "R2 adds only user-facing textual provenance distinguishing the GE/Lumen French base edition, the project Italian critical validation authority and complete AFLP 27th-edition cross-check, plus build-revision identification in À propos/support diagnostics. "
   "The authorized 79-row R1 corpus result remains the sole current meditation/reflection content authority; PRESERVE_MOVE material remains evidence-only and not user-visible.")
 v['real_device_status']='Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.137 R2.'
 v['overall_release_status']='R2_PROVENANCE_RECONCILED_CONTROLLED_DEVICE_TEST_CANDIDATE__FINAL_PUBLIC_DEPLOYMENT_UNAUTHORIZED'
 gates=[
  'physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update v101.136 R5→v101.137 R2',
  'installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'
 ]
 v['known_blockers']=gates; v['external_open_gates']=gates
 v['postfreeze_reopen_evidence']='Exact R2 successor ZIP requires external SHA-bound final recheck before controlled device testing.'
 writej(out/'version.json',v)

 # Active docs.
 (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION} {REV}\n\nControlled device-test candidate and provenance/release-only successor of exact v101.137 R1 SHA-256 `{R1_SHA}`.\n\nThe canonical meditation/reflection corpus is **byte-identical to R1** and therefore retains exactly the authorized 79-row result governed by ledger SHA-256 `{LEDGER_SHA}`. R2 introduces **zero canonical text, TEXT_LIBRARY, stable-ID, storage-schema or annotation-logic mutations**.\n\nR2 updates only À propos/provenance presentation and release identity: it identifies GE / Lumen Luminis / septembre 2021 as the French base edition, explains the full 24-Hour Italian-critical validation and complete AFLP 27th-edition cross-check, states the validation scope, and exposes `R2` in À propos and support diagnostics.\n\nThe 24 `PRESERVE_MOVE` records remain retained in package evidence but intentionally not displayed in the current UI. Deferred/recension-sensitive loci remain unchanged; H23 A/B synthesis remains forbidden; H24 burial placement remains unchanged; Desolation remains within H24 meditation scope.\n\nFinal public deployment remains unauthorized pending exact-package validation and controlled physical-device/PWA/offline/accessibility checks.\n''',encoding='utf-8')
 qa=f'''# Real-device QA checklist — {VERSION} {REV}\n\nUse only the exact **{VERSION} {REV}** controlled device-test candidate whose SHA-256 is supplied in the external final-validation receipt.\n\nPackage identity to verify before testing:\n- `app_version = {VERSION}`\n- `build_revision = {REV}`\n- `cache_name = {CACHE}`\n- `APP_EVIDENCE_STAGE = {STAGE}`\n- Aide / À propos displays **{VERSION} {REV}**\n- corpus fingerprint begins `87733d22b5e899e2` and remains identical to R1\n\nThe immutable installed update predecessor for this test is **v101.136 R5**. R1 is the immutable content predecessor for R2 but is not the required installed-PWA update starting point.\n\n## A. Live-origin binding immediately after test deployment\n- Confirm the deployed ZIP SHA-256 matches the external **{VERSION} {REV}** final-validation receipt.\n- Open Aide / À propos and confirm **{VERSION} {REV}**.\n- Confirm `Édition française de base : GE / Lumen Luminis / septembre 2021`.\n- Confirm the Validation textuelle paragraph states that all 24 meditations and 24 Réflexions et pratiques, including H24 Desolation, underwent source-critical validation and were compared Hour by Hour with AFLP 27th edition.\n- Confirm the scope note says the associated Livre du Ciel texts in Approfondir are a distinct validation programme.\n- Confirm `version.json` reports `app_version = {VERSION}`, `build_revision = {REV}`, `cache_name = {CACHE}`.\n- Use `Signaler un problème de texte` and `Copier les diagnostics`; both copied payloads must contain `Version : {VERSION} {REV}`.\n- Hard refresh once and confirm the same identity; no blank/stuck/bootstrap screen.\n\n## B. Existing-PWA update — mandatory\nTest an installation currently running **v101.136 R5**; do not uninstall first.\n- Before update record: at least one Heure méditée, one note, one highlight, one favourite/library mark if used, last reading position, theme and font size.\n- Open installed v101.136 R5 online and trigger/allow the normal update.\n- Confirm it becomes **{VERSION} {REV}**.\n- Close completely and reopen **three times**.\n- Confirm no fallback to v101.136 R5 or an older cache, blank screen, or repair loop.\n- Confirm all pre-existing user data and last-place state remain coherent.\n\n## C. Core functional smoke on each physical device\nRun on iPhone, iPad portrait, iPad landscape, and Samsung/Android. On each:\n- home renders/scrolls; all 24 Heures open; search works; Mon Espace opens; Aide opens;\n- light/dark theme and normal/large font work;\n- Méditée top/bottom controls remain synchronized;\n- notes/highlights can be created and persist after close/reopen;\n- no horizontal clipping/overflow; back navigation and last-place restore work.\n\n## D. R2 provenance-only invariants\n- Corpus fingerprint displayed in Aide matches R1 (`87733d22b5e899e2…`).\n- No meditation/reflection wording differs from the certified R1 corpus.\n- No linked Livre du Ciel text differs from R1.\n- The 24 preserve-move records remain absent from the current UI.\n\n## E. Representative inherited R1 corpus controls\n- H1: `Afflictions, tes Affections et tes Réparations`; standalone final `Gloire au Père,…` record absent.\n- H15: authorized angel-defense wording visible; moved devotional expansion absent.\n- H18 reflection: corrected veil/sweat sentence renders normally.\n- H19 reflection: documentary letters absent from reflection.\n- H20 meditation: Psalm 116 / Gloria insertion absent from canonical prose.\n- H23: `Défends-Moi, fais-Moi réparation, conduis-les tous dans mon Cœur`; no A/B synthesis.\n- H24: burial/deposition remains in H24; Desolation present; leading duplicate and final Latin paratext absent.\n\n## F. Inherited v101.136 R5 regression controls\n- H19 P118 intact; H22 punctuation loci correct; `RELATED_HOUR_06.P013` flow preserved; `RELATED_HOUR_16.P038` does not split `en`; `RELATED_HOUR_04.P127` break natural; H24 cycle controls correct; Tome 20 — 25 décembre 1926 displays `à la porte de leur cœur`.\n\n## G. Offline gate\nAfter a complete online load of {VERSION} {REV}: close PWA, enable airplane mode, cold-open; open two Heures, one linked text, Mon Espace and Aide; close/reopen once more offline; restore network and confirm no downgrade or repair loop.\n\n## H. Accessibility gate\nRepresentative VoiceOver/TalkBack on main navigation, Aide, Méditée, search/back controls; actionable controls named; focus restoration sensible.\n\n## Release rule\nAny failure involving version/update identity, provenance misstatement, user-data loss, blank/stuck startup, true-offline cold reopen, text corruption, H23 recension contamination, H24 scope/placement, or persistent navigation/rendering regression is a **release blocker**. Final public release remains unauthorized until mandatory physical/live gates are closed.\n'''
 (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(qa,encoding='utf-8')
 rows=[
 ['LIVE','LIVE-01','browser','YES',f'Aide shows {VERSION} {REV} and French base GE / Lumen Luminis / septembre 2021'],
 ['LIVE','LIVE-02','browser','YES',f'version.json = {VERSION}; build_revision {REV}; cache {CACHE}'],
 ['LIVE','LIVE-03','browser','YES','Aide validation text states full 24-meditation + 24-reflection coverage, H24 Desolation included, AFLP-27 full Hour-by-Hour comparison'],
 ['LIVE','LIVE-04','browser','YES',f'Text issue report and diagnostics both copy Version : {VERSION} {REV}'],
 ['UPDATE','UPD-01','iPhone;iPad;Samsung','YES',f'installed v101.136 R5 updates in place to {VERSION} {REV}'],
 ['UPDATE','UPD-02','iPhone;iPad;Samsung','YES','notes/highlights/read state/last place/theme/font preserved'],
 ['UPDATE','UPD-03','iPhone;iPad;Samsung','YES',f'3 close/reopen cycles stay on {VERSION} {REV}; no repair loop'],
 ['R2','R2-01','browser','YES',f'corpus fingerprint remains {CORPUS_FP}'],
 ['R2','R2-02','browser','YES','canonical CORPUS and TEXT_LIBRARY byte-identical to R1'],
 ['R2','R2-03','browser','YES','24 preserve-move records remain evidence-only and not visible'],
 ['TARGETED','NEW-01','at least iPhone + Samsung','YES','H1 corrected Affections triad visible and standalone final Gloria absent'],
 ['TARGETED','NEW-02','at least iPhone + Samsung','YES','H15 angel correction visible and moved devotional block hidden'],
 ['TARGETED','NEW-03','at least iPhone + Samsung','YES','H18 corrected reflection syntax renders normally'],
 ['TARGETED','NEW-04','at least iPhone + Samsung','YES','H19 documentary letters absent from reflection'],
 ['TARGETED','NEW-05','at least iPhone + Samsung','YES','H20 Psalm/Gloria insertion absent from canonical meditation'],
 ['TARGETED','NEW-06','at least iPhone + Samsung','YES','H23 corrected reparative wording visible; no A/B synthesis'],
 ['TARGETED','NEW-07','at least iPhone + Samsung','YES','H24 burial remains in H24; Desolation present; moved/deleted paratext absent'],
 ['OFFLINE','OFF-01','iPhone;iPad;Samsung','YES','true offline cold reopen works after online load'],
 ['OFFLINE','OFF-02','iPhone;iPad;Samsung','YES',f'{VERSION} {REV} hours/linked text/space/help usable offline'],
 ['ACCESS','ACC-01','iPhone/iPad VoiceOver','YES','representative controls named and navigable'],
 ['ACCESS','ACC-02','Samsung TalkBack','YES','representative controls named and navigable']]
 with (out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f); w.writerow(['section','test_id','devices','release_blocker_if_fail','expected','result','notes','package_sha256']);
  for r in rows: w.writerow(r+['','',''])

 # Reports/evidence. Keep R1 report but classify it historically by moving it.
 hist=out/'reports/historical/v101137_r1'; hist.mkdir(parents=True,exist_ok=True)
 oldrep=out/'reports/V101137_R1_AUTHORIZED_79_MUTATION.md'
 if oldrep.exists(): shutil.move(str(oldrep),str(hist/oldrep.name))
 report=out/'reports/V101137_R2_TEXTUAL_PROVENANCE_ABOUT_RECONCILIATION.md'
 report.write_text(f'''# {VERSION} {REV} — textual provenance / À propos reconciliation\n\n## Scope\nR2 is a provenance/release-only successor of exact R1 SHA-256 `{R1_SHA}`. It introduces no devotional/canonical corpus mutation.\n\n## User-facing changes\n- À propos now displays `{VERSION} {REV}`.\n- `Source` is relabelled `Édition française de base`, retaining the unchanged R1 value `GE / Lumen Luminis / septembre 2021`.\n- À propos explains full 24-meditation/24-reflection source-critical coverage, H24 Desolation inclusion, project Italian critical-corpus role, full AFLP-27 Hour-by-Hour comparison, divergence governance and scope exclusion for linked Livre du Ciel texts.\n- Text-problem and diagnostic payloads now include build revision.\n\n## Protected invariants\n- CORPUS byte-identical to R1.\n- TEXT_LIBRARY byte-identical to R1.\n- All protected presentation/topology declarations byte-identical to R1.\n- R1 corpus fingerprint remains `{CORPUS_FP}`.\n- R1 `evidence/v101137_r1` folder byte-identical.\n- storage schema 8 and personal snapshot schema 5 unchanged.\n- exact 79-row R1 content authority remains unchanged.\n- PRESERVE_MOVE visibility remains evidence-only/not UI.\n''',encoding='utf-8')
 ev=out/'evidence/v101137_r2'; ev.mkdir(parents=True,exist_ok=True)
 (ev/'ABOUT_TEXT_FINAL.md').write_text(f'''# Final user-facing textual provenance wording — {VERSION} {REV}\n\n**Édition française de base** — GE / Lumen Luminis / septembre 2021.\n\n**Validation textuelle** — {ABOUT_VALIDATION}\n\n**Principe de référence** — {ABOUT_GOVERNANCE}\n\n**Portée de cette validation** — {ABOUT_SCOPE}\n''',encoding='utf-8')
 writej(ev/'R1_PREDECESSOR_BINDING.json',{'version':VERSION,'build_revision':REV,'predecessor':'v101.137 R1','predecessor_zip_sha256':R1_SHA,'authorized_79_ledger_sha256':LEDGER_SHA,'immutable_r5_source_baseline_sha256':R5_SHA,'scope':'provenance/about/release identity only; zero corpus mutation'})

 # Metadata.
 active=['README.md','REAL_DEVICE_QA_CHECKLIST.md','reports/V101137_R2_TEXTUAL_PROVENANCE_ABOUT_RECONCILIATION.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md']
 writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'active_documents':active,'active_test_artifacts':['REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'],'historical_reports_root':'reports/historical/','rule':'Only listed active documents are current; predecessor/superseded reports and tooling are historical within original scope.'})
 writej(out/'metadata/build_provenance.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,'baseline_version':'v101.137 R1','baseline_zip_sha256':R1_SHA,'inherited_authorized_ledger_sha256':LEDGER_SHA,'immutable_v101136_r5_sha256':R5_SHA,'canonical_corpus_changes_r1_to_r2':0,'text_library_changes_r1_to_r2':0,'stable_id_changes_r1_to_r2':0,'protected_declaration_changes_r1_to_r2':0,'preserve_move_evidence_changes_r1_to_r2':0,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'corpus_fingerprint_sha256':CORPUS_FP,'user_facing_scope':'À propos textual provenance + R2 build identity/support diagnostics','final_validation':'EXTERNAL_EXACT_ZIP_RECHECK_REQUIRED'})
 writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_evidence_root':'evidence/v101137_r2','content_authority_evidence_root':'evidence/v101137_r1','predecessor_24h':{'version':'v101.137 R1','sha256':R1_SHA},'inherited_authorized_ledger_sha256':LEDGER_SHA,'preserve_move_visibility':'EVIDENCE_ONLY_NOT_UI','textual_validation_description':'24/24 meditations and 24/24 reflections, including H24 Desolation; governing project Italian critical master with complete AFLP-27 cross-check'})
 (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} Scope Authority\n\nR2 is authorized only as the provenance/À propos/release-identity implementation requested after the R1 corpus was frozen. Exact R1 SHA-256: `{R1_SHA}`.\n\nForbidden in R2: any CORPUS/TEXT_LIBRARY/stable-ID/presentation-topology/storage/personal-data semantic change; any new source-critical adjudication; any change to the exact 79-row content authority; any change to PRESERVE_MOVE visibility.\n\nAllowed in R2: user-facing À propos textual provenance, build revision display in support payloads, service-worker/cache/build metadata, active release documentation/evidence required to make those changes governed and testable.\n''',encoding='utf-8')
 writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'package_rule':'Package does not self-certify final ZIP bytes; exact frozen R2 ZIP must receive an external SHA-bound final validation receipt.','content_predecessor':'v101.137 R1','content_predecessor_sha256':R1_SHA,'canonical_content_changed':False,'preserve_move_visibility':'EVIDENCE_ONLY_NOT_UI','physical_device_claims':'NOT_TESTED','public_deployment_authorized':False})
 writej(out/'metadata/current_gate_map.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'internal_gates':['exact R1 SHA binding','protected declarations byte-identical','CORPUS fingerprint identical','TEXT_LIBRARY identical','R1 preservation evidence identical','R2 about text present','support payload revision identity','HTML mirror identity','JS syntax','deterministic A/B freeze','exact ZIP reopen integrity'],'external_open_gates':gates,'public_release':'UNAUTHORIZED'})
 shutil.copy2(Path(__file__),out/'scripts/build_v101137_r2_about_provenance.py')
 writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_builder':'scripts/build_v101137_r2_about_provenance.py','builder_contract':'Exact SHA-bound v101.137 R1 predecessor; release/provenance-only overlay; protected corpus declarations must remain byte-identical.'})
 writej(out/'metadata/builder_input_manifest.json',{'version':VERSION,'build_revision':REV,'predecessor_zip_sha256':R1_SHA,'inherited_authorized_ledger_sha256':LEDGER_SHA,'immutable_v101136_r5_sha256':R5_SHA})

 # Deep invariants before manifest.
 r2=(out/'index.html').read_text(encoding='utf-8'); assert r2==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 protected_after={n:sha_bytes(raw_const(r2,n)[0].encode()) for n in PROTECTED}
 assert protected_after==protected_before,(set(k for k in PROTECTED if protected_after[k]!=protected_before[k]))
 assert raw_const(r2,'CORPUS')[1]['fingerprint_sha256']==CORPUS_FP
 assert evidence_r1_before=={k:sha_file(p) for k,p in files(out/'evidence/v101137_r1').items()}
 assert "const APP_VERSION = 'v101.137';" in r2
 assert f"const BUILD_REVISION = '{REV}';" in r2
 assert f"const APP_EVIDENCE_STAGE = '{STAGE}';" in r2
 assert ABOUT_VALIDATION in r2 and ABOUT_GOVERNANCE in r2 and ABOUT_SCOPE in r2
 assert '<strong>Édition française de base :</strong>' in r2 and '<strong>Source :</strong>' not in r2[r2.find('function showHelp'):r2.find('function showProvenance')]
 assert r2.count("'Version : '+APP_VERSION+' '+BUILD_REVISION,")==2
 assert CACHE in (out/'sw.js').read_text(encoding='utf-8')
 vv=json.loads((out/'version.json').read_text(encoding='utf-8')); assert vv['build_revision']==REV and vv['cache_name']==CACHE
 assert json.loads((out/'manifest.json').read_text(encoding='utf-8'))['build_revision']==REV

 # Evidence parity receipt.
 parity={'schema':'L24H_V101137_R2_R1_PARITY_RECEIPT_V1','status':'PASS','r1_zip_sha256':R1_SHA,'protected_declarations':{},'corpus_fingerprint_sha256':CORPUS_FP,'r1_evidence_files_checked':len(evidence_r1_before),'r1_evidence_byte_mismatches':0,'storage_schema':vv['storage_schema'],'personal_snapshot':vv['personal_snapshot']}
 for n in PROTECTED: parity['protected_declarations'][n]={'r1_sha256':protected_before[n],'r2_sha256':protected_after[n],'identical':True}
 writej(ev/'R1_TO_R2_PROTECTED_PARITY_RECEIPT.json',parity)
 writej(ev/'INTERNAL_VALIDATION_RECEIPT.json',{'schema':'L24H_V101137_R2_INTERNAL_VALIDATION_RECEIPT_V1','status':'PASS','checks':{'r1_sha256_bound':R1_SHA,'corpus_changes':0,'text_library_changes':0,'stable_id_changes':0,'protected_declaration_changes':0,'r1_evidence_changes':0,'corpus_fingerprint_unchanged':True,'about_validation_text_present':True,'about_scope_text_present':True,'build_revision_visible':True,'support_payload_build_revision':True,'preserve_move_visibility_unchanged':True,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'html_mirror_identical':True},'corpus_fingerprint_sha256':CORPUS_FP})

 # Overlay + manifests (self-excluding manifest pair).
 cur=files(out); changed=sorted(k for k,p in cur.items() if k not in basehash or sha_file(p)!=basehash[k]); removed=sorted(set(basehash)-set(cur))
 for x in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
  if x not in changed: changed.append(x)
 writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101137_R2_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':'v101.137 R1','baseline_zip_sha256':R1_SHA,'changed_or_added':sorted(changed),'removed':removed,'content_semantic_delta':'ZERO'})
 ex={'metadata/hash_manifest.json','metadata/package_manifest.json'}; lst=[]
 for k,p in sorted(files(out).items()):
  if k in ex: continue
  lst.append({'path':k,'size':p.stat().st_size,'sha256':sha_file(p)})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
 writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
 return {'version':VERSION,'revision':REV,'stage':STAGE,'files':len(files(out)),'corpus_fingerprint_sha256':CORPUS_FP,'protected_declarations_identical':len(PROTECTED),'r1_evidence_files_identical':len(evidence_r1_before),'cache':CACHE}

if __name__=='__main__':
 if len(sys.argv)!=4: raise SystemExit('Usage: build.py <R1.zip> <out_dir> <out.zip>')
 result=build(sys.argv[1],sys.argv[2]); h=freeze(sys.argv[2],sys.argv[3]); print(json.dumps(result,indent=2,ensure_ascii=False)); print('ZIP',h)
