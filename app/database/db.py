"""
Database management module for KrishiMitra.
Supports:
  1. Supabase PostgreSQL (when DATABASE_URL is configured)
  2. Local SQLite3 file database (default fallback and offline testing)
"""
import os
import sqlite3
import logging
from flask import current_app, g

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# PostgreSQL Compatibility Wrapper for psycopg2
# ─────────────────────────────────────────────────────────────

class PostgresCursorWrapper:
    """Wraps psycopg2 RealDictCursor to match sqlite3.Cursor interface."""
    def __init__(self, cur):
        self._cur = cur
        self.lastrowid = None

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def fetchmany(self, size=None):
        return self._cur.fetchmany(size) if size else self._cur.fetchmany()

    @property
    def rowcount(self):
        return self._cur.rowcount

    @property
    def description(self):
        return self._cur.description


class PostgresConnectionWrapper:
    """
    Wraps psycopg2 connection to provide SQLite-compatible .execute(query, params)
    with '?' placeholder translation to '%s', RETURNING id for lastrowid, and dict row access.
    """
    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None):
        from psycopg2.extras import RealDictCursor

        pg_sql = sql.replace('?', '%s')
        stripped = pg_sql.strip().upper()
        is_insert = stripped.startswith('INSERT INTO')
        has_returning = 'RETURNING' in stripped

        # Automatically capture lastrowid for INSERT statements
        if is_insert and not has_returning:
            pg_sql_to_run = f"{pg_sql.rstrip(';')} RETURNING id;"
        else:
            pg_sql_to_run = pg_sql

        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        wrapper = PostgresCursorWrapper(cur)
        try:
            if params:
                cur.execute(pg_sql_to_run, tuple(params))
            else:
                cur.execute(pg_sql_to_run)

            if is_insert and not has_returning:
                row = cur.fetchone()
                if row and 'id' in row:
                    wrapper.lastrowid = row['id']
        except Exception:
            # Fall back to original SQL if RETURNING id is not applicable
            if is_insert and not has_returning:
                self._conn.rollback()
                cur = self._conn.cursor(cursor_factory=RealDictCursor)
                wrapper = PostgresCursorWrapper(cur)
                if params:
                    cur.execute(pg_sql, tuple(params))
                else:
                    cur.execute(pg_sql)
            else:
                raise

        return wrapper

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


# ─────────────────────────────────────────────────────────────
# Database Connection Factory
# ─────────────────────────────────────────────────────────────

def get_db():
    """
    Establish and reuse database connection with dictionary-like row access.
    Prefers Supabase PostgreSQL if DATABASE_URL is configured, else uses SQLite.
    """
    if 'db' not in g:
        db_url = current_app.config.get('DATABASE_URL') or os.environ.get('DATABASE_URL')
        
        # Check if PostgreSQL URL is present
        if db_url and (db_url.startswith('postgresql://') or db_url.startswith('postgres://')):
            try:
                import psycopg2
                # Ensure sslmode=require and quick timeout for Supabase
                conn_url = db_url
                if 'sslmode=' not in conn_url:
                    sep = '&' if '?' in conn_url else '?'
                    conn_url = f"{conn_url}{sep}sslmode=require"
                if 'connect_timeout=' not in conn_url:
                    sep = '&' if '?' in conn_url else '?'
                    conn_url = f"{conn_url}{sep}connect_timeout=2"

                pg_conn = psycopg2.connect(conn_url)
                g.db = PostgresConnectionWrapper(pg_conn)
                g.db_backend = 'postgres'
                return g.db
            except Exception as e:
                logger.warning(f"Failed to connect to PostgreSQL ({e}). Falling back to local SQLite.")

        # SQLite Fallback
        db_path = current_app.config.get('DATABASE', 'krishimitra.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        g.db = conn
        g.db_backend = 'sqlite'

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
    backend = getattr(g, 'db_backend', 'sqlite')
    if backend == 'sqlite':
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()


def init_app(app):
    """Register database teardown with Flask application."""
    app.teardown_appcontext(close_db)
