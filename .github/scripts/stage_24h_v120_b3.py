#!/usr/bin/env python3
from pathlib import Path
import shutil,re,hashlib,base64,json
R=Path('.'); src=R/'24h-v120-b2-darkmode'; dst=R/'24h-v120-b3-darkmode'
if dst.exists(): raise SystemExit('destination exists')
shutil.copytree(src,dst)
for nm in ['index.html','luisa_24_heures.html']:
 p=dst/nm; s=p.read_text(encoding='utf-8')
 old='html:not([data-theme="light"]) div.d{color:#8A857D}'
 new='html:not([data-theme="light"]) .stage6m-home-action .d{color:var(--ink3)}'
 s=s.replace(old,new)
 old2='html[data-theme="dark"] div.d{color:#8A857D}'
 new2='html[data-theme="dark"] .stage6m-home-action .d{color:var(--ink3)}'
 s=s.replace(old2,new2)
 s=s.replace("24H_V120_DARK_MODE_CLOSURE_B2","24H_V120_DARK_MODE_CLOSURE_B3")
 s=s.replace("24h-v120-b2-20261002-dark-mode-closure","24h-v120-b3-20261002-dark-mode-closure")
 m=re.search(r'<style id="dark-mode-contrast-closure-v120">(.*?)</style>',s,re.S)
 if not m: raise SystemExit('missing style')
 # replace the old B2 style hash in CSP with B3 style hash
 cspm=re.search(r'Content-Security-Policy" content="([^"]+)"',s)
 csp=cspm.group(1)
 # locate prior B2 hash by reading source counterpart
 ss=(src/nm).read_text(encoding='utf-8')
 mm=re.search(r'<style id="dark-mode-contrast-closure-v120">(.*?)</style>',ss,re.S)
 oldtok="'sha256-"+base64.b64encode(hashlib.sha256(mm.group(1).encode()).digest()).decode()+"'"
 newtok="'sha256-"+base64.b64encode(hashlib.sha256(m.group(1).encode()).digest()).decode()+"'"
 if oldtok not in csp: raise SystemExit('old CSP token absent')
 s=s.replace(oldtok,newtok,1)
 p.write_text(s,encoding='utf-8')
if (dst/'index.html').read_bytes()!=(dst/'luisa_24_heures.html').read_bytes(): raise SystemExit('shell mismatch')
shell=hashlib.sha256((dst/'index.html').read_bytes()).hexdigest()
p=dst/'manifest.json'; j=json.loads(p.read_text()); j['build_revision']='B3'; j['build']='B3'; j['release_id']='24h-v120-b3-20261002-dark-mode-closure'; p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
p=dst/'sw.js'; s=p.read_text(); s=s.replace("24h-v120-b2-20261002-dark-mode-closure","24h-v120-b3-20261002-dark-mode-closure").replace("v120-b2","v120-b3"); s=re.sub(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell}';",s,count=1); p.write_text(s)
p=dst/'version.json'; j=json.loads(p.read_text()); j['cache_name']='scope-derived:luisa-24h-<scope-fingerprint>-v120-b3'; j['release_id']='24h-v120-b3-20261002-dark-mode-closure'; j['canonical_shell_sha256']=shell; j['release_scope']='v120/B3 bounded dark-mode contrast successor; supersedes failed B1 (CSP) and B2 (selector specificity); functional/content semantics unchanged.'; j['overall_release_status']='V120_B3_DARK_MODE_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED'; j['dark_mode_v120_b3']={'date':'2026-10-02','supersedes':['v120/B1','v120/B2'],'root_cause_b2':'div.d selector lost cascade to .stage6m-home-action .d','repair':'exact affected selector uses existing semantic --ink3 token','corpus_changed':False,'search_changed':False,'provenance_changed':False,'personal_state_changed':False,'physical_pass_inferred':False,'production_deployment_authority':'NONE'}; p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
allowed={'index.html','luisa_24_heures.html','manifest.json','sw.js','version.json'}
for q in src.rglob('*'):
 if q.is_file() and str(q.relative_to(src)) not in allowed:
  d=dst/q.relative_to(src)
  assert d.exists() and q.read_bytes()==d.read_bytes(),q
print('24H_V120_B3_STAGE_PASS',shell)
