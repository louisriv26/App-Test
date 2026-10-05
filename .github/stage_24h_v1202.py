from pathlib import Path
import urllib.request, base64, hashlib, json, re, shutil, subprocess

ROOT=Path.cwd()
ROUTE=ROOT/'24h-v120-2-b1-core-loop-closure'
QUAL=ROOT/'qualification-24h-v120-2-b1'
TMP=ROOT/'.tmp_24h_v1202'
if TMP.exists(): shutil.rmtree(TMP)
TMP.mkdir()
if ROUTE.exists(): shutil.rmtree(ROUTE)

BASE='https://raw.githubusercontent.com/louisriv26/Les-24-Heures-de-la-Passion/380e61f7150d61c5d4745840de56b5a4c1c00fd0'
FILES=['.nojekyll','apple-touch-icon.png','favicon-16.png','favicon-32.png','favicon.ico','icon-60.png','icon-120.png','icon-192.png','icon-512.png','icon-maskable-512.png','index.html','luisa_24_heures.html','manifest.json','sw.js','version.json']
for name in FILES:
    with urllib.request.urlopen(BASE+'/'+name) as r:
        (TMP/name).write_bytes(r.read())

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(TMP/'index.html')=='71315aadb1806819e42860f10bffd37662660ae0ab49af805f5e9a3ea9357c00'
assert (TMP/'index.html').read_bytes()==(TMP/'luisa_24_heures.html').read_bytes()

parts=sorted((ROOT/'.github').glob('24h_v1202_patch.part*.b64'), key=lambda p:int(re.search(r'part(\d+)',p.name).group(1)))
assert [int(re.search(r'part(\d+)',p.name).group(1)) for p in parts]==list(range(1,8))
b64=''.join(p.read_text() for p in parts)
assert len(b64)==19728
assert hashlib.sha256(b64.encode()).hexdigest()=='1514f507caa66c0f33d9febeed0467c37f729325bfbb30b1efcc845620f6cea4'
patch=base64.b64decode(b64,validate=True)
assert hashlib.sha256(patch).hexdigest()=='a976fe5f6b63c17b56eb35f42d459cf91e5f6e42934d749c07412b0e3b2f410e'
patchfile=TMP/'core.patch'; patchfile.write_bytes(patch)
subprocess.run(['patch','-p1','--batch','--forward','-i',str(patchfile.resolve())],cwd=TMP,check=True)
shutil.copy2(TMP/'index.html',TMP/'luisa_24_heures.html')
assert sha(TMP/'index.html')=='568eec865918320af094669f61e3c3447a6d29aa07ec5a057a557c490e95b7f8'
assert (TMP/'index.html').read_bytes()==(TMP/'luisa_24_heures.html').read_bytes()

APP='v120.2'; BUILD='B1'; SEQ=120002001
RID='24h-v120-2-b1-20261005-core-loop-closure'
SHELL='568eec865918320af094669f61e3c3447a6d29aa07ec5a057a557c490e95b7f8'

m=json.loads((TMP/'manifest.json').read_text())
m.update(version=APP,build_revision=BUILD,release_sequence=SEQ,release_id=RID,build=BUILD)
(TMP/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')

p=TMP/'sw.js'; sw=p.read_text()
for a,b in [
("/* v120.1 B1 — visible public-version prefix closure; v120 runtime semantics preserved unchanged. */","/* v120.2 B1 — bounded meditation core-loop closure; v120.1 protected content/state semantics preserved. */"),
("const APP_VERSION = 'v120.1';","const APP_VERSION = 'v120.2';"),
("const RELEASE_SEQUENCE = 120001001;","const RELEASE_SEQUENCE = 120002001;"),
("const RELEASE_ID = '24h-v120-1-b1-20261004-visible-version-v-closure';",f"const RELEASE_ID = '{RID}';"),
("const CANONICAL_SHELL_SHA256 = '71315aadb1806819e42860f10bffd37662660ae0ab49af805f5e9a3ea9357c00';",f"const CANONICAL_SHELL_SHA256 = '{SHELL}';"),
("const CACHE_NAME = `${CACHE_PREFIX}v120-1-b1`;","const CACHE_NAME = `${CACHE_PREFIX}v120-2-b1`;")
]:
    assert sw.count(a)==1, a
    sw=sw.replace(a,b,1)
p.write_text(sw,encoding='utf-8',newline='')

s=(TMP/'index.html').read_text()
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,flags=re.S|re.I)
assert len(scripts)==1
script_hash=base64.b64encode(hashlib.sha256(scripts[0].encode()).digest()).decode()
assert script_hash=='FE5uB44dBi0XWTzpLitzxlQw/fv9KXI2D9KfGoNRUaU='

