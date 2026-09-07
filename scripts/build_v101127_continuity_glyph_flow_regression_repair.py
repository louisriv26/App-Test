#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, shutil, zipfile, sys

BASE_ZIP=Path('/mnt/data/dual_successor_work/l24h_r5/frozen/L24H_v101126_GITHUB_DEPLOY_DUAL_SUCCESSOR_R5_34_AUTHORISED_MUTATIONS_LOCKED.zip')
EXPECTED_BASE_SHA='87d812e39b14148a640dfc8095a8d07b25ce37e056e815d66c286c94638a0d85'
EXPECTED_BASE_MEMBERS=434
VERSION='v101.127'
BUILD_DATE='2026-08-31'
STAGE='CROSS_RECORD_CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR_R1'
CACHE='luisa-24h-v101-127'

CSS_OLD='''.para-seg { display:block; }\n.para-seg + .para-seg { margin-top:0.9em; }'''
CSS_NEW='''.para-seg { display:block; }\n.para-seg + .para-seg { margin-top:0.9em; }\n/* v101.127 — true cross-record glyph-flow repair.\n   The continuity surface itself was already inline, but DISPLAY_SEGMENTS remained block-level.\n   For segmented continuity leaders (currently H03 P012 and H13 P011), that forced the follower\n   onto the next line. Keep all earlier internal segment boundaries/rhythm, but let the leader's\n   final segment and a segmented follower's first segment participate in the shared inline flow. */\n.continuity-flow-surface .continuity-leader .para-text > .para-seg:last-child {\n  display:inline!important;\n  margin-top:0!important;\n}\n.continuity-flow-surface .continuity-leader .para-text > .para-seg:nth-last-child(2) {\n  margin-bottom:0.9em;\n}\n.continuity-flow-surface .continuity-follower .para-text > .para-seg:first-child {\n  display:inline!important;\n  margin-top:0!important;\n}'''


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

