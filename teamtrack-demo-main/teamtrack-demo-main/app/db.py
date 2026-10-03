import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
NO_ID_TABLES = ("INTO PROJECT_MEMBERS", "INTO FORMULA_SETTINGS")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def query(sql, args=None):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, args)
            return cur.fetchall()
    finally:
        conn.close()

def query_one(sql, args=None):
    rows = query(sql, args)
    return rows[0] if rows else None

def execute(sql, args=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            up = " ".join(sql.upper().split())
            wants_id = (up.startswith("INSERT") and "RETURNING" not in up
                        and not any(t in up for t in NO_ID_TABLES))
            last_id = None
            if wants_id:
                cur.execute(sql.rstrip("; \n") + " RETURNING id", args)
                row = cur.fetchone()
                last_id = row[0] if row else None
            else:
                cur.execute(sql, args)
            conn.commit()
            return last_id
    finally:
        conn.close()