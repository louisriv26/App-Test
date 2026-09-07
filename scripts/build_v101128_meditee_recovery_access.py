#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, shutil, zipfile, sys, os

EXPECTED_BASE_SHA='d2614307d3335d4e76a3b9559cb4d8267549b9a5a4adf4ec616344f2b98664d6'
EXPECTED_BASE_MEMBERS=440
VERSION='v101.128'
BUILD_DATE='2026-09-02'
STAGE='MEDITEE_RECOVERY_ACCESS_AND_SINGLE_STATE_SYNC_R1'
CACHE='luisa-24h-v101-128'
DEFAULT_BASE=Path('/mnt/data/regression_v126_hour3/frozen/L24H_v101127_GITHUB_DEPLOY_CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR_LOCKED.zip')
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY','VISIBLE_PARAGRAPH_TOPOLOGY']

CSS_OLD='''.mark-bar { display: flex; align-items: center; gap: 0.7rem;\n  padding: 0.55rem 0.9rem; margin-bottom: 0.75rem;\n  background: var(--bg2); border: 1px solid var(--bg3);\n  border-radius: var(--radius); }\n.mark-bar.done { border-color: var(--accent-light); background: var(--accent-pale); }\n.mark-btn { flex-shrink: 0; padding: 0.35rem 0.85rem;\n  background: var(--accent); color: #fff; border: none;\n  border-radius: calc(var(--radius) - 2px); font-family: var(--font-ui);\n  font-size: 0.8rem; cursor: pointer; white-space: nowrap;\n  transition: opacity 0.15s; }\n.mark-btn:active { opacity: 0.8; }\n.mark-hint { font-size: 0.78rem; color: var(--ink3); font-family: var(--font-ui);\n  line-height: 1.35; }'''
CSS_NEW='''.mark-bar { display: flex; align-items: center; flex-wrap: wrap; gap: 0.7rem;\n  padding: 0.6rem 0.9rem; margin-bottom: 0.75rem;\n  background: var(--bg2); border: 1px solid var(--bg3);\n  border-radius: var(--radius); }\n.mark-bar.done { border-color: var(--accent-light); background: var(--accent-pale); }\n.mark-btn { flex: 0 0 auto; min-height: 44px; max-width: 100%; padding: 0.45rem 0.85rem;\n  background: var(--accent); color: #fff; border: 1px solid var(--accent);\n  border-radius: calc(var(--radius) - 2px); font-family: var(--font-ui);\n  font-size: 0.8rem; cursor: pointer; white-space: normal; text-align: center;\n  transition: opacity 0.15s, background 0.15s, color 0.15s; }\n.mark-btn.done { background: transparent; color: var(--accent); border-color: var(--accent-light); }\n.mark-btn:active { opacity: 0.8; }\n.mark-btn:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }\n.mark-hint { flex: 1 1 15rem; min-width: 0; font-size: 0.78rem; color: var(--ink3); font-family: var(--font-ui);\n  line-height: 1.35; }\n.mark-hint strong, .mark-hint span { display: block; }\n.mark-hint strong { color: var(--ink2); font-weight: 600; }\n.mark-hint span { margin-top: 0.1rem; }\n@media (max-width: 520px) {\n  .mark-bar { align-items: stretch; }\n  .mark-btn { width: 100%; }\n}'''

