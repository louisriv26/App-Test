const {chromium}=require('playwright');
function parse(s){const m=String(s).match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(/[,\s/]+/).filter(Boolean).map(Number);return{r:a[0],g:a[1],b:a[2],a:a[3]===undefined?1:a[3]}}
function lin(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}function L(c){return .2126*lin(c.r)+.7152*lin(c.g)+.0722*lin(c.b)}function cr(a,b){return(Math.max(L(a),L(b))+.05)/(Math.min(L(a),L(b))+.05)}
(async()=>{const b=await chromium.launch({headless:true});const out=[];
for(const cand of ['24h-v120-b7-darkmode','24h-v120-b8-update-activation-closure']){
 for(const mode of ['dark','system']){
  const c=await b.newContext({colorScheme:'dark',viewport:{width:700,height:900}});const p=await c.newPage();
  await p.goto('http://127.0.0.1:8080/'+cand+'/luisa_24_heures.html',{waitUntil:'domcontentloaded',timeout:120000});
  await p.waitForFunction(()=>typeof showHome==='function',{timeout:30000});
  await p.evaluate(mode=>{if(typeof state!=='undefined'){state.themePreference=mode==='system'?'system':mode;if(typeof applyTheme==='function')applyTheme()}else document.documentElement.setAttribute('data-theme','dark'); const q=document.createElement('button');q.id='qa-int';q.className='integrity-btn';q.textContent='Vérifier';q.style.position='fixed';q.style.left='20px';q.style.top='100px';q.style.zIndex='99999';document.body.appendChild(q)},mode);
  const base=await p.$eval('#qa-int',e=>{const s=getComputedStyle(e);return{transition:s.transition,transitionDuration:s.transitionDuration,color:s.color,bg:s.backgroundColor}});
  const samples=[];await p.hover('#qa-int');
  for(const ms of [0,10,20,30,40,50,75,100,125,160,200]){if(ms)await p.waitForTimeout(ms-samples[samples.length-1]?.ms||ms);const x=await p.$eval('#qa-int',e=>{const s=getComputedStyle(e);return{color:s.color,bg:s.backgroundColor}});samples.push({ms,...x,ratio:+cr(parse(x.color),parse(x.bg)).toFixed(3)})}
  const min=Math.min(...samples.map(x=>x.ratio));out.push({cand,mode,base,min,samples});await c.close();
 }
}
await b.close();console.log(JSON.stringify(out,null,2));const bad=out.filter(x=>x.min<4.5);if(bad.length){console.error('B8_TRANSIENT_REGRESSION_FAIL',bad.map(x=>({cand:x.cand,mode:x.mode,min:x.min})));process.exit(2)}console.log('B8_TRANSIENT_REGRESSION_PASS')})().catch(e=>{console.error(e);process.exit(1)});