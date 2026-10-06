from pathlib import Path
import shutil,re,hashlib,base64,json,os
src=Path('marie-v47-b1-darkmode'); dst=Path('marie-v48-b1-darkmode')
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(src,dst)
idx=dst/'index.html'; s=idx.read_text(encoding='utf-8')
# Public/runtime version successor.
old="const APP_VERSION = '47';"; new="const APP_VERSION = '48';"
assert s.count(old)==1
s=s.replace(old,new,1)
# Explicit placeholder semantics for both search and note fields.
oldph=".search-input::placeholder { color: var(--muted); }"
newph=".search-input::placeholder, .note-textarea::placeholder { color: var(--muted); opacity: 1; }"
assert s.count(oldph)==1
s=s.replace(oldph,newph,1)
# Recompute exact inline CSP script/style hashes after final bytes.
def b64sha(txt): return base64.b64encode(hashlib.sha256(txt.encode('utf-8')).digest()).decode('ascii')
styles=re.findall(r'<style[^>]*>([\s\S]*?)</style>',s,re.I)
scripts=[m.group(1) for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>',s,re.I)]
assert len(styles)==1 and len(scripts)>=1
style_tokens=" ".join("'sha256-"+b64sha(x)+"'" for x in styles)
script_tokens=" ".join("'sha256-"+b64sha(x)+"'" for x in scripts)
m=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(">)',s,re.I)
assert m
csp=m.group(2)
csp2=re.sub(r"script-src [^;]+;", "script-src "+script_tokens+";", csp, count=1)
csp2=re.sub(r"style-src [^;]+;", "style-src "+style_tokens+";", csp2, count=1)
s=s[:m.start(2)]+csp2+s[m.end(2):]
idx.write_text(s,encoding='utf-8',newline='\n')
sw=dst/'sw.js'; w=sw.read_text(encoding='utf-8')
assert w.count("const VERSION = '47';")==1
w=w.replace("const VERSION = '47';","const VERSION = '48';",1)
sw.write_text(w,encoding='utf-8',newline='\n')
def fsha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
# Evidence and mutation boundary.
fa={str(p.relative_to(src)):fsha(p) for p in src.rglob('*') if p.is_file()}
fb={str(p.relative_to(dst)):fsha(p) for p in dst.rglob('*') if p.is_file()}
changed=sorted(k for k in set(fa)|set(fb) if fa.get(k)!=fb.get(k))
assert changed==['index.html','sw.js'],changed
e={
 'candidate':'MJV v48/B1',
 'predecessor':'MJV v47/B1',
 'date':'2026-10-03',
 'root_cause':'v47 inline stylesheet changed but CSP style-src retained the exact v46 stylesheet hash, so the browser rejected the v47 application stylesheet.',
 'repair':['advance APP_VERSION/SW VERSION 47→48','explicitly bind search/note placeholders to var(--muted) with opacity 1','recompute exact inline script and style CSP hashes'],
 'changed_files':changed,
 'index_sha256':fsha(idx),'sw_sha256':fsha(sw),
 'style_sha256_base64':[b64sha(x) for x in re.findall(r'<style[^>]*>([\\s\\S]*?)</style>',s,re.I)],
 'script_sha256_base64':[b64sha(x) for x in re.findall(r'<script(?![^>]*\\bsrc=)[^>]*>([\\s\\S]*?)</script>',s,re.I)],
 'corpus_mutation':False,'personal_state_schema_mutation':False,'production_deployment_authority':'NONE','physical_gate':'OPEN'
}
Path('marie-v48-build-evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(e,ensure_ascii=False,indent=2))
