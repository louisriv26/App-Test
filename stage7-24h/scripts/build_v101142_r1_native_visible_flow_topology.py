#!/usr/bin/env python3
from pathlib import Path
import zipfile, hashlib, json, shutil, re, sys, difflib

VERSION='v101.142'; REV='R1'; STAGE='NATIVE_VISIBLE_FLOW_TOPOLOGY_SUCCESSOR_R1'; DATE='2026-09-09'; CACHE='luisa-24h-v101-142-r1'
BASE_VERSION='v101.141 R1'; BASE_SHA='a9e86b31ee0a117cad6de6578b772e7c57cdb948dd2dc2b935b1f82c4c8299a4'
PROPOSAL_SHA='d50bd78e917e77d226eca30d8df625538496ef1625630b9c3d16fb753e0ade05'
PROTECTED_CONSTS=['CORPUS','TEXT_LIBRARY','SPEECH_DATA','SPEECH_PRESENTATION_PROJECTION','DISPLAY_SEGMENTS','VISIBLE_PARAGRAPH_TOPOLOGY','LDC_LIBRARY_FLOW_LAYOUT','INTERNAL_SUBHEADINGS','CONTINUITY_GROUPS','HOUR_LINKED_TEXTS','PASSION24_RELATED_BY_HOUR']

GROUPS = [
  {'id':'NATIVE_FLOW.H14.MOTHER_ENCOUNTER.R3','members':[('PASSION24.HOUR.14.P008',716,954,'DISPLAY_SEGMENT_3_ONLY'),('PASSION24.HOUR.14.P009',0,184,'FULL_RECORD'),('PASSION24.HOUR.14.P010',0,152,'FULL_RECORD'),('PASSION24.HOUR.14.P011',0,161,'FULL_RECORD')], 'joiner':' '},
  {'id':'NATIVE_FLOW.H18.MOTHER_ENCOUNTER.R3','members':[('PASSION24.HOUR.18.P055',0,259,'FULL_RECORD'),('PASSION24.HOUR.18.P056',0,283,'FULL_RECORD')], 'joiner':' '},
  {'id':'NATIVE_FLOW.H18.MARY_SOUL_ACTION.R3','members':[('PASSION24.HOUR.18.P062',0,119,'FULL_RECORD'),('PASSION24.HOUR.18.P063',0,245,'FULL_RECORD')], 'joiner':' '},
  {'id':'NATIVE_FLOW.H22.SIXTH_WORD_SYMPTOMS.R3','members':[('PASSION24.HOUR.22.P019',0,211,'FULL_RECORD'),('PASSION24.HOUR.22.P020',0,272,'FULL_RECORD')], 'joiner':' '},
]


