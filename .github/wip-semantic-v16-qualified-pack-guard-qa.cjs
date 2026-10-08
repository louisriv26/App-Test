const fs=require('fs'),path=require('path'),crypto=require('crypto');
const G=require('../search_semantic_pack_guard_r4.js');
const ROOT=process.env.PLS_V16_STAGE||'wip-pls-v16-qualified-pack';
const manifestPath=path.join(ROOT,'pls_v16/semantic_pack_manifest.json');
const ok=(c,m)=>{if(!c)throw new Error(m)},shaBytes=b=>crypto.createHash('sha256').update(b).digest('hex');
const manifest=JSON.parse(fs.readFileSync(manifestPath,'utf8'));
function localPath(p){if(p.startsWith('pls_v16/'))return path.join(ROOT,p);return p;}
function baseBytes(p){return new Uint8Array(fs.readFileSync(localPath(p)));}
function clone(x){return JSON.parse(JSON.stringify(x));}
function setRef(m,p,bytes){
 const h=shaBytes(bytes),n=bytes.length;
 const f=m.files.find(x=>x.path===p);ok(f,'FILE_REF '+p);f.sha256=h;f.bytes=n;
 const refs=[m.index?.vectors_file,m.index?.metadata_file,m.index?.inverse_norms_file,m.speaker_filter?.jesus_mask_file,m.coverage?.proof_file,m.coverage?.token_proof_file,m.calibration?.evidence_file].filter(Boolean);
 for(const r of refs)if(r.path===p){r.sha256=h;r.bytes=n;}
 return h;
}
async function verify(m,overrides=new Map()){return G.verifyAssets(m,async p=>overrides.has(p)?overrides.get(p):baseBytes(p));}
(async()=>{
 const report={schema:'ldc-pls-v16-qualified-pack-guard-qa-v1',checks:{},details:{},status:'UNKNOWN'};
 const good=await verify(manifest);report.details.good=good;
 report.checks.real_pack_activates=good.ok===true&&good.activation===true&&good.qualified===true&&good.code==='READY_QUALIFIED'&&good.metadata_rows===22873&&good.coverage_documents===74528&&good.coverage_tokens===1403861&&good.calibration_evidence_verified===true;

 // Rehash a calibration-evidence contradiction and update all manifest hash references.
 {
  const m=clone(manifest),p=m.calibration.evidence_file.path,ev=JSON.parse(Buffer.from(baseBytes(p)).toString('utf8'));
  ev.gates.blind_unrelated_query_gate='FAIL';
  const b=Buffer.from(JSON.stringify(ev,null,2)+'\n','utf8');setRef(m,p,b);
  const r=await verify(m,new Map([[p,new Uint8Array(b)]]));report.details.rehashed_calibration_contradiction=r;
  report.checks.rehashed_calibration_contradiction_rejected=r.ok===false&&r.code==='CALIBRATION_EVIDENCE_GATES';
 }

 // Rehash a token-coverage semantic contradiction, and also update the enclosing coverage proof/hash.
 {
  const m=clone(manifest),tp=m.coverage.token_proof_file.path,cp=m.coverage.proof_file.path;
  const tok=JSON.parse(Buffer.from(baseBytes(tp)).toString('utf8'));tok.tokens.missing=1;
  const tb=Buffer.from(JSON.stringify(tok,null,2)+'\n','utf8'),th=setRef(m,tp,tb);
  const cov=JSON.parse(Buffer.from(baseBytes(cp)).toString('utf8'));cov.token_coverage_sha256=th;
  const cb=Buffer.from(JSON.stringify(cov,null,2)+'\n','utf8');setRef(m,cp,cb);
  const r=await verify(m,new Map([[tp,new Uint8Array(tb)],[cp,new Uint8Array(cb)]]));report.details.rehashed_token_contradiction=r;
  report.checks.rehashed_token_contradiction_rejected=r.ok===false&&r.code==='TOKEN_COVERAGE_EVIDENCE_CONTRADICTION';
 }

 // Rehash a row-identity mutation and reconcile downstream hashes to prove row semantics are checked.
 {
  const m=clone(manifest),mp=m.index.metadata_file.path,cp=m.coverage.proof_file.path,ep=m.calibration.evidence_file.path;
  const lines=Buffer.from(baseBytes(mp)).toString('utf8').trimEnd().split(/\r?\n/),first=JSON.parse(lines[0]);first.passage_id='PLS16-E-96-72-TAMPER';lines[0]=JSON.stringify(first);
  const mb=Buffer.from(lines.join('\n')+'\n','utf8'),mh=setRef(m,mp,mb);
  const cov=JSON.parse(Buffer.from(baseBytes(cp)).toString('utf8'));cov.metadata_sha256=mh;const cb=Buffer.from(JSON.stringify(cov,null,2)+'\n','utf8');setRef(m,cp,cb);
  const ev=JSON.parse(Buffer.from(baseBytes(ep)).toString('utf8'));ev.pack_assets.metadata_sha256=mh;const eb=Buffer.from(JSON.stringify(ev,null,2)+'\n','utf8');setRef(m,ep,eb);
  const r=await verify(m,new Map([[mp,new Uint8Array(mb)],[cp,new Uint8Array(cb)],[ep,new Uint8Array(eb)]]));report.details.rehashed_metadata_identity_mutation=r;
  report.checks.rehashed_metadata_identity_mutation_rejected=r.ok===false&&r.code==='METADATA_IDENTITY';
 }

 report.status=Object.values(report.checks).every(Boolean)?'PASS':'FAIL';
 fs.writeFileSync('wip-pls-v16-qualified-pack-guard-qa.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
 if(report.status!=='PASS')process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
