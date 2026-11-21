import pytest
from app import create_app
from app.database import db

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

def test_home_page_renders(client):
    """Test landing page loads cleanly with 200 OK."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"KrishiMitra" in response.data
    assert b"Smart Agriculture For Every Farmer" in response.data

def test_crops_catalog_and_filter(client):
    """Test crops catalog loads all crops and responds to season/category filters."""
    # All crops
    res_all = client.get('/crops/')
    assert res_all.status_code == 200
    assert b"Rice (Paddy)" in res_all.data
    assert b"Wheat" in res_all.data
    assert b"Cotton" in res_all.data

    # Filter by Kharif
    res_kharif = client.get('/crops/?season=Kharif')
    assert res_kharif.status_code == 200
    assert b"Rice (Paddy)" in res_kharif.data

    # Filter by Category
    res_cash = client.get('/crops/?category=Cash+Crops')
    assert res_cash.status_code == 200
    assert b"Cotton" in res_cash.data
    assert b"Sugarcane" in res_cash.data

def test_crop_detail_view(client):
    """Test single crop detail page returns accurate agronomic fields."""
    # Crop 1 (Rice)
    res = client.get('/crops/1')
    assert res.status_code == 200
    assert b"Rice (Paddy)" in res.data
    assert b"Sowing &amp; Seed Preparation" in res.data or b"Sowing & Seed Preparation" in res.data
    assert b"Irrigation Management" in res.data
    assert b"Fertilizer &amp; Nutrition" in res.data or b"Fertilizer & Nutrition" in res.data

    # Invalid crop ID
    res_404 = client.get('/crops/999')
    assert res_404.status_code == 404
