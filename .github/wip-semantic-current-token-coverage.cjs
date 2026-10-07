const fs=require('fs'),cp=require('child_process'),crypto=require('crypto');
const ok=(c,m)=>{if(!c)throw new Error(m)},sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
cp.execFileSync(process.execPath,['.github/wip-semantic-current-pack-build.cjs'],{stdio:['ignore','pipe','inherit'],maxBuffer:32*1024*1024});
const docs=JSON.parse(fs.readFileSync('corpus/search_v2_documents.json','utf8')).documents,top=JSON.parse(fs.readFileSync('corpus/search_v21_topology.json','utf8'));
const rows=fs.readFileSync('wip-current-semantic-pack/metadata.jsonl','utf8').trimEnd().split(/\r?\n/).filter(Boolean).map(JSON.parse);
ok(rows.length===22873,'ROW_COUNT');for(const r of rows)ok(r.chunk_policy_id==='96-72-current-v14215-r1'&&String(r.passage_id).startsWith('PLS16-E-96-72-'),'ROW_IDENTITY '+r.passage_id);
function atom(a){if(Number.isInteger(a)){const d=docs[a];ok(d,'ATOM_DOC');return[a,0,String(d[5]||'').length];}ok(Array.isArray(a)&&a.length===3,'ATOM_SHAPE');const di=Number(a[0]),s=Number(a[1]),e=Number(a[2]),d=docs[di];ok(Number.isInteger(di)&&d&&Number.isInteger(s)&&Number.isInteger(e)&&s>=0&&e>=s&&e<=String(d[5]||'').length,'ATOM_RANGE');return[di,s,e];}
const overrides=new Map((top.enriched_overrides||[]).map(r=>[String(r[0]),r[1]])),expectedIntervals=Array.from({length:docs.length},()=>[]);
for(const r of top.base_units||[])for(const a of (overrides.get(String(r[0]))||r[4]||[])){const [di,s,e]=atom(a);expectedIntervals[di].push([s,e]);}
for(const r of top.complete_units||[])for(const a of (r[6]||[])){const [di,s,e]=atom(a);expectedIntervals[di].push([s,e]);}
const coverage=Array.from({length:docs.length},()=>[]);for(const r of rows)for(const s of r.source_spans||[]){const di=Number(s.doc_index),a=Number(s.canonical_start),b=Number(s.canonical_end);ok(Number.isInteger(di)&&docs[di]&&Number.isInteger(a)&&Number.isInteger(b)&&a>=0&&b>=a&&b<=String(docs[di][5]||'').length,'COVERAGE_SPAN');coverage[di].push([a,b]);}
function merge(xs){const s=xs.filter(x=>x[1]>x[0]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]),out=[];for(const x of s){const z=out[out.length-1];if(z&&x[0]<=z[1])z[1]=Math.max(z[1],x[1]);else out.push([x[0],x[1]]);}return out;}
function contains(xs,a,b){for(const x of xs){if(x[0]>a)return false;if(x[0]<=a&&x[1]>=b)return true;}return false;}
const WORD=/[\p{L}\p{N}]+(?:['’][\p{L}\p{N}]+)?/gu;let expectedTokens=0,coveredTokens=0,expectedDocs=0,coveredDocs=0,outside=0;const missing=[],outsideExamples=[];
for(let di=0;di<docs.length;di++){
 const exp=merge(expectedIntervals[di]),cov=merge(coverage[di]);if(exp.length)expectedDocs++;if(cov.length)coveredDocs++;
 for(const [s,e] of cov)if(!contains(exp,s,e)){outside++;if(outsideExamples.length<20)outsideExamples.push({doc_index:di,id:docs[di][0],span:[s,e],expected:exp.slice(0,8)});}
 const txt=String(docs[di][5]||''),seen=new Set();
 for(const [a,b] of exp){const slice=txt.slice(a,b);WORD.lastIndex=0;let m;while((m=WORD.exec(slice))){const s=a+m.index,e=s+m[0].length,k=s+':'+e;if(seen.has(k))continue;seen.add(k);expectedTokens++;if(contains(cov,s,e))coveredTokens++;else if(missing.length<50)missing.push({doc_index:di,id:docs[di][0],stable_ref:docs[di][4],token:m[0],span:[s,e]});}}
}
ok(expectedDocs===docs.length,'TOPOLOGY_DOCS '+expectedDocs);ok(coveredDocs===docs.length,'SEMANTIC_DOCS '+coveredDocs);ok(outside===0,'COVERAGE_OUTSIDE_TOPOLOGY '+outside);ok(coveredTokens===expectedTokens,'TOKEN_GAP '+coveredTokens+'/'+expectedTokens);
const out={schema:'ldc-wip-current-semantic-token-coverage-v1',status:'PASS',chunk_policy_id:'96-72-current-v14215-r1',passage_id_prefix:'PLS16-E-96-72-',rows:rows.length,documents:{current:docs.length,topology_expected:expectedDocs,semantic_covered:coveredDocs},tokens:{expected:expectedTokens,covered:coveredTokens,missing:expectedTokens-coveredTokens},coverage_outside_current_enriched_topology:outside,missing_examples:missing,outside_examples:outsideExamples,metadata_sha256:sha('wip-current-semantic-pack/metadata.jsonl')};
fs.writeFileSync('wip-current-semantic-token-coverage.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));
