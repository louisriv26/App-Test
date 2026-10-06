import { AutoTokenizer, AutoModel, env, mean_pooling } from '@huggingface/transformers';
import fs from 'node:fs';

const REV='761b726dd34fb83930e26aab4e9ac3899aa1fa78';
const ROOT='/tmp/ldc-e5-models';
const MODEL='e5';
const fixtures=JSON.parse(fs.readFileSync(new URL('./fixtures.json', import.meta.url),'utf8'));

env.allowRemoteModels=false;
env.allowLocalModels=true;
env.localModelPath=ROOT+'/';
env.useFS=true;
env.useFSCache=false;
env.useBrowserCache=false;

function b64ToI8(s){const b=Buffer.from(s,'base64');return new Int8Array(b.buffer,b.byteOffset,b.byteLength);}
function quantizers(v){
  let m=0;for(const x of v)m=Math.max(m,Math.abs(x));const scale=127/m;
  const mk=(fn)=>Int8Array.from(v,x=>Math.max(-127,Math.min(127,fn(x*scale))));
  return {
    js_round:mk(Math.round),
    away_from_zero:mk(x=>x<0?-Math.round(-x):Math.round(x)),
    trunc:mk(Math.trunc),
    floor:mk(Math.floor),
    ceil:mk(Math.ceil),
  };
}
function compare(a,b){let n=0,max=0,sum=0;for(let i=0;i<a.length;i++){const d=Math.abs(a[i]-b[i]);if(d)n++;if(d>max)max=d;sum+=d;}return {mismatches:n,max_abs_diff:max,sum_abs_diff:sum};}
function invNorm(q){let s=0;for(const x of q)s+=x*x;return 1/Math.sqrt(s);}

console.log(JSON.stringify({phase:'load',revision:REV,localModelPath:env.localModelPath}));
const tokenizer=await AutoTokenizer.from_pretrained(MODEL,{local_files_only:true});
const model=await AutoModel.from_pretrained(MODEL,{local_files_only:true,subfolder:'onnx',model_file_name:'model',dtype:'int8',device:'cpu'});
const report=[];
for(const f of fixtures){
  const t=await tokenizer(['passage: '+f.text],{padding:true,truncation:true,max_length:512});
  const out=await model(t);const h=out.last_hidden_state||out[Object.keys(out)[0]];
  const pooled=mean_pooling(h,t.attention_mask).normalize(2,-1);const v=Float32Array.from(pooled.data);
  if(v.length!==384)throw new Error('dimension '+v.length);
  const expected=b64ToI8(f.vector_b64);const candidates=quantizers(v);const cmp={};
  for(const [k,q] of Object.entries(candidates))cmp[k]={...compare(q,expected),inv_norm:invNorm(q),expected_inv_norm:f.inverse_norm};
  report.push({row:f.row,passage_id:f.passage_id,max_abs_float:Math.max(...Array.from(v,Math.abs)),comparisons:cmp});
}
console.log(JSON.stringify({phase:'result',report},null,2));
const exact=report.every(r=>Object.values(r.comparisons).some(x=>x.mismatches===0));
if(!exact){process.exitCode=2;}else{console.log('EXACT_SAMPLE_REPRODUCTION_PASS');}
