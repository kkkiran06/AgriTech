import psycopg2
from psycopg2.extras import RealDictCursor

class PostgresCursorWrapper:
    def __init__(self, cur):
        self._cur = cur
        self.lastrowid = None

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

class PostgresConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None):
        pg_sql = sql.replace('?', '%s')
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        wrapper = PostgresCursorWrapper(cur)
        if params:
            cur.execute(pg_sql, tuple(params))
        else:
            cur.execute(pg_sql)
        return wrapper

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

conn = psycopg2.connect(
    host='db.ojofmguhhdcvfnwgrzgd.supabase.co',
    port=5432,
    dbname='postgres',
    user='postgres',
    password='KiranKKumar',
    sslmode='require'
)
db = PostgresConnectionWrapper(conn)

# Test select with ?
res = db.execute('SELECT * FROM crops LIMIT 1').fetchone()
print(f"First Crop from Supabase: ID={res['id']}, Name={res['name']} ({res['season']})")

# Test select with like ?
res2 = db.execute('SELECT * FROM diseases_pests WHERE affected_crops LIKE ?', ('%Rice%',)).fetchall()
print(f"Rice diseases count: {len(res2)}")

# Test farmers count
res3 = db.execute('SELECT COUNT(*) AS cnt FROM farmers').fetchone()
print(f"Farmers count in Supabase: {res3['cnt']}")

# Test all tables
for tbl in ['crops', 'fertilizer_soil', 'diseases_pests', 'market_prices', 'government_schemes', 'farmers', 'diagnosis_history']:
    cnt = db.execute(f'SELECT COUNT(*) AS cnt FROM {tbl}').fetchone()['cnt']
    print(f"  Table '{tbl}': {cnt} rows")

db.close()
print("PostgresConnectionWrapper verified 100% OK!")
