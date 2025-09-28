import os, sqlite3
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]  
DB_PATH = APP_DIR / "civic.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  name TEXT,
  city TEXT,
  region TEXT,
  country TEXT DEFAULT 'US',
  lat REAL,
  lon REAL,
  created_at TEXT,
  updated_at TEXT
);
"""

def get_db_path() -> str:
    return str(DB_PATH)

def conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(get_db_path())

def ensure_schema():
    with conn() as c:
        c.executescript(SCHEMA)
        c.commit()
