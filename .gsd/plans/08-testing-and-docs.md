---
phase: 8
plan: 1
wave: 4
gap_closure: false
---

# Plan 8.1: Full Testing, Integration, Application Runner, and Final Documentation

## Objective
Execute complete test suite covering all modules, verify zero regressions, provide convenient entrypoint runner script (`run.py`), generate comprehensive documentation (`README.md`), and update project state and roadmap to finalized status.

## Context
- `.gsd/SPEC.md`
- `.gsd/ROADMAP.md`
- `.gsd/STATE.md`

## Tasks

<task type="auto">
  <name>Build app runner and execute full automated test suite</name>
  <files>
    run.py
    tests/test_integration.py
  </files>
  <action>
    1. Create root entrypoint `run.py`:
       - Loads Flask application via `create_app()`.
       - Checks and auto-initializes `krishimitra.db` with seed data if database is missing.
       - Starts development server on port 5000 with informative banner.
    2. Create `tests/test_integration.py`:
       - Comprehensive end-to-end integration test verifying that a farmer can register, log in, view dashboard, navigate through crop guide, weather advisory, fertilizer calculator, disease doctor, market prices, and government schemes without any HTTP 500 errors.
    3. Run full test suite with `python -m pytest tests/ -v`.
  </action>
  <verify>
    Execute `python -m pytest tests/ -v` and confirm 100% test pass rate.
  </verify>
  <done>
    Entire test suite passes cleanly across all 5 test files.
  </done>
</task>

<task type="auto">
  <name>Create comprehensive README and update GSD State</name>
  <files>
    README.md
    .gsd/ROADMAP.md
    .gsd/STATE.md
  </files>
  <action>
    1. Author comprehensive `README.md` detailing:
       - Problem statement and project vision.
       - Architecture diagram and directory structure.
       - Features list for all 8 modules.
       - Step-by-step setup and running instructions for Windows/Linux.
       - Technology stack explanation.
       - Database schema description and default accounts.
       - Demonstration guide for college project evaluation.
    2. Update `.gsd/ROADMAP.md` marking all phases complete.
    3. Update `.gsd/STATE.md` with final summary.
  </action>
  <verify>
    Verify all files exist and are populated properly.
  </verify>
  <done>
    README.md and GSD documentation are complete and up to date.
  </done>
</task>

## Must-Haves
- [ ] 100% test pass rate across all test files.
- [ ] `run.py` launches cleanly.
- [ ] `README.md` provides clear installation and demo instructions.
- [ ] `.gsd/ROADMAP.md` and `.gsd/STATE.md` show all 8 phases completed.
