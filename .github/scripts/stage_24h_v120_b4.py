#!/usr/bin/env python3
from pathlib import Path
import shutil,re,hashlib,base64,json
R=Path('.'); src=R/'24h-v120-b3-darkmode'; dst=R/'24h-v120-b4-darkmode'
if dst.exists(): raise SystemExit('destination exists')
shutil.copytree(src,dst)
add_media='''
html:not([data-theme="light"]) .bn-item{color:#948E84}
html:not([data-theme="light"]) .bn-item.active,html:not([data-theme="light"]) .bn-item:hover{color:#D4A843}
'''
add_explicit='''
html[data-theme="dark"] .bn-item{color:#948E84}
html[data-theme="dark"] .bn-item.active,html[data-theme="dark"] .bn-item:hover{color:#D4A843}
'''
for nm in ['index.html','luisa_24_heures.html']:
 p=dst/nm; before=p.read_text(encoding='utf-8'); s=before
 m=re.search(r'<style id="dark-mode-contrast-closure-v120">(.*?)</style>',s,re.S)
 if not m: raise SystemExit('style missing')
 body=m.group(1)
 oldtok="'sha256-"+base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()+"'"
 body2=body.replace('html:not([data-theme="light"]) .stage6m-home-action .d{color:var(--ink3)}','html:not([data-theme="light"]) .stage6m-home-action .d{color:var(--ink3)}'+add_media)
 body2=body2.replace('html[data-theme="dark"] .stage6m-home-action .d{color:var(--ink3)}','html[data-theme="dark"] .stage6m-home-action .d{color:var(--ink3)}'+add_explicit)
 if body2==body: raise SystemExit('no mutation')
 newtok="'sha256-"+base64.b64encode(hashlib.sha256(body2.encode()).digest()).decode()+"'"
 s=s[:m.start(1)]+body2+s[m.end(1):]
 if oldtok not in s: raise SystemExit('old CSP hash missing')
 s=s.replace(oldtok,newtok,1)
 s=s.replace("24H_V120_DARK_MODE_CLOSURE_B3","24H_V120_DARK_MODE_CLOSURE_B4")
 s=s.replace("24h-v120-b3-20261002-dark-mode-closure","24h-v120-b4-20261002-dark-mode-closure")
 p.write_text(s,encoding='utf-8')
assert (dst/'index.html').read_bytes()==(dst/'luisa_24_heures.html').read_bytes()
shell=hashlib.sha256((dst/'index.html').read_bytes()).hexdigest()
p=dst/'manifest.json';j=json.loads(p.read_text());j['build_revision']='B4';j['build']='B4';j['release_id']='24h-v120-b4-20261002-dark-mode-closure';p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
p=dst/'sw.js';s=p.read_text().replace('24h-v120-b3-20261002-dark-mode-closure','24h-v120-b4-20261002-dark-mode-closure').replace('v120-b3','v120-b4');s=re.sub(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell}';",s,count=1);p.write_text(s)
p=dst/'version.json';j=json.loads(p.read_text());j['cache_name']='scope-derived:luisa-24h-<scope-fingerprint>-v120-b4';j['release_id']='24h-v120-b4-20261002-dark-mode-closure';j['canonical_shell_sha256']=shell;j['release_scope']='v120/B4 dark-mode closure successor; adds bounded bottom-navigation dark contrast repair after blind adversarial audit; all corpus/search/provenance/personal semantics unchanged.';j['overall_release_status']='V120_B4_DARK_MODE_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED';j['dark_mode_v120_b4']={'date':'2026-10-02','supersedes':['v120/B1','v120/B2','v120/B3'],'new_blind_finding':'bottom navigation text used effective light-palette colours in dark rendering: muted 3.36:1, active 2.95:1','repair':'bounded dark selectors use exact existing dark-palette values #948E84 and #D4A843','settings_gear':'no mutation; non-text icon measured 3.11:1 and passes 3:1','corpus_changed':False,'search_changed':False,'provenance_changed':False,'personal_state_changed':False,'physical_pass_inferred':False,'production_deployment_authority':'NONE'};p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
print('24H_V120_B4_STAGE_PASS',shell)
