#!/usr/bin/env python3
"""Verify that the embedded MeduNetjer subset covers the live glyph corpus."""

import base64
import io
import re
from pathlib import Path

from fontTools.ttLib import TTFont


HTML = Path(__file__).with_name("reconciled_tree_v3_lenses.html")
source = HTML.read_text(encoding="utf-8")
used = sorted({ord(char) for char in source if 0x13000 <= ord(char) <= 0x1345F})

print(len(used), "hieroglyph codepoints in build:")
print(",".join(f"U+{codepoint:05X}" for codepoint in used))

declared_match = re.search(r"/\* FULL GLYPH CMAP: ([^*]+) \*/", source)
font_match = re.search(
    r"font-family:'MeduNetjer';\s*"
    r"src:url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)",
    source,
)
assert declared_match and font_match, "MeduNetjer subset metadata is missing"

declared = [int(value[2:], 16) for value in declared_match.group(1).split(",")]
assert declared == used, "FULL GLYPH CMAP comment is stale; re-run the audit"

font_bytes = base64.b64decode(font_match.group(1))
font = TTFont(io.BytesIO(font_bytes))
cmap = {codepoint for table in font["cmap"].tables for codepoint in table.cmap}
missing = sorted(set(used) - cmap)
assert not missing, "subset misses: " + ",".join(f"U+{codepoint:05X}" for codepoint in missing)

print(f"coverage PASS: {len(used)}/{len(used)}; subset {len(font_bytes)} bytes")
