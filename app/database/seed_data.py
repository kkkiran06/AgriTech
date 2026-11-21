"""
Seed data script for KrishiMitra.
Populates SQLite database with rich, realistic agricultural data.
"""
import sqlite3
import os

CROPS_DATA = [
    (
        "Rice (Paddy)", "Oryza sativa", "Cereals", "Kharif",
        "Clayey, Alluvial, Loamy (water retaining)", 21.0, 37.0, "1000 - 1500 mm",
        120,
        "Sow nursery in June-July. Transplant 20-25 day seedlings at 20x15 cm spacing. Keep 2-3 seedlings per hill.",
        "Flooding during vegetative stage (2-5 cm standing water). Drain field 10 days before harvest.",
        "NPK 100:50:50 kg/ha. Apply 50% N + full P & K as basal; remaining N in 2 splits at tillering and panicle initiation.",
        "Harvest when 80-85% grains turn golden yellow. Moisture level should be around 20-22%.",
        "🌾"
    ),
    (
        "Wheat", "Triticum aestivum", "Cereals", "Rabi",
        "Well-drained Fertile Loam, Clay Loam, Alluvial", 12.0, 25.0, "400 - 650 mm",
        135,
        "Sow between Nov 1 - Nov 20. Seed rate: 100 kg/ha. Line sowing at 20-22 cm row distance, 4-5 cm depth.",
        "Critical irrigation at Crown Root Initiation (21 days), Tillering (40-45 days), Flowering (80-85 days), and Grain Filling.",
        "NPK 120:60:40 kg/ha. Half N + full P & K basal; half N top-dressed after first irrigation.",
        "Harvest when stalks turn dry and golden brown, grains become hard and break with crisp sound.",
        "🌿"
    ),
    (
        "Cotton", "Gossypium hirsutum", "Cash Crops", "Kharif",
        "Deep Black Soil (Regur), Medium Black Soil", 20.0, 35.0, "500 - 800 mm",
        160,
        "Sow in May-June after pre-monsoon shower. Spacing: 90x60 cm or 120x45 cm for Bt Cotton.",
        "Irrigate at squaring, flowering, and boll formation stages. Avoid waterlogging at all costs.",
        "NPK 100:50:50 kg/ha. Apply FYM 10 t/ha before sowing. Split nitrogen into 3 doses.",
        "Pick mature open bolls in early morning hours. Avoid picking stained or damp bolls.",
        "☁️"
    ),
    (
        "Maize (Corn)", "Zea mays", "Cereals", "Kharif / Rabi",
        "Well-drained Sandy Loam to Silty Loam", 18.0, 32.0, "500 - 750 mm",
        105,
        "Kharif sowing in June-July; Rabi sowing in October. Spacing: 60x20 cm. Seed rate: 20 kg/ha.",
        "Critical irrigation at tasseling (silking) and grain filling stages. Highly sensitive to waterlogging.",
        "NPK 120:60:40 kg/ha with Zinc Sulfate (25 kg/ha). Apply nitrogen in 3 equal splits.",
        "Harvest when outer husks dry out and turn papery white, and black layer forms at base of grain.",
        "🌽"
    ),
    (
        "Sugarcane", "Saccharum officinarum", "Cash Crops", "Annual",
        "Deep Rich Alluvial, Well-drained Black Soil", 20.0, 38.0, "1500 - 2500 mm",
        365,
        "Plant 2-3 bud setts in furrows spaced 90-120 cm apart. Autumn planting (Oct) or Spring (Feb-March).",
        "Requires 20-25 irrigations depending on agro-climatic zone. Drip irrigation saves up to 40% water.",
        "NPK 250:100:125 kg/ha. Apply organic compost (15 t/ha) during land preparation.",
        "Harvest when brix reading exceeds 18% and lower leaves dry completely. Cut cane flush with ground level.",
        "🎋"
    ),
    (
        "Tomato", "Solanum lycopersicum", "Vegetables", "Rabi / Kharif",
        "Well-drained Sandy Loam rich in organic matter (pH 6.0 - 7.0)", 15.0, 30.0, "400 - 600 mm",
        90,
        "Transplant 4-5 week seedlings at 60x45 cm spacing on raised beds. Mulching is highly recommended.",
        "Light frequent irrigation. Drip irrigation with fertigation gives best yields. Avoid wetting foliage.",
        "NPK 100:60:60 kg/ha + 25 t/ha FYM. Apply calcium nitrate during fruit setting to prevent blossom end rot.",
        "Harvest at breaker stage for long distance transport or pink/red ripe stage for local markets.",
        "🍅"
    ),
    (
        "Potato", "Solanum tuberosum", "Vegetables", "Rabi",
        "Loose, Friable, Well-aerated Sandy Loam", 15.0, 24.0, "350 - 500 mm",
        100,
        "Plant certified disease-free seed tubers (30-40g) at 60x20 cm spacing, 5-7 cm depth in Oct-Nov.",
        "Earthing up at 30 days after planting. Keep ridges moist; stop irrigation 10-12 days before harvest.",
        "NPK 150:100:100 kg/ha + 20 t/ha well-decomposed farmyard manure.",
        "Dehaulm (cut foliage) 10 days before digging to harden tuber skins. Dry in shade after harvest.",
        "🥔"
    ),
    (
        "Groundnut (Peanut)", "Arachis hypogaea", "Oilseeds", "Kharif / Summer",
        "Sandy Loam, Red Sandy Soil with good calcium content", 22.0, 34.0, "450 - 600 mm",
        110,
        "Sow in June-July with onset of monsoon. Seed rate: 100-120 kg kernels/ha. Spacing: 30x10 cm.",
        "Critical irrigation at flowering, pegging, and pod development stages. Avoid hoeing after peg entry.",
        "NPK 25:50:50 kg/ha + Gypsum 400 kg/ha applied at pegging stage to ensure well-filled pods.",
        "Harvest when leaves turn yellow, inner shell of pod turns brownish-black, and kernels pop easily.",
        "🥜"
    )
]

