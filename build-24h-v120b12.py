#!/usr/bin/env python3
import base64, hashlib, json, pathlib, re, shutil

SRC=pathlib.Path("24h-v120-b10-predecessor-compatible-closure")
DST=pathlib.Path("24h-v120-b12-release-reconciliation-contrast-closure")
RID="24h-v120-b12-20261003-release-reconciliation-update-banner-closure"
SEQ=120000012

if DST.exists(): shutil.rmtree(DST)
shutil.copytree(SRC,DST)

def sha_b64(text):
    return base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode("ascii")

html=(DST/"index.html").read_text(encoding="utf-8")
assert "const BUILD_REVISION = 'B10';" in html
assert "const APP_RELEASE_SEQUENCE = 120000010;" in html
assert "24h-v120-b10-20261003-predecessor-compatible-activation-closure" in html
assert 'html[data-theme="dark"] .integrity-btn { transition:none !important; }' in html

# Bounded B12 UI correction: update banner controls use the existing semantic
# on-accent token and meet the important-control 44px touch floor.
old_refresh=""".update-refresh-btn { flex-shrink: 0; padding: 0.4rem 0.8rem;
  background: rgba(255,255,255,0.25); border: 1px solid rgba(255,255,255,0.4);
  color: #fff; border-radius: 8px; font-family: var(--font-ui); font-size: 0.82rem;
  cursor: pointer; white-space: nowrap; }"""
new_refresh=""".update-refresh-btn { flex-shrink: 0; min-height: 44px; padding: 0.4rem 0.8rem;
  background: rgba(255,255,255,0.25); border: 1px solid rgba(255,255,255,0.4);
  color: var(--on-accent); border-radius: 8px; font-family: var(--font-ui); font-size: 0.82rem;
  cursor: pointer; white-space: nowrap; }"""
old_dismiss=""".update-dismiss-btn { flex-shrink: 0; background: none; border: none; color: rgba(255,255,255,0.7);
  font-size: 1.1rem; cursor: pointer; padding: 2px 4px; line-height: 1; }"""
new_dismiss=""".update-dismiss-btn { flex-shrink: 0; min-width: 44px; min-height: 44px; background: none; border: none; color: var(--on-accent);
  font-size: 1.1rem; cursor: pointer; padding: 2px 4px; line-height: 1; }"""
assert html.count(old_refresh)==1
assert html.count(old_dismiss)==1
html=html.replace(old_refresh,new_refresh,1).replace(old_dismiss,new_dismiss,1)

# New immutable identity.
html=html.replace("const BUILD_REVISION = 'B10';","const BUILD_REVISION = 'B12';",1)
html=html.replace("const APP_EVIDENCE_STAGE = '24H_V120_PREDECESSOR_COMPATIBLE_ACTIVATION_CLOSURE_B10';",
                  "const APP_EVIDENCE_STAGE = '24H_V120_RELEASE_RECONCILIATION_UPDATE_BANNER_CLOSURE_B12';",1)
html=html.replace("const APP_RELEASE_SEQUENCE = 120000010;","const APP_RELEASE_SEQUENCE = 120000012;",1)
html=html.replace("const APP_RELEASE_ID = '24h-v120-b10-20261003-predecessor-compatible-activation-closure';",
                  f"const APP_RELEASE_ID = '{RID}';",1)

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
for token in script_tokens+style_tokens: assert token in csp
(DST/"index.html").write_text(html,encoding="utf-8")
(DST/"luisa_24_heures.html").write_text(html,encoding="utf-8")
shell_sha=hashlib.sha256(html.encode("utf-8")).hexdigest()

