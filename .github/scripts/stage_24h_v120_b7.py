#!/usr/bin/env python3
from pathlib import Path
import shutil,re,hashlib,base64,json
R=Path('.')
src=R/'24h-v120-b6-adversarial'
dst=R/'24h-v120-b7-adversarial'
if dst.exists(): raise SystemExit('destination exists')
shutil.copytree(src,dst)
OLD_RID='24h-v120-b6-20261003-adversarial-runtime-closure'
NEW_RID='24h-v120-b7-20261003-blind-accessibility-closure'
NEW_SEQ=120000007
D='$'

def hash_token(text):
    return "'sha256-"+base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()+"'"

def refresh_csp(s):
    scripts=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',s,re.S|re.I)
    styles=re.findall(r'<style[^>]*>(.*?)</style>',s,re.S|re.I)
    if len(scripts)!=1: raise SystemExit(f'expected one inline script, got {len(scripts)}')
    cspm=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(")',s,re.I)
    if not cspm: raise SystemExit('CSP meta missing')
    csp=cspm.group(2)
    sh=hash_token(scripts[0])
    sth=[hash_token(x) for x in styles]
    csp=re.sub(r"script-src-elem\s+[^;]*;",'script-src-elem '+sh+';',csp,count=1)
    csp=re.sub(r"style-src-elem\s+[^;]*;",'style-src-elem '+' '.join(sth)+';',csp,count=1)
    return s[:cspm.start(2)]+csp+s[cspm.end(2):]

for nm in ['index.html','luisa_24_heures.html']:
    p=dst/nm
    s=p.read_text(encoding='utf-8')
    s=s.replace("const BUILD_REVISION = 'B6';","const BUILD_REVISION = 'B7';",1)
    s=s.replace("const APP_EVIDENCE_STAGE = '24H_V120_ADVERSARIAL_RUNTIME_CLOSURE_B6';","const APP_EVIDENCE_STAGE = '24H_V120_BLIND_ACCESSIBILITY_CLOSURE_B7';",1)
    s=s.replace("const APP_RELEASE_SEQUENCE = 120000006;","const APP_RELEASE_SEQUENCE = 120000007;",1)
    s=s.replace("const APP_RELEASE_ID = '"+OLD_RID+"';","const APP_RELEASE_ID = '"+NEW_RID+"';",1)
    s=s.replace('.sr-badge.reflection { background: var(--ref-bg); color: var(--ref-border); }',
                '.sr-badge.reflection { background: var(--ref-bg); color: var(--ref-text); }',1)
    s=s.replace('color: #4a6e85; margin-bottom: 1rem; display: flex;',
                'color: var(--ref-text); margin-bottom: 1rem; display: flex;',1)
    s=s.replace('--ink: #f0ede6; --ink2: #ccc7bc; --ink3: #948e84; --ink4: #858078;',
                '--ink: #f0ede6; --ink2: #ccc7bc; --ink3: #948e84; --ink4: #8A857D;',1)
    marker='html[data-theme="dark"] .bn-item.active,html[data-theme="dark"] .bn-item:hover{color:#D4A843}'
    add=marker+'\nhtml[data-theme="dark"] .mark-btn:not(.done),html[data-theme="dark"] .resume-panel-btn.primary{color:#1A1714}\n@media (prefers-color-scheme: dark){html:not([data-theme="light"]) .mark-btn:not(.done),html:not([data-theme="light"]) .resume-panel-btn.primary{color:#1A1714}}'
    if marker not in s: raise SystemExit('dark closure marker missing')
    s=s.replace(marker,add,1)
    old='<div class="progress-summary-track" aria-label="Progression '+D+'{p.count} sur 24"><div class="progress-summary-fill" style="width:'+D+'{p.pct}%"></div></div>'
    new='<div class="progress-summary-track" role="progressbar" aria-label="Progression '+D+'{p.count} sur 24" aria-valuemin="0" aria-valuemax="24" aria-valuenow="'+D+'{p.count}"><div class="progress-summary-fill" style="width:'+D+'{p.pct}%"></div></div>'
    if old not in s: raise SystemExit('progress template missing')
    s=s.replace(old,new,1)
    oldmain='<main class="content" id="content" role="main" tabindex="-1" aria-label="Zone principale de lecture"></main>'
    newmain='<main class="content" id="content" role="main" tabindex="0" aria-label="Zone principale de lecture"></main>'
    if oldmain not in s: raise SystemExit('main target missing')
    s=s.replace(oldmain,newmain,1)
    s=refresh_csp(s)
    p.write_text(s,encoding='utf-8')

assert (dst/'index.html').read_bytes()==(dst/'luisa_24_heures.html').read_bytes()
shell=hashlib.sha256((dst/'index.html').read_bytes()).hexdigest()

p=dst/'manifest.json';j=json.loads(p.read_text())
j['version']='v120';j['build_revision']='B7';j['build']='B7';j['release_sequence']=NEW_SEQ;j['release_id']=NEW_RID
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')

p=dst/'sw.js';s=p.read_text()
s=re.sub(r"^/\*.*?\*/","/* v120 B7 — blind-adversarial accessibility/runtime closure from exact B6. Repairs five independently reproduced accessibility families while preserving corpus/Search/provenance/personal-state/backup semantics. */",s,count=1,flags=re.S)
s=s.replace("const BUILD_REVISION = 'B6';","const BUILD_REVISION = 'B7';",1)
s=s.replace("const RELEASE_SEQUENCE = 120000006;","const RELEASE_SEQUENCE = 120000007;",1)
s=s.replace("const RELEASE_ID = '"+OLD_RID+"';","const RELEASE_ID = '"+NEW_RID+"';",1)
s=re.sub(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell}';",s,count=1)
cache_line='const CACHE_NAME = ' + chr(96) + D + '{CACHE_PREFIX}v120-b7' + chr(96) + ';'
s=re.sub(r"const CACHE_NAME = .*?;",cache_line,s,count=1)
p.write_text(s)

p=dst/'version.json';j=json.loads(p.read_text())
j['app_version']='v120';j['build_revision']='B7';j['release_sequence']=NEW_SEQ;j['release_id']=NEW_RID
j['canonical_shell_sha256']=shell
j['cache_name']='scope-derived:luisa-24h-<scope-fingerprint>-v120-b7'
j['release_scope']='v120/B7 blind-adversarial accessibility/runtime closure from exact B6: semantic reflection contrast, dark primary-action contrast, muted dark text AA lift, progressbar ARIA semantics, and scrollable-main keyboard access.'
j['overall_release_status']='V120_B7_BLIND_ACCESSIBILITY_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED'
j['blind_adversarial_b7']={
 'date':'2026-10-03',
 'supersedes':['v120/B4','v120/B5','v120/B6'],
 'confirmed_b6_finding_families':[
  'light reflection search badge insufficient contrast',
  'dark gold primary controls retained white text',
  'dark reflection label and muted Espace text below AA',
  'progress summary used aria-label on roleless div',
  'prayer view scrollable main region lacked keyboard focusability'
 ],
 'repair_boundary':'shell accessibility/theme semantics + successor identity only',
 'corpus_changed':False,'search_data_changed':False,'provenance_text_changed':False,'personal_state_schema_changed':False,'backup_semantics_changed':False,
 'physical_pass_inferred':False,'production_deployment_authority':'NONE'
}
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')

allowed={'index.html','luisa_24_heures.html','manifest.json','sw.js','version.json'}
for q in src.rglob('*'):
    if q.is_file() and str(q.relative_to(src)) not in allowed:
        d=dst/q.relative_to(src);assert d.exists() and q.read_bytes()==d.read_bytes(),str(q)

print('24H_V120_B7_STAGE_PASS',shell)
