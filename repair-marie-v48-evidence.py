from pathlib import Path
import re,hashlib,base64,json
p=Path('marie-v48-b1-darkmode/index.html');s=p.read_text(encoding='utf-8')
styles=re.findall(r'<style[^>]*>([\s\S]*?)</style>',s,re.I)
scripts=[m.group(1) for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>',s,re.I)]
def h(x):return base64.b64encode(hashlib.sha256(x.encode('utf-8')).digest()).decode('ascii')
assert len(styles)==1 and len(scripts)>=1
csp=re.search(r'Content-Security-Policy" content="([^"]+)"',s,re.I).group(1)
st=[h(x) for x in styles];sc=[h(x) for x in scripts]
assert all("'sha256-"+x+"'" in csp for x in st+sc)
e=json.loads(Path('marie-v48-build-evidence.json').read_text(encoding='utf-8'))
e['style_sha256_base64']=st;e['script_sha256_base64']=sc
e['evidence_reporting_correction']='2026-10-03: populated hash arrays after correcting reporting regex; candidate bytes unchanged.'
Path('marie-v48-build-evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'styles':len(st),'scripts':len(sc),'style_hashes':st,'script_hashes':sc},indent=2))
