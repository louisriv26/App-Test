#!/usr/bin/env python3
from pathlib import Path
import shutil, re, hashlib, base64, json
R=Path('.')
src=R/'24h-v120-b1-darkmode'; dst=R/'24h-v120-b2-darkmode'
if dst.exists(): raise SystemExit('destination exists')
shutil.copytree(src,dst)
for nm in ['index.html','luisa_24_heures.html']:
 p=dst/nm; s=p.read_text(encoding='utf-8')
 m=re.search(r'<style id="dark-mode-contrast-closure-v120">(.*?)</style>',s,re.S)
 if not m: raise SystemExit('missing v120 style')
 style=m.group(1)
 token="'sha256-"+base64.b64encode(hashlib.sha256(style.encode()).digest()).decode()+"'"
 if token not in s:
  s=s.replace("style-src-elem ", "style-src-elem "+token+" ",1)
 s=s.replace("24H_V120_DARK_MODE_CLOSURE_B1","24H_V120_DARK_MODE_CLOSURE_B2")
 s=s.replace("24h-v120-b1-20261002-dark-mode-closure","24h-v120-b2-20261002-dark-mode-closure")
 p.write_text(s,encoding='utf-8')
if (dst/'index.html').read_bytes()!=(dst/'luisa_24_heures.html').read_bytes(): raise SystemExit('shell mismatch')
shell_sha=hashlib.sha256((dst/'index.html').read_bytes()).hexdigest()
p=dst/'manifest.json'; j=json.loads(p.read_text()); j['build_revision']='B2'; j['build']='B2'; j['release_id']='24h-v120-b2-20261002-dark-mode-closure'; p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
p=dst/'sw.js'; s=p.read_text(); s=s.replace("24h-v120-b1-20261002-dark-mode-closure","24h-v120-b2-20261002-dark-mode-closure").replace("v120-b1","v120-b2"); s=re.sub(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell_sha}';",s,count=1); p.write_text(s)
p=dst/'version.json'; j=json.loads(p.read_text()); j['cache_name']='scope-derived:luisa-24h-<scope-fingerprint>-v120-b2'; j['release_id']='24h-v120-b2-20261002-dark-mode-closure'; j['canonical_shell_sha256']=shell_sha; j['release_scope']='v120/B2 CSP-bound dark-mode contrast successor from exact live/frozen v119/B1; supersedes failed v120/B1 candidate; protected functional and content semantics inherited unchanged.'; j['overall_release_status']='V120_B2_DARK_MODE_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED'; j['dark_mode_v120_b2']={'date':'2026-10-02','supersedes_failed_candidate':'v120/B1','failure_root_cause':'CSP style-src-elem blocked the new bounded dark-mode style block','repair':'add exact sha256 CSP authorization for the bounded style block','corpus_changed':False,'search_changed':False,'provenance_changed':False,'personal_state_changed':False,'backup_semantics_changed':False,'physical_pass_inferred':False,'production_deployment_authority':'NONE'}; p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
# Ensure only the expected shell/metadata files differ from B1
import os
allowed={'index.html','luisa_24_heures.html','manifest.json','sw.js','version.json'}
for q in src.rglob('*'):
 if q.is_file() and str(q.relative_to(src)) not in allowed:
  d=dst/q.relative_to(src)
  if q.read_bytes()!=d.read_bytes(): raise SystemExit('protected drift '+str(q))
print('24H_V120_B2_STAGE_PASS',shell_sha)
