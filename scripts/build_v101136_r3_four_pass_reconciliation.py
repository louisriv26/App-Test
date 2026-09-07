from pathlib import Path
import json,hashlib,zipfile,shutil,re,csv,os
BASE=Path('/mnt/data/24h_successor_work/v101136_R2_A.zip')
BASE_SHA='2f9a8602a9ac6add6b3f81bd015bb198bdccc65d1dad8617c67d92e10dfe04d4'
CONTENT_PREDECESSOR_SHA='cf8b688e649b2ef3f7c36768691c6a647d9d1e9eec85c90ba697dc2a05ef26fc'
LEDGER_SHA='6bce9bad3c0c3be87beaa95e987a3a3f0ada2c8ac6a4209ba6ca788698f9737d'
R6_SHA='35ee5c69fe0468d2e3ee2d963a7fa6667169c24d6c8023da2726b4cd8b50ed20'
R6_MAN='0d04190b166932086ed45141368bd4ae88b5a22806ca1e525a3e6a60a267f3ad'
VERSION='v101.136'; REV='R3'; STAGE='INTERIM_CLOSED_96_SUCCESSOR_R3_FOUR_PASS_RECONCILED'; DATE='2026-09-07'; CACHE='luisa-24h-v101-136-r3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def files(root):return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}
def writej(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
FIXES=[
 ('R3-FIX-001','REAL_DEVICE_QA_CHECKLIST.md','STALE_V101135_DEVICE_CHECKLIST','Replace with v101.136 R3 device-testing checklist based on v101.135→v101.136 in-place update.'),
 ('R3-FIX-002','reports/V101135_MASTER_SCRIPT_VALIDATION_COMPLETION.md','OBSOLETE_CURRENT_ROOT_REPORT','Move to reports/historical/v101135/.'),
 ('R3-FIX-003','reports/V101136_INTERIM_CLOSED_SUCCESSOR.md','STALE_R2_STATUS_REPORT','Move R2 report to reports/historical/v101136_r2/ and replace with current R3 report.'),
 ('R3-FIX-004','version.json.overall_release_status','STALE_INTERNAL_VALIDATION_PENDING','Replace with external-SHA-bound internal-evidence/device-test status; final public release remains unauthorized.'),
 ('R3-FIX-005','version.json.known_blockers','CONTRADICTED_BY_R2_PACKAGE_AUDIT','Clear only after the documentary/package defects are repaired; external gates remain separate.'),
 ('R3-FIX-006','metadata/active_report_inventory.json','CURRENT_REPORT_INVENTORY_GAP','Make current docs/test artifacts explicit and ensure obsolete reports are under historical namespace.'),
 ('R3-FIX-007','metadata/current_gate_map.json + metadata/release_evidence_lifecycle.json','OBSOLETE_VALIDATION_LIFECYCLE_WORDING','Model exact-ZIP four-pass evidence as external SHA-bound, while keeping physical/live gates open.'),
 ('R3-FIX-008','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','INADEQUATE_HEADER_ONLY_TEMPLATE','Replace with enumerated v101.136 device/update/targeted/offline/accessibility test matrix.'),
]
CHECKLIST='''# Real-device QA checklist — v101.136 R3\n\nUse only the exact **v101.136 R3** GitHub/device-test candidate whose SHA-256 is supplied in the external release receipt.\n\nPackage identity to verify before testing:\n- `app_version = v101.136`\n- `build_revision = R3`\n- `cache_name = luisa-24h-v101-136-r3`\n- `APP_EVIDENCE_STAGE = INTERIM_CLOSED_96_SUCCESSOR_R3_FOUR_PASS_RECONCILED`\n\nDo not use v101.136 R1 or R2 for deployment; R3 supersedes them for device testing. R3 changes no canonical devotional text relative to the corrected R2 content build.\n\n## A. Live-origin binding immediately after test deployment\n- Confirm the deployed ZIP SHA-256 matches the external R3 release receipt.\n- Open the site normally and confirm **v101.136** in Aide / À propos.\n- Confirm `version.json` reports `app_version = v101.136`, `build_revision = R3`, and `cache_name = luisa-24h-v101-136-r3`.\n- Hard refresh once and confirm the same identity.\n- Confirm no blank/stuck/bootstrap screen.\n\n## B. Existing-PWA update — mandatory\nTest an installation currently running **v101.135**; do not uninstall first.\n- Before update record: at least one Heure méditée, one note, one highlight, one favourite/library mark if used, last reading position, theme and font size.\n- Open installed v101.135 online and trigger/allow the normal update.\n- Confirm it becomes **v101.136 / R3**.\n- Close completely and reopen **three times**.\n- Confirm no fallback to v101.135, R1/R2 cache, blank screen, or repair loop.\n- Confirm all pre-existing user data and last-place state remain coherent.\n\n## C. Core functional smoke on each physical device\nRun on iPhone, iPad portrait, iPad landscape, and Samsung/Android. On each:\n- home renders/scrolls; all 24 Heures open; search works; Mon Espace opens; Aide opens;\n- light/dark theme and normal/large font work;\n- Méditée top/bottom controls remain synchronized;\n- notes/highlights can be created and persist after close/reopen;\n- no horizontal clipping/overflow; back navigation and last-place restore work.\n\n## D. Targeted v136 controls\n- H19 P118 repaired French sentence: no truncation/garbling.\n- H22 authorized quote/punctuation loci: no stale period after the closing guillemet where v136 removed it.\n- `RELATED_HOUR_06.P013`: paragraph flow normal; historical breaks preserved.\n- `RELATED_HOUR_16.P038`: no break splitting the word `en`.\n- `RELATED_HOUR_04.P127`: remapped break visually natural.\n- H23: unchanged from v101.135; no new AFLP/source-critical material inserted.\n- H24: end-of-cycle panel, Méditée toggle and restart behaviour correct.\n\n## E. Offline gate\nAfter a complete online load of v101.136 R3:\n- close the PWA, disconnect network/enable airplane mode, cold-open it;\n- confirm v101.136 opens normally; open two Heures, one linked text, Mon Espace and Aide;\n- close/reopen once more offline; restore network and confirm no downgrade or repair loop.\n\n## F. Accessibility gate\n- iPhone/iPad: representative VoiceOver navigation of main nav, Aide, Méditée, search and back controls.\n- Samsung: corresponding TalkBack checks.\n- No visible actionable button unnamed; focus restoration after modal/Aide closure sensible.\n\n## Release rule\nAny failure involving version/update identity, user-data loss, blank/stuck startup, true-offline cold reopen, text corruption, wrong H23 content, or persistent navigation/rendering regression is a **release blocker**. Final public release remains unauthorized until all mandatory physical/live gates are closed.\n'''
RESULT_ROWS=[
 ('LIVE','LIVE-01','browser','YES','Aide shows v101.136'),('LIVE','LIVE-02','browser','YES','version.json = v101.136; build_revision R3; cache luisa-24h-v101-136-r3'),
 ('UPDATE','UPD-01','iPhone;iPad;Samsung','YES','installed v101.135 updates in place to v101.136 R3'),('UPDATE','UPD-02','iPhone;iPad;Samsung','YES','notes/highlights/read state/last place/theme/font preserved'),('UPDATE','UPD-03','iPhone;iPad;Samsung','YES','3 close/reopen cycles stay on v101.136 R3; no repair loop'),
]
for dev in ['iPhone','iPad portrait','iPad landscape','Samsung']:
 for i,(block,exp) in enumerate([('YES','home renders/scrolls'),('YES','all 24 hours open'),('NO','search works'),('NO','Mon Espace works'),('NO','Aide shows v101.136'),('NO','theme/font controls work'),('NO','Méditée controls synchronized'),('YES','notes/highlights persist'),('NO','no horizontal overflow'),('YES','back/last-place restore coherent')],1): RESULT_ROWS.append(('CORE',f'{dev}:CORE-{i:02d}',dev,block,exp))
for i,exp in enumerate(['H19 P118 repaired sentence intact','H22 authorized punctuation displayed correctly','RELATED_HOUR_06 P013 flow preserved','RELATED_HOUR_16 P038 no split inside “en”','RELATED_HOUR_04 P127 break visually natural','H23 unchanged from v101.135','H24 cycle controls correct'],1): RESULT_ROWS.append(('TARGETED',f'REG-{i:02d}','at least iPhone + Samsung','YES',exp))
RESULT_ROWS += [('OFFLINE','OFF-01','iPhone;iPad;Samsung','YES','true offline cold reopen works after online load'),('OFFLINE','OFF-02','iPhone;iPad;Samsung','YES','hours/linked text/space/help usable offline'),('ACCESS','ACC-01','iPhone/iPad VoiceOver','YES','representative controls named and navigable'),('ACCESS','ACC-02','Samsung TalkBack','YES','representative controls named and navigable')]
def build(out):
 out=Path(out);shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
 assert sha(BASE)==BASE_SHA
 with zipfile.ZipFile(BASE) as z: assert z.testzip() is None; z.extractall(out)
 basehash={k:sha(p) for k,p in files(out).items()}
 # Prove exact R2 identity before release-engineering-only patch.
 v=json.loads((out/'version.json').read_text()); assert v['app_version']==VERSION and v['cache_name']=='luisa-24h-v101-136-r2'
 html=(out/'index.html').read_text(encoding='utf-8'); assert html==(out/'luisa_24_heures.html').read_text(encoding='utf-8'); assert "const APP_EVIDENCE_STAGE = 'INTERIM_CLOSED_96_SUCCESSOR_R2';" in html
 # Archive obsolete current-root reports.
 hist135=out/'reports/historical/v101135';hist135.mkdir(parents=True,exist_ok=True)
 shutil.move(str(out/'reports/V101135_MASTER_SCRIPT_VALIDATION_COMPLETION.md'),str(hist135/'V101135_MASTER_SCRIPT_VALIDATION_COMPLETION.md'))
 histR2=out/'reports/historical/v101136_r2';histR2.mkdir(parents=True,exist_ok=True)
 shutil.move(str(out/'reports/V101136_INTERIM_CLOSED_SUCCESSOR.md'),str(histR2/'V101136_INTERIM_CLOSED_SUCCESSOR_R2.md'))
 # Runtime/package identity only. Canonical data declarations remain byte-identical.
 html=html.replace("const APP_EVIDENCE_STAGE = 'INTERIM_CLOSED_96_SUCCESSOR_R2';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
 (out/'index.html').write_text(html,encoding='utf-8');(out/'luisa_24_heures.html').write_text(html,encoding='utf-8')
 sw=(out/'sw.js').read_text(); assert "const CACHE_NAME = 'luisa-24h-v101-136-r2';" in sw; sw=sw.replace("const CACHE_NAME = 'luisa-24h-v101-136-r2';",f"const CACHE_NAME = '{CACHE}';",1); sw=sw.replace('/* v101.136 */','/* v101.136 R3 */',1);(out/'sw.js').write_text(sw)
 # QA artifacts.
 (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(CHECKLIST,encoding='utf-8')
 with (out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(['section','test_id','devices','release_blocker_if_fail','expected','result','notes','package_sha256']);
  for r in RESULT_ROWS:w.writerow([*r,'','',''])
 # Version/release metadata.
 v.update({'app_version':VERSION,'build_revision':REV,'build_date':DATE,'cache_name':CACHE,
  'overall_release_status':'INTERNAL_FOUR_PASS_EVIDENCE_EXTERNAL_SHA_BOUND__READY_FOR_CONTROLLED_DEVICE_TESTING__FINAL_PUBLIC_DEPLOYMENT_UNAUTHORIZED',
  'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.136 R3.',
  'known_blockers':[],
  'external_open_gates':['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update v101.135→v101.136 R3','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'],
  'postfreeze_reopen_evidence':'Exact-ZIP four-pass/final-reopen evidence is external and SHA-bound; the package embeds the R3 repair authority and current release metadata.'})
 writej(out/'version.json',v)
 m=json.loads((out/'manifest.json').read_text());m['version']=VERSION;m['build_revision']=REV;writej(out/'manifest.json',m)
 # Current report and docs.
 (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION} {REV}\n\nGoverned interim content successor for controlled device testing. Canonical devotional content is byte-identical to corrected v101.136 R2 and remains exactly **96 authorized record mutations relative to immutable v101.135** (83 local + 13 official-R6 derivative sync).\n\nR3 is a **release-engineering/documentation reconciliation only**: stale v101.135 device-QA/report material has been corrected/archived, current status/inventories are aligned, and the service-worker cache is isolated as `{CACHE}`. No H23 source-critical finding and no upstream LDC linguistic finding is added.\n\nUse R3, not R1/R2, for device testing. Final public deployment remains unauthorized until physical-device, installed-PWA, true-offline, accessibility and live-origin gates pass. Exact-ZIP internal/final-reopen verification is supplied externally and must bind the released R3 SHA-256.\n''',encoding='utf-8')
 (out/'reports/V101136_R3_FOUR_PASS_RELEASE_RECONCILIATION.md').write_text(f'''# {VERSION} {REV} Four-Pass Release Reconciliation\n\n- Content authority remains immutable v101.135 `{CONTENT_PREDECESSOR_SHA}` plus authorized ledger `{LEDGER_SHA}`: exact canonical delta **96 = 83 local + 13 official-R6 sync**.\n- Corrected content/renderer predecessor for this release-engineering pass is v101.136 R2 `{BASE_SHA}`.\n- R3 canonical devotional raw text, speaker/presentation authorities, stable record IDs, storage schema and personal snapshot schema are unchanged from R2.\n- R3 trigger: adversarial four-pass audit of R2 found **release-engineering/documentary defects only**, not a new corpus/runtime defect.\n- Repairs: v101.136 device checklist and enumerated QA template; stale v101.135/R2 current-root reports archived; active report/status/evidence lifecycle reconciled; distinct R3 cache/build identity.\n- R1 and R2 are superseded for deployment/device testing.\n- Internal exact-ZIP four-pass and final reopened-ZIP evidence are external and SHA-bound; this package does not self-certify its own ZIP hash.\n- Physical iPhone/iPad/Samsung, installed-PWA update/persistence, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte gates remain `NOT_TESTED`; final public release is unauthorized.\n''',encoding='utf-8')
 # Evidence for repair authority.
 ev=out/'evidence/v101136_r3';ev.mkdir(parents=True,exist_ok=True)
 with (ev/'RELEASE_ENGINEERING_FIX_LEDGER.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(['fix_id','target','r2_finding','r3_action','status']);
  for a,b,c,d in FIXES:w.writerow([a,b,c,d,'APPLIED'])
 writej(ev/'R2_FOUR_PASS_TRIGGER.json',{'schema':'L24H_V101136_R3_R2_TRIGGER_V1','r2_zip_sha256':BASE_SHA,'pass1':'PASS_22_22','pass2':'PASS_618_618_RUNTIME_PLUS_22_22_PACKAGE_STATIC','pass3':'FAIL_3_STALE_ACTIVE_LINES_OF_71','pass4':'FAIL_8_RELEASE_ENGINEERING_DOCUMENTARY_FINDINGS','canonical_runtime_defect_newly_found_in_r2_four_pass':False,'decision':'BUILD_R3_RELEASE_ENGINEERING_ONLY'})
 # Current metadata.
 active=['README.md','REAL_DEVICE_QA_CHECKLIST.md','reports/V101136_R3_FOUR_PASS_RELEASE_RECONCILIATION.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md']
 writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'active_documents':active,'active_test_artifacts':['REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'],'historical_reports_root':'reports/historical/','rule':'Only listed active documents are current; predecessor/superseded reports must reside under reports/historical/.'})
 writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'content_authority_root':'evidence/v101136','release_reconciliation_root':'evidence/v101136_r3','content_predecessor_24h':{'version':'v101.135','sha256':CONTENT_PREDECESSOR_SHA},'release_engineering_predecessor':{'version':'v101.136 R2','sha256':BASE_SHA},'authorized_ledger_sha256':LEDGER_SHA,'governing_ldc_r6':{'version':'v2.19.65-R1B','official_zip_sha256':R6_SHA,'corpus_manifest_sha256':R6_MAN},'final_exact_zip_four_pass_receipt':'EXTERNAL_SHA_BOUND'})
 writej(out/'metadata/build_provenance.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,'release_engineering_baseline':'v101.136 R2','release_engineering_baseline_zip_sha256':BASE_SHA,'content_predecessor_version':'v101.135','content_predecessor_zip_sha256':CONTENT_PREDECESSOR_SHA,'authorized_ledger_sha256':LEDGER_SHA,'canonical_text_changed_from_r2':False,'speaker_presentation_authorities_changed_from_r2':False,'stable_record_ids_unchanged':True,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'release_engineering_changes':['current docs/reports','status/evidence metadata','device QA artifacts','APP_EVIDENCE_STAGE','service-worker cache generation'],'final_validation':'EXTERNAL_SHA_BOUND_EXACT_ZIP'})
 (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} Scope Authority\n\nCanonical content authority remains exactly 96 records from ledger SHA-256 `{LEDGER_SHA}` relative to immutable v101.135. R3 authorizes **no additional canonical devotional text mutation**. No H23 source-critical finding and no upstream LDC linguistic finding is authorized. R3 scope is limited to the eight release-engineering/documentary repairs recorded in `evidence/v101136_r3/RELEASE_ENGINEERING_FIX_LEDGER.csv`, build/cache identity, and derived package manifests. Any additional canonical text change requires a new authority.\n''',encoding='utf-8')
 writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'package_rule':'Current package metadata does not self-certify final ZIP bytes. Four-pass/final-reopen evidence must be generated after freeze and SHA-bind the exact R3 ZIP.','internal_package_gates':'REQUIRE_EXTERNAL_SHA_BOUND_PASS_BEFORE_DEVICE_TESTING','physical_device_claims':'NOT_TESTED','public_deployment_authorized':False})
 writej(out/'metadata/current_gate_map.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'internal_gates':['files vs build','runtime/package behaviour','active report line audit','stale/contradiction scan','final reopened recheck'],'internal_evidence':'EXTERNAL_SHA_BOUND_EXACT_ZIP','external_open_gates':['physical devices','live-origin exact-byte binding','installed-PWA update/persistence','true offline cold reopen','VoiceOver/TalkBack'],'public_release':'UNAUTHORIZED'})
 # Current tooling inventory and builder.
 this=Path(__file__);shutil.copy2(this,out/'scripts/build_v101136_r3_four_pass_reconciliation.py')
 writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_builder':'scripts/build_v101136_r3_four_pass_reconciliation.py','content_builder_lineage':'scripts/build_v101136_interim_closed_96_r2.py retained as predecessor tooling','runtime_validation':'external rebased v101.136 harnesses; exact-ZIP receipt required'})
 writej(out/'metadata/builder_input_manifest.json',{'version':VERSION,'build_revision':REV,'release_engineering_predecessor_zip_sha256':BASE_SHA,'content_predecessor_v101135_zip_sha256':CONTENT_PREDECESSOR_SHA,'authorized_ledger_sha256':LEDGER_SHA,'governing_ldc_r6_zip_sha256':R6_SHA,'governing_ldc_r6_corpus_manifest_sha256':R6_MAN})
 # Overlay relative to R2 before manifests.
 cur=files(out); changed=sorted(k for k,p in cur.items() if k not in basehash or sha(p)!=basehash[k]); removed=sorted(set(basehash)-set(cur))
 for x in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
  if x not in changed: changed.append(x)
 writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101136_R3_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':'v101.136 R2','baseline_zip_sha256':BASE_SHA,'changed_or_added':sorted(changed),'removed':removed})
 ex={'metadata/hash_manifest.json','metadata/package_manifest.json'};lst=[]
 for k,p in sorted(files(out).items()):
  if k in ex:continue
  lst.append({'path':k,'size':p.stat().st_size,'sha256':sha(p)})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
 writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
 return {'version':VERSION,'revision':REV,'files':len(files(out)),'fixes':len(FIXES),'cache':CACHE}
def freeze(root,zp):
 root=Path(root);zp=Path(zp);zp.unlink(missing_ok=True)
 with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(root.rglob('*')):
   if not p.is_file():continue
   rel=p.relative_to(root).as_posix();info=zipfile.ZipInfo(rel,(2026,9,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16);z.writestr(info,p.read_bytes())
 return sha(zp)
if __name__=='__main__':
 import sys
 r=build(sys.argv[1]);z=freeze(sys.argv[1],sys.argv[2]);print(json.dumps(r,indent=2));print('ZIP',z)
