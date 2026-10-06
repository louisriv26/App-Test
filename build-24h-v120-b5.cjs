const fs=require('fs'),crypto=require('crypto');
const SRC='24h-v120-b4-darkmode';
const DST='24h-v120-b5-blind-adversarial-closure';
const RELEASE_ID='24h-v120-b5-20261003-blind-adversarial-integrity-closure';
const RELEASE_SEQUENCE=120000002;
const APP_VERSION='v120';
const BUILD_REVISION='B5';

function fail(m){throw new Error(m)}
function shaHex(b){return crypto.createHash('sha256').update(b).digest('hex')}
function shaB64(s){return crypto.createHash('sha256').update(s).digest('base64')}
function read(p){return fs.readFileSync(p,'utf8')}
function write(p,s){fs.writeFileSync(p,s)}
function rep1(s,a,b,label){const n=s.split(a).length-1;if(n!==1)fail(label+' expected 1 occurrence, got '+n);return s.replace(a,b)}
function reRep1(s,re,b,label){const flags=re.flags.includes('g')?re.flags:re.flags+'g';const all=[...s.matchAll(new RegExp(re.source,flags))];if(all.length!==1)fail(label+' expected 1 occurrence, got '+all.length);return s.replace(re,b)}

if(!fs.existsSync(SRC))fail('source missing');
if(fs.existsSync(DST))fail('destination already exists; immutable successor must not be overwritten');
fs.cpSync(SRC,DST,{recursive:true});