manifest=json.loads((DST/"manifest.json").read_text(encoding="utf-8"))
manifest.update({"version":"v120","build_revision":"B12","release_sequence":SEQ,"release_id":RID,"build":"B12"})
(DST/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

# Preserve exact B10 activation semantics; only release identity/cache/hash changes.
sw=(DST/"sw.js").read_text(encoding="utf-8")
assert "pendingExplicitActivationReply" in sw
for a,b in [
    ("/* v120 B10 — predecessor-compatible activation successor: defer ACTIVATE_UPDATE_V2 acknowledgement until activate/claim completes; retains B7 contrast closure in shell. */",
     "/* v120 B12 — release/state reconciliation plus update-banner contrast/touch closure; B10 activation semantics preserved unchanged. */"),
    ("const BUILD_REVISION = 'B10';","const BUILD_REVISION = 'B12';"),
    ("const RELEASE_SEQUENCE = 120000010;","const RELEASE_SEQUENCE = 120000012;"),
    ("const RELEASE_ID = '24h-v120-b10-20261003-predecessor-compatible-activation-closure';",f"const RELEASE_ID = '{RID}';"),
    ("v120-b10","v120-b12")
]:
    assert a in sw,a
    sw=sw.replace(a,b,1)
sw,n=re.subn(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",
             f"const CANONICAL_SHELL_SHA256 = '{shell_sha}';",sw,count=1); assert n==1
(DST/"sw.js").write_text(sw,encoding="utf-8")

v=json.loads((DST/"version.json").read_text(encoding="utf-8"))
v["build_revision"]="B12"; v["release_sequence"]=SEQ; v["release_id"]=RID
v["cache_name"]="scope-derived:luisa-24h-<scope-fingerprint>-v120-b12"
v["canonical_shell_sha256"]=shell_sha
v["release_scope"]="v120/B12 successor to exact frozen v120/B10. Corrects stale current-candidate B8 references found by Pass 3 and the dark/system-dark update-banner control contrast/touch-target defect found by the failed unfrozen B11 adversarial run. B10 update activation, B7 integrity-button transient contrast, corpus, Search, provenance, personal-state schema/semantics, backup/import, native-selection and devotional content are preserved."
v["real_device_status"]="V120_B12_CANDIDATE__REAL_DEVICE_GATES_OPEN"
v["overall_release_status"]="V120_B12_RELEASE_RECONCILIATION_UPDATE_BANNER_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED"
for key in ("known_blockers","external_open_gates"):
    v[key]=[str(x).replace("v120/B8","v120/B12") for x in v.get(key,[])]
v["functional_freeze_status"]="V120_B12_B10_UPDATE_ACTIVATION_PRESERVED__B7_TRANSIENT_CONTRAST_PRESERVED__UPDATE_BANNER_CONTRAST_TOUCH_CLOSED__PROTECTED_CONTENT_UNCHANGED__PHYSICAL_GATES_OPEN"
v["security_inline_script_sha256_base64"]=[x.strip("'").removeprefix("sha256-") for x in script_tokens]
v["security_inline_style_sha256_base64"]=[x.strip("'").removeprefix("sha256-") for x in style_tokens]
v["security_stage_status"]=f"CSP3_EXACT_B12_INLINE_SCRIPT_STYLE_BINDINGS__SERVICE_WORKER_CANONICAL_SHELL_HASH_BOUND_TO_{shell_sha.upper()}"
if isinstance(v.get("full_qa_20261003_update_activation_repair"),dict):
    v["full_qa_20261003_update_activation_repair"]["status"]="HISTORICAL_B6_TO_B8_STAGE__SUPERSEDED_BY_B10_AND_B12"
v["full_qa_20261003_b11_failed_attempt"]={
    "candidate":"v120/B11","release_sequence":120000011,"status":"FAILED_UNFROZEN__NEVER_PROMOTED",
    "finding":"The broad adversarial contract rendered the update banner in dark/system-dark and found white/light update controls on the dark-theme gold accent: Actualiser and dismiss controls failed the 4.5:1 text contrast contract; the controls also lacked the governed 44px important-target floor.",
    "disposition":"B11 identity retired without freeze. B12 starts again from exact frozen B10 and incorporates both the release-metadata reconciliation and the bounded update-banner correction."
}
v["full_qa_20261003_b12"]={
    "predecessor_authority":{"candidate":"v120/B10","tree":"2a12ff7881832645adfa41ebddd5772f3a5c406a","release_sequence":120000010,
                             "zip_sha256":"42937d636f0c44a78e9969bb8410fd374784e6ef6b3d937270ccd4ed81e6adc9"},
    "findings":[
        "B24H-FQA-002: frozen B10 current release metadata retained B8 labels in known_blockers/external_open_gates and functional_freeze_status.",
        "B24H-FQA-003: update banner controls hard-coded white/light foregrounds over the dark-theme gold accent, failing the adversarial contrast contract; refresh/dismiss controls were also below the governed 44px important-target floor."
    ],
    "root_causes":[
        "Candidate lineage advanced faster than current-status fields in version.json.",
        "The update banner predated the semantic --on-accent token and retained hard-coded white control colors; its compact controls predated the 44px target requirement."
    ],
    "repair":"Replace current-status B8 labels with B12; bind update controls to var(--on-accent); give refresh min-height 44px and dismiss min-width/min-height 44px; rebind identity/CSP/cache/canonical shell. No update-protocol or content mutation.",
    "mutation_boundary":["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],
    "protected_surfaces":["corpus","Search","provenance","personal-state schema/semantics","backup/import","native-selection","devotional content","B10 activation semantics","B7 integrity-button transient contrast semantics"],
    "production_deployment_authority":"NONE","physical_gate":"OPEN"
}
(DST/"version.json").write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

assert (DST/"index.html").read_bytes()==(DST/"luisa_24_heures.html").read_bytes()
assert shell_sha==hashlib.sha256((DST/"index.html").read_bytes()).hexdigest()
assert shell_sha in (DST/"sw.js").read_text(encoding="utf-8")
assert all("v120/B8" not in x for x in v["known_blockers"])
assert all("v120/B8" not in x for x in v["external_open_gates"])

evidence={
 "candidate":"v120/B12","release_id":RID,"release_sequence":SEQ,
 "source_b10_tree":"2a12ff7881832645adfa41ebddd5772f3a5c406a",
 "source_b10_zip_sha256":"42937d636f0c44a78e9969bb8410fd374784e6ef6b3d937270ccd4ed81e6adc9",
 "canonical_shell_sha256":shell_sha,
 "script_sha256_base64":[x.strip("'").removeprefix("sha256-") for x in script_tokens],
 "style_sha256_base64":[x.strip("'").removeprefix("sha256-") for x in style_tokens],
 "changed_files_expected":["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],
 "functional_change":"BOUNDED_UPDATE_BANNER_CONTRAST_TOUCH_TARGET_PLUS_RELEASE_METADATA_RECONCILIATION",
 "production_deployment_authority":"NONE","physical_gate":"OPEN"
}
pathlib.Path("24h-v120-b12-build-evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
print(json.dumps(evidence,indent=2))
