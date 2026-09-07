#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib,re,zipfile,tempfile,shutil

CAND=Path(sys.argv[1]); BASE_ZIP=Path(sys.argv[2]); OUT=Path(sys.argv[3])
EXPECTED_BASE_SHA='d2614307d3335d4e76a3b9559cb4d8267549b9a5a4adf4ec616344f2b98664d6'
EXPECTED_VERSION='v101.128'; EXPECTED_STAGE='MEDITEE_RECOVERY_ACCESS_AND_SINGLE_STATE_SYNC_R1'
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY','VISIBLE_PARAGRAPH_TOPOLOGY']

def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def extract_const_raw(text,name):
 marker=f'const {name} = '; st=text.index(marker)+len(marker)
 try:
  dec=json.JSONDecoder();obj,end=dec.raw_decode(text[st:]);return text[st:st+end]
 except json.JSONDecodeError:
  en=text.index(';',st);return text[st:en]
def extract_function(text,name):
 pat=re.compile(r'function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{')
 m=pat.search(text)
 if not m: return None
 i=m.end()-1; depth=0; q=None; esc=False; template_depth=[]
 # Practical JS brace scanner with strings/comments/template awareness sufficient for current functions.
 j=i
 in_line=False; in_block=False
 while j < len(text):
  ch=text[j]; nxt=text[j+1] if j+1<len(text) else ''
  if in_line:
   if ch=='\n': in_line=False
   j+=1; continue
  if in_block:
   if ch=='*' and nxt=='/': in_block=False; j+=2; continue
   j+=1; continue
  if q:
   if esc: esc=False
   elif ch=='\\': esc=True
   elif ch==q: q=None
   j+=1; continue
  if ch=='/' and nxt=='/': in_line=True; j+=2; continue
  if ch=='/' and nxt=='*': in_block=True; j+=2; continue
  if ch in ('"',"'"): q=ch; j+=1; continue
  # Treat template literals as ordinary string here; current protected functions don't need nested ${} parsing for equality use.
  if ch=='`':
   k=j+1; escaped=False
   while k<len(text):
    if escaped: escaped=False
    elif text[k]=='\\': escaped=True
    elif text[k]=='`': break
    k+=1
   j=k+1; continue
  if ch=='{': depth+=1
  elif ch=='}':
   depth-=1
   if depth==0:return text[m.start():j+1]
  j+=1
 return None

rows=[]
def add(name,ok,detail=None):rows.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':detail})
add('baseline_sha',sha(BASE_ZIP)==EXPECTED_BASE_SHA,sha(BASE_ZIP))
with zipfile.ZipFile(BASE_ZIP) as z:
 add('baseline_zip_integrity',z.testzip() is None)
 add('baseline_member_count',sum(not i.is_dir() for i in z.infolist())==440,sum(not i.is_dir() for i in z.infolist()))
 td=Path(tempfile.mkdtemp(prefix='v101128_scope_')); z.extractall(td)
base=(td/'index.html').read_text(encoding='utf-8'); cand=(CAND/'index.html').read_text(encoding='utf-8')
add('deploy_html_mirror',(CAND/'luisa_24_heures.html').read_text(encoding='utf-8')==cand)
add('version_identity',"const APP_VERSION = 'v101.128';" in cand)
add('stage_identity',"const APP_EVIDENCE_STAGE = 'MEDITEE_RECOVERY_ACCESS_AND_SINGLE_STATE_SYNC_R1';" in cand)
for n in PROTECTED:
 try:add('protected_'+n,extract_const_raw(base,n)==extract_const_raw(cand,n))
 except Exception as e:add('protected_'+n,False,str(e))
# Storage-key universe remains exact.
keypat=re.compile(r"['\"](lp24_[A-Za-z0-9_]+)['\"]")
bkeys=sorted(set(keypat.findall(base))); ckeys=sorted(set(keypat.findall(cand)))
add('storage_key_universe_unchanged',bkeys==ckeys,{'added':sorted(set(ckeys)-set(bkeys)),'removed':sorted(set(bkeys)-set(ckeys))})
# Core progression/resume functions remain byte-identical.
for fn in ['getCompletedHourNumbers','getProgressSnapshot','buildHour24CyclePanel','refreshHourEndCycleUI','restoreSavedParaForHour','openHour','commitDurableChange','persistPersonalSnapshot']:
 add('function_unchanged_'+fn,extract_function(base,fn)==extract_function(cand,fn))
mark=extract_function(cand,'markMeditee') or ''
add('markMeditee_single_sync_call',mark.count('refreshMediteeControls(n)')==1,mark[-500:])
add('markMeditee_no_renderReader','renderReader(' not in mark)
add('markMeditee_still_single_state',mark.count('state.readHours')>=3 and 'topMeditatedState' not in mark and 'bottomMeditatedState' not in mark)
bmb=extract_function(cand,'buildMarkBar') or ''
add('buildMarkBar_active',"return '';" not in bmb and 'data-meditee-role="recovery"' in bmb)
rf=extract_function(cand,'refreshMediteeControls') or ''
add('refresh_helper_projection_only','state.readHours.has' in rf and 'commitDurableChange' not in rf and 'saveState(' not in rf and 'renderReader(' not in rf)
add('top_and_bottom_data_roles',cand.count('data-meditee-role="recovery"')>=1 and cand.count('data-meditee-role="primary-end"')>=1)
add('aria_pressed_present',cand.count('aria-pressed=')>=2)
# No sticky/fixed on mark bar/button blocks.
css='\n'.join(re.findall(r'\.mark-(?:bar|btn)[^{]*\{[^}]*\}',cand,re.S))
add('mark_controls_not_fixed_or_sticky',not re.search(r'position\s*:\s*(?:fixed|sticky)',css,re.I),css[:1500])
# Version schema invariants.
v=json.loads((CAND/'version.json').read_text(encoding='utf-8'))
add('storage_schema_8',v.get('storage_schema')==8,v.get('storage_schema'))
add('personal_snapshot_5',v.get('personal_snapshot')==5,v.get('personal_snapshot'))
add('version_json_v101128',v.get('app_version')==EXPECTED_VERSION,v.get('app_version'))
add('cache_v101128',v.get('cache_name')=='luisa-24h-v101-128',v.get('cache_name'))
# Exact known predecessor glyph-flow CSS retained.
needle='.continuity-flow-surface .continuity-leader .para-text > .para-seg:last-child'
add('v101127_glyph_flow_css_retained',needle in cand)
# v101126 textual known repairs remain present as a sanity control.
add('delices_visuelles_retained','délices visuelles' in cand)
summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps({'schema':'L24H_V101128_STATIC_SCOPE_AUDIT_V1','version':EXPECTED_VERSION,'stage':EXPECTED_STAGE,'summary':summary,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary));shutil.rmtree(td,ignore_errors=True)
if summary['fail']:raise SystemExit(2)
