"""
AGRI SMART — Agricultural Knowledge Corpus
File: backend/app/rag/knowledge_data.py

Curated knowledge base sourced from ICAR (Indian Council of Agricultural Research),
University of Agricultural Sciences Bangalore (UASB GKVK), and UAS Dharwad.
Covers major Indian crops, organic solutions, IPM, soil care, and government schemes.
"""

AGRICULTURAL_KNOWLEDGE_BASE = [
    {
        "id": "kb_paddy_blast",
        "crop": "Paddy / Rice",
        "category": "Disease Management",
        "title": "Paddy Blast Disease (Magnaporthe oryzae) Management",
        "source": "ICAR-NRRI & UAS Bangalore Package of Practices",
        "tags": ["paddy", "rice", "blast", "benki roga", "magnaporthe", "leaf blast", "neck blast"],
        "content": """
Paddy Blast (Magnaporthe oryzae), locally known in Kannada as 'Benki Roga' (ಬೆಂಕಿ ರೋಗ), is one of the most destructive fungal diseases of rice.
Symptoms:
- Spindle-shaped lesions with grey or white centres and brownish borders on leaf blades.
- Lesions enlarge and coalesce, causing entire leaves to wither and dry up.
- In Neck Blast stage, black lesions appear at the neck node of the panicle, causing grains to become chaffy and the panicle to snap.

Cultural & Organic Control:
1. Avoid excessive application of Nitrogen fertilizers; apply Nitrogen in 3 split doses (basal, tillering, panicle initiation).
2. Maintain optimum plant spacing to avoid dense canopy microclimates.
3. Seed treatment: Treat seeds with Pseudomonas fluorescens @ 10g/kg seed or Trichoderma harzianum @ 10g/kg seed before nursery sowing.
4. Foliar spray of Pseudomonas fluorescens (0.5%) or fermented Panchagavya (3%) at early vegetative and panicle emergence stages.

Chemical Control (Only when threshold exceeds 5% leaf area infected):
- Spray Tricyclazole 75% WP @ 0.6 g/litre water OR Isoprothiolane 40% EC @ 1.5 ml/litre water.
- Ensure thorough spray coverage on both sides of the leaf in early morning.
- Safety Warning: Never spray during strong winds; observe minimum 21 days pre-harvest interval (PHI).
""",
    },
    {
        "id": "kb_ragi_blast",
        "crop": "Ragi (Finger Millet)",
        "category": "Disease Management",
        "title": "Finger Millet (Ragi) Blast & Cultivar Advisory",
        "source": "UAS Bangalore All India Coordinated Research Project on Millets",
        "tags": ["ragi", "finger millet", "blast", "kole roga", "gpu-28", "ml-365", "indaf-8"],
        "content": """
Finger Millet (Ragi) Blast is caused by Pyricularia grisea. It attacks seedlings, leaves, neck, and finger head.
Symptoms:
- Oval to diamond-shaped lesions on leaves with brown margins.
- Head blast causes neck to turn brown or black, preventing grain filling.

Management & Recommended Varieties for Karnataka:
1. Cultivar Selection: Grow resistant or moderately resistant varieties such as GPU-28, ML-365, KMR-301, or GPU-48. Avoid susceptible varieties in endemic zones.
2. Seed Treatment: Treat seeds with Carbendazim @ 2g/kg seed or Trichoderma viride @ 5g/kg seed.
3. Balanced Nutrition: Apply Farmyard Manure (FYM) @ 7.5 tonnes/ha along with recommended N:P:K (50:40:25 kg/ha). Apply Potash to enhance stalk and disease resistance.
4. Foliar Spray: If disease appears in field, spray Kitazin 48% EC @ 1 ml/litre or Saaf (Carbendazim 12% + Mancozeb 63% WP) @ 2 g/litre.
""",
    },
    {
        "id": "kb_tomato_early_late_blight",
        "crop": "Tomato",
        "category": "Disease Management",
        "title": "Tomato Early Blight and Late Blight Identification & IPM",
        "source": "ICAR-Indian Institute of Horticultural Research (IIHR), Hesaraghatta",
        "tags": ["tomato", "early blight", "late blight", "alternaria", "phytophthora", "ele suttuva roga"],
        "content": """
Early Blight (Alternaria solani) vs Late Blight (Phytophthora infestans):
- Early Blight: Characteristic concentric dark rings ('target board' pattern) on older lower leaves. Surrounding tissue turns chlorotic yellow. Favoured by alternating dry and warm-humid cycles (24-30°C).
- Late Blight: Water-soaked, pale greenish-black irregular patches that rapidly enlarge under cool, cloudy, and high humidity conditions (>90% RH, 15-22°C). White fluffy fungal downy growth on the underside of leaves during morning dew.

Integrated Management:
1. Sanitation: Remove and burn infected lower leaves touching soil. Avoid sprinkler irrigation which wets foliage.
2. Staking & Trellising: Tie indeterminate plants to bamboo stakes or trellises to keep foliage well above the ground and improve air circulation.
3. Preventative Bio-Control: Spray Bacillus subtilis or Trichoderma viride @ 5 ml/litre weekly.
4. Chemical Control:
   - For Early Blight: Spray Chlorothalonil 75 WP @ 2g/L or Mancozeb 75 WP @ 2.5g/L.
   - For Late Blight emergency: Spray Metalaxyl 8% + Mancozeb 64% WP (Ridomil MZ) @ 2g/L or Cymoxanil 8% + Mancozeb 64% WP @ 2g/L.
   - Safety: Discontinue chemical spraying at least 7 days before harvest.
""",
    },
    {
        "id": "kb_cotton_pink_bollworm",
        "crop": "Cotton",
        "category": "Pest Management",
        "title": "Integrated Management of Cotton Pink Bollworm (Pectinophora gossypiella)",
        "source": "Central Institute for Cotton Research (CICR) & UAS Dharwad",
        "tags": ["cotton", "pink bollworm", "gulabi hula", "pectinophora", "rosette flower"],
        "content": """
Pink Bollworm (PBW) is the primary pest threatening cotton production in South and Central India.
Damage Symptoms:
- 'Rosette flower' appearance: Young petals stay twisted and closed due to larvae webbing inside.
- Bores into squares and green bolls; exit holes are tiny and plug with frass.
- Internal staining and destruction of lint and seeds ('double seeds' symptom).

IPM Strategy:
1. Pheromone Monitoring: Install 5 Gossyplure pheromone traps per acre from 45 days after sowing (DAS). Count moth catches weekly.
2. Economic Threshold Level (ETL): 8 moths/trap/night for 3 consecutive days OR 10% rosette flowers or boll damage.
3. Mass Trapping: Increase to 15-20 traps/acre if moth catches surge.
4. Release Trichogramma bactrae egg parasitoid wasps @ 60,000/acre at 7-day intervals starting from square formation.
5. Foliar Chemical Spray (Strictly based on ETL):
   - At 60-90 DAS: Spray Neem oil (Azadirachtin 1500 ppm) @ 5 ml/L.
   - If ETL exceeded: Spray Profenofos 50 EC @ 2 ml/L or Chlorantraniliprole 18.5 SC @ 0.3 ml/L.
""",
    },
    {
        "id": "kb_maize_fall_armyworm",
        "crop": "Maize (Corn)",
        "category": "Pest Management",
        "title": "Maize Fall Armyworm (Spodoptera frugiperda) Control Protocol",
        "source": "ICAR-National Bureau of Agricultural Insect Resources (NBAIR), Bengaluru",
        "tags": ["maize", "fall armyworm", "faw", "spodoptera", "corn borer", "jola"],
        "content": """
Fall Armyworm (FAW) is an invasive voracious caterpillar that feeds on maize whorls, leaves, and developing cobs.
Symptoms:
- Ragged feeding holes on whorl leaves with abundant sawdust-like moist fecal pellets (frass).
- Inverted 'Y' shaped mark on caterpillar head capsule with 4 dark spots arranged in a square on the 8th abdominal segment.

Control Schedule:
1. First 20 Days: Intercrop maize with cowpea (2:1 or 4:1 ratio) to attract natural predators.
2. Bio-Pesticide: Spray Metarhizium rileyi or Beauveria bassiana @ 5 g/litre inside the whorl during evening hours.
3. Whorl Application: Apply sand mixed with neem seed kernel powder or dry soil + ash (9:1) into whorls to suffocate young larvae.
4. If damage exceeds 10% plants: Apply Emamectin Benzoate 5% SG @ 0.4 g/L water or Chlorantraniliprole 18.5 SC @ 0.4 ml/L directly directed into the whorl.
""",
    },
    {
        "id": "kb_karnataka_subsidies_schemes",
        "crop": "General Agriculture",
        "category": "Government Schemes & Finance",
        "title": "Karnataka Agricultural Subsidies, Micro-Irrigation & Insurance Guide",
        "source": "Department of Agriculture, Government of Karnataka (Raitha Mithra)",
        "tags": ["subsidy", "drip irrigation", "karnataka", "pm-kisan", "pmfby", "raitha siri", "kisan credit card"],
        "content": """
Key Agricultural Financial Schemes for Farmers in Karnataka:
1. Pradhan Mantri Krishi Sinchayee Yojana (PMKSY) - Micro Irrigation:
   - Drip and Sprinkler irrigation subsidy: Up to 90% subsidy for SC/ST small/marginal farmers (up to 5 acres).
   - 75% to 90% subsidy for General category small and marginal farmers; 45-55% for other farmers.
   - Apply through local Raitha Samparka Kendra (RSK) or the Karnataka DBT portal.
2. PM-KISAN & Raitha Siri Scheme:
   - PM-KISAN: ₹6,000/year in 3 equal installments of ₹2,000 credited directly to Aadhaar-linked bank accounts.
   - Raitha Siri (Karnataka Millet Scheme): Incentive of ₹10,000 per hectare (max 2 ha) for farmers cultivating millets (Ragi, Jowar, Bajra, Foxtail millet).
3. Pradhan Mantri Fasal Bima Yojana (PMFBY):
   - Crop insurance against drought, floods, pests. Premium rate: Kharif food & oilseed crops 2%, Rabi crops 1.5%, Commercial/horticultural crops 5%.
   - Deadline for Kharif insurance is typically July 31st; enroll via CSC or bank branches.
4. Soil Health Card Scheme: Free testing of N, P, K, pH, EC, Organic Carbon, and micronutrients at district soil testing laboratories every 2 years.
""",
    },
    {
        "id": "kb_soil_health_organic",
        "crop": "Soil & Water",
        "category": "Soil Fertility Management",
        "title": "Soil Organic Carbon Improvement & Bio-Fertilizer Protocols",
        "source": "UAS Bangalore Department of Soil Science",
        "tags": ["soil health", "vermicompost", "green manure", "jeevaramrutha", "panchagavya", "npk", "ph"],
        "content": """
Maintaining Soil Organic Carbon (SOC) above 0.5% is essential for soil microbial activity and water retention.
Practices to Revitalize Soil:
1. Green Manuring: Sow Sunn hemp (Crotalaria juncea) or Dhaincha (Sesbania aculeata) with pre-monsoon showers. Plough into soil at 45-50 days (flowering stage). Adds 15-20 tonnes/ha green biomass and 60-80 kg Nitrogen.
2. Jeevamrutha Preparation:
   - Mix 10 kg local cow dung, 5-10 L cow urine, 2 kg jaggery, 2 kg pulse flour, and handful of fertile field soil in 200 L water.
   - Ferment for 48-72 hours in shade, stirring clockwise twice daily.
   - Apply 200 L/acre through irrigation water or as foliar spray every 15-21 days.
3. Micronutrient Deficiency Management:
   - Zinc Deficiency (khaira disease / interveinal chlorosis in paddy & maize): Apply Zinc Sulphate (ZnSO4) @ 20-25 kg/ha to soil, or foliar spray 0.5% ZnSO4 + 0.25% lime.
   - Iron Chlorosis in alkaline/calcareous soils: Spray 0.5% Ferrous Sulphate + 0.1% Citric acid.
""",
    }
]
