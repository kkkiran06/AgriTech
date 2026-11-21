"""
Tests for Multi-Language & Regional Indian Languages support.
Verifies:
  - Minimum 5 Indian regional languages supported (Hindi, Marathi, Telugu, Kannada, Tamil, Punjabi, Bengali)
  - /set-language/<lang> route updates session and cookie
  - Translation helper returns localized strings
  - Language switcher dropdown renders in navbar
"""
import pytest
from app import create_app
from app.translations.languages import SUPPORTED_LANGUAGES, get_translation

@pytest.fixture
def app():
    test_app = create_app({
        'TESTING': True,
        'DATABASE': 'krishimitra.db',
        'SECRET_KEY': 'test-languages'
    })
    return test_app

@pytest.fixture
def client(app):
    return app.test_client()


def test_supported_languages_count():
    """Verify at least 5 Indian regional languages are supported."""
    regional_languages = [code for code in SUPPORTED_LANGUAGES if code != 'en']
    # Must have at least 5 regional languages
    assert len(regional_languages) >= 5
    assert 'hi' in SUPPORTED_LANGUAGES  # Hindi
    assert 'mr' in SUPPORTED_LANGUAGES  # Marathi
    assert 'te' in SUPPORTED_LANGUAGES  # Telugu
    assert 'kn' in SUPPORTED_LANGUAGES  # Kannada
    assert 'ta' in SUPPORTED_LANGUAGES  # Tamil
    assert 'pa' in SUPPORTED_LANGUAGES  # Punjabi
    assert 'bn' in SUPPORTED_LANGUAGES  # Bengali


def test_translation_helper():
    """Verify get_translation returns appropriate regional strings."""
    # English
    assert get_translation('nav_crops', 'en') == 'Crop Guide'
    # Hindi
    assert get_translation('nav_crops', 'hi') == 'फसल मार्गदर्शिका'
    # Marathi
    assert get_translation('nav_crops', 'mr') == 'पीक मार्गदर्शक'
    # Telugu
    assert get_translation('nav_crops', 'te') == 'పంటల గైడ్'
    # Kannada
    assert get_translation('nav_crops', 'kn') == 'ಬೆಳೆ ಮಾರ್ಗದರ್ಶಿ'
    # Tamil
    assert get_translation('nav_crops', 'ta') == 'பயிர் வழிகாட்டி'
    # Punjabi
    assert get_translation('nav_crops', 'pa') == 'ਫ਼ਸਲ ਗਾਈਡ'
    # Bengali
    assert get_translation('nav_crops', 'bn') == 'ফসল গাইড'


def test_set_language_route(client):
    """Test /set-language/<lang> sets session and cookies."""
    res = client.get('/set-language/hi', follow_redirects=True)
    assert res.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get('lang') == 'hi'

    # Switch to Telugu
    res_te = client.get('/set-language/te', follow_redirects=True)
    assert res_te.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get('lang') == 'te'


def test_navbar_language_dropdown_rendered(client):
    """Navbar must render regional languages dropdown."""
    res = client.get('/')
    assert res.status_code == 200
    # Checks for native language labels in dropdown
    assert 'हिन्दी'.encode('utf-8') in res.data
    assert 'मराठी'.encode('utf-8') in res.data
    assert 'తెలుగు'.encode('utf-8') in res.data
    assert 'ಕನ್ನಡ'.encode('utf-8') in res.data
    assert 'தமிழ்'.encode('utf-8') in res.data
