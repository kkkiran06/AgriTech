"""
KrishiMitra Multi-Parcel Farm Management Blueprint
Routes:
  GET  /farms/           - List authenticated farmer's land parcels
  POST /farms/add        - Register a new farm parcel
  POST /farms/delete/<id>- Remove a farm parcel
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database.db import get_db
from app.routes.helpers import login_required, get_current_farmer

farms_bp = Blueprint('farms', __name__)

@farms_bp.route('/')
@login_required
def index():
    farmer = get_current_farmer()
    db = get_db()
    farms = db.execute(
        "SELECT * FROM farms WHERE farmer_id = ? ORDER BY id DESC",
        (farmer['id'],)
    ).fetchall()
    return render_template('farms/index.html', farms=farms, farmer=farmer)

@farms_bp.route('/add', methods=['POST'])
@login_required
def add_farm():
    farmer = get_current_farmer()
    name = request.form.get('name', '').strip()
    district = request.form.get('district', farmer.get('district', 'Pune')).strip()
    taluk = request.form.get('taluk', '').strip()
    village = request.form.get('village', '').strip()
    survey_number = request.form.get('survey_number', '').strip()
    total_area = request.form.get('total_area', '1.0').strip()
    soil_type = request.form.get('soil_type', 'Red Sandy Loam').strip()
    water_source = request.form.get('water_source', 'Borewell').strip()
    irrigation_type = request.form.get('irrigation_type', 'Drip Irrigation').strip()
    ownership_type = request.form.get('ownership_type', 'Owned').strip()
    notes = request.form.get('notes', '').strip()

    lat = request.form.get('latitude', '')
    lng = request.form.get('longitude', '')
    try:
        area_val = float(total_area)
        lat_val = float(lat) if lat else None
        lng_val = float(lng) if lng else None
    except ValueError:
        area_val = 1.0
        lat_val = None
        lng_val = None

    if not name:
        flash("Farm parcel name is required.", "danger")
        return redirect(url_for('farms.index'))

    db = get_db()
    db.execute(
        """INSERT INTO farms 
           (farmer_id, name, state, district, taluk, village, survey_number, latitude, longitude,
            total_area, soil_type, water_source, irrigation_type, ownership_type, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (farmer['id'], name, farmer.get('state', 'Karnataka'), district, taluk, village, survey_number,
         lat_val, lng_val, area_val, soil_type, water_source, irrigation_type, ownership_type, notes)
    )
    db.commit()
    flash(f"Farm parcel '{name}' registered successfully!", "success")
    return redirect(url_for('farms.index'))

@farms_bp.route('/delete/<int:farm_id>', methods=['POST'])
@login_required
def delete_farm(farm_id):
    farmer = get_current_farmer()
    db = get_db()
    cur = db.execute("DELETE FROM farms WHERE id = ? AND farmer_id = ?", (farm_id, farmer['id']))
    db.commit()
    if cur.rowcount > 0:
        flash("Farm parcel removed.", "info")
    else:
        flash("Farm parcel not found or unauthorized.", "danger")
    return redirect(url_for('farms.index'))
