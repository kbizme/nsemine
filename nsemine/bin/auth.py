import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime, timedelta



def initialize_database():
    try:
        db_path = Path(__file__).resolve().parent
        conn = sqlite3.connect(database=os.path.join(db_path, 'nsedb.db'))
        cur = conn.cursor()
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS credentials (
                        id TEXT,
                        session_token TEXT, 
                        updated_on TEXT
                        );
                    """)
        conn.commit()
        conn.close()
    except (sqlite3.OperationalError, Exception):
        conn.close()
        pass
    finally:
        if conn:
            conn.close()


def get_db_connection():
        try:
            db_path = Path(__file__).resolve().parent
            conn = sqlite3.connect(os.path.join(db_path, 'nsedb.db'))
            return conn, conn.cursor()
        except Exception:
            conn.close()
            return None


def set_session_token(session_token):
    if not isinstance(session_token, dict):
        return
    nsit = session_token.get('nsit')
    nseappid = session_token.get('nseappid')
    if not nsit and not nseappid:
        return
    data = json.dumps({'nsit': nsit, 'nseappid': nseappid})
    try:
        conn, cursor = get_db_connection()
        cursor.execute(f"SELECT * FROM credentials WHERE id=?",  ('almighty',))
        existing_row = cursor.fetchone()
        if existing_row:
            cursor.execute("UPDATE credentials SET session_token=?, updated_on=? WHERE id=?", (data, str(datetime.now()), 'almighty'))
        else:
            cursor.execute("INSERT INTO credentials (id, session_token, updated_on) VALUES (?, ?, ?)", ('almighty', data, str(datetime.now())))
        conn.commit()
    except Exception as e:
        print(e)
        conn.close()
    finally:
        if conn:
            conn.close()


def get_session_token():
    try:
        conn, cursor = get_db_connection()
        cursor.execute("SELECT * FROM credentials WHERE id=?", ('almighty',))
        data = cursor.fetchone()
        if data:
            offset = datetime.now() - datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S.%f')
            if offset < timedelta(hours=1, minutes=30):
                conn.close()
                return json.loads(data[1])
        if conn:
            conn.close()
        return None
    except Exception:
        if conn:
            conn.close()
        return None

# database initialization
initialize_database()