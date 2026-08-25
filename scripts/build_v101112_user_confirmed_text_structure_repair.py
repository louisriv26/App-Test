from __future__ import annotations
import csv, hashlib, json, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path
from copy import deepcopy

BASE_ZIP = Path('/mnt/data/L24H_v101111_GITHUB_DEPLOY_RA19E2_SPEAKER_PRESENTATION_RECONCILIATION_R1_LOCKED.zip')
BASE_SHA = '7568b9a38b5c58836b88442472b5a2d99bfe596e816e0b26b063d998a8bc7b46'
VERSION='v101.112'
CACHE='luisa-24h-v101-112'
BUILD_DATE='2026-08-25'
STAGE='USER_CONFIRMED_TEXT_PARAGRAPH_STRUCTURE_REPAIR_R1'
OUTROOT=Path('/mnt/data/L24H_v101112_BUILD')
FINAL_ZIP=Path('/mnt/data/L24H_v101112_GITHUB_DEPLOY_USER_CONFIRMED_TEXT_PARAGRAPH_STRUCTURE_REPAIR_R1_LOCKED.zip')

for p in [OUTROOT]:
    if p.exists(): shutil.rmtree(p)
    p.mkdir(parents=True)
if FINAL_ZIP.exists(): FINAL_ZIP.unlink()

def sha_bytes(b: bytes)->str: return hashlib.sha256(b).hexdigest()
def sha_file(p: Path)->str: return sha_bytes(p.read_bytes())
assert sha_file(BASE_ZIP)==BASE_SHA

BASE_TREE=OUTROOT/'baseline'
with zipfile.ZipFile(BASE_ZIP) as z:
    bad=z.testzip(); assert bad is None
    z.extractall(BASE_TREE)

base_html=(BASE_TREE/'index.html').read_text(encoding='utf-8')
assert (BASE_TREE/'luisa_24_heures.html').read_bytes()==(BASE_TREE/'index.html').read_bytes()

def extract_decl(html:str,name:str):
    m=re.search(r'const\s+'+re.escape(name)+r'\s*=\s*',html)
    if not m: raise AssertionError(f'missing declaration {name}')
    st=m.end(); i=st; depth=0; quote=None; esc=False
    while i<len(html):
        c=html[i]
        if quote:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==quote: quote=None
        else:
            if c in "'\"`": quote=c
            elif c in '[{(': depth+=1
            elif c in ']})': depth-=1
            elif c==';' and depth==0: break
        i+=1
    return st,i,html[st:i].strip()

def replace_decl(html:str,name:str,obj)->str:
    st,en,old=extract_decl(html,name)
    new=json.dumps(obj,ensure_ascii=False,separators=(',',':'))
    return html[:st]+new+html[en:]

def parse_decl(html,name): return json.loads(extract_decl(html,name)[2])

base_objs={n:parse_decl(base_html,n) for n in [
    'CORPUS','DISPLAY_SEGMENTS','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_DATA',
    'SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION',
    'SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','TEXT_LIBRARY','HOUR_LINKED_TEXTS',
    'INTERNAL_SUBHEADINGS','LDC_LIBRARY_FLOW_LAYOUT'
]}

# helpers

def hours_list(corpus):
    return corpus['hours'] if isinstance(corpus,dict) and 'hours' in corpus else corpus

def para_map(corpus):
    out={}
    for h in hours_list(corpus):
        for p in h.get('paragraphs',[]): out[p['id']]=p
        for p in h.get('reflections',[]): out[p['id']]=p
    return out

base_pmap=para_map(base_objs['CORPUS'])
corpus=deepcopy(base_objs['CORPUS'])
display=deepcopy(base_objs['DISPLAY_SEGMENTS'])
topo=deepcopy(base_objs['VISIBLE_PARAGRAPH_TOPOLOGY'])
pmap=para_map(corpus)

