import os
import tempfile
import pytest
from app import create_app
from app.database import db

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    test_app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret-key'
    })

    with test_app.app_context():
        db.init_db(test_app)

    yield test_app

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except Exception:
        pass

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_and_password_hashing(client, app):
    """Test user registration with Full Name, Email, Mobile, and verify password is safe and hashed."""
    response = client.post('/auth/register', data={
        'name': 'Ramesh Kumar',
        'email': 'ramesh@example.com',
        'mobile': '9876543210',
        'password': 'secretpassword',
        'confirm_password': 'secretpassword',
        'state': 'Punjab',
        'district': 'Ludhiana',
        'farm_size': '3.5',
        'primary_crops': 'Wheat, Rice'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Must redirect to login page with success flash (no auto-login)
    assert b"Account created successfully" in response.data or b"log in" in response.data

    # Verify user in database
    with app.app_context():
        farmer = db.get_db().execute("SELECT * FROM farmers WHERE mobile = '9876543210'").fetchone()
        assert farmer is not None
        assert farmer['name'] == 'Ramesh Kumar'
        assert farmer['email'] == 'ramesh@example.com'
        # Password must NOT be plaintext
        assert farmer['password_hash'] != 'secretpassword'
        assert farmer['password_hash'].startswith('pbkdf2:') or farmer['password_hash'].startswith('scrypt:')

def test_duplicate_registration_rejected(client):
    """Ensure duplicate mobile and duplicate email are both blocked."""
    client.post('/auth/register', data={
        'name': 'Farmer One',
        'email': 'farmer1@gmail.com',
        'mobile': '9123456789',
        'password': 'password123',
        'confirm_password': 'password123',
        'state': 'Maharashtra',
        'district': 'Pune',
        'farm_size': '2.0',
        'primary_crops': 'Tomato'
    })

    # Attempt duplicate mobile
    res_mob = client.post('/auth/register', data={
        'name': 'Farmer Duplicate Mob',
        'email': 'unique_email@gmail.com',
        'mobile': '9123456789',
        'password': 'differentpass',
        'confirm_password': 'differentpass',
        'state': 'Maharashtra',
        'district': 'Pune',
        'farm_size': '4.0',
        'primary_crops': 'Sugarcane'
    }, follow_redirects=True)
    assert b"already registered" in res_mob.data

    # Attempt duplicate email
    res_email = client.post('/auth/register', data={
        'name': 'Farmer Duplicate Email',
        'email': 'farmer1@gmail.com',
        'mobile': '9999911111',
        'password': 'differentpass',
        'confirm_password': 'differentpass',
        'state': 'Maharashtra',
        'district': 'Pune',
        'farm_size': '4.0',
        'primary_crops': 'Sugarcane'
    }, follow_redirects=True)
    assert b"already registered" in res_email.data

def test_invalid_email_format_rejected(client):
    """Verify registration rejects invalid email format."""
    res = client.post('/auth/register', data={
        'name': 'Invalid Email Farmer',
        'email': 'not-an-email',
        'mobile': '9988771122',
        'password': 'password123',
        'confirm_password': 'password123',
        'state': 'Maharashtra',
        'district': 'Pune',
        'farm_size': '2.0',
        'primary_crops': 'Wheat'
    }, follow_redirects=True)
    assert b"valid email address" in res.data

def test_no_auto_login_and_unauthenticated_dashboard_redirect(client):
    """Verify registration does not auto-login and accessing dashboard without auth redirects to login."""
    # Register
    client.post('/auth/register', data={
        'name': 'Kavita Patel',
        'email': 'kavita@patel.com',
        'mobile': '9871112233',
        'password': 'kavitapassword',
        'confirm_password': 'kavitapassword',
        'state': 'Gujarat',
        'district': 'Surat',
        'farm_size': '3.0',
        'primary_crops': 'Cotton'
    })
    
    # Try accessing dashboard immediately without logging in
    res = client.get('/dashboard')
    # Must redirect to login page
    assert res.status_code == 302
    assert '/auth/login' in res.headers.get('Location', '')

def test_login_with_mobile_and_email(client):
    """Test login succeeds with either mobile number or email address."""
    client.post('/auth/register', data={
        'name': 'Suresh Patil',
        'email': 'suresh@patil.com',
        'mobile': '9988776655',
        'password': 'farmerpass123',
        'confirm_password': 'farmerpass123',
        'state': 'Maharashtra',
        'district': 'Nashik',
        'farm_size': '5.0',
        'primary_crops': 'Cotton'
    })

    # Test invalid credentials
    res_fail = client.post('/auth/login', data={
        'login_identifier': '9988776655',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b"Invalid credentials" in res_fail.data or b"Invalid" in res_fail.data

    # Test login with Mobile Number
    res_mob = client.post('/auth/login', data={
        'login_identifier': '9988776655',
        'password': 'farmerpass123'
    }, follow_redirects=True)
    assert res_mob.status_code == 200
    assert b"Welcome back, Suresh Patil" in res_mob.data
    assert b"Namaste, Suresh Patil" in res_mob.data

    # Logout
    client.get('/auth/logout')

    # Test login with Email Address
    res_email = client.post('/auth/login', data={
        'login_identifier': 'suresh@patil.com',
        'password': 'farmerpass123'
    }, follow_redirects=True)
    assert res_email.status_code == 200
    assert b"Welcome back, Suresh Patil" in res_email.data

def test_profile_update(client, app):
    """Test updating farmer profile details with authentication."""
    client.post('/auth/register', data={
        'name': 'Geeta Devi',
        'email': 'geeta@devi.com',
        'mobile': '9811223344',
        'password': 'mypassword1',
        'confirm_password': 'mypassword1',
        'state': 'Haryana',
        'district': 'Karnal',
        'farm_size': '2.0',
        'primary_crops': 'Wheat'
    })

    # Log in first
    client.post('/auth/login', data={
        'login_identifier': '9811223344',
        'password': 'mypassword1'
    }, follow_redirects=True)

    update_res = client.post('/auth/profile', data={
        'name': 'Geeta Devi Sharma',
        'email': 'geetasharma@devi.com',
        'state': 'Haryana',
        'district': 'Karnal',
        'farm_size': '4.5',
        'primary_crops': 'Wheat, Mustard, Basmati'
    }, follow_redirects=True)

    assert update_res.status_code == 200
    assert b"profile has been updated successfully" in update_res.data

    with app.app_context():
        farmer = db.get_db().execute("SELECT * FROM farmers WHERE mobile = '9811223344'").fetchone()
        assert farmer['name'] == 'Geeta Devi Sharma'
        assert farmer['email'] == 'geetasharma@devi.com'
        assert farmer['farm_size'] == 4.5
        assert 'Mustard' in farmer['primary_crops']

def test_individual_data_storage_isolation(client):
    """Test that each farmer only sees their own private farming records, with clean empty state for new users."""
    # 1. Register and log in Farmer A
    client.post('/auth/register', data={
        'name': 'Farmer A',
        'email': 'farmerA@test.com',
        'mobile': '9000000001',
        'password': 'passA123',
        'confirm_password': 'passA123',
        'state': 'Maharashtra',
        'district': 'Pune',
        'farm_size': '3.0',
        'primary_crops': 'Soybean'
    })
    client.post('/auth/login', data={'login_identifier': '9000000001', 'password': 'passA123'}, follow_redirects=True)

    # Farmer A initially has empty state
    dash_a1 = client.get('/dashboard')
    assert b"No farming records available. Add your first record." in dash_a1.data

    # Farmer A adds a personal crop record
    rec_res = client.post('/farming-records/add', data={
        'crop_name': 'Organic Soybean Plot 1',
        'area_acres': '2.5',
        'sowing_date': '2026-06-15',
        'stage': 'Vegetative Stage',
        'expected_harvest': '2026-10-15',
        'notes': 'Bio-NPK applied.'
    }, follow_redirects=True)
    assert b"Organic Soybean Plot 1" in rec_res.data

    # 2. Logout Farmer A and Register Farmer B
    client.get('/auth/logout')
    client.post('/auth/register', data={
        'name': 'Farmer B',
        'email': 'farmerB@test.com',
        'mobile': '9000000002',
        'password': 'passB123',
        'confirm_password': 'passB123',
        'state': 'Punjab',
        'district': 'Ludhiana',
        'farm_size': '5.0',
        'primary_crops': 'Wheat'
    })
    client.post('/auth/login', data={'login_identifier': '9000000002', 'password': 'passB123'}, follow_redirects=True)

    # Farmer B MUST NOT see Farmer A's records! Must see clean empty state:
    dash_b = client.get('/dashboard')
    assert b"Organic Soybean Plot 1" not in dash_b.data
    assert b"No farming records available. Add your first record." in dash_b.data
    assert b"Namaste, Farmer B" in dash_b.data

    # Farmer B attempts to delete Farmer A's record (ID 1)
    del_res = client.post('/farming-records/delete/1', follow_redirects=True)
    assert b"unauthorized" in del_res.data.lower() or b"not found" in del_res.data.lower()
