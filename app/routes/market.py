from flask import Blueprint, render_template, request
from app.database.db import get_db

market_bp = Blueprint('market', __name__)

@market_bp.route('/')
def index():
    db = get_db()
    commodity = request.args.get('commodity', '').strip()
    state = request.args.get('state', '').strip()

    query = "SELECT * FROM market_prices WHERE 1=1"
    params = []

    if commodity:
        query += " AND commodity LIKE ?"
        params.append(f"%{commodity}%")
    if state:
        query += " AND state = ?"
        params.append(state)

    query += " ORDER BY commodity ASC, modal_price DESC"
    prices = db.execute(query, params).fetchall()

    commodities = [row['commodity'] for row in db.execute("SELECT DISTINCT commodity FROM market_prices ORDER BY commodity").fetchall()]
    states = [row['state'] for row in db.execute("SELECT DISTINCT state FROM market_prices ORDER BY state").fetchall()]

    return render_template(
        'market/index.html',
        prices=prices,
        commodities=commodities,
        states=states,
        selected_commodity=commodity,
        selected_state=state
    )