def build(outdir):
    out=Path(outdir); shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
    assert sha_file(BASE_ZIP)==EXPECTED_BASE_SHA
    with zipfile.ZipFile(BASE_ZIP) as z:
        assert z.testzip() is None
        assert sum(not i.is_dir() for i in z.infolist())==EXPECTED_BASE_MEMBERS
        z.extractall(out)
    baseline_hashes={r:sha_file(p) for r,p in tree_files(out).items()}
    src=(out/'index.html').read_text(encoding='utf-8')
    assert src==(out/'luisa_24_heures.html').read_text(encoding='utf-8')

    # Preserve governed declarations exactly; this successor is presentation-only.
    protected=['CORPUS','TEXT_LIBRARY','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY']
    before={n:extract_const_raw(src,n)[1] for n in protected}

    assert src.count(CSS_OLD)==1
    new=src.replace(CSS_OLD,CSS_NEW,1)
    replacements=[
        ("const APP_VERSION = 'v101.126';",f"const APP_VERSION = '{VERSION}';"),
        ("const APP_EVIDENCE_STAGE = 'DUAL_SUCCESSOR_R5_15_LDC_SYNC_PLUS_19_NATIVE_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';"),
        ("const BUILD_DATE = '2026-08-31'; // v101.126 / governed 15 LDC synchronizations + 19 native repairs",f"const BUILD_DATE = '{BUILD_DATE}'; // {VERSION} / continuity glyph-flow regression repair; no canonical text mutation"),
    ]
    for a,b in replacements:
        assert new.count(a)==1,a
        new=new.replace(a,b,1)
    after={n:extract_const_raw(new,n)[1] for n in protected}
    assert before==after, [n for n in protected if before[n]!=after[n]]
    (out/'index.html').write_text(new,encoding='utf-8')
    (out/'luisa_24_heures.html').write_text(new,encoding='utf-8')

    # PWA/runtime identity only.
    v=json.loads((out/'version.json').read_text(encoding='utf-8'))
    v.update({
        'app_version':VERSION,'build_date':BUILD_DATE,'cache_name':CACHE,
        'release_scope':'Presentation-only successor of immutable v101.126. Repairs the cross-record continuity glyph-flow regression caused by block-level DISPLAY_SEGMENTS inside an otherwise inline continuity surface. No canonical/devotional text, paragraph IDs/order, continuity-group membership, DISPLAY_SEGMENTS offsets, speaker/presentation data, LDC-linked text, storage schema or personal snapshot schema changes.',
        'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live GitHub Pages exact-byte binding NOT_TESTED for v101.127.',
        'overall_release_status':'LIMITED_PASS_STATIC_PENDING_FINAL_REOPEN_AUDIT',
        'known_blockers':[],
        'external_open_gates':['physical iPad/iPhone/Samsung','live GitHub Pages exact-byte binding','installed PWA update','true offline cold reopen','VoiceOver/TalkBack representative testing']
    })
    write_json(out/'version.json',v)
    m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));m['version']=VERSION;write_json(out/'manifest.json',m)
    sw=(out/'sw.js').read_text(encoding='utf-8')
    assert sw.startswith('/* v101.126 */') and "const CACHE_NAME = 'luisa-24h-v101-126';" in sw
    sw=sw.replace('/* v101.126 */','/* v101.127 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-126';",f"const CACHE_NAME = '{CACHE}';",1)
    (out/'sw.js').write_text(sw,encoding='utf-8')

    # Current report/evidence.
    ev=out/'evidence'/'v101127'; ev.mkdir(parents=True,exist_ok=True)
    write_json(ev/'REGRESSION_ROOT_CAUSE.json',{
        'schema':'L24H_V101127_CONTINUITY_GLYPH_FLOW_ROOT_CAUSE_V1','version':VERSION,'stage':STAGE,
        'reported_case':{'leader':'PASSION24.HOUR.03.P012','follower':'PASSION24.HOUR.03.P013','visible_boundary':'peines, → afin que'},
        'root_cause':'continuity fragments and para-text were inline, but the leader final DISPLAY_SEGMENTS span remained display:block, forcing the follower onto a new line',
        'also_affected_by_same_mechanism':['PASSION24.HOUR.13.P011 → PASSION24.HOUR.13.P013'],
        'unaffected_pairs':['PASSION24.HOUR.15.P014 → PASSION24.HOUR.15.P015','PASSION24.HOUR.19.P183 → PASSION24.HOUR.19.P184','PASSION24.HOUR.19.P185 → PASSION24.HOUR.19.P186'],
        'prior_gate_blind_spot':'v101.124/v101.125 continuity test accepted dy <= one line-height, so a forced one-line displacement incorrectly passed',
        'repair':'last DISPLAY_SEGMENT of continuity leader becomes inline; previous segment receives equivalent margin-bottom rhythm; first segment of any segmented follower becomes inline',
        'canonical_text_changed':False
    })
    write_json(ev/'PRESENTATION_ONLY_SCOPE.json',{
        'schema':'L24H_V101127_PRESENTATION_ONLY_SCOPE_V1','version':VERSION,'stage':STAGE,
        'predecessor':{'version':'v101.126','zip_sha256':EXPECTED_BASE_SHA,'members':EXPECTED_BASE_MEMBERS},
        'inherited_textual_universe':'34 operations = 15 governed LDC sync + 19 native 24H/prayer; unchanged from v101.126',
        'new_textual_operations':0,
        'protected_declarations':protected,
        'protected_declarations_byte_identical':True,
        'storage_schema':8,'personal_snapshot':5
    })
    report=f'''# v101.127 Cross-Record Continuity Glyph-Flow Regression Repair\n\n- Predecessor: `v101.126` / `{EXPECTED_BASE_SHA}` / 434 members.\n- User-reported regression: Hour 3 visually broke after `peines,` before `afin que…`.\n- Root cause: `continuity-flow-fragment` and `.para-text` were inline, but the leader's final `.para-seg` from `DISPLAY_SEGMENTS` remained `display:block`, forcing a new line.\n- Same mechanism also affected the Hour 13 continuity pair. The Hour 15 and two Hour 19 pairs were not affected because their boundary records have no `DISPLAY_SEGMENTS`.\n- Repair is presentation-only: the final display segment of a continuity leader participates in the shared inline flow; the earlier internal segment rhythm is preserved by shifting the existing 0.9em break spacing to the preceding block segment.\n- Canonical/devotional text changes in v101.127: **0**.\n- The inherited governed textual universe remains **34 = 15 LDC-governed synchronizations + 19 native 24H/prayer repairs**.\n- `CORPUS`, `TEXT_LIBRARY`, `SPEECH_DATA`, presentation projection/adjudications, visible topology, `DISPLAY_SEGMENTS`, `CONTINUITY_GROUPS`, LDC flow and LDC sync authority are byte-identical declarations to v101.126.\n- Storage schema remains 8 and personal snapshot schema remains 5.\n- Package-local status remains pre-final-reopen; post-freeze reopen/device evidence is external by design.\n'''
    (out/'reports'/'CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR.md').write_text(report,encoding='utf-8')
    write_json(out/'metadata'/'active_report_inventory.json',{
        'version':VERSION,'stage':STAGE,'source_reports':['reports/CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR.md'],
        'historical_reports_root':'reports/historical/','inherited_nonactive_report':'reports/DUAL_SUCCESSOR_MUTATION_REPORT.md',
        'rule':'Only CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR.md is current for v101.127; v101.126 and earlier reports/evidence are predecessor/historical lineage.'})
    write_json(out/'metadata'/'current_evidence_lineage.json',{
        'version':VERSION,'stage':STAGE,'current_evidence_root':'evidence/v101127',
        'predecessor_24h':{'version':'v101.126','sha256':EXPECTED_BASE_SHA},
        'governed_ldc_source':{'version':v.get('ldc_source_app_version'),'sha256':v.get('ldc_source_package_sha256')},
        'rule':'v101.126 evidence remains predecessor lineage; v101.127 current evidence is presentation-regression repair evidence only.'})
    write_json(out/'metadata'/'build_provenance.json',{
        'version':VERSION,'stage':STAGE,'build_date':BUILD_DATE,'baseline_version':'v101.126','baseline_zip_sha256':EXPECTED_BASE_SHA,
        'baseline_html_sha256':sha_bytes(src.encode()),'candidate_html_sha256':sha_bytes(new.encode()),
        'mutation_scope':'presentation-only continuity glyph-flow CSS repair; zero canonical text operations',
        'canonical_text_changed':False,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,
        'governed_ldc_zip_sha256':v.get('ldc_source_package_sha256'),'final_reopen_evidence':'EXTERNAL_AFTER_IMMUTABLE_ZIP_FREEZE'})
    write_json(out/'metadata'/'release_evidence_lifecycle.json',{
        'version':VERSION,'stage':STAGE,'prefreeze_package_reports':'current package report may claim only directly executed static/build facts',
        'postfreeze_final_reopen_reports':'external only','physical_device_claims':'NOT_TESTED until direct evidence',
        'immutable_package_rule':'do not insert postfreeze PASS reports into frozen ZIP','current_evidence_rule':'evidence/v101127 is current; older evidence is predecessor/historical lineage',
        'active_report_rule':'current active report claims must bind directly to evidence/v101127 or current package bytes'})
    tool=out/'scripts'/'build_v101127_continuity_glyph_flow_regression_repair.py';tool.write_bytes(Path(__file__).read_bytes())
    strict_src=Path('/mnt/data/regression_v126_hour3/run_strict_continuity_glyph_flow_matrix.py')
    strict_dst=out/'scripts'/'run_v101127_strict_continuity_glyph_flow_matrix.py'; strict_dst.write_bytes(strict_src.read_bytes())
    write_json(ev/'STRICT_GLYPH_FLOW_TEST_CONTRACT.json',{'schema':'L24H_V101127_STRICT_GLYPH_FLOW_TEST_CONTRACT_V1','version':VERSION,'stage':STAGE,'profiles':['phone','ipad_portrait','ipad_landscape','desktop','samsung'],'required_pairs':5,'desktop_invariant':'last lexical glyph of leader and first lexical glyph of follower must have equal baseline (|dy| <= 1px) when the 880px reader width has space','segmented_boundary_invariant':'leader final DISPLAY_SEGMENT inline; earlier internal segments remain block with rhythm preserved','negative_control':'unrepaired v101.126 must fail this gate for H03 and H13'})
    write_json(out/'metadata'/'current_tooling_inventory.json',{
        'version':VERSION,'stage':STAGE,'current_tools':['scripts/build_v101127_continuity_glyph_flow_regression_repair.py','scripts/run_v101127_strict_continuity_glyph_flow_matrix.py'],
        'reused_validated_runtime_lineage':['v101.126 runtime/search/highlight/PWA/textual data except bounded continuity CSS and release identity'],
        'historical_or_superseded_tools':['scripts/build_v101126_dual_successor_mutations.py']})
    (out/'metadata'/'scope_escalation_authority.md').write_text(f'''# v101.127 Scope Authority\n\nCurrent mutation authority is presentation-only: repair the proven continuity glyph-flow defect at approved `CONTINUITY_GROUPS` boundaries without changing canonical text, stable IDs, group membership, display-segment offsets, speaker/presentation semantics, topology or user-data schemas. The inherited 34 textual operations from v101.126 remain frozen. Any further text/content mutation requires separate authority.\n''',encoding='utf-8')
    (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION}\n\nPresentation-only continuity regression successor of immutable v101.126.\n\n## Repair\n\n- Fixes the forced cross-record line break at Hour 3 `peines,` → `afin que…`.\n- Applies the same mechanism correction to the Hour 13 approved continuity boundary.\n- Preserves all five approved continuity pairs, stable record IDs and internal display-segment rhythm.\n- Adds **zero** canonical/devotional text changes.\n\n## Inherited textual authority\n\nThe v101.126 textual fixed point remains unchanged: 34 authorised operations = 15 governed LDC synchronizations + 19 native 24H/prayer repairs.\n\n## Validation boundary\n\nPackage-local evidence is pre-final-reopen. Physical devices, installed-PWA update, true offline cold reopen, accessibility screen readers and live GitHub Pages exact-byte binding remain external gates.\n''',encoding='utf-8')

    # Full-build overlay relative to immutable v101.126.
    current=tree_files(out)
    changed=sorted(r for r,p in current.items() if r not in baseline_hashes or sha_file(p)!=baseline_hashes[r])
    removed=sorted(set(baseline_hashes)-set(current))
    for r in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
        if r not in changed: changed.append(r)
    changed=sorted(set(changed))
    write_json(out/'metadata'/'full_build_overlay_manifest.json',{
        'schema':'L24H_V101127_FULL_BUILD_OVERLAY_V1','version':VERSION,'stage':STAGE,'baseline_version':'v101.126','baseline_zip_sha256':EXPECTED_BASE_SHA,'changed_or_added':changed,'removed':removed})

    exclusions=['metadata/hash_manifest.json','metadata/package_manifest.json']
    files=[]
    for r,p in sorted(tree_files(out).items()):
        if r in exclusions: continue
        files.append({'path':r,'size':p.stat().st_size,'sha256':sha_file(p)})
    write_json(out/'metadata'/'hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':exclusions,'file_count':len(files),'files':files})
    write_json(out/'metadata'/'package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'stage':STAGE,'self_exclusion':exclusions,'file_count':len(files),'files':[{'path':x['path'],'size':x['size']} for x in files]})
    return {'version':VERSION,'stage':STAGE,'files':len(tree_files(out)),'html_sha256':sha_file(out/'index.html'),'changed_or_added':changed,'removed':removed}

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: build_v101127...py OUTDIR')
    print(json.dumps(build(sys.argv[1]),ensure_ascii=False,indent=2))