SOILS_DATA = [
    (
        "Alluvial Soil",
        "Most fertile and widespread soil formed by river deposition. Rich in Potash and Lime, deficient in Nitrogen and Phosphorus.",
        "Rice, Wheat, Sugarcane, Maize, Pulses, Jute, Oilseeds",
        "Apply well-rotted FYM (10 t/ha), green manuring with Dhaincha, and vermicompost.",
        "Balanced NPK application (120:60:40) with Urea split doses and Zinc supplement.",
        "4:2:1",
        "6.5 - 7.8"
    ),
    (
        "Black Soil (Regur)",
        "Formed from volcanic lava rocks. High clay content, immense moisture retention capacity, self-ploughing cracks during dry season.",
        "Cotton, Soybean, Wheat, Sorghum (Jowar), Chickpea, Citrus fruits",
        "Incorporate organic crop residues and bio-fertilizers (Azotobacter, Phosphobacteria).",
        "Phosphorus application is crucial (DAP/SSP). Deep placement of nitrogenous fertilizers to avoid volatilization.",
        "2:2:1",
        "7.2 - 8.5"
    ),
    (
        "Red and Yellow Soil",
        "Derived from crystalline rocks. Red color due to ferric oxide diffusion; light textured with low water retention and low nutrient base.",
        "Groundnut, Millets (Ragi, Bajra), Tobacco, Pulses, Oilseeds, Mango",
        "Heavy organic manuring (FYM 15 t/ha) and bio-fertilizers. Mulching to conserve soil moisture.",
        "Requires supplementary Lime/Dolomite in acidic regions, followed by NPK 80:40:40 with micronutrients.",
        "3:1.5:1",
        "5.5 - 6.8"
    ),
    (
        "Laterite Soil",
        "Formed under high rainfall and high temperature via intensive leaching. Highly acidic, poor in organic matter, nitrogen, and phosphate.",
        "Tea, Coffee, Cashew, Rubber, Coconut, Pepper, Arecanut",
        "Apply abundant compost, cow dung manure, and bio-inoculants. Terrace farming to prevent erosion.",
        "Liming is essential to correct acidity (Agricultural Lime 2-4 t/ha) + slow-release rock phosphate.",
        "2:1:2",
        "4.5 - 5.5"
    ),
    (
        "Clayey Loam",
        "Balanced mixture of clay, silt, and sand. Moderate drainage, high cation exchange capacity, holds nutrients well.",
        "Paddy, Wheat, Sugarcane, Tomato, Cauliflower, Cabbage",
        "Vermicompost, decomposed leaf mold, and regular incorporation of crop stubble.",
        "Standard balanced NPK with sulfur and boron trace elements.",
        "4:2:2",
        "6.0 - 7.5"
    ),
    (
        "Sandy Loam",
        "Coarse texture with great aeration and rapid drainage. Warms up quickly in spring; prone to leaching.",
        "Potato, Carrot, Groundnut, Watermelon, Muskmelon, Onion, Garlic",
        "Add heavy green manure, compost, and biochar to improve water and nutrient holding capacity.",
        "Split nitrogen fertilizer into 3-4 small applications to prevent leaching down groundwater.",
        "3:2:2",
        "6.0 - 7.0"
    )
]

