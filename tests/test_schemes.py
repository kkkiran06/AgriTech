import pytest
from app import create_app

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

def test_schemes_index_renders(client):
    """Test government schemes index loads and lists all 6 schemes."""
    res = client.get('/schemes/')
    assert res.status_code == 200
    assert b"Government Schemes &amp; Subsidies" in res.data or b"Government Schemes & Subsidies" in res.data
    assert b"PM Kisan Samman Nidhi" in res.data
    assert b"Pradhan Mantri Fasal Bima Yojana" in res.data
    assert b"Kisan Credit Card (KCC) Scheme" in res.data

def test_scheme_category_filter(client):
    """Test filtering schemes by category."""
    res_credit = client.get('/schemes/?category=Credit+%26+Finance')
    assert res_credit.status_code == 200
    assert b"Kisan Credit Card" in res_credit.data

    res_ins = client.get('/schemes/?category=Crop+Insurance')
    assert res_ins.status_code == 200
    assert b"Pradhan Mantri Fasal Bima Yojana" in res_ins.data
