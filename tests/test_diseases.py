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

def test_disease_catalog_renders(client):
    """Test disease index catalog loads all records."""
    res = client.get('/diseases/')
    assert res.status_code == 200
    assert b"Pest &amp; Crop Disease Doctor" in res.data or b"Pest & Crop Disease Doctor" in res.data
    assert b"Rice Blast" in res.data
    assert b"Wheat Yellow (Stripe) Rust" in res.data
    assert b"Cotton Bollworm" in res.data

def test_disease_filters(client):
    """Test disease catalog filters by crop keyword and pathogen type."""
    # Filter by crop 'Cotton'
    res_cotton = client.get('/diseases/?crop=Cotton')
    assert res_cotton.status_code == 200
    assert b"Cotton Bollworm" in res_cotton.data

    # Filter by type 'Fungal'
    res_fungal = client.get('/diseases/?type=Fungal')
    assert res_fungal.status_code == 200
    assert b"Rice Blast" in res_fungal.data

def test_disease_detail_view(client):
    """Test single disease detail page renders symptoms, organic and chemical remedies."""
    res = client.get('/diseases/1')
    assert res.status_code == 200
    assert b"Rice Blast" in res.data
    assert b"Key Identification Symptoms" in res.data
    assert b"Organic &amp; Biological Remedies" in res.data or b"Organic & Biological Remedies" in res.data
    assert b"Recommended Chemical Treatment" in res.data

    # Invalid ID
    res_404 = client.get('/diseases/999')
    assert res_404.status_code == 404
