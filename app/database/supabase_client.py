"""
Supabase REST API Client for Real-Time Synchronization.
Connects via HTTPS port 443 (Zero timeout, resilient cloud sync).
"""
import os
import logging
import requests

logger = logging.getLogger(__name__)

def _load_env_if_needed():
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_KEY"):
        env_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k not in os.environ:
                            os.environ[k] = v

def get_supabase_credentials():
    _load_env_if_needed()
    url = os.environ.get("SUPABASE_URL", "").rstrip('/')
    key = os.environ.get("SUPABASE_KEY", "")
    return url, key

def get_headers():
    _, key = get_supabase_credentials()
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def sync_farmer_to_supabase(farmer_dict):
    """
    Sync a newly registered or updated farmer to Supabase in real-time.
    Non-blocking / resilient: logs error if network is offline without breaking user flow.
    """
    try:
        url, key = get_supabase_credentials()
        if not url or not key:
            print(">>> [Supabase Real-Time] SUPABASE_URL or SUPABASE_KEY not set in .env")
            return False

        raw = dict(farmer_dict)
        mobile = raw.get('mobile')
        if not mobile:
            return False

        # Clean and serialize data
        clean_data = {}
        allowed_cols = {'name', 'email', 'mobile', 'password_hash', 'state', 'district', 'farm_size', 'primary_crops', 'created_at'}
        for k in allowed_cols:
            if k in raw:
                v = raw[k]
                if k == 'created_at' and v:
                    clean_data[k] = str(v)
                elif k == 'farm_size' and v is not None:
                    try:
                        clean_data[k] = float(v)
                    except ValueError:
                        clean_data[k] = 1.0
                elif k == 'email' and v:
                    clean_data[k] = str(v).strip().lower()
                elif k == 'email' and not v:
                    clean_data[k] = None
                else:
                    clean_data[k] = v

        headers = get_headers()
        # Check if mobile already exists in Supabase
        check_url = f"{url}/farmers?mobile=eq.{mobile}"
        r = requests.get(check_url, headers=headers, timeout=5)
        
        if r.status_code == 200 and r.json():
            # Update existing record
            patch_url = f"{url}/farmers?mobile=eq.{mobile}"
            update_data = {k: v for k, v in clean_data.items() if k != 'mobile'}
            res = requests.patch(patch_url, headers=headers, json=update_data, timeout=5)
            success = res.status_code in (200, 204)
            print(f">>> [Supabase Real-Time] Updated farmer {mobile} ({clean_data.get('name')}) -> HTTP {res.status_code}")
            return success
        else:
            # Insert new record
            insert_url = f"{url}/farmers"
            res = requests.post(insert_url, headers=headers, json=clean_data, timeout=5)
            success = res.status_code in (200, 201)
            print(f">>> [Supabase Real-Time] Inserted new farmer {mobile} ({clean_data.get('name')}) -> HTTP {res.status_code}")
            return success
    except Exception as e:
        print(f">>> [Supabase Real-Time ERROR] Failed to sync farmer {farmer_dict.get('mobile')}: {e}")
        logger.warning(f"Supabase Real-Time Sync notice: {e}")
        return False

def get_farmer_from_supabase(identifier):
    """
    Fetch farmer record from Supabase by mobile or email.
    Used for bidirectional authentication and cloud lookup.
    """
    try:
        url, key = get_supabase_credentials()
        if not url or not key:
            return None

        headers = get_headers()
        identifier = str(identifier).strip()
        
        # Check by mobile
        if identifier.isdigit() and len(identifier) == 10:
            check_url = f"{url}/farmers?mobile=eq.{identifier}&limit=1"
        else:
            # Check by email
            check_url = f"{url}/farmers?email=eq.{identifier.lower()}&limit=1"

        r = requests.get(check_url, headers=headers, timeout=5)
        if r.status_code == 200 and r.json():
            return r.json()[0]
        return None
    except Exception as e:
        logger.warning(f"Supabase fetch farmer error: {e}")
        return None

def sync_farming_record_to_supabase(record_dict, farmer_mobile):
    """
    Sync a farming crop record to Supabase in real-time.
    """
    try:
        url, key = get_supabase_credentials()
        if not url or not key or not farmer_mobile:
            return False

        headers = get_headers()
        # Find farmer in Supabase
        check_url = f"{url}/farmers?mobile=eq.{farmer_mobile}&select=id&limit=1"
        r = requests.get(check_url, headers=headers, timeout=5)
        if r.status_code != 200 or not r.json():
            return False

        sb_farmer_id = r.json()[0]['id']
        data = {
            'farmer_id': sb_farmer_id,
            'crop_name': record_dict.get('crop_name'),
            'area_acres': float(record_dict.get('area_acres', 1.0)),
            'sowing_date': record_dict.get('sowing_date'),
            'stage': record_dict.get('stage', 'Sowing / Seedling'),
            'expected_harvest': record_dict.get('expected_harvest'),
            'notes': record_dict.get('notes')
        }

        insert_url = f"{url}/farming_records"
        res = requests.post(insert_url, headers=headers, json=data, timeout=5)
        success = res.status_code in (200, 201)
        print(f">>> [Supabase Real-Time] Synced farming record '{data['crop_name']}' -> HTTP {res.status_code}")
        return success
    except Exception as e:
        logger.warning(f"Supabase sync farming record error: {e}")
        return False

def delete_farming_record_from_supabase(crop_name, farmer_mobile):
    """
    Delete a farming record from Supabase in real-time.
    """
    try:
        url, key = get_supabase_credentials()
        if not url or not key or not farmer_mobile or not crop_name:
            return False

        headers = get_headers()
        check_url = f"{url}/farmers?mobile=eq.{farmer_mobile}&select=id&limit=1"
        r = requests.get(check_url, headers=headers, timeout=5)
        if r.status_code != 200 or not r.json():
            return False

        sb_farmer_id = r.json()[0]['id']
        del_url = f"{url}/farming_records?farmer_id=eq.{sb_farmer_id}&crop_name=eq.{crop_name}"
        res = requests.delete(del_url, headers=headers, timeout=5)
        return res.status_code in (200, 204)
    except Exception as e:
        logger.warning(f"Supabase delete farming record error: {e}")
        return False

def sync_diagnosis_to_supabase(diag_dict, farmer_mobile):
    """
    Sync a plant/soil AI diagnosis record to Supabase in real-time.
    """
    try:
        url, key = get_supabase_credentials()
        if not url or not key or not farmer_mobile:
            return False

        headers = get_headers()
        check_url = f"{url}/farmers?mobile=eq.{farmer_mobile}&select=id&limit=1"
        r = requests.get(check_url, headers=headers, timeout=5)
        if r.status_code != 200 or not r.json():
            return False

        sb_farmer_id = r.json()[0]['id']
        data = {
            'farmer_id': sb_farmer_id,
            'disease_name': diag_dict.get('disease_name'),
            'plant_name': diag_dict.get('plant_name'),
            'confidence_score': float(diag_dict.get('confidence_score', 0.0)),
            'severity': diag_dict.get('severity', 'Unknown'),
            'ai_mode': diag_dict.get('ai_mode', 'gemini_vision'),
            'symptoms_summary': diag_dict.get('symptoms_summary'),
            'treatment_summary': diag_dict.get('treatment_summary')
        }

        insert_url = f"{url}/diagnosis_history"
        res = requests.post(insert_url, headers=headers, json=data, timeout=5)
        return res.status_code in (200, 201)
    except Exception as e:
        logger.warning(f"Supabase sync diagnosis error: {e}")
        return False
