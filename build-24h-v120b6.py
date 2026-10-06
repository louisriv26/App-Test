from pathlib import Path
import shutil, re, hashlib, json, base64

SRC=Path("24h-v120-b5-darkmode")
DST=Path("24h-v120-b6-darkmode")
if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC,DST)

html=(SRC/"luisa_24_heures.html").read_text(encoding="utf-8")
m=re.search(r"<script>([\s\S]*?)</script>",html,re.I)
assert m and len(re.findall(r"<script\b",html,re.I))==1
script=m.group(1)

script_repls={
"const BUILD_REVISION = 'B5';":"const BUILD_REVISION = 'B6';",
"const APP_EVIDENCE_STAGE = '24H_V120_DARK_MODE_CLOSURE_B5_CSP_RUNTIME_REPAIR';":"const APP_EVIDENCE_STAGE = '24H_V120_DARK_MODE_ADVERSARIAL_CLOSURE_B6';",
"const APP_RELEASE_SEQUENCE = 120000005;":"const APP_RELEASE_SEQUENCE = 120000006;",
"const APP_RELEASE_ID = '24h-v120-b5-20261003-dark-mode-csp-runtime-repair';":"const APP_RELEASE_ID = '24h-v120-b6-20261003-dark-mode-adversarial-closure';",
}
for old,new in script_repls.items():
    assert script.count(old)==1,(old,script.count(old))
    script=script.replace(old,new,1)
html=html[:m.start(1)]+script+html[m.end(1):]

sm=re.search(r'(<style id="dark-mode-contrast-closure-v120">)([\s\S]*?)(</style>)',html,re.I)
assert sm
old_style=sm.group(2)
extra=r'''
/* B6 blind-adversarial dark-mode accessibility closure.
   Systematic class repair: accent-gold backgrounds must never retain white text
   in dark mode; tertiary ink must clear 4.5:1 even on --bg3. */
html[data-theme="dark"] { --ink4:#8F8A81; }
html[data-theme="dark"] .integrity-btn:hover,
html[data-theme="dark"] .onboarding-primary,
html[data-theme="dark"] .sf-btn.active,
html[data-theme="dark"] .sf-btn[aria-pressed="true"],
html[data-theme="dark"] .mark-btn:not(.done),
html[data-theme="dark"] .update-banner,
html[data-theme="dark"] .update-refresh-btn,
html[data-theme="dark"] .update-dismiss-btn,
html[data-theme="dark"] .cc-primary,
html[data-theme="dark"] .resume-panel-btn.primary,
html[data-theme="dark"] .note-save-btn,
html[data-theme="dark"] .library-quick-chip.active,
html[data-theme="dark"] .skip-link,
html[data-theme="dark"] .help-round:hover,
html[data-theme="dark"] .help-round:focus-visible,
html[data-theme="dark"] .panel-close-btn:hover,
html[data-theme="dark"] .panel-close-btn:focus-visible,
html[data-theme="dark"] .hour-end-btn.primary,
html[data-theme="dark"].android-scroll-fix.android-highlight-mode .android-highlight-toggle,
html[data-theme="dark"].stage6a-runtime.android-scroll-fix.android-highlight-mode .android-highlight-toggle,
html[data-theme="dark"] .theme-pref-btn.active,
html[data-theme="dark"] .library-title-mark-btn[aria-pressed="true"] {
  color:#1A1714 !important;
}
@media (prefers-color-scheme: dark){
  html:not([data-theme="light"]) { --ink4:#8F8A81; }
  html:not([data-theme="light"]) .integrity-btn:hover,
  html:not([data-theme="light"]) .onboarding-primary,
  html:not([data-theme="light"]) .sf-btn.active,
  html:not([data-theme="light"]) .sf-btn[aria-pressed="true"],
  html:not([data-theme="light"]) .mark-btn:not(.done),
  html:not([data-theme="light"]) .update-banner,
  html:not([data-theme="light"]) .update-refresh-btn,
  html:not([data-theme="light"]) .update-dismiss-btn,
  html:not([data-theme="light"]) .cc-primary,
  html:not([data-theme="light"]) .resume-panel-btn.primary,
  html:not([data-theme="light"]) .note-save-btn,
  html:not([data-theme="light"]) .library-quick-chip.active,
  html:not([data-theme="light"]) .skip-link,
  html:not([data-theme="light"]) .help-round:hover,
  html:not([data-theme="light"]) .help-round:focus-visible,
  html:not([data-theme="light"]) .panel-close-btn:hover,
  html:not([data-theme="light"]) .panel-close-btn:focus-visible,
  html:not([data-theme="light"]) .hour-end-btn.primary,
  html:not([data-theme="light"]).android-scroll-fix.android-highlight-mode .android-highlight-toggle,
  html:not([data-theme="light"]).stage6a-runtime.android-scroll-fix.android-highlight-mode .android-highlight-toggle,
  html:not([data-theme="light"]) .theme-pref-btn.active,
  html:not([data-theme="light"]) .library-title-mark-btn[aria-pressed="true"] {
    color:#1A1714 !important;
  }
}
'''
new_style=old_style+extra
html=html[:sm.start(2)]+new_style+html[sm.end(2):]

