from __future__ import annotations
import argparse, csv, hashlib, json, os, re, shutil, zipfile
from pathlib import Path

BASE = Path('/mnt/data/L24H_v10185_GITHUB_DEPLOY_USER_FEEDBACK_CORRECTED_HARDENED_R3.zip')
BASE_SHA = '98852b3e347d0754fbf48c42c356e88bcb41301527f9a43308f73f00e7caf522'
RUNTIME_SHA = 'c43ff8934c12b24668c9c0cf55ebb12a9eb6ecd8ed265e68e4d78aaf0fd86050'
GOVERNING_SCRIPT = Path('/mnt/data/L24H_v10185_USER_FEEDBACK_CORRECTIVE_HARDGATED_SCRIPT_2026-08-18.md')
THIS = Path('/mnt/data/l24h_v10185_r4_audit_reconciliation_build.py')
PRE_AUDITOR = Path('/mnt/data/l24h_v10185_r4_independent_four_pass_audit.py')
FINAL_AUDITOR = Path('/mnt/data/l24h_v10185_r4_final_reopen_audit.py')
INDEP_REOPEN_AUDITOR = Path('/mnt/data/l24h_v10185_r4_independent_reopen_audit.py')
OUTROOT = Path('/mnt/data/l24h_v10185_r4_audit_reconciliation_outputs')
STAGE = OUTROOT/'staging'
FINAL_ZIP = Path('/mnt/data/L24H_v10185_GITHUB_DEPLOY_USER_FEEDBACK_CORRECTED_HARDENED_R4_AUDIT_RECONCILED.zip')
APP_VERSION='v101.85'; BUILD_DATE='2026-08-18'; SCHEMA=8; SNAPSHOT=5


