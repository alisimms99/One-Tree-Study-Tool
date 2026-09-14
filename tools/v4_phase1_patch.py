#!/usr/bin/env python3
"""One Tree Tool v4 Phase 1 patcher. Exact-match substitutions only."""
from __future__ import annotations

import csv
import re
import shutil
from pathlib import Path

ROOT = Path("/workspace")
# Spec name (v3.49). Identical copy also lives at base/reconciled_tree_v3_lenses.html.
SRC = ROOT / "reconciled_tree_v3_lenses_2.html"
if not SRC.exists():
    SRC = ROOT / "base" / "reconciled_tree_v3_lenses.html"
DST = ROOT / "reconciled_tree_v4.html"
CSV_PATH = ROOT / "v4_notation_extract.csv"


def assert_once(hay: str, needle: str, label: str) -> None:
    n = hay.count(needle)
    if n != 1:
        raise SystemExit(f"ASSERT FAIL {label}: count={n} (want 1)\n--- needle start ---\n{needle[:180]}\n---")


def sub_once(hay: str, old: str, new: str, label: str) -> str:
    assert_once(hay, old, label)
    return hay.replace(old, new, 1)


TOKEN_RE = re.compile(
    r"T2-L|§\d+[a-z]?|[Pp]ass[- ]\d+|Ruling #?\d+|render-verified|RULED|PENDING|\bT[123]\b"
)


def _unescape(raw: str) -> str:
    if "\\" not in raw:
        return raw
    try:
        return bytes(raw, "utf-8").decode("unicode_escape")
    except Exception:
        return raw


def extract_notation(src_text: str) -> list[dict]:
    html, script = src_text.split("<script>", 1)
    rows: list[dict] = []
    seen = set()

    def add(otype: str, oid: str, field: str, full: str) -> None:
        full = _unescape(full).replace("\n", " ").strip()
        for tm in TOKEN_RE.finditer(full):
            key = (otype, oid, field, tm.group(0), full)
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "object_type": otype,
                "object_id": oid,
                "field": field,
                "matched_token": tm.group(0),
                "full_string": full[:800],
                "proposed_action": "",
            })

    # HTML chrome (tier legend is user-visible)
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", html, re.S):
        add("html", "tierPop", "copy", re.sub(r"<[^>]+>", " ", m.group(1)))

    # Lenses / modes
    for block_name, otype in (("LENSES", "lens"), ("MODES", "mode")):
        m = re.search(rf"const {block_name}\s*=\s*\[(.*?)\n\];", script, re.S)
        if not m:
            continue
        for obj in re.finditer(r'\{id:"([^"]+)",(.*?)\}(?=,|\n\])', m.group(1), re.S):
            oid, body = obj.group(1), obj.group(2)
            for fm in re.finditer(r'\b(name|desc|note)\s*:\s*"((?:\\.|[^"\\])*)"', body):
                add(otype, oid, fm.group(1), fm.group(2))

    # PATH_META
    m = re.search(r"const PATH_META\s*=\s*\{(.*?)\n\};", script, re.S)
    if m:
        for obj in re.finditer(r"(\w+):\{(.*?)\}(?=,|\n)", m.group(1), re.S):
            oid, body = obj.group(1), obj.group(2)
            for fm in re.finditer(r'\b(subtitle|lore|function)\s*:\s*"((?:\\.|[^"\\])*)"', body):
                add("path_meta", oid, fm.group(1), fm.group(2))

    # PATHS markers (user-visible on the tree)
    m = re.search(r"const PATHS\s*=\s*\[(.*?)\n\];", script, re.S)
    if m:
        for obj in re.finditer(r'\{id:"([^"]+)",(.*?)\}(?=,|\n\])', m.group(1), re.S):
            oid, body = obj.group(1), obj.group(2)
            for fm in re.finditer(r'\b(name|marker|mshort|ruler|circuit)\s*:\s*"((?:\\.|[^"\\])*)"', body):
                add("path", oid, fm.group(1), fm.group(2))

    # Kau seats
    m = re.search(r"const KAU_SEATS\s*=\s*\[(.*?)\n\];", script, re.S)
    if m:
        for obj in re.finditer(r"\{n:(\d+),(.*?)\}(?=,|\n\])", m.group(1), re.S):
            oid, body = obj.group(1), obj.group(2)
            for fm in re.finditer(r'\b(seat|gloss|deity|tier|note)\s*:\s*"((?:\\.|[^"\\])*)"', body):
                add("kau_seat", oid, fm.group(1), fm.group(2))

    # Star anchors (keyed by decade number)
    m = re.search(r"const STAR_ANCHORS\s*=\s*\{(.*?)\n\};", script, re.S)
    if m:
        for obj in re.finditer(r"(\d+)\s*:\s*\{(.*?)\}(?=,|\n\s*\d+\s*:|\n\s*$)", m.group(1), re.S):
            oid, body = obj.group(1), obj.group(2)
            for fm in re.finditer(
                r'\b(star|starTier|power|powerTier|planets|planetsTier|verdict)\s*:\s*"((?:\\.|[^"\\])*)"',
                body,
            ):
                add("star_anchor", oid, fm.group(1), fm.group(2))
            for fm in re.finditer(r'label\s*:\s*"((?:\\.|[^"\\])*)"', body):
                add("star_anchor", oid, "label", fm.group(1))
            for fm in re.finditer(r'flags:\s*\[(.*?)\]', body, re.S):
                for sm in re.finditer(r'"((?:\\.|[^"\\])*)"', fm.group(1)):
                    add("star_anchor", oid, "flags", sm.group(1))

    # Decan notes (inspector)
    m = re.search(r"const DECAN_NOTES\s*=\s*\{(.*?)\};", script, re.S)
    if m:
        for fm in re.finditer(r'(\d+)\s*:\s*"((?:\\.|[^"\\])*)"', m.group(1)):
            add("decan_note", fm.group(1), "note", fm.group(2))

    # Timing / election visible strings
    for fm in re.finditer(
        r'\b(tier|day_tier|figure_tier|function_tier|title|function)\s*:\s*"((?:\\.|[^"\\])*)"',
        script,
    ):
        # skip already-captured structured blocks by allowing dup keys via seen
        around = script[max(0, fm.start() - 80) : fm.start()]
        oid = ""
        km = re.findall(r"\b([A-Za-z][A-Za-z0-9_]*)\s*:\s*\{", around)
        if km:
            oid = km[-1]
        add("timing", oid or "timing", fm.group(1), fm.group(2))

    # Inspector templates
    for m in re.finditer(r"`([^`]{0,1200})`", script):
        blob = m.group(1)
        if not TOKEN_RE.search(blob):
            continue
        if not any(x in blob for x in ("class=", "<div", "<h2", "Pass-50", "eyebrow", "prov")):
            continue
        add("panel", "inspector", "template", re.sub(r"\s+", " ", blob))

    return rows