def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def files(root):
    root=Path(root); return {p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc')}

def writej(path,obj):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

def exact_replace(s,old,new,label):
    n=s.count(old)
    assert n==1,(label,n)
    return s.replace(old,new,1)

def raw_const(text,name):
    marker='const '+name+' = '
    i=text.find(marker)
    if i<0:
        marker='const '+name+'='
        i=text.find(marker)
    assert i>=0,name
    start=i+len(marker)
    while start<len(text) and text[start].isspace(): start+=1
    if text[start] in '[{':
        stack=[]; ins=None; esc=False; pairs={'{':'}','[':']'}
        for j in range(start,len(text)):
            ch=text[j]
            if ins:
                if esc: esc=False
                elif ch=='\\': esc=True
                elif ch==ins: ins=None
                continue
            if ch in "'\"`": ins=ch; continue
            if ch in pairs: stack.append(pairs[ch])
            elif ch in ']}':
                assert stack and ch==stack[-1],(name,j,ch); stack.pop()
                if not stack: return text[start:j+1]
        raise AssertionError(('unterminated',name))
    j=text.find(';',start); assert j>=0,name
    return text[start:j]

def freeze(root,zp):
    root=Path(root); zp=Path(zp); zp.unlink(missing_ok=True)
    with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(root.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.name.endswith('.pyc'): continue
            rel=p.relative_to(root).as_posix()
            info=zipfile.ZipInfo(rel,(2026,9,9,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.create_system=3; info.external_attr=(0o100644<<16); info.flag_bits|=0x800
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(zp) as z: assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
    return sha_file(zp)

def js_groups():
    arr=[]
    for g in GROUPS:
        arr.append({'group_id':g['id'],'members':[{'paragraph_id':m[0],'start':m[1],'end':m[2],'scope':m[3]} for m in g['members']],'joiner':g['joiner']})
    return json.dumps(arr,ensure_ascii=False,separators=(',',':'))

INSERT_AFTER_CONTINUITY = r'''function getContinuityJoinedText(paraId) {
  const lead = getContinuationLeader(paraId) || paraId;
  const follow = getContinuationFollower(lead);
  if (!follow) return null;
  const a = getTargetInfo(lead), b = getTargetInfo(follow);
  if (!a || !b) return null;
  return (a.text || '') + ' ' + (b.text || '');
}'''

NATIVE_FLOW_CODE = '''function getContinuityJoinedText(paraId) {
  const lead = getContinuationLeader(paraId) || paraId;
  const follow = getContinuationFollower(lead);
  if (!follow) return null;
  const a = getTargetInfo(lead), b = getTargetInfo(follow);
  if (!a || !b) return null;
  return (a.text || '') + ' ' + (b.text || '');
}
/* v101.142 — source-backed native visible-flow topology.
   These groups are independent of the five inherited CONTINUITY_GROUPS pairs. They govern only
   visible paragraph flow across unchanged stable records. H14 is segment-scoped: only P008's
   third DISPLAY_SEGMENT participates in the cross-record inline join; its earlier display
   segments retain their paragraph rhythm. List styling at H18/H22 remains deliberately blocked. */
const NATIVE_VISIBLE_FLOW_GROUPS = __GROUPS__;
function getNativeVisibleFlowGroupForMember(paraId) {
  for (const g of NATIVE_VISIBLE_FLOW_GROUPS) if (g.members.some(m => m.paragraph_id === paraId)) return g;
  return null;
}
function isNativeVisibleFlowGroupApplicable(group, paragraphs, startIndex) {
  if (!group || !Array.isArray(group.members) || group.members.length < 2 || !Array.isArray(paragraphs)) return false;
  for (let j=0;j<group.members.length;j++) {
    const m=group.members[j], p=paragraphs[startIndex+j];
    if (!p || p.id !== m.paragraph_id || String(p.t||'').length !== m.end) return false;
    if (getInternalSubheadingMeta(p.id)?.status === 'standalone_paragraph') return false;
    if (m.scope !== 'FULL_RECORD') {
      const segs=getDisplaySegments(p.id,p.t);
      if (!Array.isArray(segs) || !segs.length) return false;
      const last=segs[segs.length-1];
      if (!last || last.start !== m.start || last.end !== m.end) return false;
    } else if (m.start !== 0) return false;
  }
  return true;
}
function getNativeVisibleFlowJoinedText(paraId) {
  const group=getNativeVisibleFlowGroupForMember(paraId);
  if (!group) return null;
  const parts=[];
  for (const m of group.members) {
    const info=getTargetInfo(m.paragraph_id);
    if (!info) return null;
    parts.push(info.text || '');
  }
  return parts.join(group.joiner || ' ');
}
function getVisibleFlowJoinedText(paraId) {
  return getNativeVisibleFlowJoinedText(paraId) || getContinuityJoinedText(paraId);
}'''.replace('__GROUPS__', js_groups())

BUILD_SURFACE_OLD = r'''function buildContinuityFlowSurface(leader, follower, hourNum) {
  return `<div class="continuity-flow-surface" data-continuity-leader="${leader.id}" data-continuity-follower="${follower.id}">${buildContinuityNumberHtml(leader)}<div class="continuity-flow-text">${buildContinuityFragment(leader,hourNum,'leader')}<span class="continuity-flow-joiner" aria-hidden="true"> </span>${buildContinuityFragment(follower,hourNum,'follower')}</div></div>`;
}
function buildMeditationParagraphHtml(paragraphs, hourNum) {
  let html='';
  for (let i=0;i<paragraphs.length;i++) {
    const p=paragraphs[i];
    const followerId=getContinuationFollower(p.id);'''

BUILD_SURFACE_NEW = r'''function buildContinuityFlowSurface(leader, follower, hourNum) {
  return `<div class="continuity-flow-surface" data-continuity-leader="${leader.id}" data-continuity-follower="${follower.id}">${buildContinuityNumberHtml(leader)}<div class="continuity-flow-text">${buildContinuityFragment(leader,hourNum,'leader')}<span class="continuity-flow-joiner" aria-hidden="true"> </span>${buildContinuityFragment(follower,hourNum,'follower')}</div></div>`;
}
function buildNativeVisibleFlowSurface(group, groupParagraphs, hourNum) {
  const leader=groupParagraphs[0];
  const fragments=[];
  for (let j=0;j<groupParagraphs.length;j++) {
    const position=j===0?'leader':(j===groupParagraphs.length-1?'follower':'middle');
    fragments.push(buildContinuityFragment(groupParagraphs[j],hourNum,position));
  }
  return `<div class="continuity-flow-surface native-visible-flow-surface" data-native-flow-group="${group.group_id}" data-native-flow-members="${group.members.map(m=>m.paragraph_id).join(' ')}">${buildContinuityNumberHtml(leader)}<div class="continuity-flow-text">${fragments.join('<span class="continuity-flow-joiner" aria-hidden="true"> </span>')}</div></div>`;
}
function buildMeditationParagraphHtml(paragraphs, hourNum) {
  let html='';
  for (let i=0;i<paragraphs.length;i++) {
    const p=paragraphs[i];
    const nativeGroup=getNativeVisibleFlowGroupForMember(p.id);
    if (nativeGroup && nativeGroup.members[0].paragraph_id===p.id && isNativeVisibleFlowGroupApplicable(nativeGroup,paragraphs,i)) {
      const groupParagraphs=paragraphs.slice(i,i+nativeGroup.members.length);
      html += buildNativeVisibleFlowSurface(nativeGroup,groupParagraphs,hourNum);
      i += nativeGroup.members.length-1;
      continue;
    }
    const followerId=getContinuationFollower(p.id);'''


def build(base_zip, proposal_json, out_dir, out_zip):
    base_zip=Path(base_zip); proposal_json=Path(proposal_json); out=Path(out_dir); out_zip=Path(out_zip)
    assert sha_file(base_zip)==BASE_SHA,(sha_file(base_zip),BASE_SHA)
    assert sha_file(proposal_json)==PROPOSAL_SHA,(sha_file(proposal_json),PROPOSAL_SHA)
    prop=json.loads(proposal_json.read_text(encoding='utf-8'))
    assert prop['immutable_predecessor']['sha256']==BASE_SHA
    assert len(prop['groups'])==4 and sum(len(g['members'])-1 for g in prop['groups'])==6
    # exact proposal/group agreement
    for expected, actual in zip(GROUPS,prop['groups']):
        assert expected['id']==actual['group_id']
        assert [(m[0],m[1],m[2],m[3]) for m in expected['members']]==[(m['paragraph_id'],m['start'],m['end'],m['scope']) for m in actual['members']]

    shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
    with zipfile.ZipFile(base_zip) as z:
        assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
        z.extractall(out)
    base_files=files(out); base_hash={k:sha_file(v) for k,v in base_files.items()}
    idx=(out/'index.html').read_text(encoding='utf-8'); mir=(out/'luisa_24_heures.html').read_text(encoding='utf-8'); assert idx==mir
    protected_before={n:raw_const(idx,n) for n in PROTECTED_CONSTS}

    t=idx
    t=exact_replace(t,INSERT_AFTER_CONTINUITY,NATIVE_FLOW_CODE,'native flow authority/functions')
    t=exact_replace(t,BUILD_SURFACE_OLD,BUILD_SURFACE_NEW,'native flow renderer')
    t=exact_replace(t,"if (target.mode === 'paragraph' && typeof getContinuityJoinedText === 'function') body = getContinuityJoinedText(target.paragraphId) || body;","if (target.mode === 'paragraph' && typeof getVisibleFlowJoinedText === 'function') body = getVisibleFlowJoinedText(target.paragraphId) || body;",'copy visible flow')
    t=exact_replace(t,"const APP_VERSION = 'v101.141';",f"const APP_VERSION = '{VERSION}';",'APP_VERSION')
    t=exact_replace(t,"const APP_EVIDENCE_STAGE = 'SEARCH_COMPLETENESS_SUCCESSOR_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",'stage')
    t=re.sub(r"const BUILD_DATE = '2026-09-09';[^\n]*",f"const BUILD_DATE = '{DATE}'; // {VERSION} {REV} / native visible-flow topology successor; corpus, Search and speaker authority unchanged",t,count=1)
    assert t!=idx
    (out/'index.html').write_text(t,encoding='utf-8'); (out/'luisa_24_heures.html').write_text(t,encoding='utf-8')

    sw=(out/'sw.js').read_text(encoding='utf-8')
    sw=exact_replace(sw,'/* v101.141 R1 */','/* v101.142 R1 */','sw version')
    sw=exact_replace(sw,"const CACHE_NAME = 'luisa-24h-v101-141-r1';",f"const CACHE_NAME = '{CACHE}';",'sw cache')
    (out/'sw.js').write_text(sw,encoding='utf-8')
    man=json.loads((out/'manifest.json').read_text(encoding='utf-8')); assert man['version']=='v101.141' and man['build_revision']=='R1'; man['version']=VERSION; man['build_revision']=REV; writej(out/'manifest.json',man)

    vv=json.loads((out/'version.json').read_text(encoding='utf-8'))
    assert vv['app_version']=='v101.141' and vv['storage_schema']==8 and vv['personal_snapshot']==5
    vv.update({
      'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,'build_revision':REV,
      'release_scope':'Topology-only successor of exact immutable v101.141 R1. Implements exactly four source-backed native visible-flow groups / six JOIN_INLINE boundaries from authorized proposal SHA-256 '+PROPOSAL_SHA+'. H14 begins at P008 display segment 3 (offset 716) and continues through P011; H18 P055→P056 and P062→P063 and H22 P019→P020 join inline. H18/H22 list styling remains blocked. Canonical wording, stable IDs/order, Search semantics, speaker authority, DISPLAY_SEGMENTS, inherited CONTINUITY_GROUPS and personal-data schemas are unchanged.',
      'real_device_status':'Physical Samsung/iPhone/iPad, installed-PWA update/persistence, true offline cold reopen, VoiceOver/TalkBack and live-origin exact-byte binding NOT_TESTED for v101.142 R1.',
      'overall_release_status':'V101142_R1_NATIVE_VISIBLE_FLOW_TOPOLOGY_CONTROLLED_DEVICE_TEST_CANDIDATE__FINAL_PUBLIC_DEPLOYMENT_UNAUTHORIZED',
      'known_blockers':['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update to v101.142 R1 from the currently deployed build','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'],
      'external_open_gates':['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update to v101.142 R1 from the currently deployed build','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'],
      'postfreeze_reopen_evidence':'Exact v101.142 R1 successor ZIP requires external SHA-bound final recheck before controlled device testing.'
    })
    writej(out/'version.json',vv)

    # Current documentation and authority evidence.
    (out/'README.md').write_text(f'''# {VERSION} {REV} — current controlled device-test candidate\n\nCurrent stage: `{STAGE}`. Exact immutable predecessor `{BASE_VERSION}` SHA-256 `{BASE_SHA}`. User-authorized topology proposal SHA-256 `{PROPOSAL_SHA}` implements exactly 4 native visible-flow groups / 6 JOIN_INLINE boundaries. Canonical/devotional wording, stable IDs/order, Search semantics, speaker authority, inherited `CONTINUITY_GROUPS`, `DISPLAY_SEGMENTS` and personal-data schemas are unchanged. H18/H22 list styling remains blocked. Final public deployment remains unauthorized pending external device/live-origin/PWA/offline/accessibility gates.\n''',encoding='utf-8')
    (out/'REAL_DEVICE_QA_CHECKLIST.md').write_text(f'''# Real-device QA checklist — {VERSION} {REV}\n\nUse only the exact externally SHA-bound {VERSION} {REV} candidate. Internal browser evidence does not substitute for physical-device/PWA/accessibility gates.\n\n## Native visible-flow topology\n- Hour 14: confirm the final segment of P008 flows directly into P009→P010→P011 with no artificial visible paragraph gap, while P008 segments 1–2 retain their internal paragraph rhythm and a true break remains before P012.\n- Hour 18: confirm P055→P056 and P062→P063 flow inline with no artificial gap; confirm the true break before P064 remains. Do not expect newly created bullets/list styling.\n- Hour 22: confirm P019→P020 flows inline with no artificial gap. Do not expect newly created bullets/list styling.\n- Verify existing five inherited continuity pairs remain unchanged.\n\n## Protected regression\n- Search titles/direct-speech/result totals/deep links remain identical to v101.141 R1 behavior.\n- Notes, highlights, copy/selection, Samsung whole-visible-paragraph mode, last-place/resume, progression, theme and font settings continue to resolve through the unchanged stable paragraph IDs.\n- Existing Hour 24 and Méditée behavior remains intact.\n\n## External gates\n- Physical iPhone validation.\n- Physical iPad portrait and landscape validation.\n- Physical Samsung/Android validation.\n- Live-origin exact-byte binding.\n- Installed-PWA update and three close/reopen cycles.\n- True offline cold reopen.\n- Representative VoiceOver and TalkBack navigation.\n\nFinal public deployment remains unauthorized until all external gates are evidenced.\n''',encoding='utf-8')

    report=f'''# {VERSION} {REV} — Native visible-flow topology successor\n\n- Immutable predecessor: `{BASE_VERSION}` / `{BASE_SHA}`.\n- Authorized proposal: `{PROPOSAL_SHA}`.\n- Scope: presentation/topology only. Exactly **4 groups / 6 JOIN_INLINE edges**.\n- H14: `PASSION24.HOUR.14.P008` display segment 3 (`716..954`) → P009 → P010 → P011; true break before P012 preserved.\n- H18: P055→P056 and P062→P063; true break before P064 preserved.\n- H22: P019→P020.\n- H18/H22 list styling remains `BLOCKED_SOURCE_CONFLICT`; no bullets were introduced.\n- Existing five `CONTINUITY_GROUPS` pairs remain byte-identical and use their inherited renderer path.\n- Canonical text changes: **0**. Stable-ID/order changes: **0**. `DISPLAY_SEGMENTS` changes: **0**. Search semantic changes: **0**. Speaker-authority changes: **0**. User-data schema changes: **0**.\n- New runtime model: governed `NATIVE_VISIBLE_FLOW_GROUPS` is consumed before the inherited continuity-pair check, with adjacency/length/display-segment fail-closed validation.\n- Paragraph-mode copy recognizes the new visible-flow groups while range selection/highlight/note anchors remain per original stable record.\n- Final public deployment remains unauthorized pending external gates.\n'''
    (out/f'reports/V101142_R1_NATIVE_VISIBLE_FLOW_TOPOLOGY_SUCCESSOR.md').write_text(report,encoding='utf-8')
    ev=out/'evidence/v101142_r1'; ev.mkdir(parents=True,exist_ok=True)
    shutil.copy2(proposal_json,ev/'PROPOSED_24H_NATIVE_VISIBLE_FLOW_TOPOLOGY_R3.json')
    writej(ev/'USER_AUTHORIZATION_RECEIPT.json',{
      'schema':'L24H_V101142_R1_USER_AUTHORIZATION_RECEIPT_V1','date':DATE,'user_authorization':'EXPLICIT_AUTHORIZATION_RECEIVED_IN_CURRENT_CONVERSATION','immutable_predecessor_version':BASE_VERSION,'immutable_predecessor_sha256':BASE_SHA,'authorized_proposal_sha256':PROPOSAL_SHA,'scope':'Apply only the exact 24H native visible-flow topology proposal; no corpus wording, stable-ID/order, Search, speaker, user-schema or unrelated UI mutation.'
    })
    writej(ev/'IMPLEMENTED_NATIVE_VISIBLE_FLOW_LEDGER.json',{
      'schema':'L24H_V101142_R1_NATIVE_VISIBLE_FLOW_IMPLEMENTATION_LEDGER_V1','version':VERSION,'build_revision':REV,'proposal_sha256':PROPOSAL_SHA,'group_count':4,'join_inline_edge_count':6,'groups':[{'group_id':g['id'],'members':[{'paragraph_id':m[0],'start':m[1],'end':m[2],'scope':m[3]} for m in g['members']],'joiner':'space'} for g in GROUPS], 'blocked':['new list styling at H18/H22','canonical record merge/delete','CSS per-ID spacing hacks']
    })

    # Current metadata.
    writej(out/'metadata/build_provenance.json',{
      'version':VERSION,'build_revision':REV,'stage':STAGE,'build_date':DATE,'baseline_version':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,'topology_authority_sha256':PROPOSAL_SHA,
      'native_visible_flow_groups':4,'join_inline_edges':6,'corpus_text_changes':0,'text_library_changes':0,'speech_data_changes':0,'stable_id_changes':0,'display_segments_changes':0,'legacy_continuity_groups_changes':0,'search_semantics_changes':0,'storage_schema_unchanged':True,'personal_snapshot_schema_unchanged':True,'final_validation':'EXTERNAL_EXACT_ZIP_RECHECK_REQUIRED'
    })
    writej(out/'metadata/current_evidence_lineage.json',{
      'version':VERSION,'build_revision':REV,'stage':STAGE,'current_evidence_root':'evidence/v101142_r1','immediate_build_predecessor':{'version':BASE_VERSION,'sha256':BASE_SHA},'topology_authority_sha256':PROPOSAL_SHA,'content_authority':'v101.141 R1 corpus, Search and speaker authority inherited byte-for-byte','topology_scope':'exact four authorized native visible-flow groups / six JOIN_INLINE edges only'
    })
    writej(out/'metadata/current_gate_map.json',{
      'version':VERSION,'build_revision':REV,'stage':STAGE,'internal_gates':['exact v101.141 R1 SHA binding','exact authorized topology-proposal SHA binding','protected corpus/TEXT_LIBRARY/SPEECH_DATA/DISPLAY_SEGMENTS/CONTINUITY_GROUPS parity','4-group / 6-edge topology runtime verification','Search routing/highlighting/notes/copy-selection/Samsung/resume regression','Hour-24 and Méditée regression','full app regression','deterministic rebuild','four-pass adversarial audit','fresh ZIP reopen'],
      'external_open_gates':['physical iPad/iPhone/Samsung','live-origin exact-byte binding','installed PWA update to v101.142 R1 from the currently deployed build','installed PWA close/reopen persistence','true offline cold reopen','VoiceOver/TalkBack representative testing'],'public_release':'UNAUTHORIZED'
    })
    writej(out/'metadata/release_evidence_lifecycle.json',{
      'version':VERSION,'build_revision':REV,'stage':STAGE,'package_rule':'Package does not self-certify final ZIP bytes; exact frozen v101.142 R1 ZIP must receive external SHA-bound final validation receipt.','immediate_build_predecessor':BASE_VERSION,'immediate_build_predecessor_sha256':BASE_SHA,'corpus_text_changed':False,'search_code_changed':False,'topology_renderer_changed':True,'physical_device_claims':'NOT_TESTED','public_deployment_authorized':False
    })
    (out/'metadata/scope_escalation_authority.md').write_text(f'''# {VERSION} {REV} scope authority\n\nAuthorized scope is exclusively the 24H native visible-flow proposal SHA-256 `{PROPOSAL_SHA}` against immutable `{BASE_VERSION}` SHA-256 `{BASE_SHA}`.\n\nAllowed: four source-backed visible-flow groups / six JOIN_INLINE boundaries, including the H14 segment-scoped start at P008 offset 716.\n\nForbidden: corpus or `TEXT_LIBRARY` wording mutation; `SPEECH_DATA`/speaker reinterpretation; stable-ID/order mutation; Search semantic/normalizer change; personal-data schema change; new H18/H22 list styling; CSS per-ID spacing hacks; unrelated UI refactor.\n\nFinal public deployment remains externally gated.\n''',encoding='utf-8')
    writej(out/'metadata/active_report_inventory.json',{
      'version':VERSION,'build_revision':REV,'stage':STAGE,
      'active_documents':['README.md','REAL_DEVICE_QA_CHECKLIST.md','reports/V101142_R1_NATIVE_VISIBLE_FLOW_TOPOLOGY_SUCCESSOR.md','version.json','metadata/build_provenance.json','metadata/current_evidence_lineage.json','metadata/scope_escalation_authority.md'],
      'active_test_artifacts':['REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','evidence/v101142_r1/USER_AUTHORIZATION_RECEIPT.json','evidence/v101142_r1/IMPLEMENTED_NATIVE_VISIBLE_FLOW_LEDGER.json'],'historical_reports_root':'reports/historical/','rule':'Only listed active documents are current.'
    })

    # Embed builder.
    shutil.copy2(Path(__file__),out/'scripts/build_v101142_r1_native_visible_flow_topology.py')

    # Protected checks.
    final=(out/'index.html').read_text(encoding='utf-8'); assert final==(out/'luisa_24_heures.html').read_text(encoding='utf-8')
    for n in PROTECTED_CONSTS:
        assert raw_const(final,n)==protected_before[n],n
    assert "const APP_VERSION = 'v101.142';" in final and STAGE in final
    assert 'const NATIVE_VISIBLE_FLOW_GROUPS = ' in final
    assert 'getVisibleFlowJoinedText(target.paragraphId)' in final
    assert CACHE in (out/'sw.js').read_text(encoding='utf-8')
    # No canonical proposal record text changed; use proposal hashes against current CORPUS target info indirectly via verifier later.

    cur=files(out); removed=sorted(set(base_files)-set(cur)); assert removed==[],removed
    changed_or_added=sorted(k for k,p in cur.items() if k not in base_hash or sha_file(p)!=base_hash[k])
    # Must not add code outside planned files except manifests/evidence/report/builder.
    writej(out/'metadata/full_build_overlay_manifest.json',{
      'schema':'L24H_V101142_R1_FULL_BUILD_OVERLAY_V1','version':VERSION,'build_revision':REV,'baseline':BASE_VERSION,'baseline_zip_sha256':BASE_SHA,'topology_authority_sha256':PROPOSAL_SHA,
      'changed_or_added':sorted(set(changed_or_added)|{'metadata/full_build_overlay_manifest.json','metadata/hash_manifest.json','metadata/package_manifest.json'}),'removed':[],
      'corpus_text_delta':'ZERO','text_library_delta':'ZERO','speech_data_delta':'ZERO','stable_id_delta':'ZERO','display_segments_delta':'ZERO','legacy_continuity_groups_delta':'ZERO','search_semantics_delta':'ZERO','native_visible_flow_groups':4,'join_inline_edges':6
    })
    ex={'metadata/hash_manifest.json','metadata/package_manifest.json'}; lst=[]
    for k,p in sorted(files(out).items()):
        if k in ex: continue
        lst.append({'path':k,'size':p.stat().st_size,'sha256':sha_file(p)})
    writej(out/'metadata/hash_manifest.json',{'schema':'L24H_HASH_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':lst})
    writej(out/'metadata/package_manifest.json',{'schema':'L24H_PACKAGE_MANIFEST_V1','version':VERSION,'build_revision':REV,'self_exclusion':sorted(ex),'file_count':len(lst),'files':[{'path':x['path'],'size':x['size']} for x in lst]})

    # Freeze then return.
    zsha=freeze(out,out_zip)
    return {'version':VERSION,'revision':REV,'stage':STAGE,'base_sha256':BASE_SHA,'proposal_sha256':PROPOSAL_SHA,'files':len(files(out)),'zip_sha256':zsha,'zip_size':out_zip.stat().st_size,'zip_members':len(zipfile.ZipFile(out_zip).infolist()),'changed_or_added_count':len(changed_or_added)}

if __name__=='__main__':
    if len(sys.argv)!=5: raise SystemExit('Usage: build.py <v101141_R1.zip> <proposal.json> <out_dir> <out.zip>')
    print(json.dumps(build(*sys.argv[1:]),ensure_ascii=False,indent=2))
