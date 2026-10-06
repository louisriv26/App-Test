#!/usr/bin/env python3
import base64, hashlib, json, pathlib, re, shutil
SRC=pathlib.Path("24h-v120-b8-update-activation-closure")
DST=pathlib.Path("24h-v120-b9-converged-closure")
RID="24h-v120-b9-20261003-converged-activation-contrast-closure"
SEQ=120000009
if DST.exists(): shutil.rmtree(DST)
shutil.copytree(SRC,DST)
def sha_b64(text): return base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode("ascii")
html=(DST/"index.html").read_text(encoding="utf-8")
assert "const BUILD_REVISION = 'B8';" in html
assert "const APP_RELEASE_SEQUENCE = 120000008;" in html
assert "24h-v120-b8-20261003-update-activation-closure" in html
assert "const activated=await waitForWorkerState(prepared.worker,['activated'],15000);" in html
assert "target_worker_identity_mismatch_after_activation" in html
assert "html[data-theme=\"dark\"] .integrity-btn { transition:none !important; }" not in html
closure=r'''
/* B9 convergence closure: retain B7 transient-contrast repair on top of B8
   update-activation repair. Dark/system-dark hover state is atomic. */
html[data-theme="dark"] .integrity-btn { transition:none !important; }
@media (prefers-color-scheme: dark){
  html:not([data-theme="light"]) .integrity-btn { transition:none !important; }
}
'''
marker="</style>\n</head>"; pos=html.rfind(marker); assert pos>0
html=html[:pos]+closure+html[pos:]
html=html.replace("const BUILD_REVISION = 'B8';","const BUILD_REVISION = 'B9';",1)
html=html.replace("const APP_EVIDENCE_STAGE = '24H_V120_UPDATE_ACTIVATION_CLOSURE_B8';","const APP_EVIDENCE_STAGE = '24H_V120_CONVERGED_ACTIVATION_CONTRAST_CLOSURE_B9';",1)
html=html.replace("const APP_RELEASE_SEQUENCE = 120000008;","const APP_RELEASE_SEQUENCE = 120000009;",1)
html=html.replace("const APP_RELEASE_ID = '24h-v120-b8-20261003-update-activation-closure';",f"const APP_RELEASE_ID = '{RID}';",1)
scripts=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>',html,re.I)
styles=re.findall(r'<style[^>]*>([\s\S]*?)</style>',html,re.I)
assert scripts and styles
script_tokens=[f"'sha256-{sha_b64(x)}'" for x in scripts]
style_tokens=[f"'sha256-{sha_b64(x)}'" for x in styles]
m=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(")',html,re.I); assert m
csp=m.group(2)
csp,n1=re.subn(r"script-src-elem\s+[^;]*;", "script-src-elem "+" ".join(script_tokens)+";", csp, count=1)
csp,n2=re.subn(r"style-src-elem\s+[^;]*;", "style-src-elem "+" ".join(style_tokens)+";", csp, count=1)
assert n1==1 and n2==1
html=html[:m.start(2)]+csp+html[m.end(2):]
for t in script_tokens+style_tokens: assert t in csp
(DST/"index.html").write_text(html,encoding="utf-8")
(DST/"luisa_24_heures.html").write_text(html,encoding="utf-8")
shell_sha=hashlib.sha256(html.encode("utf-8")).hexdigest()
manifest=json.loads((DST/"manifest.json").read_text(encoding="utf-8"))
manifest.update({"version":"v120","build_revision":"B9","release_sequence":SEQ,"release_id":RID,"build":"B9"})
(DST/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
sw=(DST/"sw.js").read_text(encoding="utf-8")
repls=[
 ("/* v120 B8 — bounded update-activation successor from failed B6; page orchestration repaired, protected content and service-worker semantics otherwise unchanged. */","/* v120 B9 — converged successor: B8 update-activation repair plus B7 transient-contrast closure; protected content/service-worker activation semantics otherwise unchanged. */"),
 ("const BUILD_REVISION = 'B8';","const BUILD_REVISION = 'B9';"),
 ("const RELEASE_SEQUENCE = 120000008;","const RELEASE_SEQUENCE = 120000009;"),
 ("const RELEASE_ID = '24h-v120-b8-20261003-update-activation-closure';",f"const RELEASE_ID = '{RID}';"),
 ("`${CACHE_PREFIX}v120-b8`","`${CACHE_PREFIX}v120-b9`")
]
for a,b in repls:
    assert a in sw,a
    sw=sw.replace(a,b,1)
sw,n=re.subn(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell_sha}';",sw,count=1); assert n==1
(DST/"sw.js").write_text(sw,encoding="utf-8")
v=json.loads((DST/"version.json").read_text(encoding="utf-8"))
v["build_revision"]="B9"; v["release_sequence"]=SEQ; v["release_id"]=RID
v["cache_name"]="scope-derived:luisa-24h-<scope-fingerprint>-v120-b9"; v["canonical_shell_sha256"]=shell_sha
v["release_scope"]="v120/B9 converged successor to v120/B7 and v120/B8. Retains B7 atomic dark/system-dark integrity-button transition closure and B8 exact prepared-worker activation wait/identity verification. No corpus, Search, provenance, personal-state, backup/import, native-selection or service-worker activation semantic mutation."
v["overall_release_status"]="V120_B9_CONVERGED_ACTIVATION_CONTRAST_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED"
v["real_device_status"]="V120_B9_CANDIDATE__FRESH_NONPHYSICAL_REQUALIFICATION_REQUIRED__REAL_DEVICE_GATES_OPEN"
v["security_inline_script_sha256_base64"]=[x.strip("'").removeprefix("sha256-") for x in script_tokens]
v["security_inline_style_sha256_base64"]=[x.strip("'").removeprefix("sha256-") for x in style_tokens]
v["security_stage_status"]=f"CSP3_EXACT_B9_INLINE_SCRIPT_STYLE_BINDINGS__SERVICE_WORKER_CANONICAL_SHELL_HASH_BOUND_TO_{shell_sha.upper()}"
v["converged_b9_2026_10_03"]={
 "predecessor_contrast_branch":{"candidate":"v120/B7","tree":"ffa6ae0129a39d9802fce6ec5b5b1967da1efc5f","release_sequence":120000007},
 "predecessor_activation_branch":{"candidate":"v120/B8","tree":"3e5f03b4ff1c6d6ff36e8396d67193558ad7319c","release_sequence":120000008},
 "finding":"B8 repaired update activation but forked from B6 and omitted B7 transient dark-mode contrast closure.",
 "repair":"Converge on B8 and add the exact B7 dark/system-dark integrity-button transition:none closure; mechanically rebind B9 release identity, CSP, cache and canonical-shell hashes.",
 "mutation_boundary":["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],
 "protected_surfaces":["corpus","Search","provenance","personal-state schema","backup/import","native-selection","service-worker activation semantics"],
 "production_deployment_authority":"NONE","physical_gate":"OPEN"}
(DST/"version.json").write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
assert (DST/"index.html").read_bytes()==(DST/"luisa_24_heures.html").read_bytes()
assert shell_sha==hashlib.sha256((DST/"index.html").read_bytes()).hexdigest()
assert shell_sha in (DST/"sw.js").read_text(encoding="utf-8")
evidence={"candidate":"v120/B9","release_id":RID,"release_sequence":SEQ,
 "source_b7_tree":"ffa6ae0129a39d9802fce6ec5b5b1967da1efc5f","source_b8_tree":"3e5f03b4ff1c6d6ff36e8396d67193558ad7319c",
 "canonical_shell_sha256":shell_sha,
 "script_sha256_base64":[x.strip("'").removeprefix("sha256-") for x in script_tokens],
 "style_sha256_base64":[x.strip("'").removeprefix("sha256-") for x in style_tokens],
 "changed_files_expected":["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],
 "production_deployment_authority":"NONE","physical_gate":"OPEN"}
pathlib.Path("24h-v120-b9-build-evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
print(json.dumps(evidence,indent=2))
