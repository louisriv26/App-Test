const fs=require('fs');
function assert(c,m){if(!c)throw new Error(m);}
let unbound=[];
global.LDCSemanticPackGuardR4={verifyAssets:async()=>({ok:true,activation:true})};
global.LDCSemanticPackRegistryR6={
 normMode:m=>String(m)==='enriched'?'enriched':null,
 preparePackSet:async specs=>({ok:true,prepared:true,_entries:Object.keys(specs)}),
 commitPreparedSet:()=>({ok:true,activation:true}),
 unbindMode:m=>{unbound.push(m);return {available:false};},
 bindModePack:async()=>({available:true})
};
require('../search_semantic_pack_lifecycle_r6.js');
const L=global.LDCSemanticPackLifecycleR6;
assert(L&&L.VERSION==='ldc-search-v3-pack-lifecycle-r6','LIFECYCLE_LOAD');
const spec=()=>({manifest:{pack_id:'pack-v16',files:[]},fetchAsset:async()=>new Uint8Array(),createEncoder:async()=>async()=>new Float32Array(384)});
async function baselineStore(){
 const s=L.createMemoryStore();await s.putManifest('old::enriched',{pack_id:'old'});await s.commitActiveSet({enriched:'old::enriched'});return s;
}
const out={schema:'ldc-semantic-pack-lifecycle-r6-failure-injection-qa-v1',checks:{},details:{},status:'UNKNOWN'};
(async()=>{
 // Successful install keeps previous bytes by default and switches pointer.
 {
  const s=await baselineStore();global.LDCSemanticPackGuardR4.verifyAssets=async()=>({ok:true,activation:true});
  global.LDCSemanticPackRegistryR6.preparePackSet=async()=>({ok:true,prepared:true});
  global.LDCSemanticPackRegistryR6.commitPreparedSet=()=>({ok:true,activation:true});
  const r=await L.installPackSet({enriched:spec()},{store:s});
  const dbg=s._debug();out.details.success={result:r,debug:dbg};
  out.checks.success_switches_pointer=r.ok===true&&dbg.active.enriched&&dbg.active.enriched!=='old::enriched'&&dbg.packs.includes('old::enriched');
 }
 // Verification failure never changes active pointer and removes staged pack.
 {
  const s=await baselineStore();global.LDCSemanticPackGuardR4.verifyAssets=async()=>({ok:false,activation:false,code:'TAMPER'});
  const r=await L.installPackSet({enriched:spec()},{store:s});const dbg=s._debug();out.details.verify_failure={result:r,debug:dbg};
  out.checks.verify_failure_preserves_old=r.ok===false&&dbg.active.enriched==='old::enriched'&&dbg.packs.length===1&&dbg.packs[0]==='old::enriched';
 }
 // Registry prepare rejection never changes active pointer and removes staged pack.
 {
  const s=await baselineStore();global.LDCSemanticPackGuardR4.verifyAssets=async()=>({ok:true,activation:true});
  global.LDCSemanticPackRegistryR6.preparePackSet=async()=>({ok:false,code:'PREPARE_REJECTED'});
  const r=await L.installPackSet({enriched:spec()},{store:s});const dbg=s._debug();out.details.prepare_failure={result:r,debug:dbg};
  out.checks.prepare_failure_preserves_old=r.ok===false&&dbg.active.enriched==='old::enriched'&&dbg.packs.length===1&&dbg.packs[0]==='old::enriched';
 }
 // Registry commit explicit failure must roll back persistent active pointer before staged deletion.
 {
  const s=await baselineStore();global.LDCSemanticPackRegistryR6.preparePackSet=async()=>({ok:true,prepared:true});
  global.LDCSemanticPackRegistryR6.commitPreparedSet=()=>({ok:false,code:'COMMIT_REJECTED'});
  const r=await L.installPackSet({enriched:spec()},{store:s});const dbg=s._debug();out.details.commit_false={result:r,debug:dbg};
  out.checks.commit_false_rolls_back=r.ok===false&&dbg.active.enriched==='old::enriched'&&dbg.packs.length===1&&dbg.packs[0]==='old::enriched';
 }
 // Unexpected registry exception after pointer switch must also roll back; this is the repaired adversarial path.
 {
  const s=await baselineStore();global.LDCSemanticPackRegistryR6.preparePackSet=async()=>({ok:true,prepared:true});
  global.LDCSemanticPackRegistryR6.commitPreparedSet=()=>{throw new Error('INJECTED_REGISTRY_THROW');};
  const r=await L.installPackSet({enriched:spec()},{store:s});const dbg=s._debug();out.details.commit_throw={result:r,debug:dbg};
  out.checks.commit_throw_rolls_back=r.ok===false&&/INJECTED_REGISTRY_THROW/.test(r.error)&&dbg.active.enriched==='old::enriched'&&dbg.packs.length===1&&dbg.packs[0]==='old::enriched';
 }
 // Missing active manifest on startup must clear pointer and unbind registry mode.
 {
  const s=L.createMemoryStore();await s.commitActiveSet({enriched:'missing-pack'});unbound=[];
  global.LDCSemanticPackRegistryR6.bindModePack=async()=>({available:true});
  const r=await L.restoreActive({store:s,encoderFactoryByPack:async()=>async()=>new Float32Array(384)});const dbg=s._debug();out.details.restore_missing={result:r,debug:dbg,unbound:[...unbound]};
  out.checks.restore_missing_fails_closed=!dbg.active.enriched&&unbound.includes('enriched')&&r.modes.enriched.ok===false;
 }
 // Removal must clear pointer, unbind and delete active bytes when requested.
 {
  const s=await baselineStore();unbound=[];const r=await L.removeMode('enriched',{store:s,deleteBytes:true});const dbg=s._debug();out.details.remove={result:r,debug:dbg,unbound:[...unbound]};
  out.checks.remove_clears_all=r.ok===true&&!dbg.active.enriched&&!dbg.packs.includes('old::enriched')&&unbound.includes('enriched');
 }
 out.status=Object.values(out.checks).every(Boolean)?'PASS':'FAIL';
 fs.writeFileSync('wip-lifecycle-r6-qa.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));
 if(out.status!=='PASS')process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
