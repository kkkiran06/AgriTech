"""
Migrate KrishiMitra database schema and data from local SQLite to Supabase PostgreSQL.
Target: db.ojofmguhhdcvfnwgrzgd.supabase.co:5432
"""
import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

SUPABASE_HOST = os.environ.get('SUPABASE_HOST', 'db.ojofmguhhdcvfnwgrzgd.supabase.co')
SUPABASE_PORT = int(os.environ.get('SUPABASE_PORT', 5432))
SUPABASE_DB = os.environ.get('SUPABASE_DB', 'postgres')
SUPABASE_USER = os.environ.get('SUPABASE_USER', 'postgres')
SUPABASE_PASSWORD = os.environ.get('SUPABASE_PASSWORD', 'KiranKKumar')

SQLITE_PATH = os.path.join(os.path.dirname(__file__), '..', 'krishimitra.db')

POSTGRES_SCHEMA = """
-- 1. Farmers table
CREATE TABLE IF NOT EXISTS farmers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    mobile TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'Maharashtra',
    district TEXT NOT NULL,
    farm_size DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    primary_crops TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Crops table
CREATE TABLE IF NOT EXISTS crops (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    scientific_name TEXT,
    category TEXT NOT NULL,
    season TEXT NOT NULL,
    suitable_soil TEXT NOT NULL,
    min_temp DOUBLE PRECISION NOT NULL,
    max_temp DOUBLE PRECISION NOT NULL,
    rainfall_mm TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    sowing_guide TEXT NOT NULL,
    irrigation_guide TEXT NOT NULL,
    fertilizer_guide TEXT NOT NULL,
    harvesting_guide TEXT NOT NULL,
    icon TEXT DEFAULT '🌾'
);

-- 3. Soil and Fertilizer recommendations
CREATE TABLE IF NOT EXISTS fertilizer_soil (
    id SERIAL PRIMARY KEY,
    soil_type TEXT NOT NULL UNIQUE,
    characteristics TEXT NOT NULL,
    suitable_crops TEXT NOT NULL,
    organic_recommendations TEXT NOT NULL,
    chemical_recommendations TEXT NOT NULL,
    npk_ratio TEXT NOT NULL,
    ph_range TEXT NOT NULL
);

-- 4. Crop Diseases & Pests
CREATE TABLE IF NOT EXISTS diseases_pests (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    affected_crops TEXT NOT NULL,
    symptoms TEXT NOT NULL,
    prevention TEXT NOT NULL,
    organic_treatment TEXT NOT NULL,
    chemical_treatment TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'Moderate',
    image_url TEXT
);

-- 5. Market Prices (APMC Mandis)
CREATE TABLE IF NOT EXISTS market_prices (
    id SERIAL PRIMARY KEY,
    commodity TEXT NOT NULL,
    variety TEXT NOT NULL,
    market TEXT NOT NULL,
    district TEXT NOT NULL,
    state TEXT NOT NULL,
    min_price DOUBLE PRECISION NOT NULL,
    max_price DOUBLE PRECISION NOT NULL,
    modal_price DOUBLE PRECISION NOT NULL,
    is_sample INTEGER NOT NULL DEFAULT 1,
    updated_date TEXT NOT NULL
);

-- 6. Government Agricultural Schemes
CREATE TABLE IF NOT EXISTS government_schemes (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    short_desc TEXT NOT NULL,
    benefits TEXT NOT NULL,
    eligibility TEXT NOT NULL,
    documents_required TEXT NOT NULL,
    official_url TEXT NOT NULL,
    badge_label TEXT DEFAULT 'Central Scheme'
);

-- 7. PlantDoctor AI — Diagnosis History
CREATE TABLE IF NOT EXISTS diagnosis_history (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    disease_name TEXT NOT NULL,
    plant_name TEXT NOT NULL,
    confidence_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    severity TEXT NOT NULL DEFAULT 'Unknown',
    ai_mode TEXT NOT NULL DEFAULT 'demo',
    symptoms_summary TEXT,
    treatment_summary TEXT,
    image_b64 TEXT,
    diagnosed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Farming Records
CREATE TABLE IF NOT EXISTS farming_records (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    crop_name TEXT NOT NULL,
    area_acres DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    sowing_date TEXT,
    stage TEXT DEFAULT 'Sowing / Seedling',
    expected_harvest TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Multi-Parcel Farms
CREATE TABLE IF NOT EXISTS farms (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'Karnataka',
    district TEXT NOT NULL,
    taluk TEXT,
    village TEXT,
    survey_number TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    total_area DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    area_unit TEXT DEFAULT 'acres',
    soil_type TEXT DEFAULT 'Red Sandy Loam',
    water_source TEXT DEFAULT 'Borewell',
    irrigation_type TEXT DEFAULT 'Drip Irrigation',
    ownership_type TEXT DEFAULT 'Owned',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Farm Expenses
CREATE TABLE IF NOT EXISTS farm_expenses (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    farm_id INTEGER REFERENCES farms(id) ON DELETE SET NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    expense_date TEXT NOT NULL,
    season TEXT DEFAULT 'Kharif 2026',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Farm Income
CREATE TABLE IF NOT EXISTS farm_income (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    farm_id INTEGER REFERENCES farms(id) ON DELETE SET NULL,
    source TEXT NOT NULL,
    description TEXT NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    income_date TEXT NOT NULL,
    season TEXT DEFAULT 'Kharif 2026',
    quantity_quintal DOUBLE PRECISION,
    price_per_quintal DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. Community Forum
CREATE TABLE IF NOT EXISTS community_posts (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'General',
    tags TEXT,
    upvotes INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS community_replies (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    is_expert_verified INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Consultations
CREATE TABLE IF NOT EXISTS consultations (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    expert_name TEXT DEFAULT 'Dr. S. Patil (Senior Agronomist, UAS)',
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT DEFAULT 'Crop Disease',
    urgency TEXT DEFAULT 'Medium',
    status TEXT DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consultation_messages (
    id SERIAL PRIMARY KEY,
    consultation_id INTEGER NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
    sender_role TEXT NOT NULL,
    sender_name TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. Produce Marketplace
CREATE TABLE IF NOT EXISTS produce_listings (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    commodity TEXT NOT NULL,
    variety TEXT,
    quantity_quintal DOUBLE PRECISION NOT NULL,
    expected_price DOUBLE PRECISION NOT NULL,
    district TEXT NOT NULL,
    state TEXT NOT NULL,
    harvest_date TEXT,
    quality_grade TEXT DEFAULT 'Grade A',
    is_organic INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS produce_orders (
    id SERIAL PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES produce_listings(id) ON DELETE CASCADE,
    buyer_name TEXT NOT NULL,
    buyer_contact TEXT NOT NULL,
    quantity_quintal DOUBLE PRECISION NOT NULL,
    offered_price DOUBLE PRECISION NOT NULL,
    message TEXT,
    status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. Seasonal Lifecycle Milestones
CREATE TABLE IF NOT EXISTS farmer_milestones (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    crop_name TEXT NOT NULL,
    season TEXT NOT NULL,
    stage_name TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    completed_date TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def migrate():
    print(f"Connecting to Supabase PostgreSQL at {SUPABASE_HOST}...")
    pg_conn = psycopg2.connect(
        host=SUPABASE_HOST,
        port=SUPABASE_PORT,
        dbname=SUPABASE_DB,
        user=SUPABASE_USER,
        password=SUPABASE_PASSWORD,
        sslmode='require'
    )
    pg_cur = pg_conn.cursor(cursor_factory=RealDictCursor)
    print("✓ Connected to Supabase!")

    # 1. Execute schema creation
    print("Applying schema to Supabase...")
    pg_cur.execute(POSTGRES_SCHEMA)
    pg_conn.commit()
    print("✓ All 7 tables created or verified in Supabase!")

    # 2. Connect to SQLite to read current seed data
    if not os.path.exists(SQLITE_PATH):
        print("SQLite database not found. Skipping data transfer.")
        pg_conn.close()
        return

    print(f"Reading data from SQLite: {SQLITE_PATH}...")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    tables = [
        'crops',
        'fertilizer_soil',
        'diseases_pests',
        'market_prices',
        'government_schemes',
        'farmers',
        'farming_records',
        'diagnosis_history',
        'farms',
        'farm_expenses',
        'farm_income',
        'community_posts',
        'community_replies',
        'consultations',
        'consultation_messages',
        'produce_listings',
        'produce_orders',
        'farmer_milestones'
    ]

    for table in tables:
        sqlite_cur.execute(f"SELECT * FROM {table}")
        rows = sqlite_cur.fetchall()
        if not rows:
            print(f"  - {table}: 0 rows (empty)")
            continue

        # Check existing count in Postgres
        pg_cur.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
        res = pg_cur.fetchone()
        existing_count = res['cnt'] if res else 0

        if table == 'farmers':
            # Sync any new farmers whose mobile number is not yet in Supabase
            pg_cur.execute("SELECT mobile FROM farmers")
            existing_mobiles = {r['mobile'] for r in pg_cur.fetchall()}
            new_rows = [r for r in rows if r['mobile'] not in existing_mobiles]
            if not new_rows:
                print(f"  ✓ farmers: all {len(rows)} local farmers already exist in Supabase.")
                continue
            rows = new_rows
            print(f"  - farmers: found {len(new_rows)} new farmer(s) to sync to Supabase...")
        elif existing_count > 0:
            print(f"  - {table}: already has {existing_count} rows in Supabase. Skipping insert.")
            continue

        col_names = [description[0] for description in sqlite_cur.description]
        placeholders = ", ".join(["%s"] * len(col_names))
        cols_str = ", ".join(col_names)
        insert_sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"

        data_to_insert = [tuple(row[c] for c in col_names) for row in rows]
        pg_cur.executemany(insert_sql, data_to_insert)
        pg_conn.commit()

        # Reset serial sequence if id column exists
        if 'id' in col_names:
            try:
                pg_cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1)) FROM {table};")
                pg_conn.commit()
            except Exception:
                pg_conn.rollback()

        print(f"  ✓ {table}: successfully transferred {len(rows)} rows to Supabase!")

    try:
        pg_cur.execute("NOTIFY pgrst, 'reload schema';")
        pg_conn.commit()
    except Exception:
        pass

    sqlite_conn.close()
    pg_conn.close()
    print("\n🎉 Migration to Supabase PostgreSQL completed successfully!")


if __name__ == '__main__':
    migrate()
