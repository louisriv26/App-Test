const fs=require('fs'),crypto=require('crypto'),cp=require('child_process');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const ok=(c,m)=>{if(!c)throw new Error(m);};
const run=()=>cp.execFileSync(process.execPath,['.github/wip-semantic-current-pack-build.cjs'],{stdio:['ignore','pipe','inherit'],maxBuffer:32*1024*1024});
const rm=()=>fs.rmSync('wip-current-semantic-pack',{recursive:true,force:true});
const copyHashes=()=>({
 metadata:sha('wip-current-semantic-pack/metadata.jsonl'),
 mask:sha('wip-current-semantic-pack/jesus_mask.bits'),
 manifest:sha('wip-current-semantic-pack/engineering_manifest.json')
});
rm();run();const first=copyHashes();
const firstMeta=fs.readFileSync('wip-current-semantic-pack/metadata.jsonl');
const firstMask=fs.readFileSync('wip-current-semantic-pack/jesus_mask.bits');
rm();run();const second=copyHashes();
ok(JSON.stringify(first)===JSON.stringify(second),'NON_DETERMINISTIC_REBUILD');
ok(first.metadata==='55499700d4e760671573c7e476a3709d08a9aa3aeb4ce8ce7861ee7f40d36909','METADATA_HASH_DRIFT '+first.metadata);
ok(first.mask==='8935332736286b4b8238966e7a12ee2049d5fab0816a666061db7cb2c9ee56b0','MASK_HASH_DRIFT '+first.mask);
const docs=JSON.parse(fs.readFileSync('corpus/search_v2_documents.json','utf8')).documents;
const rows=firstMeta.toString('utf8').trimEnd().split(/\r?\n/).filter(Boolean).map(JSON.parse);
ok(rows.length===22873,'ROW_COUNT '+rows.length);ok(firstMask.length===Math.ceil(rows.length/8),'MASK_BYTES');
const refToIndex=new Map(),idToIndex=new Map();docs.forEach((d,i)=>{if(d[4])refToIndex.set(String(d[4]),i);if(d[0])idToIndex.set(String(d[0]),i);});
const covered=new Uint8Array(docs.length),ids=new Set();let reconstructed=0,tokenParity=0,spanErrors=0,orderingErrors=0,lastUnit=null,lastStart=-1;
const WORD=/[\p{L}\p{N}]+(?:['’][\p{L}\p{N}]+)?/gu;
for(let ri=0;ri<rows.length;ri++){
 const r=rows[ri];ok(!ids.has(r.passage_id),'DUPLICATE_PASSAGE_ID '+r.passage_id);ids.add(r.passage_id);
 ok(r.mode==='enriched'&&r.chunk_policy_id==='96-72','ROW_IDENTITY '+r.passage_id);
 ok(Number(r.word_count)>0&&Number(r.word_count)<=96&&Number(r.end_word)-Number(r.start_word)===Number(r.word_count),'WORD_GEOMETRY '+r.passage_id);
 const toks=String(r.text||'').match(WORD)||[];if(toks.length===Number(r.word_count))tokenParity++;else throw new Error('TOKEN_PARITY '+r.passage_id+' '+toks.length+' '+r.word_count);
 if(lastUnit===r.unit_id){if(Number(r.start_word)<lastStart)orderingErrors++;}else{lastUnit=r.unit_id;lastStart=-1;}lastStart=Number(r.start_word);
 const pieces=[];for(const s of r.source_spans||[]){
   const di=Number(s.doc_index),d=docs[di];if(!Number.isInteger(di)||!d){spanErrors++;continue;}
   if(String(d[0])!==String(s.para_id)||String(d[4])!==String(s.stable_ref)){spanErrors++;continue;}
   const a=Number(s.canonical_start),b=Number(s.canonical_end),txt=String(d[5]||'');if(!Number.isInteger(a)||!Number.isInteger(b)||a<0||b<a||b>txt.length){spanErrors++;continue;}
   pieces.push(txt.slice(a,b));covered[di]=1;
 }
 if(pieces.join(' ')===String(r.text||''))reconstructed++;else throw new Error('TEXT_RECONSTRUCTION '+r.passage_id);
}
ok(spanErrors===0,'SPAN_ERRORS '+spanErrors);ok(orderingErrors===0,'ORDERING_ERRORS '+orderingErrors);ok(reconstructed===rows.length,'RECONSTRUCTION_COUNT');ok(tokenParity===rows.length,'TOKEN_COUNT');
const newCovered=covered.reduce((a,b)=>a+(b?1:0),0);ok(newCovered===74528,'NEW_COVERAGE '+newCovered);
const oldRows=fs.readFileSync('pls_v15/pack/metadata.jsonl','utf8').trimEnd().split(/\r?\n/).filter(Boolean).map(JSON.parse),oldCover=new Uint8Array(docs.length);
for(const r of oldRows)for(const s of r.source_spans||[]){let i=Number.isInteger(Number(s.doc_index))?Number(s.doc_index):-1;if(i<0||i>=docs.length||String(docs[i][4])!==String(s.stable_ref||''))i=refToIndex.get(String(s.stable_ref||''))??idToIndex.get(String(s.para_id||''))??-1;if(i>=0)oldCover[i]=1;}
const oldCovered=oldCover.reduce((a,b)=>a+(b?1:0),0),oldMissing=docs.length-oldCovered;ok(oldCovered===73731&&oldMissing===797,'OLD_GAP_REPRO '+oldCovered+'/'+oldMissing);
let maskCount=0;for(let i=0;i<rows.length;i++)if(firstMask[i>>3]&(1<<(i&7)))maskCount++;ok(maskCount===20098,'MASK_COUNT '+maskCount);
const out={schema:'ldc-wip-current-semantic-independent-qa-v1',status:'PASS',deterministic_hashes:first,rows:rows.length,documents:docs.length,new_coverage:{covered:newCovered,missing:docs.length-newCovered},old_compat_pack_gap:{covered:oldCovered,missing:oldMissing},text_reconstruction:{pass:reconstructed,total:rows.length},token_geometry:{pass:tokenParity,total:rows.length},jesus_mask:{eligible:maskCount,bytes:firstMask.length},app_runtime_mutated:false};
fs.writeFileSync('wip-current-semantic-independent-qa.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));