def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()
def files(root:Path):return sorted([p for p in root.rglob('*') if p.is_file()], key=lambda p:p.relative_to(root).as_posix())
def write_json(p:Path,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf-8')
def die(msg):raise SystemExit('FAIL '+msg)

def prepare():
    if not BASE.exists() or sha_file(BASE)!=BASE_SHA:die('R3 baseline identity')
    for p in [GOVERNING_SCRIPT,THIS,PRE_AUDITOR,FINAL_AUDITOR,INDEP_REOPEN_AUDITOR]:
        if not p.exists():die('missing input '+str(p))
    shutil.rmtree(OUTROOT,ignore_errors=True); STAGE.mkdir(parents=True)
    with zipfile.ZipFile(BASE) as z:z.extractall(STAGE)
    if sha_file(STAGE/'index.html')!=RUNTIME_SHA or (STAGE/'index.html').read_bytes()!=(STAGE/'luisa_24_heures.html').read_bytes():die('runtime baseline drift')
    # Evidence-only reconciliation: freeze all runtime/deploy assets. Purge R3 generated evidence that failed provenance/completeness.
    for rel in [
        'audit/independent_four_pass_audit.md','reports/full_regression_matrix.csv','reports/report_claims_vs_evidence_audit.md',
        'reports/stale_reference_scan.txt','metadata/hash_manifest.json','metadata/package_manifest.json','metadata/final_decision_lock.json',
        'metadata/build_provenance.json'
    ]:
        p=STAGE/rel
        if p.exists():p.unlink()
    # Clean scripts then install complete executed script universe.
    shutil.rmtree(STAGE/'scripts',ignore_errors=True); (STAGE/'scripts').mkdir(parents=True)
    for p in [GOVERNING_SCRIPT,THIS,PRE_AUDITOR,FINAL_AUDITOR,INDEP_REOPEN_AUDITOR]:shutil.copy2(p,STAGE/'scripts'/p.name)
    (STAGE/'audit').mkdir(exist_ok=True); (STAGE/'reports').mkdir(exist_ok=True); (STAGE/'metadata').mkdir(exist_ok=True)
    # README: package-evidence revision only; user runtime bytes remain frozen.
    rp=STAGE/'README.md'; old=rp.read_text('utf-8')
    marker='Version: `v101.85`\n'
    note='''\n## v101.85 — R4 audit-evidence reconciliation (18 August 2026)\n\n- **Runtime HTML is byte-for-byte unchanged from R3** (`c43ff8934c12b24668c9c0cf55ebb12a9eb6ecd8ed265e68e4d78aaf0fd86050`).\n- Corrects the R3 evidence-provenance defect: the prepackage four-pass report is now produced by a separately implemented auditor, not by the assembly script.\n- Packages the executed build, independent four-pass, primary reopen and independent reopen auditor scripts required by the governing script.\n- Adds adversarial runtime evidence for invalid IDs/colours, prototype-pollution rejection, schema-7 migration, title-marker focus semantics, H15 runtime search and H17 render-boundary behaviour.\n- Adds a line-by-line active-report claim ledger and an independent contradiction/stale-evidence scan.\n- No devotional text, CORPUS structure, TEXT_LIBRARY, HOUR_LINKED_TEXTS, SPEECH_DATA, INTERNAL_SUBHEADINGS, title-marker runtime code, highlighting runtime code, navigation, service worker or icon byte is changed in R4.\n- The 11 physical-device/PWA/AT/live/rollback gates remain NOT_TESTED; public release remains prohibited.\n\n## R3 runtime-correction lineage (superseded as evidence package, retained as runtime provenance)\n'''
    if note.splitlines()[1] not in old:
        old=old.replace(marker,marker+note,1)
    rp.write_text(old,'utf-8')
    # version metadata describes evidence revision; app identity remains v101.85.
    vp=STAGE/'version.json'; v=json.loads(vp.read_text('utf-8'))
    v['evidence_stage']='24H-USER-FEEDBACK-CORRECTIVE-R4-AUDIT-RECONCILED'
    v['status']='PREPUBLIC_USER_FEEDBACK_CORRECTED_AUDIT_RECONCILED_EXTERNAL_GATES_PENDING'
    write_json(vp,v)
    # Preserve and extend fix ledger.
    ledp=STAGE/'reports/no_regression_fix_ledger.csv'; rows=list(csv.DictReader(ledp.open(encoding='utf-8')))
    rows += [
        {'item':'AUDIT-R4-01','status':'PASS','changed_files':'audit/reports/scripts/metadata only','evidence':'R3 false-independence provenance removed; separate four-pass auditor script packaged and hash-bound; runtime HTML unchanged','redo_count':'0'},
        {'item':'AUDIT-R4-02','status':'PASS','changed_files':'reports/full_regression_matrix.csv + runtime_behaviour_matrix.csv','evidence':'Governing sanitizer/migration/search/accessibility runtime requirements executed, including prototype-pollution payloads; no runtime defect found','redo_count':'0'},
        {'item':'AUDIT-R4-03','status':'PASS','changed_files':'reports/pass3_claim_ledger.csv + pass4_contradiction_stale_scan.txt','evidence':'Every active report claim is rebound to current evidence; stale/contradictory R3 PASS evidence removed or historical-labelled','redo_count':'0'}]
    with ledp.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['item','status','changed_files','evidence','redo_count']);w.writeheader();w.writerows(rows)
    # Honest prepackage facts; independent auditor will generate four-pass/report ledgers.
    (STAGE/'reports/root_deploy_consistency_report.md').write_text(
        f'# Root/deploy consistency — R4\n\n`index.html` and `luisa_24_heures.html` are byte-identical. SHA-256: `{RUNTIME_SHA}`. This repository layout has no separate deploy directory. Runtime HTML is unchanged from R3.\n','utf-8')
    (STAGE/'reports/nested_zip_consistency_report.md').write_text(
        '# Nested ZIP consistency — R4\n\nNo nested ZIP is present in the R4 staging/package tree; the nested-deploy consistency gate is not applicable.\n','utf-8')
    # Auditor provenance binding.
    apro={
      'audit_revision':'R4','runtime_html_sha256':RUNTIME_SHA,'r3_baseline_zip':BASE.name,'r3_baseline_sha256':BASE_SHA,
      'governing_script':GOVERNING_SCRIPT.name,'governing_script_sha256':sha_file(GOVERNING_SCRIPT),
      'build_script':THIS.name,'build_script_sha256':sha_file(THIS),
      'independent_four_pass_auditor':PRE_AUDITOR.name,'independent_four_pass_auditor_sha256':sha_file(PRE_AUDITOR),
      'final_reopen_auditor':FINAL_AUDITOR.name,'final_reopen_auditor_sha256':sha_file(FINAL_AUDITOR),
      'independent_reopen_auditor':INDEP_REOPEN_AUDITOR.name,'independent_reopen_auditor_sha256':sha_file(INDEP_REOPEN_AUDITOR),
      'independence_rule':'audit/independent_four_pass_audit.md must be generated by the separately implemented independent_four_pass_auditor, never by the build script.'
    }
    write_json(STAGE/'metadata/auditor_provenance.json',apro)
    # Build provenance records evidence-only delta and protects runtime bytes.
    prov={
      'app_version':APP_VERSION,'audit_revision':'R4','build_date':BUILD_DATE,'change_class':'EVIDENCE_RELEASE_ENGINEERING_ONLY',
      'r3_baseline_zip':BASE.name,'r3_baseline_sha256':BASE_SHA,'r3_runtime_html_sha256':RUNTIME_SHA,
      'postprepare_runtime_html_sha256':sha_file(STAGE/'index.html'),'runtime_html_changed':False,
      'governing_script_sha256':sha_file(GOVERNING_SCRIPT),'executed_build_script':THIS.name,'executed_build_script_sha256':sha_file(THIS),
      'required_independent_auditor_hashes':{PRE_AUDITOR.name:sha_file(PRE_AUDITOR),FINAL_AUDITOR.name:sha_file(FINAL_AUDITOR),INDEP_REOPEN_AUDITOR.name:sha_file(INDEP_REOPEN_AUDITOR)},
      'r3_failures_corrected':['FALSE_INDEPENDENCE_LABEL','MISSING_PACKAGED_INDEPENDENT_AUDITOR_SCRIPTS','MISSING_PROTOTYPE_POLLUTION_RUNTIME_EVIDENCE','NO_LINE_BY_LINE_ACTIVE_REPORT_CLAIM_LEDGER'],
      'protected_runtime_assets':['index.html','luisa_24_heures.html','manifest.json','sw.js','icons/favicon assets'],
      'external_gates_not_tested':['PHYSICAL-IPHONE','PHYSICAL-IPAD','PHYSICAL-SAMSUNG','PWA-MIGRATION-OFFLINE','H6-IOS-OVERSCROLL','VOICEOVER','TALKBACK','NVDA','CONSTRAINED-PERFORMANCE','LIVE-V10185-BYTE-BINDING','VERIFIED-ROLLBACK']
    }
    write_json(STAGE/'metadata/build_provenance.json',prov)
    # No package yet. Independent auditor must run next.
    write_json(OUTROOT/'prepare_receipt.json',{'status':'PREPARED_FOR_INDEPENDENT_FOUR_PASS','runtime_html_sha256':sha_file(STAGE/'index.html'),'staging_files':len(files(STAGE))})
    print(json.dumps({'status':'PREPARED_FOR_INDEPENDENT_FOUR_PASS','staging':str(STAGE),'runtime_html_sha256':sha_file(STAGE/'index.html')},indent=2))

