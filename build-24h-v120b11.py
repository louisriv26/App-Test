#!/usr/bin/env python3
import base64, hashlib, json, pathlib, re, shutil

SRC=pathlib.Path("24h-v120-b10-predecessor-compatible-closure")
DST=pathlib.Path("24h-v120-b11-state-reconciliation-closure")
RID="24h-v120-b11-20261003-state-reconciliation-closure"
SEQ=120000011

if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC,DST)

def sha_b64(text):
    return base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode("ascii")

# Shell: identity-only successor. No functional/style/content mutation.
html=(DST/"index.html").read_text(encoding="utf-8")
assert "const BUILD_REVISION = 'B10';" in html
assert "const APP_RELEASE_SEQUENCE = 120000010;" in html
assert "24h-v120-b10-20261003-predecessor-compatible-activation-closure" in html
assert 'html[data-theme="dark"] .integrity-btn { transition:none !important; }' in html
assert "pendingExplicitActivationReply" not in html  # worker-only B10 protocol

html=html.replace("const BUILD_REVISION = 'B10';","const BUILD_REVISION = 'B11';",1)
html=html.replace("const APP_EVIDENCE_STAGE = '24H_V120_PREDECESSOR_COMPATIBLE_ACTIVATION_CLOSURE_B10';",
                  "const APP_EVIDENCE_STAGE = '24H_V120_STATE_RECONCILIATION_CLOSURE_B11';",1)
html=html.replace("const APP_RELEASE_SEQUENCE = 120000010;","const APP_RELEASE_SEQUENCE = 120000011;",1)
html=html.replace("const APP_RELEASE_ID = '24h-v120-b10-20261003-predecessor-compatible-activation-closure';",
                  f"const APP_RELEASE_ID = '{RID}';",1)

