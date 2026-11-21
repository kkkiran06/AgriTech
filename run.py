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

    supabase_url = os.environ.get('SUPABASE_URL')
    if supabase_url:
        print("☁️ Real-Time Supabase Sync: ACTIVE (ojofmguhhdcvfnwgrzgd)")
        print("   Every newly registered farmer immediately syncs to Supabase cloud table!")
    else:
        print(f"📁 Active Database: Local SQLite3 ({app.config.get('DATABASE', 'krishimitra.db')})")

    print("✓ Flask Server Starting...")
    print("✓ Local Access URL: http://127.0.0.1:5000/")
    print("✓ Press CTRL+C to stop the server.")
    print("=" * 65 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
