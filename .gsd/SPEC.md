# SPEC.md — AgriTech Web Application (KrishiMitra) Specification

> **Status**: `FINALIZED`
>
> ✅ **Planning Lock Lifted**: Spec approved. Ready for Roadmap & Execution Plans.

---

## 1. Vision

**KrishiMitra** is a beginner-friendly, practical, and responsive smart agriculture web application designed to empower farmers with essential digital advisory services. Targeted especially at farmers and agricultural students with basic technical knowledge, the platform solves everyday farming challenges—such as weather unpredictability, pest outbreaks, uncertain market prices, soil nutrient imbalances, and lack of awareness of government subsidies—through an intuitive, accessible, and clean digital interface built with Python Flask, SQLite, HTML5, CSS3, and Bootstrap.

---

## 2. Goals & Objectives

1. **Accessibility & Simplicity**: Provide a clean, agricultural-themed, mobile-first responsive web application that requires zero technical training for farmers.
2. **Farmer Identity & Personalization**: Enable farmers to register, log in securely, and maintain a profile with their location, land size, and active crops.
3. **Comprehensive Crop Advisory**: Supply clear agronomic guides covering suitable soil types, sowing seasons, irrigation schedules, and fertilizer recommendations.
4. **Actionable Weather Insights**: Present hyper-local weather conditions (temperature, humidity, precipitation, wind) and a 5-to-7-day forecast with straightforward agricultural advisories (e.g., spraying advice, rain alerts).
5. **Soil & Fertilizer Management**: Educate farmers on soil health, soil-crop compatibility, organic versus chemical fertilizers, and balanced NPK dosage calculation.
6. **Disease & Pest Visual Identification**: Enable visual identification of major crop diseases and pests with symptom checklists, preventive practices, and biological/chemical treatments.
7. **Transparent Market Prices (Mandi Prices)**: Deliver reliable APMC market prices across commodities and markets with clear price comparisons and explicit timestamps.
8. **Government Scheme Awareness**: Catalog vital central and state government agricultural schemes (e.g., PM-KISAN, PMFBY, KCC, Soil Health Card) with eligibility criteria, benefits, and direct official application links.
9. **Unified Farmer Dashboard**: Provide an integrated home cockpit that consolidates profile info, weather alerts, quick market summaries, and timely notifications.
10. **Educational & Demonstration Excellence**: Deliver a modular, well-commented, and robust codebase suitable for college academic presentations and hackathon evaluation.

---

## 3. Users & Personas

- **Primary User: Smallholder / Marginal Farmer**
  - *Profile*: Basic digital literacy, accesses the web primarily via mobile browser or shared device.
  - *Needs*: High-contrast text, clear agricultural icons, simple language, instant access to weather alerts, market rates, and disease cures.
- **Secondary User: Agricultural Extension Worker / Village Coordinator**
  - *Profile*: Moderate digital literacy, assists multiple farmers in accessing schemes, testing soil recommendations, and market intelligence.
  - *Needs*: Quick navigation between crop advisory, soil calculators, and government subsidy links.
- **Tertiary User: Evaluator / Engineering Student / Researcher**
  - *Profile*: Technical background examining system design, code architecture, security, and reproducibility.
  - *Needs*: Clear project structure, straightforward local setup (`requirements.txt`, SQLite DB auto-initialization), realistic fallback data, and clean documentation.

---

## 4. Functional Requirements (Core Modules)

### Module A: Farmer Registration & Authentication
- **FR-A1**: Registration form capturing: Full Name, Mobile Number (10 digits, validated), State & District / Location, Land Holding Size (in Acres), Preferred/Primary Crops, and Password.
- **FR-A2**: Secure password hashing using industry standard algorithms (`werkzeug.security` / `bcrypt`).
- **FR-A3**: Session-based authentication with secure login, logout, and persistent session state.
- **FR-A4**: Farmer profile view and editing interface to update location, phone, and farming preferences.

### Module B: Crop Information & Cultivation Guide
- **FR-B1**: Crop catalog categorized by season (Kharif, Rabi, Zaid) and category (Cereals, Pulses, Oilseeds, Cash Crops, Vegetables, Fruits).
- **FR-B2**: Detailed crop pages showing: Botanical/Common name, optimal temperature range, rainfall requirement, suitable soil types, seed sowing depth, row spacing, irrigation frequency, and harvest indicators.
- **FR-B3**: Recommended fertilizer schedule (basal dose vs. top dressing) for each crop.

