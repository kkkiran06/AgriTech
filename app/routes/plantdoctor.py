"""
PlantDoctor AI Blueprint
Routes: /plantdoctor/  (upload page)
        /plantdoctor/diagnose  (POST: run AI prediction)
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

    # Check which mode the AI is running in
    try:
        from app.ml.plant_disease_model import get_predictor
        predictor = get_predictor()
        ai_mode = predictor.mode
    except Exception:
        ai_mode = 'demo'

    return render_template('plantdoctor/index.html',
                           farmer=farmer,
                           ai_mode=ai_mode,
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

    # ── 1. Collect image bytes ────────────────────────────────
    if source == 'camera':
        # Base64 data URL from camera capture
        data_url = request.form.get('camera_image_data', '')
        if not data_url or ',' not in data_url:
            flash('No camera image received. Please try again.', 'warning')
            return redirect(url_for('plantdoctor.index'))
        header, encoded = data_url.split(',', 1)
        image_bytes = base64.b64decode(encoded)
        image_b64 = encoded  # Store for display

    else:
        # File upload
        if 'plant_image' not in request.files:
            flash('Please select an image file to upload.', 'warning')
            return redirect(url_for('plantdoctor.index'))

        file = request.files['plant_image']
        if not file or file.filename == '':
            flash('No file selected. Please choose a plant leaf image.', 'warning')
            return redirect(url_for('plantdoctor.index'))

        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a JPG, PNG, or WEBP image.', 'danger')
            return redirect(url_for('plantdoctor.index'))

        image_bytes = file.read()
        if len(image_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
            flash(f'Image too large. Maximum size is {MAX_FILE_SIZE_MB} MB.', 'danger')
            return redirect(url_for('plantdoctor.index'))

        # Convert to base64 for display in results page
        import base64 as _b64
        image_b64 = _b64.b64encode(image_bytes).decode('utf-8')

    # ── 2. Run AI prediction ──────────────────────────────────
    try:
        from app.ml.plant_disease_model import get_predictor
        predictor = get_predictor()
        result = predictor.predict(image_bytes)
    except Exception as exc:
        current_app.logger.error(f"PlantDoctor prediction error: {exc}")
        flash('AI engine error. Please try again with a clearer image.', 'danger')
        return redirect(url_for('plantdoctor.index'))

    primary = result['primary']
    predictions = result['predictions']
    ai_mode = result['mode']

    # ── 3. Auto-save to history if farmer is logged in ────────
    record_id = None
    if farmer:
        try:
            db = get_db()
            cur = db.execute(
                '''INSERT INTO diagnosis_history
                   (farmer_id, disease_name, plant_name, confidence_score,
                    severity, ai_mode, symptoms_summary, treatment_summary, image_b64)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    farmer['id'],
                    primary['display_name'],
                    primary['plant'],
                    primary['confidence'],
                    primary['severity'],
                    ai_mode,
                    primary['symptoms'][:300],
                    primary['chemical_treatment'][:300],
                    image_b64[:50000] if image_b64 else None,  # Store compressed preview
                )
            )
            db.commit()
            record_id = cur.lastrowid
        except Exception as exc:
            current_app.logger.warning(f"PlantDoctor history save error: {exc}")

    return render_template(
        'plantdoctor/result.html',
        farmer=farmer,
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