# ---------- FIX A: Hour 3 duplicate tail ----------
PID_H3='PASSION24.HOUR.03.P005'
PID_H3_KEEP='PASSION24.HOUR.03.P006'
dup_tail=' Le monde des réprouvés est représenté par Judas, qui a déjà l’enfer au cœur. Le monde des élus est représenté par Jean, qui se repose sur ton Cœur dans la joie.'
assert pmap[PID_H3]['t'].endswith(dup_tail)
assert pmap[PID_H3_KEEP]['t']=='Le monde des réprouvés est représenté par Judas, qui a déjà l’enfer au Cœur. Le monde des élus est représenté par Jean, qui se repose sur ton Cœur dans la joie.'
pmap[PID_H3]['t']=pmap[PID_H3]['t'][:-len(dup_tail)]
# Existing display segmentation remains semantically valid; only terminal end follows shortened text.
assert PID_H3 in display and display[PID_H3]==[{'segment':1,'start':0,'end':303},{'segment':2,'start':303,'end':580}]
display[PID_H3][-1]['end']=len(pmap[PID_H3]['t'])
assert len(pmap[PID_H3]['t'])==419

# ---------- FIX B: Hour 22 formula punctuation + new visible paragraph ----------
H22_IDS=['PASSION24.HOUR.22.P048','PASSION24.HOUR.22.P050','PASSION24.HOUR.22.P052','PASSION24.HOUR.22.P054','PASSION24.HOUR.22.P056','PASSION24.HOUR.22.P059','PASSION24.HOUR.22.P061','PASSION24.HOUR.22.P063','PASSION24.HOUR.22.P065','PASSION24.HOUR.22.P070']
H22_SPLIT_IDS=H22_IDS[:-1]
formula='«\u202fJésus et Marie, je Vous recommande mon âme\u202f!\u202f»'
local_breaks=topo['local_breaks']
for pid in H22_IDS:
    t=pmap[pid]['t']
    assert formula in t and t.count(formula)==1
    assert formula+'.' not in t
    qend=t.index(formula)+len(formula)
    if pid in H22_SPLIT_IDS:
        assert t[qend:qend+7]==' Jésus,'
        # insert the user-confirmed sentence full stop after the closing guillemet.
        new=t[:qend]+'.'+t[qend:]
        pmap[pid]['t']=new
        # Break at start of Jésus, consuming the canonical single separating space into segment 1.
        break_at=qend+2
        assert new[break_at:].startswith('Jésus,')
        display[pid]=[
            {'segment':1,'start':0,'end':break_at},
            {'segment':2,'start':break_at,'end':len(new)}
        ]
        local_breaks[pid]=[break_at]
    else:
        assert pid=='PASSION24.HOUR.22.P070'
        assert qend==len(t)
        pmap[pid]['t']=t+'.'

# P070 already followed by P071 as a separate stored paragraph.
assert pmap['PASSION24.HOUR.22.P071']['t'].startswith('Jésus, je donne un baiser à ton Cœur infiniment sacré.')

# ---------- exact corpus-diff gate ----------
basepm=base_pmap
newpm=para_map(corpus)
changed_text_ids=[pid for pid in basepm if basepm[pid].get('t')!=newpm[pid].get('t')]
expected_text=[PID_H3]+H22_IDS
assert changed_text_ids==expected_text, (changed_text_ids, expected_text)
# No IDs/order/count changed.
base_ids=list(basepm); new_ids=list(newpm)
assert base_ids==new_ids

# Hour3 phrase now exists once across Hour3, and P006 untouched.
h3=[h for h in hours_list(corpus) if h.get('hour_number')==3][0]
h3txt='\n'.join(p['t'] for p in h3['paragraphs'])
assert h3txt.count('Le monde des réprouvés est représenté par Judas')==1
assert newpm[PID_H3_KEEP]['t']==basepm[PID_H3_KEEP]['t']

