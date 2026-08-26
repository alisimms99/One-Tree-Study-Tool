#!/usr/bin/env python3
"""Static contract for the ratified Path Signs lens."""

import re
from pathlib import Path


source = Path(__file__).with_name("reconciled_tree_v3_lenses.html").read_text(encoding="utf-8")

expected = {
    "covenant": ("𓆄", "𓏛", "H6 (+Y1)", "feather of Ma'at — the covenant that lasts"),
    "images": ("𓁷", "", "D2", "face (ḥr) — the conscious perceiving face; Sia turned to the channel"),
    "flame": ("𓊮", "", "Q7", "brazier with flame — purifying fire / overcurrent burned off"),
    "skillcommand": ("𓊹", "", "R8", "nṯr flag — the Divine; Ptah's creative authority"),
    "fortress": ("𓊅", "𓊛", "O36 (+P1)", "wall (inbw) — the enclosure that shelters"),
    "conjoin": ("𓍇", "", "U19", "adze — the Opening-of-Mouth blade that cuts AND rejoins"),
    "dwelling": ("𓉐", "𓆰", "O1 (+M2)", "house (pr) — the dwelling / receptacle where things grow"),
    "revelation": ("𓎿", "", "W14", "ḥes libation-jar — the directed pour / step-down"),
    "dualcurrent": ("𓏭", "𓊡", "Z4 (+P5)", "two strokes — the dual; two poles held apart"),
    "appliedskill": ("𓂧", "", "D46", "hand (d) — the working hand; craft into result"),
    "coiledpower": ("𓆓", "𓄲", "I10 (+F46)", "cobra (ḏ) — the coil; power wound and stored"),
    "utterance": ("𓀁", "", "A2", "man, hand-to-mouth — the effective word / decree"),
    "fate": ("𓂩", "", "D47", "open hand — the grasp; Iusaaset 'the Hand of Atum'"),
    "regeneration": ("𓆰", "𓆣", "M2 (+L1)", "sprouting plant — germination; the grain-bed rising"),
    "impulse": ("𓂸", "𓍝", "D52 (+U38)", "phallus (mt) — Atum's self-kindled seed; the first impulse"),
    "immersion": ("𓈗", "", "N35A", "three ripples (mw) — water; the submersion"),
    "solarrising": ("𓈍", "𓇳", "N28 (+N5)", "sun over hill (ḫꜥ) — the rising; appearance in glory"),
    "eyeofmatter": ("𓁹", "", "D4", "eye (ir) — clear sight of the material"),
    "pillarharmony": ("𓏣", "", "Y8", "sistrum (sššt) — the Resonator; the chord struck"),
    "hiddeninfluence": ("𓁶", "", "D1", "head (ḥꜣ) — the subconscious/autonomic"),
    "huntcatch": ("𓌕", "", "T11", "arrow (šsr) — the hunt; Sagittarius the Archer"),
    "timelocation": ("𓏴", "𓇾", "Z9 (+N16)", "crossed sticks — the cross/mark/seal that fixes the coordinate"),
}

block_match = re.search(r"const PATH_SIGNS = \{(.*?)\n\};", source, re.S)
assert block_match, "PATH_SIGNS is missing"
rows = re.findall(
    r'^\s*(\w+):\s*\{p:"([^"]*)",\s*s:"([^"]*)",\s*gard:"([^"]*)",\s*gloss:"([^"]*)"\},?$',
    block_match.group(1),
    re.M,
)
actual = {key: tuple(values) for key, *values in rows}
assert actual == expected, "PATH_SIGNS does not match the ratified proof sheet"
assert "apep" not in actual

assert "const SIGNS_SHOW_PAIR_INDIAGRAM = false;" in source
assert "const SIGN_NUDGE = {" in source
assert '{id:"medu",name:"Medu Netjer · Rulers"' in source
assert '{id:"pathsigns",name:"Medu Netjer · Paths"' in source
assert "'pathsigns'" in re.search(r"const COMPARE_BLOCK=new Set\(\[(.*?)\]\)", source).group(1)
assert re.search(r"\.psign\{[^}]*font-size:20px", source, re.S)
assert ".path-sign-primary" in source and ".path-sign-pair" in source
assert "const pathSignLabels={};" in source
assert "function renderPathSign(" in source
assert "function pathSignHtml(" in source
assert "signsOn=lensId==='pathsigns'" in source
assert "pathSignLabels" in source[source.index("function dress("):source.index("const rail=")]
assert "v3.48" in source and "+ sphere constellations" in source

print("Path Signs static contract PASS: 22 ratified entries")
