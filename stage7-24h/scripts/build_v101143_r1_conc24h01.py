#!/usr/bin/env python3
from pathlib import Path
import zipfile, hashlib, json, shutil, subprocess, sys, re
VERSION='v101.143'; REV='R1'; STAGE='PERSONAL_STATE_CONCURRENCY_SUCCESSOR_R1'; DATE='2026-09-10'; CACHE='luisa-24h-v101-143-r1'
BASE_VERSION='v101.142 R1'; BASE_SHA='5e94f3cbdff075b43dfb3c6278d30a81c94df2ccdebcabe942c5fa75b537b2c0'
PATCH_SHA='8c3b77a7bde7c46a19f347f4bb95245a6d43e145419788c87391a4a9a353bc43'
AUTH_SHA='85343515778a33019da768219bdda0ac7050674f4dff4cf98c32bade65a37098'
STATE_SHA='1b87407be51819ac08f3c4a0624a4c8968ea056c6d2087c08ffa1358c8e36bed'
ED15_SHA='efe7fd7ce09aa887781dd99388fcbbc6009e4be6d089acc4942f24e630543e01'
LOCK='collection-luisa:24h:personal-state:v1'
PROTECTED_CONSTS=['CORPUS','TEXT_LIBRARY','SPEECH_DATA','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS','VISIBLE_PARAGRAPH_TOPOLOGY','LDC_LIBRARY_FLOW_LAYOUT','INTERNAL_SUBHEADINGS','CONTINUITY_GROUPS','HOUR_LINKED_TEXTS','PASSION24_RELATED_BY_HOUR']

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def files(root):
 root=Path(root);return {p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc')}
def writej(p,o):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def raw_const(text,name):
 m='const '+name+' = ';i=text.find(m)
 if i<0:m='const '+name+'=';i=text.find(m)
 assert i>=0,name
 st=i+len(m)
 while text[st].isspace():st+=1
 if text[st] in '[{':
  stack=[];q=None;esc=False;pairs={'{':'}','[':']'}
  for j in range(st,len(text)):
   c=text[j]
   if q:
    if esc:esc=False
    elif c=='\\':esc=True
    elif c==q:q=None
    continue
   if c in "'\"`":q=c;continue
   if c in pairs:stack.append(pairs[c])
   elif c in ']}':
    assert stack and c==stack[-1];stack.pop()
    if not stack:return text[st:j+1]
  raise AssertionError(name)
 j=text.find(';',st);assert j>=0;return text[st:j]
def exact_replace(s,a,b,label):
 n=s.count(a);assert n==1,(label,n);return s.replace(a,b,1)
def freeze(root,zp):
 root=Path(root);zp=Path(zp);zp.unlink(missing_ok=True)
 with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(root.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or p.name.endswith('.pyc'):continue
   rel=p.relative_to(root).as_posix();info=zipfile.ZipInfo(rel,(2026,9,10,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.create_system=3;info.external_attr=(0o100644<<16);info.flag_bits|=0x800
   z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 with zipfile.ZipFile(zp) as z:assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
 return sha(zp)

def build(base_zip,patch_file,out_dir,out_zip):
 base_zip=Path(base_zip);patch_file=Path(patch_file);out=Path(out_dir);out_zip=Path(out_zip)
 assert sha(base_zip)==BASE_SHA,(sha(base_zip),BASE_SHA);assert sha(patch_file)==PATCH_SHA,(sha(patch_file),PATCH_SHA)
 shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
 with zipfile.ZipFile(base_zip) as z:
  assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()));z.extractall(out)
 base_files=files(out);base_hash={k:sha(v) for k,v in base_files.items()}
 base_idx=(out/'index.html').read_text(encoding='utf-8');assert base_idx==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 protected_before={n:raw_const(base_idx,n) for n in PROTECTED_CONSTS}
 # Apply exact SHA-bound runtime patch to index, then keep the launch mirror byte-identical.
 pr=subprocess.run(['patch','--batch','--forward','-p0','-i',str(patch_file)],cwd=out,capture_output=True,text=True)
 assert pr.returncode==0,(pr.stdout,pr.stderr)
 (out/'luisa_24_heures.html').write_bytes((out/'index.html').read_bytes())
 idx=(out/'index.html').read_text(encoding='utf-8');assert idx==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 assert "const APP_VERSION = 'v101.143';" in idx and "const APP_EVIDENCE_STAGE = 'PERSONAL_STATE_CONCURRENCY_SUCCESSOR_R1';" in idx
 assert LOCK in idx and 'let _passivePositionBaseline = Object.create(null);' in idx
 for n in PROTECTED_CONSTS:assert raw_const(idx,n)==protected_before[n],n
 # Mechanically necessary release bindings only; no unrelated SW logic or PWA identity change.
 sw=(out/'sw.js').read_text(encoding='utf-8');sw=exact_replace(sw,'/* v101.142 R1 */','/* v101.143 R1 */','sw version');sw=exact_replace(sw,"const CACHE_NAME = 'luisa-24h-v101-142-r1';",f"const CACHE_NAME = '{CACHE}';",'cache');(out/'sw.js').write_text(sw,encoding='utf-8')
 man=json.loads((out/'manifest.json').read_text(encoding='utf-8'));identity={k:man.get(k) for k in ['id','start_url','scope','name','short_name','display']};assert man['version']=='v101.142' and man['build_revision']=='R1';man['version']=VERSION;man['build_revision']=REV;writej(out/'manifest.json',man);assert {k:man.get(k) for k in identity}==identity
 vv=json.loads((out/'version.json').read_text(encoding='utf-8'));assert vv['storage_schema']==8 and vv['personal_snapshot']==5
 vv.update({'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,'build_revision':REV,
  'release_scope':'CONC-24H-01 bounded successor of exact immutable v101.142 R1. Eliminates confirmed multi-context committed-change loss for 24H personal state using app-specific serialization on the owner-approved iOS/iPadOS 15.4+ full-support floor, fresh canonical durable read inside the lock, operation-level delta/merge, same-record conflict preservation/retry, inherited verified persistence/rollback, coherent legacy mirrors, peer reconciliation, concurrency-safe import/restore, startup migration/recovery serialization, and conflict-aware coalesced reading-position persistence. Corpus, speaker authority, stable IDs/order, Search semantics/cap, typography/contrast/Repères semantics, PWA identity-critical fields, backup schema, Hub architecture and unrelated Service Worker logic are unchanged.',
  'real_device_status':'Physical iPhone/iPad/Samsung multi-context concurrency, live-origin exact-byte binding, installed-PWA update/persistence, true offline cold reopen and representative VoiceOver/TalkBack remain NOT_TESTED for v101.143 R1.',
  'overall_release_status':'V101143_R1_CONC24H01_FROZEN_CANDIDATE__EXTERNAL_SHA_BOUND_REOPEN_REQUIRED_BY_DESIGN',
  'known_blockers':['external SHA-bound reopened-package receipt before device candidacy','physical iPad/iPhone/Samsung multi-context concurrency','live-origin exact-byte binding','installed PWA update from deployed v101.142 R1 to v101.143 R1','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'],
  'external_open_gates':['physical iPad/iPhone/Samsung multi-context concurrency','live-origin exact-byte binding','installed PWA update from deployed v101.142 R1 to v101.143 R1','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'],
  'postfreeze_reopen_evidence':'The package intentionally does not self-certify its own final ZIP. Use the external SHA-bound CONC-24H-01 reopened-package receipt.'})
 writej(out/'version.json',vv)
 # Current package-facing documents.
 (out/'README.md').write_text(f'''# {VERSION} {REV} — CONC-24H-01 frozen successor candidate\n\nCurrent stage: `{STAGE}`. Immediate immutable predecessor: `{BASE_VERSION}` SHA-256 `{BASE_SHA}`. This successor is limited to the confirmed 24H multi-context personal-state committed-change-loss repair. Full support floor approved by the owner: iOS/iPadOS 15.4+ and equivalent modern Android/Samsung; older engines are best-effort.\n\nRepair invariant: serialize app-specific personal writes, read fresh durable state inside serialization, merge only the initiating operation, preserve newer same-record durable state on conflict, retain verified persistence/rollback and legacy mirrors, reconcile peer UI, and serialize import/startup/position write paths.\n\nProtected: corpus text, speakers, stable IDs/order, Search semantics/cap, typography/contrast/Repères semantics, PWA identity-critical fields, backup schema, Hub architecture and unrelated Service Worker behavior.\n\nThis ZIP does not self-certify final bytes. Device candidacy requires an external SHA-bound reopened-package receipt. Physical/live-origin/PWA/offline/screen-reader gates remain `NOT TESTED`.\n''',encoding='utf-8')
 (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(f'''# Real-device QA checklist — {VERSION} {REV} / CONC-24H-01\n\nUse only the exact SHA-bound frozen candidate after external reopened-package certification.\n\n## Multi-context personal-state integrity\n- Open two active instances of 24H on the same origin.\n- Add a note in A while B holds stale progress state; then change progress in B. Both committed changes must survive.\n- Repeat in the reverse direction.\n- Add independent notes/highlights on the same paragraph from A/B; both must survive.\n- Create a same-record edit conflict; the newer durable record must not be silently overwritten and the stale action must fail/retry visibly.\n- Delete/Undo note, highlight and library-mark records while the peer adds an independent record; unrelated peer records must survive.\n- Exercise rapid reading-position movement while adding a note in the peer; the note must survive and the latest non-conflicting position must persist.\n- Create a same-Hour position conflict; the newer durable pointer must be preserved.\n- Begin Import confirmation, commit a peer change, then continue Import; Import must abort rather than erase the peer change.\n\n## Failure/recovery\n- Storage write failure preserves previous durable bytes.\n- Read-back mismatch rolls back exact previous bytes where possible.\n- Future snapshot/schema remains fail-closed and byte-preserved.\n- Canonical success with a legacy mirror failure remains canonical success with honest warning.\n\n## Protected regression\n- Existing notes/highlights/progress/resume/theme/font/Repères mechanics survive update and reopen.\n- Search behavior/cap, Hour 24, Méditée, native visible-flow topology and stable anchors are unchanged.\n- Manifest installed identity remains unchanged.\n\n## External gates\n- Physical iPhone.\n- Physical iPad portrait/landscape.\n- Physical Samsung/Android.\n- Live-origin exact-byte binding.\n- Installed-PWA update from deployed v101.142 R1 and three close/reopen cycles.\n- True offline cold reopen.\n- Representative VoiceOver/TalkBack.\n''',encoding='utf-8')
 (out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').write_text('''test_id,platform,required,expected,actual,status,notes\nCONC-NOTE-PROGRESS,iPhone;iPad;Samsung,YES,Independent note and progress commits from stale peer contexts both survive,,,\nCONC-NOTE-SAME-PARA,iPhone;iPad;Samsung,YES,Independent notes on same paragraph both survive,,,\nCONC-HL-SAME-PARA,iPhone;iPad;Samsung,YES,Independent highlights on same paragraph both survive,,,\nCONC-SAME-RECORD,iPhone;iPad;Samsung,YES,Same-record stale conflict preserves newer durable value and requires retry,,,\nCONC-DELETE-UNDO,iPhone;iPad;Samsung,YES,Delete and Undo never erase independent peer records,,,\nCONC-POSITION-RAPID,iPhone;iPad;Samsung,YES,Rapid position writes do not starve or erase note/highlight commits,,,\nCONC-POSITION-CONFLICT,iPhone;iPad;Samsung,YES,Same-Hour stale pointer does not overwrite newer durable pointer,,,\nCONC-IMPORT-RACE,iPhone;iPad;Samsung,YES,Import aborts if durable personal state changed after confirmation baseline,,,\nSTATE-UPDATE,iPhone;iPad;Samsung,YES,All existing personal-state domains survive installed-PWA update and reopen,,,\nPWA-UPDATE,iPhone;iPad;Samsung,YES,Update reaches exact SHA-bound v101.143 R1 and survives three close/reopen cycles,,,\nOFFLINE-01,iPhone;iPad;Samsung,YES,True offline cold reopen succeeds after update,,,\nA11Y-01,iPhone;iPad;Samsung,YES,Representative VoiceOver or TalkBack navigation remains usable,,,\n''',encoding='utf-8')
 report=out/'reports/V101143_R1_CONC_24H_01_PERSONAL_STATE_CONCURRENCY_SUCCESSOR.md';report.write_text(f'''# {VERSION} {REV} — CONC-24H-01 personal-state concurrency successor\n\n- Immediate immutable predecessor: `{BASE_VERSION}` / `{BASE_SHA}`.\n- Repair ID: `CONC-24H-01`.\n- Full-support floor: owner-approved iOS/iPadOS 15.4+ and equivalent modern Android/Samsung; older best-effort.\n- App-specific lock: `{LOCK}`.\n- Commit model: lock → fresh durable read → operation-level delta/merge → same-record conflict check → guarded verified canonical persist/rollback → coherent legacy mirrors → peer reconciliation.\n- Covered writers: ordinary state changes, deletes/Undo, import/restore, startup migration/recovery/healing, lifecycle/resume preferences, recent-text/export/onboarding auxiliary personal keys and coalesced reading-position persistence.\n- Schemas remain storage 8 / personal snapshot 5.\n- Corpus/speaker/stable-ID/Search/typography/Repères/PWA identity/backup/Hub/unrelated SW behavior remain protected.\n- `VER-LINEAGE-24H-01`: `SEPARATE_VERSION_SIMPLIFICATION_REQUIRED`; therefore this P0 repair remains on the historically coherent legacy line `v101.143 R1`.\n- The exact ZIP must be externally reopened and SHA-bound; physical/live/PWA/offline/AT gates remain separate.\n''',encoding='utf-8')
 # Exact self-contained repair evidence included in the engineering package; fresh per-release evidence pack remains external.
 ev=out/'evidence/v101143_r1';ev.mkdir(parents=True,exist_ok=True);shutil.copy2(patch_file,ev/'CONC_24H_01_RUNTIME_INDEX_PATCH_R1.diff')
 writej(ev/'AUTHORITY_REBASE_RECEIPT.json',{'schema':'L24H_CONC24H01_AUTHORITY_REBASE_V1','repair_id':'CONC-24H-01','original_authorization_file_sha256':AUTH_SHA,'original_authorized_predecessor':'v101.141 R1','rebase_owner_instruction':'these are the latest versions. use them instead','rebased_predecessor':BASE_VERSION,'rebased_predecessor_sha256':BASE_SHA,'rebase_condition':'personal-write implementation equivalence v101.141 -> v101.142 verified before mutation','scope_broadened':False})
 writej(ev/'IMPLEMENTED_CONCURRENCY_MUTATION_LEDGER.json',{'schema':'L24H_CONC24H01_IMPLEMENTED_LEDGER_V1','version':VERSION,'build_revision':REV,'repair_id':'CONC-24H-01','runtime_patch_sha256':PATCH_SHA,'lock_name':LOCK,'changed_functional_domains':['personal-state commit serialization','operation-level merge/conflict semantics','low-level canonical/mirror lock guards','peer reconciliation','import confirmation race guard','startup migration/recovery serialization','passive reading-position coalescing/conflict','auxiliary personal-key serialization'],'mechanical_release_bindings':['APP_VERSION/stage/build date','Service Worker cache identity only','manifest non-identity version field','version.json/current package metadata'],'protected_domains':['corpus text','speaker semantics','stable IDs/order','Search semantics/cap','typography/contrast','Repères semantics','manifest id/start_url/scope','backup schema','Hub architecture','unrelated Service Worker logic'],'storage_schema':8,'personal_snapshot_schema':5})
 # Current metadata.
 writej(out/'metadata/build_provenance.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,'baseline_version':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,'baseline_state_document_sha256':STATE_SHA,'owner_authorization_template_sha256':AUTH_SHA,'edition_1_5_sha256':ED15_SHA,'authorization_rebase':'Owner explicitly instructed use of supplied v101.142 R1 latest package instead of v101.141; personal-write implementation equivalence 141->142 verified before mutation.','support_floor':'FULL_SUPPORT_IOS_IPADOS_15_4_PLUS_AND_EQUIVALENT_MODERN_ANDROID_SAMSUNG__OLDER_BEST_EFFORT','repair_id':'CONC-24H-01','runtime_patch_sha256':PATCH_SHA,'lock_name':LOCK,'version_lineage_gate':'VER-LINEAGE-24H-01','version_lineage_outcome':'SEPARATE_VERSION_SIMPLIFICATION_REQUIRED','protected_changes':{'corpus_text':0,'speaker_semantics':0,'stable_ids_order':0,'search_semantics_cap':0,'typography_contrast':0,'reperes_semantics':0,'manifest_identity_fields':0,'backup_schema':0,'unrelated_service_worker_logic':0,'storage_schema':0,'personal_snapshot_schema':0},'final_validation':'EXTERNAL_EXACT_ZIP_REOPEN_REQUIRED'})
 writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_evidence_location':'EXTERNAL_SHA_BOUND_CONC24H01_HANDOFF_EVIDENCE_PACK','immediate_build_predecessor':{'version':BASE_VERSION,'sha256':BASE_SHA},'repair_id':'CONC-24H-01','authority_rebase':'v101.142 R1 supersedes v101.141 R1 as repair predecessor by explicit owner instruction','inherited_content_authority':'v101.142 R1 corpus, Search, speaker authority and native visible-flow topology inherited byte-for-byte','version_lineage_gate':'VER-LINEAGE-24H-01','version_lineage_outcome':'SEPARATE_VERSION_SIMPLIFICATION_REQUIRED'})
 writej(out/'metadata/current_gate_map.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'internal_gates':['exact v101.142 R1 SHA binding','v101.141->v101.142 personal-write equivalence before rebase','complete personal-write-path inventory','operation-level concurrency merge/conflict semantics','defect-sensitive stale-whole-snapshot mutant','exact persistence failure/rollback semantics','import confirmation-race protection','future-schema guard inside lock','legacy mirror parity','rapid/conflicting reading-position persistence','protected corpus/Search/speaker/topology/schema/PWA-identity parity','deterministic package rebuild','four-pass adversarial audit','fresh exact-ZIP reopened-package audit'],'external_open_gates':['physical iPad/iPhone/Samsung multi-context concurrency','live-origin exact-byte binding','installed PWA update from deployed v101.142 R1 to v101.143 R1','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'],'public_release':'UNAUTHORIZED'})
 writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'package_rule':'Package does not self-certify final ZIP bytes; exact frozen v101.143 R1 ZIP requires external SHA-bound reopened-package audit and handback evidence.','immediate_build_predecessor':BASE_VERSION,'immediate_build_predecessor_sha256':BASE_SHA,'repair_id':'CONC-24H-01','corpus_text_changed':False,'search_code_changed':False,'speaker_authority_changed':False,'native_visible_flow_topology_changed':False,'storage_schema_changed':False,'personal_snapshot_schema_changed':False,'pwa_identity_fields_changed':False,'service_worker_logic_changed':False,'physical_device_claims':'NOT_TESTED','public_deployment_authorized':False})
 (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} scope authority — CONC-24H-01\n\nImmutable predecessor: `{BASE_VERSION}` SHA-256 `{BASE_SHA}`.\n\nAuthority chain: bounded `CONC-24H-01` authorization file SHA-256 `{AUTH_SHA}`, plus the owner's later explicit instruction to use the newly supplied exact v101.142 R1 package instead of v101.141 after write-path equivalence was verified. Edition 1.5 SHA-256 `{ED15_SHA}` grants no mutation authority and is a policy overlay only.\n\nAllowed: only personal-write mechanics necessary to guarantee that already-committed independent personal-state changes are not silently lost, plus mechanically necessary successor/version/cache/evidence bindings.\n\nProtected: corpus, speaker semantics, stable IDs/order, Search semantics/cap, typography/contrast/Repères semantics, manifest identity-critical fields, backup schema, Hub architecture and unrelated Service Worker/update behavior.\n''',encoding='utf-8')
 writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_builder':'scripts/build_v101143_r1_conc24h01.py','builder_contract':'Exact SHA-bound v101.142 R1 predecessor + exact CONC-24H-01 runtime patch SHA; protected-domain parity; deterministic manifests/freeze; no unrelated runtime mutation.','qa_evidence':'External SHA-bound CONC-24H-01 per-release Evidence Pack and §54A handback.'})
 writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'active_documents':['README.md','REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','reports/V101143_R1_CONC_24H_01_PERSONAL_STATE_CONCURRENCY_SUCCESSOR.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/current_gate_map.json','metadata/release_evidence_lifecycle.json','metadata/scope_escalation_authority.md','metadata/current_tooling_inventory.json'],'active_test_artifacts_external':['CONC-24H-01 per-release QA Evidence Pack bound to final successor SHA','§54A handback package to Master Governance'],'inactive_predecessor_evidence_retained':['reports/V101142_R1_NATIVE_VISIBLE_FLOW_TOPOLOGY_SUCCESSOR.md','evidence/v101142_r1/'],'historical_reports_root':'reports/historical/','rule':'Only listed active documents are current. Existing v101.142 evidence remains immutable predecessor evidence, not current successor evidence.'})
 # Embed current builder for deterministic handoff.
 shutil.copy2(Path(__file__),out/'scripts/build_v101143_r1_conc24h01.py')
 # Build overlay + self-excluding hash/package manifests.
 cur=files(out);removed=sorted(set(base_files)-set(cur));assert removed==[],removed
 changed=sorted(k for k,p in cur.items() if k not in base_hash or sha(p)!=base_hash[k])
 writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101143_R1_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,'repair_id':'CONC-24H-01','runtime_patch_sha256':PATCH_SHA,'changed_or_added':sorted(set(changed)|{'metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json'}),'removed':[],'corpus_text_delta':'ZERO','speaker_semantics_delta':'ZERO','stable_id_order_delta':'ZERO','search_semantics_cap_delta':'ZERO','typography_contrast_delta':'ZERO','reperes_semantics_delta':'ZERO','manifest_identity_delta':'ZERO','backup_schema_delta':'ZERO','unrelated_service_worker_logic_delta':'ZERO','storage_schema_delta':'ZERO','personal_snapshot_schema_delta':'ZERO'})
 ex={'metadata/hash_manifest.json','metadata/package_manifest.json'};lst=[]
 for k,p in sorted(files(out).items()):
  if k in ex:continue
  lst.append({'path':k,'size':p.stat().st_size,'sha256':sha(p)})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
 writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
 final_files=files(out)
 final_changed=sorted(k for k,p in final_files.items() if k not in base_hash or sha(p)!=base_hash[k])
 zsha=freeze(out,out_zip)
 return {'version':VERSION,'revision':REV,'stage':STAGE,'base_sha256':BASE_SHA,'patch_sha256':PATCH_SHA,'files':len(final_files),'zip_sha256':zsha,'zip_size':out_zip.stat().st_size,'zip_members':len(zipfile.ZipFile(out_zip).infolist()),'pre_manifest_changed_or_added_count':len(changed),'final_changed_or_added_count':len(final_changed)}
if __name__=='__main__':
 if len(sys.argv)!=5:raise SystemExit('Usage: build.py <v101142_R1.zip> <runtime_patch.diff> <out_dir> <out.zip>')
 print(json.dumps(build(*sys.argv[1:]),ensure_ascii=False,indent=2))
