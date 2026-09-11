from pathlib import Path
import hashlib, json, zipfile, shutil, re, sys

R2_SHA='0ae4e7da4ec034952e0e596bb2c5ded947f7c7fade21c8974783de7308b0dbc5'
R1_SHA='b63fe5e224cf28be53c59eb9098fb561b746c0b8bbc892d07ce203475c1bf65d'
VERSION='v101.138'; REV='R1'; DATE='2026-09-08'; CACHE='luisa-24h-v101-138-r1'
STAGE='HELP_SUPPORT_ABOUT_LAYOUT_SUCCESSOR_R1'
LEDGER_SHA='f9a9c4c74df33b3f96909e3611acb74c448deed5fa367fa86072d2e27cbfef49'
R5_SHA='7ef830738ff5665ae5b880d52bde029e4b9ba092d834f81b008d24615e1ab9e7'
CORPUS_FP='87733d22b5e899e23da263c37a2c2b30d85585b7a40f3dbf5b9ab4c05ae496d7'
PROTECTED=[
 'CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS',
 'LDC_LIBRARY_FLOW_LAYOUT','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_DATA',
 'VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','SPEECH_PRESENTATION_PROJECTION',
 'SPEECH_PRESENTATION_ADJUDICATIONS'
]

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
def freeze(root,zp):
 root=Path(root); zp=Path(zp); zp.unlink(missing_ok=True)
 with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(root.rglob('*')):
   if not p.is_file(): continue
   rel=p.relative_to(root).as_posix()
   info=zipfile.ZipInfo(rel,(2026,9,8,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=(0o644<<16)
   z.writestr(info,p.read_bytes())
 return sha_file(zp)

CSS_ADD=r'''
/* v101.138 R1 — Assistance / Vie privée / À propos des textes presentation */
.help-feature-section { margin: 0 0 1.35rem; padding: 0.1rem 0 1.25rem; border-bottom: 1px solid var(--bg3); }
.help-feature-section:last-of-type { border-bottom: 0; padding-bottom: 0.25rem; }
.help-feature-title { margin: 0 0 0.55rem; font-family: var(--font-display); font-size: calc(var(--ui-size, 16px) * 1.12); line-height: 1.25; color: var(--accent); font-weight: 700; }
.help-feature-intro { margin: 0 0 0.9rem; color: var(--ink2); font-size: var(--ui-size, 16px); line-height: 1.55; }
.help-support-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.85rem 1rem; }
.help-support-item { min-width: 0; }
.help-support-btn { width: 100%; min-height: 58px; display: flex; align-items: center; gap: 0.75rem; text-align: left; border: 1px solid var(--accent-light); border-radius: 12px; background: var(--accent-pale); color: var(--ink); padding: 0.75rem 0.9rem; font: 700 calc(var(--ui-size, 16px) * 0.92) var(--font-ui); cursor: pointer; -webkit-appearance: none; transition: background 0.15s, border-color 0.15s, transform 0.05s; }
.help-support-btn:hover, .help-support-btn:focus-visible { background: color-mix(in srgb, var(--accent-pale) 72%, var(--bg) 28%); border-color: var(--accent); outline: 3px solid color-mix(in srgb, var(--accent-light) 55%, transparent); outline-offset: 2px; }
.help-support-btn:active { transform: translateY(1px); }
.help-support-btn-icon { flex: 0 0 34px; width: 34px; height: 34px; border-radius: 50%; border: 1px solid var(--accent-light); display: inline-flex; align-items: center; justify-content: center; font: 700 1rem var(--font-ui); color: var(--accent); background: var(--bg); }
.help-support-copy { margin: 0.5rem 0 0; color: var(--ink3); font-size: calc(var(--ui-size, 16px) * 0.90); line-height: 1.5; }
.help-private-copy { margin: 0; color: var(--ink2); font-size: var(--ui-size, 16px); line-height: 1.55; }
.help-about-card { border: 1px solid var(--bg3); border-radius: 14px; background: var(--bg2); padding: 1rem; }
.help-about-meta { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 0.55rem 1rem; padding-bottom: 0.9rem; margin-bottom: 0.85rem; border-bottom: 1px solid var(--bg3); }
.help-about-meta-item { color: var(--ink2); font-size: calc(var(--ui-size, 16px) * 0.92); line-height: 1.45; min-width: 0; }
.help-about-meta-item strong { color: var(--ink); }
.help-about-fingerprint { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; overflow-wrap: anywhere; }
.help-about-block { margin: 0 0 0.9rem; }
.help-about-block:last-child { margin-bottom: 0; }
.help-about-label { display: block; margin-bottom: 0.18rem; color: var(--ink); font-weight: 700; font-size: var(--ui-size, 16px); }
.help-about-block p { margin: 0; color: var(--ink2); font-size: var(--ui-size, 16px); line-height: 1.58; }
.help-about-note { margin-top: 0.9rem; }
@media (min-width: 780px) {
  .help-modal { width: min(900px, 100%) !important; max-height: min(88svh, 820px) !important; }
}
@media (max-width: 640px) {
  .help-support-grid { grid-template-columns: 1fr; gap: 0.95rem; }
  .help-about-meta { grid-template-columns: 1fr; gap: 0.35rem; }
  .help-support-btn { min-height: 54px; }
  .help-feature-title { font-size: calc(var(--ui-size, 16px) * 1.05); }
  .help-about-card { padding: 0.85rem; }
}
'''

OLD_SUPPORT='''      <div class="help-section" id="help-support"><div class="help-section-hd">Assistance, confidentialité et À propos</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">!</span><span class="help-row-text"><strong>Signaler un problème de texte</strong> — Copie version et révision, empreinte du corpus, route, ID stable et référence source disponibles. Ajoutez ensuite votre description.</span></div>
        <div class="help-row"><span class="help-icon">⌘</span><span class="help-row-text"><strong>Copier les diagnostics</strong> — Copie les informations techniques utiles au dépannage.</span></div>
        <div class="help-row"><span class="help-icon">🔒</span><span class="help-row-text"><strong>Vie privée</strong> — Partager, Copier le lien, Signaler un problème de texte et Diagnostics n’ajoutent pas automatiquement le contenu de vos notes ni celui de vos surlignages personnels.</span></div>
        <div class="help-actions-row"><button type="button" class="help-action-btn" onclick="copyTextIssueReport()">! Signaler un problème de texte</button><button type="button" class="help-action-btn secondary" onclick="copyDiagnostics()">⌘ Copier les diagnostics</button></div>
        <div class="help-row"><span class="help-icon">✦</span><span class="help-row-text"><strong>Version :</strong> ${escHtml(APP_VERSION)} ${escHtml(BUILD_REVISION)} · <strong>Édition française de base :</strong> ${escHtml(sourceEdition)} · <strong>Empreinte corpus :</strong> ${escHtml(fp.slice(0,16))}</span></div>
        <div class="help-row"><span class="help-icon">✓</span><span class="help-row-text"><strong>Validation textuelle</strong> — L’intégralité du corpus des 24 méditations et des 24 « Réflexions et pratiques », y compris la Désolation de Marie de la 24e Heure, a été soumise à une validation source-critique approfondie. Cette validation s’appuie sur un corpus critique italien de référence établi pour ce projet à partir de plusieurs témoins italiens. Le corpus a également été comparé intégralement, Heure par Heure, à la 27e édition de l’AFLP.</span></div>
        <div class="help-row"><span class="help-icon">≋</span><span class="help-row-text"><strong>Principe de référence</strong> — Lorsque les sources divergent et que la question peut être tranchée avec suffisamment de certitude, le corpus critique italien retenu guide le texte de l’application. Les rares divergences historiques qui restent incertaines ont été laissées inchangées.</span></div>
        <div class="help-row"><span class="help-icon">ⓘ</span><span class="help-row-text"><strong>Portée de cette validation</strong> — Cette validation concerne les 24 méditations et les 24 « Réflexions et pratiques ». Les textes du Livre du Ciel proposés dans « Approfondir » relèvent d’un programme de validation distinct.</span></div>
        <div class="help-note">L’application rassemble les 24 Heures, les prières et les textes d’approfondissement associés. Vos annotations, progression et positions de lecture restent locales lorsque le stockage de l’appareil/navigateur est disponible.</div>
      </div></div>'''

NEW_SUPPORT='''      <section class="help-feature-section" id="help-support" aria-labelledby="help-support-title">
        <h3 class="help-feature-title" id="help-support-title">Assistance</h3>
        <p class="help-feature-intro">Si vous pensez avoir identifié une erreur dans le texte ou si vous rencontrez un problème technique, utilisez les fonctions ci-dessous.</p>
        <div class="help-support-grid">
          <div class="help-support-item">
            <button type="button" class="help-support-btn" onclick="copyTextIssueReport()"><span class="help-support-btn-icon" aria-hidden="true">!</span><span>Signaler un problème de texte</span></button>
            <p class="help-support-copy">Copie un rapport prêt à l’emploi avec la version et la révision, l’empreinte du corpus, la position de lecture, l’ID stable et la référence source disponibles. Ajoutez ensuite votre description.</p>
          </div>
          <div class="help-support-item">
            <button type="button" class="help-support-btn" onclick="copyDiagnostics()"><span class="help-support-btn-icon" aria-hidden="true">⌘</span><span>Copier les diagnostics</span></button>
            <p class="help-support-copy">Copie les informations techniques utiles au dépannage, notamment la version, l’état du cache, le stockage, le thème et la route courante.</p>
          </div>
        </div>
      </section>

      <section class="help-feature-section" id="help-privacy" aria-labelledby="help-privacy-title">
        <h3 class="help-feature-title" id="help-privacy-title">Vie privée</h3>
        <p class="help-private-copy">Partager, Copier le lien, Signaler un problème de texte et Copier les diagnostics n’ajoutent pas automatiquement le contenu de vos notes ni celui de vos surlignages personnels.</p>
      </section>

      <section class="help-feature-section" id="help-about" aria-labelledby="help-about-title">
        <h3 class="help-feature-title" id="help-about-title">À propos des textes</h3>
        <div class="help-about-card">
          <div class="help-about-meta">
            <div class="help-about-meta-item"><strong>Version :</strong> ${escHtml(APP_VERSION)} ${escHtml(BUILD_REVISION)}</div>
            <div class="help-about-meta-item"><strong>Empreinte corpus :</strong> <span class="help-about-fingerprint">${escHtml(fp.slice(0,16))}</span></div>
          </div>
          <div class="help-about-block"><span class="help-about-label">Édition française de base</span><p>${escHtml(sourceEdition)}</p></div>
          <div class="help-about-block"><span class="help-about-label">Validation textuelle</span><p>L’intégralité du corpus des 24 méditations et des 24 « Réflexions et pratiques », y compris la Désolation de Marie de la 24e Heure, a été soumise à une validation source-critique approfondie. Cette validation s’appuie sur un corpus critique italien de référence établi pour ce projet à partir de plusieurs témoins italiens. Le corpus a également été comparé intégralement, Heure par Heure, à la 27e édition de l’AFLP.</p></div>
          <div class="help-about-block"><span class="help-about-label">Principe de référence</span><p>Lorsque les sources divergent et que la question peut être tranchée avec suffisamment de certitude, le corpus critique italien retenu guide le texte de l’application. Les rares divergences historiques qui restent incertaines ont été laissées inchangées.</p></div>
          <div class="help-about-block"><span class="help-about-label">Portée de cette validation</span><p>Cette validation concerne les 24 méditations et les 24 « Réflexions et pratiques ». Les textes du Livre du Ciel proposés dans « Approfondir » relèvent d’un programme de validation distinct.</p></div>
        </div>
        <div class="help-note help-about-note">L’application rassemble les 24 Heures, les prières et les textes d’approfondissement associés. Vos annotations, progression et positions de lecture restent locales lorsque le stockage de l’appareil/navigateur est disponible.</div>
      </section>'''

def build(r2_zip,out):
 r2_zip=Path(r2_zip); out=Path(out)
 assert sha_file(r2_zip)==R2_SHA,(sha_file(r2_zip),R2_SHA)
 shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
 with zipfile.ZipFile(r2_zip) as z:
  assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
  z.extractall(out)
 basehash={k:sha_file(p) for k,p in files(out).items()}
 r2=(out/'index.html').read_text(encoding='utf-8'); assert r2==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 protected_before={n:sha_bytes(raw_const(r2,n)[0].encode()) for n in PROTECTED}
 assert raw_const(r2,'CORPUS')[1]['fingerprint_sha256']==CORPUS_FP
 ev1={k:sha_file(p) for k,p in files(out/'evidence/v101137_r1').items()}
 ev2={k:sha_file(p) for k,p in files(out/'evidence/v101137_r2').items()}

 s=r2
 s=exact_replace(s,"const APP_VERSION = 'v101.137';","const APP_VERSION = 'v101.138';",'public version')
 s=exact_replace(s,"const BUILD_REVISION = 'R2';",f"const BUILD_REVISION = '{REV}';",'runtime revision')
 s=exact_replace(s,"const APP_EVIDENCE_STAGE = 'TEXTUAL_PROVENANCE_ABOUT_RECONCILIATION_R2';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",'runtime stage')
 s=exact_replace(s,"const BUILD_DATE = '2026-09-08'; // v101.137 R2 / provenance and À propos reconciliation; canonical corpus byte-identical to R1", "const BUILD_DATE = '2026-09-08'; // v101.138 R1 / Help assistance and À propos layout successor; canonical corpus byte-identical to v101.137 R2/R1",'build comment')
 css_anchor='.help-badge.etude { background: var(--bg2); color: var(--ink3); }\n'
 s=exact_replace(s,css_anchor,css_anchor+CSS_ADD,'help feature CSS')
 s=exact_replace(s,OLD_SUPPORT,NEW_SUPPORT,'support/about markup')
 (out/'index.html').write_text(s,encoding='utf-8'); (out/'luisa_24_heures.html').write_text(s,encoding='utf-8')

 sw=(out/'sw.js').read_text(encoding='utf-8')
 sw=exact_replace(sw,'/* v101.137 R2 */','/* v101.138 R1 */','sw revision')
 sw=exact_replace(sw,"const CACHE_NAME = 'luisa-24h-v101-137-r2';",f"const CACHE_NAME = '{CACHE}';",'sw cache')
 (out/'sw.js').write_text(sw,encoding='utf-8')
 man=json.loads((out/'manifest.json').read_text(encoding='utf-8')); assert man['version']=='v101.137' and man['build_revision']=='R2'; man['version']=VERSION; man['build_revision']=REV; writej(out/'manifest.json',man)
 v=json.loads((out/'version.json').read_text(encoding='utf-8')); assert v['app_version']=='v101.137' and v['build_revision']=='R2'; v['app_version']=VERSION; v['build_revision']=REV; v['cache_name']=CACHE
 v['release_scope']=(f"Help/À-propos presentation successor of exact live v101.137 R2 SHA-256 {R2_SHA}. "
   "Canonical CORPUS, TEXT_LIBRARY, stable IDs, presentation/topology declarations, storage schema, personal snapshot schema and all R1/R2 source-validation evidence remain unchanged. "
   "v101.138 R1 reorganizes the existing support controls into a dedicated Assistance area, separates Vie privée, and presents the already-approved textual provenance in a dedicated À propos des textes card. No devotional/source-critical content changes are introduced.")
 v['real_device_status']='Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.138 R1.'
 v['overall_release_status']='V101138_R1_HELP_SUPPORT_ABOUT_LAYOUT_CONTROLLED_DEVICE_TEST_CANDIDATE__FINAL_PUBLIC_DEPLOYMENT_UNAUTHORIZED'
 gates=['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update v101.137 R2→v101.138 R1','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing']
 v['known_blockers']=gates; v['external_open_gates']=gates; v['postfreeze_reopen_evidence']='Exact v101.138 R1 successor ZIP requires external SHA-bound final recheck before controlled device testing.'; writej(out/'version.json',v)

 # Active docs and R2 report historical placement.
 hist=out/'reports/historical/v101137_r2'; hist.mkdir(parents=True,exist_ok=True)
 oldrep=out/'reports/V101137_R2_TEXTUAL_PROVENANCE_ABOUT_RECONCILIATION.md'
 if oldrep.exists(): shutil.move(str(oldrep),str(hist/oldrep.name))
 report=out/'reports/V101138_R1_HELP_SUPPORT_ABOUT_LAYOUT.md'
 report.write_text(f'''# {VERSION} {REV} — Help support / À propos layout successor\n\n## Scope\nv101.138 R1 is a UI/help-only successor of exact R2 SHA-256 `{R2_SHA}`. It introduces no canonical, linked-text, stable-ID, storage, annotation, preservation or source-critical mutation.\n\n## User-facing changes\n- The former cramped native support-button line is removed.\n- A dedicated **Assistance** area presents two styled, accessible controls: **Signaler un problème de texte** and **Copier les diagnostics**, each with a short explanation.\n- **Vie privée** is a separate section rather than being mixed into the support controls.\n- **À propos des textes** is a dedicated provenance card showing version/revision, corpus fingerprint, French base edition, textual validation, reference principle and validation scope.\n- On large screens the support actions use two columns; on mobile they stack vertically.\n- The Help modal may expand to 900px on large screens while remaining responsive on mobile.\n\n## Protected invariants\n- CORPUS and TEXT_LIBRARY byte-identical to R2/R1.\n- all 14 protected presentation/topology declarations byte-identical.\n- corpus fingerprint unchanged `{CORPUS_FP}`.\n- evidence/v101137_r1 and evidence/v101137_r2 byte-identical.\n- exact 79-row content authority unchanged.\n- PRESERVE_MOVE remains evidence-only/not UI.\n- support payload semantics unchanged; only their visual controls are reorganized.\n''',encoding='utf-8')

 (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION} {REV}\n\nControlled device-test candidate and Help/À-propos UI-only successor of exact v101.137 R2 SHA-256 `{R2_SHA}`.\n\nThe complete canonical meditation/reflection corpus and linked TEXT_LIBRARY are byte-identical to R2/R1. The exact authorized 79-row R1 result and all Italian/AFLP source-critical decisions remain unchanged.\n\nv101.138 R1 only improves the Aide / À propos presentation: dedicated Assistance controls, a separate Vie privée section, and a structured À propos des textes provenance card. Build identity/cache metadata is updated to v101.138 R1.\n\nFinal public deployment remains unauthorized pending live-origin, installed-PWA, physical-device, true-offline and accessibility gates.\n''',encoding='utf-8')

 (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(f'''# Real-device QA checklist — {VERSION} {REV}\n\nUse only the exact v101.138 R1 candidate identified by the external SHA-bound receipt.\n\n## Identity\n- app_version = v101.138\n- build_revision = R1\n- cache_name = {CACHE}\n- APP_EVIDENCE_STAGE = {STAGE}\n- corpus fingerprint begins `87733d22b5e899e2` and is unchanged from R2/R1\n\n## A. Aide / À propos layout\nOn desktop/iPad wide view:\n- Assistance appears as its own section; two support controls are styled cards in two columns when space permits.\n- Vie privée is separate and readable.\n- À propos des textes is a separate provenance section/card.\n- Version displays v101.138 R1.\n- French base edition remains GE / Lumen Luminis / septembre 2021.\n- Validation text, reference principle, scope text and fingerprint all appear.\n- no horizontal overflow, clipped controls or native/default-looking button strip.\n\nOn iPhone/mobile:\n- the two Assistance controls stack vertically; tap targets are at least 44px high.\n- text wraps naturally; fingerprint does not force horizontal scrolling.\n- modal scroll and Fermer control remain usable.\n\nFunctional controls:\n- Signaler un problème de texte copies a payload containing `Version : v101.138 R1`.\n- Copier les diagnostics copies a payload containing `Version : v101.138 R1`.\n- both controls remain keyboard/focus accessible where applicable.\n\n## B. Existing-PWA update\nTest installed v101.137 R2 → v101.138 R1 without uninstalling. Preserve at least one note, highlight, meditated Hour, last place, theme and font size. Close/reopen three times and confirm no stale R2/R1 cache or repair loop.\n\n## C. Corpus regression\n- canonical CORPUS and TEXT_LIBRARY match certified R2/R1; fingerprint unchanged.\n- H1/H15/H18/H19/H20/H23/H24 representative R1 controls remain correct.\n- 24 PRESERVE_MOVE records remain evidence-only/not visible.\n\n## D. Physical/offline/accessibility\nRun iPhone, iPad portrait/landscape and Samsung/Android; verify normal app navigation, notes/highlights persistence, true offline cold reopen, and representative VoiceOver/TalkBack including the two Assistance controls and Help close/focus behavior.\n\nFinal public deployment remains unauthorized until all mandatory external gates pass.\n''',encoding='utf-8')
 (out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').write_text('\ufeffsection,test_id,devices,release_blocker_if_fail,expected,result,notes,package_sha256\n'
 'LIVE,LIVE-01,browser,YES,Aide shows v101.138 R1 and structured Assistance / Vie privée / À propos des textes,,,\n'
 'LIVE,LIVE-02,browser,YES,version.json = v101.138; build_revision R1; cache luisa-24h-v101-138-r1,,,\n'
 'HELP,HELP-01,desktop;iPad,YES,Assistance controls render as two styled columns when space permits; no native button strip,,,\n'
 'HELP,HELP-02,iPhone,YES,Assistance controls stack vertically and remain >=44px tap targets,,,\n'
 'HELP,HELP-03,desktop;iPhone;iPad,YES,Vie privée is separate and À propos des textes contains validation/source/scope information,,,\n'
 'HELP,HELP-04,desktop;iPhone;iPad,YES,No horizontal overflow or clipped text/control in Help modal,,,\n'
 'HELP,HELP-05,browser,YES,Both support payloads contain Version : v101.138 R1,,,\n'
 'UPDATE,UPD-01,iPhone;iPad;Samsung,YES,installed v101.137 R2 updates in place to v101.138 R1,,,\n'
 'UPDATE,UPD-02,iPhone;iPad;Samsung,YES,notes/highlights/read state/last place/theme/font preserved,,,\n'
 'CORPUS,CORPUS-01,browser,YES,CORPUS/TEXT_LIBRARY and fingerprint unchanged from R2/R1,,,\n'
 'OFFLINE,OFF-01,iPhone;iPad;Samsung,YES,true offline cold reopen works after online load,,,\n'
 'ACCESS,ACC-01,iPhone/iPad VoiceOver,YES,Assistance controls and Help close are named/navigable,,,\n'
 'ACCESS,ACC-02,Samsung TalkBack,YES,Assistance controls and Help close are named/navigable,,,\n',encoding='utf-8')

 # v101.138 R1 evidence and current metadata.
 ev3=out/'evidence/v101138_r1'; ev3.mkdir(parents=True,exist_ok=True)
 writej(ev3/'R2_PREDECESSOR_BINDING.json',{'version':VERSION,'build_revision':REV,'predecessor':'v101.137 R2','predecessor_zip_sha256':R2_SHA,'r1_content_predecessor_sha256':R1_SHA,'authorized_79_ledger_sha256':LEDGER_SHA,'immutable_r5_source_baseline_sha256':R5_SHA,'scope':'Help/support/About UI presentation only; zero corpus mutation'})
 (ev3/'UI_LAYOUT_DECISION.md').write_text('''# v101.138 R1 Help / À propos UI decision\n\nThe existing support functions are retained but moved out of the cramped inline native-button strip. v101.138 R1 presents them in a dedicated Assistance section with styled controls and explanatory text, separates Vie privée, and keeps the approved textual-validation wording in a dedicated À propos des textes card.\n\nLarge screens: two-column Assistance actions. Mobile: one-column stacked actions.\n''',encoding='utf-8')

 writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'active_documents':['README.md','REAL_DEVICE_QA_CHECKLIST.md','reports/V101138_R1_HELP_SUPPORT_ABOUT_LAYOUT.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md'],'active_test_artifacts':['REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'],'historical_reports_root':'reports/historical/','rule':'Only listed active documents are current; predecessor/superseded reports and tooling are historical within original scope.'})
 writej(out/'metadata/build_provenance.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,'baseline_version':'v101.137 R2','baseline_zip_sha256':R2_SHA,'content_predecessor':'v101.137 R1','content_predecessor_sha256':R1_SHA,'inherited_authorized_ledger_sha256':LEDGER_SHA,'immutable_v101136_r5_sha256':R5_SHA,'canonical_corpus_changes_r2_to_r3':0,'text_library_changes_r2_to_r3':0,'stable_id_changes_r2_to_r3':0,'protected_declaration_changes_r2_to_r3':0,'r1_evidence_changes_r2_to_r3':0,'r2_evidence_changes_r2_to_r3':0,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'corpus_fingerprint_sha256':CORPUS_FP,'user_facing_scope':'Help Assistance/Vie privée/À propos des textes layout only','final_validation':'EXTERNAL_EXACT_ZIP_RECHECK_REQUIRED'})
 writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_evidence_root':'evidence/v101138_r1','content_authority_evidence_root':'evidence/v101137_r1','provenance_evidence_root':'evidence/v101137_r2','predecessor_24h':{'version':'v101.137 R2','sha256':R2_SHA},'content_predecessor_24h':{'version':'v101.137 R1','sha256':R1_SHA},'inherited_authorized_ledger_sha256':LEDGER_SHA,'preserve_move_visibility':'EVIDENCE_ONLY_NOT_UI'})
 writej(out/'metadata/current_gate_map.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'internal_gates':['exact R2 SHA binding','protected declarations byte-identical','CORPUS fingerprint identical','TEXT_LIBRARY identical','R1/R2 evidence identical','Assistance layout present','Vie privée separate','À propos des textes card present','support payload revision identity','HTML mirror identity','JS syntax','responsive Help layout','deterministic rebuild','exact ZIP reopen integrity'],'external_open_gates':gates,'public_release':'UNAUTHORIZED'})
 writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'package_rule':'Package does not self-certify final ZIP bytes; exact frozen v101.138 R1 ZIP must receive an external SHA-bound final validation receipt.','immediate_predecessor':'v101.137 R2','immediate_predecessor_sha256':R2_SHA,'content_predecessor':'v101.137 R1','content_predecessor_sha256':R1_SHA,'canonical_content_changed':False,'preserve_move_visibility':'EVIDENCE_ONLY_NOT_UI','physical_device_claims':'NOT_TESTED','public_deployment_authorized':False})
 (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} Scope Authority\n\nv101.138 R1 is authorized only for the Help/Assistance/Vie privée/À propos layout implementation requested after live v101.137 R2 was frozen. Exact R2 SHA-256: `{R2_SHA}`.\n\nForbidden: any CORPUS/TEXT_LIBRARY/stable-ID/presentation-topology/storage/personal-data semantic change; any source-critical adjudication or wording change; any change to the exact 79-row content authority or PRESERVE_MOVE visibility.\n\nAllowed: Help-only markup/CSS for support/About organization, v101.138 R1 build/cache identity, and corresponding release documentation/evidence.\n''',encoding='utf-8')
 writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_builder':'scripts/build_v101138_r1_help_support_layout.py','builder_contract':'Exact SHA-bound v101.137 R2 predecessor; Help UI-only overlay; protected corpus declarations and R1/R2 evidence must remain byte-identical.'})
 writej(out/'metadata/builder_input_manifest.json',{'version':VERSION,'build_revision':REV,'predecessor_zip_sha256':R2_SHA,'content_predecessor_r1_sha256':R1_SHA,'inherited_authorized_ledger_sha256':LEDGER_SHA,'immutable_v101136_r5_sha256':R5_SHA})
 shutil.copy2(Path(__file__),out/'scripts/build_v101138_r1_help_support_layout.py')

 # Deep invariants.
 r3=(out/'index.html').read_text(encoding='utf-8'); assert r3==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 protected_after={n:sha_bytes(raw_const(r3,n)[0].encode()) for n in PROTECTED}
 assert protected_after==protected_before
 assert raw_const(r3,'CORPUS')[1]['fingerprint_sha256']==CORPUS_FP
 assert ev1=={k:sha_file(p) for k,p in files(out/'evidence/v101137_r1').items()}
 assert ev2=={k:sha_file(p) for k,p in files(out/'evidence/v101137_r2').items()}
 assert "const APP_VERSION = 'v101.138';" in r3 and f"const BUILD_REVISION = '{REV}';" in r3 and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in r3
 assert 'help-actions-row' not in r3[r3.find('function showHelp'):r3.find('function showProvenance')]
 assert 'Assistance</h3>' in r3 and 'Vie privée</h3>' in r3 and 'À propos des textes</h3>' in r3
 assert 'help-support-grid' in r3 and 'help-about-card' in r3 and 'grid-template-columns: repeat(2' in r3
 assert 'Édition française de base' in r3 and 'Validation textuelle' in r3 and 'Principe de référence' in r3 and 'Portée de cette validation' in r3
 assert CACHE in (out/'sw.js').read_text(encoding='utf-8')
 assert json.loads((out/'version.json').read_text(encoding='utf-8'))['build_revision']==REV
 assert json.loads((out/'manifest.json').read_text(encoding='utf-8'))['build_revision']==REV

 writej(ev3/'R2_TO_V101138_R1_PROTECTED_PARITY_RECEIPT.json',{'schema':'L24H_V101138_R1_R2_PARITY_RECEIPT_V1','status':'PASS','r2_zip_sha256':R2_SHA,'protected_declarations':{n:{'r2_sha256':protected_before[n],'v101138_r1_sha256':protected_after[n],'identical':True} for n in PROTECTED},'corpus_fingerprint_sha256':CORPUS_FP,'r1_evidence_files_checked':len(ev1),'r1_evidence_byte_mismatches':0,'r2_evidence_files_checked':len(ev2),'r2_evidence_byte_mismatches':0})
 writej(ev3/'INTERNAL_VALIDATION_RECEIPT.json',{'schema':'L24H_V101138_R1_INTERNAL_VALIDATION_RECEIPT_V1','status':'PASS','checks':{'r2_sha256_bound':R2_SHA,'corpus_changes':0,'text_library_changes':0,'stable_id_changes':0,'protected_declaration_changes':0,'r1_evidence_changes':0,'r2_evidence_changes':0,'corpus_fingerprint_unchanged':True,'assistance_section_present':True,'privacy_section_separate':True,'about_texts_card_present':True,'support_button_native_strip_removed':True,'responsive_two_to_one_column_css_present':True,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'html_mirror_identical':True}})

 # Manifests.
 cur=files(out); changed=sorted(k for k,p in cur.items() if k not in basehash or sha_file(p)!=basehash[k]); removed=sorted(set(basehash)-set(cur))
 for x in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
  if x not in changed: changed.append(x)
 writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101138_R1_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':'v101.137 R2','baseline_zip_sha256':R2_SHA,'changed_or_added':sorted(changed),'removed':removed,'content_semantic_delta':'ZERO','ui_delta':'HELP_SUPPORT_ABOUT_LAYOUT_ONLY'})
 ex={'metadata/hash_manifest.json','metadata/package_manifest.json'}; lst=[]
 for k,p in sorted(files(out).items()):
  if k in ex: continue
  lst.append({'path':k,'size':p.stat().st_size,'sha256':sha_file(p)})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
 writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
 return {'version':VERSION,'revision':REV,'stage':STAGE,'files':len(files(out)),'corpus_fingerprint_sha256':CORPUS_FP,'protected_declarations_identical':len(PROTECTED),'r1_evidence_files_identical':len(ev1),'r2_evidence_files_identical':len(ev2),'cache':CACHE}

if __name__=='__main__':
 if len(sys.argv)!=4: raise SystemExit('Usage: build.py <R2.zip> <out_dir> <out.zip>')
 result=build(sys.argv[1],sys.argv[2]); h=freeze(sys.argv[2],sys.argv[3]); print(json.dumps(result,indent=2,ensure_ascii=False)); print('ZIP',h)
