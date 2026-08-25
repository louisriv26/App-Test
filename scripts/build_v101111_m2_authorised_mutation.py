from pathlib import Path
import csv, hashlib, json, shutil, sys, zipfile

BASE_ZIP=Path('/mnt/data/m2_recovery/v101110_locked.zip')
EXPECTED_BASE='4e204832023ff8d6d71319caf854a94bda53f148258df700b8792789597294a8'
LEDGER=Path('/mnt/data/L24H_RA19E2_M2_2026-08-25/M2_AUTHORISED_ACTION_LEDGER.csv')
VERSION='v101.111'
DATE='2026-08-25'
STAGE='RA19E2_M2_AUTHORISED_MUTATION_INTEGRITY_R1'

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def extract_json_const(text,name):
    marker=f'const {name} = '
    st=text.index(marker)+len(marker)
    obj,end=json.JSONDecoder().raw_decode(text[st:])
    return obj,st,st+end

def replace_json_const(text,name,obj):
    old,st,en=extract_json_const(text,name)
    encoded=json.dumps(obj,ensure_ascii=False,separators=(',',':'))
    # Baseline serializer contract: reserializing an untouched declaration must be byte exact.
    assert json.dumps(old,ensure_ascii=False,separators=(',',':'))==text[st:en]
    return text[:st]+encoded+text[en:]

