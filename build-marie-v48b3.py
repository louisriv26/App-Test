#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, json, re, shutil

SRC=Path('marie-v47-b1-darkmode')
DST=Path('marie-v48-b3-csp-note-placeholder-closure')
PREDECESSOR_TREE='81acbb9f409c7c0e1695b0ab35f33dfdc4978631'
if DST.exists(): shutil.rmtree(DST)
shutil.copytree(SRC,DST)

def b64sha(text): return base64.b64encode(hashlib.sha256(text.encode('utf-8')).digest()).decode('ascii')
def fsha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

idx=DST/'index.html'
s=idx.read_text(encoding='utf-8')
assert s.count("const APP_VERSION = '47';")==1
s=s.replace("const APP_VERSION = '47';","const APP_VERSION = '48';",1)

# Fresh B2 full-QA finding: only the note placeholder lacks the authored dark-mode-safe placeholder colour.
anchor='.search-input::placeholder { color: var(--muted); }'
addition='.note-textarea::placeholder { color: var(--muted); }'
assert s.count(anchor)==1
assert addition not in s
s=s.replace(anchor,anchor+'\n'+addition,1)

# Rebind CSP after every final inline byte is known.
styles=re.findall(r'<style[^>]*>([\s\S]*?)</style>',s,re.I)
scripts=[m.group(1) for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>',s,re.I)]
assert len(styles)==1 and len(scripts)==3
style_tokens=' '.join("'sha256-"+b64sha(x)+"'" for x in styles)
script_tokens=' '.join("'sha256-"+b64sha(x)+"'" for x in scripts)
m=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(")',s,re.I); assert m
csp=m.group(2)
csp,n1=re.subn(r'script-src\s+[^;]*;','script-src '+script_tokens+';',csp,count=1)
csp,n2=re.subn(r'style-src\s+[^;]*;','style-src '+style_tokens+';',csp,count=1)
assert n1==1 and n2==1
s=s[:m.start(2)]+csp+s[m.end(2):]
idx.write_text(s,encoding='utf-8',newline='\n')

sw=DST/'sw.js'
w=sw.read_text(encoding='utf-8')
assert w.count("const VERSION = '47';")==1
w=w.replace("const VERSION = '47';","const VERSION = '48';",1)
sw.write_text(w,encoding='utf-8',newline='\n')

fa={str(p.relative_to(SRC)):fsha(p) for p in SRC.rglob('*') if p.is_file()}
fb={str(p.relative_to(DST)):fsha(p) for p in DST.rglob('*') if p.is_file()}
changed=sorted(k for k in set(fa)|set(fb) if fa.get(k)!=fb.get(k))
assert changed==['index.html','sw.js'],changed
final=idx.read_text(encoding='utf-8')
assert final.count(anchor)==1 and final.count(addition)==1
assert '.search-input::placeholder, .note-textarea::placeholder' not in final
assert 'opacity: 1' not in final[final.find(anchor):final.find(anchor)+220]

evidence={
 'candidate':'MJV v48/B3','public_version':'48','predecessor':'MJV v47/B1','predecessor_tree':PREDECESSOR_TREE,'date':'2026-10-04',
 'root_causes':[
   'v47 changed the inline stylesheet and main inline application script but omitted CSP hash rebinding, causing both blocks to be rejected.',
   'After CSP execution was restored in failed/unfrozen B2, fresh dark-mode rendering exposed the note textarea placeholder at 3.606:1 because it had no authored placeholder colour and inherited the browser default.'
 ],
 'corrections':[
   'advance runtime/service-worker public version 47 to 48',
   'add only .note-textarea::placeholder { color: var(--muted); } while leaving the existing search placeholder rule unchanged',
   'recompute exact final script-src and style-src CSP hashes'
 ],
 'retired_candidates':[
   'MJV v48/B1: over-broad placeholder+CSP staging candidate; never production authority',
   'MJV v48/B2: minimal CSP-only candidate; Pass 1 passed but full runtime found note-placeholder contrast 3.606:1; unfrozen/never promoted'
 ],
 'changed_files':changed,'index_sha256':fsha(idx),'sw_sha256':fsha(sw),
 'script_sha256_base64':[b64sha(x) for x in scripts],'style_sha256_base64':[b64sha(x) for x in styles],
 'protected_surfaces':['corpus and migration bytes','manifest/icons/fonts','search placeholder styling','search/reader/navigation/help semantics','personal-state schema/transactions','backup/export/restore semantics','v47 backup-primary dark-mode repair'],
 'corpus_mutation':False,'personal_state_schema_mutation':False,'production_deployment_authority':'NONE','physical_gate':'OPEN'
}
Path('MJV_v48_B3_BUILD_EVIDENCE.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(evidence,ensure_ascii=False,indent=2))