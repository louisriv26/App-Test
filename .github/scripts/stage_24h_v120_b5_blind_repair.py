
#!/usr/bin/env python3
from pathlib import Path
import shutil,re,json,hashlib,base64
R=Path('.'); src=R/'24h-v120-b4-darkmode'; dst=R/'24h-v120-b5-blind-repair'
if dst.exists(): raise SystemExit('destination already exists')
shutil.copytree(src,dst)
NEW_RELEASE_ID='24h-v120-b5-20261002-blind-adversarial-repair'; NEW_STAGE='24H_V120_BLIND_ADVERSARIAL_REPAIR_B5'; NEW_BUILD='B5'
def hash_token(text): return "'sha256-"+base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()+"'"
def rebuild_csp(html):
    cm=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(">)',html)
    if not cm: raise RuntimeError('CSP meta missing')
    csp=cm.group(2)
    scripts=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',html,re.S|re.I)
    styles=re.findall(r'<style(?![^>]*\bsrc=)[^>]*>(.*?)</style>',html,re.S|re.I)
    def repl(policy,name,toks):
        val=' '.join(hash_token(x) for x in toks); pat=re.compile(r'(^|;\s*)'+re.escape(name)+r'\s+[^;]+'); m=pat.search(policy)
        if m:
            pre=m.group(1); return policy[:m.start()]+pre+name+' '+val+policy[m.end():]
        return policy.rstrip('; ')+'; '+name+' '+val
    csp=repl(csp,'script-src-elem',scripts); csp=repl(csp,'style-src-elem',styles)
    return html[:cm.start(2)]+csp+html[cm.end(2):]
for nm in ['index.html','luisa_24_heures.html']:
    p=dst/nm; s=p.read_text(encoding='utf-8')
    s=s.replace("const BUILD_REVISION = 'B1';","const BUILD_REVISION = 'B5';",1)
    s=s.replace("const APP_EVIDENCE_STAGE = '24H_V120_DARK_MODE_CLOSURE_B4';","const APP_EVIDENCE_STAGE = '24H_V120_BLIND_ADVERSARIAL_REPAIR_B5';",1)
    s=s.replace("const APP_RELEASE_ID = '24h-v120-b4-20261002-dark-mode-closure';","const APP_RELEASE_ID = '24h-v120-b5-20261002-blind-adversarial-repair';",1)
    p.write_text(rebuild_csp(s),encoding='utf-8')
if (dst/'index.html').read_bytes()!=(dst/'luisa_24_heures.html').read_bytes(): raise RuntimeError('shells diverged')
shell_sha=hashlib.sha256((dst/'luisa_24_heures.html').read_bytes()).hexdigest()
p=dst/'manifest.json'; m=json.loads(p.read_text(encoding='utf-8')); m.update({'version':'v120','build_revision':'B5','build':'B5','release_sequence':120000001,'release_id':NEW_RELEASE_ID,'start_url':'./luisa_24_heures.html'}); p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=dst/'sw.js'; s=p.read_text(encoding='utf-8')
s=re.sub(r'^/\*.*?\*/','/* v120 B5 — blind-adversarial release-shell repair from failed B4: release identity, CSP, cache and canonical-shell bindings reconciled; protected corpus/Search/provenance/personal-state/backup semantics unchanged. */',s,count=1,flags=re.S)
s=s.replace("const BUILD_REVISION = 'B1';","const BUILD_REVISION = 'B5';",1)
s=re.sub(r"const RELEASE_ID = '[^']+';",f"const RELEASE_ID = '{NEW_RELEASE_ID}';",s,count=1)
s=re.sub(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell_sha}';",s,count=1)
s=re.sub(r"const CACHE_NAME = .*?;","const CACHE_NAME = " + chr(96) + "\${CACHE_PREFIX}v120-b5" + chr(96) + ";",s,count=1)
p.write_text(s,encoding='utf-8')
p=dst/'version.json'; v=json.loads(p.read_text(encoding='utf-8'))
v.update({'app_version':'v120','build_revision':'B5','release_sequence':120000001,'release_id':NEW_RELEASE_ID,'cache_name':'scope-derived:luisa-24h-<scope-fingerprint>-v120-b5','canonical_shell':'./luisa_24_heures.html','canonical_shell_sha256':shell_sha,'release_scope':'v120/B5 blind-adversarial release-shell correction from failed B4. Rebinds exact technical identity, CSP inline-script/style authorization, cache identity, canonical-shell hash and current physical-gate wording. No corpus, Search, provenance, personal-state, backup/import or update-protocol semantic change.','real_device_status':'V120_B5_CANDIDATE__BLIND_ADVERSARIAL_REPAIR__REAL_DEVICE_GATES_OPEN','overall_release_status':'V120_B5_BLIND_ADVERSARIAL_REPAIR_CANDIDATE__PRODUCTION_NOT_AUTHORIZED','functional_freeze_status':'V120_B5_BLIND_ADVERSARIAL_RELEASE_SHELL_CORRECTION__PROTECTED_FUNCTIONAL_AND_CONTENT_SURFACES_UNCHANGED__PHYSICAL_GATES_OPEN','postfreeze_reopen_evidence':'B5 is the bounded successor required by the independent blind audit of B4; B4 is failed/superseded. No devotional, Search, provenance, personal-state, backup/import or update-protocol semantic mutation is authorized.'})
page=(dst/'index.html').read_text(encoding='utf-8'); scripts=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',page,re.S|re.I); styles=re.findall(r'<style(?![^>]*\bsrc=)[^>]*>(.*?)</style>',page,re.S|re.I)
v['security_inline_script_sha256_base64']=hash_token(scripts[0]).strip("'") if len(scripts)==1 else [hash_token(x).strip("'") for x in scripts]
v['security_inline_style_sha256_base64']=[hash_token(x).strip("'") for x in styles]
v['security_stage_status']=f'CSP3_ARCHITECTURE_PRESERVED__V120_B5_INLINE_SCRIPT_AND_STYLE_HASHES_REBOUND_TO_EXACT_V120_B5_SUCCESSOR_SHELL__SERVICE_WORKER_CANONICAL_SHELL_HASH_BOUND_TO_EXACT_V120_B5_SHELL_{shell_sha.upper()}'
def gate(x):
    x=str(x)
    x=x.replace('Exact production v111/R36 → v119/B1 installed-PWA update/activation and acknowledged-state preservation on iPhone and iPad.','Exact production v119/B1 → v120/B5 installed-PWA update/activation and acknowledged-state preservation on iPhone and iPad.')
    x=x.replace('v119/B1 iPad H03/P013 physical A–D replay','v120/B5 iPad H03/P013 physical A–D replay')
    x=x.replace('v119/B1 provenance panels','v120/B5 provenance panels')
    return x
for key in ['known_blockers','external_open_gates']: v[key]=[gate(x) for x in (v.get(key) or [])]
v['blind_adversarial_v120_b5']={'date':'2026-10-02','predecessor':'v120/B4','predecessor_tree':'fa26ec9bf92f9d5ff8551113ad43d26fda45168e','b4_status':'FAILED_SUPERSEDED','findings':['B24H-B4-001: page and service-worker BUILD_REVISION remained B1 while manifest declared B4.','B24H-B4-002: version.json active build revision and real-device status remained B1.','B24H-B4-003: CSP script-src-elem did not authorize the actual B4 inline application script, blocking JavaScript initialization on a fresh load.','B24H-B4-004: current physical-gate wording still targeted v119/B1 rather than the current v120 candidate.'],'root_cause':'B1→B4 dark-mode mutations updated release IDs/CSS/style CSP but did not perform a complete release-shell identity/CSP rebind after script-affecting release metadata changed.','repair':'Create immutable B5 from exact B4; reconcile page/SW/manifest/version identity; rebuild exact inline CSP hashes from current bytes; rebind cache and canonical-shell SHA; update only active current-gate wording.','protected_surfaces':['CORPUS','TEXT_LIBRARY','SPEECH_DATA','Search semantics/results','provenance','personal-state schema/semantics','backup/import semantics','IndexedDB/Web-Locks architecture','update-v2 protocol'],'physical_pass_inferred':False,'production_deployment_authority':'NONE'}
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
allowed={'index.html','luisa_24_heures.html','manifest.json','sw.js','version.json'}
def sha(q): return hashlib.sha256(q.read_bytes()).hexdigest()
fa={str(q.relative_to(src)):sha(q) for q in src.rglob('*') if q.is_file()}; fb={str(q.relative_to(dst)):sha(q) for q in dst.rglob('*') if q.is_file()}; changed={k for k in set(fa)|set(fb) if fa.get(k)!=fb.get(k)}
if changed!=allowed: raise RuntimeError(f'unexpected changed set {changed}')
page=(dst/'index.html').read_text(encoding='utf-8'); sw=(dst/'sw.js').read_text(encoding='utf-8'); manifest=json.loads((dst/'manifest.json').read_text(encoding='utf-8')); version=json.loads((dst/'version.json').read_text(encoding='utf-8'))
assert "const BUILD_REVISION = 'B5';" in page and f"const APP_RELEASE_ID = '{NEW_RELEASE_ID}';" in page
assert "const BUILD_REVISION = 'B5';" in sw and f"const RELEASE_ID = '{NEW_RELEASE_ID}';" in sw
assert manifest['build_revision']=='B5' and manifest['release_id']==NEW_RELEASE_ID
assert version['build_revision']=='B5' and version['release_id']==NEW_RELEASE_ID and version['canonical_shell_sha256']==shell_sha
assert f"const CANONICAL_SHELL_SHA256 = '{shell_sha}';" in sw
print('24H_V120_B5_STAGE_PASS',shell_sha)
