#!/usr/bin/env python3
from pathlib import Path
import shutil,re,hashlib,base64,json

R=Path('.')
src=R/'lettres-v2.12-b1-darkmode'
dst=R/'lettres-v2.13-b1-csp-cleanup'
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

# Remove only the four independently-proved historical handler hashes.
for h in STALE:
    if s.count(h)!=1: raise SystemExit('stale hash count != 1: '+h)
    s=s.replace(' '+h,'',1)

# Governed successor identity/cache names.
s=s.replace("const APP_VERSION = '2.12';","const APP_VERSION = '2.13';")
s=s.replace('shell-v2.12-b1','shell-v2.13-b1').replace('corpus-v2.12-b1','corpus-v2.13-b1')
s=s.replace('v2.12 · 2026-10-02','v2.13 · 2026-10-04')
s=s.replace('Version de l’app :</strong> v2.12','Version de l’app :</strong> v2.13')

# Re-authorize any changed inline block exactly; do not alter unchanged block hashes.
def blocks(x,tag):
    return re.findall(fr'<{tag}(?![^>]*\bsrc=)[^>]*>(.*?)</{tag}>',x,re.S|re.I)
for tag in ['style','script']:
    a,b=blocks(before,tag),blocks(s,tag)
    if len(a)!=len(b): raise SystemExit(tag+' block count changed')
    for x,y in zip(a,b):
        if x!=y:
            oh="'sha256-"+base64.b64encode(hashlib.sha256(x.encode()).digest()).decode()+"'"
            nh="'sha256-"+base64.b64encode(hashlib.sha256(y.encode()).digest()).decode()+"'"
            if oh not in s: raise SystemExit('old CSP hash missing '+tag)
            s=s.replace(oh,nh,1)

# Prove stale hashes are gone.
for h in STALE:
    if h in s: raise SystemExit('stale hash survived: '+h)
p.write_text(s,encoding='utf-8')

p=dst/'manifest.json'
j=json.loads(p.read_text(encoding='utf-8'))
j['version']='2.13'
j['build_revision']='B1'
j['release_id']='lettres-v2.13-b1-csp-cleanup'
p.write_text(json.dumps(j,ensure_ascii=False,indent=4)+'\n',encoding='utf-8')

p=dst/'sw.js'
q=p.read_text(encoding='utf-8')
if 'v2.12' not in q: raise SystemExit('SW predecessor version absent')
p.write_text(q.replace('v2.12','v2.13'),encoding='utf-8')

# Protected surfaces must be byte-identical.
for rel in ['corpus.json','fonts','icons','vendor']:
    a=src/rel; b=dst/rel
    if a.is_file():
        assert a.read_bytes()==b.read_bytes(), rel
    else:
        af={x.relative_to(a):x.read_bytes() for x in a.rglob('*') if x.is_file()}
        bf={x.relative_to(b):x.read_bytes() for x in b.rglob('*') if x.is_file()}
        assert af==bf, rel

print('LETTRES_V2_13_STAGE_PASS')
