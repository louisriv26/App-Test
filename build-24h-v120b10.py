#!/usr/bin/env python3
import base64, hashlib, json, pathlib, re, shutil

SRC=pathlib.Path("24h-v120-b8-update-activation-closure")
DST=pathlib.Path("24h-v120-b10-predecessor-compatible-closure")
RID="24h-v120-b10-20261003-predecessor-compatible-activation-closure"
SEQ=120000010
if DST.exists(): shutil.rmtree(DST)
shutil.copytree(SRC,DST)

def sha_b64(text):
    return base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode("ascii")

html=(DST/"index.html").read_text(encoding="utf-8")
assert "const BUILD_REVISION = 'B8';" in html
assert "const APP_RELEASE_SEQUENCE = 120000008;" in html
assert "24h-v120-b8-20261003-update-activation-closure" in html
assert "const activated=await waitForWorkerState(prepared.worker,['activated'],15000);" in html
assert "target_worker_identity_mismatch_after_activation" in html

# Converge the B7 transient dark-mode contrast closure that B8 omitted.
closure=r'''
/* B10 convergence closure: retain B7 atomic transient contrast while preserving
   all devotional/content and personal-state surfaces byte-for-byte. */
html[data-theme="dark"] .integrity-btn { transition:none !important; }
@media (prefers-color-scheme: dark){
  html:not([data-theme="light"]) .integrity-btn { transition:none !important; }
}
'''
assert 'html[data-theme="dark"] .integrity-btn { transition:none !important; }' not in html
marker="</style>\n</head>"; pos=html.rfind(marker); assert pos>0
html=html[:pos]+closure+html[pos:]

html=html.replace("const BUILD_REVISION = 'B8';","const BUILD_REVISION = 'B10';",1)
html=html.replace("const APP_EVIDENCE_STAGE = '24H_V120_UPDATE_ACTIVATION_CLOSURE_B8';","const APP_EVIDENCE_STAGE = '24H_V120_PREDECESSOR_COMPATIBLE_ACTIVATION_CLOSURE_B10';",1)
html=html.replace("const APP_RELEASE_SEQUENCE = 120000008;","const APP_RELEASE_SEQUENCE = 120000010;",1)
html=html.replace("const APP_RELEASE_ID = '24h-v120-b8-20261003-update-activation-closure';",f"const APP_RELEASE_ID = '{RID}';",1)

