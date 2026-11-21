---
phase: 3
plan: 1
wave: 2
gap_closure: false
---

# Plan 3.1: Farmer Dashboard, Homepage, and Crop Advisory Module

## Objective
Implement a welcoming agricultural landing page, enrich the unified farmer dashboard, and build the full crop catalog system with seasonal/category filtering and comprehensive agronomic cultivation, irrigation, and fertilizer schedules.

## Context
- `.gsd/SPEC.md` (Module B & H)
- `.gsd/ROADMAP.md` (Phase 3)
- `app/routes/crops.py`
- `app/routes/main.py`

## Tasks

<task type="auto">
  <name>Build landing page and crop catalog templates</name>
  <files>
    app/templates/index.html
    app/templates/crops/index.html
    app/templates/crops/detail.html
    tests/test_crops.py
  </files>
  <action>
    1. Create `app/templates/index.html`:
       - High-impact agricultural hero section with call-to-actions ("Explore Crops", "Check Weather", "Mandi Rates").
       - Highlights cards for the 6 core modules.
       - Farmer testimonials/impact metrics (8 crops, 12 APMC mandis, 6 major government schemes).
    2. Create `app/templates/crops/index.html`:
       - Filter bar by Season (All, Kharif, Rabi, Zaid) and Category (Cereals, Cash Crops, Vegetables, Oilseeds).
       - Responsive crop cards showing crop icon, botanical name, duration, season badge, and quick soil match.
    3. Create `app/templates/crops/detail.html`:
       - Full agronomic specification sheet:
         - Sowing & seed preparation guide
         - Irrigation schedules & critical growth stages
         - Step-by-step fertilizer plan (basal dose vs top dressing)
         - Harvesting indicators & moisture checks
         - Temperature & rainfall compatibility meters
    4. Write automated tests in `tests/test_crops.py` to verify:
       - Home page renders 200 OK.
       - Crop catalog renders with filter queries.
       - Crop detail pages render valid data and 404 on invalid IDs.
  </action>
  <verify>
    Run `python -m pytest tests/test_crops.py -v` and check all tests pass.
  </verify>
  <done>
    All crop pages render completely with accurate agronomic guidance and pass automated verification.
  </done>
</task>

## Must-Haves
- [ ] Crop catalog displays all 8 seeded crops.
- [ ] Season and category filters correctly filter crops.
- [ ] Crop detail page presents sowing, irrigation, fertilizer, and harvest guidance.
- [ ] 404 status returned for non-existent crop ID.
