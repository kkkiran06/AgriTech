import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db import get_db
from app.routes.helpers import login_required, get_current_farmer

auth_bp = Blueprint('auth', __name__)

INDIAN_STATES_DISTRICTS = {
    "Maharashtra": ["Pune", "Nashik", "Nagpur", "Gondia", "Kolhapur", "Solapur", "Aurangabad", "Amravati"],
    "Punjab": ["Ludhiana", "Amritsar", "Patiala", "Jalandhar", "Bathinda", "Khanna"],
    "Haryana": ["Karnal", "Hisar", "Ambala", "Kurukshetra", "Sirsa", "Rohtak"],
    "Uttar Pradesh": ["Agra", "Varanasi", "Lucknow", "Kanpur", "Meerut", "Prayagraj"],
    "Madhya Pradesh": ["Indore", "Bhopal", "Ujjain", "Jabalpur", "Gwalior", "Chhindwara"],
    "Rajasthan": ["Kota", "Bikaner", "Jaipur", "Jodhpur", "Udaipur", "Sri Ganganagar"],
    "Karnataka": ["Davanagere", "Kolar", "Belagavi", "Mysuru", "Hubballi-Dharwad", "Ballari"],
    "Gujarat": ["Rajkot", "Surat", "Ahmedabad", "Vadodara", "Junagadh", "Mehsana"]
}

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new individual farmer account."""
    if session.get('farmer_id'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        state = request.form.get('state', 'Maharashtra').strip()
        district = request.form.get('district', '').strip()
        farm_size = request.form.get('farm_size', '1.0').strip()
        primary_crops = request.form.get('primary_crops', '').strip()

        errors = []
        if not name or len(name) < 2:
            errors.append("Full Name is required (minimum 2 characters).")
        if not email or not EMAIL_REGEX.match(email):
            errors.append("Please provide a valid email address (e.g., farmer@example.com).")
        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            errors.append("Please enter a valid 10-digit mobile number.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if not district:
            errors.append("District is required.")

        try:
            farm_size_val = float(farm_size)
            if farm_size_val <= 0:
                errors.append("Farm size must be greater than zero.")
        except ValueError:
            farm_size_val = 1.0
            errors.append("Farm size must be a valid number.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', states=INDIAN_STATES_DISTRICTS,
                                   name=name, email=email, mobile=mobile,
                                   farm_size=farm_size, primary_crops=primary_crops)

        db = get_db()
        # Check duplicate mobile
        existing_mobile = db.execute("SELECT id FROM farmers WHERE mobile = ?", (mobile,)).fetchone()
        if existing_mobile:
            flash("This mobile number is already registered. Please log in.", 'warning')
            return redirect(url_for('auth.login'))

        # Check duplicate email
        existing_email = db.execute("SELECT id FROM farmers WHERE LOWER(email) = ?", (email,)).fetchone()
        if existing_email:
            flash("This email address is already registered. Please log in.", 'warning')
            return redirect(url_for('auth.login'))

        password_hash = generate_password_hash(password)
        db.execute(
            """INSERT INTO farmers (name, email, mobile, password_hash, state, district, farm_size, primary_crops)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, email, mobile, password_hash, state, district, farm_size_val, primary_crops)
        )
        db.commit()

        # Retrieve new farmer record for real-time cloud backup
        new_farmer = db.execute("SELECT * FROM farmers WHERE mobile = ?", (mobile,)).fetchone()
        try:
            from app.database.supabase_client import sync_farmer_to_supabase
            sync_farmer_to_supabase(new_farmer)
        except Exception:
            pass

        # Clear any existing session; do NOT auto-login as per requirements
        session.clear()
        flash(f"Account created successfully for {name}! Please log in with your credentials to access your dashboard.", 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', states=INDIAN_STATES_DISTRICTS)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate registered farmer using mobile or email."""
    if session.get('farmer_id'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('login_identifier', request.form.get('mobile', '')).strip()
        password = request.form.get('password', '')

        if not identifier or not password:
            flash("Please enter your mobile number or email address and password.", 'danger')
            return render_template('auth/login.html', identifier=identifier)

        db = get_db()
        # Search by mobile number or email address
        farmer = db.execute(
            "SELECT * FROM farmers WHERE mobile = ? OR LOWER(email) = LOWER(?)",
            (identifier, identifier)
        ).fetchone()

        if farmer is None or not check_password_hash(farmer['password_hash'], password):
            flash("Invalid credentials. Please enter a valid registered mobile/email and password.", 'danger')
            return render_template('auth/login.html', identifier=identifier)

        # Set clean, secure authenticated session
        session.clear()
        session['farmer_id'] = farmer['id']
        session['farmer_name'] = farmer['name']
        session['farmer_email'] = farmer['email']
        session['district'] = farmer['district']
        session['state'] = farmer['state']

        flash(f"Welcome back, {farmer['name']}!", 'success')
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('main.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Clear session and log out farmer."""
    session.clear()
    flash("You have been securely logged out. Have a productive day!", 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and update authenticated farmer profile."""
    db = get_db()
    farmer = get_current_farmer()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        state = request.form.get('state', farmer['state']).strip()
        district = request.form.get('district', farmer['district']).strip()
        farm_size = request.form.get('farm_size', str(farmer['farm_size'])).strip()
        primary_crops = request.form.get('primary_crops', farmer['primary_crops'] or '').strip()

        errors = []
        if not name or len(name) < 2:
            errors.append("Full Name cannot be empty.")
        if email and not EMAIL_REGEX.match(email):
            errors.append("Please enter a valid email address.")
        if not district:
            errors.append("District is required.")
        try:
            farm_size_val = float(farm_size)
            if farm_size_val <= 0:
                errors.append("Farm size must be greater than zero.")
        except ValueError:
            farm_size_val = farmer['farm_size']
            errors.append("Invalid farm size number.")

        # Check duplicate email if changed
        if email and email != (farmer['email'] or '').lower():
            dup_email = db.execute("SELECT id FROM farmers WHERE LOWER(email) = ? AND id != ?", (email, farmer['id'])).fetchone()
            if dup_email:
                errors.append("This email address is already in use by another account.")

        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            db.execute(
                """UPDATE farmers 
                   SET name = ?, email = ?, state = ?, district = ?, farm_size = ?, primary_crops = ?
                   WHERE id = ?""",
                (name, email, state, district, farm_size_val, primary_crops, farmer['id'])
            )
            db.commit()
            session['farmer_name'] = name
            session['farmer_email'] = email
            session['district'] = district
            session['state'] = state
            flash("Your farm profile has been updated successfully!", 'success')
            farmer = get_current_farmer()

            # Real-time sync profile update to Supabase
            try:
                from app.database.supabase_client import sync_farmer_to_supabase
                sync_farmer_to_supabase(farmer)
            except Exception:
                pass

    return render_template('auth/profile.html', farmer=farmer, states=INDIAN_STATES_DISTRICTS)