p=TMP/'version.json'; v=json.loads(p.read_text())
v['app_version']=APP
v['build_date']='2026-10-05'
v['cache_name']='scope-derived:luisa-24h-<scope-fingerprint>-v120-2-b1'
v['release_scope']='v120.2/B1 successor to exact production v120.1/B1. Bounded meditation core-loop closure only: replaces the premature top recovery question with a compact status/recovery control; makes end-of-Hour completion explicit through “J’ai médité cette Heure”; labels unmarked forward navigation “Continuer sans marquer”; removes duplicated end-of-Hour tab/next actions; fixes the meditation recovery-control focus token. Corpus, Text Library, provenance, Search semantics, personal-state schema/semantics, backup/import, native selection and update-protocol semantics are protected and unchanged.'
v['real_device_status']='V120_2_B1_CANDIDATE__TARGETED_PHYSICAL_GATE_OPEN'
v['overall_release_status']='V120_2_B1_CORE_LOOP_CLOSURE_CANDIDATE__PRODUCTION_NOT_AUTHORIZED'
blockers=[
'Physical iPhone/iPad verification on App-Test of the exact v120.2/B1 core-loop states: unmarked top status, explicit end completion, Continue without marking, marked next-Hour path, and keyboard focus visibility.',
'Physical close/reopen persistence check after marking and after continuing without marking.',
'Installed-PWA production v120.1 → v120.2 update/activation and acknowledged-state preservation if included in the release physical protocol.',
'Live-origin exact-byte binding after any future production deployment before release closure.'
]
v['known_blockers']=blockers; v['external_open_gates']=blockers
v['build_revision']=BUILD; v['release_sequence']=SEQ; v['release_id']=RID
v['canonical_shell_sha256']=SHELL
v['pwa_update_predecessor_version']='v120.1'
v['pwa_update_predecessor_zip_sha256']='ab9db64fc632aedd22a954731a02e3339e7e6478b92626aab007b6ef087f6314'
v['functional_freeze_status']='V120_2_B1_BOUNDED_CORE_LOOP_CLOSURE__PROTECTED_CONTENT_AND_PERSONAL_STATE_SCHEMA_UNCHANGED__TARGETED_PHYSICAL_GATE_OPEN'
v['security_stage_status']='CSP3_EXACT_V120_2_B1_INLINE_BINDINGS__SERVICE_WORKER_CANONICAL_SHELL_HASH_BOUND_TO_'+SHELL.upper()
v['security_inline_script_sha256_base64']=[script_hash]
v['ux_audit_core_loop_v120_2_b1']={
'candidate':'v120.2/B1','date':'2026-10-05',
'predecessor':'exact production v120.1/B1 commit 380e61f7150d61c5d4745840de56b5a4c1c00fd0 / tree f1a24a2bb38fdf902a5ffb87bf4cb6a9a70949d6',
'authority':'User instruction 2026-10-05: proceed as recommended after adversarial adjudication of the attached v120.1 UX audit.',
'included_findings':['N1 core-loop hierarchy/bypass','F-05 premature/stale top recovery prompt','F-03 recovery-control focus indicator','F-06-B duplicate end-of-Hour next/tab actions'],
'explicitly_not_included':['F-06-A duplicate Home start','N2 notifications','N3 Holy-Hour non-colour cue','N4 heading semantics','N5 size/reflow','N6 Home disclosure affordance','N7 navigation/focus architecture beyond meditation focus token','N8 Home duplication','N9 title wrapping','N10 time wording','N11 technical labels','N12 secondary-button affordance','N13 resume context','N14 Help shortcut','N15 decorative symbols','N16 desktop layout','N17 Settings taxonomy','N18 report destination','N19 internal reader-facing notes','F-09 ordinal consistency','F-13 search-result exact-range adjudication','WCAG 1.4.12 tab-spacing regression'],
'interaction_contract':{
'top_unmarked':'Compact status/recovery control only; no “Vous avez déjà médité ?” question.',
'end_unmarked':'Primary explicit action “J’ai médité cette Heure”.',
'forward_unmarked':'Explicit “Continuer sans marquer”; navigation does not mutate meditation state.',
'end_marked':'Status “✓ Heure méditée”; current Hour counts exactly once in progression.',
'forward_marked':'Next control becomes “Prier la Xe Heure”.',
'undo':'Top recovery control remains available as “Retirer”.',
'automatic_marking':'Forbidden.'
},
'protected_surfaces':['CORPUS exact block','TEXT_LIBRARY exact block','PROVENANCE_PUBLIC_PROJECTION exact block','PROVENANCE_PUBLIC_GUIDE exact block','Search semantics/results','personal-state schema and persistence semantics','backup/import','native-selection','update-v2 protocol'],
'mutation_authority':'AUTHORIZED_BOUNDED_V120_2_B1_CORE_LOOP_ONLY',
'production_deployment_authority':'NONE','physical_gate':'OPEN'
}
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')

