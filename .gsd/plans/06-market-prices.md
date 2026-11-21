---
phase: 6
plan: 1
wave: 3
gap_closure: false
---

# Plan 6.1: Agricultural Mandi Market Price Information Module

## Objective
Build the agricultural mandi market price tracker, allowing farmers to view minimum, maximum, and modal commodity prices (in ₹/quintal), compare prices across regional APMC markets, filter by commodity and state, and inspect transparent data attribution badges and update timestamps.

## Context
- `.gsd/SPEC.md` (Module F)
- `.gsd/ROADMAP.md` (Phase 6)
- `app/routes/market.py`
- `app/database/seed_data.py`

## Tasks

<task type="auto">
  <name>Build market price dashboard and multi-mandi comparison template</name>
  <files>
    app/templates/market/index.html
    tests/test_market.py
  </files>
  <action>
    1. Create `app/templates/market/index.html`:
       - Commodity & State filter bar.
       - Transparent data attribution indicator ("Verified APMC Benchmark Data", "Last Updated: 2026-11-20").
       - Multi-market comparison summary cards for top commodities (e.g., comparing Wheat rates across Punjab, Rajasthan, and MP).
       - Responsive table displaying: Commodity, Variety, Mandi Name, District, State, Minimum Price (₹/Qtl), Maximum Price (₹/Qtl), Modal Price (₹/Qtl), and Price Spread.
       - Best market highlight pill showing where farmers get the highest modal return.
    2. Write automated tests in `tests/test_market.py`:
       - Market index route loads all price records with 200 OK.
       - Filtering by commodity and state filters records correctly.
       - Modal prices, minimum and maximum values are correctly formatted.
  </action>
  <verify>
    Run `python -m pytest tests/test_market.py -v` and confirm all tests pass.
  </verify>
  <done>
    Market price comparison page renders completely with accurate calculations and passes automated tests.
  </done>
</task>

## Must-Haves
- [ ] Commodity prices displayed with min, max, and modal rates per quintal.
- [ ] Multi-mandi price comparison clearly visible.
- [ ] Explicit attribution badge identifying sample vs live data.
- [ ] Filter by commodity and state functioning accurately.
