# ONE TREE TOOL — TIMING & ELECTION DATA MODEL v1 (DRAFT)
### Schema specification for the `elections` layer: what fills the placeholder columns mounted in Pass v1
*For Ali's ratification, then Cursor implementation. This document defines DATA SHAPE ONLY — no rendering, no UI. Full register: all 37 cells, martial and benefic alike, no functional filter (ruling of 2026-08-12).*

---

## 0. DESIGN PRINCIPLES (binding on Cursor)

1. **Schema-correct now.** Every field defined here mounts even if empty. Gaps render as visible stubs, never invented content.
2. **Tier travels with data.** Every substantive field carries a `tier` (T1/T2/T2-L/T3/G). Attested Naos function and modern application overlay are DIFFERENT TIERS and must never render as the same grade.
3. **Deterministic first.** Phase 1 uses only date math and fixed cycles (decan windows, planetary days, five-figure solar phases, moon phase via simple algorithm). NO ephemeris dependency. Swiss Ephemeris precision (exaltations, retrogrades, transits) is Phase 2, schema-reserved.
4. **Canon constants reused, not redefined.** `PLANET_SPHERE` (existing hard constant), `WEP_RONPET` anchor, `SPHERES`/`PATHS` geometry. Cursor must verify against the canonical data objects before wiring — Golden Dawn substitution is a session-terminating error.
5. **One tree.** All 37 cells carry their full attested function — protective, martial, lethal. What the operator fires and when is the operator's call; the data model does not editorialize.

---

## 1. GLOBAL TIMING CONSTANTS (new top-level objects)

### 1.1 `CALENDAR_ANCHOR`
```js
const CALENDAR_ANCHOR = {
  wep_ronpet: "2026-08-07",        // Giza-calibrated heliacal rising of Sirius (Pass v4 canon)
  calibration: "giza_heliacal",     // doctrine: astronomical, not institutional/lunar
  year_length: 365,                 // civil year: 36 × 10 + 5 epagomenal
  recompute: "annual",              // WR recomputed per year (Phase 1: table of dates; Phase 2: computed)
  wr_table: { 2026: "2026-08-07", 2027: null /* stub — extend before 2027-07 */ },
  timezone_default: "America/New_York",
  location_default: { lat: 40.44, lon: -79.99, label: "Pittsburgh" },  // parameterized, not hardcoded
  tier: "T3 (anchor ruling, Pass v4)"
};
```

### 1.2 Decade window derivation (pure date math — DO NOT store per-cell dates)
```
window(N) for N in 1..36:
  start = wep_ronpet + (N−1) × 10 days
  end   = start + 9 days (inclusive)
window(37):  // epagomenal — the five days BEFORE the next Wep Ronpet
  start = wep_ronpet + 360 days
  end   = wep_ronpet + 364 days
```
Season arcs (already rendered): Akhet = cells 1–12, Peret = 13–24, Shemu = 25–36, epagomenal = 37.

### 1.3 `PLANETARY_DAYS` (fixed 7-day cycle — deterministic)
```js
const PLANETARY_DAYS = {
  sunday: "Sun", monday: "Moon", tuesday: "Mars", wednesday: "Mercury",
  thursday: "Jupiter", friday: "Venus", saturday: "Saturn",
  tier: "T2 (received electional convention)"
};
```
Sphere linkage derives via existing `PLANET_SPHERE` — a cell whose planets include Venus is "day-matched" on Friday AND "sphere-linked" to the Venus sphere. One constant, both uses.

