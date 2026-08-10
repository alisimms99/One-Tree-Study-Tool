# CURSOR BUILD PROMPT — The Reconciled Tree: Paths Mode + Kau Mode
Paste this file's contents as your Cursor prompt, with this repo open. 2026-08-09.

## Context
`base/reconciled_tree_v3_lenses.html` is a single-file, data-driven render of an **eleven-sphere** Kemetic Tree of Life. Architecture: a `#rail` of lens buttons, an SVG `#tree` (nodes + paths built in JS from data objects `LENSES`, `pathGroups`, `sphereGroups`, `lensTexts`), and an inspector `#panel`. One click re-dresses the tree; registers appear in the inspector. Dark theme, IBM Plex Mono, CSS variables (incl. `--gold`).

**⚠ Version check first:** this base is titled v3.18. If a newer local render exists, build on that instead and tell me.

## Task 1 — PATHS MODE (primary)
Add a top-level mode (rail entry or mode toggle) for **path study**:

1. **Ruler gallery.** A strip/grid of clickable deity portraits from `images/` (thumbnail size; filenames identify deities). Include every deity that rules at least one path.
2. **On deity click:** highlight all paths that deity rules in `var(--gold)` (or a complementary accent if gold conflicts with an active lens); dim non-ruled paths; keep spheres visible for orientation. A ruler may govern multiple paths — highlight all simultaneously.
3. **Inspector caption:** for the clicked ruler (and on hover/click of an individual highlighted path), show:
   - the path's name and letter/grade metadata,
   - condensed **lore** (≤120 words) drawn from `data/Path_Trump_Book_Entries_v3_FINAL.md`,
   - the path's **function in the tree's machinery**, drawn from `data/Path_Trump_Semantics_v2.md` and `data/Dua_Station_Operating_Doctrine_PENDING_2026-08-09.md`.
4. **Ruler→path mapping:** derive it from the data files (`reconciled_tree_v2.json` + the Book Entries name each path's ruler). Do not invent any assignment. If a path's ruler is ambiguous or missing in the sources, render it with a visible `[ruler unconfirmed]` stub and list all stubs in a code comment at the top of the new section.

## Task 2 — KAU MODE (secondary, smaller)
Add a mode rendering the **Fourteen Kau of Re** per `data/Kau_Comparative_Register_v2_RATIFIED.md`, exactly as specified in its §Layer tables and §O4:

1. **Layer 1 — the fourteen-seat ring** around/beside the tree: each seat shows its Lanzone source-form, gloss, and presiding deity (thumbnail where an image exists). Seats **1, 9, 11** carry a visible *contested* marker; open alternates (5, 8, 10, 13) display as `alt:` subtext; the six stable-core seats (2, 3, 6, 10 + hearing #12, seeing #9) get a visually distinct treatment (e.g., solid vs dashed ring).
2. **Layer 2 — barque overlay:** Hu, Sia, Heka as presiding positions above the ring (use `Hu_revised_raw.png`, `Sia_revised_raw.png`, `03_heka.png`), Sutekh at the prow position linked to seat #11. **Never depict or name Apep anywhere in the render.**
3. **Layer 3 — benefaction annotations:** venerability→Amen-Ra, faithfulness→Auset, skill→Ptah, shown as small annotation chips on those sphere rulers, visually distinct from seats.
4. Tier marks (G/T3, T2+G, etc.) visible as small mono superscripts, matching the register.

## Hard constraints (violating any of these fails the build)
- **Geometry:** the existing eleven-sphere layout only. Never substitute a ten-sephirot Golden Dawn tree or its path arrangement.
- **No invented content.** All lore, functions, rulers, seats, tiers come from `data/`. Condensing is allowed; paraphrase-invention is not. Gaps render as visible stubs, never as filler.
- **Preserve everything existing:** all current lenses, inspector registers, and styling must keep working. Extend the data-driven pattern; don't fork the architecture. Single-file output.
- **Aesthetic continuity:** existing fonts, CSS variables, spacing idiom. Gold = `var(--gold)`.
- **Version-bump** the title/sub line (e.g., v3.19 or next local number) and note the additions.
- Image paths relative (`images/…`); assume the HTML ships alongside the folders as-is.

## Deliverable
The updated single HTML file + a short CHANGES.md listing: stubs encountered, any ruler ambiguities, and anything in the data files that conflicted (do not resolve conflicts yourself — list them for review).
