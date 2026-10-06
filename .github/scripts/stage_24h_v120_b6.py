#!/usr/bin/env python3
from pathlib import Path
import shutil,re,hashlib,base64,json
R=Path('.')
src=R/'24h-v120-b5-adversarial'
dst=R/'24h-v120-b6-adversarial'
if dst.exists(): raise SystemExit('destination exists')
shutil.copytree(src,dst)
OLD_RID='24h-v120-b5-20261003-adversarial-runtime-closure'
NEW_RID='24h-v120-b6-20261003-adversarial-runtime-closure'
NEW_SEQ=120000006

def inline_script_hash(text):
    m=re.search(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',text,re.S|re.I)
    if not m: raise SystemExit('inline script missing')
    return "'sha256-"+base64.b64encode(hashlib.sha256(m.group(1).encode()).digest()).decode()+"'"

for nm in ['index.html','luisa_24_heures.html']:
    p=dst/nm
    s=p.read_text(encoding='utf-8')
    s=s.replace("const BUILD_REVISION = 'B5';","const BUILD_REVISION = 'B6';",1)
    s=s.replace("const APP_EVIDENCE_STAGE = '24H_V120_ADVERSARIAL_RUNTIME_CLOSURE_B5';","const APP_EVIDENCE_STAGE = '24H_V120_ADVERSARIAL_RUNTIME_CLOSURE_B6';",1)
    s=s.replace("const APP_RELEASE_SEQUENCE = 120000005;","const APP_RELEASE_SEQUENCE = 120000006;",1)
    s=s.replace("const APP_RELEASE_ID = '"+OLD_RID+"';","const APP_RELEASE_ID = '"+NEW_RID+"';",1)
    new_hash=inline_script_hash(s)
    cspm=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(")',s,re.I)
    if not cspm: raise SystemExit('CSP meta missing')
    csp=cspm.group(2)
    seg=csp.split('script-src-elem',1)[1].split(';',1)[0]
    hashes=re.findall(r"'sha256-[A-Za-z0-9+/=]+'",seg)
    if len(hashes)!=1: raise SystemExit('expected one script hash')
    csp=csp.replace(hashes[0],new_hash,1)
    s=s[:cspm.start(2)]+csp+s[cspm.end(2):]
    p.write_text(s,encoding='utf-8')

assert (dst/'index.html').read_bytes()==(dst/'luisa_24_heures.html').read_bytes()
shell=hashlib.sha256((dst/'index.html').read_bytes()).hexdigest()

p=dst/'manifest.json'; j=json.loads(p.read_text())
j['version']='v120';j['build_revision']='B6';j['build']='B6';j['release_sequence']=NEW_SEQ;j['release_id']=NEW_RID
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')

p=dst/'sw.js'; s=p.read_text()
s=re.sub(r"^/\*.*?\*/","/* v120 B6 — blind-adversarial runtime/release-identity closure from failed B5; fixes B5 SW syntax while preserving the bounded CSP/identity repair. Protected corpus/Search/provenance/personal-state/backup semantics unchanged. */",s,count=1,flags=re.S)
s=s.replace("const BUILD_REVISION = 'B5';","const BUILD_REVISION = 'B6';",1)
s=s.replace("const RELEASE_SEQUENCE = 120000005;","const RELEASE_SEQUENCE = 120000006;",1)
s=s.replace("const RELEASE_ID = '"+OLD_RID+"';","const RELEASE_ID = '"+NEW_RID+"';",1)
s=re.sub(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell}';",s,count=1)
cache_line='const CACHE_NAME = ' + chr(96) + '${CACHE_PREFIX}v120-b6' + chr(96) + ';'
s=re.sub(r"const CACHE_NAME = .*?;",cache_line,s,count=1)
p.write_text(s)

p=dst/'version.json';j=json.loads(p.read_text())
j['app_version']='v120';j['build_revision']='B6';j['release_sequence']=NEW_SEQ;j['release_id']=NEW_RID
j['canonical_shell_sha256']=shell
j['cache_name']='scope-derived:luisa-24h-<scope-fingerprint>-v120-b6'
j['release_scope']='v120/B6 blind-adversarial runtime/release-identity closure; supersedes failed B4 and failed B5; fixes CSP script authorization, coherent release identity, and B5 service-worker syntax only.'
j['overall_release_status']='V120_B6_ADVERSARIAL_RUNTIME_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED'
j['blind_adversarial_b6']={
 'date':'2026-10-03',
 'supersedes':['v120/B4','v120/B5'],
 'confirmed_failures':['B4 CSP blocked application script','B4 B1/B4 release-identity mismatch broke SW verifiedInstall','B5 generated invalid service-worker cache-name syntax'],
 'repair_boundary':'release identity + CSP binding + service-worker syntax only',
 'corpus_changed':False,'search_changed':False,'provenance_changed':False,'personal_state_changed':False,'backup_semantics_changed':False,
 'physical_pass_inferred':False,'production_deployment_authority':'NONE'
}
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')

allowed={'index.html','luisa_24_heures.html','manifest.json','sw.js','version.json'}
for q in src.rglob('*'):
    if q.is_file() and str(q.relative_to(src)) not in allowed:
        d=dst/q.relative_to(src);assert d.exists() and q.read_bytes()==d.read_bytes(),str(q)

print('24H_V120_B6_STAGE_PASS',shell,inline_script_hash((dst/'index.html').read_text()))
