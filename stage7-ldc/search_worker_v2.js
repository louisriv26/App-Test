'use strict';
importScripts('./search_engine_v2.js');
const EXPECTED_PREDECESSOR='5e3896468c6d822760fcd555c59e0042d3ed217ee7f389e8b2ab7a60d2b7d6dd';
const EXPECTED_MANIFEST_SHA256='1be0e8d1549c5a5e068fc65b3c4779c4e81ccf9d5e9185be6226723f49425d25';
const CV='LDC-V74-FAST1-CERTIFIED-MUTATION';
let enginePromise=null;
function hex(buf){return [...new Uint8Array(buf)].map(b=>b.toString(16).padStart(2,'0')).join('');}
async function sha256(bytes){return hex(await crypto.subtle.digest('SHA-256',bytes));}
async function fetchBytes(url){const r=await fetch(`${url}?${CV}`,{cache:'no-store'});if(!r.ok)throw new Error(`${url} HTTP ${r.status}`);return new Uint8Array(await r.arrayBuffer());}
function parseJson(bytes){return JSON.parse(new TextDecoder().decode(bytes));}
async function verifiedJson(url,expected){const bytes=await fetchBytes(url);const got=await sha256(bytes);if(got!==expected)throw new Error(`${url} SHA-256 mismatch`);return parseJson(bytes);}
async function load(){
 const mb=await fetchBytes('corpus/search_v2_manifest.json');const mh=await sha256(mb);if(mh!==EXPECTED_MANIFEST_SHA256)throw new Error('SEARCH-V2 manifest SHA-256 mismatch');const m=parseJson(mb);
 if(m.schema!=='ldc-search-v2-manifest-v1'||m.predecessor_sha256!==EXPECTED_PREDECESSOR)throw new Error('SEARCH-V2 manifest authority mismatch');
 const get=async p=>verifiedJson(p,m.assets[p].sha256);
 const [index,documents,entries,jesusFilter]=await Promise.all([get('corpus/search_v2_index.json'),get('corpus/search_v2_documents.json'),get('corpus/search_v2_entries.json'),get('corpus/search_v2_jesus_filter.json')]);
 return LDCSearchV2.createEngine({index,documents,entries,jesusFilter});
}
function engine(){if(!enginePromise)enginePromise=load();return enginePromise;}
self.onmessage=async ev=>{const msg=ev.data||{};if(msg.type!=='search')return;const generation=msg.generation;try{const e=await engine();const result=e.search(msg.query,msg.options||{});self.postMessage({type:'search-result',generation,ok:true,result});}catch(err){enginePromise=null;self.postMessage({type:'search-result',generation,ok:false,error:String(err&&err.message||err)});}};
