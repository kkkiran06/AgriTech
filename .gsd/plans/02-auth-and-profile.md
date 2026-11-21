---
phase: 2
plan: 1
wave: 2
gap_closure: false
---

# Plan 2.1: Farmer Registration, Authentication, and Profile Management

## Objective
Implement secure farmer registration, password hashing, credential verification, session-based login/logout, and profile editing with validation for mobile numbers and agricultural preferences.

## Context
- `.gsd/SPEC.md` (Module A)
- `.gsd/ROADMAP.md` (Phase 2)
- `app/database/db.py`
- `app/database/schema.sql`

## Tasks

<task type="auto">
  <name>Implement auth blueprint and helper utilities</name>
  <files>
    app/routes/auth.py
    app/routes/helpers.py
  </files>
  <action>
    1. In `app/routes/helpers.py`, create `@login_required` decorator and helper functions for session retrieval and validation (e.g. 10-digit mobile number format).
    2. In `app/routes/auth.py`, implement Blueprint `auth_bp`:
       - `/register` (GET, POST): Form validation (name, mobile, district, state, farm_size, password). Hash password with `generate_password_hash`. Handle duplicate mobile error gracefully with user-friendly alert.
       - `/login` (GET, POST): Authenticate mobile and password via `check_password_hash`. On success, populate session (`farmer_id`, `farmer_name`, `district`, `state`).
       - `/logout` (GET): Clear session and redirect to login with confirmation flash.
       - `/profile` (GET, POST): Protected by `@login_required`. View current farmer details; allow updating district, farm size, and primary crops.
  </action>
  <verify>
    Run automated unit tests in `tests/test_auth.py` verifying registration, password hashing, login success, invalid password rejection, and profile updates.
  </verify>
  <done>
    All authentication endpoints pass functional tests with 200/302 responses, session validation, and database persistence.
  </done>
</task>

<task type="auto">
  <name>Build base layout, navigation, and auth templates</name>
  <files>
    app/templates/base.html
    app/templates/auth/login.html
    app/templates/auth/register.html
    app/templates/auth/profile.html
    app/static/css/style.css
  </files>
  <action>
    1. Create `app/templates/base.html` with:
       - Bootstrap 5.3 CDN + Bootstrap Icons
       - Clean agricultural palette (nature green `#2e7d32`, golden harvest `#fbc02d`, earthy card backgrounds)
       - Accessible responsive navbar with mobile hamburger menu
       - Flash message alert banner (success, danger, info)
       - Footer with agricultural helpline and government portal quick links
    2. Create `app/templates/auth/register.html`:
       - Clean, card-based form with fields: Full Name, Mobile Number, State, District, Farm Size (Acres), Preferred Crops, Password, Confirm Password.
       - Client-side mobile number length validation and password confirmation matching.
    3. Create `app/templates/auth/login.html`:
       - Mobile number & password login with "Remember me" option and quick test credentials helper button for demonstration convenience.
    4. Create `app/templates/auth/profile.html`:
       - Farmer card showing joined date, land size, location, registered crops, and editable form.
    5. Enhance `app/static/css/style.css` with responsive styling and agricultural variables.
  </action>
  <verify>
    Render `/auth/login`, `/auth/register`, and `/auth/profile` via test client and check HTML elements and status codes.
  </verify>
  <done>
    Templates render valid HTML5 without errors and forms submit correctly.
  </done>
</task>

## Must-Haves
- [ ] Passwords stored strictly as PBKDF2 hashes in database.
- [ ] Duplicate mobile registration is prevented with a clear flash error.
- [ ] Protected routes reject unauthenticated requests and redirect to `/auth/login`.
- [ ] Profile editing updates the database record.
