from pathlib import Path
import shutil, re, hashlib, json, base64

SRC=Path("24h-v120-b6-darkmode")
DST=Path("24h-v120-b7-darkmode")
if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC,DST)

html=(SRC/"luisa_24_heures.html").read_text(encoding="utf-8")
m=re.search(r"<script>([\s\S]*?)</script>",html,re.I)
assert m and len(re.findall(r"<script\b",html,re.I))==1
script=m.group(1)

for old,new in {
"const BUILD_REVISION = 'B6';":"const BUILD_REVISION = 'B7';",
"const APP_EVIDENCE_STAGE = '24H_V120_DARK_MODE_ADVERSARIAL_CLOSURE_B6';":"const APP_EVIDENCE_STAGE = '24H_V120_DARK_MODE_ADVERSARIAL_CLOSURE_B7';",
"const APP_RELEASE_SEQUENCE = 120000006;":"const APP_RELEASE_SEQUENCE = 120000007;",
"const APP_RELEASE_ID = '24h-v120-b6-20261003-dark-mode-adversarial-closure';":"const APP_RELEASE_ID = '24h-v120-b7-20261003-dark-mode-transition-closure';",
}.items():
    assert script.count(old)==1,(old,script.count(old))
    script=script.replace(old,new,1)
html=html[:m.start(1)]+script+html[m.end(1):]

sm=re.search(r'(<style id="dark-mode-contrast-closure-v120">)([\s\S]*?)(</style>)',html,re.I)
assert sm
old_style=sm.group(2)
extra=r'''
/* B7 blind-adversarial transient-contrast closure.
   Prevent an intermediate dark-on-dark frame while .integrity-btn animates
   from accent-pale to accent on hover/focus in dark mode. */
html[data-theme="dark"] .integrity-btn { transition:none !important; }
@media (prefers-color-scheme: dark){
  html:not([data-theme="light"]) .integrity-btn { transition:none !important; }
}
'''
new_style=old_style+extra
html=html[:sm.start(2)]+new_style+html[sm.end(2):]

# Rebind exact inline-script and closure-style CSP hashes.
script2=re.search(r"<script>([\s\S]*?)</script>",html,re.I).group(1)
script_b64=base64.b64encode(hashlib.sha256(script2.encode("utf-8")).digest()).decode("ascii")
html,n=re.subn(r"(script-src-elem\s+)'sha256-[^']+'",lambda mm:mm.group(1)+"'sha256-"+script_b64+"'",html,count=1)
assert n==1
old_style_b64=base64.b64encode(hashlib.sha256(old_style.encode("utf-8")).digest()).decode("ascii")
new_style_b64=base64.b64encode(hashlib.sha256(new_style.encode("utf-8")).digest()).decode("ascii")
assert ("sha256-"+old_style_b64) in html
html=html.replace("sha256-"+old_style_b64,"sha256-"+new_style_b64,1)

for name in ["index.html","luisa_24_heures.html"]:
    (DST/name).write_text(html,encoding="utf-8",newline="")
shell_sha=hashlib.sha256((DST/"luisa_24_heures.html").read_bytes()).hexdigest()

