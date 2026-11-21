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

    # 1. Update farmers table
    cur.execute("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS email TEXT;")

    # 2. Farming records table
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

    # 3. Multi-parcel farms table
    cur.execute("""
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
    """)

    # 4. Farm finance tables
    cur.execute("""
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
    """)

    cur.execute("""
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
    """)

    # 5. Community Q&A Forum
    cur.execute("""
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
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS community_replies (
        id SERIAL PRIMARY KEY,
        post_id INTEGER NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
        farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
        body TEXT NOT NULL,
        is_expert_verified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Consultations
    cur.execute("""
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
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS consultation_messages (
        id SERIAL PRIMARY KEY,
        consultation_id INTEGER NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
        sender_role TEXT NOT NULL,
        sender_name TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Produce Marketplace
    cur.execute("""
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
    """)

    cur.execute("""
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
    """)

    # 8. Milestones
    cur.execute("""
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
    """)

    # 9. Reload PostgREST schema cache
    cur.execute("NOTIFY pgrst, 'reload schema';")

    conn.commit()
    conn.close()
    print('All reference project tables synchronized to Supabase PostgreSQL!')

if __name__ == '__main__':
    sync_schema()
