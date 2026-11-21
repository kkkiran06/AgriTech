from flask import Blueprint, render_template, session, request, redirect, url_for, make_response, flash
from app.database.db import get_db
from app.routes.helpers import get_current_farmer, login_required
from app.translations.languages import SUPPORTED_LANGUAGES

main_bp = Blueprint('main', __name__)

@main_bp.route('/set-language/<lang_code>')
def set_language(lang_code):
    """Update session language preference and set cookie for client-side translation."""
    if lang_code in SUPPORTED_LANGUAGES:
        session['lang'] = lang_code

    target = request.referrer or url_for('main.home')
    resp = make_response(redirect(target))
    # Also set Google Translate cookie for client-side full page translation
    if lang_code == 'en':
        resp.set_cookie('googtrans', '/en/en', path='/')
    else:
        resp.set_cookie('googtrans', f'/en/{lang_code}', path='/')
    return resp

@main_bp.route('/')
def home():
    """Landing homepage or dashboard redirect if already logged in."""
    farmer = get_current_farmer()
    return render_template('index.html', farmer=farmer)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Authenticated farmer personalized dashboard.
    Strictly displays the logged-in user's actual personal data and farming records.
    """
    db = get_db()
    farmer = get_current_farmer()

    # Individual user's private farming records
    user_records = db.execute(
        "SELECT * FROM farming_records WHERE farmer_id = ? ORDER BY id DESC",
        (farmer['id'],)
    ).fetchall()

    # Individual user's recent plant / soil diagnoses
    recent_diagnoses = db.execute(
        "SELECT * FROM diagnosis_history WHERE farmer_id = ? ORDER BY diagnosed_at DESC LIMIT 3",
        (farmer['id'],)
    ).fetchall()

    # Public reference data (kept separate from user personal data)
    commodities = db.execute("SELECT * FROM market_prices LIMIT 4").fetchall()
    crops = db.execute("SELECT * FROM crops LIMIT 4").fetchall()
    schemes = db.execute("SELECT * FROM government_schemes LIMIT 3").fetchall()

    return render_template(
        'dashboard.html',
        farmer=farmer,
        user_records=user_records,
        recent_diagnoses=recent_diagnoses,
        commodities=commodities,
        crops=crops,
        schemes=schemes
    )

@main_bp.route('/farming-records/add', methods=['POST'])
@login_required
def add_farming_record():
    """Add a new personal field/crop record for the authenticated farmer."""
    farmer = get_current_farmer()
    crop_name = request.form.get('crop_name', '').strip()
    area_acres = request.form.get('area_acres', '1.0').strip()
    sowing_date = request.form.get('sowing_date', '').strip()
    stage = request.form.get('stage', 'Sowing / Seedling').strip()
    expected_harvest = request.form.get('expected_harvest', '').strip()
    notes = request.form.get('notes', '').strip()

    if not crop_name:
        flash("Crop name is required to add a farming record.", "danger")
        return redirect(url_for('main.dashboard'))

    try:
        area_val = float(area_acres)
        if area_val <= 0:
            area_val = 1.0
    except ValueError:
        area_val = 1.0

    db = get_db()
    db.execute(
        """INSERT INTO farming_records 
           (farmer_id, crop_name, area_acres, sowing_date, stage, expected_harvest, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (farmer['id'], crop_name, area_val, sowing_date, stage, expected_harvest, notes)
    )
    db.commit()

    # Real-time sync to Supabase cloud
    try:
        from app.database.supabase_client import sync_farming_record_to_supabase
        rec_data = {
            'crop_name': crop_name,
            'area_acres': area_val,
            'sowing_date': sowing_date,
            'stage': stage,
            'expected_harvest': expected_harvest,
            'notes': notes
        }
        sync_farming_record_to_supabase(rec_data, farmer.get('mobile'))
    except Exception:
        pass

    flash(f"Farming record for '{crop_name}' added successfully to your private account!", "success")
    return redirect(url_for('main.dashboard'))

@main_bp.route('/farming-records/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_farming_record(record_id):
    """Delete a personal farming record strictly owned by the authenticated farmer."""
    farmer = get_current_farmer()
    db = get_db()
    # Fetch record to identify crop for cloud deletion before local delete
    rec = db.execute("SELECT crop_name FROM farming_records WHERE id = ? AND farmer_id = ?", (record_id, farmer['id'])).fetchone()
    # Enforce strict user ownership check
    cur = db.execute(
        "DELETE FROM farming_records WHERE id = ? AND farmer_id = ?",
        (record_id, farmer['id'])
    )
    db.commit()
    if cur.rowcount > 0:
        if rec and farmer.get('mobile'):
            try:
                from app.database.supabase_client import delete_farming_record_from_supabase
                delete_farming_record_from_supabase(rec['crop_name'], farmer['mobile'])
            except Exception:
                pass
        flash("Farming record deleted.", "info")
    else:
        flash("Record not found or unauthorized.", "danger")
    return redirect(url_for('main.dashboard'))