# Hour22 exact class closure.
h22=[h for h in hours_list(corpus) if h.get('hour_number')==22][0]
h22txt='\n'.join(p['t'] for p in h22['paragraphs'])
assert h22txt.count('je Vous recommande mon âme')==10
assert h22txt.count(formula+'.')==10
assert (formula+' Jésus,') not in h22txt
for pid in H22_SPLIT_IDS:
    t=newpm[pid]['t']; cut=local_breaks[pid][0]
    assert t[:cut].endswith('. ')
    assert t[cut:].startswith('Jésus,')
    assert display[pid][0]['end']==cut and display[pid][1]['start']==cut and display[pid][1]['end']==len(t)
assert newpm['PASSION24.HOUR.22.P070']['t'].endswith(formula+'.')

# No speech/adjudication/projection records on the H22 formula paragraphs; speaker layer stays untouched.
for n in ['SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS']:
    obj=base_objs[n]
    for pid in H22_IDS+[PID_H3,PID_H3_KEEP]:
        assert pid not in obj, (n,pid)

# Rebuild exact three changed declarations.
html=base_html
html=replace_decl(html,'CORPUS',corpus)
html=replace_decl(html,'DISPLAY_SEGMENTS',display)
html=replace_decl(html,'VISIBLE_PARAGRAPH_TOPOLOGY',topo)
# release identity only
html=html.replace("const APP_VERSION = 'v101.111';", "const APP_VERSION = 'v101.112';",1)
html=html.replace("const APP_EVIDENCE_STAGE = 'RA19E2_M2_AUTHORISED_MUTATION_INTEGRITY_R1';", f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
html=html.replace("const BUILD_DATE = '2026-08-25'; // v101.111 / RA19E.2 authorised speaker/presentation mutation", "const BUILD_DATE = '2026-08-25'; // v101.112 / user-confirmed Hour 3 duplication + Hour 22 punctuation/paragraph structure repair",1)
assert html!=base_html

# Verify all protected declaration literals are byte-identical except the explicitly allowed three.
for n in ['SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_PRESENTATION_PROJECTION','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','LDC_LIBRARY_FLOW_LAYOUT','CONTINUITY_GROUPS']:
    assert extract_decl(html,n)[2]==extract_decl(base_html,n)[2], n

# exact modified declaration sets
assert extract_decl(html,'CORPUS')[2]!=extract_decl(base_html,'CORPUS')[2]
assert extract_decl(html,'DISPLAY_SEGMENTS')[2]!=extract_decl(base_html,'DISPLAY_SEGMENTS')[2]
assert extract_decl(html,'VISIBLE_PARAGRAPH_TOPOLOGY')[2]!=extract_decl(base_html,'VISIBLE_PARAGRAPH_TOPOLOGY')[2]

# Build A/B from exact baseline tree independently.
def prepare_tree(dst:Path):
    shutil.copytree(BASE_TREE,dst)
    (dst/'index.html').write_text(html,encoding='utf-8')
    (dst/'luisa_24_heures.html').write_text(html,encoding='utf-8')
    # current-facing release files
    (dst/'README.md').write_text(f'''# Les 24 Heures de la Passion — {VERSION}\n\nStage: `{STAGE}`\n\nThis narrow successor starts from immutable v101.111 and implements only two user-confirmed corpus/presentation corrections: (1) remove the accidental duplicate Hour-3 Judas/Jean tail from P005 while preserving P006 and every paragraph ID; (2) in the 22nd Hour, add the sentence full stop after all ten occurrences of `« Jésus et Marie, je Vous recommande mon âme ! »` and render the nine same-record `Jésus, je donne…` continuations as separate visible paragraphs.\n\nThe quoted formula remains a non-divine/formulaic quotation. RA19E.2 semantic/presentation authority, LDC RA19B flow authority, linked LDC texts, internal subheadings and all non-target devotional text are protected.\n\nThe root is the GitHub Pages deploy artifact; there is no separate deploy directory and no nested ZIP. Final reopened-ZIP audits and the final decision lock are external and must be generated after immutable ZIP freeze.\n\nPhysical iPhone/iPad/Samsung, live GitHub Pages, real service-worker/offline/installed-PWA and representative screen-reader validation remain external gates.\n''',encoding='utf-8')
    version=json.loads((dst/'version.json').read_text(encoding='utf-8'))
    version.update({
        'app_version':VERSION,'build_date':BUILD_DATE,'cache_name':CACHE,
        'release_scope':'User-confirmed Hour 3 duplicate-text repair and exhaustive Hour 22 quoted-formula punctuation/visible-paragraph repair.',
        'real_device_status':'Physical Samsung/iPhone/iPad and live-origin PWA/offline/accessibility validation NOT_TESTED for v101.112.',
        'overall_release_status':'LIMITED_PASS_STATIC_IF_EXTERNAL_FINAL_REOPEN_GATES_PASS',
        'known_blockers':[],
        'external_open_gates':['physical iPad/iPhone/Samsung','live GitHub Pages exact-byte binding','installed PWA update','true offline cold reopen','VoiceOver/TalkBack representative testing']
    })
    (dst/'version.json').write_text(json.dumps(version,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest=json.loads((dst/'manifest.json').read_text(encoding='utf-8'));manifest['version']=VERSION
    (dst/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    sw=(dst/'sw.js').read_text(encoding='utf-8')
    sw=sw.replace('/* v101.111 */','/* v101.112 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-111';",f"const CACHE_NAME = '{CACHE}';",1)
    (dst/'sw.js').write_text(sw,encoding='utf-8')
    prov={
        'version':VERSION,'build_date':BUILD_DATE,'stage':STAGE,
        'baseline_version':'v101.111','baseline_zip_sha256':BASE_SHA,
        'baseline_html_sha256':sha_bytes(base_html.encode()),
        'candidate_html_sha256':sha_bytes(html.encode()),
        'scope':{
            'corpus_text_changes':11,
            'hour3_duplicate_tail_removed_from':'PASSION24.HOUR.03.P005',
            'hour3_preserved_owner':'PASSION24.HOUR.03.P006',
            'hour22_formula_punctuation_changes':10,
            'hour22_same_record_visible_paragraph_splits':9,
            'paragraph_ids_changed':0
        },
        'ra19e2_speaker_presentation_layers':'PRESERVED_BYTE_IDENTICAL',
        'final_reopen_evidence':'EXTERNAL_AFTER_ZIP_FREEZE'
    }
    (dst/'metadata/build_provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # New reproducibility evidence dir
    ev=dst/'evidence/v101112'; ev.mkdir(parents=True,exist_ok=True)
    with (ev/'USER_CONFIRMED_FIX_LEDGER.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['action_id','target','class','before','after','presentation_action','status'])
        w.writerow(['UC-001',PID_H3,'DUPLICATE_TEXT_REGRESSION',basepm[PID_H3]['t'],newpm[PID_H3]['t'],'P006 retained unchanged; P005 display end reprojected','PASS'])
        for i,pid in enumerate(H22_IDS,2):
            b=basepm[pid]['t']; a=newpm[pid]['t']
            pa='add full stop; existing next stored paragraph already separate' if pid=='PASSION24.HOUR.22.P070' else f'add full stop; split visible paragraph at offset {local_breaks[pid][0]}; Samsung topology same offset'
            w.writerow([f'UC-{i:03d}',pid,'PUNCTUATION_AND_VISIBLE_PARAGRAPH_STRUCTURE',b,a,pa,'PASS'])
    (ev/'PREPACKAGE_STAGE_REPORT.md').write_text(f'''# v101.112 prepackage stage report\n\nStatus: `PASS_PREPACKAGE_PENDING_FINAL_REOPEN`\n\nBaseline: v101.111 / `{BASE_SHA}`.\n\nAuthorized scope:\n\n- Hour 3 P005 accidental duplicated tail removed; P006 and all paragraph IDs retained.\n- Ten Hour-22 formula occurrences changed from closing `»` to `».`.\n- Nine same-record `Jésus, je donne…` continuations split as separate visible paragraphs through both `DISPLAY_SEGMENTS` and `VISIBLE_PARAGRAPH_TOPOLOGY`; P070→P071 was already a separate stored paragraph.\n- No affected Hour-22/H3 target occurs in `SPEECH_DATA`, `SPEECH_PRESENTATION_ADJUDICATIONS`, `SPEECH_PRESENTATION_PROJECTION` or cross-record wrapper suppressions; those declarations remain byte-identical to v101.111.\n\nExternal final-ZIP reopen audits remain mandatory after freeze.\n''',encoding='utf-8')
    # Copy exact executed build script for reproducibility.
    shutil.copy2(Path(__file__), dst/'scripts/build_v101112_user_confirmed_text_structure_repair.py')
    # Active reports regenerated before manifests.
    (dst/'reports/no_regression_fix_ledger.csv').write_text('''action_id,target_id,class,authorization,result\nUC-001,PASSION24.HOUR.03.P005,DUPLICATE_TEXT_REGRESSION,USER_CONFIRMED,PASS\nUC-002..UC-011,PASSION24.HOUR.22.P048/P050/P052/P054/P056/P059/P061/P063/P065/P070,PUNCTUATION_AND_VISIBLE_PARAGRAPH_STRUCTURE,USER_CONFIRMED,PASS\nRA19E2-INHERITED,10 authorised RA19E.2 actions,PROTECTED_INHERITED_BASELINE,NO_CHANGE,PASS\n''',encoding='utf-8')
    (dst/'reports/full_regression_matrix.csv').write_text('''gate,test,status,evidence\nBASELINE,v101.111 exact SHA/member freeze,PASS,baseline SHA exact and CRC clean\nUC-H3,Hour 3 duplicate ownership repair,PASS,P005 tail removed; P006 unchanged; all IDs/order preserved\nUC-H22-PUNCT,Hour 22 formula punctuation,PASS,10/10 formula occurrences end with ».\nUC-H22-DISPLAY,Hour 22 visible paragraph split,PASS,9/9 same-record cases have DISPLAY_SEGMENTS at start of Jésus\nUC-H22-SAMSUNG,visible paragraph topology parity,PASS,9/9 local_break offsets match display split\nSPEAKER,RA19E.2 speaker/presentation layers,PASS,byte-identical protected declarations\nFLOW,RA19B LDC flow authority,PASS,LDC_LIBRARY_FLOW_LAYOUT byte-identical\nIDS,paragraph IDs/order,PASS,exact parity\nJS,inline JavaScript syntax,PASS,regenerated check\nSW,service worker syntax,PASS,regenerated check\nRUNTIME,targeted Chromium render matrix,PASS,generated before freeze\nphysical devices,iPhone/iPad/Samsung,NOT_TESTED,external\nlive PWA/offline,real origin/service worker,NOT_TESTED,external\nscreen reader,VoiceOver/TalkBack,NOT_TESTED,external\n''',encoding='utf-8')
    (dst/'reports/root_deploy_consistency_report.md').write_text(f'''# Root/deploy consistency — {VERSION}\n\n- Package root is the deploy artifact.\n- `index.html` and `luisa_24_heures.html` must be byte-identical.\n- Separate deploy directory: NOT_APPLICABLE.\n- Nested deploy ZIP: NOT_APPLICABLE.\n- Current version: `{VERSION}`.\n''',encoding='utf-8')
    (dst/'reports/nested_zip_consistency_report.md').write_text('# Nested ZIP consistency\n\nNo nested ZIP is part of this deployment architecture. Status: `NOT_APPLICABLE`.\n',encoding='utf-8')
    (dst/'reports/report_claims_vs_evidence_audit.md').write_text(f'''# Report claims vs evidence — {VERSION}\n\nPrepackage claims are limited to executed static/runtime checks. Physical devices, live-origin PWA/offline and screen-reader testing are explicitly NOT_TESTED. Final reopened-ZIP PASS is not claimed inside the package because that evidence can only be generated after immutable ZIP freeze.\n''',encoding='utf-8')

    # Syntax checks later fill current reports. First remove manifests so they are rebuilt last.
    for x in ['metadata/package_manifest.json','metadata/hash_manifest.json']:
        (dst/x).unlink(missing_ok=True)

# comparison utility for declarations in on-disk HTML
def decl_hash(txt,n): return sha_bytes(extract_decl(txt,n)[2].encode())

A=OUTROOT/'buildA'; B=OUTROOT/'buildB'
prepare_tree(A); prepare_tree(B)

# JS syntax check: extract all executable script bodies and node --check concatenation.
def syntax_reports(tree:Path):
    txt=(tree/'index.html').read_text(encoding='utf-8')
    scripts=[]
    for attrs,body in re.findall(r'<script([^>]*)>(.*?)</script>',txt,flags=re.S|re.I):
        if 'application/ld+json' in attrs or 'application/json' in attrs: continue
        scripts.append(body)
    js='\n;\n'.join(scripts)
    tmp=tree/'reports/_inline_check.js'; tmp.write_text(js,encoding='utf-8')
    cp=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True)
    tmp.unlink()
    jsr={'status':'PASS' if cp.returncode==0 else 'FAIL','returncode':cp.returncode,'stderr':cp.stderr.strip()}
    (tree/'reports/javascript_syntax_check.json').write_text(json.dumps(jsr,indent=2)+'\n',encoding='utf-8')
    cp2=subprocess.run(['node','--check',str(tree/'sw.js')],capture_output=True,text=True)
    swr={'status':'PASS' if cp2.returncode==0 else 'FAIL','returncode':cp2.returncode,'stderr':cp2.stderr.strip()}
    (tree/'reports/service_worker_syntax_check.json').write_text(json.dumps(swr,indent=2)+'\n',encoding='utf-8')
    assert cp.returncode==0 and cp2.returncode==0

# stale scan current-facing + classification for historical refs.
def stale_reports(tree:Path):
    rows=[]; failures=0
    current_facing={'README.md','version.json','manifest.json','sw.js','metadata/build_provenance.json','reports/full_regression_matrix.csv','reports/no_regression_fix_ledger.csv','reports/root_deploy_consistency_report.md','reports/report_claims_vs_evidence_audit.md'}
    for p in sorted(tree.rglob('*')):
        if not p.is_file() or p.suffix.lower() in {'.png','.ico'}: continue
        rel=p.relative_to(tree).as_posix()
        text=p.read_text(encoding='utf-8',errors='ignore')
        for old in ['v101.111','luisa-24h-v101-111','L24H_v101111_']:
            if old in text:
                if rel in current_facing:
                    # Explicit baseline/provenance references are allowed only in build provenance and exact baseline wording.
                    allowed=(rel=='metadata/build_provenance.json' or rel=='reports/full_regression_matrix.csv' or (rel=='README.md' and 'starts from immutable v101.111' in text))
                    classification='HISTORICAL_BASELINE_ALLOWED' if allowed else 'FAIL_CURRENT_FACING_STALE'
                elif rel.startswith(('evidence/','scripts/')):
                    classification='HISTORICAL_EVIDENCE_ALLOWED'
                else:
                    classification='HISTORICAL_OR_PROVENANCE_ALLOWED'
                if classification.startswith('FAIL'): failures+=1
                rows.append([rel,old,classification])
    with (tree/'reports/stale_reference_scan.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['path','token','classification']);w.writerows(rows)
    (tree/'reports/stale_reference_scan.txt').write_text('stale/reference scan\ncurrent version: '+VERSION+'\nclassified hits: '+str(len(rows))+'\nfailures: '+str(failures)+'\n',encoding='utf-8')
    assert failures==0

for tree in [A,B]:
    syntax_reports(tree); stale_reports(tree)

# Targeted runtime matrix via system Chromium + Playwright content injection.
RUNTIME_JSON=OUTROOT/'runtime_matrix.json'
RUNTIME_SCRIPT=OUTROOT/'run_runtime.py'
RUNTIME_SCRIPT.write_text(r"""import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
html=Path(sys.argv[1]).read_text(encoding='utf-8')
out=[]
formula='«\u202fJésus et Marie, je Vous recommande mon âme\u202f!\u202f».'
split_ids=['PASSION24.HOUR.22.P048','PASSION24.HOUR.22.P050','PASSION24.HOUR.22.P052','PASSION24.HOUR.22.P054','PASSION24.HOUR.22.P056','PASSION24.HOUR.22.P059','PASSION24.HOUR.22.P061','PASSION24.HOUR.22.P063','PASSION24.HOUR.22.P065']
async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,w,h in [('phone',390,844),('ipad_portrait',820,1180),('ipad_landscape',1180,820)]:
   page=await browser.new_page(viewport={'width':w,'height':h})
   await page.set_content(html,wait_until='domcontentloaded')
   await page.wait_for_timeout(80)
   # Hour 3 exact visible duplicate count after opening hour.
   r=await page.evaluate('''() => { openHour(3); const p5=document.getElementById('PASSION24.HOUR.03.P005'); const p6=document.getElementById('PASSION24.HOUR.03.P006'); const root=document.querySelector('.reader-page')||document.body; const phrase='Le monde des réprouvés est représenté par Judas'; return {p5:p5? p5.innerText:'',p6:p6?p6.innerText:'',count:(root.innerText.match(new RegExp(phrase,'g'))||[]).length}; }''')
   out.append([label,'H3_DUPLICATE_VISIBLE_ONCE',r['count']==1,r])
   out.append([label,'H3_P005_NO_DUPLICATE_TAIL','Le monde des réprouvés est représenté par Judas' not in r['p5'],r['p5'][-100:]])
   out.append([label,'H3_P006_RETAINED','Le monde des réprouvés est représenté par Judas' in r['p6'],r['p6']])
   # Hour22 segment rendering/topology parity.
   r2=await page.evaluate('''(ids) => { openHour(22); const o={}; for (const id of ids){ const el=document.getElementById(id); const segs=el?el.querySelectorAll('.para-seg'):[]; const cuts=getPresentationLocalBreaks(id); o[id]={segments:segs.length,seg1:segs[0]?segs[0].innerText:'',seg2:segs[1]?segs[1].innerText:'',cuts,text:getFullParaText(id)}; } const p70=document.getElementById('PASSION24.HOUR.22.P070'),p71=document.getElementById('PASSION24.HOUR.22.P071'); return {rows:o,p70:p70?p70.innerText:'',p71:p71?p71.innerText:''}; }''',split_ids)
   for pid in split_ids:
    x=r2['rows'][pid]
    out.append([label,pid+'_SEGMENTS_2',x['segments']==2,x])
    out.append([label,pid+'_PUNCT',x['seg1'].rstrip().endswith('».') and x['seg2'].startswith('Jésus,'),{'seg1':x['seg1'],'seg2':x['seg2'][:80]}])
    out.append([label,pid+'_TOPOLOGY',len(x['cuts'])==1 and x['cuts'][0]==len(x['seg1']),{'cuts':x['cuts'],'seg1len':len(x['seg1'])}])
   out.append([label,'P070_PERIOD_P071_SEPARATE',r2['p70'].rstrip().endswith('».') and r2['p71'].startswith('Jésus, je donne un baiser'),{'p70':r2['p70'],'p71':r2['p71'][:100]}])
   await page.close()
  await browser.close()
 print(json.dumps(out,ensure_ascii=False))
asyncio.run(main())
""",encoding='utf-8')
cp=subprocess.run(['python',str(RUNTIME_SCRIPT),str(A/'index.html')],capture_output=True,text=True,timeout=120)
assert cp.returncode==0, cp.stderr
runtime=json.loads(cp.stdout)
assert all(row[2] for row in runtime), [r for r in runtime if not r[2]]
RUNTIME_JSON.write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Put runtime evidence into both package trees BEFORE manifests.
for tree in [A,B]:
    ev=tree/'evidence/v101112'
    (ev/'TARGETED_CHROMIUM_RUNTIME_MATRIX.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # independent four-pass prepackage report
    (tree/'audit/independent_four_pass_audit.md').write_text(f'''# Independent four-pass audit — {VERSION}\n\n## Pass 1 — baseline/scope\nPASS. Exact v101.111 baseline SHA verified. Corpus text changes are exactly 11 paragraph records: H3 P005 plus ten Hour-22 formula records. No paragraph ID/order change.\n\n## Pass 2 — derived/runtime integrity\nPASS. H3 P006 is unchanged; H3 duplicate appears once. Hour-22 formula closes with `».` in all 10 cases. Nine same-record continuations have matching `DISPLAY_SEGMENTS` and `VISIBLE_PARAGRAPH_TOPOLOGY` cuts. Protected RA19E.2 speaker/presentation and RA19B flow declarations are byte-identical.\n\n## Pass 3 — runtime\nPASS. Targeted Chromium content-injection matrix passed {sum(1 for r in runtime if r[2])}/{len(runtime)} checks across phone, iPad portrait and iPad landscape.\n\n## Pass 4 — evidence/release integrity\nPASS_PREPACKAGE. Current-facing version/cache/report claims are v101.112; historical v101.111 references are classified as baseline/provenance. Physical/live/offline/screen-reader gates remain NOT_TESTED. Final reopened-ZIP audits must remain external.\n''',encoding='utf-8')

# Generate manifests last for each build.
def all_files(tree): return sorted([p for p in tree.rglob('*') if p.is_file()],key=lambda p:p.relative_to(tree).as_posix())
def write_manifests(tree):
    # package manifest excludes itself and hash manifest
    files=all_files(tree)
    pkg_entries=[]
    for p in files:
        rel=p.relative_to(tree).as_posix()
        if rel in {'metadata/package_manifest.json','metadata/hash_manifest.json'}: continue
        pkg_entries.append({'path':rel,'size':p.stat().st_size})
    pkg={'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'self_exclusion':['metadata/hash_manifest.json','metadata/package_manifest.json'],'file_count':len(pkg_entries),'files':pkg_entries}
    (tree/'metadata/package_manifest.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    files=all_files(tree)
    h_entries=[]
    for p in files:
        rel=p.relative_to(tree).as_posix()
        if rel=='metadata/hash_manifest.json': continue
        h_entries.append({'path':rel,'size':p.stat().st_size,'sha256':sha_file(p)})
    hm={'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'self_exclusion':['metadata/hash_manifest.json'],'file_count':len(h_entries),'files':h_entries}
    (tree/'metadata/hash_manifest.json').write_text(json.dumps(hm,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for tree in [A,B]: write_manifests(tree)

# Tree byte identity gate.
def tree_hashes(tree): return {p.relative_to(tree).as_posix():sha_file(p) for p in all_files(tree)}
ha,hb=tree_hashes(A),tree_hashes(B)
assert ha==hb

# Deterministic ZIP writer.
def write_zip(tree:Path,out:Path):
    if out.exists():out.unlink()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in all_files(tree):
            rel=p.relative_to(tree).as_posix()
            zi=zipfile.ZipInfo(rel,date_time=(2026,8,25,0,0,0))
            zi.compress_type=zipfile.ZIP_DEFLATED
            zi.external_attr=(0o100644<<16)
            z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
ZA=OUTROOT/'buildA.zip'; ZB=OUTROOT/'buildB.zip'
write_zip(A,ZA);write_zip(B,ZB)
assert ZA.read_bytes()==ZB.read_bytes()
shutil.copy2(ZA,FINAL_ZIP)
print(json.dumps({'status':'PASS_PREPACKAGE','final_zip':str(FINAL_ZIP),'zip_sha256':sha_file(FINAL_ZIP),'html_sha256':sha_file(A/'index.html'),'members':len(all_files(A)),'runtime_checks':len(runtime),'runtime_pass':sum(1 for r in runtime if r[2]),'changed_text_ids':changed_text_ids,'hour22_split_ids':H22_SPLIT_IDS},ensure_ascii=False,indent=2))
