#!/usr/bin/env python3
from pathlib import Path
import shutil,re,hashlib,base64,json

R=Path('.')
src=R/'lettres-v2.13-b1-csp-cleanup'
dst=R/'lettres-v2.14-b1-csp-repair'
if dst.exists(): raise SystemExit('destination exists')
shutil.copytree(src,dst)

STALE=[
"'sha256-5f7hkRF7W/iK5De4fekXDFX5QLBdvzg+24Ynn7Kg1J0='",
"'sha256-EsFT1O/naZelunScCVdb0tL5ruF0UOnBO1yhoLcieeY='",
"'sha256-KbOnILe3AvDAjicxs+Uo8W4hxfqGINcDwFYp8pvDrWQ='",
"'sha256-ugrsOjEHVa7sYJzyVQnFDOk46B8+0QDCLn4IrrHG9gg='",
]

p=dst/'index.html'
before=p.read_text(encoding='utf-8')
s=before
s=s.replace("const APP_VERSION = '2.13';","const APP_VERSION = '2.14';")
s=s.replace('shell-v2.13-b1','shell-v2.14-b1').replace('corpus-v2.13-b1','corpus-v2.14-b1')
s=s.replace('v2.13 · 2026-10-04','v2.14 · 2026-10-04')
s=s.replace('Version de l’app :</strong> v2.13','Version de l’app :</strong> v2.14')

def blocks(x,tag):
    return re.findall(fr'<{tag}(?![^>]*\bsrc=)[^>]*>(.*?)</{tag}>',x,re.S|re.I)

old_scripts=blocks(before,'script')
new_scripts=blocks(s,'script')
if len(old_scripts)!=1 or len(new_scripts)!=1: raise SystemExit('unexpected script block count')
old_hash="'sha256-"+base64.b64encode(hashlib.sha256(old_scripts[0].encode()).digest()).decode()+"'"
new_hash="'sha256-"+base64.b64encode(hashlib.sha256(new_scripts[0].encode()).digest()).decode()+"'"

# Replace every current main-script authorization in script-src.
if old_hash not in s: raise SystemExit('current main script hash absent from CSP')
s=s.replace(old_hash,new_hash)

# Independently bind script-src-elem to the same actual successor script hash.
pat=r"(script-src-elem\s+)'sha256-[^']+'"
s,n=re.subn(pat,lambda m:m.group(1)+new_hash,s,count=1)
if n!=1: raise SystemExit('script-src-elem directive not repaired')

# Prove exact CSP binding and stale-hash cleanup before writing.
if s.count(new_hash)!=2:
    raise SystemExit(f'new main hash occurrence count {s.count(new_hash)} != 2')
if re.search(r"script-src-elem\s+(?!"+re.escape(new_hash)+r")",s):
    raise SystemExit('script-src-elem not bound to new hash')
for h in STALE:
    if h in s: raise SystemExit('historical CSP residue survived: '+h)

p.write_text(s,encoding='utf-8')

p=dst/'manifest.json'
j=json.loads(p.read_text(encoding='utf-8'))
j['version']='2.14'
j['build_revision']='B1'
j['release_id']='lettres-v2.14-b1-csp-repair'
p.write_text(json.dumps(j,ensure_ascii=False,indent=4)+'\n',encoding='utf-8')

p=dst/'sw.js'
q=p.read_text(encoding='utf-8')
if 'v2.13' not in q: raise SystemExit('SW predecessor version absent')
p.write_text(q.replace('v2.13','v2.14'),encoding='utf-8')

# Protected assets/content remain byte-identical to v2.13/v2.12.
for rel in ['corpus.json','fonts','icons','vendor']:
    a=src/rel; b=dst/rel
    if a.is_file():
        assert a.read_bytes()==b.read_bytes(), rel
    else:
        af={x.relative_to(a):x.read_bytes() for x in a.rglob('*') if x.is_file()}
        bf={x.relative_to(b):x.read_bytes() for x in b.rglob('*') if x.is_file()}
        assert af==bf, rel

print('LETTRES_V2_14_STAGE_PASS',new_hash)