manifest=json.loads((DST/"manifest.json").read_text(encoding="utf-8"))
manifest.update({
 "version":"v120","build_revision":"B7","release_sequence":120000007,
 "release_id":"24h-v120-b7-20261003-dark-mode-transition-closure","build":"B7"
})
(DST/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

sw=(DST/"sw.js").read_text(encoding="utf-8")
sw,n=re.subn(r"/\* v120 B6 —[^*]*\*/",
             "/* v120 B7 — blind-adversarial transient dark-mode contrast closure successor from exact frozen v120/B6. Functional/content semantics unchanged; protected corpus/Search/provenance/personal-state/backup semantics unchanged. */",
             sw,count=1)
assert n==1
for old,new in {
"const BUILD_REVISION = 'B6';":"const BUILD_REVISION = 'B7';",
"const RELEASE_SEQUENCE = 120000006;":"const RELEASE_SEQUENCE = 120000007;",
"const RELEASE_ID = '24h-v120-b6-20261003-dark-mode-adversarial-closure';":"const RELEASE_ID = '24h-v120-b7-20261003-dark-mode-transition-closure';",
}.items():
    assert sw.count(old)==1,(old,sw.count(old))
    sw=sw.replace(old,new,1)
tick=chr(96); dol=chr(36)
cache_old="const CACHE_NAME = "+tick+dol+"{CACHE_PREFIX}v120-b6"+tick+";"
cache_new="const CACHE_NAME = "+tick+dol+"{CACHE_PREFIX}v120-b7"+tick+";"
assert sw.count(cache_old)==1,(cache_old,sw.count(cache_old))
sw=sw.replace(cache_old,cache_new,1)
sw,n=re.subn(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell_sha}';",sw,count=1)
assert n==1
(DST/"sw.js").write_text(sw,encoding="utf-8",newline="")

version=json.loads((DST/"version.json").read_text(encoding="utf-8"))
version["build_date"]="2026-10-03"
version["cache_name"]="scope-derived:luisa-24h-<scope-fingerprint>-v120-b7"
version["release_scope"]="v120/B7 blind-adversarial transient dark-mode contrast closure successor from exact frozen v120/B6. Removes the integrity-button dark-mode background transition that produced a transient 1.45:1 hover frame; no corpus/search/provenance/personal-state/backup semantics changed."
version["real_device_status"]="V120_B7_CANDIDATE__BLIND_REQUALIFICATION_REQUIRED__REAL_DEVICE_GATES_OPEN"
version["overall_release_status"]="V120_B7_DARK_MODE_TRANSITION_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED"
version["build_revision"]="B7"
version["release_sequence"]=120000007
version["release_id"]="24h-v120-b7-20261003-dark-mode-transition-closure"
version["canonical_shell_sha256"]=shell_sha
version["blind_adversarial_transient_contrast_closure_2026_10_03"]={
 "predecessor_candidate":"v120/B6",
 "predecessor_tree_sha":"d16b05961a5efedd63669433f8ed0947582f6f80",
 "finding":"In dark/system-dark mode, .integrity-btn hover text switched immediately to #1A1714 while its 150 ms background transition was still between accent-pale and accent; at ~30 ms the observed contrast was 1.45:1.",
 "repair":"Disable the integrity-button transition only in dark/system-dark mode so the high-contrast hover state is atomic.",
 "mutation_boundary":["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],
 "production_deployment_authority":"NONE",
 "physical_gate":"OPEN"
}
(DST/"version.json").write_text(json.dumps(version,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

h=(DST/"luisa_24_heures.html").read_text(encoding="utf-8")
script_final=re.search(r"<script>([\s\S]*?)</script>",h,re.I).group(1)
style_final=re.search(r'<style id="dark-mode-contrast-closure-v120">([\s\S]*?)</style>',h,re.I).group(1)
csp=re.search(r'Content-Security-Policy" content="([^"]+)"',h).group(1)
script_final_b64=base64.b64encode(hashlib.sha256(script_final.encode("utf-8")).digest()).decode("ascii")
style_final_b64=base64.b64encode(hashlib.sha256(style_final.encode("utf-8")).digest()).decode("ascii")
assert ("sha256-"+script_final_b64) in csp
assert ("sha256-"+style_final_b64) in csp
assert hashlib.sha256((DST/"index.html").read_bytes()).hexdigest()==shell_sha

changed=[]
for p in sorted(x for x in DST.rglob("*") if x.is_file()):
    rel=p.relative_to(DST); q=SRC/rel
    if hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(q.read_bytes()).digest():
        changed.append(str(rel))
assert changed==["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],changed

evidence={
 "candidate":"v120/B7","predecessor":"v120/B6","changed_files":changed,
 "script_sha256_base64":script_final_b64,"style_sha256_base64":style_final_b64,
 "canonical_shell_sha256":shell_sha,"csp_script_authorized":True,"csp_style_authorized":True,
 "production_deployment_authority":"NONE","physical_gate":"OPEN"
}
Path("24h-v120-b7-build-evidence.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
print(json.dumps(evidence,indent=2))
