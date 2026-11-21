---
phase: 1
plan: 1
wave: 1
gap_closure: false
---

# Plan 1.1: Project Setup and Database Design

## Objective
Establish the foundational project architecture, application directory structure, dependency manifest (`requirements.txt`), SQLite database schema, and seed data initialization script containing rich, realistic data for crops, soils, diseases, mandi prices, and government schemes.

## Context
- `.gsd/SPEC.md`
- `.gsd/ROADMAP.md`

## Tasks

<task type="auto">
  <name>Create directory hierarchy and requirements.txt</name>
  <files>
    requirements.txt
    app/__init__.py
    app/database/schema.sql
    app/database/db.py
    app/database/seed_data.py
    app/static/css/style.css
    app/static/js/main.js
  </files>
  <action>
    1. Create clean folder hierarchy:
       - app/
         - routes/
         - database/
         - templates/
           - components/
         - static/
           - css/
           - js/
           - images/
       - tests/
       - docs/
    2. Create `requirements.txt` with Flask, Werkzeug, requests, pytest.
    3. Create database schema `app/database/schema.sql` defining:
       - `farmers`: id, name, mobile, password_hash, district, state, farm_size, primary_crops, created_at
       - `crops`: id, name, category, season, soil_suitability, water_requirement, temp_range, duration_days, planting_guide, fertilizer_guide, harvesting_guide, icon
       - `fertilizer_soil`: id, soil_type, characteristics, suitable_crops, organic_recommendations, chemical_recommendations, npk_ratio
       - `diseases_pests`: id, name, type, affected_crops, symptoms, prevention, organic_treatment, chemical_treatment, image_url
       - `market_prices`: id, commodity, variety, market, district, state, min_price, max_price, modal_price, is_sample, updated_date
       - `government_schemes`: id, title, short_desc, eligibility, benefits, documents_required, official_url, category
    4. Implement `app/database/db.py` for connection pooling, database initialization, and helper query execution.
    5. Implement `app/database/seed_data.py` to populate SQLite database with comprehensive, realistic Indian agricultural data for at least 8 crops, 6 soils, 8 diseases/pests, 12 market commodities, and 6 government schemes.
  </action>
  <verify>
    Execute Python database initialization script:
    `python -m app.database.seed_data` or `python run_init_db.py`
    Verify tables are created and row counts are non-zero.
  </verify>
  <done>
    Database file `krishimitra.db` created with all 6 tables populated and verified via SQL count query.
  </done>
</task>

## Must-Haves
- [ ] `requirements.txt` includes essential dependencies without bloated packages.
- [ ] SQLite database initializes cleanly with all 6 tables.
- [ ] Rich seed data inserted and queryable.
