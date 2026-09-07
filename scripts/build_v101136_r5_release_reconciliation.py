from pathlib import Path
import csv,json,hashlib,zipfile,shutil,re,sys
BASE_SHA='7af0df0f37552f603d58aa407e94d9bd8f2719bd12b8b7313538d7b5d575668b'
LEDGER97_SHA='f9c89f2fdcb0f6588cb4250e8ea4bc00d9ccf1f51900a83d77e6e3b415ae9394'
CONTENT_PREDECESSOR_SHA='cf8b688e649b2ef3f7c36768691c6a647d9d1e9eec85c90ba697dc2a05ef26fc'
VERSION='v101.136'; REV='R5'; DATE='2026-09-07'; CACHE='luisa-24h-v101-136-r5'; STAGE='INTERIM_CLOSED_97_SUCCESSOR_R5_FOUR_PASS_RELEASE_RECONCILED'
R6_SHA='35ee5c69fe0468d2e3ee2d963a7fa6667169c24d6c8023da2726b4cd8b50ed20'
R6_MAN='0d04190b166932086ed45141368bd4ae88b5a22806ca1e525a3e6a60a267f3ad'
RID='PASSION24.TEXT.RELATED_HOUR_13.BODY.P124'

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def files(root): return {p.relative_to(root).as_posix():p for p in Path(root).rglob('*') if p.is_file()}
def writej(p,o): p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def extract(t,n):
 m=re.search(rf'const\s+{re.escape(n)}\s*=\s*',t); assert m,n
 o,e=json.JSONDecoder().raw_decode(t[m.end():]); return o,m.end(),m.end()+e

def canonical_raw(t):
 c,_,_=extract(t,'CORPUS'); tl,_,_=extract(t,'TEXT_LIBRARY'); d={}
 def add(x): d[x['id']]=x['t']
 for h in c['hours']:
  for k in ('paragraphs','reflections'):
   for x in h.get(k,[]): add(x)
  for sub in h.get('subsections',[]):
   for x in sub.get('paragraphs',[]): add(x)
 for pr in c.get('prayers',[]):
  for x in pr.get('paragraphs',[]): add(x)
 for sec in c.get('sections',[]):
  for x in sec.get('paragraphs',[]): add(x)
 for it in tl:
  iid=it['id'];
  if iid.startswith('PASSION24.TEXT.') and isinstance(it.get('title'),str): d[f'{iid}.TITLE']=it['title']
  p=it.get('practice_options') or it.get('practice') or []
  if isinstance(p,list):
   for j,x in enumerate(p,1):
    if isinstance(x,str): d[f'{iid}.PRACTICE.P{j:03d}']=x
  body=it.get('body') or []; nums=it.get('body_stable_numbers') or []
  for i,x in enumerate(body):
   n=nums[i] if i<len(nums) else i+1
   try:n=f'{int(n):03d}'
   except:n=str(n)
   d[f'{iid}.BODY.P{n}']=x
 return d

