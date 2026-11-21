"""
Unit & Integration Tests for newly integrated features from AGRI_SMART reference:
- RAG & Voice Agronomic Assistant (/rag/)
- Community Forum (/community/)
- Multi-Parcel Farm Management (/farms/)
- Farm Finance & PMFBY Insurance (/finance/)
- Expert Consultations (/consultations/)
- Direct Produce Marketplace (/marketplace/)
- Seasonal Lifecycle Milestones (/progress/)
"""

import pytest
from app import create_app
from app.database.db import get_db

@pytest.fixture
def app():
    test_app = create_app({
        'TESTING': True,
        'DATABASE': 'krishimitra.db',
        'SECRET_KEY': 'test-secret-reference-features'
    })
    return test_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """Client with a logged-in test farmer session."""
    with app.app_context():
        db = get_db()
        row = db.execute("SELECT * FROM farmers WHERE mobile = '9876543210'").fetchone()
        if not row:
            db.execute("""
                INSERT INTO farmers (name, mobile, password_hash, district, state, farm_size, primary_crops)
                VALUES ('Ramesh Kumar', '9876543210', 'dummy_hash', 'Mandya', 'Karnataka', 4.5, 'Paddy, Sugarcane')
            """)
            db.commit()
            farmer_id = db.execute("SELECT id FROM farmers WHERE mobile = '9876543210'").fetchone()['id']
        else:
            farmer_id = row['id']

    with client.session_transaction() as sess:
        sess['farmer_id'] = farmer_id
        sess['farmer_name'] = 'Ramesh Kumar'
        sess['mobile'] = '9876543210'
        sess['district'] = 'Mandya'
        sess['state'] = 'Karnataka'

    return client


# ── 1. RAG & Voice Assistant Tests ───────────────────────────────
def test_rag_page_renders(client):
    res = client.get('/rag/')
    assert res.status_code == 200
    assert b"Voice" in res.data or b"Knowledge" in res.data or b"ICAR" in res.data

def test_rag_topics_api(client):
    res = client.get('/rag/topics')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'title' in data[0]

def test_rag_search_api(client):
    res = client.get('/rag/search?q=blast')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)

def test_rag_ask_endpoint(client):
    res = client.post('/rag/ask', json={'question': 'What are the symptoms of rice blast and how to treat it?'})
    assert res.status_code == 200
    data = res.get_json()
    assert 'answer' in data
    assert len(data['answer']) > 0


# ── 2. Community Forum Tests ────────────────────────────────────
def test_community_page_renders(client):
    res = client.get('/community/')
    assert res.status_code == 200
    assert b"Community" in res.data or b"Forum" in res.data

def test_community_ask_requires_auth(client):
    res = client.post('/community/new', data={'title': 'Test title', 'body': 'Test body', 'category': 'Pest Control'})
    # Unauthenticated should redirect to login
    assert res.status_code == 302
    assert '/auth/login' in res.headers['Location']

def test_community_ask_and_view(auth_client, app):
    res = auth_client.post('/community/new', data={
        'title': 'Yellowing leaves on sugarcane crop',
        'body': 'My sugarcane crop is showing yellow stripes on upper leaves. What fertilizer is recommended?',
        'category': 'Soil & Fertilizer',
        'crop_name': 'Sugarcane',
        'tags': 'sugarcane, nutrients, nitrogen'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Yellowing leaves on sugarcane crop" in res.data


# ── 3. Multi-Parcel Farm Management Tests ────────────────────────
def test_farms_requires_auth(client):
    res = client.get('/farms/')
    assert res.status_code == 302
    assert '/auth/login' in res.headers['Location']

def test_farms_crud(auth_client):
    # View index
    res = auth_client.get('/farms/')
    assert res.status_code == 200
    assert b"Land Parcels" in res.data or b"Farm" in res.data

    # Add parcel
    res_add = auth_client.post('/farms/add', data={
        'name': 'North River Field',
        'location': 'Mandya Sector 4',
        'area_acres': '2.5',
        'soil_type': 'Alluvial / Loam',
        'water_source': 'Canal Irrigation',
        'latitude': '12.52',
        'longitude': '76.89',
        'notes': 'Adjacent to irrigation canal branch'
    }, follow_redirects=True)
    assert res_add.status_code == 200
    assert b"North River Field" in res_add.data


# ── 4. Farm Finance & PMFBY Insurance Tests ───────────────────────
def test_finance_requires_auth(client):
    res = client.get('/finance/')
    assert res.status_code == 302
    assert '/auth/login' in res.headers['Location']

def test_finance_ledger_and_pmfby(auth_client):
    res = auth_client.get('/finance/')
    assert res.status_code == 200
    assert b"Financial" in res.data or b"Ledger" in res.data or b"Insurance" in res.data

    # Add expense
    res_exp = auth_client.post('/finance/expenses/add', data={
        'category': 'Seed',
        'amount': '3200',
        'description': 'Hybrid paddy seeds 25kg',
        'crop_name': 'Paddy',
        'receipt_number': 'REC-901'
    }, follow_redirects=True)
    assert res_exp.status_code == 200

    # Add income
    res_inc = auth_client.post('/finance/income/add', data={
        'source': 'Crop Sale',
        'amount': '57500',
        'description': 'Paddy 25 quintals sold at Mandi',
        'quantity_quintal': '25.0',
        'price_per_quintal': '2300'
    }, follow_redirects=True)
    assert res_inc.status_code == 200

    # PMFBY insurance calculation API
    res_ins = auth_client.post('/finance/insurance/calculate', json={
        'crop_name': 'Paddy',
        'area_acres': 2.5,
        'sum_insured_per_acre': 35000,
        'season': 'Kharif'
    })
    assert res_ins.status_code == 200
    ins_data = res_ins.get_json()
    assert ins_data['farmer_share_pct'] == 2.0
    assert ins_data['farmer_premium'] > 0


# ── 5. Expert Consultations Tests ─────────────────────────────────
def test_consultations_index(auth_client):
    res = auth_client.get('/consultations/')
    assert res.status_code == 200
    assert b"Consultation" in res.data or b"Expert" in res.data

def test_consultations_experts_api(client):
    res = client.get('/consultations/experts')
    assert res.status_code == 200
    data = res.get_json()
    assert 'experts' in data
    assert len(data['experts']) >= 3


# ── 6. Direct Produce Marketplace Tests ───────────────────────────
def test_marketplace_index(client):
    res = client.get('/marketplace/')
    assert res.status_code == 200
    assert b"Marketplace" in res.data or b"Produce" in res.data

def test_marketplace_listings_api(client):
    res = client.get('/marketplace/api/listings')
    assert res.status_code == 200
    data = res.get_json()
    assert 'listings' in data

def test_marketplace_create_listing(auth_client):
    res = auth_client.post('/marketplace/listings/add', data={
        'commodity': 'Organic Tomatoes',
        'variety': 'Vaishnavi F1',
        'quantity_quintal': '50',
        'expected_price': '1800',
        'district': 'Mandya',
        'state': 'Karnataka'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Organic Tomatoes" in res.data


# ── 7. Crop Stage Milestones Tests ────────────────────────────────
def test_progress_requires_auth(client):
    res = client.get('/progress/')
    assert res.status_code == 302
    assert '/auth/login' in res.headers['Location']

def test_progress_milestones_flow(auth_client):
    res = auth_client.get('/progress/')
    assert res.status_code == 200
    assert b"Milestone" in res.data or b"Lifecycle" in res.data or b"Stage" in res.data
