---
phase: 7
plan: 1
wave: 3
gap_closure: false
---

# Plan 7.1: Government Agriculture Schemes & Subsidies Module

## Objective
Implement comprehensive government schemes directory with categorization (income support, crop insurance, credit, soil health, farm mechanization, irrigation), eligibility requirements, benefit details, document checklists, and verified direct links to official government portals.

## Context
- `.gsd/SPEC.md` (Module G)
- `.gsd/ROADMAP.md` (Phase 7)
- `app/routes/schemes.py`
- `app/database/seed_data.py`

## Tasks

<task type="auto">
  <name>Build government schemes catalog and test suite</name>
  <files>
    app/templates/schemes/index.html
    tests/test_schemes.py
  </files>
  <action>
    1. Create `app/templates/schemes/index.html`:
       - Category filter tabs/badges (Income Support, Crop Insurance, Credit, Soil, Equipment, Irrigation).
       - Scheme detail cards presenting:
         - Scheme Title and category badge.
         - Short objective and core financial benefit / subsidy terms.
         - Who is eligible (marginal farmers, tenant farmers, etc.).
         - Required documentation checklist (Aadhaar, 7/12 Land Record, Bank Passbook).
         - Direct verified link button to official portal (`gov.in` / `nic.in`).
    2. Write automated tests in `tests/test_schemes.py`:
       - Schemes index route loads 6 schemes with 200 OK.
       - Category filtering returns matched schemes.
       - Each scheme card renders valid official URL and benefits text.
  </action>
  <verify>
    Run `python -m pytest tests/test_schemes.py -v` and confirm all tests pass.
  </verify>
  <done>
    Government schemes directory renders completely with verified portal links and passes automated tests.
  </done>
</task>

## Must-Haves
- [ ] At least 6 major schemes displayed.
- [ ] Eligibility and benefits clearly detailed.
- [ ] Direct links to official portals (`gov.in` / `nic.in`) functional.
- [ ] Category filter operational.