scripts=re.findall(r'<script(?![^>]*\\bsrc=)[^>]*>([\\s\\S]*?)</script>',html,re.I)
styles=re.findall(r'<style[^>]*>([\\s\\S]*?)</style>',html,re.I)
assert scripts and styles
script_tokens=[f"'sha256-{sha_b64(x)}'" for x in scripts]
style_tokens=[f"'sha256-{sha_b64(x)}'" for x in styles]
m=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(")',html,re.I); assert m
csp=m.group(2)
csp,n1=re.subn(r"script-src-elem\\s+[^;]*;", "script-src-elem "+" ".join(script_tokens)+";", csp, count=1)
csp,n2=re.subn(r"style-src-elem\\s+[^;]*;", "style-src-elem "+" ".join(style_tokens)+";", csp, count=1)
assert n1==1 and n2==1
html=html[:m.start(2)]+csp+html[m.end(2):]
for t in script_tokens+style_tokens: assert t in csp
(DST/"index.html").write_text(html,encoding="utf-8")
(DST/"luisa_24_heures.html").write_text(html,encoding="utf-8")
shell_sha=hashlib.sha256(html.encode("utf-8")).hexdigest()

manifest=json.loads((DST/"manifest.json").read_text(encoding="utf-8"))
manifest.update({"version":"v120","build_revision":"B10","release_sequence":SEQ,"release_id":RID,"build":"B10"})
(DST/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

sw=(DST/"sw.js").read_text(encoding="utf-8")
for a,b in [
 ("/* v120 B8 — bounded update-activation successor from failed B6; page orchestration repaired, protected content and service-worker semantics otherwise unchanged. */",
  "/* v120 B10 — predecessor-compatible activation successor: defer ACTIVATE_UPDATE_V2 acknowledgement until activate/claim completes; retains B7 contrast closure in shell. */"),
 ("const BUILD_REVISION = 'B8';","const BUILD_REVISION = 'B10';"),
 ("const RELEASE_SEQUENCE = 120000008;","const RELEASE_SEQUENCE = 120000010;"),
 ("const RELEASE_ID = '24h-v120-b8-20261003-update-activation-closure';",f"const RELEASE_ID = '{RID}';"),
 ("`" + "${CACHE_PREFIX}" + "v120-b8`","`" + "${CACHE_PREFIX}" + "v120-b10`")
]:
    assert a in sw,a
    sw=sw.replace(a,b,1)

old_activate="""self.addEventListener('activate', event => {
  // Automatic/first activation still does not seize existing clients. After a verified explicit
  // ACTIVATE_UPDATE_V2 request, claim same-scope clients so the requesting installed PWA can load
  // the successor shell instead of being served the predecessor cache again on Apple platforms.
  event.waitUntil((async()=>{
    const armed=await readExplicitCommitClaim();
    if (!armed) return;
    const ok=String(armed.release_id||'')===RELEASE_ID && Number(armed.release_sequence)===RELEASE_SEQUENCE && !!armed.request_id;
    if (!ok) { await clearExplicitCommitClaim(); throw new Error('explicit_commit_claim_identity_mismatch'); }
    await self.clients.claim();
    await clearExplicitCommitClaim();
  })());
});"""
new_activate="""let pendingExplicitActivationReply = null;
self.addEventListener('activate', event => {
  // A predecessor page (not the successor shell) orchestrates an installed-PWA update.
  // Reply ACTIVATE_UPDATE_ACCEPTED_V2 only after this exact successor has entered activate,
  // claimed the requester, and completed the explicit-claim checks. This avoids the v119
  // predecessor's active-worker polling from racing/starving the successor transition.
  event.waitUntil((async()=>{
    const armed=await readExplicitCommitClaim();
    if (!armed) return;
    const pending=pendingExplicitActivationReply;
    const ok=String(armed.release_id||'')===RELEASE_ID && Number(armed.release_sequence)===RELEASE_SEQUENCE && !!armed.request_id;
    if (!ok) {
      await clearExplicitCommitClaim();
      pendingExplicitActivationReply=null;
      if (pending && pending.port) {
        try { pending.port.postMessage({type:'ACTIVATE_UPDATE_REJECTED_V2',request_id:pending.request_id||null,release_id:RELEASE_ID,reason:'explicit_commit_claim_identity_mismatch'}); pending.port.close(); } catch(_e) {}
      }
      throw new Error('explicit_commit_claim_identity_mismatch');
    }
    await self.clients.claim();
    await clearExplicitCommitClaim();
    pendingExplicitActivationReply=null;
    if (pending && pending.port && String(pending.request_id||'')===String(armed.request_id||'')) {
      try {
        pending.port.postMessage({type:'ACTIVATE_UPDATE_ACCEPTED_V2',request_id:armed.request_id,release_id:RELEASE_ID,release_sequence:RELEASE_SEQUENCE});
        pending.port.close();
      } catch(_e) {}
    }
  })());
});"""
assert old_activate in sw
sw=sw.replace(old_activate,new_activate,1)

old_message="""  if (data.type==='ACTIVATE_UPDATE_V2') {
    const ok=String(data.expected_release_id||'')===RELEASE_ID && Number(data.expected_release_sequence)===RELEASE_SEQUENCE && !!data.request_id;
    if (!ok) { reply(event,{type:'ACTIVATE_UPDATE_REJECTED_V2',request_id:data.request_id||null,release_id:RELEASE_ID,reason:'release_identity_mismatch'}); return; }
    event.waitUntil((async()=>{
      // R33 changes the canonical personal-state authority from localStorage to IndexedDB.
      // Never cross that migration boundary while another predecessor window is live:
      // R32 cannot participate in the new canonical store and a mixed R32/R33 writer set
      // could otherwise acknowledge changes into different authorities. Fail closed and
      // leave every current page untouched; the user can close the other window and retry.
      const isolation=await explicitUpdateHasNoOtherLiveScopeClient(event);
      if (!isolation.ok) {
        reply(event,{type:'ACTIVATE_UPDATE_REJECTED_V2',request_id:data.request_id,release_id:RELEASE_ID,reason:isolation.reason,other_scope_clients:isolation.otherCount||0});
        return;
      }
      await armExplicitCommitClaim(data.request_id);
      reply(event,{type:'ACTIVATE_UPDATE_ACCEPTED_V2',request_id:data.request_id,release_id:RELEASE_ID,release_sequence:RELEASE_SEQUENCE});
      await self.skipWaiting();
    })());
    return;
  }"""
new_message="""  if (data.type==='ACTIVATE_UPDATE_V2') {
    const ok=String(data.expected_release_id||'')===RELEASE_ID && Number(data.expected_release_sequence)===RELEASE_SEQUENCE && !!data.request_id;
    if (!ok) { reply(event,{type:'ACTIVATE_UPDATE_REJECTED_V2',request_id:data.request_id||null,release_id:RELEASE_ID,reason:'release_identity_mismatch'}); return; }
    event.waitUntil((async()=>{
      const isolation=await explicitUpdateHasNoOtherLiveScopeClient(event);
      if (!isolation.ok) {
        reply(event,{type:'ACTIVATE_UPDATE_REJECTED_V2',request_id:data.request_id,release_id:RELEASE_ID,reason:isolation.reason,other_scope_clients:isolation.otherCount||0});
        return;
      }
      if (!event.ports || !event.ports[0]) {
        reply(event,{type:'ACTIVATE_UPDATE_REJECTED_V2',request_id:data.request_id,release_id:RELEASE_ID,reason:'reply_port_missing'});
        return;
      }
      if (pendingExplicitActivationReply) {
        reply(event,{type:'ACTIVATE_UPDATE_REJECTED_V2',request_id:data.request_id,release_id:RELEASE_ID,reason:'activation_already_pending'});
        return;
      }
      await armExplicitCommitClaim(data.request_id);
      pendingExplicitActivationReply={port:event.ports[0],request_id:String(data.request_id)};
      try {
        await self.skipWaiting();
      } catch(error) {
        const pending=pendingExplicitActivationReply;
        pendingExplicitActivationReply=null;
        await clearExplicitCommitClaim();
        if (pending && pending.port) {
          try { pending.port.postMessage({type:'ACTIVATE_UPDATE_REJECTED_V2',request_id:data.request_id,release_id:RELEASE_ID,reason:'skip_waiting_failed'}); pending.port.close(); } catch(_e) {}
        }
      }
    })());
    return;
  }"""
assert old_message in sw
sw=sw.replace(old_message,new_message,1)
sw,n=re.subn(r"const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';",f"const CANONICAL_SHELL_SHA256 = '{shell_sha}';",sw,count=1); assert n==1
(DST/"sw.js").write_text(sw,encoding="utf-8")

v=json.loads((DST/"version.json").read_text(encoding="utf-8"))
v["build_revision"]="B10"; v["release_sequence"]=SEQ; v["release_id"]=RID
v["cache_name"]="scope-derived:luisa-24h-<scope-fingerprint>-v120-b10"; v["canonical_shell_sha256"]=shell_sha
v["release_scope"]="v120/B10 predecessor-compatible convergence successor. Starts from exact B8, restores the bounded B7 atomic dark/system-dark integrity-button transition closure, and changes only the successor service-worker ACTIVATE_UPDATE_V2 acknowledgement timing so an installed v119 predecessor receives acceptance after successor activate/claim rather than before. No corpus, Search, provenance, personal-state schema, backup/import, native-selection or devotional-content mutation."
v["overall_release_status"]="V120_B10_PREDECESSOR_COMPATIBLE_ACTIVATION_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED"
v["real_device_status"]="V120_B10_CANDIDATE__FRESH_NONPHYSICAL_REQUALIFICATION_REQUIRED__REAL_DEVICE_GATES_OPEN"
v["security_inline_script_sha256_base64"]=[x.strip("'").removeprefix("sha256-") for x in script_tokens]
v["security_inline_style_sha256_base64"]=[x.strip("'").removeprefix("sha256-") for x in style_tokens]
v["security_stage_status"]=f"CSP3_EXACT_B10_INLINE_SCRIPT_STYLE_BINDINGS__SERVICE_WORKER_CANONICAL_SHELL_HASH_BOUND_TO_{shell_sha.upper()}"
v["full_qa_20261003_b10"]={
 "predecessor_authority":{"candidate":"v120/B8","tree":"3e5f03b4ff1c6d6ff36e8396d67193558ad7319c","release_sequence":120000008},
 "superseded_attempt":{"candidate":"v120/B9","release_sequence":120000009,"status":"NOT_FROZEN__UPDATE_GATE_FAILED"},
 "finding":"B8/B9 attempted to repair v119→successor activation in successor page code, but the already-loaded v119 predecessor page remains the update orchestrator and cannot be repaired by successor-page bytes.",
 "root_cause":"The v119 predecessor receives ACTIVATE_UPDATE_ACCEPTED_V2 before successor activate/claim completes, then enters active-worker polling. The exact-worker event wait proved activation can complete when predecessor polling is not started prematurely.",
 "repair":"Successor service worker retains the MessagePort and sends ACTIVATE_UPDATE_ACCEPTED_V2 from its activate event only after explicit claim verification and clients.claim(); two-client isolation rejections remain immediate and fail closed.",
 "contrast_convergence":"Exact B7 dark/system-dark integrity-button transition:none closure retained.",
 "mutation_boundary":["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],
 "protected_surfaces":["corpus","Search","provenance","personal-state schema/semantics","backup/import","native-selection","devotional content"],
 "production_deployment_authority":"NONE","physical_gate":"OPEN"
}
(DST/"version.json").write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

assert (DST/"index.html").read_bytes()==(DST/"luisa_24_heures.html").read_bytes()
assert shell_sha==hashlib.sha256((DST/"index.html").read_bytes()).hexdigest()
assert shell_sha in (DST/"sw.js").read_text(encoding="utf-8")
evidence={"candidate":"v120/B10","release_id":RID,"release_sequence":SEQ,
 "source_b7_tree":"ffa6ae0129a39d9802fce6ec5b5b1967da1efc5f","source_b8_tree":"3e5f03b4ff1c6d6ff36e8396d67193558ad7319c",
 "canonical_shell_sha256":shell_sha,
 "script_sha256_base64":[x.strip("'").removeprefix("sha256-") for x in script_tokens],
 "style_sha256_base64":[x.strip("'").removeprefix("sha256-") for x in style_tokens],
 "changed_files_expected":["index.html","luisa_24_heures.html","manifest.json","sw.js","version.json"],
 "activation_repair":"DEFER_ACCEPT_ACK_TO_SUCCESSOR_ACTIVATE_AFTER_CLIENTS_CLAIM",
 "production_deployment_authority":"NONE","physical_gate":"OPEN"}
pathlib.Path("24h-v120-b10-build-evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
print(json.dumps(evidence,indent=2))
