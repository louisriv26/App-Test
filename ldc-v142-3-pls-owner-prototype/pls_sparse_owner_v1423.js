/* LDC Par le sens owner prototype v142.3 — current-v142 96/72 passage BM25.
   Owner/App-Test diagnostic only. No production qualification claim. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.LDCPLSSparseOwnerV1423=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='ldc-pls-sparse-owner-v142.3-v1',K1=1.2,B=0.75,WIN=96,STRIDE=72,OUT=20;
let initPromise=null,state=null,lastError=null;
function norm(s){s=String(s||'').toLowerCase();const r=[['é','e'],['è','e'],['ê','e'],['ë','e'],['à','a'],['â','a'],['î','i'],['ï','i'],['ô','o'],['ö','o'],['ù','u'],['û','u'],['ü','u'],['ç','c'],['œ','oe'],['æ','ae']];for(const [a,b] of r)s=s.split(a).join(b);return s.replace(/[\u00A0\u202F]/g,' ').replace(/[‘’‚‛]/g,' ').replace(/[-–—]/g,' ').replace(/[^A-Za-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();}
function qterms(s){return [...new Set(norm(s).split(' ').filter(t=>t&&t.length>=3))];}
function allTerms(s){return norm(s).split(' ').filter(t=>t&&t.length>=3);}
function bitBytes(s){const bin=atob(s),a=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)a[i]=bin.charCodeAt(i);return a;}
function bitHas(bits,i){return !!(bits[i>>3]&(1<<(i&7)));}
async function getJson(path){const r=await fetch(path,{cache:'force-cache'});if(!r.ok)throw new Error('PLS_FETCH_'+path+':'+r.status);return r.json();}
function buildWindows(docPayload,entryPayload,jesusPayload){
 const docs=docPayload.documents,entries=entryPayload.entries,bits=bitBytes(jesusPayload.bits_b64),by=Array.from({length:entries.length},()=>[]);
 for(let i=0;i<docs.length;i++){const d=docs[i];if(by[d[1]])by[d[1]].push([i,d]);}
 const passages=[];let totalDl=0;
 for(let ei=0;ei<entries.length;ei++){
  const ds=by[ei];if(!ds||!ds.length)continue;ds.sort((a,b)=>a[0]-b[0]);
  let text='',ranges=[];
  for(const [di,d] of ds){const t=String(d[5]||'').trim();if(!t)continue;if(text)text+=' ';const start=text.length;text+=t;ranges.push({di,start,end:text.length,d,trimLeft:String(d[5]||'').indexOf(t)});}
  const toks=[];const rx=/\S+/g;let m;while((m=rx.exec(text)))toks.push([m.index,m.index+m[0].length]);
  for(let sw=0;sw<toks.length;sw+=STRIDE){const ew=Math.min(sw+WIN,toks.length);if(sw>=ew)break;const a=toks[sw][0],z=toks[ew-1][1],ptext=text.slice(a,z),spans=[];let hasJesus=false;
   for(const rr of ranges){const x=Math.max(a,rr.start),y=Math.min(z,rr.end);if(x<y){const cs=(x-rr.start)+rr.trimLeft,ce=(y-rr.start)+rr.trimLeft;spans.push({doc_index:rr.di,para_id:rr.d[0],stable_ref:rr.d[4],canonical_start:cs,canonical_end:ce});if(bitHas(bits,rr.di))hasJesus=true;}}
   const ts=allTerms(ptext);totalDl+=ts.length;passages.push({passage_id:`V1423-96-72-${String(passages.length+1).padStart(6,'0')}`,entry_index:ei,entry_id:entries[ei][0],volume:entries[ei][2],title:entries[ei][3],date_display:entries[ei][4],date_iso:entries[ei][5],kind:docs[ds[0][0]][3]===1?'supplement':'principal',text:ptext,source_spans:spans,has_jesus:hasJesus,dl:ts.length});
   if(ew===toks.length)break;
  }
 }
 return {passages,entries,avgdl:totalDl/Math.max(1,passages.length)};
}
async function init(){if(state)return status();if(initPromise)return initPromise;initPromise=(async()=>{try{const [d,e,j]=await Promise.all([getJson('corpus/search_v2_documents.json'),getJson('corpus/search_v2_entries.json'),getJson('corpus/search_v2_jesus_filter.json')]);state=buildWindows(d,e,j);lastError=null;return status();}catch(e){lastError=String(e&&e.message||e);state=null;throw e;}finally{if(!state)initPromise=null;}})();return initPromise;}
function status(){return {schema:'ldc-pls-owner-prototype-status-v1',version:VERSION,available:true,ready:!!state,loading:!!initPromise&&!state,error:lastError,prototype:true,source_mode:'enriched',chunk_policy_id:'96-72-current-v142',retrieval:'MATCHED_WINDOW_BM25'};}
function allowed(p,opt){if(opt.volMin&&p.volume<opt.volMin)return false;if(opt.volMax&&p.volume>opt.volMax)return false;if(opt.dateIso&&p.date_iso!==opt.dateIso)return false;if(opt.year&&String(p.date_iso||'').slice(0,4)!==String(opt.year))return false;if(opt.jesus&&!p.has_jesus)return false;if(opt.stableRef){const r=String(opt.stableRef).toUpperCase();if(!(p.source_spans||[]).some(s=>String(s.stable_ref||'').toUpperCase().includes(r)))return false;}return true;}
async function search(query,options={}){const q=String(query||'').trim();if(!q)throw new Error('PLS_QUERY_EMPTY');await init();const opt={volMin:0,volMax:0,dateIso:null,year:0,stableRef:null,jesus:false,...options},qt=qterms(q),N=state.passages.length,dfs=new Map(),rows=[];
 for(let i=0;i<N;i++){const p=state.passages[i];if(!allowed(p,opt))continue;const ts=allTerms(p.text),c=new Map();for(const t of ts)if(qt.includes(t))c.set(t,(c.get(t)||0)+1);for(const t of c.keys())dfs.set(t,(dfs.get(t)||0)+1);rows.push({i,c});}
 const scored=[];for(const x of rows){if(!x.c.size)continue;const p=state.passages[x.i];let score=0;for(const [t,tf] of x.c){const df=dfs.get(t)||0,idf=Math.log(1+(rows.length-df+.5)/(df+.5)),den=tf+K1*(1-B+B*p.dl/state.avgdl);score+=idf*tf*(K1+1)/den;}if(score>0)scored.push({i:x.i,score});}
 scored.sort((a,b)=>b.score-a.score||a.i-b.i);const seen=new Set(),results=[];for(const x of scored){const p=state.passages[x.i];if(seen.has(p.entry_id))continue;seen.add(p.entry_id);results.push({...p,bm25_score:x.score,bm25_entry_rank:results.length+1});if(results.length>=OUT)break;}
 return {schema:'ldc-pls-owner-prototype-result-v142.3-v1',prototype_owner_v1423:true,query:q,source_mode:'enriched',candidate_population:'CURRENT_V142_96_72_MATCHED_WINDOW_BM25',confidence:{state:'possible',label:'Prototype personnel — pistes issues de la mémoire de votre formulation'},results,diagnostics:{passages:N,query_terms:qt.length,retrieval:'BM25_96_72_CURRENT_V142'}};}
return Object.freeze({VERSION,status,init,search,_test:{norm,qterms,allTerms,buildWindows}});
});