DISEASES_DATA = [
    (
        "Rice Blast", "Fungal", "Rice (Paddy)",
        "Spindle-shaped lesions on leaves with gray centers and brown borders. Rotten neck and panicle breakage.",
        "Use certified resistant varieties. Avoid excessive nitrogenous fertilizers. Maintain optimum plant spacing.",
        "Seed treatment with Trichoderma viride (10g/kg). Spray fermented butter milk diluted 1:10.",
        "Spray Tricyclazole 75% WP @ 0.6 g/L or Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/L.",
        "Severe",
        "/static/images/diseases/rice_blast.svg"
    ),
    (
        "Wheat Yellow (Stripe) Rust", "Fungal", "Wheat",
        "Yellow-orange powdery pustules arranged in linear stripes on leaf surfaces. Shriveled grain filling.",
        "Plant rust-resistant cultivars (HD 2967, PBW 550). Early sowing in November.",
        "Spray Cow urine extract (10%) and neem oil (3ml/L) as protective barrier.",
        "Spray Propiconazole 25% EC (Tilt) @ 1 ml/L or Tebuconazole 25% WG @ 1 g/L at first sign of pustules.",
        "Severe",
        "/static/images/diseases/wheat_rust.svg"
    ),
    (
        "Cotton Bollworm (Helicoverpa)", "Insect Pest", "Cotton, Chickpea, Tomato",
        "Caterpillars bore circular holes into bolls and buds. Dropping of squares, leaves with chewed margins.",
        "Install pheromone traps @ 5 traps/acre. Grow Marigold as trap crop along borders.",
        "Release Trichogramma egg parasitoids @ 60,000/acre. Spray Neem Seed Kernel Extract (NSKE 5%).",
        "Spray Emamectin Benzoate 5% SG @ 0.5 g/L or Chlorantraniliprole 18.5% SC @ 0.3 ml/L.",
        "Severe",
        "/static/images/diseases/cotton_bollworm.svg"
    ),
    (
        "Early Blight of Tomato / Potato", "Fungal", "Tomato, Potato",
        "Target-board concentric dark brown rings on older lower leaves. Yellowing and premature leaf fall.",
        "Crop rotation with non-solanaceous crops. Stake plants to keep leaves off damp soil. Drip irrigation.",
        "Spray baking soda solution (5g/L) + Neem oil (3ml/L). Remove and destroy lower infected foliage.",
        "Spray Mancozeb 75% WP @ 2.5 g/L or Chlorothalonil 75% WP @ 2 g/L at 10-day intervals.",
        "Moderate",
        "/static/images/diseases/early_blight.svg"
    ),
    (
        "Fall Armyworm", "Insect Pest", "Maize (Corn), Sorghum",
        "Ragged holes on whorl leaves with sawdust-like fecal frass. Pin-hole feeding on young seedlings.",
        "Deep summer ploughing. Intercrop with pulses. Install solar light traps @ 1/acre.",
        "Apply dry sand or wood ash mixed with lime into leaf whorls. Spray Bacillus thuringiensis (Bt) @ 2 g/L.",
        "Apply Chlorantraniliprole 18.5% SC @ 0.4 ml/L or Spinetoram 11.7% SC @ 0.5 ml/L into whorls.",
        "Severe",
        "/static/images/diseases/fall_armyworm.svg"
    ),
    (
        "Sugarcane Red Rot", "Fungal", "Sugarcane",
        "Third or fourth leaf turns pale yellow and withers. Splitting cane shows longitudinal red tissues with white cross patches.",
        "Plant healthy disease-free setts. Hot water treatment of setts at 52°C for 30 minutes. Strict crop rotation.",
        "Sett dip treatment in Trichoderma harzianum suspension (10g/L) for 15 minutes before furrow planting.",
        "Dip setts in Carbendazim 50% WP @ 1 g/L solution prior to planting. Rogue out infected clumps immediately.",
        "Severe",
        "/static/images/diseases/sugarcane_red_rot.svg"
    ),
    (
        "Aphids & Whiteflies", "Insect Pest", "Vegetables, Cotton, Mustard",
        "Clusters of tiny soft-bodied green/black insects on tender shoots. Sticky honeydew leading to black sooty mold.",
        "Install yellow sticky traps @ 10 traps/acre. Maintain predatory ladybird beetles and lacewings.",
        "Spray 5% Neem oil emulsion or soap water spray (10g washing soap per litre water).",
        "Spray Imidacloprid 17.8% SL @ 0.5 ml/L or Acetamiprid 20% SP @ 0.4 g/L.",
        "Moderate",
        "/static/images/diseases/aphids.svg"
    ),
    (
        "Powdery Mildew", "Fungal", "Pulses, Cucurbits, Mango",
        "White talcum-like powdery spots on upper leaf surfaces and stems. Leaves curl upwards and wither.",
        "Provide wide plant spacing for sunlight penetration and air movement. Avoid overhead sprinkler irrigation.",
        "Spray milk-water solution (1:9) or wettable sulfur (Sulfex @ 3g/L) during morning hours.",
        "Spray Dinocap 48% EC @ 1 ml/L or Hexaconazole 5% EC @ 1 ml/L.",
        "Moderate",
        "/static/images/diseases/powdery_mildew.svg"
    )
]

