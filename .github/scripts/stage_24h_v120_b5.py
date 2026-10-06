#!/usr/bin/env python3
from pathlib import Path
import shutil,re,hashlib,base64,json
R=Path('.')
src=R/'24h-v120-b4-darkmode'
dst=R/'24h-v120-b5-adversarial'
if dst.exists(): raise SystemExit('destination exists')
shutil.copytree(src,dst)
OLD_RID='24h-v120-b4-20261002-dark-mode-closure'
NEW_RID='24h-v120-b5-20261003-adversarial-runtime-closure'
NEW_SEQ=120000005

def inline_script_hash(text):
    m=re.search(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',text,re.S|re.I)
    if not m: raise SystemExit('inline script missing')
    return "'sha256-"+base64.b64encode(hashlib.sha256(m.group(1).encode()).digest()).decode()+"'"

for nm in ['index.html','luisa_24_heures.html']:
    p=dst/nm
    s=p.read_text(encoding='utf-8')
    s=s.replace("const BUILD_REVISION = 'B1';","const BUILD_REVISION = 'B5';",1)
    s=s.replace("const APP_EVIDENCE_STAGE = '24H_V120_DARK_MODE_CLOSURE_B4';","const APP_EVIDENCE_STAGE = '24H_V120_ADVERSARIAL_RUNTIME_CLOSURE_B5';",1)
    s=s.replace("const APP_RELEASE_SEQUENCE = 120000001;","const APP_RELEASE_SEQUENCE = 120000005;",1)
    s=s.replace("const APP_RELEASE_ID = '"+OLD_RID+"';","const APP_RELEASE_ID = '"+NEW_RID+"';",1)
    new_hash=inline_script_hash(s)
    cspm=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(")',s,re.I)
    if not cspm: raise SystemExit('CSP meta missing')
    csp=cspm.group(2)
    if 'script-src-elem' not in csp: raise SystemExit('script-src-elem missing')
    seg=csp.split('script-src-elem',1)[1].split(';',1)[0]
    hashes=re.findall(r"'sha256-[A-Za-z0-9+/=]+'",seg)
    if len(hashes)!=1: raise SystemExit('expected exactly one script-src-elem hash')
    csp=csp.replace(hashes[0],new_hash,1)
    s=s[:cspm.start(2)]+csp+s[cspm.end(2):]
    p.write_text(s,encoding='utf-8')

if (dst/'index.html').read_bytes()!=(dst/'luisa_24_heures.html').read_bytes():
    raise SystemExit('shells diverged')
shell=hashlib.sha256((dst/'index.html').read_bytes()).hexdigest()

p=dst/'manifest.json'
j=json.loads(p.read_text(encoding='utf-8'))
j['version']='v120'; j['build_revision']='B5'; j['build']='B5'; j['release_sequence']=NEW_SEQ; j['release_id']=NEW_RID
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=dst/'sw.js'
s=p.read_text(encoding='utf-8')
s=re.sub(r"^/\*.*?\*/","/* v120 B5 — blind-adversarial runtime/release-identity closure from exact v120/B4. Fixes CSP script binding and coherent B5 identity only; protected corpus/Search/provenance/personal-state/backup semantics unchanged. */",s,count=1,flags=re.S)
s=s.replace("const BUILD_REVISION = 'B1';","const BUILD_REVISION = 'B5';",1)
s=s.replace("const RELEASE_SEQUENCE = 120000001;","const RELEASE_SEQUENCE = 120000005;",1)
s=s.replace("const RELEASE_ID = '"+OLD_RID+"';","const RELEASE_ID = '"+NEW_RID+"';",1)
s=re.sub(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell}';",s,count=1)
s=re.sub(r"const CACHE_NAME = .*?;", "const CACHE_NAME = \`\${CACHE_PREFIX}v120-b5\`;", s, count=1)
p.write_text(s,encoding='utf-8')

p=dst/'version.json'
j=json.loads(p.read_text(encoding='utf-8'))
j['app_version']='v120'; j['build_revision']='B5'; j['release_sequence']=NEW_SEQ; j['release_id']=NEW_RID
j['canonical_shell_sha256']=shell
j['cache_name']='scope-derived:luisa-24h-<scope-fingerprint>-v120-b5'
j['release_scope']='v120/B5 blind-adversarial runtime/release-identity closure from exact frozen B4; fixes CSP inline-script authorization and coherent B5 identity across shell/manifest/service worker/version metadata only.'
j['overall_release_status']='V120_B5_ADVERSARIAL_RUNTIME_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED'
j['blind_adversarial_b5']={
 'date':'2026-10-03',
 'supersedes_failed_candidate':'v120/B4',
 'confirmed_b4_failures':[
  'CSP script-src-elem hash did not match the only inline application script, blocking all app JavaScript in served Chromium',
  'shell/service-worker/version metadata still declared BUILD_REVISION B1 while manifest declared B4',
  'service-worker verifiedInstall would reject manifest with manifest_release_identity_mismatch'
 ],
 'repair_boundary':'release identity + CSP binding only',
 'corpus_changed':False,'search_changed':False,'provenance_changed':False,'personal_state_changed':False,'backup_semantics_changed':False,
 'physical_pass_inferred':False,'production_deployment_authority':'NONE'
}
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

allowed={'index.html','luisa_24_heures.html','manifest.json','sw.js','version.json'}
for q in src.rglob('*'):
    if q.is_file() and str(q.relative_to(src)) not in allowed:
        d=dst/q.relative_to(src)
        assert d.exists() and q.read_bytes()==d.read_bytes(),str(q)

html=(dst/'index.html').read_text(encoding='utf-8')
sw=(dst/'sw.js').read_text(encoding='utf-8')
man=json.loads((dst/'manifest.json').read_text())
ver=json.loads((dst/'version.json').read_text())
assert "const BUILD_REVISION = 'B5';" in html
assert "const APP_RELEASE_SEQUENCE = 120000005;" in html
assert NEW_RID in html
assert "const BUILD_REVISION = 'B5';" in sw
assert "const RELEASE_SEQUENCE = 120000005;" in sw
assert NEW_RID in sw
assert man['build_revision']=='B5' and man['release_sequence']==NEW_SEQ and man['release_id']==NEW_RID
assert ver['build_revision']=='B5' and ver['release_sequence']==NEW_SEQ and ver['release_id']==NEW_RID
print('24H_V120_B5_STAGE_PASS',shell,inline_script_hash(html))