### Module C: Weather Information & Agro-Advisory
- **FR-C1**: Display current weather: Temperature (°C), Humidity (%), Wind Speed (km/h), Precipitation probability (%), and condition iconography (Sunny, Rainy, Overcast, etc.).
- **FR-C2**: 5 to 7-day weather forecast table and charts.
- **FR-C3**: Dynamic agricultural rule-based suggestions:
  - *High rainfall alert*: Delay fertilizer application and pesticide spray to avoid runoff.
  - *High humidity & warm temperature*: Heightened fungal spore alert.
  - *Dry spell & high heat*: Immediate irrigation reminder.
- **FR-C4**: Open-Meteo Weather API integration (zero API key needed, open-access, reliable) with seamless, realistic fallback dataset when offline.

### Module D: Fertilizer & Soil Management
- **FR-D1**: Soil classification guide: Alluvial, Black (Regur), Red & Yellow, Laterite, Arid/Desert, and Clayey/Loamy soils, highlighting pH ranges and crop affinity.
- **FR-D2**: Organic vs. Chemical fertilizer primer: Benefits of Vermicompost, Farmyard Manure (FYM), Neem cake, Bio-fertilizers vs. Urea, DAP, MOP.
- **FR-D3**: Interactive Fertilizer Dosage Calculator: Calculates estimated Nitrogen (N), Phosphorus (P), and Potassium (K) requirements based on crop selection and farm acreage.
- **FR-D4**: Practical soil health preservation tips (crop rotation, green manuring, mulching, drip irrigation).

### Module E: Crop Disease & Pest Management
- **FR-E1**: Visual pest and disease encyclopedia with high-quality reference imagery.
- **FR-E2**: Search and filter by crop name (e.g., Rice, Wheat, Cotton, Tomato, Potato) and pest/disease type (Fungal, Bacterial, Viral, Insect Pest).
- **FR-E3**: Comprehensive profiles per ailment: Common Symptoms, Early Warning Signs, Cultural & Preventive Measures, Organic/Biological Remedies, and Recommended Chemical Formulations (with safe dosage warnings).
- **FR-E4**: **PlantDoctor AI Pathologist (Camera & Upload)**:
  - Mobile phone camera capture & local image upload.
  - Deep Learning model (MobileNetV2 / PlantVillage 38 disease classes) providing disease identification with confidence scores.
  - Comprehensive symptoms, organic remedies, and chemical treatment guidelines.
  - Historical diagnosis archive per registered farmer.
  - Automatic graceful fallback to deterministic demonstration simulation mode if model weights are offline.

### Module F: Agricultural Market Price Information (Mandi Rates)
- **FR-F1**: Commodity price dashboard showing Commodity Name, Variety, Mandi/Market Name, State/District, Min Price, Max Price, and Modal Price (₹ per Quintal).
- **FR-F2**: Multi-market price comparison tool allowing farmers to compare price variations across nearby district markets.
- **FR-F3**: Transparent metadata tags showing Last Updated Date, Source, and unambiguous badge identifying whether data is "Live Mandi Feed" or "Verified Benchmark Sample Data".

### Module G: Government Agriculture Schemes & Subsidies
- **FR-G1**: Curated directory of key national and state agricultural welfare schemes:
  - PM Kisan Samman Nidhi (PM-KISAN)
  - Pradhan Mantri Fasal Bima Yojana (PMFBY - Crop Insurance)
  - Kisan Credit Card (KCC) Scheme
  - Soil Health Card Scheme (SHC)
  - Sub-Mission on Agricultural Mechanization (SMAM - Farm Equipment Subsidy)
  - Pradhan Mantri Krishi Sinchayee Yojana (PMKSY - Micro-Irrigation)
- **FR-G2**: Breakdown for each scheme: Core Objective, Financial Benefit / Subsidy Amount, Eligibility Criteria, Required Documents checklist, and Direct Link to Official Government Portal (`gov.in` / `nic.in`).

### Module H: Farmer Dashboard & Notifications
- **FR-H1**: Personalized dashboard summarizing: Logged-in farmer profile, registered crops, and quick weather snapshot for their district.
- **FR-H2**: Quick-action cards for 1-click access to Crop Guide, Fertilizer Calculator, Disease Identifier, Mandi Prices, and Government Schemes.
- **FR-H3**: Agricultural Notification Feed displaying timely seasonal advisories, upcoming scheme deadlines, and MSP announcements.

---

## 5. Non-Functional Requirements

