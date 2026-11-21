from flask import Blueprint, render_template, request
from app.database.db import get_db

crops_bp = Blueprint('crops', __name__)

@crops_bp.route('/')
def index():
    db = get_db()
    season = request.args.get('season', '').strip()
    category = request.args.get('category', '').strip()

    query = "SELECT * FROM crops WHERE 1=1"
    params = []

    if season:
        query += " AND season LIKE ?"
        params.append(f"%{season}%")
    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY name ASC"
    crops = db.execute(query, params).fetchall()

    return render_template('crops/index.html', crops=crops, selected_season=season, selected_category=category)

@crops_bp.route('/<int:crop_id>')
def detail(crop_id):
    db = get_db()
    crop = db.execute("SELECT * FROM crops WHERE id = ?", (crop_id,)).fetchone()
    if not crop:
        return "Crop not found", 404
    return render_template('crops/detail.html', crop=crop)