script2=(re.search(r"<script>([\s\S]*?)</script>",html,re.I)).group(1)
new_script_b64=base64.b64encode(hashlib.sha256(script2.encode("utf-8")).digest()).decode("ascii")
html,n=re.subn(r"(script-src-elem\s+)'sha256-[^']+'",lambda mm:mm.group(1)+"'sha256-"+new_script_b64+"'",html,count=1)
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
 "version":"v120","build_revision":"B6","release_sequence":120000006,
 "release_id":"24h-v120-b6-20261003-dark-mode-adversarial-closure","build":"B6"
})
(DST/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

sw=(DST/"sw.js").read_text(encoding="utf-8")
sw=sw.replace("/* v120 B5 — bounded CSP/runtime identity repair successor from exact frozen v120/B4. Dark-mode CSS/content semantics unchanged; protected corpus/Search/provenance/personal-state/backup semantics unchanged. */",
              "/* v120 B6 — blind-adversarial dark-mode accessibility closure successor from exact frozen v120/B5. Functional/content semantics unchanged; protected corpus/Search/provenance/personal-state/backup semantics unchanged. */",1)
for old,new in {
"const BUILD_REVISION = 'B5';":"const BUILD_REVISION = 'B6';",
"const RELEASE_SEQUENCE = 120000005;":"const RELEASE_SEQUENCE = 120000006;",
"const RELEASE_ID = '24h-v120-b5-20261003-dark-mode-csp-runtime-repair';":"const RELEASE_ID = '24h-v120-b6-20261003-dark-mode-adversarial-closure';",
}.items():
    assert sw.count(old)==1,(old,sw.count(old)); sw=sw.replace(old,new,1)
cache_old="const CACHE_NAME = `${CACHE_PREFIX}v120-b5`;"
cache_new="const CACHE_NAME = `${CACHE_PREFIX}v120-b6`;"
assert sw.count(cache_old)==1,(cache_old,sw.count(cache_old))
sw=sw.replace(cache_old,cache_new,1)
sw,n=re.subn(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell_sha}';",sw,count=1)
assert n==1
(DST/"sw.js").write_text(sw,encoding="utf-8",newline="")

version=json.loads((DST/"version.json").read_text(encoding="utf-8"))
version["build_date"]="2026-10-03"
version["cache_name"]="scope-derived:luisa-24h-<scope-fingerprint>-v120-b6"
version["release_scope"]="v120/B6 blind-adversarial dark-mode accessibility closure successor from exact frozen v120/B5. Repairs inherited low-contrast accent-primary states and tertiary dark text; no corpus/search/provenance/personal-state/backup semantics changed."
version["real_device_status"]="V120_B6_CANDIDATE__BLIND_REQUALIFICATION_REQUIRED__REAL_DEVICE_GATES_OPEN"
version["overall_release_status"]="V120_B6_DARK_MODE_ADVERSARIAL_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED"
version["build_revision"]="B6"
version["release_sequence"]=120000006
version["release_id"]="24h-v120-b6-20261003-dark-mode-adversarial-closure"
version["canonical_shell_sha256"]=shell_sha
version["blind_adversarial_dark_mode_closure_2026_10_03"]={
 "predecessor_candidate":"v120/B5",
 "predecessor_tree_sha":"6fc3cd1506e25c3f706513a7624e9586b7744a7d",
 "findings":[
   "Accent-gold primary controls retained white text in dark mode (~2.21:1).",
   "Tertiary --ink4 text remained below 4.5:1 on dark card/background surfaces (observed ~4.34:1)."
 ],
 "repair":[
   "Use #1A1714 for all enumerated accent-gold control states under explicit dark and system-dark conditions.",
   "Raise dark --ink4 to #8F8A81, preserving hierarchy under --ink3 while clearing 4.5:1 on --bg3."
 ],
 "mutation_boundary":["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],
 "production_deployment_authority":"NONE","physical_gate":"OPEN"
}
(DST/"version.json").write_text(json.dumps(version,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

h=(DST/"luisa_24_heures.html").read_text(encoding="utf-8")
script_final=re.search(r"<script>([\s\S]*?)</script>",h,re.I).group(1)
style_final=re.search(r'<style id="dark-mode-contrast-closure-v120">([\s\S]*?)</style>',h,re.I).group(1)
csp=re.search(r'Content-Security-Policy" content="([^"]+)"',h).group(1)
script_b64=base64.b64encode(hashlib.sha256(script_final.encode("utf-8")).digest()).decode("ascii")
style_b64=base64.b64encode(hashlib.sha256(style_final.encode("utf-8")).digest()).decode("ascii")
assert ("sha256-"+script_b64) in csp
assert ("sha256-"+style_b64) in csp
assert hashlib.sha256((DST/"index.html").read_bytes()).hexdigest()==shell_sha

changed=[]
for p in sorted(x for x in DST.rglob("*") if x.is_file()):
    rel=p.relative_to(DST); q=SRC/rel
    if hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(q.read_bytes()).digest():
        changed.append(str(rel))
assert changed==["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],changed

evidence={
 "candidate":"v120/B6","predecessor":"v120/B5","changed_files":changed,
 "script_sha256_base64":script_b64,"style_sha256_base64":style_b64,
 "canonical_shell_sha256":shell_sha,"csp_script_authorized":True,"csp_style_authorized":True,
 "production_deployment_authority":"NONE","physical_gate":"OPEN"
}
Path("24h-v120-b6-build-evidence.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
print(json.dumps(evidence,indent=2))
