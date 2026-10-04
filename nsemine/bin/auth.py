import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta


DB_PATH = Path(__file__).resolve().parent / "nsedb.db"




def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn
    except Exception as e:
        print(f"Database connection failure: {e}")
        return None


def initialize_database():
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    id TEXT PRIMARY KEY,
                    session_token TEXT,
                    updated_on TEXT
                );
            """)
    finally:
        conn.close()


def set_session_token(session_token: dict):
    if not isinstance(session_token, dict) or not session_token:
        return
        
    conn = get_db_connection()
    if not conn:
        return
    try:
        data = json.dumps(session_token)
        now_str = datetime.now().isoformat()
        with conn:
            conn.execute("""
                INSERT INTO credentials (id, session_token, updated_on)
                VALUES ('almighty', ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    session_token = excluded.session_token,
                    updated_on = excluded.updated_on;
            """, (data, now_str))
    except Exception as e:
        print(f"Database write error: {e}")
    finally:
        conn.close()


def get_session_token(max_age_minutes: int = 60) -> dict | None:
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT session_token, updated_on FROM credentials WHERE id=?", ('almighty',))
        row = cursor.fetchone()
        if row:
            session_json, updated_str = row
            updated_time = datetime.fromisoformat(updated_str)
            if datetime.now() - updated_time < timedelta(minutes=max_age_minutes):
                return json.loads(session_json)
        return None
    except Exception as e:
        print(f"Database read error: {e}")
        return None
    finally:
        conn.close()


# database initialization
initialize_database()