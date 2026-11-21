"""
PlantDoctor & Soil AI Scanner Blueprint
Routes: /plantdoctor/  (upload & camera scanner page with Leaf / Soil switcher)
        /plantdoctor/diagnose  (POST: run Gemini Multimodal Vision AI prediction)
        /plantdoctor/history   (saved diagnoses for logged-in farmers)
        /plantdoctor/history/delete/<id>  (POST: delete a saved record)
"""

import os
import uuid
import base64
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session, jsonify, current_app
)
from app.database.db import get_db
from app.routes.helpers import get_current_farmer
from app.ml.gemini_vision import analyze_crop_or_soil, get_gemini_api_key

plantdoctor_bp = Blueprint('plantdoctor', __name__)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
MAX_FILE_SIZE_MB = 10


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─────────────────────────────────────────────
# GET /plantdoctor/  — Upload & Camera page
# ─────────────────────────────────────────────
@plantdoctor_bp.route('/')
def index():
    farmer = get_current_farmer()
    # Get recent history count for logged-in farmer
    history_count = 0
    if farmer:
        db = get_db()
        row = db.execute(
            'SELECT COUNT(*) as cnt FROM diagnosis_history WHERE farmer_id = ?',
            (farmer['id'],)
        ).fetchone()
        history_count = row['cnt'] if row else 0

    # Check initial scan target (from query param: ?scan_type=soil or leaf)
    selected_scan_type = request.args.get('scan_type', request.args.get('target', 'auto'))
    if selected_scan_type not in ('leaf', 'soil', 'auto'):
        selected_scan_type = 'auto'

    # Check Gemini API status
    has_gemini = bool(get_gemini_api_key())
    ai_mode = 'gemini_vision' if has_gemini else 'demo'

    return render_template('plantdoctor/index.html',
                           farmer=farmer,
                           ai_mode=ai_mode,
                           has_gemini=has_gemini,
                           selected_scan_type=selected_scan_type,
                           history_count=history_count)


