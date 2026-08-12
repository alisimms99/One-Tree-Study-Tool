# TESTS — Timing & Election Layer (v3.42)

Manual acceptance checks for `TREE.elections` (browser console on the live page).

## Derived windows

```js
const E = TREE.elections;
E.decanWindow(1, 2026);   // → 2026-08-07 … 2026-08-16
E.decanWindow(36, 2026);  // → 2027-07-23 … 2027-08-01
E.decanWindow(37, 2026);  // → 2027-08-02 … 2027-08-06 (epagomenal)
E.inDecanWindow(1, new Date(2026,7,7,12));  // true — Wep Ronpet ∈ cell 1
E.inDecanWindow(37, new Date(2026,7,6,12)); // true — day before WR ∈ cell 37 (prior year)
```

Today’s cell: `civilDayInfo()` → `E.decanWindow(info.n, year)`.

## Day matches

```js
E.dayMatches(3); // ["tuesday","wednesday"]  // Mars·Mercury
```

## STAND_DOWN

```js
E.nextFavorableWindow(11, new Date(), {moon_mode:'any'});
// → {favorable:false, excluded:true, reason:'STAND_DOWN', flags:['STAND_DOWN'], window:…}
```

Cell 11 never appears as a favorable result; direct inspection still returns its window + flag.

## Score monotonicity

Weights: `W_DECAN=0.45, W_DAY=0.20, W_MOON=0.15, W_FIGURE=0.20`.

For cell 3, Tuesday 2026-09-01 noon (in window + day match + noon figure + moon any=0.5):

| Conditions | Expected score |
|---|---|
| none | 0 |
| decan only | 0.45 |
| decan + day | 0.65 |
| decan + day + moon(any) | 0.725 |
| decan + day + moon + figure | 0.925 |

```js
E.electionScore(3, new Date(2026,8,1,12), E.CALENDAR_ANCHOR.location_default, {moon_mode:'any'});
// parts.decan=1, day=1, figure=1, moon=0.5 → score 0.925

E.electionScore(3, new Date(2026,8,3,12), …, {moon_mode:'any'}); // Thursday in-window
// day=0 → score 0.725  (strictly less)

E.electionScore(3, new Date(2026,9,6,12), …, {moon_mode:'any'}); // Tuesday outside window
// decan=0 → score 0.475  (strictly less)
```

Full set scores strictly higher than any proper subset.

## Inspector

Open Decans → cell 3: Timing block shows window, Tuesday/Wednesday, F2/F3 figures, moon toggle (default outflow for `strike_fear`), next favorable range.
