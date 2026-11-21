"""
KrishiMitra - Smart Agriculture Platform
Root Application Entry Point
"""
import os
import sys
from app import create_app
from app.database.seed_data import seed_database

app = create_app()

def main():
    db_url = os.environ.get('DATABASE_URL')
    if db_url and ('postgresql://' in db_url or 'postgres://' in db_url):
        print("☁️ Connected to Cloud Database: Supabase PostgreSQL (ojofmguhhdcvfnwgrzgd)")
    else:
        db_path = app.config.get('DATABASE', 'krishimitra.db')
        # If database file does not exist or has 0 size, auto-seed
        if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
            print("🌱 SQLite database not found. Auto-initializing and seeding KrishiMitra database...")
            seed_database(db_path)
            print("✅ SQLite database initialized successfully!")
        else:
            print(f"📁 Local Database: SQLite3 ({db_path})")

    print("\n" + "=" * 60)
    print("🌾  KrishiMitra - Smart Agriculture Web Platform  🌾")
    print("=" * 60)
    print("✓ Flask Server Starting...")
    print("✓ Local Access URL: http://127.0.0.1:5000/")
    print("✓ Test Farmer Login: Mobile: 9876543210 (Register anytime)")
    print("✓ Press CTRL+C to stop the server.")
    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
