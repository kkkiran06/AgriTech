"""
Sync all farmers, diagnosis history, and data from local SQLite to live Supabase REST API.
"""
import os
import sqlite3
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "krishimitra.db")

def sync():
    print("Syncing farmers from SQLite to Supabase...")
    r = requests.get(f"{SUPABASE_URL}/farmers", headers=HEADERS, timeout=10)
    existing_mobiles = {row['mobile'] for row in r.json()} if r.status_code == 200 else set()
    print(f"Existing farmers in Supabase: {len(existing_mobiles)}")

    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    farmers = conn.execute("SELECT * FROM farmers").fetchall()

    for f in farmers:
        data = dict(f)
        mobile = data['mobile']
        if mobile not in existing_mobiles:
            data.pop('id', None)
            res = requests.post(f"{SUPABASE_URL}/farmers", headers=HEADERS, json=data, timeout=10)
            if res.status_code in (200, 201):
                print(f"  ✓ Synced {data['name']} ({mobile}) to Supabase!")
            else:
                print(f"  ✗ Failed to sync {mobile}: {res.status_code} {res.text}")

    # Check total count now
    final_res = requests.get(f"{SUPABASE_URL}/farmers", headers=HEADERS, timeout=10)
    if final_res.status_code == 200:
        print(f"\n🎉 Sync complete! Total farmers in Supabase now: {len(final_res.json())}")
        for row in final_res.json():
            print(f"   ID {row['id']}: {row['name']} | {row['mobile']} | {row['district']}, {row['state']}")

    conn.close()

if __name__ == '__main__':
    sync()
