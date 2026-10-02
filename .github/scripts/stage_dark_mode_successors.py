#!/usr/bin/env python3
from pathlib import Path
import re, json, hashlib, base64, shutil
R=Path('.'); TODAY='2026-10-02'
def req(c,m):
    if not c: raise SystemExit('FAIL: '+m)
def rep(s,a,b,n=None):
    c=s.count(a); req(c==(n if n is not None else c) and c>0,f'replace {a!r}: {c}')
    if n is not None: req(c==n,f'expected {n} {a!r}, got {c}')
    return s.replace(a,b)
def cp(a,b): req(a.exists(),f'missing {a}'); req(not b.exists(),f'exists {b}'); shutil.copytree(a,b)
def hfile(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def h64(s): return base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()

# 24H v120 from exact live v119
s24=Path('/tmp/prod24'); d24=R/'24h-v120-b1-darkmode'; cp(s24,d24); shutil.rmtree(d24/'.git',ignore_errors=True)
css='''\n<style id="dark-mode-contrast-closure-v120">\n@media (prefers-color-scheme: dark){\nhtml:not([data-theme="light"]) .onboarding-primary,html:not([data-theme="light"]) .sf-btn.active{color:#1A1714}\nhtml:not([data-theme="light"]) .sr-badge.reflection{color:#A9D2EA;border-color:#A9D2EA}\nhtml:not([data-theme="light"]) .sr-badge.speech{color:#D0AFE8;border-color:#D0AFE8}\nhtml:not([data-theme="light"]) div.d{color:#8A857D}\n}\nhtml[data-theme="dark"] .onboarding-primary,html[data-theme="dark"] .sf-btn.active{color:#1A1714}\nhtml[data-theme="dark"] .sr-badge.reflection{color:#A9D2EA;border-color:#A9D2EA}\nhtml[data-theme="dark"] .sr-badge.speech{color:#D0AFE8;border-color:#D0AFE8}\nhtml[data-theme="dark"] div.d{color:#8A857D}\n</style>\n'''
for nm in ['index.html','luisa_24_heures.html']:
 p=d24/nm; s=p.read_text(); req('</head>' in s,'24H head'); s=s.replace('</head>',css+'</head>',1)
 s=rep(s,"const APP_VERSION = 'v119';","const APP_VERSION = 'v120';",1)
 s=rep(s,"const APP_EVIDENCE_STAGE = '24H_V119_ADVERSARIAL_UX_CORRECTION_B1';","const APP_EVIDENCE_STAGE = '24H_V120_DARK_MODE_CLOSURE_B1';",1)
 s=rep(s,'const APP_RELEASE_SEQUENCE = 119000001;','const APP_RELEASE_SEQUENCE = 120000001;',1)
 s=rep(s,"const APP_RELEASE_ID = '24h-v119-b1-20261001-adversarial-ux-correction';","const APP_RELEASE_ID = '24h-v120-b1-20261002-dark-mode-closure';",1)
 p.write_text(s)
req((d24/'index.html').read_bytes()==(d24/'luisa_24_heures.html').read_bytes(),'24H shells differ')
sh=hfile(d24/'index.html')
m=json.loads((d24/'manifest.json').read_text()); req(m['version']=='v119','24H manifest'); m.update(version='v120',build_revision='B1',release_sequence=120000001,release_id='24h-v120-b1-20261002-dark-mode-closure',build='B1'); (d24/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
p=d24/'sw.js'; s=p.read_text(); s=rep(s,"const APP_VERSION = 'v119';","const APP_VERSION = 'v120';",1); s=rep(s,'const RELEASE_SEQUENCE = 119000001;','const RELEASE_SEQUENCE = 120000001;',1); s=rep(s,"const RELEASE_ID = '24h-v119-b1-20261001-adversarial-ux-correction';","const RELEASE_ID = '24h-v120-b1-20261002-dark-mode-closure';",1); s=re.sub(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{sh}';",s,count=1); s=rep(s,'const CACHE_NAME = `${CACHE_PREFIX}v119-b1`;','const CACHE_NAME = `${CACHE_PREFIX}v120-b1`;',1); p.write_text(s)
p=d24/'version.json'; v=json.loads(p.read_text()); req(v['app_version']=='v119','24H version'); v.update(app_version='v120',build_date=TODAY,cache_name='scope-derived:luisa-24h-<scope-fingerprint>-v120-b1',release_sequence=120000001,release_id='24h-v120-b1-20261002-dark-mode-closure',canonical_shell_sha256=sh,pwa_update_predecessor_version='v119',pwa_update_predecessor_zip_sha256='9f1b83a313330b3b57553851e73612dc006819afee6915b3cda8881c427b9b1a'); v['release_scope']='v120/B1 bounded dark-mode contrast successor from exact live/frozen v119/B1; protected functional and content semantics inherited unchanged.'; v['real_device_status']='V120_B1_CANDIDATE__NONPHYSICAL_DARK_MODE_CLOSURE__REAL_DEVICE_GATES_OPEN'; v['overall_release_status']='V120_B1_DARK_MODE_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED'; v['dark_mode_v120_b1']={'date':TODAY,'exact_predecessor_commit':'50a11cb67a79882e6e80088d6740b6db4827c06c','exact_predecessor_tree':'f8d73f59ee09e302f7b860553adc946702917dfb','exact_predecessor_package_sha256':'9f1b83a313330b3b57553851e73612dc006819afee6915b3cda8881c427b9b1a','corpus_changed':False,'search_changed':False,'provenance_changed':False,'personal_state_changed':False,'backup_semantics_changed':False,'physical_pass_inferred':False,'production_deployment_authority':'NONE'}; (d24/'version.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

# LDC v136/R9 from exact v135/R8
src=R/'ldc-v135-r8-governed-r7'; dst=R/'ldc-v136-r9-darkmode'; cp(src,dst); oa='v2.19.135-R1B-UX-ACCESS-R8'; na='v2.19.136-R1B-UX-ACCESS-R9'; orv='ldc-v2.19.135-R1B-ux-access-r8'; nrv='ldc-v2.19.136-R1B-ux-access-r9'
p=dst/'index.html'; s=p.read_text(); s=rep(s,oa,na); s=rep(s,orv,nrv); s=rep(s,"[1] || '135'","[1] || '136'",1)
for a,b in [
('background:var(--gold-pale);color:#7A5A20;border-radius:10px;','background:var(--gold-pale);color:var(--gold-text);border-radius:10px;'),
('background:var(--gold-pale);color:#7A5A20;}\n.rc-tag.exact','background:var(--gold-pale);color:var(--gold-text);}\n.rc-tag.exact'),
('.rc-tag.approximate{background:var(--gold-pale);color:#7A5A20;}','.rc-tag.approximate{background:var(--gold-pale);color:var(--gold-text);}'),
('.hsi-gold {background:var(--gold-pale);color:#7A5A20;}','.hsi-gold {background:var(--gold-pale);color:var(--gold-text);}'),
('.help-chip.light{background:var(--gold-pale);color:#7A5A20;}','.help-chip.light{background:var(--gold-pale);color:var(--gold-text);}'),
('font-size:var(--help-tip-size);color:#7A5A20;line-height:1.6','font-size:var(--help-tip-size);color:var(--gold-text);line-height:1.6'),
('margin-top:5px;background:var(--gold-pale);color:#7A5A20;}','margin-top:5px;background:var(--gold-pale);color:var(--gold-text);}'),
('style="background:rgba(201,168,76,.15);color:#7A5A20;"','style="background:rgba(201,168,76,.15);color:var(--gold-text);"')]:
 if a in s: s=s.replace(a,b)
req(s.count('#7A5A20')==1 and '.st-luisa{background:var(--gold-pale);color:#7A5A20;}' in s,'LDC hardcode boundary'); p.write_text(s)
p=dst/'sw.js'; s=p.read_text(); s=rep(s,orv,nrv); s=rep(s,oa,na); p.write_text(s)
p=dst/'offline_manifest.json'; j=json.loads(p.read_text()); req(j['app_version']==oa and j['page_worker_revision']==orv,'LDC offline'); j['app_version']=na; j['page_worker_revision']=nrv; j['rebuild_status']='V136_R9_BOUNDED_DARK_MODE_GOLD_LABEL_CONTRAST_CLOSURE__V135_R8_RELEASE_BINDING_INHERITED__CORPUS_SEARCH_PROVENANCE_USER_STATE_OFFLINE_CONTENT_BINDING_UNCHANGED__PUBLIC_RELEASE_NOT_AUTHORIZED'; p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
p=dst/'version.json'; j=json.loads(p.read_text()); req(j['app_version']==oa and j['page_worker_revision']==orv,'LDC version'); j.update(app_version=na,public_version='136',page_worker_revision=nrv,baseline_candidate_sha256='SUPERSEDED__SEE_GOVERNING_STATE_FOR_EXACT_V136_PACKAGE_HASH',rebuild_status='V136_R9_BOUNDED_DARK_MODE_GOLD_LABEL_CONTRAST_CLOSURE__V135_R8_RELEASE_BINDING_INHERITED__CORPUS_SEARCH_PROVENANCE_USER_STATE_OFFLINE_CONTENT_BINDING_UNCHANGED__PUBLIC_RELEASE_NOT_AUTHORIZED',physical_ipad_gate='OPEN__EXACT_V136_SUCCESSOR_BYTES_REQUIRED__PHYSICAL_PASS_NEVER_INFERRED',physical_iphone_gate='OPEN__EXACT_V136_SUCCESSOR_BYTES_REQUIRED__PHYSICAL_PASS_NEVER_INFERRED',public_deployment_authorized=False,public_release='NOT_AUTHORIZED'); j['dark_mode_v136_r9']={'date':TODAY,'exact_predecessor_tree':'ba58aff745cbb016ff465566e86d7a36eac9351d','exact_predecessor_package_sha256':'b4f71d24cbcec01d01bbff813376b7d2b4e6afe9404b93ade2cff36c0657353f','repair':'theme-aware --gold-text for confirmed gold-pale labels','corpus_changed':False,'search_changed':False,'provenance_changed':False,'user_state_changed':False,'offline_content_assets_changed':False,'physical_pass_inferred':False,'production_deployment_authority':'NONE'}; p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')

# Lettres v2.11 from exact v2.10
src=R/'lettres-v2.10-b1-prephysical'; dst=R/'lettres-v2.11-b1-darkmode'; cp(src,dst); p=dst/'index.html'; before=p.read_text(); s=before
css='''\n/* v2.11 dark-mode selector/contrast closure */\n@media (prefers-color-scheme: dark){\n:root:not([data-theme="light"]) .help-topic-select,:root:not([data-theme="light"]) #search-sort{-webkit-appearance:none;appearance:none;color-scheme:dark;background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),linear-gradient(135deg,var(--muted) 50%,transparent 50%);background-position:calc(100% - 14px) 50%,calc(100% - 9px) 50%;background-size:5px 5px,5px 5px;background-repeat:no-repeat}\n:root:not([data-theme="light"]) .path-step.done{color:#1A1612}\n:root:not([data-theme="light"]) .search-term-flash{background:rgba(255,214,74,.20)}\n:root:not([data-theme="light"]) .help-dot:not(.active)::after{background:var(--muted)}\n}\n[data-theme="dark"] .help-topic-select,[data-theme="dark"] #search-sort{-webkit-appearance:none;appearance:none;color-scheme:dark;background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),linear-gradient(135deg,var(--muted) 50%,transparent 50%);background-position:calc(100% - 14px) 50%,calc(100% - 9px) 50%;background-size:5px 5px,5px 5px;background-repeat:no-repeat}\n[data-theme="dark"] .path-step.done{color:#1A1612}\n[data-theme="dark"] .search-term-flash{background:rgba(255,214,74,.20)}\n[data-theme="dark"] .help-dot:not(.active)::after{background:var(--muted)}\n'''
i=s.find('</style>'); req(i>0,'Lettres style'); s=s[:i]+css+s[i:]; s=rep(s,"const APP_VERSION = '2.10';","const APP_VERSION = '2.11';",1); s=s.replace('shell-v2.10-b1','shell-v2.11-b1').replace('corpus-v2.10-b1','corpus-v2.11-b1').replace('v2.10 \u00b7 2026-09-30','v2.11 \u00b7 2026-10-02').replace('Version de l\u2019app :</strong> v2.10','Version de l\u2019app :</strong> v2.11')
def blocks(x,tag): return re.findall(fr'<{tag}(?![^>]*\\bsrc=)[^>]*>(.*?)</{tag}>',x,re.S|re.I)
for tag in ['style','script']:
 a,b=blocks(before,tag),blocks(s,tag); req(len(a)==len(b),f'Lettres {tag} blocks')
 for x,y in zip(a,b):
  if x!=y:
   oh='sha256-'+h64(x); nh='sha256-'+h64(y); req(oh in s,f'Lettres CSP {tag} old hash'); s=s.replace(oh,nh)
p.write_text(s)
p=dst/'manifest.json'; j=json.loads(p.read_text()); req(j['version']=='2.10','Lettres manifest'); j.update(version='2.11',build_revision='B1',release_id='lettres-v2.11-b1-darkmode'); p.write_text(json.dumps(j,ensure_ascii=False,indent=4)+'\n')
p=dst/'sw.js'; s=p.read_text(); req('v2.10' in s,'Lettres sw'); p.write_text(s.replace('v2.10','v2.11'))

# Marie v47 from exact v46
src=R/'marie-v46'; dst=R/'marie-v47-b1-darkmode'; cp(src,dst); p=dst/'index.html'; s=p.read_text(); s=rep(s,'--primary-light: #3D6399;','--primary-light: #3D6399;\n  --primary-action-hover-bg: #3D6399;',1); s=s.replace('--primary: #5E92CC; --primary-light: #78A8DE;','--primary: #5E92CC; --primary-light: #78A8DE; --primary-action-hover-bg:#3D6399;'); req(s.count('--primary-action-hover-bg:#3D6399;')==2,'Marie dark tokens'); s=rep(s,'.backup-btn.primary:hover, .backup-btn.primary:focus-visible { color: #fff; background: var(--primary-light); }','.backup-btn.primary:hover, .backup-btn.primary:focus-visible { color: #fff; background: var(--primary-action-hover-bg); }',1); s=rep(s,"const APP_VERSION = '46';","const APP_VERSION = '47';",1); p.write_text(s); p=dst/'sw.js'; p.write_text(rep(p.read_text(),"const VERSION = '46';","const VERSION = '47';",1))

# protected bytes
for q in d24.rglob('*'):
 if q.is_file() and q.name not in {'index.html','luisa_24_heures.html','manifest.json','sw.js','version.json'}: req(q.read_bytes()==(s24/q.relative_to(d24)).read_bytes(),f'24H protected {q}')
for q in (R/'ldc-v136-r9-darkmode/corpus').rglob('*'):
 if q.is_file(): req(q.read_bytes()==(R/'ldc-v135-r8-governed-r7'/q.relative_to(R/'ldc-v136-r9-darkmode')).read_bytes(),f'LDC corpus {q}')
req((R/'lettres-v2.11-b1-darkmode/corpus.json').read_bytes()==(R/'lettres-v2.10-b1-prephysical/corpus.json').read_bytes(),'Lettres corpus')
for q in (R/'marie-v47-b1-darkmode/corpus').rglob('*'):
 if q.is_file(): req(q.read_bytes()==(R/'marie-v46'/q.relative_to(R/'marie-v47-b1-darkmode')).read_bytes(),f'Marie corpus {q}')
print('STAGE_SUCCESSORS_PASS'); print('24H_SHELL_SHA256',sh)
