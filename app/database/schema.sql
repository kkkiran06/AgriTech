-- KrishiMitra SQLite Database Schema
PRAGMA foreign_keys = ON;

-- 1. Farmers table (Registered Individual Users)
CREATE TABLE IF NOT EXISTS farmers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    mobile TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'Maharashtra',
    district TEXT NOT NULL,
    farm_size REAL NOT NULL DEFAULT 1.0,
    primary_crops TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Crops table
CREATE TABLE IF NOT EXISTS crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    scientific_name TEXT,
    category TEXT NOT NULL,        -- Cereals, Pulses, Cash Crops, Oilseeds, Vegetables
    season TEXT NOT NULL,          -- Kharif, Rabi, Zaid
    suitable_soil TEXT NOT NULL,
    min_temp REAL NOT NULL,
    max_temp REAL NOT NULL,
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,            -- Fungal, Bacterial, Viral, Insect Pest
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commodity TEXT NOT NULL,
    variety TEXT NOT NULL,
    market TEXT NOT NULL,
    district TEXT NOT NULL,
    state TEXT NOT NULL,
    min_price REAL NOT NULL,
    max_price REAL NOT NULL,
    modal_price REAL NOT NULL,
    is_sample INTEGER NOT NULL DEFAULT 1, -- 1 = Curated Benchmark Sample, 0 = Live Feed
    updated_date TEXT NOT NULL
);

-- 7. PlantDoctor AI — Diagnosis History
CREATE TABLE IF NOT EXISTS diagnosis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    disease_name TEXT NOT NULL,
    plant_name TEXT NOT NULL,
    confidence_score REAL NOT NULL DEFAULT 0.0,
    severity TEXT NOT NULL DEFAULT 'Unknown',
    ai_mode TEXT NOT NULL DEFAULT 'demo',   -- 'ai' or 'demo'
    symptoms_summary TEXT,
    treatment_summary TEXT,
    image_b64 TEXT,                          -- Compressed base64 thumbnail
    diagnosed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
);

-- 6. Government Agricultural Schemes
CREATE TABLE IF NOT EXISTS government_schemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,        -- Income Support, Insurance, Credit, Soil, Equipment, Irrigation
    short_desc TEXT NOT NULL,
    benefits TEXT NOT NULL,
    eligibility TEXT NOT NULL,
    documents_required TEXT NOT NULL,
    official_url TEXT NOT NULL,
    badge_label TEXT DEFAULT 'Central Scheme'
);

-- 8. Individual Farmer Farming Records (Personal Crop Log & Field Data)
CREATE TABLE IF NOT EXISTS farming_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    crop_name TEXT NOT NULL,
    area_acres REAL NOT NULL DEFAULT 1.0,
    sowing_date TEXT,
    stage TEXT DEFAULT 'Sowing / Seedling',
    expected_harvest TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
);

-- 9. Multi-Parcel Farm Management
CREATE TABLE IF NOT EXISTS farms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'Karnataka',
    district TEXT NOT NULL,
    taluk TEXT,
    village TEXT,
    survey_number TEXT,
    latitude REAL,
    longitude REAL,
    total_area REAL NOT NULL DEFAULT 1.0,
    area_unit TEXT DEFAULT 'acres',
    soil_type TEXT DEFAULT 'Red Sandy Loam',
    water_source TEXT DEFAULT 'Borewell',
    irrigation_type TEXT DEFAULT 'Drip Irrigation',
    ownership_type TEXT DEFAULT 'Owned',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
);

-- 10. Farm Financial Management (Expenses & Income)
CREATE TABLE IF NOT EXISTS farm_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    farm_id INTEGER,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    expense_date TEXT NOT NULL,
    season TEXT DEFAULT 'Kharif 2026',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE,
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS farm_income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    farm_id INTEGER,
    source TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    income_date TEXT NOT NULL,
    season TEXT DEFAULT 'Kharif 2026',
    quantity_quintal REAL,
    price_per_quintal REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE,
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE SET NULL
);

-- 11. Community Q&A Forum
CREATE TABLE IF NOT EXISTS community_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'General',
    tags TEXT,
    upvotes INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS community_replies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    farmer_id INTEGER NOT NULL,
    body TEXT NOT NULL,
    is_expert_verified INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
);

-- 12. Expert Consultations
CREATE TABLE IF NOT EXISTS consultations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    expert_name TEXT DEFAULT 'Dr. S. Patil (Senior Agronomist, UAS)',
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT DEFAULT 'Crop Disease',
    urgency TEXT DEFAULT 'Medium',
    status TEXT DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS consultation_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultation_id INTEGER NOT NULL,
    sender_role TEXT NOT NULL,
    sender_name TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES consultations(id) ON DELETE CASCADE
);

-- 13. Produce Marketplace (Direct-to-Buyer / Direct-to-Consumer)
CREATE TABLE IF NOT EXISTS produce_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    commodity TEXT NOT NULL,
    variety TEXT,
    quantity_quintal REAL NOT NULL,
    expected_price REAL NOT NULL,
    district TEXT NOT NULL,
    state TEXT NOT NULL,
    harvest_date TEXT,
    quality_grade TEXT DEFAULT 'Grade A',
    is_organic INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS produce_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id INTEGER NOT NULL,
    buyer_name TEXT NOT NULL,
    buyer_contact TEXT NOT NULL,
    quantity_quintal REAL NOT NULL,
    offered_price REAL NOT NULL,
    message TEXT,
    status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES produce_listings(id) ON DELETE CASCADE
);

-- 14. Seasonal Milestones Tracking
CREATE TABLE IF NOT EXISTS farmer_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    crop_name TEXT NOT NULL,
    season TEXT NOT NULL,
    stage_name TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    completed_date TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
);
