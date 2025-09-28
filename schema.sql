
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  name TEXT,
  city TEXT,
  region TEXT,
  country TEXT DEFAULT 'US',
  lat REAL,
  lon REAL,
  created_at TEXT,
  user_id TEXT,
  updated_at TEXT
);