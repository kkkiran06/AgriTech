from flask import Blueprint, render_template, request, jsonify
import requests

weather_bp = Blueprint('weather', __name__)

# Coordinates for major agricultural centers in India
DISTRICT_COORDINATES = {
    "Pune": {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra"},
    "Nashik": {"lat": 19.9975, "lon": 73.7898, "state": "Maharashtra"},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882, "state": "Maharashtra"},
    "Gondia": {"lat": 21.4600, "lon": 80.1960, "state": "Maharashtra"},
    "Ludhiana": {"lat": 30.9010, "lon": 75.8573, "state": "Punjab"},
    "Khanna": {"lat": 30.7071, "lon": 76.2167, "state": "Punjab"},
    "Karnal": {"lat": 29.6857, "lon": 76.9905, "state": "Haryana"},
    "Kota": {"lat": 25.2138, "lon": 75.8648, "state": "Rajasthan"},
    "Indore": {"lat": 22.7196, "lon": 75.8577, "state": "Madhya Pradesh"},
    "Davanagere": {"lat": 14.4644, "lon": 75.9218, "state": "Karnataka"},
    "Kolar": {"lat": 13.1367, "lon": 78.1291, "state": "Karnataka"},
    "Agra": {"lat": 27.1767, "lon": 78.0081, "state": "Uttar Pradesh"},
    "Rajkot": {"lat": 22.3039, "lon": 70.8022, "state": "Gujarat"}
}

FALLBACK_WEATHER = {
    "Pune": {"temp": 28.5, "humidity": 55, "rain": 0.0, "wind": 12.0, "condition": "Partly Cloudy", "icon": "⛅"},
    "Nashik": {"temp": 27.0, "humidity": 58, "rain": 0.0, "wind": 10.5, "condition": "Pleasant", "icon": "☀️"},
    "Ludhiana": {"temp": 22.5, "humidity": 65, "rain": 0.0, "wind": 8.0, "condition": "Clear", "icon": "☀️"},
    "Karnal": {"temp": 23.0, "humidity": 62, "rain": 0.0, "wind": 9.0, "condition": "Clear", "icon": "☀️"},
    "default": {"temp": 26.0, "humidity": 60, "rain": 0.0, "wind": 10.0, "condition": "Clear Sky", "icon": "☀️"}
}

def get_agro_advisory(temp, humidity, rain):
    """Generate practical agricultural suggestions based on weather metrics."""
    suggestions = []
    if rain > 5.0:
        suggestions.append({
            "type": "warning",
            "title": "Rainfall Expected",
            "desc": "Postpone chemical pesticide spraying and fertilizer application to avoid surface runoff."
        })
    else:
        suggestions.append({
            "type": "info",
            "title": "Spraying Conditions",
            "desc": "Dry weather expected. Favorable conditions for foliar nutrient sprays and weeding."
        })

    if humidity > 75:
        suggestions.append({
            "type": "danger",
            "title": "High Fungal Risk",
            "desc": "Humid conditions favor fungal growth (Downy Mildew / Blast). Monitor lower foliage closely."
        })
    elif humidity < 40 and temp > 30:
        suggestions.append({
            "type": "warning",
            "title": "Moisture Stress",
            "desc": "Dry air and elevated temperatures accelerate evapotranspiration. Ensure timely irrigation."
        })

    if temp > 35:
        suggestions.append({
            "type": "warning",
            "title": "Heat Warning",
            "desc": "High temperature alert. Irrigate during early morning or evening hours to reduce heat stress."
        })
    elif temp < 10:
        suggestions.append({
            "type": "info",
            "title": "Cold Conditions",
            "desc": "Cool weather favorable for Rabi crops (Wheat/Gram). Guard sensitive young vegetable seedlings from frost."
        })

    return suggestions

@weather_bp.route('/')
def index():
    district = request.args.get('district', 'Pune').strip()
    geo = DISTRICT_COORDINATES.get(district, DISTRICT_COORDINATES['Pune'])

    current_data = None
    is_live = False

    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={geo['lat']}&longitude={geo['lon']}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
        res = requests.get(url, timeout=3.0)
        if res.status_code == 200:
            raw = res.json()
            curr = raw.get('current', {})
            current_data = {
                "temp": curr.get('temperature_2m', 28.0),
                "humidity": curr.get('relative_humidity_2m', 55),
                "rain": curr.get('precipitation', 0.0),
                "wind": curr.get('wind_speed_10m', 10.0),
                "condition": "Fair / Clear",
                "icon": "☀️"
            }
            is_live = True
    except Exception:
        pass

    if not current_data:
        current_data = FALLBACK_WEATHER.get(district, FALLBACK_WEATHER['default'])
        is_live = False

    advisories = get_agro_advisory(current_data['temp'], current_data['humidity'], current_data['rain'])

    return render_template(
        'weather/index.html',
        district=district,
        districts=sorted(list(DISTRICT_COORDINATES.keys())),
        weather=current_data,
        is_live=is_live,
        advisories=advisories
    )
