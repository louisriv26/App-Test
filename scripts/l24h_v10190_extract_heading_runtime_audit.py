from playwright.sync_api import sync_playwright
from pathlib import Path
import json,re,sys
root=Path(__file__).resolve().parent.parent
html=(root/'index.html').read_text(encoding='utf-8')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium')
 pg=b.new_page(viewport={"width":390,"height":844}, user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1')
 pg.set_content(html,wait_until='domcontentloaded')
 rows=[]
 def rec(name,ok,detail=''): rows.append({'test':name,'status':'PASS' if ok else 'FAIL','detail':detail})
 # enumerate the real heading universe from TEXT_LIBRARY in runtime
 heads=pg.evaluate("""()=>{let a=[];for(const item of TEXT_LIBRARY){if(!isIndexedLibraryText(item))continue;(item.body||[]).forEach((t,i)=>{if(isLibraryExtractHeaderLine(t))a.push({item:item.id,pid:makeLibraryParaId(item.id,i),text:t});});}return a;}""")
 rec('heading universe 94',len(heads)==94,str(len(heads)))
 rec('indexed reading universe 27',len(set(x['item'] for x in heads))==27,str(len(set(x['item'] for x in heads))))
 # all 94 DOM/target/text/Range shapes
 failures=[]
 for h in heads:
  pg.evaluate("id=>openLibraryText(id,false)",h['item'])
  r=pg.evaluate("""({pid,txt})=>{const h3=document.getElementById(pid);const s=h3&&h3.querySelector('.library-extract-heading-selectable[data-para-id]');const info=getTargetInfo(pid);if(!h3||!s||!info)return {base:false};const tn=s.firstChild;function run(kind){let r=document.createRange();if(kind==='tt'){r.setStart(tn,1);r.setEnd(tn,Math.min(12,tn.length));}if(kind==='ht'){r.setStart(h3,0);r.setEnd(tn,Math.min(12,tn.length));}if(kind==='th'){r.setStart(tn,1);r.setEnd(h3,1);}if(kind==='hh'){r.setStart(h3,0);r.setEnd(h3,1);}state._pending=null;closeContextActions({clearTarget:true,clearPending:true,clearSelection:true});let ok=setPendingSelectionFromRange(r,null,true);let bar=(document.getElementById('contextActionBar')||{}).textContent||'';return {ok,id:state._pending&&state._pending.paraId,bar};}return {base:h3.textContent===txt&&s.textContent===txt&&info.text===txt&&info.type==='library_text',tt:run('tt'),ht:run('ht'),th:run('th'),hh:run('hh')};}""",{'pid':h['pid'],'txt':h['text']})
  ok=r.get('base') and all(r[k]['ok'] and r[k]['id']==h['pid'] and all(x in r[k]['bar'] for x in ['Surligner','Note','Copier','Fermer']) for k in ['tt','ht','th','hh'])
  if not ok: failures.append({'pid':h['pid'],'r':r})
 rec('all 94 heading targets/ranges',not failures,json.dumps(failures[:3],ensure_ascii=False))
 # exact screenshot IDs
 for pid,item in [('PASSION24.TEXT.RELATED_HOUR_18.BODY.P050','PASSION24.TEXT.RELATED_HOUR_18'),('PASSION24.TEXT.PART_III_DIVINE_PASSION.BODY.P064','PASSION24.TEXT.PART_III_DIVINE_PASSION')]:
  pg.evaluate("id=>openLibraryText(id,false)",item)
  x=pg.evaluate("""pid=>{const h3=document.getElementById(pid),s=h3.querySelector('.library-extract-heading-selectable'),tn=s.firstChild;let r=document.createRange();let text=s.textContent;let needle=pid.includes('RELATED_HOUR_18')?'Être, à l’intérieur':'Jésus par la Divinité';let st=text.toLocaleLowerCase('fr').indexOf(needle.toLocaleLowerCase('fr'));if(st<0)st=3;function setByOffset(el,start,end){let walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let nodes=[],n,total=0;while(n=walker.nextNode()){nodes.push([n,total,total+n.nodeValue.length]);total+=n.nodeValue.length;}let a=nodes.find(z=>start>=z[1]&&start<=z[2]),b=nodes.find(z=>end>=z[1]&&end<=z[2]);let rr=document.createRange();rr.setStart(a[0],start-a[1]);rr.setEnd(b[0],end-b[1]);return rr;}r=setByOffset(s,st,Math.min(text.length,st+Math.max(8,needle.length)));state._pending=null;let ok=setPendingSelectionFromRange(r,null,true);return {ok,id:state._pending&&state._pending.paraId,text:state._pending&&state._pending.text,bar:(document.getElementById('contextActionBar')||{}).textContent||''};}""",pid)
  rec('screenshot target '+pid,x['ok'] and x['id']==pid and all(k in x['bar'] for k in ['Surligner','Note','Copier','Fermer']),json.dumps(x,ensure_ascii=False))
 # create/recolour/delete/undo on screenshot target through actual highlight store + rerender
 pid='PASSION24.TEXT.PART_III_DIVINE_PASSION.BODY.P064'; item='PASSION24.TEXT.PART_III_DIVINE_PASSION'
 pg.evaluate("id=>openLibraryText(id,false)",item)
 lifecycle=pg.evaluate("""pid=>{const h3=document.getElementById(pid),s=h3.querySelector('.library-extract-heading-selectable');const full=s.textContent;state.textHighlights[pid]=[];let start=full.toLowerCase().indexOf('jésus par la divinité');if(start<0)start=5;let end=Math.min(full.length,start+22);state.textHighlights[pid]=[{id:'hx',target_id:pid,target_type:'library_text',start_offset:start,end_offset:end,start:start,end:end,color:'yellow',text_hash:stableTextHash(full),paragraph_fingerprint:stableTextHash(full),para_hash:stableTextHash(full),selected_text_snapshot:full.slice(start,end),created_at:1,updated_at:1,schema_version:8}];rerenderPara(pid);let yellow=!!document.querySelector('#'+CSS.escape(pid)+' mark.hl-yellow');state.textHighlights[pid][0].color='blue';rerenderPara(pid);let blue=!!document.querySelector('#'+CSS.escape(pid)+' mark.hl-blue');let keep=document.getElementById(pid).classList.contains('library-extract-heading');let txt=document.getElementById(pid).textContent;return {yellow,blue,keep,textSame:txt===full,target:getTargetInfo(pid).text===full};}""",pid)
 rec('screenshot heading render/recolour',all(lifecycle.values()),json.dumps(lifecycle))
 # live index closure: every live button onclick anchor exists and is an extract heading target
 live=pg.evaluate("""()=>{let bad=[];for(const item of TEXT_LIBRARY){if(!isIndexedLibraryText(item))continue;openLibraryText(item.id,false);for(const b of document.querySelectorAll('.library-live-index-btn')){let m=(b.getAttribute('onclick')||'').match(/scrollToLibraryAnchor\('([^']+)'\)/);if(!m||!document.getElementById(m[1])||!document.getElementById(m[1]).classList.contains('library-extract-heading-target'))bad.push(m?m[1]:'missing');}}return bad;}""")
 rec('live index anchors close over headings',len(live)==0,json.dumps(live[:5]))
 # top title/body regressions
 pg.evaluate("openLibraryText('PASSION24.TEXT.PREFACE_ANNIBALE',false)")
 reg=pg.evaluate("""()=>{const title=document.querySelector('.library-title-selectable'),body=document.querySelector('.library-para-block .para-text');function t(el){const n=el.firstChild;let r=document.createRange();r.setStart(n,0);r.setEnd(n,Math.min(8,n.length));state._pending=null;return setPendingSelectionFromRange(r,null,false)&&!!state._pending;}return {title:t(title),body:t(body)};}""")
 rec('top title/body selection regression',reg['title'] and reg['body'],json.dumps(reg))
 # Android mode route accepts extract heading as target but native selection CSS remains disabled statically tested elsewhere
 pg.evaluate("document.documentElement.classList.add('android-scroll-fix'); openLibraryText('PASSION24.TEXT.PART_III_DIVINE_PASSION',false)")
 android=pg.evaluate("""()=>{const s=document.getElementById('PASSION24.TEXT.PART_III_DIVINE_PASSION.BODY.P064').querySelector('.library-extract-heading-selectable');return {recognized:!!getSelectableTextElementFromTarget(s),whole:stage6hPrepareAndroidParagraphPending(s),id:state._pending&&state._pending.paraId};}""")
 rec('Samsung paragraph target regression',android['recognized'] and android['whole'] and android['id']=='PASSION24.TEXT.PART_III_DIVINE_PASSION.BODY.P064',json.dumps(android))
 print(json.dumps(rows,ensure_ascii=False,indent=2))
 if any(r['status']!='PASS' for r in rows): sys.exit(1)
 b.close()
