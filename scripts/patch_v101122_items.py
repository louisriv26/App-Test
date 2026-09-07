#!/usr/bin/env python3
from pathlib import Path
import re,sys,hashlib,json,difflib
TREE=Path(sys.argv[1]); ITEM=sys.argv[2]
P=TREE/'index.html'; txt=P.read_text(encoding='utf-8')

def span(txt,name):
 m=re.search(r'function\s+'+re.escape(name)+r'\s*\(',txt)
 if not m: raise AssertionError(name)
 i=txt.find('(',m.start()); dep=0;q=None;esc=False
 while i<len(txt):
  c=txt[i]
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==q:q=None
  else:
   if c in "'\"`":q=c
   elif c=='(':dep+=1
   elif c==')':
    dep-=1
    if dep==0:i+=1;break
  i+=1
 b=txt.find('{',i); assert b>=0
 i=b+1;dep=1;q=None;esc=False;line=False;block=False
 while i<len(txt) and dep:
  c=txt[i];n=txt[i+1] if i+1<len(txt) else ''
  if line:
   if c=='\n':line=False
   i+=1;continue
  if block:
   if c=='*' and n=='/':block=False;i+=2;continue
   i+=1;continue
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==q:q=None
   i+=1;continue
  if c=='/' and n=='/':line=True;i+=2;continue
  if c=='/' and n=='*':block=True;i+=2;continue
  if c in "'\"`":q=c;i+=1;continue
  if c=='{':dep+=1
  elif c=='}':dep-=1
  i+=1
 return m.start(),i

def replace_func(txt,name,new):
 s,e=span(txt,name);return txt[:s]+new.strip()+txt[e:]

def insert_after(txt,name,new):
 s,e=span(txt,name);return txt[:e]+'\n'+new.strip()+'\n'+txt[e:]

def sync(t):
 P.write_text(t,encoding='utf-8');(TREE/'luisa_24_heures.html').write_text(t,encoding='utf-8')

def evidence(before,after):
 out=TREE/'evidence'/'v101122'/'per_item';out.mkdir(parents=True,exist_ok=True)
 diff=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='before',tofile='after'))
 (out/f'{ITEM}_diff.patch').write_text(diff,encoding='utf-8')
 (out/f'{ITEM}_sha.json').write_text(json.dumps({'item':ITEM,'before_sha256':hashlib.sha256(before.encode()).hexdigest(),'after_sha256':hashlib.sha256(after.encode()).hexdigest(),'changed_lines':sum(1 for x in diff.splitlines() if x.startswith(('+','-')) and not x.startswith(('+++','---')))},indent=2)+'\n')

before=txt
if ITEM=='H24-01':
 new=r'''function buildHourEndActions(hour, next) {
  const isTerminal = Number(hour && hour.hour_number) === 24;
  const nextHour = isTerminal ? null : next;
  const nextLabel = nextHour ? ('Prier la ' + ordinalHeure(nextHour.hour_number)) : '';
  const nextBtn = nextHour ? `<button type="button" class="hour-end-btn primary" onclick="openHour(${nextHour.hour_number})">${escHtml(nextLabel)}</button>` : '';
  const title = isTerminal ? 'Après cette Heure' : 'Continuer le chemin des Heures';
  const note = isTerminal
    ? 'Vous pouvez réfléchir à cette Heure, l’approfondir ou la reprendre depuis le début.'
    : 'Après cette méditation, vous pouvez réfléchir, approfondir ou poursuivre vers l’Heure suivante.';
  return `<div class="hour-end-actions" id="hourEndActions"><div class="hour-end-title">${title}</div><div class="hour-end-note">${note}</div><div class="hour-end-buttons"><button type="button" class="hour-end-btn" onclick="goToHourTab('reflections', 'reflectionsContent')">Réflexion et pratique</button><button type="button" class="hour-end-btn" onclick="goToHourTab('linked', 'linkedTextsContent')">Approfondir</button><button type="button" class="hour-end-btn" onclick="scrollReaderToTop()">↟ Revenir au début</button>${nextBtn}</div></div>`;
}'''
 txt=replace_func(txt,'buildHourEndActions',new)
