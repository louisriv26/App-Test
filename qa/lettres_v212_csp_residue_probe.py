from pathlib import Path
from html.parser import HTMLParser
import re,hashlib,base64,json

ROOT=Path('.')
CURRENT=ROOT/'lettres-v2.12-b1-darkmode/index.html'

def token(s):
    return "'sha256-"+base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()+"'"

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.csp=''; self.handlers=[]
    def handle_starttag(self,t,a):
        d=dict(a)
        if t.lower()=='meta' and d.get('http-equiv','').lower()=='content-security-policy':
            self.csp=d.get('content','')
        for k,v in a:
            if k.lower().startswith('on') and v is not None:
                self.handlers.append(v)

h=CURRENT.read_text(encoding='utf-8')
p=P(); p.feed(h)
D={}
for part in p.csp.split(';'):
    part=part.strip()
    if part:
        xs=part.split(); D[xs[0]]=xs[1:]
script_blocks=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',h,re.S|re.I)
current_values=set(p.handlers)
for m in re.finditer(r'\bon[a-z]+\s*=\s*(["\'])(.*?)\1',h,re.I|re.S):
    current_values.add(m.group(2))
needed={token(x) for x in script_blocks}|{token(x) for x in current_values}
allow={x for x in D.get('script-src',[]) if x.startswith("'sha256-")}
extras=sorted(allow-needed)
print('CURRENT_KNOWN_HANDLER_VALUES',len(current_values))
print('CSP_SHA_COUNT',len(allow))
print('UNMAPPED_CURRENT',json.dumps(extras))
matches={x:[] for x in extras}

paths=sorted(set(ROOT.glob('lettres-*/index.html'))|set(ROOT.glob('**/lettres-*/index.html')))
for path in paths:
    try:
        txt=path.read_text(encoding='utf-8')
    except Exception:
        continue
    vals=set()
    pp=P()
    try: pp.feed(txt); vals.update(pp.handlers)
    except Exception: pass
    for m in re.finditer(r'\bon[a-z]+\s*=\s*(["\'])(.*?)\1',txt,re.I|re.S):
        vals.add(m.group(2))
    for v in vals:
        t=token(v)
        if t in matches:
            matches[t].append({'path':str(path),'value':v})

print('HISTORICAL_MATCHES='+json.dumps(matches,ensure_ascii=False))
for t,rows in matches.items():
    print('HASH',t,'MATCHES',len(rows))
    for row in rows[:20]:
        print('  ',row['path'],repr(row['value']))
