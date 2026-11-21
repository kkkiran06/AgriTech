import functools
from flask import session, redirect, url_for, flash, g
from app.database.db import get_db

def login_required(view):
    """Decorator to require login for protected routes."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('farmer_id') is None:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def get_current_farmer():
    """Retrieve currently authenticated farmer's database record."""
    farmer_id = session.get('farmer_id')
    if farmer_id is None:
        return None
    db = get_db()
    farmer = db.execute("SELECT * FROM farmers WHERE id = ?", (farmer_id,)).fetchone()
    return farmer
