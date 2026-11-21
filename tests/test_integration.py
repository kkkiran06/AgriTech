import pytest
from app import create_app

@pytest.fixture
def app():
    test_app = create_app({
        'TESTING': True,
        'DATABASE': 'krishimitra.db',
        'SECRET_KEY': 'integration-secret'
    })
    return test_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_full_farmer_journey(client, app):
    """End-to-end user journey across all agricultural modules."""
    # 1. Landing Page
    landing_res = client.get('/')
    assert landing_res.status_code == 200
    assert b"KrishiMitra" in landing_res.data

    # 2. Registration — use a unique mobile and email each run
    import time
    unique_mobile = '98' + str(int(time.time()))[-8:]
    unique_email = f'farmer_{unique_mobile}@example.com'
    reg_res = client.post('/auth/register', data={
        'name': 'Balwant Singh',
        'email': unique_email,
        'mobile': unique_mobile,
        'password': 'farmerSecure1',
        'confirm_password': 'farmerSecure1',
        'state': 'Punjab',
        'district': 'Ludhiana',
        'farm_size': '4.0',
        'primary_crops': 'Wheat, Mustard'
    }, follow_redirects=True)
    assert reg_res.status_code == 200

    # Explicit login step (no auto-login as per individual authentication requirements)
    login_res = client.post('/auth/login', data={
        'login_identifier': unique_email,
        'password': 'farmerSecure1'
    }, follow_redirects=True)
    assert login_res.status_code == 200
    assert b"Balwant Singh" in login_res.data

    # 3. Access Dashboard
    dash_res = client.get('/dashboard')
    assert dash_res.status_code == 200
    assert b"Namaste, Balwant Singh" in dash_res.data
    assert b"Ludhiana, Punjab" in dash_res.data

    # 4. View Crops Catalog and specific crop details
    crops_res = client.get('/crops/')
    assert crops_res.status_code == 200
    assert b"Crop Cultivation Guide" in crops_res.data

    crop_detail_res = client.get('/crops/2')
    if crop_detail_res.status_code == 404:
        from app.database.db import get_db
        with app.app_context():
            db2 = get_db()
            cid = db2.execute('SELECT id FROM crops LIMIT 1 OFFSET 1').fetchone()
        crop_detail_res = client.get(f'/crops/{cid["id"]}')
    assert crop_detail_res.status_code == 200
    assert b"Wheat" in crop_detail_res.data
    assert b"Ideal Temperature" in crop_detail_res.data

    # 5. Check Weather & Advisory
    weather_res = client.get('/weather/?district=Ludhiana')
    assert weather_res.status_code == 200
    assert b"Agro-Meteorological Advisory" in weather_res.data
    assert b"Ludhiana" in weather_res.data

    # 6. Calculate Fertilizer Dosage
    calc_res = client.post('/soil/', data={
        'crop': 'Wheat',
        'acres': '4.0'
    })
    assert calc_res.status_code == 200
    assert b"Fertilizer Schedule For Wheat (4.0 Acres)" in calc_res.data
    assert b"Urea (46% N)" in calc_res.data

    # 7. Diagnose Pest & Disease
    disease_res = client.get('/diseases/?crop=Wheat')
    assert disease_res.status_code == 200
    assert b"Wheat Yellow (Stripe) Rust" in disease_res.data

    disease_detail_res = client.get('/diseases/2')
    if disease_detail_res.status_code == 404:
        from app.database.db import get_db
        with app.app_context():
            db3 = get_db()
            did = db3.execute('SELECT id FROM diseases_pests LIMIT 1 OFFSET 1').fetchone()
        disease_detail_res = client.get(f'/diseases/{did["id"]}')
    assert disease_detail_res.status_code == 200
    assert b"Puccinia" in disease_detail_res.data or b"Wheat Yellow" in disease_detail_res.data

    # 8. Check APMC Market Prices
    market_res = client.get('/market/?commodity=Wheat')
    assert market_res.status_code == 200
    assert b"Khanna Mandi" in market_res.data

    # 9. Browse Government Schemes
    schemes_res = client.get('/schemes/')
    assert schemes_res.status_code == 200
    assert b"PM Kisan Samman Nidhi" in schemes_res.data
    assert b"https://pmkisan.gov.in/" in schemes_res.data

    # 10. Update Profile
    profile_res = client.post('/auth/profile', data={
        'name': 'Sardar Balwant Singh',
        'state': 'Punjab',
        'district': 'Ludhiana',
        'farm_size': '5.5',
        'primary_crops': 'Wheat, Cotton, Mustard'
    }, follow_redirects=True)
    assert profile_res.status_code == 200
    assert b"profile has been updated successfully" in profile_res.data

    # 11. Secure Logout
    logout_res = client.get('/auth/logout', follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"securely logged out" in logout_res.data
