from flask import Blueprint, render_template, session, request, redirect, url_for, make_response
from app.database.db import get_db
from app.routes.helpers import get_current_farmer
from app.translations.languages import SUPPORTED_LANGUAGES

main_bp = Blueprint('main', __name__)

@main_bp.route('/set-language/<lang_code>')
def set_language(lang_code):
    """Update session language preference and set cookie for client-side translation."""
    if lang_code in SUPPORTED_LANGUAGES:
        session['lang'] = lang_code

    target = request.referrer or url_for('main.home')
    resp = make_response(redirect(target))
    # Also set Google Translate cookie for client-side full page translation
    if lang_code == 'en':
        resp.set_cookie('googtrans', '/en/en', path='/')
    else:
        resp.set_cookie('googtrans', f'/en/{lang_code}', path='/')
    return resp

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
