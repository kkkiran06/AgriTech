"""
Supabase REST API Client for Real-Time Synchronization.
Connects via HTTPS port 443 (Zero timeout, zero IPv6 issues).
"""
import os
import logging
import requests

logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def sync_farmer_to_supabase(farmer_dict):
    """
    Sync a newly registered or updated farmer to Supabase in real-time.
    Non-blocking / resilient: logs error if network is offline without breaking user flow.
    """
    try:
        raw = dict(farmer_dict)
        mobile = raw.get('mobile')
        if not mobile:
            return None

        # Clean and serialize data
        clean_data = {}
        for k, v in raw.items():
            if k == 'id':
                continue  # Supabase handles its own auto-increment ID
            if k == 'created_at':
                if v:
                    clean_data[k] = str(v)
            else:
                clean_data[k] = v

        headers = get_headers()
        # Check if mobile already exists in Supabase
        check_url = f"{SUPABASE_URL}/farmers?mobile=eq.{mobile}"
        r = requests.get(check_url, headers=headers, timeout=5)
        
        if r.status_code == 200 and r.json():
            # Update existing record
            patch_url = f"{SUPABASE_URL}/farmers?mobile=eq.{mobile}"
            update_data = {k: v for k, v in clean_data.items() if k != 'mobile'}
            res = requests.patch(patch_url, headers=headers, json=update_data, timeout=5)
            success = res.status_code in (200, 204)
            print(f">>> [Supabase Real-Time] Updated farmer {mobile} ({clean_data.get('name')}) -> HTTP {res.status_code}")
            return success
        else:
            # Insert new record
            insert_url = f"{SUPABASE_URL}/farmers"
            res = requests.post(insert_url, headers=headers, json=clean_data, timeout=5)
            success = res.status_code in (200, 201)
            print(f">>> [Supabase Real-Time] Inserted new farmer {mobile} ({clean_data.get('name')}) -> HTTP {res.status_code}")
            return success
    except Exception as e:
        print(f">>> [Supabase Real-Time ERROR] Failed to sync farmer {farmer_dict.get('mobile')}: {e}")
        logger.warning(f"Supabase Real-Time Sync notice: {e}")
        return False