NEW_LENSES = r'''const LENSES = [
 {id:"sky",name:"The Tree",tier:"public",note:"",desc:"Foundation: planets, sign-seats, path names, markers, rulers."},
 {id:"neteru",name:"Neteru",tier:"public",note:"",desc:"Sphere rulers — pairs and soles (§3b, canon)."},
 {id:"soul",name:"Soul",tier:"practitioner",note:"",desc:"The soul-parts: Ba, Akh, Sekhem, Ka, Ib, Sheut, Ren, Khet, Sah."},
 {id:"timing",name:"Timing",tier:"practitioner",note:"",desc:"Election console — intent to cell, scored against decan window, planetary day, moon mode, and tactical figure. Full register; STAND_DOWN cells never recommended."},
 {id:"week",name:"Week",tier:"practitioner",note:"",desc:"Akradinbosom: days and Akan pairs. Akua operates with Set; she does not reside at Hod. Geb & Renenutet receive dua on ANY day — the earth-pair stands outside the weekday rotation."},
 {id:"body",name:"Body",tier:"practitioner",hidden:true,cut:"C5",note:"",desc:"Chakras & seed sounds. The 8th chakra lies beneath the feet — soundless; seat unassigned."},
 {id:"elements",name:"Elements",tier:"public",note:"",desc:"Five horizontal strata: Fire · Spirit · Air · Water · Earth."},
 {id:"forces",name:"Forces",tier:"public",note:"",desc:"The force register; Magnetism at Malkuth per the Circuit Doctrine."},
 {id:"symbols",name:"Symbols",tier:"public",hidden:false,note:"",desc:"The teaching layer — the tree read at sight."},
 {id:"medu",name:"Medu Netjer · Rulers",tier:"public",note:"",desc:"The written layer — each road wears the name of its ruler in the god's own script. Select a path to read the name large."},
 {id:"pathsigns",name:"Medu Netjer · Paths",tier:"public",note:"",desc:"The sign layer — each road bears its own concept-sign, the force of the path written as one glyph. Select a path for the sign, its pairing, and its meaning."},
 {id:"strengths",name:"Strengths",tier:"practitioner",note:"",desc:"The circuit working — with the pass-33 re-seatings and Gestation at the Moon."},
 {id:"weaknesses",name:"Weaknesses",tier:"practitioner",hidden:true,cut:"C4",note:"",desc:"The circuit malfunctioning — each capacity overdriven or starved."},
 {id:"distortions",name:"Distortions",tier:"practitioner",hidden:true,cut:"C4",note:"",desc:"The office inverted — all eleven nodes. The Qliphoth, replaced."},
 {id:"rulerships",name:"Rulerships",tier:"practitioner",note:"",desc:"Dominion pairs — Free Will and Fertility stand unpaired on the pillar."},
 {id:"questions",name:"Questions",tier:"practitioner",note:"",desc:"What consciousness asks at each station. Left: space. Right: time."},
 {id:"circuit",name:"The Circuit",tier:"practitioner",hidden:true,cut:"C1",note:"",desc:"§4d — rail, neutral, ground, supply, bus, winding, magnet. The operator closes switches."},
 {id:"decans",name:"Decans",tier:"practitioner",note:"",desc:"The 36 decades + the epagomenal Geb-cell as a ring around the tree — the sky surrounds; nothing lands on a sphere or path. Per the Naos of the Decades (T1 monument; von Bomhard’s “war machine / texts of execration,” T2, confirmed via associate T2-L). All 37 cells named (Chronos-canonical, Pass 50; the alternate chat names printed as T2-L variants, not harmonized). Command: Ra → Shu (promoted, theater commander) → Thoth (Lord of the Books) → Sekhmet/Sirius (field-regent, T2-L) → the 36. Sopdet keys the ring at Solar Rising; the year anchors to the heliacal rising of Sirius. Effect-texts = Negative/martial register; effects-content and live-decade computation remain Sphere-of-Iah / Strike Window territory; the competitive-ops overlay is private and print-excluded."},
 {id:"divmasc",name:"Divine ♂",tier:"practitioner",note:"",desc:"The Tree of Dua — the masculine godform seated in each sphere. Click a sphere to light the paths that touch it."},
 {id:"divfem",name:"Divine ♀",tier:"practitioner",note:"",desc:"The Tree of Dua — the feminine layer as a receptive chalice: the sole-masculine central axis (Amen · Ausar · Heru) descends as the Kamutef seed-ray through Auset into Geb. Amenet appears twice — Red-Crowned Amenet-Menit at Binah (Saturn), solar-crowned Amenet-Rait haloed at Chesed (Jupiter). Click a sphere to light its paths."},
 {id:"paths",name:"Paths",tier:"public",note:"",desc:"[COPY PENDING]"},
 {id:"nightface",name:"Night Face",tier:"public",note:"",desc:"[COPY PENDING]"},
 {id:"circuits",name:"Circuits",tier:"public",note:"",desc:"[COPY PENDING]"},
 {id:"maat",name:"Ma'at",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"sekhmet",name:"Sekhmet",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"taweret",name:"Taweret",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"het_heru",name:"Het-Heru",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"iusaaset",name:"Iusaaset",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"auset",name:"Auset",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"tefnut",name:"Tefnut",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"sia",name:"Sia",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"ptah",name:"Ptah",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"anubis",name:"Anpu (Anubis)",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"heka",name:"Heka",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"shu",name:"Shu",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"set_higher",name:"Set (higher form)",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"hu",name:"Hu",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"ausar",name:"Ausar",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"atum",name:"Atum",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"heru",name:"Heru",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"khonsu",name:"Khonsu",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"wepwawet",name:"Wepwawet",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"geb",name:"Geb",tier:"practitioner",hidden:true,cut:"C2",note:"",desc:""},
 {id:"covenant",name:"Written Covenant",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"images",name:"Sequenced Images",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"flame",name:"Flame of Consumption",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"skillcommand",name:"Divine Skill & Command",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"fortress",name:"Mobile Fortress",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"conjoin",name:"Conjoining & Separation",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"dwelling",name:"Fertile Dwelling",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"revelation",name:"Flowing Revelation",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"dualcurrent",name:"The Dual Current",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"appliedskill",name:"Applied Skill",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"coiledpower",name:"Coiled Power",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"utterance",name:"Forceful Utterance",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"fate",name:"Grasping Fate",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"regeneration",name:"Regeneration",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"impulse",name:"Divine Impulse",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"immersion",name:"Immersion",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"solarrising",name:"Solar Rising",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"eyeofmatter",name:"Eye of Matter",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"pillarharmony",name:"Pillar of Harmony",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"hiddeninfluence",name:"Hidden Influence",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"huntcatch",name:"Hunt & Catch",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""},
 {id:"timelocation",name:"Time and Location",tier:"practitioner",hidden:true,cut:"C3",note:"",desc:""}
];'''

