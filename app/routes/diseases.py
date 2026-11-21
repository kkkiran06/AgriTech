from flask import Blueprint, render_template, request
from app.database.db import get_db

diseases_bp = Blueprint('diseases', __name__)

@diseases_bp.route('/')
def index():
    db = get_db()
    crop_filter = request.args.get('crop', '').strip()
    type_filter = request.args.get('type', '').strip()

    query = "SELECT * FROM diseases_pests WHERE 1=1"
    params = []

    if crop_filter:
        query += " AND affected_crops LIKE ?"
        params.append(f"%{crop_filter}%")
    if type_filter:
        query += " AND type = ?"
        params.append(type_filter)

    query += " ORDER BY severity DESC, name ASC"
    items = db.execute(query, params).fetchall()

    return render_template(
        'diseases/index.html',
        items=items,
        selected_crop=crop_filter,
        selected_type=type_filter
    )

@diseases_bp.route('/<int:item_id>')
def detail(item_id):
    db = get_db()
    item = db.execute("SELECT * FROM diseases_pests WHERE id = ?", (item_id,)).fetchone()
    if not item:
        return "Disease/Pest record not found", 404
    return render_template('diseases/detail.html', item=item)
