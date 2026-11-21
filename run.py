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
    print("\n" + "=" * 65)
    print("🌾  KrishiMitra - Smart Agriculture Web Platform  🌾")
    print("=" * 65)

    if db_url and ('postgresql://' in db_url or 'postgres://' in db_url):
        print("☁️ Active Database: Supabase PostgreSQL (ojofmguhhdcvfnwgrzgd)")
        print("   All new farmer registrations will save directly to Supabase cloud.")
    else:
        db_path = app.config.get('DATABASE', 'krishimitra.db')
        if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
            print("🌱 SQLite database not found. Auto-initializing and seeding...")
            seed_database(db_path)
            print("✅ SQLite database initialized successfully!")
        else:
            print(f"📁 Active Database: Local SQLite3 ({db_path})")
            print("   All new farmer registrations will save to krishimitra.db.")
            print("   💡 If viewing in VS Code: click the 🔄 Refresh button to see new rows.")

    print("✓ Flask Server Starting...")
    print("✓ Local Access URL: http://127.0.0.1:5000/")
    print("✓ Test Farmer Login: Mobile: 9876543210 (Register anytime)")
    print("✓ Press CTRL+C to stop the server.")
    print("=" * 65 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
