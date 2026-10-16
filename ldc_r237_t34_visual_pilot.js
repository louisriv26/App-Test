/* R237 APPLICATION-ONLY EXTENSION: development branch. Never modify corpus or semantic speaker data.
   Explicit, exact-text and exact-segment pilot only. Does NOT implement R237's 28-paragraph / 21-boundary adapter.
   Never deploy without separate authorization and complete Reader/IndexedDB/Safari/SW qualification.
*/
(function(root){
'use strict';
const AUTHORITIES=Object.freeze({"LDC.T34.E0016.P009":{"text":"Elle appela toutes les créatures dans cette céleste Créature pour avoir la joie de les voir toutes contenues en elle et de l’entendre dire : « Tes enfants sont déjà tous en moi. Par conséquent je vous aime pour chacun d’eux. »","segments":[["LDC.T34.E0016.P009.R3A31.0000.0139.JESUS.01",0,140,"JESUS","JESUS",0],["LDC.T34.E0016.P009.R3A31.0142.0223.MARY.02",143,224,"MARY","MARY",1]]},"LDC.T34.E0018.P019":{"text":"Elle M'a prié de manifester ce que Je T'ai dit, son grand héritage pour lequel elle attend ses héritières et ce qu'elle peut faire pour elles en Me disant : « Mon fils, n'attends pas plus longtemps. Agis bientôt. Manifeste mon grand héritage et ce que je peux faire pour les créatures. Je me sens plus honorée, plus glorifiée, lorsque c'est toi qui dis ce que ta Maman peut faire que lorsque je le dis moi-même. »","segments":[["LDC.T34.E0018.P019.R3A31.0000.0155.JESUS.01",0,156,"JESUS","JESUS",0],["LDC.T34.E0018.P019.R3A31.0158.0409.MARY.02",159,411,"MARY","MARY",1]]},"LDC.T34.E0019.P010":{"text":"Elle invita le Ciel avec son Amour et elle mit sur chaque étoile le sceau du « Je T’aime, ô Fils» pour Moi et pour tous. Elle invita le soleil dans sa mer d'Amour. Et elle imprima sur chaque goutte de lumière son «Je t’aime, ô Fils».","segments":[["LDC.T34.E0019.P010.R3A31.0000.0076.JESUS.01",0,76,"JESUS","JESUS",0],["LDC.T34.E0019.P010.R3A31.0079.0096.MARY.02",79,96,"MARY","MARY",1],["LDC.T34.E0019.P010.R3A31.0098.0212.JESUS.03",98,212,"JESUS","JESUS",1],["LDC.T34.E0019.P010.R3A31.0214.0231.JESUS.04",214,231,"JESUS","JESUS",1]]},"LDC.T34.E0019.P011":{"text":"Elle demanda au soleil de revêtir de sa lumière son Créateur et de Le réchauffer afin qu'Il puisse ressentir en chaque goutte de lumière le «Je T’aime» de sa Maman.","segments":[["LDC.T34.E0019.P011.R3A31.0000.0139.JESUS.01",0,139,"JESUS","JESUS",0],["LDC.T34.E0019.P011.R3A31.0141.0150.MARY.02",141,150,"MARY","MARY",1],["LDC.T34.E0019.P011.R3A31.0152.0164.JESUS.03",152,164,"JESUS","JESUS",1]]},"LDC.T34.E0019.P012":{"text":"Elle investit le vent de son Amour et avec chaque souffle elle scella le «Je T’aime, ô Fils». Puis elle l'appela afin de Le caresser et qu'Il puisse ressentir avec chaque souffle le « Je t’aime, ô Fils, Je t’aime, ô Fils». Elle invita l'air tout entier dans ses Mers d'Amour afin qu'en respirant Il puisse ressentir le souffle d'Amour de sa Mère. Elle recouvrit la mer tout entière de sa Mer d'Amour, chaque frétillement de poissons, et la mer murmura «Je t’aime, ô Fils», et les poissons frétillaient «Je t’aime, ô Fils».","segments":[["LDC.T34.E0019.P012.R3A31.0000.0072.JESUS.01",0,72,"JESUS","JESUS",0],["LDC.T34.E0019.P012.R3A31.0074.0091.MARY.02",74,91,"MARY","MARY",1],["LDC.T34.E0019.P012.R3A31.0092.0181.JESUS.03",92,181,"JESUS","JESUS",1],["LDC.T34.E0019.P012.R3A31.0184.0220.JESUS.04",184,220,"JESUS","JESUS",1],["LDC.T34.E0019.P012.R3A31.0221.0451.JESUS.05",221,451,"JESUS","JESUS",1],["LDC.T34.E0019.P012.R3A31.0453.0470.JESUS.06",453,470,"JESUS","JESUS",1],["LDC.T34.E0019.P012.R3A31.0471.0501.JESUS.07",471,501,"JESUS","JESUS",1],["LDC.T34.E0019.P012.R3A31.0503.0520.JESUS.08",503,520,"JESUS","JESUS",1]]},"LDC.T34.E0019.P014":{"text":"C'est pourquoi les gazouillis, les trilles et les pépiements des oiseaux, même chaque atome de la terre étaient revêtus de son Amour. Le souffle des bêtes venait avec le «Je T’aime» de Ma Mère, le foin était revêtu de son Amour. Il n'y avait rien que Je puisse voir ou toucher sans ressentir la douceur de son Amour. Elle Me préparait ainsi la plus belle des Fêtes dans Ma Naissance, la Fête de l'Amour et de l’échange de Mon grand Amour que M'a fait trouver Ma douce Mère. Et c’est son Amour qui calmait Mes pleurs, qui Me réchauffait dans la mangeoire où J'étais transi de froid. Je trouvais dans son Amour celui de toutes les créatures. Et elle M'embrassait, Me pressait contre son Cœur et M’aimait avec l'Amour d'une Mère pour tous ses enfants. Et Moi, Je sentais en chaque créature son Amour maternel. Je les aimais comme ses enfants et comme Mes chers frères et sœurs.","segments":[["LDC.T34.E0019.P014.R3A31.0000.0169.JESUS.01",0,169,"JESUS","JESUS",0],["LDC.T34.E0019.P014.R3A31.0171.0180.MARY.02",171,180,"MARY","MARY",1],["LDC.T34.E0019.P014.R3A31.0182.0874.JESUS.03",182,874,"JESUS","JESUS",1]]},"LDC.T34.E0019.P018":{"text":"C'est pourquoi tu Me donnes également la Fête que Ma Mère M'a donnée à Ma Naissance. Invoque le Ciel et la terre avec ton «Je T’aime, ô Jésus».","segments":[["LDC.T34.E0019.P018.R3A31.0000.0121.JESUS.01",0,121,"JESUS","JESUS",0],["LDC.T34.E0019.P018.R3A31.0123.0141.MARY.02",123,141,"MARY","MARY",1]]}});
function signature(segs){return segs.map(s=>[s.segment_id,s.start_char,s.end_char,s.speaker,s.presentation_parent,s.quotation_depth]);}
function adapt(paraId,fullText,start,end,sourceSegments){
  const auth=AUTHORITIES[paraId];
  if(!auth || typeof fullText!=='string' || fullText!==auth.text ||
     start!==0 || end!==fullText.length || !Array.isArray(sourceSegments))return sourceSegments;
  const got=signature(sourceSegments);
  if(JSON.stringify(got)!==JSON.stringify(auth.segments))return sourceSegments;
  return sourceSegments.map(s=>{
    if(s.speaker!=='MARY')return s;
    // Modify display_speaker on a CLONE, not semantic speaker/presentation_parent/offsets.
    return Object.assign({},s,{display_speaker:'JESUS'});
  });
}
function restoreNestedClosingQuote(paraId,canonicalText,start,end,model,html){
  const authority=AUTHORITIES[paraId];
  if(!authority || typeof html!=='string' || canonicalText!==authority.text ||
     start!==0 || end!==canonicalText.length || !model || !model.ok ||
     !Array.isArray(model.runs) || !Array.isArray(model.intervals) ||
     model.intervals.map(iv=>iv.text).join('')!==canonicalText)return html;
  // Only a genuinely embedded final close-quote after one governing JESUS run
  // can be restored. A standalone direct-speech outer delimiter remains hidden.
  if(!/»\.?$/.test(canonicalText))return html;
  const styled=model.runs.filter(r=>r.styled);
  if(styled.length!==1 || styled[0].speaker!=='JESUS' ||
     !Array.isArray(styled[0].semantic_voices) ||
     !styled[0].semantic_voices.some(v=>v.speaker==='MARY'))return html;
  const close=/<span class="speech-outer-delimiter" aria-hidden="true">(\s*»)<\/span>(\.?)$/;
  const match=html.match(close);
  if(!match)return html;
  // The closing glyph is already present as canonical text. Only its derived
  // visibility/accessibility attributes change; do not append or remove text.
  return html.replace(close,(whole,quote,period)=>
    '<span class="speech-outer-delimiter" data-r237-nested-close="1">'+quote+'</span>'+period);
}
root.LDCAppOnlyVoicePilot=Object.freeze({adapt,restoreNestedClosingQuote,authoritiesCount:Object.keys(AUTHORITIES).length});
})(typeof window!=='undefined'?window:globalThis);