scripts=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>',html,re.I)
styles=re.findall(r'<style[^>]*>([\s\S]*?)</style>',html,re.I)
assert scripts and styles
script_tokens=[f"'sha256-{sha_b64(x)}'" for x in scripts]
style_tokens=[f"'sha256-{sha_b64(x)}'" for x in styles]
m=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(")',html,re.I)
assert m
csp=m.group(2)
csp,n1=re.subn(r"script-src-elem\s+[^;]*;", "script-src-elem "+" ".join(script_tokens)+";", csp, count=1)
csp,n2=re.subn(r"style-src-elem\s+[^;]*;", "style-src-elem "+" ".join(style_tokens)+";", csp, count=1)
assert n1==1 and n2==1
html=html[:m.start(2)]+csp+html[m.end(2):]
for token in script_tokens+style_tokens:
    assert token in csp

(DST/"index.html").write_text(html,encoding="utf-8")
(DST/"luisa_24_heures.html").write_text(html,encoding="utf-8")
shell_sha=hashlib.sha256(html.encode("utf-8")).hexdigest()

# Manifest identity.
manifest=json.loads((DST/"manifest.json").read_text(encoding="utf-8"))
manifest.update({"version":"v120","build_revision":"B11","release_sequence":SEQ,"release_id":RID,"build":"B11"})
(DST/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

# Service worker: identity/cache/hash only; B10 activation semantics must remain byte-equivalent after normalization.
sw=(DST/"sw.js").read_text(encoding="utf-8")
assert "pendingExplicitActivationReply" in sw
for a,b in [
    ("/* v120 B10 — predecessor-compatible activation successor: defer ACTIVATE_UPDATE_V2 acknowledgement until activate/claim completes; retains B7 contrast closure in shell. */",
     "/* v120 B11 — state/release-metadata reconciliation successor; B10 activation and B7 contrast semantics preserved unchanged. */"),
    ("const BUILD_REVISION = 'B10';","const BUILD_REVISION = 'B11';"),
    ("const RELEASE_SEQUENCE = 120000010;","const RELEASE_SEQUENCE = 120000011;"),
    ("const RELEASE_ID = '24h-v120-b10-20261003-predecessor-compatible-activation-closure';",f"const RELEASE_ID = '{RID}';"),
    ("v120-b10","v120-b11")
]:
    assert a in sw, a
    sw=sw.replace(a,b,1)
sw,n=re.subn(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",
             f"const CANONICAL_SHELL_SHA256 = '{shell_sha}';",sw,count=1)
assert n==1
(DST/"sw.js").write_text(sw,encoding="utf-8")

# Version/release metadata reconciliation.
v=json.loads((DST/"version.json").read_text(encoding="utf-8"))
v["build_revision"]="B11"
v["release_sequence"]=SEQ
v["release_id"]=RID
v["cache_name"]="scope-derived:luisa-24h-<scope-fingerprint>-v120-b11"
v["canonical_shell_sha256"]=shell_sha
v["release_scope"]="v120/B11 metadata/state reconciliation successor to exact frozen v120/B10. Runtime activation protocol and B7 dark/system-dark atomic contrast closure are preserved; the only semantic correction is removal of stale B8 current-candidate references from governing release metadata. No corpus, Search, provenance, personal-state schema/semantics, backup/import, native-selection or devotional-content mutation."
v["real_device_status"]="V120_B11_CANDIDATE__REAL_DEVICE_GATES_OPEN"
v["overall_release_status"]="V120_B11_STATE_RECONCILIATION_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED"
for key in ("known_blockers","external_open_gates"):
    v[key]=[str(x).replace("v120/B8","v120/B11") for x in v.get(key,[])]
v["functional_freeze_status"]="V120_B11_B10_RUNTIME_SEMANTICS_PRESERVED__B7_TRANSIENT_CONTRAST_CLOSURE_PRESERVED__PROTECTED_CONTENT_AND_NON_UPDATE_SURFACES_UNCHANGED__PHYSICAL_GATES_OPEN"
v["security_inline_script_sha256_base64"]=[x.strip("'").removeprefix("sha256-") for x in script_tokens]
v["security_inline_style_sha256_base64"]=[x.strip("'").removeprefix("sha256-") for x in style_tokens]
v["security_stage_status"]=f"CSP3_EXACT_B11_INLINE_SCRIPT_STYLE_BINDINGS__SERVICE_WORKER_CANONICAL_SHELL_HASH_BOUND_TO_{shell_sha.upper()}"
if isinstance(v.get("full_qa_20261003_update_activation_repair"),dict):
    v["full_qa_20261003_update_activation_repair"]["status"]="HISTORICAL_B6_TO_B8_STAGE__SUPERSEDED_BY_B10_AND_B11"
v["full_qa_20261003_b11"]={
    "predecessor_authority":{"candidate":"v120/B10","tree":"2a12ff7881832645adfa41ebddd5772f3a5c406a","release_sequence":120000010,
                             "zip_sha256":"42937d636f0c44a78e9969bb8410fd374784e6ef6b3d937270ccd4ed81e6adc9"},
    "finding":"Pass-3 reconciliation found current-candidate release metadata in frozen B10 still named B8 in known_blockers/external_open_gates and functional_freeze_status after the lineage had advanced to B10.",
    "classification":"RELEASE_EVIDENCE_AND_STATE_STALENESS__NO_RUNTIME_DEFECT",
    "repair":"Create immutable B11 from exact B10; preserve B10 runtime/content semantics, rebind identity/CSP/cache/canonical shell, and replace only current-status B8 references with B11 while retaining clearly historical B8 lineage evidence.",
    "mutation_boundary":["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],
    "protected_surfaces":["corpus","Search","provenance","personal-state schema/semantics","backup/import","native-selection","devotional content","B10 activation semantics","B7 transient contrast semantics"],
    "production_deployment_authority":"NONE",
    "physical_gate":"OPEN"
}
(DST/"version.json").write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

# Build invariants.
assert (DST/"index.html").read_bytes()==(DST/"luisa_24_heures.html").read_bytes()
assert shell_sha==hashlib.sha256((DST/"index.html").read_bytes()).hexdigest()
assert shell_sha in (DST/"sw.js").read_text(encoding="utf-8")
assert all("v120/B11" in x or "v120/B8" not in x for x in v["known_blockers"])
assert all("v120/B11" in x or "v120/B8" not in x for x in v["external_open_gates"])
assert "V120_B8" not in v["functional_freeze_status"]

evidence={
    "candidate":"v120/B11","release_id":RID,"release_sequence":SEQ,
    "source_b10_tree":"2a12ff7881832645adfa41ebddd5772f3a5c406a",
    "source_b10_zip_sha256":"42937d636f0c44a78e9969bb8410fd374784e6ef6b3d937270ccd4ed81e6adc9",
    "canonical_shell_sha256":shell_sha,
    "script_sha256_base64":[x.strip("'").removeprefix("sha256-") for x in script_tokens],
    "style_sha256_base64":[x.strip("'").removeprefix("sha256-") for x in style_tokens],
    "changed_files_expected":["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],
    "functional_change":"NONE__IDENTITY_AND_CURRENT_STATE_METADATA_RECONCILIATION_ONLY",
    "production_deployment_authority":"NONE","physical_gate":"OPEN"
}
pathlib.Path("24h-v120-b11-build-evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
print(json.dumps(evidence,indent=2))
