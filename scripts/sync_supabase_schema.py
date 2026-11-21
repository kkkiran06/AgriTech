import psycopg2

def sync_schema():
    conn = psycopg2.connect(
        host='db.ojofmguhhdcvfnwgrzgd.supabase.co',
        port=5432,
        dbname='postgres',
        user='postgres',
        password='KiranKKumar',
        connect_timeout=10
    )
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = [t[0] for t in cur.fetchall()]
    print('Existing tables in Supabase public schema:', tables)

    # 1. Update farmers table
    print('Ensuring farmers table columns...')
    cur.execute("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS email TEXT;")

    # 2. Farming records table
    print('Ensuring farming_records table...')
    cur.execute("""
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
    """)

    # 3. Diagnosis history table
    print('Ensuring diagnosis_history table...')
    cur.execute("""
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
    """)

    # 4. Reload PostgREST schema cache so REST API reflects changes immediately
    print('Reloading PostgREST schema cache...')
    cur.execute("NOTIFY pgrst, 'reload schema';")

    conn.commit()
    conn.close()
    print('Schema synchronization complete!')

if __name__ == '__main__':
    sync_schema()
