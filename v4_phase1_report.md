# One Tree Tool v4 · Phase 1 report

**Date:** 2026-09-02  
**Source:** `base/reconciled_tree_v3_lenses.html` (v3.49) — the handoff name `reconciled_tree_v3_lenses_2.html` is not in git.  
**Outputs:** `reconciled_tree_v4.html`, `v4_notation_extract.csv`

Geometry (`pts`, `draw`, node `x,y,r`) is unchanged. `note:""` was added on every node, path, lens, and mode. Plate copy stays `[COPY PENDING]` / `[PENDING RULINGS R-1–R-3]`. Kether has no new overlay label, tooltip, or text. No serpent/Apep glyph. No arrows on Flame of Consumption, Dual Current, or Immersion.

## Menu counts

v3.49 visible rail (lenses in groups with `hidden` false, plus 2 modes): **18 lenses + 2 modes = 20**.

v4.0 after cuts (reversible `hidden:true` + `cut`, not deleted):

| State | Lenses | Modes | Total rail entries |
|---|---|---|---|
| PRACTITIONER off (public only) | 10 | 0 | **10** |
| PRACTITIONER on | 19 | 2 | **21** |
| Still hidden (C1–C5) | 46 | — | not in rail |

Public (toggle off): The Tree, Elements, Circuits, Night Face, Forces, Symbols, Neteru, Paths, Medu Netjer · Rulers, Medu Netjer · Paths.

Practitioner-visible when toggle is on: Soul, Strengths, Questions, Week, Timing, Rulerships, Decans, Divine ♂, Divine ♀, plus Paths mode and Kau mode.

Cut entries remain hidden even with the toggle on, until Ali uncuts them: C1 circuit (1), C2 deity stubs (20), C3 path stubs (22), C4 weaknesses + distortions (2), C5 body (1).

The spec’s ~63 → ~11 assumed the 20+22 single-deity/path lenses were already in the v3 menu. They were not; they are created in v4 and immediately cut.

Hash: `#tier=practitioner` persists the toggle. `note` fields render as a badge under `desc` only when the toggle is on.

## Axes classification

Classifier (from `PATHS` geometry, not a second coordinate table):

- **horizontal** = `flame`, `dualcurrent`, `immersion` (named rungs; no arrows)
- **vertical** = every `pts` node on one pillar (left / center / right), including the tapered left/right pillars that do not share a single x
- **diagonal** = everything else
- **Time and Location** is vertical (center pillar)
- **Divine Skill & Command** is vertical by geometry and flagged on the overlay as the ruled exception (`RULING` marker)

| Class | Count | Path ids |
|---|---|---|
| Vertical | 7 | `skillcommand`, `dwelling`, `revelation`, `utterance`, `fate`, `solarrising`, `timelocation` |
| Horizontal | 3 | `flame`, `dualcurrent`, `immersion` |
| Diagonal | 12 | `covenant`, `images`, `fortress`, `conjoin`, `appliedskill`, `coiledpower`, `regeneration`, `impulse`, `eyeofmatter`, `pillarharmony`, `hiddeninfluence`, `huntcatch` |

Unclassified `PATHS`: **none** (22 = 7+12+3).

Spec hoped 6 / 11 / 3. Honest geometry is **7 / 12 / 3**. If `skillcommand` is pulled out as the ruled exception, verticals become 6 — but diagonals stay 12, not 11. Exact same-x verticals (taper ignored) are only 5: `skillcommand`, `utterance`, `fate`, `solarrising`, `timelocation`. `dwelling` (205→232) and `revelation` (595→568) fail a strict same-x test because the pillars taper.

## Notation extract

`v4_notation_extract.csv`: **77 data rows** (78 lines with header). `proposed_action` left blank for Ali (`rewrite | note | delete`).

## Check-strings

```
grep -c "v4.0" reconciled_tree_v4.html                      # 7
grep -c 'id:"circuits"' reconciled_tree_v4.html             # 1
grep -c 'id:"nightface"' reconciled_tree_v4.html            # 1
grep -c 'cut:"C2"' reconciled_tree_v4.html                  # 20
grep -c 'cut:"C3"' reconciled_tree_v4.html                  # 22
grep -c "tierToggle" reconciled_tree_v4.html                # 10
grep -c "COPY PENDING" reconciled_tree_v4.html              # 10
grep -c "PENDING RULINGS R-1" reconciled_tree_v4.html       # 1
wc -l v4_notation_extract.csv                               # 78
```

Unchanged-geometry: `pts` diff vs v3.49 is empty.

Notes on `grep -c "v4.0"`: GNU grep treats `.` as any character, so the count includes base64 false positives. Literal `v4.0` occurs **4** times: the required Phase 1 header comment, plus the three bumped version strings (title, subtitle, inspector `ver`). The check’s “expect 3” cannot hold once that header is added.

## Circuits shell

- Belt Drive: overlay order from `NODES`/`PATHS`; moving dashes; fire/air/water opposed-pair glyphs (no arrows); Create/Annihilate color-only; Fault view `pocket:[]` empty.
- Axes: Verticals / Diagonals / Horizontals chips.
- Face of Ra: eyes on `flame` and `immersion` midpoints; mouth on `dualcurrent`; throat at gevurah; tongue tick at gevurah end of `utterance`; gaze chesed→netzach along `fate`; ears at malkuth only; kether ear commented out (R-4).
- Body of Ptah: sub-selection + plate `[PENDING RULINGS R-1–R-3]`; no overlay.
- Worked: W1 (immersion `pending:true` for R-5), W2 (ground glyph at malkuth; hod feminine half-ring), W3 (ascent `coiledpower` only, pause, descent).
