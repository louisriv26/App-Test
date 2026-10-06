const fs=require('fs'),path=require('path');
const root=process.argv[2]; if(!root) throw new Error('target root missing');
global.fetch=async p=>{const f=path.join(root,String(p));return fs.existsSync(f)?{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(f,'utf8'))}:{ok:false,status:404,json:async()=>null};};
const mod=require(path.join(root,'pls_sparse_owner_v1423.js'));
const cases=[
["La volonté de Dieu et la volonté de l'homme peuvent être comme deux bâtons de la croix. Quand la volonté des hommes est alignée sur la volonté de Dieu, les deux poteaux de la croix sont alignés, donc il n'y a plus de croix. Voilà, donc ça serait un texte que je demanderais de chercher en disant cela.",'ldc_t11_1913_11_18_e001',9],
["Deuxième, il ne faut pas regarder le passé. Le passé est passé et il faut vivre dans le présent. Ce n'est pas utile du tout de regarder dans le passé. C'est un affront à Jésus. C'est le deuxième texte.",'ldc_t09_1909_11_02_e001',7],
["Un troisième texte, la potence de garder le silence. Plus quelqu'un est proche de Dieu et en Dieu, plus il veut rester à l'intérieur de lui et garder le silence. Plus il parle, plus c'est qu'il est vide de Dieu. Voilà un troisième texte.",'ldc_t09_1909_05_08_e001',1]
];
(async()=>{const got=[];for(const [q,t,exp] of cases){const r=await mod.search(q);const rank=r.results.findIndex(x=>x.entry_id===t)+1;if(rank!==exp)throw new Error(`rank mismatch ${t}: ${rank} != ${exp}`);got.push(rank);}console.log(JSON.stringify({status:'PASS',ranks:got,engine:mod.VERSION}));})().catch(e=>{console.error(e);process.exit(1)});
