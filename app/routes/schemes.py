from flask import Blueprint, render_template, request
from app.database.db import get_db

schemes_bp = Blueprint('schemes', __name__)

@schemes_bp.route('/')
def index():
    db = get_db()
    category = request.args.get('category', '').strip()

    query = "SELECT * FROM government_schemes WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY id ASC"
    schemes = db.execute(query, params).fetchall()

    categories = [row['category'] for row in db.execute("SELECT DISTINCT category FROM government_schemes ORDER BY category").fetchall()]

    return render_template(
        'schemes/index.html',
        schemes=schemes,
        categories=categories,
        selected_category=category
    )
