'use strict';
importScripts('./search_engine_v2.js','./search_exact_v21.js','./search_foundation_v21b.js','./search_near_v22.js');
const EXPECTED_PREDECESSOR='5e3896468c6d822760fcd555c59e0042d3ed217ee7f389e8b2ab7a60d2b7d6dd';
const EXPECTED_MANIFEST_SHA256='295c5361c70a8d150985cee888e96a7bee8bd46c4d5197b4f3c1c6996d8dafbd';
const EXPECTED_V21_MANIFEST_SHA256='a656c6b39dd5a6e4ba5649aaf1dc2a32516009c87ec38422bc1a6472a67baec4';
const CV='LDC-V74-FAST1-CERTIFIED-MUTATION';
let enginePromise=null;
function hex(buf){return [...new Uint8Array(buf)].map(b=>b.toString(16).padStart(2,'0')).join('');}
async function sha256(bytes){return hex(await crypto.subtle.digest('SHA-256',bytes));}
async function fetchBytes(url){const r=await fetch(`${url}?${CV}`,{cache:'no-store'});if(!r.ok)throw new Error(`${url} HTTP ${r.status}`);return new Uint8Array(await r.arrayBuffer());}
function parseJson(bytes){return JSON.parse(new TextDecoder().decode(bytes));}
async function verifiedJson(url,expected){const bytes=await fetchBytes(url);const got=await sha256(bytes);if(got!==expected)throw new Error(`${url} SHA-256 mismatch`);return parseJson(bytes);}
function requireBinding(m21,m2,path,key){const expected=m21&&m21.bindings&&m21.bindings[key],actual=m2&&m2.assets&&m2.assets[path]&&m2.assets[path].sha256;if(!expected||expected!==actual)throw new Error(`SEARCH-V2.1A binding mismatch: ${key}`);}
async function load(){
 const mb=await fetchBytes('corpus/search_v2_manifest.json');const mh=await sha256(mb);if(mh!==EXPECTED_MANIFEST_SHA256)throw new Error('SEARCH-V2 manifest SHA-256 mismatch');const m=parseJson(mb);
 if(m.schema!=='ldc-search-v2-manifest-v1'||m.predecessor_sha256!==EXPECTED_PREDECESSOR)throw new Error('SEARCH-V2 manifest authority mismatch');
 const v21b=await fetchBytes('corpus/search_v21_manifest.json'),v21h=await sha256(v21b);if(v21h!==EXPECTED_V21_MANIFEST_SHA256)throw new Error('SEARCH-V2.1A manifest SHA-256 mismatch');const m21=parseJson(v21b);
 if(m21.schema!=='ldc-search-v21-manifest-r1'||m21.bindings?.normalizer!=='NFC+SEARCH_V2_NORMALISE_V1_ALL_NONEMPTY_TOKENS'||m21.bindings?.composition_contract!=='STAGE12_V21A_READER_EQUIVALENT_TOPOLOGY_R1')throw new Error('SEARCH-V2.1A manifest authority mismatch');
 requireBinding(m21,m,'corpus/search_v2_documents.json','search_v2_documents_sha256');requireBinding(m21,m,'corpus/search_v2_entries.json','search_v2_entries_sha256');requireBinding(m21,m,'corpus/search_v2_index.json','search_v2_index_sha256');requireBinding(m21,m,'corpus/search_v2_jesus_filter.json','search_v2_jesus_filter_sha256');
 const get=async p=>verifiedJson(p,m.assets[p].sha256);
 const [index,documents,entries,jesusFilter,topology]=await Promise.all([get('corpus/search_v2_index.json'),get('corpus/search_v2_documents.json'),get('corpus/search_v2_entries.json'),get('corpus/search_v2_jesus_filter.json'),verifiedJson(m21.topology_asset,m21.topology_sha256)]);
 if(JSON.stringify(topology.bindings)!==JSON.stringify(m21.bindings))throw new Error('SEARCH-V2.1A topology binding mismatch');
 const lexical=LDCSearchV2.createEngine({index,documents,entries,jesusFilter});
 const exact=LDCSearchExactV21.createExactLayer({documents,entries,jesusFilter,topology});
 const foundation=LDCSearchFoundationV21B.createFoundation({lexical,exact,documents:documents.documents,entries:entries.entries,jesusFilter,topology,index});
 const near=LDCSearchNearV22.createNearLayer({index,documents,entries,jesusFilter,topology,exact});
 return {search(raw,options){const query=String(raw==null?'':raw).normalize('NFC'),opt=options||{},base=foundation.search(query,opt);const nearResult=base.structuralError?{schema:'ldc-search-v22-near-result-r1',version:LDCSearchNearV22.VERSION,eligible:false,reason:'STRUCTURAL_ERROR',results:[],totalAccepted:0,ambiguous:false,competitive_count:0}:near.search(base.parsed,opt);return {...base,near:nearResult};}};
}
function engine(){if(!enginePromise)enginePromise=load();return enginePromise;}
self.onmessage=async ev=>{const msg=ev.data||{};if(msg.type!=='search')return;const generation=msg.generation;try{const e=await engine();const result=e.search(msg.query,msg.options||{});self.postMessage({type:'search-result',generation,ok:true,result});}catch(err){enginePromise=null;self.postMessage({type:'search-result',generation,ok:false,error:String(err&&err.message||err)});}};
