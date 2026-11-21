"""
Sync all farmers, diagnosis history, and data from local SQLite to live Supabase REST API.
"""
import os
import sys
import sqlite3
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database.supabase_client import get_supabase_credentials, get_headers

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "krishimitra.db")

def sync():
    url, key = get_supabase_credentials()
    if not url or not key:
        print("❌ Error: SUPABASE_URL or SUPABASE_KEY not configured in .env")
        return

    headers = get_headers()
    print(f"Connecting to Supabase at {url}...")
    r = requests.get(f"{url}/farmers", headers=headers, timeout=10)
    if r.status_code != 200:
        print(f"❌ Failed to reach Supabase: HTTP {r.status_code} - {r.text}")
        return

    existing_mobiles = {row['mobile'] for row in r.json()}
    print(f"Existing farmers in Supabase: {len(existing_mobiles)}")

    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    farmers = conn.execute("SELECT * FROM farmers").fetchall()

    synced_count = 0
    for f in farmers:
        data = dict(f)
        mobile = data['mobile']
        if mobile not in existing_mobiles:
            data.pop('id', None)
            if data.get('created_at'):
                data['created_at'] = str(data['created_at'])
            res = requests.post(f"{url}/farmers", headers=headers, json=data, timeout=10)
            if res.status_code in (200, 201):
                print(f"  ✓ Synced {data['name']} ({mobile}) to Supabase!")
                synced_count += 1
            else:
                print(f"  ✗ Failed to sync {mobile}: {res.status_code} {res.text}")

    # Check total count now
    final_res = requests.get(f"{url}/farmers", headers=headers, timeout=10)
    if final_res.status_code == 200:
        print(f"\n🎉 Sync complete! Newly added: {synced_count}. Total farmers in Supabase now: {len(final_res.json())}")
        for row in final_res.json():
            print(f"   ID {row['id']}: {row['name']} | {row['mobile']} | {row['district']}, {row['state']}")

    conn.close()

if __name__ == '__main__':
    sync()
