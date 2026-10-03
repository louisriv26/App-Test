#!/usr/bin/env python3
from pathlib import Path
import shutil,re,json,hashlib,base64
R=Path('.'); src=R/'24h-v120-b6-blind-closure'; dst=R/'24h-v120-b8-update-activation-closure'
if dst.exists(): raise SystemExit('destination exists')
shutil.copytree(src,dst)
NEW_BUILD='B8'; NEW_SEQ=120000008
OLD_ID='24h-v120-b6-20261002-blind-adversarial-closure'
NEW_ID='24h-v120-b8-20261003-update-activation-closure'
NEW_STAGE='24H_V120_UPDATE_ACTIVATION_CLOSURE_B8'
def token(x): return "'sha256-"+base64.b64encode(hashlib.sha256(x.encode()).digest()).decode()+"'"
def csp_rebind(html):
    cm=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(">)',html)
    if not cm: raise RuntimeError('CSP missing')
    policy=cm.group(2)
    for tag,name in [('script','script-src-elem'),('style','style-src-elem')]:
        blocks=re.findall(r'<'+tag+r'(?![^>]*\bsrc=)[^>]*>(.*?)</'+tag+r'>',html,re.S|re.I)
        val=' '.join(token(x) for x in blocks)
        pat=re.compile(r'(^|;\s*)'+re.escape(name)+r'\s+[^;]+')
        m=pat.search(policy)
        policy=(policy[:m.start()]+m.group(1)+name+' '+val+policy[m.end():]) if m else (policy.rstrip('; ')+'; '+name+' '+val)
    return html[:cm.start(2)]+policy+html[cm.end(2):]
OLD_WAIT="""      active=await waitForActiveRelease(registration,remote,15000);
      if (!active) throw new Error('target_worker_not_active');"""
NEW_WAIT="""      const activated=await waitForWorkerState(prepared.worker,['activated'],15000);
      if (!activated) throw new Error('target_worker_not_active');
      const activatedInfo=await queryWorkerRelease(activated);
      if (!workerMatchesRemote(activatedInfo,remote)) throw new Error('target_worker_identity_mismatch_after_activation');
      active=activated;"""
for nm in ['index.html','luisa_24_heures.html']:
    p=dst/nm; s=p.read_text(encoding='utf-8')
    pairs=[
      ("const BUILD_REVISION = 'B6';","const BUILD_REVISION = 'B8';"),
      ("const APP_RELEASE_SEQUENCE = 120000001;",f"const APP_RELEASE_SEQUENCE = {NEW_SEQ};"),
      ("const APP_RELEASE_ID = '"+OLD_ID+"';","const APP_RELEASE_ID = '"+NEW_ID+"';"),
      ("const APP_EVIDENCE_STAGE = '24H_V120_BLIND_ADVERSARIAL_CLOSURE_B6';","const APP_EVIDENCE_STAGE = '"+NEW_STAGE+"';"),
      (OLD_WAIT,NEW_WAIT)]
    for old,new in pairs:
        if s.count(old)!=1: raise RuntimeError('shell target count '+str(s.count(old))+' '+old[:70])
        s=s.replace(old,new,1)
    p.write_text(csp_rebind(s),encoding='utf-8')
if (dst/'index.html').read_bytes()!=(dst/'luisa_24_heures.html').read_bytes(): raise RuntimeError('shell divergence')
shell_sha=hashlib.sha256((dst/'luisa_24_heures.html').read_bytes()).hexdigest()

p=dst/'manifest.json'; m=json.loads(p.read_text(encoding='utf-8'))
m.update({'version':'v120','build_revision':NEW_BUILD,'build':NEW_BUILD,'release_sequence':NEW_SEQ,'release_id':NEW_ID,'start_url':'./luisa_24_heures.html'})
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=dst/'sw.js'; s=p.read_text(encoding='utf-8')
s=re.sub(r'^/\*.*?\*/','/* v120 B8 — bounded update-activation successor from failed B6; page orchestration repaired, protected content and service-worker semantics otherwise unchanged. */',s,count=1,flags=re.S)
for old,new in [
 ("const BUILD_REVISION = 'B6';","const BUILD_REVISION = 'B8';"),
 ("const RELEASE_SEQUENCE = 120000001;",f"const RELEASE_SEQUENCE = {NEW_SEQ};"),
 ("const RELEASE_ID = '"+OLD_ID+"';","const RELEASE_ID = '"+NEW_ID+"';")]:
    if s.count(old)!=1: raise RuntimeError('SW target count '+str(s.count(old))+' '+old)
    s=s.replace(old,new,1)
s=re.sub(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';","const CANONICAL_SHELL_SHA256 = '"+shell_sha+"';",s,count=1)
cache_expr='const CACHE_NAME = '+chr(96)+chr(36)+'{CACHE_PREFIX}v120-b8'+chr(96)+';'
s=re.sub(r'const CACHE_NAME = .*?;',cache_expr,s,count=1)
p.write_text(s,encoding='utf-8')

p=dst/'version.json'; v=json.loads(p.read_text(encoding='utf-8'))
v.update({
 'app_version':'v120','build_revision':NEW_BUILD,'release_sequence':NEW_SEQ,'release_id':NEW_ID,'build_date':'2026-10-03',
 'cache_name':'scope-derived:luisa-24h-<scope-fingerprint>-v120-b8','canonical_shell':'./luisa_24_heures.html','canonical_shell_sha256':shell_sha,
 'release_scope':'v120/B8 bounded successor to failed v120/B6 under the 2026-10-03 full QA. Repairs only the page-side Update-v2 activation wait: after a verified ACTIVATE_UPDATE_V2 acknowledgement, wait on the exact prepared worker statechange to activated, verify its release identity, then verify controller takeover. Corpus, Search, provenance, personal-state, backup/import, native-selection and service-worker activation semantics are unchanged.',
 'real_device_status':'V120_B8_CANDIDATE__UPDATE_ACTIVATION_REPAIR__REAL_DEVICE_GATES_OPEN',
 'overall_release_status':'V120_B8_UPDATE_ACTIVATION_REPAIR_CANDIDATE__PRODUCTION_NOT_AUTHORIZED',
 'functional_freeze_status':'V120_B8_UPDATE_ACTIVATION_REPAIR__PROTECTED_CONTENT_AND_NON_UPDATE_SURFACES_UNCHANGED__PHYSICAL_GATES_OPEN',
 'postfreeze_reopen_evidence':'B8 supersedes exact B6 after fresh full-QA falsification found a reproducible page-driven Update-v2 activation defect. Direct worker activation passed; page refresh failed target_worker_not_active. Event-driven waiting on the exact prepared worker was proven on unchanged B6 before mutation.'
})
for key in ['known_blockers','external_open_gates']:
    v[key]=[str(x).replace('v120/B6','v120/B8').replace('v120/B5','v120/B8') for x in (v.get(key) or [])]
page=(dst/'index.html').read_text(encoding='utf-8')
scripts=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',page,re.S|re.I)
styles=re.findall(r'<style(?![^>]*\bsrc=)[^>]*>(.*?)</style>',page,re.S|re.I)
v['security_inline_script_sha256_base64']=token(scripts[0]).strip("'") if len(scripts)==1 else [token(x).strip("'") for x in scripts]
v['security_inline_style_sha256_base64']=[token(x).strip("'") for x in styles]
v['security_stage_status']='CSP3_ARCHITECTURE_PRESERVED__V120_B8_REBOUND__SERVICE_WORKER_CANONICAL_SHELL_HASH_'+shell_sha.upper()
v['full_qa_20261003_update_activation_repair']={
 'status':'CORRECTED_PENDING_FRESH_SUCCESSOR_QUALIFICATION',
 'superseded_candidate':'v120/B6','superseded_tree':'977b1d9c9475988d03aa6debb78cd9370e6e1192',
 'defect':'B24H-FQA-001: v119/B1 to v120/B6 page-driven refresh prepared the correct waiting worker but refreshAppForUpdate failed after 15 seconds with target_worker_not_active, leaving v119 active and B6 waiting.',
 'root_cause':'After ACTIVATE_UPDATE_V2 was accepted, waitForActiveRelease repeatedly queried registration.active. The same B6 worker activated and claimed the controller when activation was awaited through its own statechange instead.',
 'repair':'Await waitForWorkerState on the exact prepared worker until activated, verify that worker identity, then retain the existing controller-release verification.',
 'proof':'Fresh unchanged-B6 event-driven activation proof passed: acknowledgement accepted, prepared worker activated, controller changed to exact B6.',
 'protected_surfaces':['CORPUS','TEXT_LIBRARY','SPEECH_DATA','Search semantics/results','provenance','personal-state schema/semantics','backup/import semantics','native-selection renderer and persistence','Update-v2 service-worker activation/isolation protocol'],
 'physical_pass_inferred':False,'production_deployment_authority':'NONE'}
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

allowed={'index.html','luisa_24_heures.html','manifest.json','sw.js','version.json'}
def sha(q): return hashlib.sha256(q.read_bytes()).hexdigest()
fa={str(q.relative_to(src)):sha(q) for q in src.rglob('*') if q.is_file()}
fb={str(q.relative_to(dst)):sha(q) for q in dst.rglob('*') if q.is_file()}
changed={k for k in set(fa)|set(fb) if fa.get(k)!=fb.get(k)}
if changed!=allowed: raise RuntimeError('unexpected mutation boundary '+repr(sorted(changed)))
for rel,h in fa.items():
    if rel not in allowed and fb.get(rel)!=h: raise RuntimeError('protected drift '+rel)
sw=(dst/'sw.js').read_text(encoding='utf-8')
assert f"const RELEASE_SEQUENCE = {NEW_SEQ};" in sw
assert cache_expr in sw
assert "const CANONICAL_SHELL_SHA256 = '"+shell_sha+"';" in sw
assert OLD_WAIT not in page
assert "const activated=await waitForWorkerState(prepared.worker,['activated'],15000);" in page
print('24H_V120_B8_STAGE_PASS',shell_sha)
