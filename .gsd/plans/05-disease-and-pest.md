---
phase: 5
plan: 1
wave: 3
gap_closure: false
---

# Plan 5.1: Crop Disease & Pest Management Module

## Objective
Implement visual pest and disease doctor catalog with symptom identification, early warning checklists, crop-specific filtering, and actionable dual-treatment recommendations (organic/biological remedies and chemical treatments with dosage guidelines).

## Context
- `.gsd/SPEC.md` (Module E)
- `.gsd/ROADMAP.md` (Phase 5)
- `app/routes/diseases.py`
- `app/database/seed_data.py`

## Tasks

<task type="auto">
  <name>Create disease identification images and templates</name>
  <files>
    app/static/images/diseases/rice_blast.svg
    app/static/images/diseases/wheat_rust.svg
    app/static/images/diseases/cotton_bollworm.svg
    app/static/images/diseases/early_blight.svg
    app/static/images/diseases/fall_armyworm.svg
    app/static/images/diseases/sugarcane_red_rot.svg
    app/static/images/diseases/aphids.svg
    app/static/images/diseases/powdery_mildew.svg
    app/templates/diseases/index.html
    app/templates/diseases/detail.html
    tests/test_diseases.py
  </files>
  <action>
    1. Create clean SVG illustrations for all 8 plant diseases/pests in `app/static/images/diseases/`.
    2. Build `app/templates/diseases/index.html`:
       - Filter by Crop and Pest/Disease Type (Fungal, Bacterial, Viral, Insect Pest).
       - Visual ailment cards showing disease name, affected crops, severity badge (Severe, Moderate), and teaser symptoms.
    3. Build `app/templates/diseases/detail.html`:
       - Detailed symptom diagnosis with early warning signs.
       - Cultural and agronomic preventive measures (crop rotation, seed treatment, field sanitation).
       - Organic / Biological remedies (Neem formulations, Trichoderma, cow urine, biocontrol agents).
       - Chemical formulations with precise dilutions and safety precautions.
    4. Write automated tests in `tests/test_diseases.py`:
       - Catalog renders 8 disease items.
       - Filtering by crop and type works as expected.
       - Detail view renders remedies and returns 404 for non-existent IDs.
  </action>
  <verify>
    Run `python -m pytest tests/test_diseases.py -v` and confirm all tests pass.
  </verify>
  <done>
    Disease management pages render fully with visual graphics and pass automated tests.
  </done>
</task>

## Must-Haves
- [ ] Visual disease cards render without broken images.
- [ ] Both organic and chemical treatments are clearly specified.
- [ ] Disease filtering by crop and type functions accurately.