CSS = r'''
  /* —— v4 Phase 1: practitioner toggle, night face, circuits shell —— */
  #tierToggle{margin-left:8px; background:transparent; border:1px solid #3A4060; border-radius:4px;
    font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:.16em; color:#8A91AC;
    padding:4px 9px; cursor:pointer; transition:color .15s, border-color .15s, background .15s}
  #tierToggle:hover{color:var(--gold); border-color:var(--gold)}
  #tierToggle[aria-pressed="true"]{color:var(--gold); border-color:var(--gold); background:#171C30}
  #lensSubbar{display:none; position:absolute; top:10px; left:12px; z-index:7; max-width:min(520px,70%);
    font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:.08em}
  #lensSubbar.on{display:flex; flex-wrap:wrap; gap:5px; align-items:center}
  #lensSubbar .chip{background:#171C30; border:1px solid #3A4060; color:#B0B8D0; border-radius:3px;
    padding:4px 8px; cursor:pointer; font:inherit; letter-spacing:.08em; text-transform:uppercase}
  #lensSubbar .chip.on{color:var(--gold); border-color:var(--gold)}
  #lensSubbar .chip.pending{opacity:.7; border-style:dashed}
  .note-badge{margin:8px 0 12px; padding:6px 8px; background:var(--papyrus2); border-left:3px solid #8A6D1F;
    font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:.04em; color:#5A4A22; line-height:1.45}
  .note-badge .k{font-size:8px; letter-spacing:.18em; text-transform:uppercase; color:#8A6D1F; margin-bottom:2px}
  .sphere.night-halo circle.body{filter:drop-shadow(0 0 10px #6B2A4A) drop-shadow(0 0 4px #C0392B); stroke:#8A3A4A; stroke-width:3}
  .pgroup.night-halo .path-line{stroke:#8A3A4A; stroke-width:2.8; filter:drop-shadow(0 0 6px #6B2A4A)}
  .pgroup.axis-dim .path-line{opacity:.18}
  .pgroup.axis-on .path-line{stroke:var(--gold); stroke-width:2.8}
  .pgroup.circ-dim .path-line{opacity:.22}
  .pgroup.circ-rev .path-line{stroke:#8A3A4A; stroke-width:2.6; stroke-dasharray:5 4}
  .circ-current{fill:none; stroke:var(--gold); stroke-width:2.4; stroke-dasharray:8 6; stroke-linecap:round;
    pointer-events:none; animation:circDash 1.1s linear infinite}
  .circ-current.down{animation-name:circDash}
  .circ-current.up{animation-name:circDashUp}
  .circ-current.stoch{stroke-dasharray:2 7; stroke:#C9A24A; opacity:.85}
  @keyframes circDash{to{stroke-dashoffset:-56}}
  @keyframes circDashUp{to{stroke-dashoffset:56}}
  .circ-art{pointer-events:none; fill:none}
  .circ-art.create{stroke:#D4A93C}
  .circ-art.annihilate{stroke:#C0392B}
  .circ-whirl{transform-box:fill-box; transform-origin:center; animation:circSpin 12s linear infinite}
  @keyframes circSpin{to{transform:rotate(360deg)}}
  .circ-dot{fill:var(--gold); stroke:none; pointer-events:none}
  .circ-except{fill:var(--gold); font-family:'IBM Plex Mono',monospace; font-size:8px; letter-spacing:.08em}
  .circ-ground{stroke:var(--gold); fill:none; stroke-width:1.6; pointer-events:none}
  .hod-fem-half{fill:none; stroke:#E6A0B8; stroke-width:3; pointer-events:none; filter:drop-shadow(0 0 6px #E6A0B8)}
  .ra-art{pointer-events:none; fill:none; stroke:#E6C765; stroke-width:1.4; opacity:.55}
  .ra-art.fill{fill:#E6C765; stroke:none; opacity:.4}
'''

