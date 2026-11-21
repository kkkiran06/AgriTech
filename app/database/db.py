import sqlite3
import os
from flask import current_app, g

def get_db():
    """Establish and reuse a SQLite database connection with row dictionary access."""
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close the database connection if open."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app=None):
    """Initialize database tables using schema.sql."""
    if app:
        with app.app_context():
            _execute_schema()
    else:
        _execute_schema()

def _execute_schema():
    db = get_db()
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()

def init_app(app):
    """Register database teardown with Flask application."""
    app.teardown_appcontext(close_db)
