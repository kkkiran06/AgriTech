# 🌾 KrishiMitra — Smart Agriculture Web Platform

> A practical, beginner-friendly, and mobile-responsive smart agriculture web application empowering Indian farmers with essential digital advisory services. Built using **Python Flask**, **SQLite3**, **Bootstrap 5.3**, and **Open-Meteo REST API**.

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features & Modules](#key-features--modules)
3. [Technology Stack](#technology-stack)
4. [Architecture & Folder Structure](#architecture--folder-structure)
5. [Database Schema & Data Models](#database-schema--data-models)
6. [Getting Started & Installation](#getting-started--installation)
7. [Running The Application](#running-the-application)
8. [Automated Test Suite](#automated-test-suite)
9. [Demonstration Guide for College Evaluation](#demonstration-guide-for-college-evaluation)

---

## 1. Project Overview

Agriculture in India is heavily impacted by climate volatility, fluctuating mandi market prices, unbalanced chemical fertilizer application, and a general lack of accessible knowledge regarding government subsidies.

**KrishiMitra** solves these critical agricultural challenges by providing a simple, high-contrast, mobile-friendly interface designed specifically for farmers with basic technical knowledge. The platform avoids unnecessary bloated complexity or costly paid APIs, delivering accurate and actionable advisories directly into the hands of farmers.

---

## 2. Key Features & Modules

### A. 👨‍🌾 Farmer Registration & Authentication
- Secure registration capturing: Name, 10-digit Mobile Number, State, District, Farm Size (in Acres), and Active Crops.
- Industry-standard password hashing using `werkzeug.security` (`pbkdf2:sha256`).
- Session-based authentication with persistent state and secure logout.
- Profile management allowing updates to location, farm acreage, and crop pattern.

### B. 🌾 Crop Cultivation Guide
- Rich catalog of 8 major Indian crops: **Rice (Paddy), Wheat, Cotton, Maize, Sugarcane, Tomato, Potato, and Groundnut**.
- Interactive filtering by Growing Season (*Kharif, Rabi, Zaid, Annual*) and Category (*Cereals, Cash Crops, Vegetables, Oilseeds*).
- Comprehensive cultivation guides detailing seed rate, sowing depth, spacing, water requirement, critical irrigation stages, fertilizer schedules, and harvesting indicators.

### C. 🌦️ Weather Information & Agro-Meteorological Advisory
- Hyper-local meteorological conditions: Temperature (°C), Relative Humidity (%), Rainfall (mm), and Wind Speed (km/h).
- Automated, rule-based agricultural recommendations:
  - *Rain Alert*: Delays foliar chemical sprays and fertilizer top-dressing.
  - *High Humidity Alert*: Warns of heightened fungal spore spread (Downy Mildew/Blast).
  - *Moisture Stress*: Reminds farmers to irrigate during heat spells.
- Live data integration via Open-Meteo REST API with seamless, realistic fallback when offline.
- Unambiguous badge distinguishing "Live Satellite Feed" vs "Offline Benchmark Data".

### D. 🧪 Soil & Fertilizer Management (Interactive NPK Calculator)
- Soil classification guide covering **Alluvial, Black (Regur), Red & Yellow, Laterite, Clayey Loam, and Sandy Loam** soils with pH ranges and crop affinities.
- Organic vs. Chemical fertilizer comparison guide.
- **Interactive NPK Calculator**: Computes exact pure Nitrogen (N), Phosphorus (P), and Potassium (K) requirements based on crop selection and farm size, and converts them directly into practical commercial bag numbers:
  - Urea (46% N) — 45kg standard bags
  - DAP (18-46-0) — 50kg standard bags
  - MOP (60% K) — 50kg standard bags
  - Farmyard Manure / Organic Compost in tons.

### E. 🐛 Pest & Crop Disease Doctor
- Visual encyclopedia covering 8 devastating crop pests and diseases: **Rice Blast, Wheat Yellow Rust, Cotton Bollworm, Early Blight, Fall Armyworm, Sugarcane Red Rot, Aphids, and Powdery Mildew**.
- Disease filtering by crop keyword and pathogen category (*Fungal, Insect Pest, Bacterial, Viral*).
- Integrated Pest Management (IPM) guidance featuring:
  - Key visual identification symptoms & early warning signs.
  - Agronomic and cultural prevention practices.
  - Organic / Biological remedies (Neem formulations, Trichoderma, cow urine, biocontrol agents).
  - Recommended chemical formulations with precise dilutions and protective handling warnings.
- Clean SVG illustrations for instant visual diagnosis without broken image links.

### F. 📊 Agricultural Mandi Market Rates
- Daily agricultural commodity quotations across major regional APMC mandis.
- Tracks Minimum Price, Maximum Price, and Modal Price in ₹ per Quintal (100 kg).
- Multi-mandi price comparison to help farmers choose the highest-paying market.
- Explicit data attribution tags clearly identifying verified benchmark APMC data and last update date.

### G. 🏛️ Government Schemes & Subsidies
- Comprehensive directory of 6 flagship central and state agricultural welfare programs:
  1. **PM Kisan Samman Nidhi (PM-KISAN)** — ₹6,000 annual direct income support.
  2. **Pradhan Mantri Fasal Bima Yojana (PMFBY)** — Comprehensive low-premium crop insurance.
  3. **Kisan Credit Card (KCC) Scheme** — Concessional credit up to ₹3 Lakhs at 4% effective interest.
  4. **Soil Health Card Scheme (SHC)** — Free 12-parameter soil testing.
  5. **Sub-Mission on Agricultural Mechanization (SMAM)** — 40-50% subsidy on modern farm machinery.
  6. **Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)** — Up to 55% subsidy on micro-irrigation systems.
- Details financial subsidies, eligibility criteria, document checklists, and verified links to official `.gov.in` / `.nic.in` portals.

### H. 📱 Farmer Dashboard
- Unified personal farm cockpit displaying active farmer profile, registered district weather, quick access widgets, latest mandi rate ticker, and timely seasonal notification advisories.

---

## 3. Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | HTML5, CSS3 (Agricultural Theme Palette), Bootstrap 5.3, Bootstrap Icons, Vanilla JavaScript |
| **Backend** | Python 3.10+ / 3.14, Flask Web Framework (Modular Blueprints, Jinja2 Templates), Werkzeug Security |
| **Database** | SQLite3 (Embedded zero-configuration file database `krishimitra.db`) |
| **External APIs** | Open-Meteo REST API (Open-access weather data) + Curated APMC Mandi Benchmark Dataset |
| **Testing** | Pytest 8.x/9.x (Unit, Functional, and End-to-End Integration Tests) |
| **Tooling** | VS Code, Git, GitHub |

---

## 4. Architecture & Folder Structure

```
hackathon 3.0/
├── app/
│   ├── database/
│   │   ├── db.py                 # SQLite connection pooling & helpers
│   │   ├── schema.sql            # Table definitions (6 core tables)
│   │   └── seed_data.py          # Comprehensive seed data script
│   ├── routes/
│   │   ├── auth.py               # Registration, login, logout, profile
│   │   ├── crops.py              # Crop catalog and detail views
│   │   ├── diseases.py           # Pest & disease doctor
│   │   ├── helpers.py            # Login-required decorator & auth helpers
│   │   ├── main.py               # Landing page and farmer dashboard
│   │   ├── market.py             # Mandi market prices and comparison
│   │   ├── schemes.py            # Government schemes & subsidies
│   │   ├── soil.py               # Soil guide and NPK bag calculator
│   │   └── weather.py            # Open-Meteo weather & agro-advisory
│   ├── static/
│   │   ├── css/style.css         # Agricultural theme stylesheet
│   │   ├── js/main.js            # Client-side validation scripts
│   │   └── images/diseases/      # 8 SVG disease visual identification cards
│   └── templates/
│       ├── base.html             # Base layout with navbar, alerts & footer
│       ├── index.html            # Public landing homepage
│       ├── dashboard.html        # Personalized farmer cockpit
│       ├── auth/                 # Login, Register, Profile templates
│       ├── crops/                # Crop list and detailed guide
│       ├── diseases/             # Disease list and symptom/cure guides
│       ├── market/               # Mandi price comparison table
│       ├── schemes/              # Government schemes directory
│       ├── soil/                 # Soil classification & NPK calculator
│       └── weather/              # Weather dashboard & advisory
├── tests/
│   ├── test_auth.py              # Auth & session security tests
│   ├── test_crops.py             # Crop catalog and filter tests
│   ├── test_diseases.py          # Disease diagnosis and treatment tests
│   ├── test_integration.py       # Full end-to-end user journey test
│   ├── test_market.py            # Mandi price comparison tests
│   ├── test_schemes.py           # Government schemes verification
│   └── test_weather_soil.py      # Weather rules & NPK calculator tests
├── .gsd/                         # GSD methodology specifications & roadmap
├── run.py                        # Root execution entrypoint
├── requirements.txt              # Python dependency manifest
└── README.md                     # Project documentation
```

---

## 5. Database Schema & Data Models

The SQLite database (`krishimitra.db`) is organized into 6 relational tables:

1. `farmers`:
   - `id` (INTEGER PRIMARY KEY)
   - `name` (TEXT)
   - `mobile` (TEXT UNIQUE)
   - `password_hash` (TEXT)
   - `state` (TEXT)
   - `district` (TEXT)
   - `farm_size` (REAL)
   - `primary_crops` (TEXT)
   - `created_at` (TIMESTAMP)

2. `crops`:
   - `id` (INTEGER PRIMARY KEY)
   - `name`, `scientific_name`, `category`, `season`, `suitable_soil`
   - `min_temp`, `max_temp`, `rainfall_mm`, `duration_days`
   - `sowing_guide`, `irrigation_guide`, `fertilizer_guide`, `harvesting_guide`, `icon`

3. `fertilizer_soil`:
   - `id` (INTEGER PRIMARY KEY)
   - `soil_type`, `characteristics`, `suitable_crops`
   - `organic_recommendations`, `chemical_recommendations`, `npk_ratio`, `ph_range`

4. `diseases_pests`:
   - `id` (INTEGER PRIMARY KEY)
   - `name`, `type`, `affected_crops`, `symptoms`, `prevention`
   - `organic_treatment`, `chemical_treatment`, `severity`, `image_url`

5. `market_prices`:
   - `id` (INTEGER PRIMARY KEY)
   - `commodity`, `variety`, `market`, `district`, `state`
   - `min_price`, `max_price`, `modal_price`, `is_sample`, `updated_date`

6. `government_schemes`:
   - `id` (INTEGER PRIMARY KEY)
   - `title`, `category`, `short_desc`, `benefits`, `eligibility`
   - `documents_required`, `official_url`, `badge_label`

---

## 6. Getting Started & Installation

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Web Browser (Google Chrome, Microsoft Edge, Firefox, or Safari)

### Step 1: Clone or Navigate to Project
```powershell
cd "c:\hackathon 3.0"
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 7. Running The Application

Start the Flask development server:
```powershell
python run.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

### Quick Demo Accounts:
You can register any 10-digit number (e.g., `9876543210`), or test registration directly from the register page.

---

## 8. Automated Test Suite

Run all automated unit, security, functional, and integration tests:
```powershell
python -m pytest tests/ -v
```

Expected Output:
```
============================= 18 passed in 1.56s =============================
```

All 18 tests cover:
- Password hashing & duplicate mobile prevention
- Profile update persistence
- Crop season and category filtering
- Weather rule triggers & advisory logic
- Fertilizer dosage NPK bag calculation
- Pest symptom and dual-remedy validation
- Mandi price comparison
- Government scheme portal URL verification
- Full end-to-end farmer journey

---

## 9. Demonstration Guide for College Evaluation

When presenting this project to evaluators or during a hackathon:

1. **Homepage (`/`)**: Show the clean, agricultural theme design, mobile responsiveness, and module cards.
2. **Registration & Login (`/auth/register` & `/auth/login`)**: Demonstrate input validation for the 10-digit mobile number, state/district dropdown auto-population, and password hashing in SQLite.
3. **Dashboard (`/dashboard`)**: Show personalized farmer greetings, active crop tracking, district weather snapshot, and quick access cards.
4. **Crop Guide (`/crops/`)**: Filter crops by season (e.g. *Kharif* or *Rabi*) and inspect the complete sowing and harvesting schedule for Wheat or Rice.
5. **Weather & Advisory (`/weather/`)**: Change districts to see hyper-local temperatures and how automated spray advisories warn farmers against spraying during rain.
6. **NPK Fertilizer Calculator (`/soil/`)**: Input your farm acreage (e.g., 3.5 acres) and show how the platform calculates exact bags of Urea, DAP, and MOP.
7. **Pest Doctor (`/diseases/`)**: Search by crop name (e.g., *Cotton*), click *Cotton Bollworm*, and explain the dual-remedy approach (Neem oil bio-remedies vs chemical formulations).
8. **Mandi Prices (`/market/`)**: Compare commodity prices across different APMC yards to show which market yields the best return.
9. **Government Schemes (`/schemes/`)**: Filter by *Credit & Finance* or *Insurance* and click the official portal link to verify authenticity.
10. **Test Evidence**: Run `python -m pytest tests/ -v` live in the terminal to prove software reliability and code quality.

---

*KrishiMitra — Developed with rigor following the GSD (Get Shit Done) methodology.*