MARKET_DATA = [
    ("Wheat", "Sharbati", "Khanna Mandi", "Ludhiana", "Punjab", 2350.0, 2680.0, 2520.0, 1, "2026-11-20"),
    ("Wheat", "Kalyan Sona", "Kota Mandi", "Kota", "Rajasthan", 2200.0, 2450.0, 2350.0, 1, "2026-11-20"),
    ("Wheat", "Lokwan", "Indore Mandi", "Indore", "Madhya Pradesh", 2400.0, 2800.0, 2650.0, 1, "2026-11-20"),
    ("Rice (Paddy)", "Basmati 1121", "Karnal Mandi", "Karnal", "Haryana", 3800.0, 4450.0, 4200.0, 1, "2026-11-20"),
    ("Rice (Paddy)", "Common (Grade A)", "Gondia Mandi", "Gondia", "Maharashtra", 2183.0, 2350.0, 2250.0, 1, "2026-11-20"),
    ("Cotton", "Medium Staple", "Rajkot APMC", "Rajkot", "Gujarat", 6800.0, 7450.0, 7150.0, 1, "2026-11-20"),
    ("Cotton", "Long Staple", "Adilabad APMC", "Adilabad", "Telangana", 7100.0, 7650.0, 7400.0, 1, "2026-11-20"),
    ("Maize (Corn)", "Yellow Hybrid", "Davanagere Mandi", "Davanagere", "Karnataka", 2050.0, 2300.0, 2180.0, 1, "2026-11-20"),
    ("Tomato", "Hybrid Local", "Kolar Market", "Kolar", "Karnataka", 1400.0, 2100.0, 1750.0, 1, "2026-11-20"),
    ("Tomato", "Special Red", "Nashik APMC", "Nashik", "Maharashtra", 1300.0, 1950.0, 1600.0, 1, "2026-11-20"),
    ("Potato", "Jyoti", "Agra Mandi", "Agra", "Uttar Pradesh", 1100.0, 1450.0, 1280.0, 1, "2026-11-20"),
    ("Groundnut", "Bold Kernels", "Bikaner Mandi", "Bikaner", "Rajasthan", 5900.0, 6600.0, 6300.0, 1, "2026-11-20")
]