def mutate_html(src):
    text=src
    sd,_,_=extract_json_const(text,'SPEECH_DATA')
    adj,_,_=extract_json_const(text,'SPEECH_PRESENTATION_ADJUDICATIONS')
    proj,_,_=extract_json_const(text,'SPEECH_PRESENTATION_PROJECTION')
    sup,_,_=extract_json_const(text,'SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS')
    topo,_,_=extract_json_const(text,'VISIBLE_PARAGRAPH_TOPOLOGY')

    # Exact preconditions repeated inside the mutation script.
    assert sup['PASSION24.TEXT.RELATED_HOUR_06.BODY.P053']==[{'start':122,'end':123,'reason':'cross_record_direct_speech_opening_wrapper','next_id':'PASSION24.TEXT.RELATED_HOUR_06.BODY.P054','speaker':'JESUS'}]
    assert sup['PASSION24.TEXT.RELATED_HOUR_06.BODY.P068']==[{'start':312,'end':313,'reason':'cross_record_direct_speech_opening_wrapper','next_id':'PASSION24.TEXT.RELATED_HOUR_06.BODY.P069','speaker':'JESUS'}]
    assert sd['PASSION24.TEXT.RELATED_HOUR_13.BODY.P056']==[{'speaker':'JESUS','start':0,'end':61},{'speaker':'JESUS','start':62,'end':101},{'speaker':'JESUS','start':102,'end':128},{'speaker':'JESUS','start':132,'end':134}]
    assert sd['PASSION24.TEXT.RELATED_HOUR_15.BODY.P097']==[{'speaker':'JESUS','start':0,'end':83}]
    assert sd['PASSION24.TEXT.RELATED_HOUR_15.BODY.P098']==[{'speaker':'JESUS','start':0,'end':61}]
    assert sd['PASSION24.TEXT.RELATED_HOUR_15.BODY.P099']==[{'speaker':'JESUS','start':0,'end':113}]
    assert sd['PASSION24.SECTION.BENEFITS.P139']==[{'speaker':'JESUS','start':0,'end':76}]
    assert proj['PASSION24.TEXT.RELATED_HOUR_21.BODY.P059'].get('adjudications') and proj['PASSION24.TEXT.RELATED_HOUR_21.BODY.P059']['adjudications'][0]['start']==108
    assert proj['PASSION24.TEXT.RELATED_HOUR_21.BODY.P147']=={'runs':[{'start':0,'end':196,'speaker':'JESUS'}],'hidden':[],'breaks':[]}
    assert 'PASSION24.TEXT.RELATED_HOUR_21.BODY.P147' not in adj

    # M1-SA-001/002 — remove stale inert cross-record opening suppressions.
    del sup['PASSION24.TEXT.RELATED_HOUR_06.BODY.P053']
    del sup['PASSION24.TEXT.RELATED_HOUR_06.BODY.P068']

    # M1-SA-003 — close semantic lexical gap and presentation/topology discontinuity.
    sd['PASSION24.TEXT.RELATED_HOUR_13.BODY.P056'].insert(3,{'speaker':'JESUS','start':129,'end':131})
    proj['PASSION24.TEXT.RELATED_HOUR_13.BODY.P056']={'runs':[{'start':0,'end':134,'speaker':'JESUS'}],'hidden':[],'breaks':[]}
    del topo['local_breaks']['PASSION24.TEXT.RELATED_HOUR_13.BODY.P056']

    # M1-SA-004 — opening straight quote is meaningful nested content and inherits JESUS display.
    proj['PASSION24.TEXT.RELATED_HOUR_15.BODY.P096']['runs']=[{'start':0,'end':226,'speaker':'JESUS'}]

    # M1-SA-005/006/007 — semantic generic-soul quotation nested inside JESUS presentation.
    for tid,end in [
        ('PASSION24.TEXT.RELATED_HOUR_15.BODY.P097',83),
        ('PASSION24.TEXT.RELATED_HOUR_15.BODY.P098',61),
        ('PASSION24.TEXT.RELATED_HOUR_15.BODY.P099',113),
    ]:
        del sd[tid]
        adj[tid]=[{'start':0,'end':end,'semantic_speaker':'GENERIC_SOUL','presentation_speaker':'JESUS','quotation_depth':2,'reason':'RA19E.2 M1 source-backed T15.E0036 nested generic-soul quotation; semantic voice remains distinct while the active outer JESUS turn governs display.'}]
    proj['PASSION24.TEXT.RELATED_HOUR_15.BODY.P099']['runs']=[{'start':0,'end':114,'speaker':'JESUS'}]

    # M1-SA-008 — exact-text mirror of the already-correct P134 model.
    del sd['PASSION24.SECTION.BENEFITS.P139']
    adj['PASSION24.SECTION.BENEFITS.P139']=[{'start':0,'end':76,'semantic_speaker':'GENERIC_SOUL','presentation_speaker':'JESUS','quotation_depth':2,'reason':'RA19E.2 M1 mirror reconciliation to source-correct PROMISES_BENEFITS P134 / ldc_t11_1914_11_06_e001_p007.'}]
    proj['PASSION24.SECTION.BENEFITS.P139']={'runs':[{'start':0,'end':77,'speaker':'JESUS'}],'hidden':[{'start':77,'end':78,'role':'OUTER_DIVINE_CLOSE_WRAPPER_HIDE','reason':'OUTER_DIVINE_DIRECT_ATTRIBUTION'}],'breaks':[]}
    del topo['local_breaks']['PASSION24.SECTION.BENEFITS.P139']

    # M1-SA-009 — remove stale local pending-upstream provenance from the active projection object.
    del proj['PASSION24.TEXT.RELATED_HOUR_21.BODY.P059']['adjudications']

    # M1-SA-010 — exact A16 PERSONIFIED_VOICE span. P147 binding is proved by source map and exact offsets.
    adj['PASSION24.TEXT.RELATED_HOUR_21.BODY.P147']=[{'start':167,'end':194,'semantic_speaker':'PERSONIFIED_VOICE','presentation_speaker':'JESUS','quotation_depth':1,'reason':'RA19E.2 M1.1 exact A16 LDC.T35.E0040.P023 correction: winds/seas personified voice “Je vous aime, je vous aime.” remains visually within the JESUS outer presentation turn.'}]

    # Serialize only governed declarations. Untouched JSON ordering is preserved.
    for name,obj in [
        ('SPEECH_DATA',sd),
        ('SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS',sup),
        ('SPEECH_PRESENTATION_ADJUDICATIONS',adj),
        ('SPEECH_PRESENTATION_PROJECTION',proj),
        ('VISIBLE_PARAGRAPH_TOPOLOGY',topo),
    ]:
        text=replace_json_const(text,name,obj)

    # Required successor identity inside candidate HTML only; package-wide propagation is M4.
    old="const APP_VERSION = 'v101.110';"
    assert text.count(old)==1
    text=text.replace(old,f"const APP_VERSION = '{VERSION}';",1)
    old="const APP_EVIDENCE_STAGE = 'RA19E_NESTED_QUOTE_DELIMITER_DISPLAY_CONTINUITY_R1';"
    assert text.count(old)==1
    text=text.replace(old,f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
    old="const BUILD_DATE = '2026-08-23'; // v101.110 / RA19E nested quote delimiter display continuity"
    assert text.count(old)==1
    text=text.replace(old,f"const BUILD_DATE = '{DATE}'; // {VERSION} / RA19E.2 authorised speaker/presentation mutation",1)
    return text

def build(outdir):
    outdir=Path(outdir)
    shutil.rmtree(outdir,ignore_errors=True); outdir.mkdir(parents=True)
    assert sha_file(BASE_ZIP)==EXPECTED_BASE
    with zipfile.ZipFile(BASE_ZIP) as z:
        assert z.testzip() is None
        z.extractall(outdir)
    rows=list(csv.DictReader(LEDGER.open(encoding='utf-8-sig')))
    assert len(rows)==10 and len({r['action_id'] for r in rows})==10
    assert all(r['m2_authorization']=='AUTHORIZED_EXACT_SCOPE' for r in rows)
    src=(outdir/'luisa_24_heures.html').read_text(encoding='utf-8')
    assert src==(outdir/'index.html').read_text(encoding='utf-8')
    new=mutate_html(src)
    (outdir/'luisa_24_heures.html').write_text(new,encoding='utf-8')
    (outdir/'index.html').write_text(new,encoding='utf-8')
    return sha_bytes(new.encode('utf-8'))

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: build_v101111_m2_authorised_mutation.py OUTDIR')
    print(build(sys.argv[1]))
