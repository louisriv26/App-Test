const fs=require('fs');const V15=require('../pls_v15/hybrid_core_v1_5.js'),R6=require('../search_semantic_hybrid_r6.js');
const ok=(c,m)=>{if(!c)throw new Error(m);};
const P=[
 {passage_id:'p1',entry_id:'e1',mode:'enriched',volume:1,date_iso:'1900-01-01',text:'la volonté divine remplit la créature et lui donne la paix',source_spans:[]},
 {passage_id:'p2',entry_id:'e2',mode:'enriched',volume:1,date_iso:'1900-01-02',text:'le silence intérieur garde l âme recueillie en Dieu',source_spans:[]},
 {passage_id:'p3',entry_id:'e3',mode:'enriched',volume:2,date_iso:'1900-01-03',text:'la volonté humaine produit la croix quand elle résiste',source_spans:[]}
],bits=new Uint8Array([7]);
ok(R6.normalise("Volonté—divine")===V15.normalise("Volonté—divine"),'NORMALISE_PARITY');ok(JSON.stringify(R6.terms("Volonté divine et paix"))===JSON.stringify(V15.terms("Volonté divine et paix")),'TERMS_PARITY');
const a=V15.buildBm25(P,bits),b=R6.buildBm25(P,bits),qa=V15.bm25Search(a,'volonté divine',{sourceMode:'enriched',maxCandidates:160}),qb=R6.bm25Search(b,'volonté divine',{sourceMode:'enriched',maxCandidates:160});
ok(JSON.stringify(qa.results.map(x=>[x.passage_id,x.bm25_rank,x.bm25_score]))===JSON.stringify(qb.results.map(x=>[x.passage_id,x.bm25_rank,x.bm25_score])),'BM25_PARITY');
const dense=[{entry_id:'e3',passage_id:'p3',volume:2,text:P[2].text},{entry_id:'e1',passage_id:'p1',volume:1,text:P[0].text}],sparse=qb.results;
const f15=V15.fuse(dense,sparse,{maxResults:20}),f6=R6.fuse(dense,sparse,{maxResults:20});ok(JSON.stringify(f15.map(x=>[x.entry_id,x.rrf60_score,x.source_ranks]))===JSON.stringify(f6.map(x=>[x.entry_id,x.rrf60_score,x.source_ranks])),'RRF_PARITY');
const rows=[{entry_id:'x',rrf60_score:.032,dense_score:.72,source_ranks:{dense_96_72:1,bm25_96_72:2}},{entry_id:'y',rrf60_score:.025,dense_score:.55,source_ranks:{dense_96_72:3}}];
const p={policy_id:'HYBRID_DENSE_ABSTENTION_V1',close_enabled:false,possible_min_dense:.60,possible_min_channels:2};
ok(R6.classify(rows,p).state==='possible','POSSIBLE_CLASSIFICATION');ok(R6.classify([{...rows[0],dense_score:.58},{...rows[1],dense_score:.55}],p).state==='abstain','DENSE_ABSTAIN_CLASSIFICATION');ok(R6.classify([{...rows[0],source_ranks:{dense_96_72:1}}],p).state==='abstain','SINGLE_CHANNEL_ABSTAIN');ok(R6.classify([],p).state==='abstain','EMPTY_ABSTAIN');
ok(!fs.readFileSync('index.html','utf8').includes('search_semantic_hybrid_r6.js')&&!fs.readFileSync('index.html','utf8').includes('search_semantic_pack_registry_r6.js'),'NO_APP_WIRING');
const out={schema:'ldc-wip-hybrid-r6-qa-v1',status:'PASS',bm25_v15_parity:true,rrf60_v15_parity:true,classification:{possible:true,dense_abstain:true,single_channel_abstain:true,empty_abstain:true},runtime_wired:false};fs.writeFileSync('wip-hybrid-r6-qa.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));
