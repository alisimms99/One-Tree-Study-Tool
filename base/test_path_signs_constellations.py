#!/usr/bin/env python3
"""Contract checks for geometry-derived Path Signs sphere constellations."""

import ast
import re
from pathlib import Path


source = Path(__file__).with_name("reconciled_tree_v3_lenses.html").read_text(encoding="utf-8")

path_block = re.search(r"const PATHS = \[(.*?)\n\];", source, re.S)
assert path_block, "PATHS is missing"
paths = []
for row in re.findall(r'^\s*\{id:"[^"]+".*$', path_block.group(1), re.M):
    path_id = re.search(r'id:"([^"]+)"', row).group(1)
    points = ast.literal_eval("[" + re.search(r'pts:\[([^\]]+)\]', row).group(1) + "]")
    draw_match = re.search(r'draw:\[([^\]]+)\]', row)
    draw = ast.literal_eval("[" + draw_match.group(1) + "]") if draw_match else points
    paths.append((path_id, points, draw))

expected = {
    "kether": (3, 0),
    "chokmah": (5, 0),
    "binah": (5, 0),
    "ausar": (0, 3),
    "chesed": (5, 1),
    "gevurah": (5, 1),
    "tiphereth": (2, 2),
    "netzach": (5, 0),
    "hod": (5, 0),
    "yesod": (6, 0),
    "malkuth": (3, 0),
}
actual = {}
for sphere_id in expected:
    terminal = sum(sphere_id in (draw[0], draw[-1]) for _, points, draw in paths if sphere_id in points)
    transit = sum(sphere_id not in (draw[0], draw[-1]) for _, points, draw in paths if sphere_id in points)
    actual[sphere_id] = (terminal, transit)
assert actual == expected, f"geometry-derived constellation counts changed: {actual}"

assert 'const CONST_ORDER = "clockwise12";' in source
assert 'const CONST_TRANSITS = "halflight";' in source
assert "const SIGN_MASS = {" in source
for entry in (
    "dualcurrent:1.25",
    "immersion:1.20",
    "appliedskill:1.10",
    "timelocation:1.10",
    "pillarharmony:1.10",
    "fortress:0.90",
    "dwelling:0.90",
    "flame:0.95",
):
    assert entry in source, f"missing SIGN_MASS entry {entry}"

assert "function spherePathConstellation(" in source
assert "function constellationDepartureAngle(" in source
assert "function applyPathSignConstellation(" in source
assert "function pathSignConstellationHtml(" in source
assert "const-terminal" in source and "const-transit" in source and "const-dim" in source
assert "IN TRANSIT" in source
assert "v3.49" in source and "+ sphere constellations" in source

print("Path Signs constellation contract PASS:", actual)
