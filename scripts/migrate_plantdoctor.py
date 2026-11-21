import sqlite3
conn = sqlite3.connect('krishimitra.db')
conn.execute("""CREATE TABLE IF NOT EXISTS diagnosis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    disease_name TEXT NOT NULL,
    plant_name TEXT NOT NULL,
    confidence_score REAL NOT NULL DEFAULT 0.0,
    severity TEXT NOT NULL DEFAULT 'Unknown',
    ai_mode TEXT NOT NULL DEFAULT 'demo',
    symptoms_summary TEXT,
    treatment_summary TEXT,
    image_b64 TEXT,
    diagnosed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
)""")
conn.commit()
conn.close()
print("diagnosis_history table created OK")
