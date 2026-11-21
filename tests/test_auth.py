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
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_and_password_hashing(client, app):
    """Test user registration and verify password is safe and hashed."""
    response = client.post('/auth/register', data={
        'name': 'Ramesh Kumar',
        'mobile': '9876543210',
        'password': 'secretpassword',
        'confirm_password': 'secretpassword',
        'state': 'Punjab',
        'district': 'Ludhiana',
        'farm_size': '3.5',
        'primary_crops': 'Wheat, Rice'
    }, follow_redirects=True)
    
    assert response.status_code == 200

    # Verify user in database
    with app.app_context():
        farmer = db.get_db().execute("SELECT * FROM farmers WHERE mobile = '9876543210'").fetchone()
        assert farmer is not None
        assert farmer['name'] == 'Ramesh Kumar'
        # Password must NOT be plaintext
        assert farmer['password_hash'] != 'secretpassword'
        assert farmer['password_hash'].startswith('pbkdf2:') or farmer['password_hash'].startswith('scrypt:')

def test_duplicate_registration_rejected(client):
    """Ensure duplicate mobile number is blocked."""
    client.post('/auth/register', data={
        'name': 'Farmer One',
        'mobile': '9123456789',
        'password': 'password123',
        'confirm_password': 'password123',
        'state': 'Maharashtra',
        'district': 'Pune',
        'farm_size': '2.0',
        'primary_crops': 'Tomato'
    })
    client.get('/auth/logout')

    # Attempt duplicate registration
    res = client.post('/auth/register', data={
        'name': 'Farmer Duplicate',
        'mobile': '9123456789',
        'password': 'differentpass',
        'confirm_password': 'differentpass',
        'state': 'Maharashtra',
        'district': 'Pune',
        'farm_size': '4.0',
        'primary_crops': 'Sugarcane'
    }, follow_redirects=True)

    assert b"already registered" in res.data

def test_login_success_and_failure(client):
    """Test login with valid and invalid credentials."""
    client.post('/auth/register', data={
        'name': 'Suresh Patil',
        'mobile': '9988776655',
        'password': 'farmerpass123',
        'confirm_password': 'farmerpass123',
        'state': 'Maharashtra',
        'district': 'Nashik',
        'farm_size': '5.0',
        'primary_crops': 'Cotton'
    })
    client.get('/auth/logout')

    # Test invalid password
    res_fail = client.post('/auth/login', data={
        'mobile': '9988776655',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b"Invalid mobile number or password" in res_fail.data

    # Test valid password
    res_succ = client.post('/auth/login', data={
        'mobile': '9988776655',
        'password': 'farmerpass123'
    }, follow_redirects=True)
    assert res_succ.status_code == 200
    assert b"Welcome back, Suresh Patil" in res_succ.data

def test_profile_update(client, app):
    """Test updating farmer profile details."""
    client.post('/auth/register', data={
        'name': 'Geeta Devi',
        'mobile': '9811223344',
        'password': 'mypassword1',
        'confirm_password': 'mypassword1',
        'state': 'Haryana',
        'district': 'Karnal',
        'farm_size': '2.0',
        'primary_crops': 'Wheat'
    })

    update_res = client.post('/auth/profile', data={
        'name': 'Geeta Devi Sharma',
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
        assert farmer['farm_size'] == 4.5
        assert 'Mustard' in farmer['primary_crops']