let html=read(DST+'/index.html');
const oldScript=(html.match(/<script\b[^>]*>([\s\S]*?)<\/script>/i)||[])[1];
if(!oldScript)fail('main inline script missing');
const oldScriptHash='sha256-'+shaB64(oldScript);
const csp=(html.match(/Content-Security-Policy" content="([^"]+)"/)||[])[1]||'';
if(csp.includes("'"+oldScriptHash+"'"))fail('B4 unexpectedly already authorizes its script; precondition changed');
if(!html.includes("const BUILD_REVISION = 'B1';"))fail('B4 BUILD_REVISION precondition missing');
if(!html.includes("const APP_RELEASE_ID = '24h-v120-b4-20261002-dark-mode-closure';"))fail('B4 release id precondition missing');

html=rep1(html,"const BUILD_REVISION = 'B1';","const BUILD_REVISION = 'B5';",'shell revision');
html=rep1(html,"const APP_EVIDENCE_STAGE = '24H_V120_DARK_MODE_CLOSURE_B4';","const APP_EVIDENCE_STAGE = '24H_V120_BLIND_ADVERSARIAL_INTEGRITY_CLOSURE_B5';",'evidence stage');
html=rep1(html,"const APP_RELEASE_SEQUENCE = 120000001;","const APP_RELEASE_SEQUENCE = 120000002;",'release sequence');
html=rep1(html,"const APP_RELEASE_ID = '24h-v120-b4-20261002-dark-mode-closure';","const APP_RELEASE_ID = '"+RELEASE_ID+"';",'release id');

const newScript=(html.match(/<script\b[^>]*>([\s\S]*?)<\/script>/i)||[])[1];
if(!newScript)fail('new main script missing');
const newScriptHash='sha256-'+shaB64(newScript);
const cspScript=(html.match(/script-src-elem ([^;]+);/)||[])[1]||'';
const scriptHashTokens=[...cspScript.matchAll(/'sha256-[^']+'/g)].map(m=>m[0]);
if(scriptHashTokens.length!==1)fail('expected exactly one script-src-elem hash, got '+scriptHashTokens.length);
html=rep1(html,scriptHashTokens[0],"'"+newScriptHash+"'",'CSP script hash');
write(DST+'/index.html',html);
write(DST+'/luisa_24_heures.html',html);

const styles=[...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)].map(m=>m[1]);
const styleHashes=styles.map(s=>'sha256-'+shaB64(s));
const finalCsp=(html.match(/Content-Security-Policy" content="([^"]+)"/)||[])[1]||'';
if(!finalCsp.includes("'"+newScriptHash+"'"))fail('final CSP missing new script hash');
for(const h of styleHashes)if(!finalCsp.includes("'"+h+"'"))fail('final CSP missing style hash '+h);

const shellHash=shaHex(fs.readFileSync(DST+'/index.html'));
if(shaHex(fs.readFileSync(DST+'/luisa_24_heures.html'))!==shellHash)fail('index and canonical shell diverged');

const manifestPath=DST+'/manifest.json';
const manifest=JSON.parse(read(manifestPath));
manifest.version=APP_VERSION;
manifest.build_revision=BUILD_REVISION;
manifest.release_sequence=RELEASE_SEQUENCE;
manifest.release_id=RELEASE_ID;
manifest.build=BUILD_REVISION;
write(manifestPath,JSON.stringify(manifest,null,2)+'\n');

const swPath=DST+'/sw.js';
let sw=read(swPath);
sw=sw.replace(/^\/\*.*?\*\//,"/* v120 B5 — blind adversarial release-integrity closure successor from frozen v120/B4. Repairs CSP/script authorization and exact release identity binding only; dark-mode CSS and protected corpus/search/provenance/personal-state/backup semantics unchanged. */");
sw=rep1(sw,"const BUILD_REVISION = 'B1';","const BUILD_REVISION = 'B5';",'SW revision');
sw=rep1(sw,"const RELEASE_SEQUENCE = 120000001;","const RELEASE_SEQUENCE = 120000002;",'SW release sequence');
sw=rep1(sw,"const RELEASE_ID = '24h-v120-b4-20261002-dark-mode-closure';","const RELEASE_ID = '"+RELEASE_ID+"';",'SW release id');
sw=reRep1(sw,/const CANONICAL_SHELL_SHA256 = '[0-9a-f]{64}';/,"const CANONICAL_SHELL_SHA256 = '"+shellHash+"';",'SW shell hash');
const tick=String.fromCharCode(96), cacheToken='$'+'{CACHE_PREFIX}';
sw=rep1(sw,"const CACHE_NAME = "+tick+cacheToken+"v120-b4"+tick+";","const CACHE_NAME = "+tick+cacheToken+"v120-b5"+tick+";",'SW cache name');
write(swPath,sw);

const versionPath=DST+'/version.json';
const v=JSON.parse(read(versionPath));
v.app_version=APP_VERSION;
v.build_date='2026-10-03';
v.cache_name='scope-derived:luisa-24h-<scope-fingerprint>-v120-b5';
v.release_scope='v120/B5 blind-adversarial release-integrity closure successor from frozen v120/B4; preserves all dark-mode repairs and corrects CSP/script authorization plus exact shell/manifest/service-worker/version identity binding. No corpus/search/provenance/personal-state/backup semantic mutation.';
v.real_device_status='V120_B5_CANDIDATE__BLIND_ADVERSARIAL_RELEASE_INTEGRITY_CLOSURE__REAL_DEVICE_GATES_OPEN';
v.overall_release_status='V120_B5_BLIND_ADVERSARIAL_INTEGRITY_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED';
v.build_revision=BUILD_REVISION;
v.release_sequence=RELEASE_SEQUENCE;
v.release_id=RELEASE_ID;
v.canonical_shell_sha256=shellHash;
v.canonical_shell_inline_script_sha256_csp=newScriptHash;
v.security_inline_script_sha256_base64=newScriptHash;
v.security_inline_style_sha256_base64=styleHashes;
v.functional_freeze_status='V120_B5_PREPHYSICAL_CANDIDATE__DARK_MODE_CLOSURE_PRESERVED__CSP_AND_RELEASE_IDENTITY_REPAIRED__PHYSICAL_GATES_OPEN';
v.security_stage_status='CSP3_ARCHITECTURE_PRESERVED__V120_B5_INLINE_SCRIPT_HASH_BOUND_'+newScriptHash.replace(/[^A-Za-z0-9]/g,'_')+'__ALL_INLINE_STYLE_HASHES_BOUND__SERVICE_WORKER_CANONICAL_SHELL_HASH_BOUND_'+shellHash.toUpperCase();

if(Array.isArray(v.known_blockers)){
  v.known_blockers=v.known_blockers.map((x,i)=>{
    if(i===0)return 'Exact production v119/B1 → v120/B5 installed-PWA update/activation and acknowledged-state preservation on iPhone and iPad.';
    if(i===1)return 'v120/B5 iPad H03/P013 physical A–D replay of the inherited native-selection surface: direct P013 selection; highlight/persistence; P012→P013 regression; selection inside existing cross-record highlight.';
    if(i===2)return 'v120/B5 provenance panels for normal Hours and H08/H23/H24, plus methodology and Help, at Très grand in portrait and landscape.';
    return x;
  });
}
if(Array.isArray(v.external_open_gates)){
  v.external_open_gates=v.external_open_gates.map((x,i)=>{
    if(i===0)return 'Exact production v119/B1 → v120/B5 installed-PWA update/activation and acknowledged-state preservation on iPhone and iPad.';
    if(i===1)return 'v120/B5 iPad H03/P013 physical A–D replay of the inherited native-selection surface: direct P013 selection; highlight/persistence; P012→P013 regression; selection inside existing cross-record highlight.';
    if(i===2)return 'v120/B5 provenance panels for normal Hours and H08/H23/H24, plus methodology and Help, at Très grand in portrait and landscape.';
    return x;
  });
}
v.dark_mode_v120_b5={
  date:'2026-10-03',
  exact_predecessor_tree:'fa26ec9bf92f9d5ff8551113ad43d26fda45168e',
  supersedes:['v120/B1','v120/B2','v120/B3','v120/B4'],
  blind_adversarial_findings:[
    'B4 main inline script SHA-256 was not authorized by script-src-elem CSP, so Chromium blocked the entire application script and the runtime did not initialize.',
    'B4 shell and service worker declared BUILD_REVISION B1 while manifest declared B4; service-worker verifiedInstall would reject manifest_release_identity_mismatch.',
    'B4 version.json current-state fields contained stale B1/v119 physical-gate and security-stage identity wording.'
  ],
  repair:[
    'Rebind script-src-elem to the exact B5 inline-script SHA-256.',
    'Align shell, manifest, service worker and version.json to B5 / release_sequence 120000002 / exact B5 release ID.',
    'Rebind service-worker canonical-shell SHA-256 to the exact B5 shell.',
    'Refresh current release/security/physical-gate metadata while preserving historical lineage fields.'
  ],
  dark_mode_css_changed:false,
  corpus_changed:false,
  search_changed:false,
  provenance_changed:false,
  personal_state_changed:false,
  backup_semantics_changed:false,
  physical_pass_inferred:false,
  production_deployment_authority:'NONE'
};
write(versionPath,JSON.stringify(v,null,2)+'\n');

const final={
  dir:DST,
  release_id:RELEASE_ID,
  release_sequence:RELEASE_SEQUENCE,
  shell_sha256:shellHash,
  inline_script_sha256:newScriptHash,
  inline_style_sha256:styleHashes,
  index_luisa_equal:shaHex(fs.readFileSync(DST+'/index.html'))===shaHex(fs.readFileSync(DST+'/luisa_24_heures.html')),
  manifest:JSON.parse(read(manifestPath)),
  sw_revision:(read(swPath).match(/const BUILD_REVISION = '([^']+)'/)||[])[1],
  version_revision:JSON.parse(read(versionPath)).build_revision
};
fs.writeFileSync('24h-v120-b5-build-report.json',JSON.stringify(final,null,2)+'\n');
console.log(JSON.stringify(final,null,2));