def build(base_zip,out):
 base_zip=Path(base_zip);out=Path(out);shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
 assert sha_file(base_zip)==BASE_SHA,(sha_file(base_zip),BASE_SHA)
 with zipfile.ZipFile(base_zip) as z:
  assert z.testzip() is None; z.extractall(out)
 basehash={k:sha_file(p) for k,p in files(out).items()}
 src=(out/'index.html').read_text(encoding='utf-8'); assert src==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
 raw_before=canonical_raw(src); assert len(raw_before)==4613 and RID in raw_before and 'à la porte de leur cœur' in raw_before[RID]
 ledger=out/'evidence/v101136_r4/AUTHORIZED_MUTATION_UNIVERSE_97.csv'; assert sha_file(ledger)==LEDGER97_SHA
 rows=list(csv.DictReader(ledger.open(encoding='utf-8-sig'))); assert len(rows)==97 and len({r['record_id'] for r in rows})==97
 # Runtime identity only; no canonical text mutation.
 oldstage="const APP_EVIDENCE_STAGE = 'INTERIM_CLOSED_97_SUCCESSOR_R4_SINGLE_GRAMMAR_FIX';"; assert src.count(oldstage)==1
 src=src.replace(oldstage,f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
 src=re.sub(r"const BUILD_DATE = '2026-09-07';[^\n]*",f"const BUILD_DATE = '{DATE}'; // {VERSION} {REV} / 97-record corpus unchanged from R4; release-engineering reconciliation only",src,count=1)
 (out/'index.html').write_text(src,encoding='utf-8');(out/'luisa_24_heures.html').write_text(src,encoding='utf-8')
 assert canonical_raw(src)==raw_before
 # SW/cache identity.
 sw=(out/'sw.js').read_text(encoding='utf-8'); assert "const CACHE_NAME = 'luisa-24h-v101-136-r4';" in sw
 sw=sw.replace("const CACHE_NAME = 'luisa-24h-v101-136-r4';",f"const CACHE_NAME = '{CACHE}';",1).replace('/* v101.136 R4 */','/* v101.136 R5 */',1)
 (out/'sw.js').write_text(sw,encoding='utf-8')
 # Device QA docs: eliminate R3/R4 procedural staleness and bind to R5.
 checklist=(out/'REAL_DEVICE_QA_CHECKLIST.md').read_text(encoding='utf-8')
 checklist=checklist.replace('# Real-device QA checklist — v101.136 R4','# Real-device QA checklist — v101.136 R5')
 checklist=checklist.replace('exact **v101.136 R4** GitHub/device-test candidate','exact **v101.136 R5** GitHub/device-test candidate')
 checklist=checklist.replace('`build_revision = R4`','`build_revision = R5`').replace('luisa-24h-v101-136-r4','luisa-24h-v101-136-r5')
 checklist=checklist.replace('INTERIM_CLOSED_97_SUCCESSOR_R4_SINGLE_GRAMMAR_FIX',STAGE)
 checklist=checklist.replace('Do not use v101.136 R1, R2 or R3 for deployment; R4 supersedes them for device testing. R4 adds exactly one authorized grammar repair to R3.',
   'Do not use v101.136 R1, R2, R3 or R4 for deployment; R5 supersedes them for device testing. R5 changes release engineering/documentation only; the 97-record canonical corpus is identical to R4.')
 checklist=checklist.replace('external R3 release receipt','external R5 release receipt')
 checklist=checklist.replace('`build_revision = R4`','`build_revision = R5`')
 checklist=checklist.replace('becomes **v101.136 / R3**','becomes **v101.136 / R5**')
 checklist=checklist.replace('v101.135, R1/R2 cache','v101.135, R1/R2/R3/R4 cache')
 checklist=checklist.replace('online load of v101.136 R4','online load of v101.136 R5')
 (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(checklist,encoding='utf-8')
 # Results template.
 p=out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'; data=p.read_text(encoding='utf-8-sig')
 data=data.replace('build_revision R4','build_revision R5').replace('v101.136 R4','v101.136 R5').replace('luisa-24h-v101-136-r4','luisa-24h-v101-136-r5')
 p.write_text(data,encoding='utf-8-sig')
 # Archive R4 current report, write R5 report.
 hist=out/'reports/historical/v101136_r4';hist.mkdir(parents=True,exist_ok=True)
 rp=out/'reports/V101136_R4_SINGLE_GRAMMAR_FIX.md'
 if rp.exists(): shutil.move(str(rp),str(hist/rp.name))
 report=out/'reports/V101136_R5_FOUR_PASS_RELEASE_RECONCILIATION.md'
 report.write_text(f'''# v101.136 R5 — Four-pass release-engineering reconciliation\n\n- Release-engineering predecessor: v101.136 R4 `{BASE_SHA}`.\n- Public app version remains **v101.136**; build revision is **R5**.\n- Canonical devotional corpus is **byte-identical to R4**; R5 introduces **0 new canonical text records**.\n- Total canonical delta relative to immutable v101.135 remains **97 records = 84 local + 13 official-R6 sync**.\n- Governing 97-record authority ledger remains `{LEDGER97_SHA}`.\n- R4 four-pass audit found four release-package defects: two stale R3 device-checklist instructions, a stale `INTERNAL_VALIDATION_REQUIRED` status, and contradictory empty `known_blockers` despite open external gates.\n- R5 corrects those release-engineering/documentation defects and makes the current builder portable: it accepts the SHA-bound predecessor ZIP as an explicit input rather than relying on ephemeral absolute build paths.\n- H23 remains unchanged; no new H23 source-critical finding is authorized. The single R4 upstream-hold exception at `{RID}` remains exactly bounded to the already-authorized insertion `de `.\n- Physical-device, installed-PWA, true-offline, VoiceOver/TalkBack and live-origin exact-byte gates remain open. Final public deployment remains unauthorized.\n- This package does not self-certify its own final ZIP hash; controlled device testing requires the accompanying external SHA-bound R5 four-pass/final-recheck receipt.\n''',encoding='utf-8')
 # Evidence R5 trigger/reconciliation.
 ev=out/'evidence/v101136_r5';ev.mkdir(parents=True,exist_ok=True)
 writej(ev/'R4_FOUR_PASS_TRIGGER.json',{
  'schema':'L24H_V101136_R5_R4_FOUR_PASS_TRIGGER_V1','predecessor_sha256':BASE_SHA,'canonical_defects_found':0,'runtime_defects_found':0,
  'release_package_defects_found':4,'defects':[
   {'id':'R4-DOC-01','file':'REAL_DEVICE_QA_CHECKLIST.md','line':14,'old':'external R3 release receipt','new':'external R5 release receipt'},
   {'id':'R4-DOC-02','file':'REAL_DEVICE_QA_CHECKLIST.md','line':24,'old':'v101.136 / R3','new':'v101.136 / R5'},
   {'id':'R4-META-01','file':'version.json','field':'overall_release_status','old':'R4_INTERNAL_VALIDATION_REQUIRED...','new':'R5_CONTROLLED_DEVICE_TEST_CANDIDATE...'},
   {'id':'R4-META-02','file':'version.json','field':'known_blockers','old':[],'new':'explicit external open release gates'}],
  'r4_pass1_rebuild':'876/876 files identical; exact ZIP SHA reproduced','r4_pass2_runtime':'625/625 PASS','r4_pass2_static':'47/47 PASS'
 })
 # README.
 (out/'README.md').write_text(f'''# Les 24 Heures de la Passion — v101.136 R5\n\nControlled device-test candidate. Canonical devotional corpus is unchanged from R4 and remains exactly **97 authorized changed records relative to immutable v101.135 = 84 local corrections + 13 official-LDC-R6 derivative synchronizations**.\n\nR5 is a release-engineering/documentation reconciliation only: **0 new canonical text mutations**. It corrects stale device-test instructions/status metadata discovered by the R4 four-pass audit and replaces the current builder with a portable SHA-bound predecessor-input builder.\n\nThe R4 grammar repair `PASSION24.TEXT.RELATED_HOUR_13.BODY.P124`, `à la porte leur cœur` → `à la porte de leur cœur`, remains present and authorized. H23 remains unchanged.\n\nR5 supersedes R1/R2/R3/R4 for deployment/device testing. Final public release remains unauthorized pending physical-device, installed-PWA update/persistence, true-offline, accessibility and live-origin exact-byte gates.\n''',encoding='utf-8')
 # Version and current metadata.
 v=json.loads((out/'version.json').read_text());gates=[
  'physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update v101.135→v101.136 R5','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing']
 v.update({'app_version':VERSION,'build_revision':REV,'build_date':DATE,'cache_name':CACHE,
  'release_scope':'Governed v101.136 R5 device-test candidate. Canonical corpus is unchanged from R4 and remains exactly 97 records different from immutable v101.135 = 84 local corrections + 13 official-R6 derivative sync. R5 is release-engineering/documentation only and introduces no new canonical text mutation.',
  'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.136 R5.',
  'overall_release_status':'R5_CONTROLLED_DEVICE_TEST_CANDIDATE__FINAL_PUBLIC_DEPLOYMENT_UNAUTHORIZED',
  'known_blockers':gates,'external_open_gates':gates,
  'postfreeze_reopen_evidence':'Package does not self-certify its final ZIP hash. Controlled device testing requires the accompanying external SHA-bound R5 four-pass and final-recheck receipt.'})
 writej(out/'version.json',v)
 m=json.loads((out/'manifest.json').read_text());m['version']=VERSION;m['build_revision']=REV;writej(out/'manifest.json',m)
 active=['README.md','REAL_DEVICE_QA_CHECKLIST.md','reports/V101136_R5_FOUR_PASS_RELEASE_RECONCILIATION.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md']
 writej(out/'metadata/active_report_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'active_documents':active,'active_test_artifacts':['REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'],'historical_reports_root':'reports/historical/','rule':'Only listed active documents are current; predecessor/superseded reports are historical.'})
 writej(out/'metadata/build_provenance.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,'release_engineering_baseline':'v101.136 R4','release_engineering_baseline_zip_sha256':BASE_SHA,'content_predecessor_version':'v101.135','content_predecessor_zip_sha256':CONTENT_PREDECESSOR_SHA,'authorized_ledger_97_sha256':LEDGER97_SHA,'canonical_text_changed_from_r4':False,'canonical_text_delta_from_r4_records':0,'canonical_total_delta_from_v101135_records':97,'upstream_hold_exception_records':1,'other_upstream_findings_consumed':False,'stable_record_ids_unchanged':True,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'final_validation':'EXTERNAL_RECEIPT_REQUIRED_FOR_EXACT_ZIP'})
 writej(out/'metadata/current_evidence_lineage.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'content_authority_root':'evidence/v101136_r4','release_engineering_authority_root':'evidence/v101136_r5','content_predecessor_24h':{'version':'v101.135','sha256':CONTENT_PREDECESSOR_SHA},'release_engineering_predecessor':{'version':'v101.136 R4','sha256':BASE_SHA},'authorized_ledger_97_sha256':LEDGER97_SHA,'governing_ldc_r6':{'version':'v2.19.65-R1B','official_zip_sha256':R6_SHA,'corpus_manifest_sha256':R6_MAN},'r5_canonical_delta_records':0,'canonical_total_delta_from_v101135_records':97,'upstream_hold_exception_records':1,'other_upstream_findings_consumed':False,'final_exact_zip_validation':'EXTERNAL_RECEIPT_REQUIRED_FOR_THIS_EXACT_ZIP'})
 (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} Scope Authority\n\nCanonical content authority remains exactly **97 records relative to immutable v101.135** under ledger `{LEDGER97_SHA}`. R5 authorizes **zero** additional canonical text mutations and is release-engineering/documentation only. No H23 source-critical finding is authorized. The existing R4 exception at `{RID}` remains limited to the exact previously authorized insertion `de `; no other upstream finding or action is authorized. Any further canonical text change requires new authority.\n''',encoding='utf-8')
 writej(out/'metadata/release_evidence_lifecycle.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'package_rule':'Package does not self-certify final ZIP bytes. The exact R5 ZIP must be SHA-bound by the external four-pass/final-recheck receipt before controlled device testing.','internal_package_content_status':'RECONCILED_FOR_EXTERNAL_EXACT_ZIP_RECHECK','physical_device_claims':'NOT_TESTED','public_deployment_authorized':False})
 writej(out/'metadata/current_gate_map.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'internal_package_content_gates':['exact R4→R5 zero-record canonical delta','exact v135→R5 97-record canonical delta','runtime/package regression','active-report line audit','contradiction/stale-evidence scan','final reopened exact-ZIP recheck'],'external_receipt_required':True,'external_open_gates':['physical devices','live-origin exact-byte binding','installed-PWA update/persistence','true offline cold reopen','VoiceOver/TalkBack'],'public_release':'UNAUTHORIZED'})
 # portable builder: store this script, documented CLI, no absolute predecessor path.
 shutil.copy2(Path(__file__),out/'scripts/build_v101136_r5_release_reconciliation.py')
 writej(out/'metadata/current_tooling_inventory.json',{'version':VERSION,'build_revision':REV,'stage':STAGE,'current_builder':'scripts/build_v101136_r5_release_reconciliation.py','builder_cli':'python scripts/build_v101136_r5_release_reconciliation.py <sha-bound-v101136-R4-predecessor.zip> <out_dir> <out_zip>','predecessor_builder':'scripts/build_v101136_r4_single_grammar_fix.py retained as historical tooling','runtime_validation':'external exact-ZIP v101.136 R5 harnesses and final reopened recheck required'})
 writej(out/'metadata/builder_input_manifest.json',{'version':VERSION,'build_revision':REV,'release_engineering_predecessor_version':'v101.136 R4','release_engineering_predecessor_zip_sha256':BASE_SHA,'content_predecessor_v101135_zip_sha256':CONTENT_PREDECESSOR_SHA,'authorized_ledger_97_sha256':LEDGER97_SHA,'governing_ldc_r6_zip_sha256':R6_SHA,'governing_ldc_r6_corpus_manifest_sha256':R6_MAN,'current_builder_input_contract':'Explicit predecessor ZIP path supplied by CLI; builder verifies fixed SHA-256 before extraction. No ephemeral absolute build path is required.'})
 # Overlay + manifests.
 cur=files(out); changed=sorted(k for k,p in cur.items() if k not in basehash or sha_file(p)!=basehash[k]); removed=sorted(set(basehash)-set(cur))
 for x in ['metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json']:
  if x not in changed:changed.append(x)
 writej(out/'metadata/full_build_overlay_manifest.json',{'schema':'L24H_V101136_R5_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':'v101.136 R4','baseline_zip_sha256':BASE_SHA,'changed_or_added':sorted(changed),'removed':removed})
 ex={'metadata/hash_manifest.json','metadata/package_manifest.json'};lst=[]
 for k,p in sorted(files(out).items()):
  if k in ex:continue
  lst.append({'path':k,'size':p.stat().st_size,'sha256':sha_file(p)})
 writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
 writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})
 assert canonical_raw((out/'index.html').read_text(encoding='utf-8'))==raw_before
 return {'version':VERSION,'revision':REV,'files':len(files(out)),'canonical_delta_from_r4':0,'canonical_total_delta_from_v101135':97,'ledger97_sha256':LEDGER97_SHA,'cache':CACHE,'stage':STAGE}

def freeze(root,zp):
 root=Path(root);zp=Path(zp);zp.unlink(missing_ok=True)
 with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(root.rglob('*')):
   if not p.is_file():continue
   rel=p.relative_to(root).as_posix();info=zipfile.ZipInfo(rel,(2026,9,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16);z.writestr(info,p.read_bytes())
 return sha_file(zp)

if __name__=='__main__':
 if len(sys.argv)!=4: raise SystemExit('Usage: build_v101136_r5_release_reconciliation.py <R4_predecessor.zip> <out_dir> <out_zip>')
 r=build(sys.argv[1],sys.argv[2]);h=freeze(sys.argv[2],sys.argv[3]);print(json.dumps(r,indent=2,ensure_ascii=False));print('ZIP',h)
