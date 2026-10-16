/* R237 — LOCAL ONLY, exact-text guarded presentation adapter.
 * No corpus or source metadata edits; no IndexedDB access, no DOM replacement.
 * Runs only after the real v142.37 Reader has built its own fragment/anchor model.
 * R235 pilot authority is intentionally limited to 28 exact paragraphs.
 */
(function(global){
'use strict';
const P=(global.LDCR237PilotAuthority||{}).paragraphs||{};
const B=(global.LDCR237PilotAuthority||{}).boundaries||{};
const log=[];
const lastFinalization=new WeakMap();
function record(status,id,reason){log.push({status,id,reason});}
function checkAuthority(para,recorded,vol){
 if(!para||!recorded||Number(recorded.vol)!==Number(vol)||
    String(para.canonicalText)!==recorded.text||
    String(para.text)!==recorded.text||para.isSlice)return false;
 let end=0;
 for(const turn of recorded.turns){
   if(!Number.isInteger(turn.start)||!Number.isInteger(turn.end)||turn.start!==end||turn.end<=end||
      turn.end>recorded.text.length||!['JESUS','MARY','MARIE','LUISA','NEUTRAL'].includes(turn.speaker))return false;
   end=turn.end;
 }
 return end===recorded.text.length;
}
function applyFragment(frag,model,vol){
 if(!frag||!model)return false;
 const id=model.paraId, a=P[id];
 if(!a)return false;
 if(!checkAuthority(model,a,vol)||frag.dataset.paraId!==id ||
    Number(frag.dataset.canonicalStart)!==0||Number(frag.dataset.canonicalEnd)!==a.text.length){
    record('REJECT',id,'authority/canonical/slice mismatch');return false;
 }
 // T30 remains the already owner-approved render path, completely untouched.
 if(Number(vol)===30){record('PROTECTED_NOOP',id,'owner-accepted T30 v142.37 visual repair');return true;}
 if(!model.model||!model.model.ok){record('REJECT',id,'speech model missing');return false;}
 const turns=a.turns;
 if(turns.length>1){
    // A genuine autonomous reply may start inside a canonical paragraph.
    // Do not repaint a generic source run if exact run endpoints differ.
    if(turns.length!==2||turns[0].speaker!=='LUISA'||turns[1].speaker!=='JESUS'){
      record('REJECT',id,'unreviewed multi-turn topology');return false;
    }
    const styled=Array.from(frag.querySelectorAll('.speech-run'));
    const hit=styled.filter(n=>Number(n.dataset.runStart)===turns[1].start &&
      Number(n.dataset.runEnd)===turns[1].end &&n.classList.contains('speech-jesus'));
    if(hit.length!==1){record('REJECT',id,'autonomous speaker run mismatch');return false;}
    if(a.layoutPolicy!=='preserve_original'){record('REJECT',id,'mixed-turn visual policy invalid');return false;}
    frag.classList.add('r237-reviewed','r237-mixed');
    hit[0].classList.add('r237-autonomous-jesus');
    record('APPLY',id,'two distinct governing voices; preserved independent break');
    return true;
 }
 // Run/offset/source annotation elements stay in place, even when attribution is contested.
 const tone=turns[0].speaker;
 if(!['JESUS','LUISA'].includes(tone)){
   record('REJECT',id,'single-turn speaker outside reviewed pilot');return false;
 }
 if(a.layoutPolicy!=='reviewed_inline' && a.layoutPolicy!=='preserve_original'){
   record('REJECT',id,'missing independent visual-layout decision');return false;
 }
 frag.classList.add('r237-reviewed',tone==='JESUS'?'r237-governed-jesus':'r237-governed-neutral');
 // This class derives ONLY from the separate explicit layout authority,
 // never from speaker/colour. Real paragraph/speaker breaks are preserved.
 if(a.layoutPolicy==='reviewed_inline')frag.classList.add('r237-visual-inline');
 record('APPLY',id,'visual voice and independent reviewed layout; source metadata retained');
 return true;
}
function isVerified(frag,vol){
 const id=frag&&frag.dataset.paraId,a=id&&P[id];
 return !!(a&&Number(a.vol)===Number(vol)&&frag.classList.contains('r237-reviewed'));
}
function visualBoundary(divA,divB,from,to,action){
 if(!divA||!divB||divA===divB)return false;
 if(divA.parentElement!==divB.parentElement||divA.parentElement.id!=='reader-body')return false;
 if(divA.nextElementSibling!==divB)return false;
 if(divA.classList.contains('supplement-inline-block')||divB.classList.contains('supplement-inline-block')||
    divA.classList.contains('canonical-slice-unit')||divB.classList.contains('canonical-slice-unit'))return false;
 const la=[...divA.querySelectorAll('.para-fragment')],lb=[...divB.querySelectorAll('.para-fragment')];
 // Never suppress boundaries around unreviewed or documentary source material.
 if(!la.length||!lb.length||!la.every(x=>x.classList.contains('r237-reviewed'))||
    !lb.every(x=>x.classList.contains('r237-reviewed'))||
    la[la.length-1].dataset.paraId!==from||lb[0].dataset.paraId!==to)return false;
 if(action==='join_space'){
   divA.classList.add('r237-crossunit-inline');divB.classList.add('r237-crossunit-inline');
   const joiner=divA.ownerDocument.createElement('span');
   joiner.className='r237-crossunit-derived-space';
   joiner.dataset.visualAction='reviewed_join_space';
   joiner.setAttribute('aria-hidden','true');joiner.textContent=' ';
   divA.after(joiner);
 }
 return true;
}
function finalizeReader(body,vol,entryId){
 if(!body||!body.isConnected||!entryId)return {applied:0,pending:0};
 // Invariant on repeated calls: do not duplicate derived joiner/break nodes.
 // A new Reader render changes the firstElementChild even at the same entry.
 const cached=lastFinalization.get(body);
 if(cached&&cached.entry===entryId&&cached.vol===Number(vol)&&cached.first===body.firstElementChild)
   return {...cached.result,alreadyFinalized:true};
 const frags=[...body.querySelectorAll('.para-fragment')], byId=new Map();
 for(const f of frags){if(isVerified(f,vol)){
  if(!byId.has(f.dataset.paraId))byId.set(f.dataset.paraId,[]);
  byId.get(f.dataset.paraId).push(f);
 }}
 let applied=0,pending=0;
 for(const [edge,action] of Object.entries(B)){
   const [from,to]=edge.split('>'),l=byId.get(from)||[],r=byId.get(to)||[];
   if(l.length!==1||r.length!==1)continue;
   const L=l[0],R=r[0],la=L.closest('.dp'),rb=R.closest('.dp');
   const li=frags.indexOf(L),ri=frags.indexOf(R);
   if(ri!==li+1){record('REVIEW',edge,'not adjacent in rendered content');pending++;continue;}
   // Existing visually-approved T30 continuity remains entirely unchanged.
   if(Number(vol)===30)continue;
   if(la===rb){
      // Exact source boundary is represented by one pre-existing flow joiner.
      const n=[];for(let q=L.nextSibling;q&&q!==R;q=q.nextSibling)n.push(q);
      if(!n.length||!n.every(x=>(x.nodeType===1&&x.classList.contains('flow-joiner'))||
          (x.nodeType===1&&x.classList.contains('para-anchor')) ||
          (x.nodeType===3&&!x.textContent.trim()))){
         record('REVIEW',edge,'unexpected inter-fragment DOM');pending++;continue;
      }
      const join=n.filter(x=>x.nodeType===1&&x.classList.contains('flow-joiner'));
      if(join.length!==1){record('REVIEW',edge,'no unique canonical-free joiner');pending++;continue;}
      join[0].classList.add(action==='join_space'?'r237-inline-joiner':'r237-separate-joiner');
      applied++;
   }else if(action==='separate'){
      // A later approved join on either side can turn BOTH adjacent .dp units
      // inline: without a separate explicit boundary, the intervening true
      // Jesus->Luisa change would be accidentally flattened (T23 P058>P059).
      // This zero-text marker is outside every canonical fragment and anchor.
      if(la&&rb&&la.parentElement===rb.parentElement &&
         la.parentElement.id==='reader-body' && la.nextElementSibling===rb){
        const marker=body.ownerDocument.createElement('span');
        marker.className='r237-crossunit-explicit-break';
        marker.dataset.visualAction='reviewed_separate';
        marker.setAttribute('aria-hidden','true');
        la.after(marker);applied++;
      }else{record('REVIEW',edge,'separation topology unexpected');pending++;}
   }else if(visualBoundary(la,rb,from,to,action))applied++;
   else{record('REVIEW',edge,'cross-unit visual joining not safe');pending++;}
 }
 global.__ldcR237LocalDiagnostics={appliedBoundaries:applied,pendingBoundaries:pending,records:log.slice(),
    originalEntry:entryId,vol:Number(vol)};
 const result={applied,pending};
 lastFinalization.set(body,{entry:entryId,vol:Number(vol),first:body.firstElementChild,result});
 return result;
}
global.LDCR237LocalAdapter=Object.freeze({applyFragment,finalizeReader,checkAuthority,diagnostics:()=>log.slice()});
})(typeof window!=='undefined'?window:globalThis);
