---
milestone: AgriTech Smart Agriculture Platform (KrishiMitra)
version: 1.0.0
updated: 2026-11-21
---

# ROADMAP.md — Project Roadmap

> **Current Phase:** Phase 1 - Project Setup and Database Design
> **Status:** executing

## Must-Haves (from SPEC.md)
- [ ] Modular Flask backend architecture with clean separation of routes, templates, and static assets.
- [ ] SQLite database schema for Farmers, Crops, Soil Guides, Diseases/Pests, Mandi Prices, and Government Schemes with seed data.
- [ ] Secure registration, login, logout, and farmer profile editing with hashed passwords.
- [ ] Personalized farmer dashboard displaying local weather, active crops, quick links, and agricultural alerts.
- [ ] Rich crop catalog with season/soil filters, sowing guidelines, and fertilizer recommendations.
- [ ] Weather forecast module with Open-Meteo live API + robust offline fallback and agro-advisory tips.
- [ ] Soil health guide and interactive NPK fertilizer dosage calculator.
- [ ] Visual crop disease and pest encyclopedia with symptoms and dual-remedy guidelines (organic & chemical).
- [ ] Mandi market prices tracker with multi-market price comparisons and explicit data attribution.
- [ ] Government schemes directory with eligibility criteria, subsidies, and official application links.
- [ ] Comprehensive verification test suite and complete setup documentation (`README.md`).

---

## Phases & Execution Waves

```
Wave 1 (Foundation):
  Phase 1: Project Setup and Database Design

Wave 2 (Authentication & Core Advisory):
  Phase 2: Farmer Registration and Authentication
  Phase 3: Farmer Dashboard and Crop Information

Wave 3 (Specialized Farm Services):
  Phase 4: Weather Information and Soil Management
  Phase 5: Disease and Pest Management
  Phase 6: Agricultural Market Prices
  Phase 7: Government Schemes

Wave 4 (Quality & Delivery):
  Phase 8: Testing, Integration, and Final Documentation
```

---

### Phase 1: Project Setup and Database Design
- **Status:** 🔄 In Progress
- **Wave:** 1
- **Objective:** Establish the application directory structure, Python virtual environment dependencies, SQLite database schema, initialization scripts, and baseline seed data.
- **Plan File:** `.gsd/plans/01-setup-and-db.md`

### Phase 2: Farmer Registration and Authentication
- **Status:** ⬜ Not Started
- **Wave:** 2
- **Objective:** Implement secure user registration, password hashing (`werkzeug.security`), session-based login/logout, profile viewing, and profile updating.
- **Plan File:** `.gsd/plans/02-auth-and-profile.md`

### Phase 3: Farmer Dashboard and Crop Information
- **Status:** ⬜ Not Started
- **Wave:** 2
- **Objective:** Build the farmer home dashboard, navigation, and comprehensive crop catalog with seasonal filters, irrigation schedules, and cultivation guides.
- **Plan File:** `.gsd/plans/03-dashboard-and-crops.md`

### Phase 4: Weather Information and Soil Management
- **Status:** ⬜ Not Started
- **Wave:** 3
- **Objective:** Implement Open-Meteo weather API integration with offline fallback, weather-based agricultural advisories, soil classification guides, and interactive NPK fertilizer calculator.
- **Plan File:** `.gsd/plans/04-weather-and-soil.md`

### Phase 5: Disease and Pest Management
- **Status:** ⬜ Not Started
- **Wave:** 3
- **Objective:** Build visual pest & disease identification catalog with symptoms, high-resolution imagery, organic remedies, and chemical treatment guidelines.
- **Plan File:** `.gsd/plans/05-disease-and-pest.md`

### Phase 6: Agricultural Market Prices (Mandi Rates)
- **Status:** ⬜ Not Started
- **Wave:** 3
- **Objective:** Create market price dashboard with commodity filters, APMC mandi comparisons, modal price indicators, and data attribution tags.
- **Plan File:** `.gsd/plans/06-market-prices.md`

### Phase 7: Government Schemes & Subsidies
- **Status:** ⬜ Not Started
- **Wave:** 3
- **Objective:** Develop directory of vital central and state government agricultural schemes with benefits, eligibility criteria, document checklists, and verified links.
- **Plan File:** `.gsd/plans/07-government-schemes.md`

### Phase 8: Testing, Integration, and Final Documentation
- **Status:** ⬜ Not Started
- **Wave:** 4
- **Objective:** Perform automated end-to-end and unit testing, verify mobile responsive layout across all pages, capture verification evidence, and finalize `README.md` and user setup guide.
- **Plan File:** `.gsd/plans/08-testing-and-docs.md`

---

## Progress Summary

| Phase | Description | Wave | Status | Plans | Complete |
|---|---|---|---|---|---|
| **1** | Project Setup & Database Design | 1 | 🔄 In Progress | 1/1 | 0/1 |
| **2** | Farmer Auth & Profile | 2 | ⬜ Not Started | 1/1 | 0/1 |
| **3** | Dashboard & Crop Information | 2 | ⬜ Not Started | 1/1 | 0/1 |
| **4** | Weather & Soil Management | 3 | ⬜ Not Started | 1/1 | 0/1 |
| **5** | Disease & Pest Management | 3 | ⬜ Not Started | 1/1 | 0/1 |
| **6** | Market Prices (Mandi Rates) | 3 | ⬜ Not Started | 1/1 | 0/1 |
| **7** | Government Schemes | 3 | ⬜ Not Started | 1/1 | 0/1 |
| **8** | Testing, Polish & Documentation | 4 | ⬜ Not Started | 1/1 | 0/1 |