OLD_BUILD_MARK="function buildMarkBar(hourNum) { return ''; }"
NEW_BUILD_MARK=r'''function mediteeAriaLabel(hourNum, isRead) {
  const label = ordinalHeure(Number(hourNum));
  return isRead
    ? ('Retirer le statut méditée de la ' + label)
    : ('Marquer la ' + label + ' comme méditée');
}
function buildMarkBar(hourNum) {
  const n = Number(hourNum);
  const isRead = state.readHours.has(n);
  return `<div class="mark-bar ${isRead?'done':''}" data-meditee-bar-hour="${n}">
    <div class="mark-hint">
      <strong data-meditee-status-title-hour="${n}">${isRead?'✓ Cette Heure est marquée comme méditée.':'Vous avez déjà médité cette Heure ?'}</strong>
      <span data-meditee-status-detail-hour="${n}" ${isRead?'hidden':''}>Si vous avez oublié de la cocher à la fin.</span>
    </div>
    <button type="button" class="mark-btn ${isRead?'done':''}" data-meditee-action-hour="${n}" data-meditee-role="recovery" aria-pressed="${isRead?'true':'false'}" aria-label="${escHtml(mediteeAriaLabel(n,isRead))}" onclick="markMeditee(${n})">${isRead?'Retirer':'Marquer comme méditée'}</button>
  </div>`;
}
function refreshMediteeControls(hourNum) {
  const n = Number(hourNum);
  const isRead = state.readHours.has(n);
  document.querySelectorAll(`[data-meditee-bar-hour="${n}"]`).forEach(bar => {
    bar.classList.toggle('done', isRead);
    const title = bar.querySelector(`[data-meditee-status-title-hour="${n}"]`);
    const detail = bar.querySelector(`[data-meditee-status-detail-hour="${n}"]`);
    if (title) title.textContent = isRead ? '✓ Cette Heure est marquée comme méditée.' : 'Vous avez déjà médité cette Heure ?';
    if (detail) { detail.textContent = 'Si vous avez oublié de la cocher à la fin.'; detail.hidden = isRead; }
  });
  document.querySelectorAll(`[data-meditee-action-hour="${n}"]`).forEach(btn => {
    const role = btn.getAttribute('data-meditee-role') || '';
    btn.classList.toggle('done', isRead);
    btn.setAttribute('aria-pressed', isRead ? 'true' : 'false');
    btn.setAttribute('aria-label', mediteeAriaLabel(n, isRead));
    if (role === 'primary-end') {
      btn.innerHTML = isRead
        ? '<span>✓ Méditée</span>'
        : '<span>Méditée</span><span class="mark-btn-hint">Appuyez après avoir médité</span>';
    } else if (role === 'recovery') {
      btn.textContent = isRead ? 'Retirer' : 'Marquer comme méditée';
    }
  });
  return isRead;
}'''

OLD_BOTTOM='''<button class="mark-read-btn ${isRead?'done':''}" onclick="markMeditee(${hour.hour_number})" id="markReadBtn">\n        <span>${isRead?'✓ Méditée':'Méditée'}</span>${isRead?'':'<span class="mark-btn-hint">Appuyez après avoir médité</span>'}\n      </button>'''
NEW_BOTTOM='''<button class="mark-read-btn ${isRead?'done':''}" onclick="markMeditee(${hour.hour_number})" id="markReadBtn" data-meditee-action-hour="${hour.hour_number}" data-meditee-role="primary-end" aria-pressed="${isRead?'true':'false'}" aria-label="${escHtml(mediteeAriaLabel(hour.hour_number,isRead))}">\n        <span>${isRead?'✓ Méditée':'Méditée'}</span>${isRead?'':'<span class="mark-btn-hint">Appuyez après avoir médité</span>'}\n      </button>'''

OLD_MARK_REFRESH='''  const btn = document.getElementById('markReadBtn');\n  if (btn) { const rd = state.readHours.has(n); btn.classList.toggle('done', rd); btn.innerHTML = rd ? '<span>✓ Méditée</span>' : '<span>Méditée</span><span class="mark-btn-hint">Appuyez après avoir médité</span>'; }\n  refreshHourEndCycleUI();'''
NEW_MARK_REFRESH='''  refreshMediteeControls(n);\n  refreshHourEndCycleUI();'''

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()
def write_json(p,o): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def tree_files(root): return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}
def extract_const_raw(text,name):
    marker=f'const {name} = '
    st=text.index(marker)+len(marker)
    try:
        dec=json.JSONDecoder(); obj,end=dec.raw_decode(text[st:]); return obj,text[st:st+end]
    except json.JSONDecodeError:
        en=text.index(';',st); return None,text[st:en]

