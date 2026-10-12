/* R88 — bounded, conservative structural-intent gate; no corpus, model or ranking mutation.
 * Frozen source authority: v142.19; R86 preserved separately, never extended in place. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.LDCStructuralPreflightR88=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='ldc-structural-preflight-r88';
const months={janvier:1,'février':2,fevrier:2,mars:3,avril:4,mai:5,juin:6,juillet:7,'août':8,aout:8,septembre:9,octobre:10,novembre:11,'décembre':12,decembre:12};
const rxMonths=Object.keys(months).sort((a,b)=>b.length-a.length).join('|');
const frDate=new RegExp('\\b(1er|[1-9]|[12]\\d|3[01])\\s+('+rxMonths+')\\s+((?:18|19|20)\\d{2})\\b','gi');
const monYear=new RegExp('\\b('+rxMonths+')\\s+((?:18|19|20)\\d{2})\\b','gi');
const isoDate=/\b((?:18|19|20)\d{2})[-/](\d{1,2})[-/](\d{1,2})\b/g;
const slashDate=/\b([0-3]?\d)[/-]([01]?\d)[/-]((?:18|19|20)\d{2})\b/g;
const refsRx=/\b(?:LDCSUP|LDC)\.[A-Za-z0-9][A-Za-z0-9._-]*/gi;
const volumeRx=/\btomes?\s+(\d+)\b/gi;
const volumeAlts=/\btomes?\s+(\d+)\s*(ou|et|,|;|\/|-|–|—|à)\s*(?:tomes?\s+)?(\d+)\b/gi;
const spacedAlts=/\btomes?\s+(\d+)\s+ou\s+(?:dans\s+le\s+)?tomes?\s+(\d+)\b/gi;
const yearRx=/\b(?:18|19|20)\d{2}\b/g;
const yearAlts=/\b((?:18|19|20)\d{2})\s*(ou|et|,|;)\s*((?:18|19|20)\d{2})\b/gi;
const span=(m,type,ext={})=>({type,start:m.index,end:m.index+m[0].length,text:m[0],...ext});
const overlap=(a,b)=>a.start<b.end&&b.start<a.end;
const intersects=(x,items)=>items.some(a=>overlap(x,a));
function removeRanges(raw, ranges){let s=raw;for(const [a,b] of [...ranges].sort((x,y)=>y[0]-x[0]))s=s.slice(0,a)+s.slice(b);return s.replace(/\s+/g,' ').trim();}
function replaceRange(raw,a,b,replacement){return(raw.slice(0,a)+replacement+raw.slice(b)).replace(/\s+/g,' ').trim();}
function validDate(y,m,d){if(!Number.isInteger(y)||!Number.isInteger(m)||!Number.isInteger(d)||y<1800||y>2099||m<1||m>12||d<1)return false;let feb=(y%4===0&&(y%100!==0||y%400===0))?29:28;return d<=[31,feb,31,30,31,30,31,31,30,31,30,31][m-1];}
function fmt(y,m,d){return `${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`;}
function group(v){let min=Math.floor((v-1)/6)*6+1;return{min,max:Math.min(36,min+5)};}
function stripArticle(raw,a,b){let left=raw.slice(0,a),right=raw.slice(b);left=left.replace(/\b(?:le|du|de|en)\s*[,;:]?\s*$/i,'');return (left+' '+right).replace(/\s+/g,' ').trim().replace(/\s+[,;:]\s*$/,'');}
function cleanDescription(raw,atoms){
 const ranges=atoms.map(a=>[a.start,a.end]);let desc=removeRanges(raw,ranges).replace(/[(),;:.]+/g,' ').replace(/\s+/g,' ').trim();
 // Only bounded search boilerplate and grammar adjacent to structural components.
 desc=desc.replace(/^je\s+cherche(?:\s+à\s+trouver)?\s*/i,'');
 // Prepositions generally stranded by date/tome removal; remove as entire boundary phrases only.
 desc=desc.replace(/^(?:(?:dans\s+le|dans\s+les|le|la|les|du|de|en|et|au|à)\b\s*)+/i,'');
 desc=desc.replace(/\s+(?:dans\s+le|dans\s+les|du|de|en|et|le|la|les)$/i,'');
 // The whole residue must be nonsemantic for pure structural navigation. Never erase content words.
 if(/^(?:(?:dans\s+le|dans\s+les|je\s+cherche|le|la|les|du|de|en|et|à|au)\s*)*$/i.test(desc))return '';
 return desc.trim();
}
function analyze(input,flags={}){
 const raw=String(input||'').normalize('NFC').trim(),mode=flags.mode==='words'?'words':'meaning',chipMin=Number(flags.volMin)||0,chipMax=chipMin?Number(flags.volMax)||chipMin:0,jesus=!!flags.jesus,sourceMode=flags.sourceMode||'enriched';
 const refs=[],dates=[],monthsFound=[],volumes=[],years=[],alts=[];
 for(const m of raw.matchAll(refsRx))refs.push(span(m,'ref',{value:m[0].replace(/[.,;:]+$/,'').toUpperCase()}));
 for(const m of raw.matchAll(frDate)){
   // Without a separating day, `Tome 12 février 1919` is a TOME and MONTH, not 12-Feb.
   let a=span(m,'date',{year:+m[3],month:months[m[2].toLowerCase()],day:m[1].toLowerCase()==='1er'?1:+m[1]});
   const prefix=raw.slice(Math.max(0,a.start-9),a.start);if(/\btomes?\s*$/i.test(prefix))continue;
   if(!intersects(a,refs))dates.push({...a,iso:fmt(a.year,a.month,a.day),valid:validDate(a.year,a.month,a.day)});
 }
 for(const m of raw.matchAll(isoDate)){const a=span(m,'date',{year:+m[1],month:+m[2],day:+m[3]});if(!intersects(a,[...refs,...dates]))dates.push({...a,iso:fmt(a.year,a.month,a.day),valid:validDate(a.year,a.month,a.day)});}
 for(const m of raw.matchAll(slashDate)){const a=span(m,'date',{year:+m[3],month:+m[2],day:+m[1]});if(!intersects(a,[...refs,...dates]))dates.push({...a,iso:fmt(a.year,a.month,a.day),valid:validDate(a.year,a.month,a.day)});}
 for(const m of raw.matchAll(monYear)){const a=span(m,'month',{year:+m[2],month:months[m[1].toLowerCase()]});if(!intersects(a,[...refs,...dates]))monthsFound.push({...a,iso:`${a.year}-${String(a.month).padStart(2,'0')}`});}
 const shield=[...refs,...dates,...monthsFound];
 for(const m of raw.matchAll(spacedAlts)){const a=span(m,'alternative-volume',{left:+m[1],right:+m[2],join:'ou'});if(!intersects(a,shield))alts.push(a);}
 for(const m of raw.matchAll(volumeAlts)){
   // R114-S: A four-digit year following comma/et/semicolon is not an implicit second Tome.
   // An explicit second `Tome 1919` remains an invalid volume; `ou` remains ambiguous.
   const secondIsExplicitTome=/\btomes?\s+\d+\s*$/i.test(m[0].slice(m[0].indexOf(m[2])+m[2].length));
   if(/^(?:18|19|20)\d{2}$/.test(m[3])&&!secondIsExplicitTome&&/^(?:et|,|;)$/.test(m[2]))continue;
   const a=span(m,'alternative-volume',{left:+m[1],right:+m[3],join:m[2].toLowerCase()});
   if(!intersects(a,[...shield,...alts]))alts.push(a);
 }
 for(const m of raw.matchAll(volumeRx)){const a=span(m,'volume',{value:+m[1]});if(!intersects(a,[...shield,...alts]))volumes.push(a);}
 for(const m of raw.matchAll(yearAlts)){const a=span(m,'alternative-year',{left:+m[1],right:+m[3],join:m[2].toLowerCase()});if(!intersects(a,[...shield,...alts,...volumes]))alts.push(a);}
 for(const m of raw.matchAll(yearRx)){const a=span(m,'year',{value:+m[0]});if(!intersects(a,[...shield,...alts,...volumes]))years.push(a);}
 const atoms=[...refs,...dates,...monthsFound,...volumes,...alts,...years].sort((a,b)=>a.start-b.start||a.end-b.end);
 const description=cleanDescription(raw,atoms),pure=atoms.length>0&&!description;
 const structural={volume:volumes.length===1?volumes[0].value:null,date:dates.length===1&&dates[0].valid?dates[0].iso:(monthsFound.length===1?monthsFound[0].iso:null),year:dates.length||monthsFound.length?null:(years.length===1?years[0].value:null),ref:refs.length===1?refs[0].value:null};
 const opts={sourceMode:'enriched',volMin:structural.volume||chipMin||0,volMax:structural.volume||chipMax||0,dateIso:structural.date||null,year:structural.year||0,stableRef:structural.ref||null,jesus,maxResults:20};
 const base={schema:'ldc-structural-intent-r88',version:VERSION,raw,mode,sourceMode,jesus,chip:{min:chipMin,max:chipMax},atoms,residual:description,description,pure,structural,status:'ready',route:mode==='words'?'words':(pure?'structural':'semantic'),engineQuery:raw,options:opts,actions:[],message:null};
 const unsupported=(reason,message)=>({...base,status:'unsupported',reason,message,actions:[],route:null});
 const clarify=(reason,message,actions)=>({...base,status:'clarify',reason,message,actions,route:null});
 const action=(a,label,replace='',chip=null)=>({label,query:replaceRange(raw,a.start,a.end,replace),chip});
 // R111: complete validation BEFORE emitting any exact structural filter.
 // This deliberately recognizes only a bounded set of French structural expressions;
 // unknown constraints fail closed instead of being silently made positive/exact.
 const tomeMentions=atoms.filter(a=>a.type==='volume'||a.type==='alternative-volume');
 const invalidTome=tomeMentions.find(a=>{
   const numeric=String(a.text.match(/\btomes?\s+(\d+)/i)?.[1]||'');
   const first=a.type==='volume'?a.value:a.left,second=a.type==='alternative-volume'?a.right:null;
   const longNumber=!!raw.slice(a.start,a.end).match(/\btomes?\s+\d{4,}|\b(?:ou|et)\s+\d{4,}/i);
   return longNumber||numeric.length>3||first<1||first>36||(second!==null&&(second<1||second>36))||
     (a.type==='alternative-volume'&&a.text.match(/\b(?:ou|et|,|;|\/|-|–|—|à)\s+(?:tomes?\s+)?(\d+)/i)?.[1]?.length>3);
 });
 if(invalidTome){
   // Do not 'correct' 37 to 36, or discard an invalid half of an alternative.
   const trimmed=stripArticle(raw,invalidTome.start,invalidTome.end);
   return clarify('invalid-explicit-tome',`La mention « ${invalidTome.text} » contient un Tome inexistant ou mal formé (Tomes 1 à 36). Aucun filtre de Tome n’a été appliqué.`,
     trimmed?[{label:'Retirer explicitement cette mention (sans deviner de Tome)',query:trimmed,chip:null}]:[]);
 }
 // R112: expressions that cannot denote a positive exact filter must not be
 // stripped into one. Scope these guards to explicit structural atoms only.
 const normalizedBefore=a=>raw.slice(Math.max(0,a.start-100),a.start)
   .normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[’‘]/g,"'").toLowerCase().replace(/\s+/g,' ');
 const refIsExcluded=refs.some(a=>/(?:\b(?:pas|jamais)\s+dans\s+(?:(?:le|la)\s+)?|\b(?:sauf|hors|excepte|exclure|excluant)\s+(?:la\s+reference\s+|le\s+)?|\ben\s+dehors\s+de\s+|\ba\s+l'exclusion\s+de\s+(?:la\s+reference\s+)?|\bne\s+(?:se\s+trouve|figure)\s+pas\s+dans\s+|\bje\s+ne\s+pense\s+pas\s+que\s+(?:cela|ce)\s+soit\s+dans\s+)$/i.test(normalizedBefore(a)));
 if(refIsExcluded)return clarify('negative-reference','Une référence semble exclue : elle ne peut pas devenir un filtre positif. Reformulez votre demande.',[]);
 if(volumes.some(a=>/\b(?:je\s+)?ne\s+pense\s+pas\s+que\s+(?:cela|ce)\s+soit\s+dans\s+(?:(?:le|du)\s+)?$/i.test(normalizedBefore(a))))
   return clarify('negative-volume-proposition','Une phrase indique que ce Tome ne contient probablement pas le passage : confirmez un Tome à inclure ou cherchez sans ce critère.',[]);
 if(years.some(a=>/\b(?:avant|apres|depuis|pendant|jusqu'a|jusqu'en|dans|vers|entre|au\s+cours\s+de)\s+(?:(?:les|des)\s+)?annees\s*$/i.test(normalizedBefore(a))||/\b(?:les|des)\s+annees\s*$/i.test(normalizedBefore(a))))
   return clarify('decade-or-period-not-exact','Une décennie ou une période ne peut pas être transformée en une année unique. Précisez une année exacte ou cherchez sans ce filtre.',[]);
 if(volumes.some(a=>/^\s+(?:ou|et)\s+(?:(?:celui|celle)\s+de|(?:le|la)\s+)\s*\d{1,3}\b/i.test(raw.slice(a.end))))
   return clarify('implicit-second-volume','Vous semblez citer plusieurs Tomes sans préciser la portée du second numéro. Indiquez un seul Tome avant la recherche.',[]);
 // A zero-padded valid Tome must be normalized in the engine query in Words mode.
 // R114-S: bounded, atom-scoped exclusions/periods/durations left ambiguous by R112.
 // Guards act before the exact options are exposed to either words or meaning engine.
 for(const a of atoms){
   const before=normalizedBefore(a),after=raw.slice(a.end,a.end+72).normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[’‘]/g,"'").toLowerCase();
   if(a.type==='volume'&&/\bne\s+doit\s+pas\s+etre\s+dans\s+(?:le\s+)?$/i.test(before))
     return clarify('negative-volume-modal','Le Tome mentionné est exclu, non demandé comme filtre positif. Reformulez la demande.',[]);
   if(a.type==='year'){
     if(/\bje\s+ne\s+pense\s+pas\s+que\s+(?:ce|cela)\s+soit\s+(?:en\s+)?$/i.test(before))
       return clarify('negative-year-proposition','L’année apparaît dans une phrase négative : aucun filtre positif ne peut être appliqué.',[]);
     if(/\b(?:la\s+)?decennie\s+(?:de\s+|des\s+|en\s+)?$/i.test(before))
       return clarify('decade-not-exact-year','Une décennie n’est pas une année unique. Précisez une date exacte.',[]);
     if(/^\s+ans\b/i.test(after))
       return clarify('duration-not-year','Un nombre d’années indique une durée, pas une année de publication. Reformulez.',[]);
   }
   if((a.type==='year'||a.type==='date'||a.type==='month')&&/^\s*[,;]?\s*approximativement\b/i.test(after))
     return clarify('postposed-approximate-date','La date est approximative : aucune date exacte ne sera imposée.',[]);
 }
 const paddedTomes=volumes.filter(a=>/\btomes?\s+0\d+/i.test(a.text));
 const allStructural=[...dates,...monthsFound,...years,...volumes];
 const issue=(reason,message)=>clarify(reason,message,[]);
 const canonical=s=>String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[’‘]/g,"'").toLowerCase();
 const scopeBefore=(a,n=85)=>canonical(raw.slice(Math.max(0,a.start-n),a.start)).replace(/\s+/g,' ');
 const scopeAfter=(a,n=65)=>canonical(raw.slice(a.end,a.end+n)).replace(/\s+/g,' ');
 for(const a of allStructural){
   const before=scopeBefore(a),after=scopeAfter(a);
   if(a.type==='volume'){
     // Only a negation governing the Tome is relevant: 'Tome 12 pas dans le texte'
     // describes the text and must NOT be classified as NOT Tome 12.
     if(/(?:\bpas\s+(?:du\s+tout\s+)?(?:dans\s+(?:le\s+)?|le\s+|du\s+|en\s+)?|\bne\s+(?:se\s+trouve|figure|serait)\s+pas\s+dans\s+(?:le\s+)?|\bhors\s+(?:du\s+|le\s+)?|\bsauf\s+(?:le\s+|dans\s+le\s+)?|\ben\s+dehors\s+du\s+|\ba\s+l'exclusion\s+du\s+|\bexcepte\s+le\s+|\bnon\s+(?:le\s+)?|\bplutot\s+que\s+(?:le\s+)?)$/i.test(before))
       return issue('negative-volume','Vous semblez exclure un Tome. Cette version ne prend pas en charge « sauf/pas dans le Tome ». Reformulez sans cette exclusion ou précisez un Tome à inclure.');
     if(/^\s*(?:\?|pas\s*(?:$|[,;.!?]|le\b|du\b))/.test(after))
       return issue('postposed-negative-volume','La mention du Tome est négative ou incertaine : précisez le Tome voulu avant de chercher.');
   }
   if(a.type==='volume'||a.type==='year'||a.type==='month'||a.type==='date'){
     // Modalities relevant to a nearby structural criterion. Avoid treating ordinary
     // prose containing "pas dans le texte" as an uncertainty about its Tome.
     if(/(?:\b(?:peut-?etre|probablement|vraisemblablement|environ|approximativement|incertain|incertaine|vers|autour\s+de|je\s+crois|je\s+pense|il\s+me\s+semble|sans\s+certitude|a\s+peu\s+pres)\s*(?:(?:dans|en|le|la|du|de|des|l'|d'|que\s+c'est|que\s+ce\s+soit|il\s+s'agit\s+du)\s*){0,4})$/i.test(before)||
        /^\s*[,;]?\s*(?:peut-?etre|probablement|environ|a\s+peu\s+pres|sans\s+certitude|je\s+crois|je\s+pense|incertain\w*|\?)\b/i.test(after))
       return issue('uncertain-structural','Un Tome ou une date semble approximatif ou incertain. Aucun filtre exact n’est appliqué sans confirmation : retirez l’indice incertain ou rendez-le explicitement certain.');
   }
   if(a.type==='year'||a.type==='month'||a.type==='date'){
     // Bounded date/year/time ranges are NOT equivalent to exact selection.
     if(/(?:\b(?:avant|apres|depuis|jusqu'(?:en|a)|jusque\s+(?:en|au|le)|a\s+partir\s+(?:de|du)|entre|a\s+compter\s+de|au\s+plus\s+(?:tot|tard)|au\s+(?:moins|minimum|maximum)|pas\s+(?:avant|apres)|vers\s+la\s+fin\s+de|pas\s+(?:en|le|de)|hors\s+de)\s*(?:l'annee\s+|l'an\s+|en\s+|de\s+|du\s+|le\s+|la\s+|au\s+|d'\s*){0,3})$/i.test(before)||
       /\b(?:dans\s+les\s+annees|pendant\s+les\s+annees|au\s+cours\s+des\s+annees)\s*$/i.test(before)||
       /^\s*(?:ou\s+(?:avant|apres)|ou\s+plus\s+(?:tot|tard))\b/i.test(after))
       return issue('temporal-range-not-exact','L’année ou la date exprime une borne ou une période. Cette version n’applique que les dates exactes ; précisez votre demande, ou retirez la restriction.');
   }
 }
 // Other explicit Tome mentions must not be accidentally swallowed as ordinary prose.
 // The atom regexes above cover the same full Tome-number syntax; fail closed if
 // a mention remains unaccounted for (e.g. long, malformed or composite number).
 for(const m of raw.matchAll(/\btomes?\s+(\d+)\b/gi)){
   if(!atoms.some(a=>a.start<=m.index&&a.end>=m.index+m[0].length))
     return issue('unaccounted-tome','Une mention explicite de Tome n’a pas pu être interprétée de manière sûre. Reformulez-la avant la recherche.');
 }
 if(refs.length>1)return unsupported('multiple-references','Plusieurs références : conservez une référence précise.');
 if(dates.length>1||monthsFound.length>1||(dates.length&&monthsFound.length))return unsupported('multiple-dates','Dates ou mois multiples : précisez une seule période.');
 if(alts.length>1)return unsupported('multiple-alternatives','Plusieurs alternatives : précisez votre intention.');
 if(volumes.length>1)return unsupported('multiple-volumes','Plusieurs tomes : précisez un seul tome.');
 for(const r of refs){const m=r.value.match(/^(?:LDCSUP|LDC)\.T(\d+)(?:\.|$)/);if(m&&(+m[1]<1||+m[1]>36))return unsupported('invalid-reference-volume','Cette référence contient un tome hors de 1–36.');}
 // Adjacent uncertainty/negation, never a remote arbitrary preceding `pas`.
 const near=(a,expr,dist=26)=>expr.test(raw.slice(Math.max(0,a.start-dist),a.start));
 // Interposed range marker is not interchangeable with a date-introducing comma or `et`.
 if(volumes.length&&dates.length){const v=volumes[0],d=dates[0];if(d.start>=v.end&&/^(?:\s*à\s*|\s*[-–—/]\s*)$/.test(raw.slice(v.end,d.start)))return unsupported('ambiguous-tome-date-range','Le séparateur peut indiquer une plage de tomes ou une date. Reformulez explicitement le tome et la date.');}
 if(volumes.some(a=>near(a,/(?:\b(?:pas(?:\s+du\s+tout)?|non|jamais|hors|sauf|sans|excepté|vers|autour|probablement|peut[ -]?être|plutôt\s+que)\s+(?:(?:dans\s+)?(?:le|du)|de)?\s*|\bne\s+pense\s+pas\s+que\s+ce\s+soit\s+dans\s+le\s+)$/i,65)||/^\s*(?:\?|pas\s*(?:$|[,;.!?]|le\b|du\b)|plutôt\s+\d+)/i.test(raw.slice(a.end,a.end+19))))return unsupported('negated-or-tentative-volume','La restriction de tome semble négative ou incertaine : reformulez-la avant de la rendre obligatoire.');
 if(dates.some(a=>near(a,/(?:\b(?:pas|non|vers|autour|avant|après|entre|environ|peut[ -]?être|ou)\s*(?:(?:le|du|de)\s*)?|\bdu\s+\d{1,2}\s+au\s*)$/i,30)))return unsupported('uncertain-or-negated-date','La date est incertaine ou relative : précisez-la avant application.');
 if(monthsFound.some(a=>near(a,/\b(?:pas|non|vers|autour|avant|après|entre|environ|peut[ -]?être)\s*$/i,24)))return unsupported('uncertain-or-negated-month','Le mois est présenté comme incertain. Précisez votre intention.');
 if(years.some(a=>near(a,/(?:\b(?:pas|non|vers|autour|avant|après|entre|environ|peut[ -]?être)\s*(?:(?:de|en)\s*)?|\b(?:date|ann[ée]e)\s+(?:approximati(?:ve|f)|incertain(?:e)?)\s*)$/i,32)))return unsupported('uncertain-or-negated-year','L’année est incertaine ou relative : précisez-la avant application.');
 if(years.length>1)return unsupported('multiple-years','Plusieurs années hors alternative : précisez une seule année.');
 if((dates.length||monthsFound.length)&&years.length)return unsupported('date-with-additional-year','Date et année supplémentaire contradictoires : précisez votre recherche.');
 if(alts.length){
   const a=alts[0],isVolume=a.type==='alternative-volume';
   // `Tome 12 ou 13 février` may refer to a second tome or to the date; do not guess.
   if(isVolume&&new RegExp('^\\s+(?:'+rxMonths+')\\s+\\d{4}\\b','i').test(raw.slice(a.end)))return unsupported('ambiguous-volume-date','Le numéro après « ou » peut désigner un tome ou un jour. Réécrivez votre recherche.');
   let prefix=raw.slice(0,a.start),suffix=raw.slice(a.end);
   // `entre 1919 et 1920` / `vers 1919 ou 1920`: choosing a year also removes its uncertainty marker.
   if(!isVolume)prefix=prefix.replace(/\b(?:entre|vers|autour|environ)\s*$/i,'');
   const rep=(n)=>isVolume?`Tome ${n}`:String(n);
   const revised=(n)=>(prefix+rep(n)+suffix).replace(/\s+/g,' ').trim();
   const noRestriction=(prefix+suffix).replace(/\s+/g,' ').trim();
   const choices=[{label:`Confirmer ${isVolume?'le tome':'l’année'} ${a.left}`,query:revised(a.left),chip:null},{label:`Confirmer ${isVolume?'le tome':'l’année'} ${a.right}`,query:revised(a.right),chip:null},
     {label:isVolume?'Élargir explicitement à tous les tomes (sans cette alternative)':'Retirer explicitement la restriction d’année',query:noRestriction,chip:isVolume?{min:0,max:0}:null}];
   if(!noRestriction)choices.pop();
   return clarify(isVolume?'volume-alternative':'year-alternative','Plusieurs valeurs sont mentionnées. Choisissez celle à confirmer ou élargissez explicitement la recherche.',choices);
 }
 if(dates.some(d=>!d.valid)){
   const d=dates.find(x=>!x.valid);return clarify('invalid-date',`La date « ${d.text} » est impossible. Choisissez si vous souhaitez l’écarter.`,[{label:'Retirer uniquement la date invalide et conserver les autres critères',query:stripArticle(raw,d.start,d.end),chip:null}]);
 }
 if(refs.length&&volumes.length){const m=refs[0].value.match(/^(?:LDCSUP|LDC)\.T(\d+)(?:\.|$)/);if(m&&+m[1]!==volumes[0].value)return clarify('reference-volume-conflict',`La référence indique T${+m[1]} mais vous avez saisi T${volumes[0].value}.`,[action(volumes[0],'Conserver la référence, retirer le tome indiqué'),action(refs[0],'Conserver le tome indiqué, retirer la référence')]);}
 if(refs.length&&dates.length){const m=refs[0].value.match(/^(?:LDCSUP|LDC)\.T\d+\.(\d{4}-\d{2}-\d{2})(?:\.|$)/);if(m&&m[1]!==dates[0].iso){const d=dates[0];return clarify('reference-date-conflict',`Référence datée du ${m[1]}, mais date saisie ${d.iso}.`,[{label:'Conserver la référence et retirer uniquement la date contradictoire',query:stripArticle(raw,d.start,d.end),chip:null},action(refs[0],'Conserver la date indiquée et retirer uniquement la référence')]);}}
 if(volumes.length&&chipMin&&(structural.volume<chipMin||structural.volume>chipMax)){let v=structural.volume,g=group(v);return clarify('chip-volume-conflict',`Le tome ${v} est hors de votre filtre visible T${chipMin}–${chipMax}.`,[{label:`Adapter le filtre visible à T${g.min}–${g.max}`,query:raw,chip:g},...(action(volumes[0],'').query?[action(volumes[0],`Conserver le filtre T${chipMin}–${chipMax} et retirer le tome`)]:[])]);}
 if(refs.length&&chipMin){const m=refs[0].value.match(/^(?:LDCSUP|LDC)\.T(\d+)(?:\.|$)/);if(m&&(+m[1]<chipMin||+m[1]>chipMax)){let g=group(+m[1]);return clarify('chip-reference-conflict',`La référence est hors du filtre T${chipMin}–${chipMax}.`,[{label:`Adapter le filtre à T${g.min}–${g.max}`,query:raw,chip:g},...(action(refs[0],'').query?[action(refs[0],'Retirer uniquement la référence et conserver le filtre')]:[])]);}}
 // Semantic model only implements EXACT dateIso, not a month prefix. Do not silently request a zero-result semantic month scope.
 if(mode==='meaning'&&monthsFound.length&&!pure)return unsupported('semantic-month-prefix-unsupported','La recherche par le sens ne peut pas appliquer un filtre de mois à un souvenir descriptif. Utilisez « Par les mots » ou précisez une date exacte / année.');
 // Meaning-mode pure metadata and all Words-mode queries share the unchanged
 // lexical worker. Therefore use a single canonical encoder for structural-only
 // navigation; ISO YYYY-MM-DD is NOT a day filter in this worker.
 const monthName=['','janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];
 if(pure){
   // This construction never uses offsets; harmless navigation boilerplate is
   // removed only when the whole remaining description was judged non-semantic.
   const bits=[];
   if(structural.ref)bits.push(structural.ref);
   if(structural.volume)bits.push(`Tome ${structural.volume}`);
   if(dates.length){const d=dates[0];bits.push(`${d.day} ${monthName[d.month]} ${d.year}`);}
   else if(monthsFound.length){const d=monthsFound[0];bits.push(`${monthName[d.month]} ${d.year}`);}
   else if(structural.year)bits.push(String(structural.year));
   base.engineQuery=bits.join(' ');
 }else if(mode==='words'){
   // Mixed lexical and structural phrases: retain every word outside proved
   // structural atoms. Every replacement offset is relative to ORIGINAL raw;
   // apply it in descending order to avoid the R111 double-offset corruption.
   const replacements=[];
   for(const a of paddedTomes)replacements.push({start:a.start,end:a.end,text:a.text.replace(/(tomes?\s+)0+(\d+)/i,(_,head,n)=>head+String(Number(n)))});
   for(const a of dates)if(!new RegExp('^(?:1er|\\d{1,2})\\s+(?:'+rxMonths+')\\s+\\d{4}$','i').test(a.text))
     replacements.push({start:a.start,end:a.end,text:`${a.day} ${monthName[a.month]} ${a.year}`});
   let q=raw;
   for(const r of replacements.sort((a,b)=>b.start-a.start))q=q.slice(0,r.start)+r.text+q.slice(r.end);
   base.engineQuery=q;
 }
 // Empty or stopword-only semantic residue must not fall back to raw structural input and invoke ONNX.
 if(mode==='meaning'&&!pure&&atoms.length&&description&&!/[\p{L}\p{N}]{3,}/u.test(description))return unsupported('zero-lexical-semantic-residual','Précisez les termes mémorisés : aucun terme de passage exploitable ne subsiste.');
 return base;
}
return Object.freeze({VERSION,analyze,removeRanges,replaceRange,validDate,group});
});
