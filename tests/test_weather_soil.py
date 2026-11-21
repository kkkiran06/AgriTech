import pytest
from app import create_app
from app.routes.weather import get_agro_advisory

@pytest.fixture
def app():
    test_app = create_app({
        'TESTING': True,
        'DATABASE': 'krishimitra.db',
        'SECRET_KEY': 'test-secret'
    })
    return test_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_weather_page_renders(client):
    """Test weather index page loads with current district and advisory."""
    res = client.get('/weather/?district=Pune')
    assert res.status_code == 200
    assert b"Agro-Meteorological Advisory" in res.data
    assert b"Pune" in res.data
    assert b"Current Temperature" in res.data
    assert b"Precipitation" in res.data

def test_agro_advisory_rules():
    """Verify rule-based agro-advisory triggers correct messages."""
    # Test rainfall alert
    rain_adv = get_agro_advisory(temp=25.0, humidity=80, rain=10.0)
    titles = [a['title'] for a in rain_adv]
    assert "Rainfall Expected" in titles
    assert "High Fungal Risk" in titles

    # Test heat warning
    heat_adv = get_agro_advisory(temp=38.0, humidity=35, rain=0.0)
    titles_heat = [a['title'] for a in heat_adv]
    assert "Heat Warning" in titles_heat
    assert "Moisture Stress" in titles_heat

def test_soil_page_and_calculator(client):
    """Test soil classification and NPK fertilizer calculator output."""
    # GET view
    res = client.get('/soil/')
    assert res.status_code == 200
    assert b"Alluvial Soil" in res.data
    assert b"Black Soil (Regur)" in res.data
    assert b"Interactive NPK Fertilizer Calculator" in res.data

    # POST calculation for 2.0 acres of Wheat
    post_res = client.post('/soil/', data={
        'crop': 'Wheat',
        'acres': '2.0'
    })
    assert post_res.status_code == 200
    assert b"Fertilizer Schedule For Wheat (2.0 Acres)" in post_res.data
    assert b"Urea (46% N)" in post_res.data
    assert b"DAP (18-46-0)" in post_res.data
    assert b"MOP (60% K)" in post_res.data
