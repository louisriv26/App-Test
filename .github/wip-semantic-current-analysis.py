#!/usr/bin/env python3
import json, hashlib, re, statistics, collections
from pathlib import Path

ROOT=Path('.')
OUT=Path('wip-semantic-current-analysis.json')
TOKEN_RE=re.compile(r"\w+(?:['’]\w+)?", re.UNICODE)

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def load(p):
    with open(p,encoding='utf-8') as f:return json.load(f)

docs_obj=load('corpus/search_v2_documents.json')
entries_obj=load('corpus/search_v2_entries.json')
top=load('corpus/search_v21_topology.json')
docs=docs_obj['documents']; entries=entries_obj['entries']
old=[]
with open('pls_v15/pack/metadata.jsonl',encoding='utf-8') as f:
    for line in f:
        if line.strip(): old.append(json.loads(line))

refs={str(d[4]):i for i,d in enumerate(docs) if len(d)>4 and d[4]}
ids={str(d[0]):i for i,d in enumerate(docs) if d}
covered=set(); span_keys=collections.Counter(); row_keys=collections.Counter()
for r in old:
    row_keys.update(r.keys())
    for s in r.get('source_spans') or []:
        if isinstance(s,dict):
            span_keys.update(s.keys())
            for k in ('stable_ref','ref','paragraph_ref','paragraph_id','id','doc_id'):
                v=s.get(k)
                if v is not None:
                    sv=str(v)
                    if sv in refs: covered.add(refs[sv])
                    if sv in ids: covered.add(ids[sv])

word_counts=[len(TOKEN_RE.findall(str(r.get('text','')))) for r in old]
missing=sorted(set(range(len(docs)))-covered)
missing_by_entry=collections.Counter()
missing_by_volume=collections.Counter()
for i in missing:
    d=docs[i]; ei=int(d[1]); e=entries[ei] if 0<=ei<len(entries) else []
    missing_by_entry[str(e[0] if e else d[0])]+=1
    missing_by_volume[str(d[2])]+=1

def small_row(r):
    z=dict(r)
    if 'text' in z and len(str(z['text']))>500:z['text']=str(z['text'])[:500]+'…'
    return z

def sample_unit(x):
    if not isinstance(x,list):return x
    y=[]
    for v in x[:7]:
        if isinstance(v,list) and len(v)>12:y.append(v[:12]+['…'])
        else:y.append(v)
    return y

report={
 'schema':'ldc-wip-current-semantic-analysis-v1',
 'authorities':{
   'corpus_manifest_sha256':sha('corpus/manifest.json'),
   'search_v2_manifest_sha256':sha('corpus/search_v2_manifest.json'),
   'search_v21_manifest_sha256':sha('corpus/search_v21_manifest.json'),
   'search_documents_sha256':sha('corpus/search_v2_documents.json'),
   'search_topology_sha256':sha('corpus/search_v21_topology.json'),
   'offline_manifest_sha256':sha('offline_manifest.json'),
 },
 'current':{
   'documents':len(docs),'entries':len(entries),
   'document_schema':docs_obj.get('schema'),'entry_schema':entries_obj.get('schema'),
   'topology_keys':sorted(top.keys()),
   'topology_counts':{k:len(v) for k,v in top.items() if isinstance(v,list)},
   'base_unit_sample':sample_unit((top.get('base_units') or [None])[0]),
   'enriched_override_sample':sample_unit((top.get('enriched_overrides') or [None])[0]),
   'complete_unit_sample':sample_unit((top.get('complete_units') or [None])[0]),
   'complement_unit_sample':sample_unit((top.get('complement_units') or [None])[0]),
   'document_sample':docs[:3],
 },
 'old_pack':{
   'rows':len(old),
   'row_keys':dict(row_keys),
   'source_span_keys':dict(span_keys),
   'word_count_min':min(word_counts) if word_counts else 0,
   'word_count_max':max(word_counts) if word_counts else 0,
   'word_count_median':statistics.median(word_counts) if word_counts else 0,
   'word_count_96':sum(1 for x in word_counts if x==96),
   'row_samples':[small_row(x) for x in old[:3]],
 },
 'compat_coverage_recomputed':{
   'covered_documents':len(covered),
   'missing_documents':len(missing),
   'coverage_fraction':(len(covered)/len(docs) if docs else 0),
   'missing_first_30':[{'doc_index':i,'doc_id':docs[i][0],'stable_ref':docs[i][4],'entry_id':entries[int(docs[i][1])][0],'volume':docs[i][2]} for i in missing[:30]],
   'missing_by_volume':dict(sorted(missing_by_volume.items(),key=lambda x:int(x[0]))),
   'top_missing_entries':missing_by_entry.most_common(30),
 },
}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({
 'documents':len(docs),'old_rows':len(old),'covered':len(covered),'missing':len(missing),
 'word_count_max':report['old_pack']['word_count_max'],
 'span_keys':report['old_pack']['source_span_keys'],
 'sha':report['authorities']
},ensure_ascii=False,indent=2))
