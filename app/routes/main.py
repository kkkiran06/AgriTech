from flask import Blueprint, render_template, session
from app.database.db import get_db
from app.routes.helpers import get_current_farmer

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Landing homepage or dashboard redirect."""
    farmer = get_current_farmer()
    return render_template('index.html', farmer=farmer)

@main_bp.route('/dashboard')
def dashboard():
    """Farmer home dashboard."""
    db = get_db()
    farmer = get_current_farmer()
    
    # Recent commodities preview
    commodities = db.execute("SELECT * FROM market_prices LIMIT 4").fetchall()
    # Featured crops
    crops = db.execute("SELECT * FROM crops LIMIT 4").fetchall()
    # Quick schemes
    schemes = db.execute("SELECT * FROM government_schemes LIMIT 3").fetchall()

    return render_template(
        'dashboard.html',
        farmer=farmer,
        commodities=commodities,
        crops=crops,
        schemes=schemes
    )
