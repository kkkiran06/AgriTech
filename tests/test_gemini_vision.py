"""
Unit & Integration Tests for Gemini Multimodal Vision Engine (Leaf & Soil Scanning).
"""
import io
import pytest
from PIL import Image
from app import create_app
from app.ml.gemini_vision import (
    get_gemini_api_key,
    detect_mime_type,
    build_agronomist_prompt,
    analyze_crop_or_soil
)

@pytest.fixture
def app():
    test_app = create_app({
        'TESTING': True,
        'DATABASE': 'krishimitra.db',
        'SECRET_KEY': 'test-gemini-vision'
    })
    return test_app

@pytest.fixture
def client(app):
    return app.test_client()

def create_test_image(color=(34, 139, 34), fmt='JPEG'):
    img = Image.new('RGB', (80, 80), color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def test_gemini_api_key_configured():
    """Verify Gemini API key is configured from environment."""
    key = get_gemini_api_key()
    assert key is not None
    assert len(key) > 10


def test_mime_type_detection():
    """Verify MIME detection for JPEG and PNG formats."""
    jpg = create_test_image(fmt='JPEG')
    png = create_test_image(fmt='PNG')
    assert detect_mime_type(jpg) == 'image/jpeg'
    assert detect_mime_type(png) == 'image/png'


def test_prompt_generation_schema():
    """Verify prompts contain required schema fields for leaf and soil."""
    leaf_p = build_agronomist_prompt('leaf', 'en')
    soil_p = build_agronomist_prompt('soil', 'en')
    auto_p = build_agronomist_prompt('auto', 'en')

    assert 'scan_type' in leaf_p and 'organic_treatment' in leaf_p
    assert 'Indian Soil Type' in soil_p and 'npk_advice' in soil_p
    assert 'leaf or soil' in auto_p


def test_gemini_vision_leaf_analysis():
    """Verify leaf image analysis produces structured diagnostic output."""
    leaf_bytes = create_test_image(color=(34, 139, 34))
    res = analyze_crop_or_soil(leaf_bytes, target_hint='leaf')
    assert res['success'] is True
    assert res['scan_type'] in ('leaf', 'soil')
    assert len(res['subject_name']) > 0
    assert len(res['health_status']) > 0
    assert len(res['organic_treatment']) > 0
    assert len(res['chemical_treatment']) > 0


def test_gemini_vision_soil_analysis():
    """Verify soil image analysis produces structured soil & fertilizer output."""
    soil_bytes = create_test_image(color=(120, 65, 30))
    res = analyze_crop_or_soil(soil_bytes, target_hint='soil')
    assert res['success'] is True
    assert res['scan_type'] == 'soil'
    assert len(res['subject_name']) > 0
    assert len(res['npk_advice']) > 0
    assert len(res['suitable_crops']) > 0


def test_soil_scan_route_integration(client):
    """POST a soil image with scan_type='soil' to /plantdoctor/diagnose."""
    soil_bytes = create_test_image(color=(120, 65, 30))
    data = {
        'source': 'upload',
        'scan_type': 'soil',
        'plant_image': (io.BytesIO(soil_bytes), 'farm_soil.jpg', 'image/jpeg')
    }
    res = client.post('/plantdoctor/diagnose', data=data,
                       content_type='multipart/form-data', follow_redirects=True)
    assert res.status_code == 200
    assert b'SOIL HEALTH' in res.data or b'Soil' in res.data
    assert b'NPK Fertilizer' in res.data or b'NPK' in res.data


def test_soil_page_has_camera_scanner_banner(client):
    """Verify the /soil/ page prominently links to the AI Soil Scanner."""
    res = client.get('/soil/')
    assert res.status_code == 200
    assert b'Scan Soil with AI' in res.data
    assert b'scan_type=soil' in res.data
