from pathlib import Path
import json,re,csv,sys,collections
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
H=(ROOT/'index.html').read_text('utf8');assert H==(ROOT/'luisa_24_heures.html').read_text('utf8')
def pc(n):
 m=re.search(r'const\s+'+re.escape(n)+r'\s*=\s*',H);assert m,n;return json.JSONDecoder().raw_decode(H[m.end():])[0]
assert "const APP_VERSION = 'v101.99'" in H
v=json.loads((ROOT/'version.json').read_text());assert v['app_version']=='v101.99' and v['cache_name']=='luisa-24h-v101-99' and v['ldc_source_app_version']=='v2.19.29-R1B' and v['ldc_source_package_sha256']=='eb2fa6abce1525399547f469ad1c2d64e818ff8685fe11cc20a57571c59f92fc'
assert json.loads((ROOT/'manifest.json').read_text())['version']=='v101.99';assert "const CACHE_NAME = 'luisa-24h-v101-99'" in (ROOT/'sw.js').read_text()
a=pc('LDC_CURRENT_SYNC_AUTHORITY');assert a=={'source_public_version':'Version 29','source_app_version':'v2.19.29-R1B','source_package_sha256':'eb2fa6abce1525399547f469ad1c2d64e818ff8685fe11cc20a57571c59f92fc','sync_date':'2026-08-21','mapped_source_blocks':115,'ra19b_changed_blocks_vs_ra18':61,'explicit_preserve_breaks':100,'explicit_preserve_list_breaks':0,'runtime_flow_overrides':66}
C=pc('CORPUS');b=next(x for x in C['sections'] if x.get('section_id')=='PASSION24.SECTION.BENEFITS');assert b['ldc_sync']['source_app_version']=='v2.19.29-R1B' and b['ldc_sync']['source_public_version']=='Version 29' and b['ldc_sync']['source_package_sha256']=='eb2fa6abce1525399547f469ad1c2d64e818ff8685fe11cc20a57571c59f92fc' and 'ra19b' in b['ldc_sync']['mode'];assert len(b['ldc_source_map'])==21 and all(x['status']=='SYNCED_CURRENT_LDC_RA19B' and 'Current LDC RA19B' in x['source_reason'] for x in b['ldc_source_map'])
assert 'SYNCED_CURRENT_LDC_RA18' not in H and 'Current LDC RA18' not in H and 'cbe48143dd41661a3bbe1da6cf8f1213c705ff9d15527848969587723affe3cc' not in H
TL=pc('TEXT_LIBRARY');maps=[r for it in TL for r in (it.get('source_map') if isinstance(it.get('source_map'),list) else []) if isinstance(r,dict) and r.get('matched_entry_id')];assert maps and all(r['status']=='SYNCED_CURRENT_LDC_RA19B' for r in maps)
lay=pc('LDC_LIBRARY_FLOW_LAYOUT');assert len(lay)==22 and sum(map(len,lay.values()))==66
c=collections.Counter()
for bs in lay.values():
 for bl in bs:
  c.update(bl['break_before_actions'].values())
  for d in bl['intra_actions'].values():c.update(d.values())
assert c=={'paragraph_break':1518,'preserve_break':100} and 'preserve_list_break' not in c
summ=json.loads((ROOT/'reports/ldc_ra19b_flow_boundary_summary.json').read_text());assert summ['source_blocks']==115 and summ['ra19b_changed_vs_ra18_blocks']==61 and summ['paragraph_break']==2179 and summ['preserve_break']==100 and summ['preserve_list_break']==0 and summ['runtime_overrides']==66 and summ['flow_surface_visual_paragraph_groups']==1584
rows=list(csv.DictReader((ROOT/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open(encoding='utf8')));assert len(rows)==15 and all(r['app_version']=='v101.99' and r['status']=='NOT_TESTED' for r in rows)
print(json.dumps({'authority':a,'promesses_maps':len(b['ldc_source_map']),'layout_items':len(lay),'overrides':66,'actions':c}))
