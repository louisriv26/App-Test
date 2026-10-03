from pathlib import Path
import shutil, re, hashlib, json, base64

SRC=Path("24h-v120-b4-darkmode")
DST=Path("24h-v120-b5-darkmode")
if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC,DST)

html=(SRC/"luisa_24_heures.html").read_text(encoding="utf-8")
m=re.search(r"<script>([\s\S]*?)</script>",html,re.I)
assert m and len(re.findall(r"<script\b",html,re.I))==1
script=m.group(1)

expected={
"const APP_VERSION = 'v120';":"const APP_VERSION = 'v120';",
"const BUILD_REVISION = 'B1';":"const BUILD_REVISION = 'B5';",
"const APP_EVIDENCE_STAGE = '24H_V120_DARK_MODE_CLOSURE_B4';":"const APP_EVIDENCE_STAGE = '24H_V120_DARK_MODE_CLOSURE_B5_CSP_RUNTIME_REPAIR';",
"const APP_RELEASE_SEQUENCE = 120000001;":"const APP_RELEASE_SEQUENCE = 120000005;",
"const APP_RELEASE_ID = '24h-v120-b4-20261002-dark-mode-closure';":"const APP_RELEASE_ID = '24h-v120-b5-20261003-dark-mode-csp-runtime-repair';",
}
for old,new in expected.items():
    if old==new:
        assert script.count(old)==1
        continue
    assert script.count(old)==1, (old,script.count(old))
    script=script.replace(old,new,1)

new_script_b64=base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode("ascii")
new_html=html[:m.start(1)]+script+html[m.end(1):]
old_hash="sha256-rBwKg0I45rOGuTWMvEdSHB31NGf8+230HVNdAbNFK48="
assert new_html.count(old_hash)==1
new_html=new_html.replace(old_hash,"sha256-"+new_script_b64,1)

sm=re.search(r'<style id="dark-mode-contrast-closure-v120">([\s\S]*?)</style>',new_html,re.I)
assert sm
style_b64=base64.b64encode(hashlib.sha256(sm.group(1).encode("utf-8")).digest()).decode("ascii")
assert ("sha256-"+style_b64) in new_html

for name in ["index.html","luisa_24_heures.html"]:
    (DST/name).write_text(new_html,encoding="utf-8",newline="")

shell_sha=hashlib.sha256((DST/"luisa_24_heures.html").read_bytes()).hexdigest()

manifest=json.loads((DST/"manifest.json").read_text(encoding="utf-8"))
manifest["version"]="v120"
manifest["build_revision"]="B5"
manifest["release_sequence"]=120000005
manifest["release_id"]="24h-v120-b5-20261003-dark-mode-csp-runtime-repair"
manifest["build"]="B5"
(DST/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

sw=(DST/"sw.js").read_text(encoding="utf-8")
old_comment="/* v119 B1 — adversarial pre-physical correction successor from exact v118/B1: F-03 focus visibility, complete F-07 tab/tabpanel relationships, comprehensive F-30 forced-colors button boundaries, and active release-metadata reconciliation. Protected corpus/Search/provenance/personal-state/backup semantics unchanged. */"
new_comment="/* v120 B5 — bounded CSP/runtime identity repair successor from exact frozen v120/B4. Dark-mode CSS/content semantics unchanged; protected corpus/Search/provenance/personal-state/backup semantics unchanged. */"
assert sw.count(old_comment)==1
sw=sw.replace(old_comment,new_comment,1)
repls={
"const BUILD_REVISION = 'B1';":"const BUILD_REVISION = 'B5';",
"const RELEASE_SEQUENCE = 120000001;":"const RELEASE_SEQUENCE = 120000005;",
"const RELEASE_ID = '24h-v120-b4-20261002-dark-mode-closure';":"const RELEASE_ID = '24h-v120-b5-20261003-dark-mode-csp-runtime-repair';",
"const CACHE_NAME = \`\${CACHE_PREFIX}v120-b4\`;":"const CACHE_NAME = \`\${CACHE_PREFIX}v120-b5\`;",
}
for old,new in repls.items():
    assert sw.count(old)==1,(old,sw.count(old))
    sw=sw.replace(old,new,1)
sw,n=re.subn(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell_sha}';",sw,count=1)
assert n==1
(DST/"sw.js").write_text(sw,encoding="utf-8",newline="")

version=json.loads((DST/"version.json").read_text(encoding="utf-8"))
version["app_version"]="v120"
version["build_date"]="2026-10-03"
version["cache_name"]="scope-derived:luisa-24h-<scope-fingerprint>-v120-b5"
version["release_scope"]="v120/B5 bounded CSP/runtime identity repair successor from exact frozen v120/B4; restores execution of the already-bounded dark-mode closure and reconciles candidate identity. No corpus/search/provenance/personal-state/backup semantics changed."
version["real_device_status"]="V120_B5_CANDIDATE__BLIND_REQUALIFICATION_REQUIRED__REAL_DEVICE_GATES_OPEN"
version["overall_release_status"]="V120_B5_CSP_RUNTIME_REPAIR_CANDIDATE__PRODUCTION_NOT_AUTHORIZED"
version["build_revision"]="B5"
version["release_sequence"]=120000005
version["release_id"]="24h-v120-b5-20261003-dark-mode-csp-runtime-repair"
version["canonical_shell_sha256"]=shell_sha
version["blind_adversarial_runtime_repair_2026_10_03"]={
    "predecessor_candidate":"v120/B4",
    "predecessor_tree_sha":"fa26ec9bf92f9d5ff8551113ad43d26fda45168e",
    "finding":"B4 inline application script SHA-256 changed but script-src-elem still authorized the v119 script hash, causing the browser to block all application JavaScript.",
    "observed_b4_script_sha256_base64":"MUpFKtmdtzdG8ydjkE1ii9t1AfTBNUuHRaduKlo8xzU=",
    "repair":"Update runtime identity to B5, recompute and bind exact inline script CSP hash, reconcile manifest/service-worker/version identity and canonical-shell hash.",
    "mutation_boundary":["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],
    "production_deployment_authority":"NONE",
    "physical_gate":"OPEN"
}
(DST/"version.json").write_text(json.dumps(version,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

html2=(DST/"luisa_24_heures.html").read_text(encoding="utf-8")
m2=re.search(r"<script>([\s\S]*?)</script>",html2,re.I)
script2=m2.group(1)
h2=base64.b64encode(hashlib.sha256(script2.encode("utf-8")).digest()).decode("ascii")
csp=(re.search(r'Content-Security-Policy" content="([^"]+)"',html2) or [None,""])[1]
assert ("'sha256-"+h2+"'") in csp
assert hashlib.sha256((DST/"index.html").read_bytes()).hexdigest()==shell_sha
assert json.loads((DST/"manifest.json").read_text(encoding="utf-8"))["build_revision"]=="B5"
assert "v120-b5" in (DST/"sw.js").read_text(encoding="utf-8")

changed=[]
for p in sorted(x for x in DST.rglob("*") if x.is_file()):
    rel=p.relative_to(DST)
    q=SRC/rel
    if not q.exists() or hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(q.read_bytes()).digest():
        changed.append(str(rel))
assert changed==["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],changed

evidence={
 "candidate":"v120/B5",
 "predecessor":"v120/B4",
 "changed_files":changed,
 "script_sha256_base64":h2,
 "canonical_shell_sha256":shell_sha,
 "style_sha256_base64":style_b64,
 "csp_script_authorized":True,
 "production_deployment_authority":"NONE",
 "physical_gate":"OPEN"
}
Path("24h-v120-b5-build-evidence.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
print(json.dumps(evidence,indent=2))