| Dimension | Specification |
|-----------|---------------|
| **Usability & UX** | Clean agricultural visual design (greens `#2e7d32`, `#43a047`, earthy tones `#5d4037`, warm cream `#fafafa`). Responsive on mobile (360px+), tablet, and desktop. Large touch targets (≥44px), readable typography (sans-serif), and intuitive icons. |
| **Performance** | Page load time under 1.5 seconds on standard 3G/4G connections. Lightweight static assets, minified CSS/JS where appropriate, CDN fallback. |
| **Security** | Hashed passwords (PBKDF2/SHA256 via Werkzeug), session hijacking prevention (secure cookies, session timeouts), parameterized SQL queries to prevent SQL injection, and XSS escaping in Jinja2 templates. |
| **Reliability & Offline Grace** | Graceful degradation: If external weather or market data services fail or are offline, system falls back immediately to realistic bundled benchmark datasets without crashing. |
| **Data Integrity** | Strict SQLite schema constraints (unique mobile numbers, foreign keys, non-null fields, timestamped records). |
| **Maintainability** | Clean modular Python Flask application with separation of concerns (`routes/`, `models/`, `templates/`, `static/`), readable PEP 8 compliant code with descriptive docstrings. |

---

## 6. Technology Stack

- **Frontend**:
  - HTML5 & CSS3 (Modern custom agricultural styling + CSS variables)
  - Bootstrap 5.3 (Responsive grid, accessible components, modals, alerts)
  - Bootstrap Icons / SVG Icons (Standard agricultural and interface glyphs)
  - Vanilla JavaScript (Form validation, dynamic calculators, interactive filters, no heavyweight framework dependencies)
- **Backend**:
  - Python 3.10+ / 3.14 compatible
  - Flask (Lightweight, robust Python WSGI web framework)
  - Werkzeug (Secure password hashing and routing utilities)
- **Database**:
  - SQLite3 (Embedded, zero-configuration, cross-platform file-based database ideal for demonstration and zero-friction grading)
  - Native Python `sqlite3` or lightweight helper layer with schema migrations and automatic seeding
- **External APIs**:
  - Open-Meteo Weather API (Free, open-source, no API key required for weather data)
  - Bundled verified APMC Mandi dataset + optional Agmarket API connector
- **Environment & Tooling**:
  - VS Code
  - Git & GitHub (Atomic commits following Conventional Commits format)

---

## 7. Project Limitations & Out of Scope (Non-Goals)

1. **No Paid / Rate-Limited Proprietary APIs**: No hard dependency on paid third-party APIs (e.g., Google Maps API, paid weather services); all integrations must be free or self-contained.
2. **No Heavyweight Cloud / GPU AI Models**: No multi-gigabyte PyTorch/TensorFlow models running heavy local neural inference that could crash standard student laptops; disease identification is structured with high-accuracy symptom-matching rules and visual guide libraries.
3. **No Commercial Payment Gateway**: No real monetary transactions or online payment gateways (Stripe/Razorpay) to avoid financial overhead and credential requirements.
4. **No Direct Hardware IoT Physical Wiring**: Focus is on software-accessible web technology; while sensor telemetry can be simulated or manually recorded, physical microcontroller hardware assembly is out of scope.
5. **No Fake "Live" Claims**: The UI will never deceive users by claiming sample data is live; live and curated sample data are always visibly distinguished.

---

## 8. Success Criteria & Verification Gates

- [ ] **SC-1**: User can register with valid mobile and credentials, log in, and view personal dashboard.
- [ ] **SC-2**: Farmer profile updates (crops, location, land size) persist correctly in SQLite database.
- [ ] **SC-3**: Crop catalog displays at least 8 major crops with comprehensive agronomic, irrigation, and fertilizer guidelines.
- [ ] **SC-4**: Weather module pulls live data for selected districts from Open-Meteo or switches smoothly to realistic benchmark data if network is unavailable.
- [ ] **SC-5**: Fertilizer dosage calculator produces accurate, mathematically sound NPK recommendations based on crop and land acreage.
- [ ] **SC-6**: Disease encyclopedia details at least 8 major crop diseases with symptoms, images, preventive measures, and treatments.
- [ ] **SC-7**: Market price table allows filtering by crop/market and displays price range (min/max/modal) with explicit data attribution and timestamps.
- [ ] **SC-8**: Government schemes section presents at least 6 active schemes with eligibility criteria, subsidy details, and verified application URLs.
- [ ] **SC-9**: All application pages render cleanly on mobile viewport (375px width) without horizontal overflow or clipped text.
- [ ] **SC-10**: Clean test suite passes 100% of functional tests (HTTP status codes, database CRUD, calculator logic, auth security).

---

*Specification Drafted: 2026-11-21*