elif ITEM=='H24-02':
 funcs=r'''function buildHour24CyclePanel(hour) {
  if (Number(hour && hour.hour_number) !== 24) return '';
  const p = getProgressSnapshot();
  if (!p.complete) {
    return `<div class="hour-end-actions cycle" id="hour24CyclePanel"><div class="hour-end-title">VOTRE PARCOURS</div><div class="hour-end-note"><strong>${p.count}/24</strong> Heures marquées comme méditées.</div><div class="hour-end-buttons"><button type="button" class="hour-end-btn primary" onclick="showProgressView()">Voir ma progression</button><button type="button" class="hour-end-btn" onclick="showCompletedHoursView()">Revoir les Heures méditées</button></div></div>`;
  }
  return `<div class="hour-end-actions cycle" id="hour24CyclePanel"><div class="hour-end-title">LE CYCLE DES 24 HEURES EST ACCOMPLI</div><div class="hour-end-note"><strong>24/24</strong> Heures marquées comme méditées.</div><div class="hour-end-buttons"><button type="button" class="hour-end-btn primary" onclick="restartTwentyFourHours({requireComplete:true,destination:'hour1'})">↻ Recommencer depuis la 1re Heure</button><button type="button" class="hour-end-btn" onclick="showProgressView()">Voir ma progression</button><button type="button" class="hour-end-btn" onclick="showCompletedHoursView()">Revoir les Heures méditées</button></div></div>`;
}
function refreshHourEndCycleUI() {
  if (state.view !== 'reader' || Number(state.currentHour) !== 24) return false;
  const host = document.getElementById('hour24CyclePanelHost');
  if (!host) return false;
  const content = document.getElementById('content');
  const y = content ? content.scrollTop : null;
  const hour = CORPUS.hours.find(h => Number(h.hour_number) === 24);
  host.innerHTML = buildHour24CyclePanel(hour);
  if (content && y !== null) content.scrollTop = y;
  return true;
}'''
 txt=insert_after(txt,'buildHourEndActions',funcs)
 s,e=span(txt,'renderReader'); block=txt[s:e]
 old='''    </div>\n  </div>`;'''
 repl='''    </div>\n    ${Number(hour.hour_number) === 24 ? `<div id="hour24CyclePanelHost">${buildHour24CyclePanel(hour)}</div>` : ''}\n  </div>`;'''
 assert old in block
 block=block.replace(old,repl,1)
 txt=txt[:s]+block+txt[e:]
elif ITEM=='H24-03':
 s,e=span(txt,'markMeditee');block=txt[s:e]
 old="  if (committed.ok) showToast(wasRead ? 'Progression retirée' : ('✓ ' + ordinalHeure(n) + ' méditée'));"
 new="  refreshHourEndCycleUI();\n  if (committed.ok) showToast(wasRead ? 'Progression retirée' : ('✓ ' + ordinalHeure(n) + ' méditée'));"
 assert old in block;block=block.replace(old,new,1);txt=txt[:s]+block+txt[e:]
elif ITEM=='H24-04':
 new=r'''function restartTwentyFourHours(options = {}) {
  const p = getProgressSnapshot();
  const requireComplete = !!(options && options.requireComplete === true);
  const destination = options && options.destination === 'hour1' ? 'hour1' : 'home';
  if (requireComplete && !p.complete) {
    showToast('Le cycle n’est pas encore complet.');
    refreshHourEndCycleUI();
    return false;
  }
  if (!p.hasCycleState) { showToast('Votre progression est déjà à zéro'); return false; }
  const label = requireComplete || p.complete ? 'Recommencer depuis la 1re Heure ?' : 'Réinitialiser ma progression ?';
  const message = `${label}\n\nVotre progression des 24 Heures sera remise à zéro :\n• statuts « Méditée »\n• positions de reprise\n• onglets de lecture enregistrés\n• historique quotidien de méditation\n\nVos surlignages, notes et préférences seront conservés.`;
  if (!window.confirm(message)) return false;
  const beforeSnapshot = buildPersonalSnapshotFromState();
  state.readHours = new Set();
  state.lastParas = Object.create(null);
  state.hourTabs = Object.create(null);
  state.meditationLog = [];
  state.currentHour = null;
  /* Preserve the canonical reset contract: clear the resume Hour before committing. */
  state.lastHour = null;
  const committed = commitDurableChange(beforeSnapshot, 'Réinitialisation de la progression');
  if (!committed.ok) {
    updateRightContextPanel(); buildSidebar();
    refreshHourEndCycleUI();
    return false;
  }
  try { sessionStorage.removeItem(STAGE6A_ANCHOR_STORAGE_KEY); } catch(e) {}
  if (destination === 'hour1') {
    openHour(1, false);
    showToast('Progression réinitialisée. Vous recommencez à la 1re Heure.');
  } else {
    showHome();
    showToast('Progression réinitialisée. Vous pouvez recommencer à la 1re Heure.');
  }
  return true;
}'''
 txt=replace_func(txt,'restartTwentyFourHours',new)
