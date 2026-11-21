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

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new farmer account."""
    if session.get('farmer_id'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        state = request.form.get('state', 'Maharashtra').strip()
        district = request.form.get('district', '').strip()
        farm_size = request.form.get('farm_size', '1.0').strip()
        primary_crops = request.form.get('primary_crops', '').strip()

        errors = []
        if not name:
            errors.append("Full Name is required.")
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
            errors.append("Farm size must be a valid number.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', states=INDIAN_STATES_DISTRICTS)

        db = get_db()
        existing = db.execute("SELECT id FROM farmers WHERE mobile = ?", (mobile,)).fetchone()
        if existing:
            flash("This mobile number is already registered. Please log in.", 'warning')
            return redirect(url_for('auth.login'))

        password_hash = generate_password_hash(password)
        db.execute(
            """INSERT INTO farmers (name, mobile, password_hash, state, district, farm_size, primary_crops)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, mobile, password_hash, state, district, farm_size_val, primary_crops)
        )
        db.commit()

        # Retrieve new farmer record to start session
        new_farmer = db.execute("SELECT * FROM farmers WHERE mobile = ?", (mobile,)).fetchone()
        session.clear()
        session['farmer_id'] = new_farmer['id']
        session['farmer_name'] = new_farmer['name']
        session['district'] = new_farmer['district']
        session['state'] = new_farmer['state']

        flash(f"Welcome to KrishiMitra, {name}! Your registration was successful.", 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html', states=INDIAN_STATES_DISTRICTS)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate registered farmer."""
    if session.get('farmer_id'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')

        if not mobile or not password:
            flash("Please enter both mobile number and password.", 'danger')
            return render_template('auth/login.html')

        db = get_db()
        farmer = db.execute("SELECT * FROM farmers WHERE mobile = ?", (mobile,)).fetchone()

        if farmer is None or not check_password_hash(farmer['password_hash'], password):
            flash("Invalid mobile number or password. Please try again.", 'danger')
            return render_template('auth/login.html')

        session.clear()
        session['farmer_id'] = farmer['id']
        session['farmer_name'] = farmer['name']
        session['district'] = farmer['district']
        session['state'] = farmer['state']

        flash(f"Welcome back, {farmer['name']}!", 'success')
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
    """View and update farmer profile."""
    db = get_db()
    farmer = get_current_farmer()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        state = request.form.get('state', farmer['state']).strip()
        district = request.form.get('district', farmer['district']).strip()
        farm_size = request.form.get('farm_size', str(farmer['farm_size'])).strip()
        primary_crops = request.form.get('primary_crops', farmer['primary_crops'] or '').strip()

        errors = []
        if not name:
            errors.append("Full Name cannot be empty.")
        if not district:
            errors.append("District is required.")
        try:
            farm_size_val = float(farm_size)
            if farm_size_val <= 0:
                errors.append("Farm size must be greater than zero.")
        except ValueError:
            errors.append("Invalid farm size number.")

        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            db.execute(
                """UPDATE farmers 
                   SET name = ?, state = ?, district = ?, farm_size = ?, primary_crops = ?
                   WHERE id = ?""",
                (name, state, district, farm_size_val, primary_crops, farmer['id'])
            )
            db.commit()
            session['farmer_name'] = name
            session['district'] = district
            session['state'] = state
            flash("Your profile has been updated successfully!", 'success')
            farmer = get_current_farmer()

    return render_template('auth/profile.html', farmer=farmer, states=INDIAN_STATES_DISTRICTS)
