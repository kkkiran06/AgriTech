"""
KrishiMitra Seasonal Crop Lifecycle Milestones Blueprint
Routes:
  GET  /progress/          - View milestones checklist across active crops
  POST /progress/add       - Initialize milestones for a new crop
  POST /progress/toggle/<id> - Check off or reopen a milestone stage
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database.db import get_db
from app.routes.helpers import login_required, get_current_farmer

progress_bp = Blueprint('progress', __name__)

DEFAULT_STAGES = [
    "1. Land Preparation & Basal Nutrition (DAP/FYM)",
    "2. Seed Selection & Bio-Treatment (Trichoderma)",
    "3. Sowing & Line Spacing Protocol",
    "4. Early Vegetative Growth & First Weeding",
    "5. First Top-Dressing Fertigation (Urea/Potash)",
    "6. Flowering Onset & Pest Monitoring",
    "7. Pod / Grain Filling & Foliar Nutrient Spray",
    "8. Maturity Assessment & Harvesting",
    "9. Post-Harvest Cleaning, Grading & Mandi Sale"
]

@progress_bp.route('/')
@login_required
def index():
    farmer = get_current_farmer()
    db = get_db()

    # Get active farming records for crop choices
    crops = db.execute("SELECT DISTINCT crop_name FROM farming_records WHERE farmer_id = ?", (farmer['id'],)).fetchall()
    crop_names = [c['crop_name'] for c in crops]

    # Get all milestones
    milestones = db.execute(
        "SELECT * FROM farmer_milestones WHERE farmer_id = ? ORDER BY id ASC",
        (farmer['id'],)
    ).fetchall()

    # Group milestones by crop_name
    grouped = {}
    for m in milestones:
        c = m['crop_name']
        if c not in grouped:
            grouped[c] = []
        grouped[c].append(m)

    return render_template(
        'progress/index.html',
        farmer=farmer,
        crop_names=crop_names,
        grouped_milestones=grouped,
        default_stages=DEFAULT_STAGES
    )

@progress_bp.route('/add', methods=['POST'])
@login_required
def add_crop_milestones():
    farmer = get_current_farmer()
    crop_name = request.form.get('crop_name', '').strip()
    season = request.form.get('season', 'Kharif 2026').strip()

    if not crop_name:
        flash("Please specify a crop name to track milestones.", "danger")
        return redirect(url_for('progress.index'))

    db = get_db()
    # Check if already initialized for this crop
    existing = db.execute(
        "SELECT id FROM farmer_milestones WHERE farmer_id = ? AND crop_name = ?",
        (farmer['id'], crop_name)
    ).fetchone()
    if existing:
        flash(f"Milestones for '{crop_name}' are already being tracked.", "warning")
        return redirect(url_for('progress.index'))

    for stage in DEFAULT_STAGES:
        db.execute(
            """INSERT INTO farmer_milestones (farmer_id, crop_name, season, stage_name, completed)
               VALUES (?, ?, ?, ?, 0)""",
            (farmer['id'], crop_name, season, stage)
        )
    db.commit()
    flash(f"Crop lifecycle milestone tracker initialized for '{crop_name}'!", "success")
    return redirect(url_for('progress.index'))

@progress_bp.route('/toggle/<int:milestone_id>', methods=['POST'])
@login_required
def toggle_milestone(milestone_id):
    farmer = get_current_farmer()
    db = get_db()
    m = db.execute("SELECT * FROM farmer_milestones WHERE id = ? AND farmer_id = ?", (milestone_id, farmer['id'])).fetchone()
    if not m:
        flash("Milestone not found.", "danger")
        return redirect(url_for('progress.index'))

    new_val = 0 if m['completed'] else 1
    completed_date = datetime.now().strftime('%Y-%m-%d') if new_val else None

    db.execute(
        "UPDATE farmer_milestones SET completed = ?, completed_date = ? WHERE id = ?",
        (new_val, completed_date, milestone_id)
    )
    db.commit()
    flash(f"Updated milestone: {m['stage_name']}", "info")
    return redirect(url_for('progress.index'))
