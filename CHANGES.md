# CHANGES — v3.34 (Hieroglyphic names as text)

**v3.34** — seshkemet-derived name-block graphics replaced with attested hieroglyphic text, to preempt any copyright claim:

- Each ruler's name is now written in **Unicode Egyptian hieroglyphs**, taken sign-for-sign from the attested spelling in the deity's Wikipedia infobox (WikiHiero markup → Gardiner codes → Unicode), with the extracted reference graphics used only as a cross-check. Rendered in gold in every caption.
- **Font:** Noto Sans Egyptian Hieroglyphs (OFL licensed), subset to the 46 signs used (~19 KB) and embedded as a data-URI `@font-face`, so the glyphs render offline with no external dependency.
- `images/glyphs/` (the graphics extracted from the reference PDFs) **removed from the repo**. Note: they remain in git history from v3.33; history rewrite needed if full removal is required.
- Shu, previously without a glyph image, now has his attested name 𓈙𓆄𓅱𓀭 like the rest. Set (higher) and Set (lower) both use the primary attested spelling 𓋴𓏏𓈙𓃩 (stẖ).
- **FLAG — Iusaaset:** Wikipedia's spelling (𓂻𓍢𓋴𓌇𓂝𓄿𓋴𓏏𓆇𓆗) includes signs I could not independently verify (V1 rope-coil, T1 mace) and the article is low-quality; caption carries a visible “spelling unverified” flag. All other 19 names verified against both Wikipedia and the reference graphics.

---

# CHANGES — v3.33 (Deity lore captions)

**v3.33** — Paths-mode ruler captions rebuilt as finished, public-facing entries:

- **Deity lore** compiled from `data/Female_Divinities_Reference.pdf` + `data/Male_Divinities_Reference.pdf` into `DEITY_LORE`: name meaning, features, symbols, roles, epithets (with transliterations), and invocations. Fields absent from the references are skipped.
- **Hieroglyphic name-blocks** extracted from the reference PDFs to `images/glyphs/` (29 deities) and shown in each ruler caption with a conventional phonetic pronunciation and the MDC/Gardiner/Budge transliterations. *Stub: Shu's name-block is missing from the reference PDF (his page repeats Hu's block) — glyph omitted for Shu.*
- **Removed** the Hebrew-letter “audit” metadata (`PATH_LETTERS`) from path and ruler captions, the “Ruler→path mapping…” provenance box, and the path-study provenance box.
- Set (higher) and Set (lower) share the single Sutekh reference entry. The serpent slain nightly from Ra's barque is left unnamed in the render per the Kau constraint.

---

# CHANGES — v3.32 (Paths Mode + Kau Mode)

**Base:** Built on `base/reconciled_tree_v3_lenses.html` at **v3.31** (newer than the v3.18 referenced in CURSOR_PROMPT.md). Bumped to **v3.32**.

**Deliverable:** `base/reconciled_tree_v3_lenses.html` — single-file, all existing lenses preserved.

---

## Additions

### Task 1 — Paths Mode
- New **Modes → Paths** rail entry with ruler portrait gallery (`images/…`, relative paths).
- Click a ruler → all governed paths highlight in `var(--gold)`; other paths dim; spheres stay visible.
- Inspector shows path list for the ruler; click or hover a highlighted path for lore (≤120 words, condensed from `Path_Trump_Book_Entries_v3_FINAL.md`) and tree function (from `Path_Trump_Semantics_v2.md` + `Dua_Station_Operating_Doctrine_PENDING_2026-08-09.md` where cited).
- Letter/grade audit-trail metadata from `reconciled_tree_v2.json` derivation trail (display only; not system letters).

### Task 2 — Kau Mode
- New **Modes → Kau** rail entry per `Kau_Comparative_Register_v2_RATIFIED.md` §O4.
- **Layer 1:** Fourteen-seat elliptical ring with Lanzone source-form, gloss, presiding deity, tier superscripts, thumbnails where available.
- **Layer 2:** Barque overlay — Hu, Sia, Heka above the ring; dashed prow link to seat #11 (Sutekh). **Apep not depicted or named.**
- **Layer 3:** Benefaction chips on Amen-Ra (chesed), Auset (yesod), Ptah/skill (tiphereth — see stubs).
- Contested markers on seats **#1, #9, #11**; `alt:` subtext on **#5, #8, #10, #13**; stable-core solid ring on **#2, #3, #6, #9, #10, #12**; open seats dashed.

---

## Stubs encountered (visible in render)

| Item | Treatment |
|------|-----------|
| **Ptah benefaction (skill)** | Layer 3 chip at Tiphereth labeled `skill → Ptah [stub]` — Ptah has no sphere seat; register attaches skill to Ptah, not a sphere ruler. |
| **Seat #8 presiding deity** | Register: "Yesod-station" — no dedicated portrait; **Auset** thumbnail used as Yesod-sphere proxy. |
| **Seat #10 presiding deity** | Register: "Fertile Dwelling" (path-name seat) — **Het-Heru** image shown; `alt: Het-Heru` also listed. |
| **Impulse co-rulers** | Auset and Atum listed separately in gallery; both govern path `impulse`. |

No paths rendered with `[ruler unconfirmed]` — all 22 paths have rulers in `reconciled_tree_v2.json` and Book Entries.

---

## Ruler ambiguities (listed, not resolved)

1. **Ptah** rules two paths (Divine Skill & Command + Applied Skill) — rendered as one gallery entry governing both; Book Entries distinguish "Ptah" vs "Ptah (2nd)".
2. **Set (higher form)** vs **Set (lower form)** — two gallery entries, two paths; higher uses `12_set_animal.png`, lower uses `08_sutekh.png` (form distinction from JSON).
3. **Het-Heru** rules two paths (Fertile Dwelling + Pillar of Harmony) — one gallery entry, two paths; Book Entries note "Het-Heru (2nd)" on Pillar of Harmony.
4. **Impulse** — JSON: "Auset & Atum (co-rulers)"; Book Entries treat as separately attested co-rulers (Path 15).

---

## Data conflicts (listed, not resolved)

1. **Operating Doctrine §2** says Flowing Revelation runs "Kether→Tiphareth through the Amen-Ra sphere" — JSON/diagram has `revelation` as **chokmah→chesed** (Aquarius, Heka). Function text cites §3 provocation cycle without re-routing geometry.
2. **Operating Doctrine §0** Kamutef central axis vs **Coiled Power** placement — doctrine pending geometry; function text uses §4d winding language only, no spine reassignment.
3. **Kau seat #1 (Seekh)** — Heru at Tiphareth-station; **Sia equation rejected (D2)** — contested marker shown pending further collation.
4. **Kau seat #9 (Maa)** — directional split (downward Ma'at / upward Hu-path); **O1 collation pending** — contested marker shown.
5. **Kau seat #11 (Set)** — Sutekh barque-prow argument; **O2 collation pending** — contested marker shown.
6. **Tefnut = moisture** — Semantics v2 flags as weakly grounded (CT 80 = Ma'at); path keeps Elemental Water *marker* per canon ruling 3.
7. **Geb as path ruler vs "locus not ruler"** — Book Entry Path 22 says Geb is locus of time, not ruler; JSON assigns `ruler: "Geb"`. Render follows JSON; lore follows Book Entry.

---

## Verification

- JavaScript syntax validated via Node `new Function()` parse.
- Open `base/reconciled_tree_v3_lenses.html` in a browser with `images/` and `data/` alongside (relative image paths require same folder layout as repo).
