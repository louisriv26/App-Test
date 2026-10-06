
#!/usr/bin/env python3
from pathlib import Path
import shutil,re,json,hashlib,base64
R=Path('.'); src=R/'24h-v120-b5-blind-repair'; dst=R/'24h-v120-b6-blind-closure'
if dst.exists(): raise SystemExit('destination exists')
shutil.copytree(src,dst)
NEW_BUILD='B6'; NEW_RELEASE_ID='24h-v120-b6-20261002-blind-adversarial-closure'; NEW_STAGE='24H_V120_BLIND_ADVERSARIAL_CLOSURE_B6'
def token(text): return "'sha256-"+base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()+"'"
def rebuild_csp(html):
    cm=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(">)',html)
    if not cm: raise RuntimeError('CSP missing')
    csp=cm.group(2); scripts=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',html,re.S|re.I); styles=re.findall(r'<style(?![^>]*\bsrc=)[^>]*>(.*?)</style>',html,re.S|re.I)
    def rep(policy,name,blocks):
        val=' '.join(token(x) for x in blocks); pat=re.compile(r'(^|;\s*)'+re.escape(name)+r'\s+[^;]+'); m=pat.search(policy)
        if not m: return policy.rstrip('; ')+'; '+name+' '+val
        return policy[:m.start()]+m.group(1)+name+' '+val+policy[m.end():]
    csp=rep(csp,'script-src-elem',scripts); csp=rep(csp,'style-src-elem',styles)
    return html[:cm.start(2)]+csp+html[cm.end(2):]
def mutate_shell(s):
    s=s.replace("const BUILD_REVISION = 'B5';","const BUILD_REVISION = 'B6';",1)
    s=s.replace("const APP_EVIDENCE_STAGE = '24H_V120_BLIND_ADVERSARIAL_REPAIR_B5';","const APP_EVIDENCE_STAGE = '24H_V120_BLIND_ADVERSARIAL_CLOSURE_B6';",1)
    s=s.replace("const APP_RELEASE_ID = '24h-v120-b5-20261002-blind-adversarial-repair';",f"const APP_RELEASE_ID = '{NEW_RELEASE_ID}';",1)
    s=s.replace('--accent: #7a5c10; --accent-light: #c9a84c; --accent-pale: #f0e8d4;','--accent: #7a5c10; --accent-light: #c9a84c; --accent-pale: #f0e8d4; --on-accent: #fff;',1)
    s=s.replace('--ink: #f0ede6; --ink2: #ccc7bc; --ink3: #948e84; --ink4: #858078;','--ink: #f0ede6; --ink2: #ccc7bc; --ink3: #948e84; --ink4: #8e8981; --on-accent: #1a1714;',1)
    pat=re.compile(r'(\{[^{}]*?background\s*:\s*var\(--accent\)(?:\s*!important)?[^{}]*?\bcolor\s*:\s*)(#fff|white)(\s*!important)?',re.I|re.S)
    s,n=pat.subn(lambda m:m.group(1)+'var(--on-accent)'+(m.group(3) or ''),s)
    if n < 10: raise RuntimeError(f'expected systemic accent replacements, got {n}')
    s=s.replace('.search-input { width: 100%; padding:', '.search-input { width: 100%; min-height:44px; padding:',1)
    s=s.replace('<div class="cross-ornament">✦ ✝ ✦</div>','<div class="cross-ornament" aria-hidden="true">✦ ✝ ✦</div>',1)
    return rebuild_csp(s)
for nm in ['index.html','luisa_24_heures.html']:
    p=dst/nm; p.write_text(mutate_shell(p.read_text(encoding='utf-8')),encoding='utf-8')
if (dst/'index.html').read_bytes()!=(dst/'luisa_24_heures.html').read_bytes(): raise RuntimeError('shell divergence')
shell_sha=hashlib.sha256((dst/'luisa_24_heures.html').read_bytes()).hexdigest()
p=dst/'manifest.json'; m=json.loads(p.read_text(encoding='utf-8')); m.update({'version':'v120','build_revision':NEW_BUILD,'build':NEW_BUILD,'release_sequence':120000001,'release_id':NEW_RELEASE_ID,'start_url':'./luisa_24_heures.html'}); p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=dst/'sw.js'; s=p.read_text(encoding='utf-8')
s=re.sub(r'^/\*.*?\*/','/* v120 B6 — full blind-adversarial closure successor from failed B5: current identity/CSP/cache binding plus systemic dark-mode on-accent, tertiary contrast and 44px search-target correction; protected application semantics unchanged. */',s,count=1,flags=re.S)
s=s.replace("const BUILD_REVISION = 'B5';","const BUILD_REVISION = 'B6';",1)
s=re.sub(r"const RELEASE_ID = '[^']+';",f"const RELEASE_ID = '{NEW_RELEASE_ID}';",s,count=1)
s=re.sub(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell_sha}';",s,count=1)
cache_expr="const CACHE_NAME = " + chr(96) + chr(36) + "{CACHE_PREFIX}v120-b6" + chr(96) + ";"
s=re.sub(r"const CACHE_NAME = .*?;",cache_expr,s,count=1)
p.write_text(s,encoding='utf-8')
p=dst/'version.json'; v=json.loads(p.read_text(encoding='utf-8'))
v.update({'app_version':'v120','build_revision':NEW_BUILD,'release_sequence':120000001,'release_id':NEW_RELEASE_ID,'cache_name':'scope-derived:luisa-24h-<scope-fingerprint>-v120-b6','canonical_shell':'./luisa_24_heures.html','canonical_shell_sha256':shell_sha,'release_scope':'v120/B6 blind-adversarial closure successor from failed B5. Corrects B5 cache-name interpolation and the independently discovered dark-mode on-accent/tertiary contrast and search-target defects. No corpus, Search semantics/results, provenance, personal-state, backup/import or update-v2 semantic change.','real_device_status':'V120_B6_CANDIDATE__BLIND_ADVERSARIAL_CLOSURE__REAL_DEVICE_GATES_OPEN','overall_release_status':'V120_B6_BLIND_ADVERSARIAL_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED','functional_freeze_status':'V120_B6_BLIND_ADVERSARIAL_CLOSURE__PROTECTED_FUNCTIONAL_AND_CONTENT_SURFACES_UNCHANGED__PHYSICAL_GATES_OPEN','postfreeze_reopen_evidence':'B6 supersedes failed B4 and B5 after independent blind verification. Mutation remains confined to release-shell identity/CSP/cache metadata and bounded CSS/accessibility presentation corrections; protected semantics are unchanged.'})
page=(dst/'index.html').read_text(encoding='utf-8'); scripts=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',page,re.S|re.I); styles=re.findall(r'<style(?![^>]*\bsrc=)[^>]*>(.*?)</style>',page,re.S|re.I)
v['security_inline_script_sha256_base64']=token(scripts[0]).strip("'") if len(scripts)==1 else [token(x).strip("'") for x in scripts]
v['security_inline_style_sha256_base64']=[token(x).strip("'") for x in styles]
v['security_stage_status']=f'CSP3_ARCHITECTURE_PRESERVED__V120_B6_INLINE_SCRIPT_AND_STYLE_HASHES_REBOUND_TO_EXACT_V120_B6_SUCCESSOR_SHELL__SERVICE_WORKER_CANONICAL_SHELL_HASH_BOUND_TO_EXACT_V120_B6_SHELL_{shell_sha.upper()}'
for key in ['known_blockers','external_open_gates']: v[key]=[str(x).replace('v120/B5','v120/B6') for x in (v.get(key) or [])]
literal_cache=chr(36)+'{CACHE_PREFIX}v120-b5'
v['blind_adversarial_v120_b6']={'date':'2026-10-02','predecessor':'v120/B5','predecessor_tree':'b1000f0e0187ec8f77359c2df2e491746f0a24d2','b5_status':'FAILED_SUPERSEDED','findings':['B24H-B5-001: CACHE_NAME created a literal '+literal_cache+' cache instead of the scope-derived cache.','B24H-B5-002: dark-mode accent-filled primary controls used white text on #d4a843 (~2.21:1), a systemic on-accent polarity defect.','B24H-B5-003: dark tertiary --ink4 text on common bg2 surfaces measured ~4.34:1, below 4.5:1.','B24H-B5-004: the governed search input rendered ~43.4px high, below the 44px touch floor.','B24H-B5-005: the home cross ornament is decorative and is now explicitly aria-hidden; its decorative low contrast is not treated as information loss.'],'root_cause':'The dark theme inverted the accent luminance without a semantic on-accent token; tertiary dark token and search control geometry were not covered by the earlier bounded target list. B5 cache repair script also escaped template interpolation.','repair':'Introduce light/dark --on-accent tokens and apply them systematically to accent-filled CSS rules; raise dark --ink4 to #8e8981; impose min-height:44px on search inputs; mark the ornamental cross aria-hidden; correct CACHE_NAME to the true scope-derived template; fully rebind identity/CSP/canonical-shell metadata.','protected_surfaces':['CORPUS','TEXT_LIBRARY','SPEECH_DATA','Search semantics/results','provenance','personal-state schema/semantics','backup/import semantics','IndexedDB/Web-Locks architecture','update-v2 protocol'],'physical_pass_inferred':False,'production_deployment_authority':'NONE'}
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
allowed={'index.html','luisa_24_heures.html','manifest.json','sw.js','version.json'}
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
fa={str(q.relative_to(src)):sha(q) for q in src.rglob('*') if q.is_file()}; fb={str(q.relative_to(dst)):sha(q) for q in dst.rglob('*') if q.is_file()}; ch={k for k in set(fa)|set(fb) if fa.get(k)!=fb.get(k)}
if ch!=allowed: raise RuntimeError(f'unexpected boundary {ch}')
sw=(dst/'sw.js').read_text(encoding='utf-8'); escaped='\\'+chr(36)+'{CACHE_PREFIX}'
if escaped in sw: raise RuntimeError('escaped cache interpolation remains')
expected_cache="const CACHE_NAME = " + chr(96) + chr(36) + "{CACHE_PREFIX}v120-b6" + chr(96) + ";"
assert expected_cache in sw
print('24H_V120_B6_STAGE_PASS',shell_sha)
