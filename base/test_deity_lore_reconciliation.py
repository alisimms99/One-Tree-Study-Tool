#!/usr/bin/env python3
"""Contract for Register v2 FINAL deity-name captions."""

import re
from pathlib import Path


source = Path(__file__).with_name("reconciled_tree_v3_lenses.html").read_text(encoding="utf-8")

expected = {
    "maat": ("𓆄𓏏𓁐", "mꜣꜥt"),
    "sekhmet": ("𓌂𓏏𓆗", "sḫmt"),
    "het_heru": ("𓉗𓅃", "ḥwt-ḥr"),
    "iusaaset": ("𓂻𓅱𓋴𓉻𓂝𓋴𓁐", "jw.s-ꜥꜣ.s"),
    "auset": ("𓊨𓏏𓁐", "ꜣst"),
    "tefnut": ("𓏏𓆑𓈖𓏏𓆗", "tfnt"),
    "sia": ("𓋴𓇋𓄿𓀭", "sjꜣ"),
    "heka": ("𓎛𓂓𓀭", "ḥkꜣ"),
    "shu": ("𓈙𓅱𓀭", "šw"),
    "set_higher": ("𓋴𓏏𓐍𓃩", "stẖ"),
    "hu": ("𓎛𓅱𓀭", "ḥw"),
    "atum": ("𓇋𓏏𓅓𓅱𓀭", "jtm(w)"),
    "khonsu": ("𓐍𓈖𓊃𓅱", "ḫnsw"),
    "wepwawet": ("𓄋𓅱𓄿𓅱𓏏𓈐𓃧", "wp-wꜣwt"),
    "geb": ("𓅬𓃀", "gb"),
}
unchanged = {
    "taweret": ("𓏏𓄿𓅨𓂋𓏏𓆗", "tAwrt · Gardiner TꜢ-wrt"),
    "ptah": ("𓊪𓏏𓎛𓀭", "ptH · Gardiner ptḥ · Budge Ptaḥ"),
    "anubis": ("𓇋𓈖𓊪𓅱𓃣", "inpw · Gardiner ỉnpw · Budge Ȧnpu"),
    "ausar": ("𓊨𓁹𓀭", "wsir, Asr · Gardiner Wśỉr · Budge Ȧusȧr"),
    "heru": ("𓅃", "Hr, Hrw · Gardiner Ḥr(.w) · Budge Ḥeru"),
}


def lore_row(key):
    match = re.search(
        rf"^\s*{key}:\{{hiero:\"([^\"]+)\"(.*?),translit:\"([^\"]+)\"",
        source,
        re.M,
    )
    assert match, f"DEITY_LORE.{key} is missing"
    return match.group(1), match.group(2), match.group(3)


for key, (hiero, translit) in expected.items():
    actual_hiero, middle, actual_translit = lore_row(key)
    assert actual_hiero == hiero, f"{key} hiero mismatch: {actual_hiero}"
    assert actual_translit.split(" · ", 1)[0] == translit, f"{key} translit mismatch: {actual_translit}"
    if key == "iusaaset":
        assert "hieroFlag" not in middle, "Iusaaset must not render an unverified flag"

for key, (hiero, translit) in unchanged.items():
    actual_hiero, _, actual_translit = lore_row(key)
    assert (actual_hiero, actual_translit) == (hiero, translit), f"{key} changed incidentally"

maat_path = re.search(r'covenant:\s*\{g:"([^"]+)"', source)
assert maat_path and maat_path.group(1) == expected["maat"][0]
assert "LORE HIERO SOURCE = REGISTER V2 FINAL" in source
assert "Tree_of_Dua_Deity_Hieroglyph_Register_v2_FINAL_2026-08-25" in source
assert "L.hieroFlag?" in source, "future caption-flag mechanism was removed"
assert "𓌷𓂝𓏏𓁦" not in source
assert "𓏏𓍃𓀭" not in source
assert "Amunet appears twice" not in source
assert "Amenet appears twice" in source
assert "v3.49" in source and "+ lore-register reconciliation" in source

print("DEITY_LORE reconciliation PASS: 15 patched, 5 unchanged")