JS = r'''
/* ================= v4 Phase 1 — tiers, cuts, circuits shell ================= */
let practitionerOn=false;
let nightfaceSub='seats';
let circuitsSub='belt';
let beltFlameMode='create';
let beltFault=false;
let beltPendingImmersion=true;
let axesChip='verticals';
let workedId='W1';
let workedPhase='ascent';

const PILLAR_LEFT=new Set(['binah','gevurah','hod']);
const PILLAR_CENTER=new Set(['kether','ausar','tiphereth','yesod','malkuth']);
const PILLAR_RIGHT=new Set(['chokmah','chesed','netzach']);
function pillarOf(id){
  if(PILLAR_LEFT.has(id)) return 'left';
  if(PILLAR_CENTER.has(id)) return 'center';
  if(PILLAR_RIGHT.has(id)) return 'right';
  return null;
}
function axisClassOf(p){
  if(p.id==='flame'||p.id==='dualcurrent'||p.id==='immersion') return 'horizontal';
  const pillars=new Set((p.pts||[]).map(pillarOf).filter(Boolean));
  if(pillars.size===1) return 'vertical';
  return 'diagonal';
}
const AXIS_VERTICAL=PATHS.filter(p=>axisClassOf(p)==='vertical').map(p=>p.id);
const AXIS_DIAGONAL=PATHS.filter(p=>axisClassOf(p)==='diagonal').map(p=>p.id);
const AXIS_HORIZONTAL=PATHS.filter(p=>axisClassOf(p)==='horizontal').map(p=>p.id);

const CIRCUIT_PLATES={
  belt:{title:"Belt Drive",desc:"[COPY PENDING]",note:"",readmore:"",pocket:[]},
  axes:{title:"Axes",desc:"[COPY PENDING]",note:"",readmore:""},
  ra:{title:"Face of Ra",desc:"[COPY PENDING]",note:"",readmore:""},
  ptah:{title:"Body of Ptah",desc:"[PENDING RULINGS R-1–R-3]",note:"",readmore:""},
  worked:{title:"Worked Circuits",desc:"[COPY PENDING]",note:"",readmore:""},
  W1:{title:"W1 The Roar",desc:"[COPY PENDING]",note:"",readmore:"",trace:["flame","dwelling","utterance","immersion","pillarharmony"],pending:["immersion"]},
  W2:{title:"W2 The Grounding Strike",desc:"[COPY PENDING]",note:"",readmore:"",trace:["coiledpower","eyeofmatter","timelocation"]},
  W3:{title:"W3 The One Who Hears",desc:"[COPY PENDING]",note:"",readmore:"",ascent:["coiledpower"],descent:["dualcurrent","utterance","hiddeninfluence","timelocation"]}
};

function rulersSeatedAt(id){
  const blob=((L.neteru&&L.neteru[id])||[]).join(' ').toLowerCase();
  return RULERS.filter(r=>{
    if(r.id==='set_lower') return false;
    if(id==='kether') return false;
    const nm=r.name.toLowerCase();
    if(r.id==='set_higher') return /sutekh|\bset\b/.test(blob) && id==='hod';
    const key=nm.replace(/\(.*?\)/g,'').replace(/'/g,'').trim().split(/[\s-]+/)[0];
    return key && blob.replace(/'/g,'').indexOf(key)>=0;
  });
}

(function seedNotes(){
  for(const id in NODES){ if(NODES[id].note==null) NODES[id].note=""; }
  PATHS.forEach(p=>{ if(p.note==null) p.note=""; });
  LENSES.forEach(l=>{ if(l.note==null) l.note=""; });
  MODES.forEach(m=>{
    if(m.note==null) m.note="";
    m.tier=m.tier||'practitioner';
  });
})();

const circLayer=el('g',{id:'v4circ'});
svg.appendChild(circLayer);

function noteBadgeHtml(obj){
  if(!practitionerOn || !obj || !obj.note) return '';
  return '<div class="note-badge"><div class="k">Note</div>'+obj.note+'</div>';
}
function lensVisible(l){
  if(!l) return false;
  if(l.hidden) return false;
  if(!practitionerOn && l.tier!=='public') return false;
  return true;
}
function modeVisible(m){
  if(!m) return false;
  if(!practitionerOn && m.tier!=='public') return false;
  return true;
}

const LENS_GROUPS_V4=[
  {head:'Structure', ids:['sky','elements','circuits','nightface']},
  {head:'Consciousness', ids:['soul','forces','symbols','strengths','questions']},
  {head:'Practice', ids:['week','timing','rulerships','decans']},
  {head:'Divine', ids:['neteru','paths','medu','pathsigns','divmasc','divfem']}
];

const railModesBox=document.createElement('div'); railModesBox.id='railModes';
const railLensesBox=document.createElement('div'); railLensesBox.id='railLenses';
rail.appendChild(railModesBox); rail.appendChild(railLensesBox);

function rebuildRail(){
  railModesBox.innerHTML=''; railLensesBox.innerHTML='';
  const visModes=MODES.filter(modeVisible);
  if(visModes.length){
    railModesBox.insertAdjacentHTML('beforeend','<div class="railhead">Modes</div>');
    visModes.forEach(m=>{
      const b=document.createElement('button');
      b.className='mode-btn'; b.textContent=m.name; b.dataset.id=m.id;
      b.addEventListener('click',()=>{ if(compareArmed) setCompareArmed(false); clearSel();activeRuler=null;setMode(m.id);});
      railModesBox.appendChild(b);
    });
  }
  LENS_GROUPS_V4.forEach(g=>{
    const vis=g.ids.map(id=>LENSES.find(x=>x.id===id)).filter(lensVisible);
    if(!vis.length) return;
    railLensesBox.insertAdjacentHTML('beforeend','<div class="railhead">'+g.head+'</div>');
    vis.forEach(addLensBtn);
  });
  document.querySelectorAll('#rail .lens-btn').forEach(b=>b.classList.toggle('on',!activeMode && b.dataset.id===activeLens));
  document.querySelectorAll('#rail .mode-btn').forEach(b=>b.classList.toggle('on',!!activeMode && b.dataset.id===activeMode));
  paintCompareChrome();
}

const tierToggle=document.getElementById('tierToggle');
function setPractitioner(on, fromHash){
  practitionerOn=!!on;
  if(tierToggle){
    tierToggle.setAttribute('aria-pressed', practitionerOn?'true':'false');
    tierToggle.classList.toggle('on', practitionerOn);
  }
  rebuildRail();
  const still=LENSES.find(l=>l.id===activeLens);
  if(still && !lensVisible(still) && !activeMode){
    activeMode=null; dress('sky'); home(LENSES.find(l=>l.id==='sky'));
  } else if(!document.querySelector('.sel') && !activeMode){
    const lens=LENSES.find(l=>l.id===activeLens);
    if(lens) home(lens);
  }
  if(!fromHash) syncHash();
}
if(tierToggle){
  tierToggle.addEventListener('click',()=>setPractitioner(!practitionerOn));
}

function pathD(p){
  const pts=pathGeom(p);
  return pts.map((q,i)=>(i?'L':'M')+q.x+' '+q.y).join(' ');
}
function midOf(pid){
  const p=PATHS.find(x=>x.id===pid); if(!p) return {x:0,y:0};
  return pointAt(pathGeom(p), 0.5);
}
function endOf(pid, which){
  const p=PATHS.find(x=>x.id===pid); if(!p) return {x:0,y:0};
  const pts=pathGeom(p);
  return which==='start'?pts[0]:pts[pts.length-1];
}

function clearCirc(){
  circLayer.innerHTML='';
  PATHS.forEach(p=>{
    const g=pathGroups[p.id]; if(!g) return;
    g.classList.remove('circ-dim','circ-rev','axis-dim','axis-on','night-halo');
  });
  for(const id in sphereGroups){
    sphereGroups[id].classList.remove('night-halo');
  }
}

function drawCurrent(pid, cls){
  const p=PATHS.find(x=>x.id===pid); if(!p) return;
  el('path',{class:'circ-current '+(cls||''), d:pathD(p)}, circLayer);
}
function opposedFire(at, mode){
  const g=el('g',{class:'circ-art '+(mode||'create'), transform:'translate('+at.x+' '+at.y+')'}, circLayer);
  el('path',{class:'circ-art '+(mode||'create'), d:'M-16,-6 A18,10 0 0,1 16,-6'}, g);
  el('path',{class:'circ-art '+(mode||'create'), d:'M16,6 A18,10 0 0,1 -16,6'}, g);
}
function opposedAir(at){
  const g=el('g',{class:'circ-art create', transform:'translate('+at.x+' '+at.y+')'}, circLayer);
  el('path',{class:'circ-art create', d:'M-14,8 C-10,-16 10,-16 14,8'}, g);
  el('path',{class:'circ-art create', d:'M-8,10 C-4,-8 4,-8 8,10'}, g);
}
function opposedWater(at){
  const g=el('g',{class:'circ-art create circ-whirl', transform:'translate('+at.x+' '+at.y+')'}, circLayer);
  el('ellipse',{class:'circ-art create', cx:0, cy:0, rx:16, ry:10}, g);
  el('ellipse',{class:'circ-art create', cx:0, cy:0, rx:10, ry:6}, g);
  el('ellipse',{class:'circ-art create', cx:0, cy:0, rx:5, ry:3}, g);
}

function renderBelt(){
  const order=[
    ['images','down'],
    ['dwelling','down'],['utterance','down'],
    ['revelation','down'],['fate','down'],
    ['coiledpower','down'],['appliedskill','down'],
    ['eyeofmatter','stoch'],['hiddeninfluence','stoch'],['pillarharmony','stoch'],['huntcatch','stoch'],
    ['timelocation','stoch']
  ];
  PATHS.forEach(p=>{ if(pathGroups[p.id]) pathGroups[p.id].classList.add('circ-dim'); });
  order.forEach(([id,cls])=>{
    if(pathGroups[id]) pathGroups[id].classList.remove('circ-dim');
    drawCurrent(id, cls);
  });
  ['flame','dualcurrent','immersion'].forEach(id=>{ if(pathGroups[id]) pathGroups[id].classList.remove('circ-dim'); });
  const ketherPt=NODES.kether;
  el('circle',{class:'circ-dot', cx:ketherPt.x, cy:ketherPt.y, r:4}, circLayer);
  opposedFire(midOf('flame'), beltFlameMode);
  opposedAir(midOf('dualcurrent'));
  opposedWater(midOf('immersion'));
  if(beltFault){
    (CIRCUIT_PLATES.belt.pocket||[]).forEach(id=>{
      if(sphereGroups[id]) sphereGroups[id].classList.add('night-halo');
      if(pathGroups[id]) pathGroups[id].classList.add('night-halo');
    });
  }
}
function renderAxes(){
  const want=axesChip==='verticals'?'vertical':axesChip==='diagonals'?'diagonal':'horizontal';
  PATHS.forEach(p=>{
    const g=pathGroups[p.id]; if(!g) return;
    const on=axisClassOf(p)===want || (want==='vertical' && p.id==='timelocation');
    g.classList.add(on?'axis-on':'axis-dim');
  });
  const sc=PATHS.find(p=>p.id==='skillcommand');
  if(sc){
    const mid=pointAt(pathGeom(sc), 0.28);
    el('text',{class:'circ-except', x:mid.x+10, y:mid.y-6}, circLayer).textContent='RULING';
  }
}
function renderFaceOfRa(){
  const fe=midOf('flame'), im=midOf('immersion'), dc=midOf('dualcurrent');
  const gv=NODES.gevurah, ch=NODES.chesed, nz=NODES.netzach, mk=NODES.malkuth, ut=endOf('utterance','start');
  function eye(pt){
    el('ellipse',{class:'ra-art', cx:pt.x, cy:pt.y, rx:18, ry:9}, circLayer);
    el('circle',{class:'ra-art fill', cx:pt.x, cy:pt.y, r:4}, circLayer);
  }
  eye(fe); eye(im);
  el('path',{class:'ra-art', d:'M'+(dc.x-28)+' '+(dc.y+4)+' Q'+dc.x+' '+(dc.y+16)+' '+(dc.x+28)+' '+(dc.y+4)}, circLayer);
  el('circle',{class:'ra-art', cx:gv.x, cy:gv.y, r:gv.r+8}, circLayer);
  el('line',{class:'ra-art', x1:ut.x, y1:ut.y, x2:ut.x-16, y2:ut.y+8}, circLayer);
  el('line',{class:'ra-art', x1:ch.x, y1:ch.y, x2:nz.x, y2:nz.y}, circLayer);
  function ear(pt){
    el('path',{class:'ra-art', d:'M'+(pt.x-22)+' '+(pt.y-8)+' Q'+(pt.x-34)+' '+pt.y+' '+(pt.x-22)+' '+(pt.y+8)}, circLayer);
    el('path',{class:'ra-art', d:'M'+(pt.x+22)+' '+(pt.y-8)+' Q'+(pt.x+34)+' '+pt.y+' '+(pt.x+22)+' '+(pt.y+8)}, circLayer);
  }
  ear(mk);
  /* R-4: kether ear position left EMPTY pending ruling — do not render.
     el('g',{class:'ra-art kether-ear-pending'},circLayer); ear(NODES.kether); */
}
function renderWorked(){
  const plate=CIRCUIT_PLATES[workedId]; if(!plate) return;
  PATHS.forEach(p=>{ if(pathGroups[p.id]) pathGroups[p.id].classList.add('circ-dim'); });
  if(workedId==='W1'){
    (plate.trace||[]).forEach(id=>{
      if(id==='immersion' && !beltPendingImmersion) return;
      if(pathGroups[id]) pathGroups[id].classList.remove('circ-dim');
      if(id==='pillarharmony' && pathGroups[id]) pathGroups[id].classList.add('circ-rev');
      drawCurrent(id, id==='flame'?'down':'down');
    });
    opposedFire(midOf('flame'), 'annihilate');
  } else if(workedId==='W2'){
    (plate.trace||[]).forEach(id=>{
      if(pathGroups[id]) pathGroups[id].classList.remove('circ-dim');
      drawCurrent(id,'down');
    });
    const mk=NODES.malkuth;
    [-10,0,10].forEach((dy,i)=>{
      const w=18-i*4;
      el('line',{class:'circ-ground', x1:mk.x-w, y1:mk.y+mk.r+8+dy, x2:mk.x+w, y2:mk.y+mk.r+8+dy}, circLayer);
    });
    const hd=NODES.hod;
    el('path',{class:'hod-fem-half', d:'M '+hd.x+' '+(hd.y-hd.r)+' A '+hd.r+' '+hd.r+' 0 0 1 '+hd.x+' '+(hd.y+hd.r)}, circLayer);
  } else if(workedId==='W3'){
    const ids=workedPhase==='ascent'?(plate.ascent||[]):(plate.descent||[]);
    ids.forEach(id=>{
      if(pathGroups[id]) pathGroups[id].classList.remove('circ-dim');
      drawCurrent(id, workedPhase==='ascent'?'up':'down');
    });
  }
}

function renderNightface(){
  const src=nightfaceSub==='seats'?'weaknesses':'distortions';
  for(const id in NODES){
    // Lock: kether is a bare terminal — no label/tooltip/text on new overlays.
    const vals=(id==='kether')?[]:((L[src]&&L[src][id])?L[src][id]:[]);
    lensTexts[id].forEach((t,i)=>{
      t.textContent=vals[i]||'';
      t.classList.toggle('gold', !!vals[i]);
    });
    if(vals.filter(Boolean).length) sphereGroups[id].classList.add('night-halo');
  }
}

function renderV4Lens(lensId){
  clearCirc();
  const bar=document.getElementById('lensSubbar');
  if(bar){ bar.classList.remove('on'); bar.innerHTML=''; }
  if(lensId==='nightface'){
    renderNightface();
    paintSubbar([
      {id:'seats', lab:'Seats', on:nightfaceSub==='seats', fn:()=>{nightfaceSub='seats'; dress('nightface'); home(LENSES.find(l=>l.id==='nightface'));}},
      {id:'roads', lab:'Roads', on:nightfaceSub==='roads', fn:()=>{nightfaceSub='roads'; dress('nightface'); home(LENSES.find(l=>l.id==='nightface'));}}
    ]);
  } else if(lensId==='circuits'){
    if(circuitsSub==='belt') renderBelt();
    else if(circuitsSub==='axes') renderAxes();
    else if(circuitsSub==='ra') renderFaceOfRa();
    else if(circuitsSub==='worked') renderWorked();
    const chips=[
      {id:'belt', lab:'Belt Drive', on:circuitsSub==='belt', fn:()=>{circuitsSub='belt'; dress('circuits'); showCircuitPlate();}},
      {id:'axes', lab:'Axes', on:circuitsSub==='axes', fn:()=>{circuitsSub='axes'; dress('circuits'); showCircuitPlate();}},
      {id:'ra', lab:'Face of Ra', on:circuitsSub==='ra', fn:()=>{circuitsSub='ra'; dress('circuits'); showCircuitPlate();}},
      {id:'ptah', lab:'Body of Ptah', on:circuitsSub==='ptah', fn:()=>{circuitsSub='ptah'; dress('circuits'); showCircuitPlate();}},
      {id:'worked', lab:'Worked Circuits ▸', on:circuitsSub==='worked', fn:()=>{circuitsSub='worked'; dress('circuits'); showCircuitPlate();}}
    ];
    if(circuitsSub==='belt'){
      chips.push({id:'create', lab:beltFlameMode==='create'?'Create':'Annihilate', on:true, fn:()=>{beltFlameMode=beltFlameMode==='create'?'annihilate':'create'; dress('circuits'); showCircuitPlate();}});
      chips.push({id:'fault', lab:'Fault view', on:beltFault, fn:()=>{beltFault=!beltFault; dress('circuits'); showCircuitPlate();}});
    }
    if(circuitsSub==='axes'){
      chips.push({id:'verticals', lab:'Verticals', on:axesChip==='verticals', fn:()=>{axesChip='verticals'; dress('circuits'); showCircuitPlate();}});
      chips.push({id:'diagonals', lab:'Diagonals', on:axesChip==='diagonals', fn:()=>{axesChip='diagonals'; dress('circuits'); showCircuitPlate();}});
      chips.push({id:'horizontals', lab:'Horizontals', on:axesChip==='horizontals', fn:()=>{axesChip='horizontals'; dress('circuits'); showCircuitPlate();}});
    }
    if(circuitsSub==='worked'){
      chips.push({id:'W1', lab:'W1 The Roar', on:workedId==='W1', fn:()=>{workedId='W1'; dress('circuits'); showCircuitPlate();}});
      chips.push({id:'W2', lab:'W2 Grounding Strike', on:workedId==='W2', fn:()=>{workedId='W2'; dress('circuits'); showCircuitPlate();}});
      chips.push({id:'W3', lab:'W3 One Who Hears', on:workedId==='W3', fn:()=>{workedId='W3'; workedPhase='ascent'; dress('circuits'); showCircuitPlate(); setTimeout(()=>{workedPhase='descent'; if(activeLens==='circuits'&&circuitsSub==='worked'){ dress('circuits'); showCircuitPlate(); }}, 1800);}});
      if(workedId==='W1') chips.push({id:'r5', lab:'R-5 immersion', on:beltPendingImmersion, pending:true, fn:()=>{beltPendingImmersion=!beltPendingImmersion; dress('circuits'); showCircuitPlate();}});
      if(workedId==='W3') chips.push({id:'phase', lab:workedPhase==='ascent'?'Ascent':'Descent', on:true, fn:()=>{workedPhase=workedPhase==='ascent'?'descent':'ascent'; dress('circuits'); showCircuitPlate();}});
    }
    paintSubbar(chips);
  } else if(lensId==='paths'){
    PATHS.forEach(p=>{ if(pathGroups[p.id]) pathGroups[p.id].classList.remove('dim'); });
  }
}

function paintSubbar(chips){
  const bar=document.getElementById('lensSubbar'); if(!bar) return;
  bar.classList.add('on'); bar.innerHTML='';
  chips.forEach(c=>{
    const b=document.createElement('button');
    b.type='button'; b.className='chip'+(c.on?' on':'')+(c.pending?' pending':'');
    b.textContent=c.lab; b.addEventListener('click', c.fn);
    bar.appendChild(b);
  });
}

function showCircuitPlate(){
  const key=circuitsSub==='worked'?workedId:circuitsSub;
  const plate=CIRCUIT_PLATES[key]||CIRCUIT_PLATES.worked;
  const lens=LENSES.find(l=>l.id==='circuits');
  setPanel(`
    <div class="eyebrow">Lens · Circuits</div>
    <h2>${plate.title}</h2>
    <h3 class="route">Phase 1 shell</h3>
    <div class="note">${plate.desc}</div>
    ${noteBadgeHtml(plate)}
    ${plate.readmore?field('Read more', plate.readmore):''}
    <div class="prov">Overlay geometry is read from NODES / PATHS. Plate copy awaits Ali approval.</div>`);
}

function showNeteruSeat(id){
  const n=NODES[id];
  const seated=(L.neteru&&L.neteru[id])?L.neteru[id].join(' '):'';
  let body='';
  rulersSeatedAt(id).forEach(r=>{
    const lore=DEITY_LORE[r.id]||{};
    const epithets=lore.epithets?'<ul class="epithets">'+lore.epithets.map(e=>'<li>'+(e.t?'<span class="tr">'+e.t+'</span> — ':'')+e.e+'</li>').join('')+'</ul>':'';
    const sub=[lore.pron?'“'+lore.pron+'”':'',lore.translit||''].filter(Boolean).join(' · ');
    body += portraitHtml(r.img,r.name);
    body += '<h2>'+r.name+'</h2>';
    if(sub) body += '<h3 class="route">'+sub+'</h3>';
    if(lore.hiero) body += '<div class="glyph-block"><div class="hiero-name">'+lore.hiero+'</div></div>';
    body += field('Name meaning', lore.meaning);
    body += field('Features', lore.features);
    body += field('Symbols', lore.symbols);
    body += field('Roles', lore.roles);
    body += field('Epithets', epithets);
    if(lore.invocation) body += '<div class="field"><div class="k">Invocation</div><blockquote class="invoke">'+lore.invocation.text+(lore.invocation.src?'<span class="src">— '+lore.invocation.src+'</span>':'')+'</blockquote></div>';
  });
  setPanel(`
    <div class="eyebrow">Neteru · ${n.seph}</div>
    <h2>${n.kem}</h2>
    <h3 class="route">${n.planet}</h3>
    ${field('Seated', seated)}
    ${body}
    ${noteBadgeHtml(n)}
    <div class="prov">Deity desc / lore / img by reference from DEITY_LORE and RULERS — not copied. Kether remains a bare terminal.</div>`);
}

function showPathFromObject(pid){
  const p=PATHS.find(x=>x.id===pid), m=PATH_META[pid];
  if(!p) return;
  const route=p.pts.map((q,i)=> (i>0&&i<p.pts.length-1)?'→ '+NODES[q].kem+' →':NODES[q].kem).join(' ');
  setPanel(`
    <div class="eyebrow">Path</div>
    <h2>${p.name}</h2>
    <h3 class="route">${m?'<i>'+m.subtitle+'</i> · ':''}${route}</h3>
    ${pathGlyphHtml(pid)}
    ${field('Marker · '+p.mtype,p.marker)}
    ${field('Ruler',p.ruler)}
    ${m?field('Lore',m.lore):''}
    ${m?field('Function in the tree',m.function):''}
    ${p.circuit?field('Circuit role',p.circuit):''}
    ${noteBadgeHtml(p)}
    <div class="prov">Path panel reads PATHS / PATH_META by reference.</div>`);
}
'''