# ─────────────────────────────────────────────
# POST /plantdoctor/diagnose  — Run AI prediction
# ─────────────────────────────────────────────
@plantdoctor_bp.route('/diagnose', methods=['POST'])
def diagnose():
    farmer = get_current_farmer()

    image_bytes = None
    image_b64 = None
    source = request.form.get('source', 'upload')  # 'upload' or 'camera'
    scan_type = request.form.get('scan_type', 'auto')
    if scan_type not in ('leaf', 'soil', 'auto'):
        scan_type = 'auto'

    # ── 1. Collect image bytes ────────────────────────────────
    if source == 'camera':
        data_url = request.form.get('camera_image_data', '')
        if not data_url or ',' not in data_url:
            flash('No camera image received. Please try again.', 'warning')
            return redirect(url_for('plantdoctor.index', scan_type=scan_type))
        header, encoded = data_url.split(',', 1)
        image_bytes = base64.b64decode(encoded)
        image_b64 = encoded

    else:
        # File upload
        if 'plant_image' not in request.files:
            flash('Please select an image file to upload.', 'warning')
            return redirect(url_for('plantdoctor.index', scan_type=scan_type))

        file = request.files['plant_image']
        if not file or file.filename == '':
            flash('No file selected. Please choose a plant leaf or soil image.', 'warning')
            return redirect(url_for('plantdoctor.index', scan_type=scan_type))

        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a JPG, PNG, or WEBP image.', 'danger')
            return redirect(url_for('plantdoctor.index', scan_type=scan_type))

        image_bytes = file.read()
        if len(image_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
            flash(f'Image too large. Maximum size is {MAX_FILE_SIZE_MB} MB.', 'danger')
            return redirect(url_for('plantdoctor.index', scan_type=scan_type))

        import base64 as _b64
        image_b64 = _b64.b64encode(image_bytes).decode('utf-8')

    # ── 2. Run Gemini Multimodal Vision Prediction ────────────
    lang = session.get('lang', 'en')
    try:
        analysis = analyze_crop_or_soil(image_bytes, target_hint=scan_type, language=lang)
    except Exception as exc:
        current_app.logger.error(f"Gemini Vision prediction exception: {exc}")
        analysis = None

    if not analysis:
        flash('AI analysis error. Please try again with a clearer image.', 'danger')
        return redirect(url_for('plantdoctor.index', scan_type=scan_type))

    # Standardize primary structure for template & backwards compatibility
    primary = {
        'display_name': analysis['health_status'],
        'plant': analysis['subject_name'],
        'confidence': analysis['confidence'],
        'severity': analysis['severity'],
        'symptoms': analysis['visual_analysis'],
        'organic_treatment': analysis['organic_treatment'],
        'chemical_treatment': analysis['chemical_treatment'],
        'npk_advice': analysis.get('npk_advice', ''),
        'prevention': analysis['prevention_tips'],
        'suitable_crops': analysis.get('suitable_crops', ''),
        'emoji': analysis['emoji'],
    }

    predictions = [
        {
            'name': analysis['health_status'],
            'confidence': analysis['confidence'],
            'display_name': analysis['health_status'],
            'plant': analysis['subject_name'],
            'severity': analysis['severity'],
            'is_healthy': 'healthy' in analysis['health_status'].lower() or 'healthy' in analysis['severity'].lower()
        }
    ]

    ai_mode = analysis.get('mode', 'gemini_ai')

    # ── 3. Auto-save to history if farmer is logged in ────────
    record_id = None
    if farmer:
        try:
            db = get_db()
            tag = f"[{analysis['scan_type'].upper()}]"
            cur = db.execute(
                '''INSERT INTO diagnosis_history
                   (farmer_id, disease_name, plant_name, confidence_score,
                    severity, ai_mode, symptoms_summary, treatment_summary, image_b64)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    farmer['id'],
                    analysis['health_status'],
                    f"{tag} {analysis['subject_name']}",
                    analysis['confidence'],
                    analysis['severity'],
                    analysis['ai_engine'],
                    analysis['visual_analysis'][:300],
                    f"Organic: {analysis['organic_treatment'][:140]} | Chemical/NPK: {analysis['chemical_treatment'][:140]}",
                    image_b64[:50000] if image_b64 else None,
                )
            )
            db.commit()
            record_id = cur.lastrowid

            # Real-time sync diagnosis to Supabase
            try:
                from app.database.supabase_client import sync_diagnosis_to_supabase
                diag_data = {
                    'disease_name': analysis['health_status'],
                    'plant_name': f"{tag} {analysis['subject_name']}",
                    'confidence_score': analysis['confidence'],
                    'severity': analysis['severity'],
                    'ai_mode': analysis['ai_engine'],
                    'symptoms_summary': analysis['visual_analysis'][:300],
                    'treatment_summary': f"Organic: {analysis['organic_treatment'][:140]} | Chemical/NPK: {analysis['chemical_treatment'][:140]}"
                }
                sync_diagnosis_to_supabase(diag_data, farmer.get('mobile'))
            except Exception:
                pass
        except Exception as exc:
            current_app.logger.warning(f"PlantDoctor history save error: {exc}")

    return render_template(
        'plantdoctor/result.html',
        farmer=farmer,
        analysis=analysis,
        primary=primary,
        predictions=predictions,
        image_b64=image_b64,
        ai_mode=ai_mode,
        record_id=record_id,
        diagnosed_at=datetime.now().strftime('%d %b %Y, %I:%M %p'),
    )


# ─────────────────────────────────────────────
# GET /plantdoctor/history  — Saved diagnosis history
# ─────────────────────────────────────────────
@plantdoctor_bp.route('/history')
def history():
    farmer = get_current_farmer()
    if not farmer:
        flash('Please login to view your diagnosis history.', 'warning')
        return redirect(url_for('auth.login'))

    db = get_db()
    records = db.execute(
        '''SELECT * FROM diagnosis_history
           WHERE farmer_id = ?
           ORDER BY diagnosed_at DESC
           LIMIT 50''',
        (farmer['id'],)
    ).fetchall()

    return render_template('plantdoctor/history.html',
                           farmer=farmer,
                           records=records)


# ─────────────────────────────────────────────
# POST /plantdoctor/history/delete/<id>
# ─────────────────────────────────────────────
@plantdoctor_bp.route('/history/delete/<int:record_id>', methods=['POST'])
def delete_history(record_id):
    farmer = get_current_farmer()
    if not farmer:
        flash('Please login to manage your history.', 'warning')
        return redirect(url_for('auth.login'))

    db = get_db()
    db.execute(
        'DELETE FROM diagnosis_history WHERE id = ? AND farmer_id = ?',
        (record_id, farmer['id'])
    )
    db.commit()
    flash('Diagnosis record deleted.', 'success')
    return redirect(url_for('plantdoctor.history'))