elif ITEM=='H24-05':
 s,e=span(txt,'renderReader');block=txt[s:e]
 old='''      <button class="nav-btn" onclick="openHour(${next?next.hour_number:-1})" ${!next?'disabled':''}>\n        <span><span class="nav-label">Suivante</span>${next?escHtml(next.short_title.slice(0,28)):''}</span>\n        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>\n      </button>'''
 new='''      ${next ? `<button class="nav-btn" onclick="openHour(${next.hour_number})">\n        <span><span class="nav-label">Suivante</span>${escHtml(next.short_title.slice(0,28))}</span>\n        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>\n      </button>` : ''}'''
 assert old in block;block=block.replace(old,new,1);txt=txt[:s]+block+txt[e:]
elif ITEM=='H24-06':
 # precise current-facing runtime strings; Help is intentionally untouched.
 replacements={
  "'Parcours terminé. Vous pouvez commencer un nouveau cycle tout en conservant vos surlignages et notes.'":"'Les 24 Heures sont marquées comme méditées. Vous pouvez recommencer depuis la 1re Heure tout en conservant vos surlignages et notes.'",
  "'Aucune Heure n’est encore marquée comme lue.'":"'Aucune Heure n’est encore marquée comme méditée.'",
  "'Revoir les Heures terminées'":"'Revoir les Heures méditées'",
  "'Parcours terminé'":"'Cycle accompli'",
  "'Heures marquées comme lues'":"'Heures marquées comme méditées'",
  "Aucune Heure terminée pour le moment. Marquez une Heure comme lue lorsque vous souhaitez l’ajouter à votre progression.":"Aucune Heure n’est encore marquée comme méditée. Appuyez sur « Méditée » après avoir médité une Heure pour l’ajouter à votre progression.",
  "Retrouvez les Heures marquées comme lues et recommencez un cycle lorsque vous le souhaitez.":"Retrouvez les Heures marquées comme méditées et gérez votre progression.",
  ">Heures terminées<":">Heures méditées<",
  "Relisez une Heure déjà marquée comme lue ou revenez à votre progression.":"Relisez une Heure déjà marquée comme méditée ou revenez à votre progression.",
  ">Revoir les Heures terminées<":">Revoir les Heures méditées<",
 }
 for a,b in replacements.items(): txt=txt.replace(a,b)
elif ITEM=='H24-07':
 # persistent bottom-nav Accueil was independently verified on progress/completed views in all five profiles before this patch.
 txt=txt.replace('<button type="button" class="resume-panel-btn" onclick="showHome()">Revenir à l’Accueil</button>','')
 txt=txt.replace('<button type="button" class="hour-end-btn" onclick="showHome()">⌂ Revenir à l’Accueil</button>','')
elif ITEM=='H24-08':
 # release identity only; detailed metadata/report regeneration occurs in finalizer.
 txt=txt.replace("const APP_VERSION = 'v101.121';","const APP_VERSION = 'v101.122';")
 txt=txt.replace("const APP_EVIDENCE_STAGE = 'FOUR_PASS_REPORT_TOOLING_RECONCILIATION_R1';","const APP_EVIDENCE_STAGE = 'HOUR24_END_OF_CYCLE_STATE_AND_ACTION_HIERARCHY_R1';")
else: raise SystemExit('unknown item')
if txt==before: raise AssertionError(f'{ITEM}: no change')
sync(txt);evidence(before,txt)
print(ITEM,hashlib.sha256(txt.encode()).hexdigest())