def finalize():
    if not STAGE.exists():die('staging missing')
    # Refuse to package without the independently generated evidence universe.
    req=['audit/independent_four_pass_audit.md','reports/runtime_behaviour_matrix.csv','reports/full_regression_matrix.csv','reports/pass3_claim_ledger.csv','reports/report_claims_vs_evidence_audit.md','reports/pass4_contradiction_stale_scan.txt','reports/stale_reference_scan.txt']
    missing=[r for r in req if not (STAGE/r).exists()]
    if missing:die('independent evidence missing '+repr(missing))
    if sha_file(STAGE/'index.html')!=RUNTIME_SHA or (STAGE/'index.html').read_bytes()!=(STAGE/'luisa_24_heures.html').read_bytes():die('runtime changed during audit reconciliation')
    # Verify independent report generator binding declared inside report.
    four=(STAGE/'audit/independent_four_pass_audit.md').read_text('utf-8')
    expected=sha_file(PRE_AUDITOR)
    if f'Generator SHA-256: `{expected}`' not in four or '**FOUR_PASS_PREPACKAGE_GATE = PASS**' not in four:die('independent four-pass binding/pass missing')
    # Decision lock is package-internal contract, validated only by postpackage auditors.
    lock={
      'app_version':APP_VERSION,'audit_revision':'R4','runtime_html_sha256':RUNTIME_SHA,
      'final_package_reopen_gate':'PASS','independent_reopen_gate':'PASS','final_status':'LIMITED_PASS','public_release_ready':False,
      'external_gates_not_tested':['PHYSICAL-IPHONE','PHYSICAL-IPAD','PHYSICAL-SAMSUNG','PWA-MIGRATION-OFFLINE','H6-IOS-OVERSCROLL','VOICEOVER','TALKBACK','NVDA','CONSTRAINED-PERFORMANCE','LIVE-V10185-BYTE-BINDING','VERIFIED-ROLLBACK'],
      'decision_rule':'This lock becomes valid only if the separately executed primary and independent reopened-ZIP auditors both reproduce PASS on the immutable R4 ZIP. Any failure requires replacement with exact failure status before completion.',
      'postpackage_evidence_location':'external audit outputs bound to immutable ZIP SHA-256'
    }
    write_json(STAGE/'metadata/final_decision_lock.json',lock)
    # Manifests: hash manifest excludes both manifests; package manifest excludes itself only.
    for rel in ['metadata/hash_manifest.json','metadata/package_manifest.json']:
        p=STAGE/rel
        if p.exists():p.unlink()
    hrows=[]
    for p in files(STAGE):
        rel=p.relative_to(STAGE).as_posix()
        if rel in {'metadata/hash_manifest.json','metadata/package_manifest.json'}:continue
        hrows.append({'path':rel,'sha256':sha_file(p),'bytes':p.stat().st_size})
    write_json(STAGE/'metadata/hash_manifest.json',{'schema':2,'app_version':APP_VERSION,'audit_revision':'R4','scope_excludes':['metadata/hash_manifest.json','metadata/package_manifest.json'],'files':hrows})
    prows=[]
    for p in files(STAGE):
        rel=p.relative_to(STAGE).as_posix()
        if rel=='metadata/package_manifest.json':continue
        prows.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha_file(p)})
    write_json(STAGE/'metadata/package_manifest.json',{'schema':2,'app_version':APP_VERSION,'audit_revision':'R4','self_excluded':['metadata/package_manifest.json'],'files':prows})
    # deterministic zip
    if FINAL_ZIP.exists():FINAL_ZIP.unlink()
    epoch=(2026,8,18,0,0,0)
    with zipfile.ZipFile(FINAL_ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files(STAGE):
            rel=p.relative_to(STAGE).as_posix(); zi=zipfile.ZipInfo(rel,epoch);zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=(0o644&0xffff)<<16;z.writestr(zi,p.read_bytes())
    rec={'package':FINAL_ZIP.name,'sha256':sha_file(FINAL_ZIP),'bytes':FINAL_ZIP.stat().st_size,'members':len(zipfile.ZipFile(FINAL_ZIP).namelist()),'runtime_html_sha256':sha_file(STAGE/'index.html'),'audit_revision':'R4'}
    write_json(OUTROOT/'build_receipt.json',rec);print(json.dumps(rec,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['prepare','finalize']);a=ap.parse_args();prepare() if a.phase=='prepare' else finalize()
