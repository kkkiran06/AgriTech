"""
KrishiMitra Agricultural Expert Consultations Blueprint
Provides direct farmer-to-scientist advisory consultations and ticket threads.
Routes:
  GET  /consultations/           - View expert directory and farmer's consultation tickets
  POST /consultations/new        - Submit a new consultation inquiry
  GET  /consultations/<id>       - View consultation thread and conversation
  POST /consultations/<id>/message - Post reply message to consultation
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database.db import get_db
from app.routes.helpers import login_required, get_current_farmer

consultations_bp = Blueprint('consultations', __name__)

EXPERTS = [
    {
        "id": 1,
        "name": "Dr. S. Patil",
        "title": "Senior Agronomist & Crop Physiologist",
        "institution": "University of Agricultural Sciences (UAS), Dharwad",
        "specialization": "Cereals, Millets & Pulses Cultivation",
        "experience": "18+ Years",
        "availability": "Mon - Fri (10 AM - 4 PM)",
        "verified": True
    },
    {
        "id": 2,
        "name": "Dr. Ananya Sharma",
        "title": "Plant Pathologist & IPM Specialist",
        "institution": "Indian Agricultural Research Institute (ICAR-IARI)",
        "specialization": "Fungal & Viral Foliar Diseases, Bio-control",
        "experience": "14+ Years",
        "availability": "Mon - Sat (9 AM - 2 PM)",
        "verified": True
    },
    {
        "id": 3,
        "name": "Prof. R. Venkatesh",
        "title": "Soil Chemist & Micro-irrigation Expert",
        "institution": "College of Agriculture, Pune",
        "specialization": "Saline Soil Reclamation & Fertigation Protocols",
        "experience": "22+ Years",
        "availability": "Tue - Thu (11 AM - 5 PM)",
        "verified": True
    }
]

@consultations_bp.route('/')
@login_required
def index():
    farmer = get_current_farmer()
    db = get_db()
    consultations = db.execute(
        """SELECT * FROM consultations 
           WHERE farmer_id = ? 
           ORDER BY id DESC""",
        (farmer['id'],)
    ).fetchall()

    return render_template(
        'consultations/index.html',
        farmer=farmer,
        consultations=consultations,
        experts=EXPERTS
    )

@consultations_bp.route('/experts')
def api_experts():
    from flask import jsonify
    return jsonify({'experts': EXPERTS})

@consultations_bp.route('/new', methods=['POST'])
@login_required
def create_consultation():
    farmer = get_current_farmer()
    subject = request.form.get('subject', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', 'Crop Disease').strip()
    urgency = request.form.get('urgency', 'Medium').strip()
    expert_name = request.form.get('expert_name', 'Dr. S. Patil (Senior Agronomist)').strip()

    if not subject or len(subject) < 5:
        flash("Subject must be at least 5 characters.", "danger")
        return redirect(url_for('consultations.index'))
    if not description or len(description) < 10:
        flash("Please provide detailed description of the crop problem (at least 10 characters).", "danger")
        return redirect(url_for('consultations.index'))

    db = get_db()
    cur = db.execute(
        """INSERT INTO consultations 
           (farmer_id, expert_name, subject, description, category, urgency, status)
           VALUES (?, ?, ?, ?, ?, ?, 'Open')""",
        (farmer['id'], expert_name, subject, description, category, urgency)
    )
    consultation_id = cur.lastrowid

    # Add initial opening message
    db.execute(
        """INSERT INTO consultation_messages 
           (consultation_id, sender_role, sender_name, message)
           VALUES (?, 'farmer', ?, ?)""",
        (consultation_id, farmer['name'], description)
    )
    db.commit()

    flash(f"Consultation ticket #{consultation_id} created successfully! Assigned to {expert_name}.", "success")
    return redirect(url_for('consultations.detail', consultation_id=consultation_id))

@consultations_bp.route('/<int:consultation_id>')
@login_required
def detail(consultation_id):
    farmer = get_current_farmer()
    db = get_db()
    consultation = db.execute(
        "SELECT * FROM consultations WHERE id = ? AND farmer_id = ?",
        (consultation_id, farmer['id'])
    ).fetchone()

    if not consultation:
        flash("Consultation not found or unauthorized.", "danger")
        return redirect(url_for('consultations.index'))

    messages = db.execute(
        "SELECT * FROM consultation_messages WHERE consultation_id = ? ORDER BY id ASC",
        (consultation_id,)
    ).fetchall()

    return render_template(
        'consultations/detail.html',
        consultation=consultation,
        messages=messages,
        farmer=farmer
    )

@consultations_bp.route('/<int:consultation_id>/message', methods=['POST'])
@login_required
def add_message(consultation_id):
    farmer = get_current_farmer()
    message = request.form.get('message', '').strip()
    if not message:
        flash("Message cannot be empty.", "danger")
        return redirect(url_for('consultations.detail', consultation_id=consultation_id))

    db = get_db()
    # verify ownership
    c = db.execute("SELECT id, status, expert_name FROM consultations WHERE id = ? AND farmer_id = ?", (consultation_id, farmer['id'])).fetchone()
    if not c:
        flash("Unauthorized.", "danger")
        return redirect(url_for('consultations.index'))

    db.execute(
        """INSERT INTO consultation_messages (consultation_id, sender_role, sender_name, message)
           VALUES (?, 'farmer', ?, ?)""",
        (consultation_id, farmer['name'], message)
    )
    db.commit()
    flash("Message sent to expert.", "success")
    return redirect(url_for('consultations.detail', consultation_id=consultation_id))