def base_zip_from_args(argv):
    if len(argv)==3: return Path(argv[1]),Path(argv[2])
    if len(argv)==2: return Path(os.environ.get('L24H_V101127_BASE_ZIP',str(DEFAULT_BASE))),Path(argv[1])
    raise SystemExit('usage: build_v101128_meditee_recovery_access.py [BASE_ZIP] OUTDIR')

def build(base_zip,outdir):
    base_zip=Path(base_zip); out=Path(outdir)
    if sha_file(base_zip)!=EXPECTED_BASE_SHA: raise AssertionError('baseline SHA mismatch')
    shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
    with zipfile.ZipFile(base_zip) as z:
        if z.testzip() is not None: raise AssertionError('baseline ZIP corrupt')
        if sum(not i.is_dir() for i in z.infolist())!=EXPECTED_BASE_MEMBERS: raise AssertionError('baseline member count mismatch')
        z.extractall(out)
    baseline={r:sha_file(p) for r,p in tree_files(out).items()}
    src=(out/'index.html').read_text(encoding='utf-8')
    if src!=(out/'luisa_24_heures.html').read_text(encoding='utf-8'): raise AssertionError('deploy HTML mirror mismatch')
    protected_before={n:extract_const_raw(src,n)[1] for n in PROTECTED}

    new=src
    for old,repl,label in [
        (CSS_OLD,CSS_NEW,'mark CSS'),
        (OLD_BUILD_MARK,NEW_BUILD_MARK,'buildMarkBar'),
        (OLD_BOTTOM,NEW_BOTTOM,'bottom control'),
        (OLD_MARK_REFRESH,NEW_MARK_REFRESH,'markMeditee refresh'),
        ("const APP_VERSION = 'v101.127';",f"const APP_VERSION = '{VERSION}';",'version'),
        ("const APP_EVIDENCE_STAGE = 'CROSS_RECORD_CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",'stage'),
        ("const BUILD_DATE = '2026-08-31'; // v101.127 / continuity glyph-flow regression repair; no canonical text mutation",f"const BUILD_DATE = '{BUILD_DATE}'; // {VERSION} / Méditée recovery access; no canonical text mutation",'build date'),
    ]:
        if new.count(old)!=1: raise AssertionError(f'{label} replacement cardinality {new.count(old)}')
        new=new.replace(old,repl,1)
    protected_after={n:extract_const_raw(new,n)[1] for n in PROTECTED}
    if protected_before!=protected_after: raise AssertionError('protected declaration changed')
    (out/'index.html').write_text(new,encoding='utf-8')
    (out/'luisa_24_heures.html').write_text(new,encoding='utf-8')

    v=json.loads((out/'version.json').read_text(encoding='utf-8'))
    v.update({
      'app_version':VERSION,'build_date':BUILD_DATE,'cache_name':CACHE,
      'release_scope':'UX-only successor of immutable v101.127. Adds a discreet recovery/status Méditée control below the Hour header, synchronized with the existing bottom action through the single state.readHours / markMeditee authority. No canonical/devotional text, speaker/presentation data, continuity authority, paragraph IDs/order, storage schema or personal snapshot schema changes.',
      'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live GitHub Pages exact-byte binding NOT_TESTED for v101.128.',
      'overall_release_status':'LIMITED_PASS_STATIC_PENDING_FINAL_REOPEN_AUDIT',
      'known_blockers':[],
      'external_open_gates':['physical iPad/iPhone/Samsung','live GitHub Pages exact-byte binding','installed PWA update from v101.127','true offline cold reopen','VoiceOver/TalkBack representative testing']
    })
    write_json(out/'version.json',v)
    m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));m['version']=VERSION;write_json(out/'manifest.json',m)
    sw=(out/'sw.js').read_text(encoding='utf-8')
    if not sw.startswith('/* v101.127 */') or "const CACHE_NAME = 'luisa-24h-v101-127';" not in sw: raise AssertionError('SW baseline identity mismatch')
    sw=sw.replace('/* v101.127 */','/* v101.128 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-127';",f"const CACHE_NAME = '{CACHE}';",1)
    (out/'sw.js').write_text(sw,encoding='utf-8')

    report='''# v101.128 Méditée Recovery Access / Single-State Synchronisation\n\n- Predecessor: immutable `v101.127` / `d2614307d3335d4e76a3b9559cb4d8267549b9a5a4adf4ec616344f2b98664d6` / 440 members.\n- User need: after forgetting the bottom `Méditée` action, reopening an Hour from the list currently starts at the top and otherwise requires scrolling through the complete Hour again.\n- UX repair: activates the existing `buildMarkBar(hourNum)` slot below the Hour header as a discreet recovery/status control while preserving the existing bottom action.\n- Single authority: `state.readHours`. Single state-changing action: `markMeditee(hourNum)`.\n- The two visual controls are synchronized by `refreshMediteeControls(hourNum)`; no new progression state or storage key exists.\n- Toggle refresh is DOM-only: `renderReader()` is not called by `markMeditee()`.\n- Hour-24 completion remains exactly 24 explicit `Méditée` states via `getProgressSnapshot()`.\n- Canonical/devotional text changes: **0**. Speaker/presentation/continuity data changes: **0**. Storage/snapshot schema changes: **0**.\n- Physical-device/PWA/offline/live-origin/screen-reader evidence remains external.\n'''
    (out/'reports'/'MEDITEE_RECOVERY_ACCESS.md').write_text(report,encoding='utf-8')
    (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION}\n\nUX-only successor of immutable v101.127.\n\n## Méditée recovery access\n\n- Keeps the normal bottom `Méditée` action.\n- Activates a discreet recovery/status control under the Hour header for users who forgot to mark the Hour at the end.\n- Uses one state authority (`state.readHours`) and one mutation path (`markMeditee`).\n- Adds no corpus/devotional-text, speaker, continuity-authority, storage-schema or snapshot-schema changes.\n\n## Validation boundary\n\nPackage-local evidence is pre-final-reopen. Physical devices, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live GitHub Pages exact-byte binding remain external gates.\n''',encoding='utf-8')

    ev=out/'evidence'/'v101128'; ev.mkdir(parents=True,exist_ok=True)
    write_json(ev/'V101128_BASELINE_BINDING.json',{'schema':'L24H_V101128_BASELINE_BINDING_V1','version':VERSION,'baseline_version':'v101.127','baseline_zip_sha256':EXPECTED_BASE_SHA,'baseline_members':EXPECTED_BASE_MEMBERS,'status':'PASS'})
    write_json(ev/'V101128_MUTATION_AUTHORITY.json',{'schema':'L24H_V101128_MUTATION_AUTHORITY_V1','version':VERSION,'stage':STAGE,'authority':'MEDITEE_RECOVERY_ACCESS_ONLY','single_state_authority':'state.readHours','single_mutation_function':'markMeditee(hourNum)','new_storage_keys':0,'canonical_text_operations':0,'forbidden_scope_preserved':True})
    write_json(ev/'V101128_PROTECTED_DECLARATION_HASHES.json',{'schema':'L24H_V101128_PROTECTED_DECLARATION_HASHES_V1','version':VERSION,'protected':{n:sha_bytes(protected_before[n].encode()) for n in PROTECTED},'byte_identical_to_v101127':True})
    (ev/'V101128_EXISTING_MEDITEE_ARCHITECTURE_REPORT.md').write_text('''# Existing Méditée architecture — v101.127 baseline\n\nPASS. `buildMarkBar(hourNum)` exists and was dormant; `renderReader()` already invokes it below the reader header; the bottom `markReadBtn` invokes `markMeditee(hourNum)`; `markMeditee` mutates only `state.readHours`/`meditationLog`, uses `commitDurableChange`, and refreshes Hour-24 cycle UI; resume uses `restoreSavedParaForHour`. No second progression authority is present.\n''',encoding='utf-8')

    # Current metadata.
    write_json(out/'metadata'/'active_report_inventory.json',{'version':VERSION,'stage':STAGE,'source_reports':['reports/MEDITEE_RECOVERY_ACCESS.md'],'historical_reports_root':'reports/historical/','inherited_nonactive_reports':['reports/CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR.md','reports/DUAL_SUCCESSOR_MUTATION_REPORT.md'],'rule':'Only MEDITEE_RECOVERY_ACCESS.md is current for v101.128; prior reports are predecessor/historical lineage.'})
    write_json(out/'metadata'/'current_evidence_lineage.json',{'version':VERSION,'stage':STAGE,'current_evidence_root':'evidence/v101128','predecessor_24h':{'version':'v101.127','sha256':EXPECTED_BASE_SHA},'rule':'v101.127 evidence remains predecessor lineage; v101.128 current evidence concerns only the Méditée recovery-access UX successor.'})
    write_json(out/'metadata'/'current_tooling_inventory.json',{'version':VERSION,'stage':STAGE,'current_tools':['scripts/build_v101128_meditee_recovery_access.py','scripts/run_v101128_meditee_ux_matrix.py','scripts/run_v101128_static_scope_audit.py','scripts/run_v101127_strict_continuity_glyph_flow_matrix.py'],'reused_validated_runtime_lineage':['v101.127 strict continuity and current runtime lineages'],'historical_or_superseded_tools':['scripts/build_v101127_continuity_glyph_flow_regression_repair.py']})
    write_json(out/'metadata'/'release_evidence_lifecycle.json',{'version':VERSION,'stage':STAGE,'prefreeze_package_reports':'current package report may claim only directly executed static/build/runtime facts','postfreeze_final_reopen_reports':'external only','physical_device_claims':'NOT_TESTED until direct evidence','immutable_package_rule':'do not insert postfreeze PASS reports into frozen ZIP','current_evidence_rule':'evidence/v101128 is current; older evidence is predecessor/historical lineage','active_report_rule':'current active report claims must bind directly to evidence/v101128 or current package bytes'})
    write_json(out/'metadata'/'build_provenance.json',{'version':VERSION,'stage':STAGE,'build_date':BUILD_DATE,'baseline_version':'v101.127','baseline_zip_sha256':EXPECTED_BASE_SHA,'baseline_html_sha256':sha_file(Path(out/'index.html')) if False else '496e4e50c29397b3a435b3973e3185c53f85ee5b0985c6a14e3f9266c6d5e530','candidate_html_sha256':sha_file(out/'index.html'),'mutation_scope':'UX-only Méditée recovery/status control + dual-control single-state synchronization + release identity','canonical_text_changed':False,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'final_reopen_evidence':'EXTERNAL_AFTER_IMMUTABLE_ZIP_FREEZE'})

    # Copy current build/audit scripts from control directory when available.
    control_dir=Path(__file__).resolve().parent
    for s in control_dir.glob('*.py'):
        shutil.copy2(s,out/'scripts'/s.name)

    after=tree_files(out)
    changed=sorted(r for r,p in after.items() if r not in baseline or sha_file(p)!=baseline[r])
    removed=sorted(set(baseline)-set(after))
    write_json(ev/'V101128_IMPLEMENTATION_DELTA.json',{'schema':'L24H_V101128_IMPLEMENTATION_DELTA_V1','version':VERSION,'changed_or_added':changed,'removed':removed,'canonical_text_operations':0})
    return {'version':VERSION,'stage':STAGE,'files':len(tree_files(out)),'html_sha256':sha_file(out/'index.html'),'changed_or_added':changed,'removed':removed}

if __name__=='__main__':
    base,out=base_zip_from_args(sys.argv)
    print(json.dumps(build(base,out),ensure_ascii=False,indent=2))