expected={
'index.html':'568eec865918320af094669f61e3c3447a6d29aa07ec5a057a557c490e95b7f8',
'luisa_24_heures.html':'568eec865918320af094669f61e3c3447a6d29aa07ec5a057a557c490e95b7f8',
'manifest.json':'a9307442168251eec9750b3e0a675e55f0fc9cec6df2f35c8e0c60e3d1d4254d',
'sw.js':'5cbace63cb2af3555b1f491c97c81001509c38c5cf7dc5724083d6f024285d68',
'version.json':'d28b5b89fc1b2da48ab3ac2b622c3e70b6e607f585f67f5158485daa2c3147ba'
}
for name,h in expected.items(): assert sha(TMP/name)==h,(name,sha(TMP/name),h)

assert 'Vous avez déjà médité cette Heure ?' not in s
assert 'Si vous avez oublié de la cocher à la fin.' not in s
assert 'J’ai médité cette Heure' in s and 'Continuer sans marquer' in s
assert 'var(--focus);' not in s
subprocess.run(['node','--check','sw.js'],cwd=TMP,check=True)
Path('/tmp/app_v1202.js').write_text(scripts[0])
subprocess.run(['node','--check','/tmp/app_v1202.js'],check=True)

ROUTE.mkdir()
for name in FILES: shutil.copy2(TMP/name,ROUTE/name)

QUAL.mkdir(exist_ok=True)
evidence={
'candidate':'v120.2/B1','release_sequence':SEQ,'release_id':RID,
'predecessor_commit':'380e61f7150d61c5d4745840de56b5a4c1c00fd0',
'predecessor_tree':'f1a24a2bb38fdf902a5ffb87bf4cb6a9a70949d6',
'shell_sha256':SHELL,'script_sha256_base64':script_hash,
'file_sha256':{name:sha(ROUTE/name) for name in FILES},
'scope':'N1 + F-05 + F-03 + F-06-B core-loop closure only',
'production_deployment_authority':'NONE','physical_gate':'OPEN'
}
(QUAL/'STAGING.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
shutil.rmtree(TMP)
print(json.dumps(evidence,indent=2))
