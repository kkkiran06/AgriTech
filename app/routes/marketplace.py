"""
KrishiMitra Direct Farm-to-Buyer Produce Marketplace Blueprint
Routes:
  GET  /marketplace/            - Browse produce listings & view personal listings
  POST /marketplace/listings/add - Post farm produce for sale
  POST /marketplace/orders/add   - Place purchase order / enquiry on a listing
  POST /marketplace/listings/delete/<id> - Delete listing
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.database.db import get_db
from app.routes.helpers import login_required, get_current_farmer

marketplace_bp = Blueprint('marketplace', __name__)

@marketplace_bp.route('/api/listings')
def api_listings():
    db = get_db()
    rows = db.execute(
        """SELECT p.*, f.name as farmer_name, f.mobile as farmer_mobile
           FROM produce_listings p
           JOIN farmers f ON p.farmer_id = f.id
           ORDER BY p.id DESC"""
    ).fetchall()
    return jsonify({'listings': [dict(r) for r in rows]})

@marketplace_bp.route('/')
def index():
    farmer = get_current_farmer()
    db = get_db()

    # All active produce listings
    listings = db.execute(
        """SELECT p.*, f.name as farmer_name, f.mobile as farmer_mobile,
                  (SELECT COUNT(*) FROM produce_orders o WHERE o.listing_id = p.id) as order_count
           FROM produce_listings p
           JOIN farmers f ON p.farmer_id = f.id
           ORDER BY p.id DESC"""
    ).fetchall()

    # If farmer is logged in, fetch personal listings and received orders
    my_listings = []
    my_orders = []
    if farmer:
        my_listings = [l for l in listings if l['farmer_id'] == farmer['id']]
        my_orders = db.execute(
            """SELECT o.*, p.commodity, p.variety 
               FROM produce_orders o
               JOIN produce_listings p ON o.listing_id = p.id
               WHERE p.farmer_id = ?
               ORDER BY o.id DESC""",
            (farmer['id'],)
        ).fetchall()

    return render_template(
        'marketplace/index.html',
        farmer=farmer,
        listings=listings,
        my_listings=my_listings,
        my_orders=my_orders,
        today_date=datetime.now().strftime('%Y-%m-%d')
    )

@marketplace_bp.route('/listings/add', methods=['POST'])
@login_required
def add_listing():
    farmer = get_current_farmer()
    commodity = request.form.get('commodity', '').strip()
    variety = request.form.get('variety', '').strip()
    qty_str = request.form.get('quantity_quintal', '1.0').strip()
    price_str = request.form.get('expected_price', '0').strip()
    district = request.form.get('district', farmer.get('district', 'Pune')).strip()
    state = request.form.get('state', farmer.get('state', 'Maharashtra')).strip()
    harvest_date = request.form.get('harvest_date', datetime.now().strftime('%Y-%m-%d')).strip()
    quality_grade = request.form.get('quality_grade', 'Grade A').strip()
    is_organic = 1 if request.form.get('is_organic') else 0

    if not commodity:
        flash("Commodity name is required.", "danger")
        return redirect(url_for('marketplace.index'))

    try:
        qty = float(qty_str)
        price = float(price_str)
        if qty <= 0 or price <= 0:
            flash("Quantity and price must be greater than zero.", "danger")
            return redirect(url_for('marketplace.index'))
    except ValueError:
        flash("Invalid quantity or price value.", "danger")
        return redirect(url_for('marketplace.index'))

    db = get_db()
    db.execute(
        """INSERT INTO produce_listings 
           (farmer_id, commodity, variety, quantity_quintal, expected_price, district, state, harvest_date, quality_grade, is_organic)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (farmer['id'], commodity, variety, qty, price, district, state, harvest_date, quality_grade, is_organic)
    )
    db.commit()
    flash(f"Produce listing for '{commodity}' published to the Marketplace!", "success")
    return redirect(url_for('marketplace.index'))

@marketplace_bp.route('/orders/add', methods=['POST'])
def place_order():
    listing_id = request.form.get('listing_id')
    buyer_name = request.form.get('buyer_name', '').strip()
    buyer_contact = request.form.get('buyer_contact', '').strip()
    qty_str = request.form.get('quantity_quintal', '1.0').strip()
    price_str = request.form.get('offered_price', '0').strip()
    message = request.form.get('message', '').strip()

    if not buyer_name or not buyer_contact:
        flash("Buyer name and contact number are required.", "danger")
        return redirect(url_for('marketplace.index'))

    try:
        qty = float(qty_str)
        price = float(price_str)
        if qty <= 0 or price <= 0:
            flash("Order quantity and offered price must be positive.", "danger")
            return redirect(url_for('marketplace.index'))
    except ValueError:
        flash("Invalid order values.", "danger")
        return redirect(url_for('marketplace.index'))

    db = get_db()
    db.execute(
        """INSERT INTO produce_orders (listing_id, buyer_name, buyer_contact, quantity_quintal, offered_price, message)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (listing_id, buyer_name, buyer_contact, qty, price, message)
    )
    db.commit()
    flash("Purchase enquiry submitted successfully to the farmer!", "success")
    return redirect(url_for('marketplace.index'))

@marketplace_bp.route('/listings/delete/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    farmer = get_current_farmer()
    db = get_db()
    cur = db.execute("DELETE FROM produce_listings WHERE id = ? AND farmer_id = ?", (listing_id, farmer['id']))
    db.commit()
    if cur.rowcount > 0:
        flash("Produce listing removed from Marketplace.", "info")
    else:
        flash("Listing not found or unauthorized.", "danger")
    return redirect(url_for('marketplace.index'))