def main() -> None:
    src = SRC.read_text(encoding="utf-8")
    rows = extract_notation(src)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["object_type", "object_id", "field", "matched_token", "full_string", "proposed_action"],
        )
        w.writeheader()
        w.writerows(rows)
    print(f"notation rows: {len(rows)} (plus header → {len(rows)+1} lines)")

    shutil.copyfile(SRC, DST)
    text = DST.read_text(encoding="utf-8")

    if text.count("v3.49") != 3:
        raise SystemExit(f"v3.49 count={text.count('v3.49')} want 3")
    text = text.replace("v3.49", "v4.0")

    text = sub_once(
        text,
        "<!DOCTYPE html>\n",
        "<!DOCTYPE html>\n<!-- v4.0 · Phase 1 · tiers + notation strip + circuits shell · 2026-09-02 -->\n",
        "header-comment",
    )

    old_lenses = text[text.index("const LENSES = [") : text.index("];", text.index("const LENSES = [")) + 2]
    text = sub_once(text, old_lenses, NEW_LENSES, "lenses-array")

    text = sub_once(text, "</style>", CSS + "\n</style>", "css")

    text = sub_once(
        text,
        '<button type="button" id="tierBtn" aria-expanded="false" aria-controls="tierPop" title="Tier vocabulary">TIERS ?</button>',
        '<button type="button" id="tierToggle" aria-pressed="false" title="Show practitioner lenses">PRACTITIONER</button>\n'
        '  <button type="button" id="tierBtn" aria-expanded="false" aria-controls="tierPop" title="Tier vocabulary">TIERS ?</button>',
        "tierToggle-html",
    )

    text = sub_once(
        text,
        '<div id="stage">',
        '<div id="stage">\n      <div id="lensSubbar" aria-label="Lens sub-selections"></div>',
        "lensSubbar",
    )

    text = sub_once(
        text,
        "if(lensId==='timing' && !activeMode) applyTimingRingDim(timingState.matchingIds);\n}",
        "if(lensId==='timing' && !activeMode) applyTimingRingDim(timingState.matchingIds);\n"
        "  if(typeof renderV4Lens==='function') renderV4Lens(lensId);\n}",
        "dress-hook",
    )

    text = sub_once(
        text,
        "const vals=(lensId==='elements'||lensId==='decans'||lensId==='timing')? (L.sky[id]||[]) : (L[lensId]?L[lensId][id]:[])||[];",
        "const vals=(lensId==='elements'||lensId==='decans'||lensId==='timing')? (L.sky[id]||[]) : (L[lensId]?L[lensId][id]:(lensId==='paths'?(L.sky[id]||[]):[]))||[];",
        "dress-paths-labels",
    )

    text = sub_once(
        text,
        "function parseHash(){\n  try{\n    const raw=(location.hash||'').replace(/^#/,'').trim();\n    if(!raw) return {lens:'sky', secondary:null, sel:null};",
        "function parseHash(){\n  try{\n    const raw0=(location.hash||'').replace(/^#/,'').trim();\n"
        "    const practitioner=/tier=practitioner/.test(raw0);\n"
        "    const raw=raw0.replace(/&?tier=practitioner/g,'').replace(/^&|&$/g,'').trim();\n"
        "    if(!raw) return {lens:'sky', secondary:null, sel:null, practitioner};",
        "parseHash-tier",
    )

    text = sub_once(
        text,
        "if(!LENSES.some(l=>l.id===lens)) return null;",
        "if(!LENSES.some(l=>l.id===lens && !l.hidden && !l.cut)) return null;",
        "parseHash-skip-cuts",
    )

    text = sub_once(
        text,
        "return {lens, secondary, sel};",
        "return {lens, secondary, sel, practitioner};",
        "parseHash-return",
    )

    text = sub_once(
        text,
        "function buildHash(){\n  if(activeMode) return null;\n  let h='#'+activeLens;",
        "function buildHash(){\n  if(activeMode) return practitionerOn?'#tier=practitioner':null;\n  let h='#'+activeLens;",
        "buildHash-mode",
    )

    text = sub_once(
        text,
        "return h;\n}\nfunction syncHash(){",
        "if(practitionerOn) h+=(h==='#'?'':'&')+'tier=practitioner';\n  return h;\n}\nfunction syncHash(){",
        "buildHash-append",
    )

    text = sub_once(
        text,
        "const st=state||{lens:'sky', secondary:null, sel:null};",
        "const st=state||{lens:'sky', secondary:null, sel:null, practitioner:false};\n"
        "    if(typeof setPractitioner==='function') setPractitioner(!!st.practitioner, true);",
        "applyHash-practitioner",
    )

    text = sub_once(
        text,
        "rail.insertAdjacentHTML('beforeend','<div class=\"railhead\">Modes</div>');\n"
        "MODES.forEach(m=>{\n"
        "  const b=document.createElement('button');\n"
        "  b.className='mode-btn'; b.textContent=m.name; b.dataset.id=m.id;\n"
        "  b.addEventListener('click',()=>{ if(compareArmed) setCompareArmed(false); clearSel();activeRuler=null;setMode(m.id);});\n"
        "  rail.appendChild(b);\n"
        "});\n"
        "const LENS_GROUPS=[\n"
        "  {head:'Structure', ids:['sky','elements','circuit','decans']},\n"
        "  {head:'Consciousness', ids:['soul','forces','strengths','weaknesses','distortions','questions']},\n"
        "  {head:'Practice', ids:['week','timing','rulerships']},\n"
        "  {head:'Divine', ids:['neteru','medu','pathsigns','divmasc','divfem']}\n"
        "];\n"
        "function addLensBtn(l){\n"
        "  const b=document.createElement('button');\n"
        "  b.className='lens-btn'; b.textContent=l.name; b.dataset.id=l.id;\n"
        "  b.addEventListener('click',()=>{\n"
        "    if(compareArmed){\n"
        "      if(!COMPARE_OK.has(l.id)) return;\n"
        "      if(l.id===activeLens){ secondaryLens=null; refreshCompareSecondaryClass(); dress(activeLens); syncHash(); return; }\n"
        "      if(!COMPARE_OK.has(activeLens)){\n"
        "        return;\n"
        "      }\n"
        "      secondaryLens=l.id;\n"
        "      refreshCompareSecondaryClass();\n"
        "      dress(activeLens);\n"
        "      syncHash();\n"
        "      return;\n"
        "    }\n"
        "    clearSel();activeMode=null;activeRuler=null;treewrap.classList.remove('paths-mode','kau-mode');highlightRulerPaths(null);secondaryLens=null;dress(l.id);home(l);syncHash();\n"
        "  });\n"
        "  rail.appendChild(b);\n"
        "}\n"
        "LENS_GROUPS.forEach(g=>{\n"
        "  rail.insertAdjacentHTML('beforeend','<div class=\"railhead\">'+g.head+'</div>');\n"
        "  g.ids.forEach(id=>{ const l=LENSES.find(x=>x.id===id); if(l && !l.hidden) addLensBtn(l); });\n"
        "});",
        "function addLensBtn(l){\n"
        "  const b=document.createElement('button');\n"
        "  b.className='lens-btn'; b.textContent=l.name; b.dataset.id=l.id;\n"
        "  b.addEventListener('click',()=>{\n"
        "    if(compareArmed){\n"
        "      if(!COMPARE_OK.has(l.id)) return;\n"
        "      if(l.id===activeLens){ secondaryLens=null; refreshCompareSecondaryClass(); dress(activeLens); syncHash(); return; }\n"
        "      if(!COMPARE_OK.has(activeLens)){\n"
        "        return;\n"
        "      }\n"
        "      secondaryLens=l.id;\n"
        "      refreshCompareSecondaryClass();\n"
        "      dress(activeLens);\n"
        "      syncHash();\n"
        "      return;\n"
        "    }\n"
        "    clearSel();activeMode=null;activeRuler=null;treewrap.classList.remove('paths-mode','kau-mode');highlightRulerPaths(null);secondaryLens=null;dress(l.id);home(l);syncHash();\n"
        "  });\n"
        "  railLensesBox.appendChild(b);\n"
        "}\n",
        "rail-rebuild-placeholder",
    )

    # home() note badge + circuits plate
    text = sub_once(
        text,
        "   <div class=\"note\">${lens.desc}</div>",
        "   <div class=\"note\">${lens.desc}</div>\n"
        "   ${noteBadgeHtml(lens)}",
        "home-note-badge",
    )

    text = sub_once(
        text,
        "if(!activeMode && lens && lens.id==='timing'){ showTimingLens(); return; }",
        "if(!activeMode && lens && lens.id==='timing'){ showTimingLens(); return; }\n"
        "  if(!activeMode && lens && lens.id==='circuits'){ showCircuitPlate(); return; }",
        "home-circuits",
    )

    # select() neteru + paths
    text = sub_once(
        text,
        "if(kind==='sphere'){\n    sphereGroups[id].classList.add('sel');",
        "if(kind==='sphere'){\n"
        "    if(activeLens==='neteru' && !activeMode){\n"
        "      sphereGroups[id].classList.add('sel');\n"
        "      PATHS.forEach(p=>{ if(p.pts.indexOf(id)>=0) pathGroups[p.id].classList.add('incident'); });\n"
        "      showNeteruSeat(id); syncHash(); return;\n"
        "    }\n"
        "    sphereGroups[id].classList.add('sel');",
        "select-neteru",
    )

    text = sub_once(
        text,
        "if(activeMode==='paths'){ showPathStudy(id); syncHash(); return; }",
        "if(activeMode==='paths' || activeLens==='paths'){ showPathFromObject(id); syncHash(); return; }",
        "select-paths-lens",
    )

    text = sub_once(
        text,
        "      ${rows}\n"
        "      ${decanRes}\n"
        "      <div class=\"prov\">Every register shown; blanks are canon. Full provenance per cell lives in the master dataset v3.32.</div>`);",
        "      ${rows}\n"
        "      ${decanRes}\n"
        "      ${noteBadgeHtml(n)}\n"
        "      <div class=\"prov\">Every register shown; blanks are canon. Full provenance per cell lives in the master dataset v3.32.</div>`);",
        "select-sphere-note",
    )

    text = sub_once(
        text,
        "      ${p.circuit?field('Circuit role',p.circuit):''}\n"
        "      <div class=\"prov\">Full provenance in the master dataset v3.32.</div>`);",
        "      ${p.circuit?field('Circuit role',p.circuit):''}\n"
        "      ${noteBadgeHtml(p)}\n"
        "      <div class=\"prov\">Full provenance in the master dataset v3.32.</div>`);",
        "select-path-note",
    )

    text = sub_once(
        text,
        "const COMPARE_OK=new Set(['neteru','soul','week','body','forces','symbols','strengths','weaknesses','distortions','rulerships','questions','circuit']);",
        "const COMPARE_OK=new Set(['neteru','soul','week','body','forces','symbols','strengths','rulerships','questions','nightface']);",
        "compare-ok",
    )

    # Inject v4 JS before inspector, and boot rebuildRail
    text = sub_once(
        text,
        "/* ================= inspector ================= */",
        JS + "\n/* ================= inspector ================= */",
        "inject-js",
    )

    text = sub_once(
        text,
        "(function boot(){\n"
        "  const st=parseHash();\n"
        "  if(st && (st.lens!=='sky' || st.secondary || st.sel || (location.hash||'').length>1)) applyHashState(st);\n"
        "  else { dress('sky'); home(); syncHash(); }\n"
        "})();",
        "(function boot(){\n"
        "  rebuildRail();\n"
        "  const st=parseHash();\n"
        "  if(st && st.practitioner) setPractitioner(true, true);\n"
        "  if(st && (st.lens!=='sky' || st.secondary || st.sel || st.practitioner || (location.hash||'').length>1)) applyHashState(st);\n"
        "  else { dress('sky'); home(); syncHash(); }\n"
        "})();",
        "boot",
    )

    # parseHash empty-raw must keep practitioner flag — already handled.
    # When raw is empty after stripping, first return now includes practitioner.

    # note:"" on every NODES / PATHS object (empty; Step 2 CSV governs later moves)
    import re as _re

    def add_node_notes(s: str) -> str:
        m = _re.search(r"const NODES = \{.*?\n\};", s, _re.S)
        if not m:
            raise SystemExit("ASSERT FAIL nodes-block: not found")
        block = m.group(0)
        if block.count('note:""') >= 11:
            return s
        new_block = _re.sub(
            r'(\b(?:kether|chokmah|binah|ausar|chesed|gevurah|tiphereth|netzach|hod|yesod|malkuth):\{)',
            r'\1note:"",',
            block,
        )
        if new_block.count('note:""') != 11:
            raise SystemExit(f"ASSERT FAIL node-notes: count={new_block.count('note:\"\"')} want 11")
        return s[: m.start()] + new_block + s[m.end() :]

    def add_path_notes(s: str) -> str:
        m = _re.search(r"const PATHS = \[.*?\n\];", s, _re.S)
        if not m:
            raise SystemExit("ASSERT FAIL paths-block: not found")
        block = m.group(0)
        if 'note:""' in block:
            return s
        new_block = _re.sub(r'\{id:"([^"]+)",name:', r'{id:"\1",note:"",name:', block)
        if new_block.count('note:""') != 22:
            raise SystemExit(f"ASSERT FAIL path-notes: count={new_block.count('note:\"\"')} want 22")
        # geometry guard: pts arrays must be identical
        old_pts = _re.findall(r"pts:\[[^\]]+\]", block)
        new_pts = _re.findall(r"pts:\[[^\]]+\]", new_block)
        if old_pts != new_pts:
            raise SystemExit("ASSERT FAIL path-notes mutated pts")
        return s[: m.start()] + new_block + s[m.end() :]

    text = add_node_notes(text)
    text = add_path_notes(text)

    text = sub_once(
        text,
        '{id:"paths",name:"Paths",desc:"Path study — click a path ruler to highlight every path that deity governs. Lore and tree-function in the inspector."}',
        '{id:"paths",name:"Paths",tier:"practitioner",note:"",desc:"Path study — click a path ruler to highlight every path that deity governs. Lore and tree-function in the inspector."}',
        "mode-paths-tier",
    )
    text = sub_once(
        text,
        '{id:"kau",name:"Kau",desc:"The Fourteen Kau of Re — Lanzone ring (Layer 1), barque overlay (Layer 2), benefaction annotations (Layer 3). Per Kau_Comparative_Register_v2_RATIFIED §O4."}',
        '{id:"kau",name:"Kau",tier:"practitioner",note:"",desc:"The Fourteen Kau of Re — Lanzone ring (Layer 1), barque overlay (Layer 2), benefaction annotations (Layer 3). Per Kau_Comparative_Register_v2_RATIFIED §O4."}',
        "mode-kau-tier",
    )

    DST.write_text(text, encoding="utf-8")
    print("wrote", DST, "bytes", DST.stat().st_size)


if __name__ == "__main__":
    main()
