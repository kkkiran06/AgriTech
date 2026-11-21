---
phase: 4
plan: 1
wave: 3
gap_closure: false
---

# Plan 4.1: Weather Forecasting, Agro-Advisory, and Soil & Fertilizer Calculator

## Objective
Implement weather forecasting module using Open-Meteo with offline fallback and automated agro-meteorological advisories, coupled with a comprehensive soil classification guide and an interactive NPK fertilizer dosage calculator that computes commercial bag counts based on acreage.

## Context
- `.gsd/SPEC.md` (Modules C & D)
- `.gsd/ROADMAP.md` (Phase 4)
- `app/routes/weather.py`
- `app/routes/soil.py`

## Tasks

<task type="auto">
  <name>Build weather advisory and soil fertilizer templates</name>
  <files>
    app/templates/weather/index.html
    app/templates/soil/index.html
    tests/test_weather_soil.py
  </files>
  <action>
    1. Create `app/templates/weather/index.html`:
       - District selector dropdown with 13 key agricultural districts.
       - Current conditions dashboard: Temperature, Humidity, Precipitation, Wind Speed, Weather Icon.
       - Transparent data badge ("Live Open-Meteo Feed" vs "Offline Benchmark Data").
       - Rule-based Agricultural Advisory card (spraying advice, fungal outbreak risk, irrigation advisory).
       - 5-Day forecast cards displaying daily min/max temperature and precipitation probabilities.
    2. Create `app/templates/soil/index.html`:
       - Soil classification guide displaying 6 major soils with characteristics, pH range, and compatible crops.
       - Organic vs Chemical fertilizer comparative guide.
       - Interactive NPK Fertilizer Calculator:
         - Form to select crop (Rice, Wheat, Cotton, Maize, Sugarcane, Tomato, Potato, Groundnut) and land size (Acres).
         - Output card presenting total N, P, K (kg), required 45kg Urea bags, 50kg DAP bags, 50kg MOP bags, and organic compost requirement.
    3. Write automated unit and integration tests in `tests/test_weather_soil.py`:
       - Weather endpoint loads and switches gracefully between districts.
       - Weather advisory rules function properly based on temperature and precipitation.
       - Soil catalog displays all 6 soils.
       - Fertilizer calculator produces mathematically correct NPK and bag estimates.
  </action>
  <verify>
    Run `python -m pytest tests/test_weather_soil.py -v` and ensure all tests pass.
  </verify>
  <done>
    Weather and Soil modules function accurately with dynamic calculation and pass automated test suites.
  </done>
</task>

## Must-Haves
- [ ] Weather displays temperature, humidity, rainfall, wind, and agricultural advisory.
- [ ] Explicit badge indicates whether weather data is live or benchmark sample.
- [ ] Soil guide details 6 soil types and pH ranges.
- [ ] Fertilizer calculator accurately computes NPK and bag quantities for any given acreage.
