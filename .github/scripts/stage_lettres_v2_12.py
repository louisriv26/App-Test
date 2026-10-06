#!/usr/bin/env python3
from pathlib import Path
import shutil,re,hashlib,base64,json
R=Path('.'); src=R/'lettres-v2.11-b1-darkmode'; dst=R/'lettres-v2.12-b1-darkmode'
if dst.exists(): raise SystemExit('destination exists')
shutil.copytree(src,dst)
p=dst/'index.html'; before=p.read_text(encoding='utf-8'); s=before
s=s.replace('background:rgba(255,214,74,.20)}','background:rgba(255,214,74,.08);color:var(--ink)}')
if s==before: raise SystemExit('highlight rule not replaced')
s=s.replace("const APP_VERSION = '2.11';","const APP_VERSION = '2.12';")
s=s.replace('shell-v2.11-b1','shell-v2.12-b1').replace('corpus-v2.11-b1','corpus-v2.12-b1')
s=s.replace('v2.11 · 2026-10-02','v2.12 · 2026-10-02').replace('Version de l’app :</strong> v2.11','Version de l’app :</strong> v2.12')
def blocks(x,tag): return re.findall(fr'<{tag}(?![^>]*\bsrc=)[^>]*>(.*?)</{tag}>',x,re.S|re.I)
for tag in ['style','script']:
 a,b=blocks(before,tag),blocks(s,tag)
 if len(a)!=len(b): raise SystemExit(tag+' block count')
 for x,y in zip(a,b):
  if x!=y:
   oh="'sha256-"+base64.b64encode(hashlib.sha256(x.encode()).digest()).decode()+"'"
   nh="'sha256-"+base64.b64encode(hashlib.sha256(y.encode()).digest()).decode()+"'"
   if oh not in s: raise SystemExit('old CSP hash missing '+tag)
   s=s.replace(oh,nh)
p.write_text(s,encoding='utf-8')
p=dst/'manifest.json'; j=json.loads(p.read_text()); j['version']='2.12'; j['build_revision']='B1'; j['release_id']='lettres-v2.12-b1-darkmode'; p.write_text(json.dumps(j,ensure_ascii=False,indent=4)+'\n')
p=dst/'sw.js'; q=p.read_text(); 
if 'v2.11' not in q: raise SystemExit('SW version absent')
p.write_text(q.replace('v2.11','v2.12'))
assert (dst/'corpus.json').read_bytes()==(src/'corpus.json').read_bytes()
print('LETTRES_V2_12_STAGE_PASS')
