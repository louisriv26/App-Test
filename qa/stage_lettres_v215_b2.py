#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import shutil,re,hashlib,base64,json,subprocess,os

SRC=Path('lettres-v2.15-b1-contrast-repair')
DST=Path('lettres-v2.15-b2-contrast-repair')
if DST.exists(): shutil.rmtree(DST)
shutil.copytree(SRC,DST)

def one(s,a,b,label):
    n=s.count(a)
    if n!=1: raise SystemExit(f'{label}: expected 1 occurrence, got {n}')
    return s.replace(a,b)

p=DST/'index.html'
s=p.read_text(encoding='utf-8')
s=one(s,'.export-btn.primary:hover{opacity:.88;}','.export-btn.primary:hover{opacity:1;background:#243659;}','export hover')
s=one(s,"const APP_BUILD = 'B1';","const APP_BUILD = 'B2';",'APP_BUILD')
s=s.replace('shell-v2.15-b1','shell-v2.15-b2').replace('corpus-v2.15-b1','corpus-v2.15-b2')

scripts=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',s,re.S|re.I)
styles=re.findall(r'<style[^>]*>(.*?)</style>',s,re.S|re.I)
if len(scripts)!=1 or len(styles)!=2: raise SystemExit(f'inline blocks scripts={len(scripts)} styles={len(styles)}')
token=lambda x:"'sha256-"+base64.b64encode(hashlib.sha256(x.encode()).digest()).decode()+"'"
main_hash=token(scripts[0]); style_hashes=[token(x) for x in styles]

class CSP(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False); self.content=None
    def handle_starttag(self,tag,attrs):
        d={k.lower():v for k,v in attrs}
        if tag.lower()=='meta' and (d.get('http-equiv') or '').lower()=='content-security-policy':
            self.content=d.get('content')
cp=CSP();cp.feed(s)
if not cp.content: raise SystemExit('CSP meta absent')
parts=[x.strip() for x in cp.content.split(';') if x.strip()]
order=[]; directives={}
for d in parts:
    z=d.split(); order.append(z[0]); directives[z[0]]=z[1:]
old_main=(directives.get('script-src-elem') or [None])[0]
if not old_main or old_main not in directives.get('script-src',[]): raise SystemExit('old main hash not structurally bound')
directives['script-src']=[main_hash if x==old_main else x for x in directives['script-src']]
directives['script-src-elem']=[main_hash]
directives['style-src-elem']=style_hashes
new_csp='; '.join(k+' '+' '.join(directives[k]) for k in order)
s=one(s,cp.content,new_csp,'CSP content')
p.write_text(s,encoding='utf-8')

m=json.loads((DST/'manifest.json').read_text(encoding='utf-8'))
m['version']='2.15';m['build_revision']='B2';m['release_id']='lettres-v2.15-b2-contrast-repair'
(DST/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=4)+'\n',encoding='utf-8')

sp=DST/'sw.js';w=sp.read_text(encoding='utf-8')
w=w.replace('B1','B2').replace('v2.15-b1','v2.15-b2')
sp.write_text(w,encoding='utf-8')

# Hard mutation boundary: only three package members may differ from B1.
def hmap(root):
    return {x.relative_to(root).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in root.rglob('*') if x.is_file()}
A=hmap(SRC);B=hmap(DST)
if set(A)!=set(B) or len(B)!=22: raise SystemExit('member-set drift')
changed=sorted(k for k in A if A[k]!=B[k])
if changed!=['index.html','manifest.json','sw.js']: raise SystemExit('unexpected changed members '+repr(changed))
if B['corpus.json']!='362e763684e19d818722082b88348d912f06f434d8960e2a278db07b7f63f8ec': raise SystemExit('corpus drift')

# Stage exact candidate and derive its Git subtree SHA without committing it.
subprocess.run(['git','add','--',str(DST)],check=True)
root_tree=subprocess.check_output(['git','write-tree'],text=True).strip()
subtree=subprocess.check_output(['git','rev-parse',f'{root_tree}:{DST.as_posix()}'],text=True).strip()
Path('/tmp/LETTRES_V2_15_B2_TREE.txt').write_text(subtree+'\n',encoding='utf-8')
with open(os.environ['GITHUB_ENV'],'a',encoding='utf-8') as f:f.write('LETTRES_V215_TREE='+subtree+'\n')
print('STAGED_B2_TREE',subtree)
print('B2_MAIN_SCRIPT_HASH',main_hash)
print('B2_STYLE_HASHES',style_hashes)
print('B2_CHANGED_MEMBERS',changed)