### 1.4 `TACTICAL_FIGURES` (five-figure daily cycle — from Chronos, Naos-derived)
Five phases per day, boundaries computed from local solar events (location-parameterized):
```js
const TACTICAL_FIGURES = [
  { fig: 1, name: "The Human-Headed Bird (Ba)",        window: "pre_dawn",           // astronomical dawn → sunrise
    function: "intelligence / early warning",           tier: "T2-L" },
  { fig: 2, name: "The Falcon-Headed Sphinx (Sopdu-Shu)", window: "sunrise_to_midmorning", // sunrise → sunrise+4h
    function: "offensive strike operations",             title: "Lord of Combat", tier: "T2-L" },
  { fig: 3, name: "The Lion-Headed Ram",               window: "solar_noon",         // culmination ±90 min
    function: "power projection / maximum force",        title: "Lord of Life", tier: "T2-L" },
  { fig: 4, name: "The Standing Canine Mummy (Tekem)", window: "late_afternoon",     // 15:00 local → sunset
    function: "resource allocation / supply control",    title: "Opener of Ways", tier: "T2-L" },
  { fig: 5, name: "The Reclining Mummy",               window: "night",              // sunset → next dawn
    function: "regeneration / strategic reserve",        tier: "T2-L" }
];
```
**Included:** figure names, astronomical windows, military function, principle line. **Not mounted (Ali's call, separate ruling):** the Chronos per-figure business-action lists — those are OJPM-specific application examples (T3 overlay), referenced in the Chronos file, mountable later as an optional lens if ruled in. Flagged, not decided here.

### 1.5 `MOON_PHASE` (Phase 1: simple algorithm)
Synodic approximation (known new-moon epoch + 29.53059 d) → phase in 8 bins (new / waxing crescent / first quarter / waxing gibbous / full / waning gibbous / last quarter / waning crescent). Accuracy ±1 day — sufficient for Phase 1 scoring. Phase 2 replaces with ephemeris. No per-cell moon preferences are attested; see §2.4.

---

## 2. PER-CELL SCHEMA EXTENSION (the `elections` block each of the 37 cells carries)

Extends the mounted decan objects from Pass v1. Existing fields (id, number, names, star, naos_power, planets, tier flags) unchanged.

```js
elections: {
  // 2.1 WINDOW — derived, never stored (see §1.2). Render computes from CALENDAR_ANCHOR.

  // 2.2 PLANETARY DAY MATCHES — derived from this cell's planet pair
  day_matches: ["tuesday", "wednesday"],   // e.g. cell 3 (Mars·Mercury); DERIVED, cached OK
  day_tier: "T3 (planet pair is owned construction; day cycle T2)",

  // 2.3 FIGURE AFFINITY — which of the five daily phases suit this cell's function class
  figure_affinity: [2, 3],                 // e.g. war-class cells → strike & projection figures
  figure_tier: "T3 (owned mapping, rule-derived — see §3.2)",

  // 2.4 MOON — NOT CELL DATA (ruling 2026-08-12). Moon is an operator-side election
  // parameter: inflow (waxing) vs outflow (waning), chosen per working. See §4.1.
  // The per-cell placeholder from Pass v1 is RETIRED.

  // 2.5 DIRECTION — NOT CELL DATA (ruling 2026-08-12). Direction flavors delivery and
  // is operator preference, chosen per working. Recorded in the election output,
  // never scored. The per-cell placeholder from Pass v1 is RETIRED.

  // 2.6 FUNCTION CLASS — the query key for the console (intent → cells)
  function_class: ["strike_fear", "bind"],  // from controlled vocabulary, §3.1
  function_tier: "T2-L (classed from Naos summary)",

  // 2.7 OPERATIONAL FLAGS — carried from Chronos/canon
  flags: [],                                // e.g. ["STAND_DOWN"] (11), ["TOTAL_WAR"] (9),
                                            // ["DE_ESCALATION"] (13), ["SUPREME"] (36),
                                            // ["MAX_DANGER"] (37), ["DANGER"] (34)
  // PRIME/STAND-DOWN ring coloring from the 236-case dataset remains practitioner-private;
  // toggle ruling deferred per existing backlog. Schema holds the field; UI exposure is a separate ruling.

  // 2.8 PHASE 2 RESERVED — mount empty, do not populate
  ephemeris: null                           // future: dignities, retrogrades, transits at window
}
```

---

## 3. CONTROLLED VOCABULARIES

### 3.1 `function_class` (intent-query keys — full spectrum, no filter)
```
initiate_attract    — beginnings, drawing in (abundance-console positive lane)
protect             — warding, defense of order        (e.g. 34, 35)
expel_banish        — driving out rebels/chaos          (e.g. 26, 35)
strike_fear         — psychological force               (e.g. 3)
plague_afflict      — disease/affliction functions      (e.g. 2, 4, 7, 29, 32)
war_carnage         — open destructive force            (e.g. 9, 21)
bind_restrain       — freezing, stopping                (e.g. 5)
de_escalate_settle  — stops the fighting                (13 — unique)
dissolve_end        — life-and-death authority          (36)
regenerate          — recovery, reserve                 (night-lane; 24-class cells)
justice_authority   — truth, rulership                  (e.g. 10, 30)
commerce_alliance   — exchange, bonds                   (e.g. 15, 16, 17)
open_road           — path-opening                      (37)
```
One cell may carry several. Vocabulary is closed — additions require a ruling (prevents drift).

### 3.2 Figure-affinity derivation rule (T3, mechanical — so Cursor doesn't judge)
```
protect / justice_authority / commerce_alliance / initiate_attract → figures [3, 4]
strike_fear / war_carnage / expel_banish                            → figures [2, 3]
plague_afflict / bind_restrain / dissolve_end                       → figures [2, 5]
de_escalate_settle                                                  → figures [4]
regenerate / open_road                                              → figures [5, 1]
```
Stated as a rule so every affinity is reproducible and revisable in one place.

---

## 4. ELECTION SCORING (Phase 1)

### 4.1 Operator parameters (query-time inputs, not cell data)
```js
operator_params: {
  moon_mode: "inflow" | "outflow" | "any",   // inflow = waxing (draw in), outflow = waning (drive out)
  direction: null | "N" | "S" | "E" | "W" | ...,  // free choice; flavors delivery; RECORDED, never scored
}
```
Console may PRE-SELECT moon_mode from intent polarity as a convenience default
(T3 rule, overridable): initiate_attract / commerce_alliance / protect / regenerate /
justice_authority / open_road → inflow · expel_banish / strike_fear / plague_afflict /
war_carnage / bind_restrain / dissolve_end → outflow · de_escalate_settle → any.
The operator's explicit choice always wins.

### 4.2 Score
```
score(cell, datetime, location, operator_params) =
    W_DECAN  × in_window(cell, date)                    // 1 or 0
  + W_DAY    × day_match(cell, weekday)                  // 1 if weekday planet ∈ cell.planets
  + W_MOON   × moon_fit(operator_params.moon_mode, phase) // waxing↔inflow / waning↔outflow; 1, 0.5 near quarters, 0 opposed; "any"=0.5
  + W_FIGURE × figure_match(cell, local_solar_phase)     // 1 if current figure ∈ figure_affinity

Defaults (T3, tunable constants — Chronos guidance: decan+day+moon ≈ 80% of weight):
  W_DECAN = 0.45   W_DAY = 0.20   W_MOON = 0.15   W_FIGURE = 0.20
Phase 2 adds W_EPHEMERIS and renormalizes.
```
Console query shape: **intent (function_class) → matching cells → next window(s) → scored datetimes within window.** "Next favorable window" = earliest window where score ≥ threshold (default 0.65, tunable).

Hard rule: `STAND_DOWN`-flagged cells never surface as *favorable* for initiation queries; they surface with their flag when their window is current. (This mirrors Chronos's own danger-zone logic for cells 11 and 34.)

---

## 5. REGISTER RECONCILIATION (required before Cursor wiring)

`claude_Star_Anchored_Powers_Register_v1.md` (source of truth) currently lacks the `elections` block. Deliverable alongside the tool pass: **Register v1.1** adding, per cell: `function_class`, `flags`, `day_matches` (derived), and the two visible stubs (`moon_pref`, `direction`). JSON mirror updated in the same pass. Tool must read the same shape the register declares — the register stays authoritative.

---

## 6. STUB LEDGER (visible gaps, by design)

| Field | Cells affected | Fill path |
|---|---|---|
| `star` | 28 of 37 | heliacal computation, epoch ruling pending (deferred) |
| `wr_table` beyond 2026 | — | extend before 2027-07 |
| `ephemeris` | all 37 | Phase 2 (Swiss Ephemeris) |
| Chronos business-action overlay | figures 1–5 | Ali ruling: mount as optional lens or leave in Chronos file |

*(Moon and direction removed from ledger — reclassified as operator parameters per ruling 2026-08-12; Pass v1 per-cell placeholders retired.)*

---

## 7. RULINGS LOG

**Ratified 2026-08-12 (Ali):**
- Moon = operator-side inflow/outflow parameter (lunar phase valve), not cell data.
- Direction = operator-side delivery flavor, recorded not scored, not cell data.
- Full register mounts — all 37 cells, martial and benefic, no functional filter.

**Open, non-blocking:**
1. Business-action overlay: mount as optional lens or leave in Chronos file.
2. PRIME/STAND-DOWN UI exposure (already deferred in backlog; schema-ready regardless).
3. Scoring weights/threshold: defaults in §4.2 stand as tunable constants unless amended.
