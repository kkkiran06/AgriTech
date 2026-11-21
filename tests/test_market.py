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

def test_market_index_renders(client):
    """Test market price index renders all mandi records."""
    res = client.get('/market/')
    assert res.status_code == 200
    assert b"Agricultural Mandi Market Rates" in res.data
    assert b"Khanna Mandi" in res.data
    assert b"Kota Mandi" in res.data
    assert b"Rajkot APMC" in res.data

def test_market_filters(client):
    """Test filtering by commodity and state."""
    # Filter Wheat
    res_wheat = client.get('/market/?commodity=Wheat')
    assert res_wheat.status_code == 200
    assert b"Khanna Mandi" in res_wheat.data
    assert b"Kota Mandi" in res_wheat.data

    # Filter State
    res_gujarat = client.get('/market/?state=Gujarat')
    assert res_gujarat.status_code == 200
    assert b"Rajkot APMC" in res_gujarat.data