SCHEMES_DATA = [
    (
        "PM Kisan Samman Nidhi (PM-KISAN)",
        "Income Support",
        "Direct income support of ₹6,000 per year in three equal instalments of ₹2,000 directly transferred into farmer bank accounts.",
        "Financial safety net of ₹6,000 annually via DBT for agricultural inputs, seed purchases, and seasonal expenses.",
        "All landholding farmer families with cultivable land in their names (subject to exclusion criteria for high income / institutional owners).",
        "Aadhaar Card, Land ownership documents (7/12, Khatauni), Active Bank Passbook linked with Aadhaar, Mobile Number.",
        "https://pmkisan.gov.in/",
        "Central Sector Scheme"
    ),
    (
        "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "Crop Insurance",
        "Comprehensive crop insurance cover against non-preventable natural risks from pre-sowing to post-harvest stages.",
        "Lowest premium rates: 2% for Kharif crops, 1.5% for Rabi crops, and 5% for Annual Horticultural/Commercial crops. Full claim payout for yield losses.",
        "All farmers including sharecroppers and tenant farmers growing notified crops in notified areas are eligible.",
        "Land Record (RoR), Sowing Certificate from Patwari/Gram Sevak, Bank Passbook, Aadhaar Card, Proposal Form.",
        "https://pmfby.gov.in/",
        "Flagship Insurance"
    ),
    (
        "Kisan Credit Card (KCC) Scheme",
        "Credit & Finance",
        "Simplified short-term institutional credit at highly subsidized interest rates to meet cultivation and farm maintenance needs.",
        "Concessional credit limit up to ₹3 Lakhs at an effective interest rate of 4% per annum (with 3% prompt repayment incentive).",
        "Individual/joint farmers, tenant farmers, oral lessees, self-help groups (SHGs), and joint liability groups (JLGs).",
        "Application Form, Two Passport Photos, Identity & Address Proof (Aadhaar/Voter ID), Land Records with crop pattern certificate.",
        "https://www.myscheme.gov.in/schemes/kcc",
        "Concessional Credit"
    ),
    (
        "Soil Health Card Scheme (SHC)",
        "Soil & Fertilizers",
        "Issue soil health cards to farmers every 2 years indicating the nutrient status of their farm soil along with customized fertilizer recommendations.",
        "Free laboratory testing of 12 soil parameters (N, P, K, S, Zn, Fe, Cu, Mn, Bo, pH, EC, OC) to prevent over-fertilization and reduce input costs by 15-20%.",
        "All farmers possessing agricultural land in all States and Union Territories across India.",
        "Soil sample collection form, Aadhaar Card, Land ownership parcel number (Survey/Khasra number).",
        "https://soilhealth.dac.gov.in/",
        "Soil Care"
    ),
    (
        "Sub-Mission on Agricultural Mechanization (SMAM)",
        "Farm Equipment",
        "Subsidy on modern agricultural machinery, tractors, power tillers, rotavators, and establishment of Custom Hiring Centres (CHCs).",
        "40% to 50% financial subsidy on procurement of farm equipment, enabling small and marginal farmers to mechanize farm operations.",
        "Small, marginal, SC/ST, and women farmers are prioritized for higher subsidy slabs.",
        "Aadhaar Card, Land ownership proof, Bank Account details, Category certificate (if applicable), Quotation of equipment from authorized dealer.",
        "https://agrimachinery.nic.in/",
        "Mechanization Subsidy"
    ),
    (
        "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)",
        "Irrigation",
        "'Per Drop More Crop' initiative promoting micro-irrigation systems (drip and sprinkler) to maximize water use efficiency.",
        "Up to 55% subsidy for small & marginal farmers and 45% for other farmers for installing drip and sprinkler irrigation systems.",
        "All farmers having cultivable land with an assured water source (borewell, open well, farm pond, or canal access).",
        "Land Records (7/12 & 8A or equivalent), Water source verification certificate, Electricity bill/pump certificate, Aadhaar Card, Bank Passbook.",
        "https://pmksy.gov.in/",
        "Water Conservation"
    )
]

def seed_database(db_path=None):
    """Seed the SQLite database with full initial dataset."""
    if db_path is None:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'krishimitra.db')
    
    db_path = os.path.abspath(db_path)
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute schema
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())

    # 1. Seed Crops
    cursor.execute("DELETE FROM crops")
    cursor.executemany("""
        INSERT INTO crops (
            name, scientific_name, category, season, suitable_soil,
            min_temp, max_temp, rainfall_mm, duration_days,
            sowing_guide, irrigation_guide, fertilizer_guide, harvesting_guide, icon
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, CROPS_DATA)

    # 2. Seed Soils
    cursor.execute("DELETE FROM fertilizer_soil")
    cursor.executemany("""
        INSERT INTO fertilizer_soil (
            soil_type, characteristics, suitable_crops, organic_recommendations,
            chemical_recommendations, npk_ratio, ph_range
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, SOILS_DATA)

    # 3. Seed Diseases & Pests
    cursor.execute("DELETE FROM diseases_pests")
    cursor.executemany("""
        INSERT INTO diseases_pests (
            name, type, affected_crops, symptoms, prevention,
            organic_treatment, chemical_treatment, severity, image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, DISEASES_DATA)

    # 4. Seed Market Prices
    cursor.execute("DELETE FROM market_prices")
    cursor.executemany("""
        INSERT INTO market_prices (
            commodity, variety, market, district, state,
            min_price, max_price, modal_price, is_sample, updated_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, MARKET_DATA)

    # 5. Seed Government Schemes
    cursor.execute("DELETE FROM government_schemes")
    cursor.executemany("""
        INSERT INTO government_schemes (
            title, category, short_desc, benefits, eligibility,
            documents_required, official_url, badge_label
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, SCHEMES_DATA)

    conn.commit()
    
    # Verify counts
    counts = {}
    for table in ['crops', 'fertilizer_soil', 'diseases_pests', 'market_prices', 'government_schemes']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]
    
    conn.close()
    print("Database seeding completed successfully!")
    print(f"Table row counts: {counts}")
    return counts

if __name__ == '__main__':
    seed_database()
