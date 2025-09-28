from datetime import datetime
from typing import Optional, Dict
from .db import conn, ensure_schema 

ensure_schema()  

def upsert_user(user_id: str, city: str, region: str = "", country: str = "US",
                name: Optional[str] = None, lat: Optional[float] = None,
                lon: Optional[float] = None) -> None:
    now = datetime.utcnow().isoformat()
    with conn() as c:
        c.execute("""
            INSERT INTO users (id, name, city, region, country, lat, lon, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              name=excluded.name,
              city=excluded.city,
              region=excluded.region,
              country=excluded.country,
              lat=excluded.lat,
              lon=excluded.lon,
              updated_at=excluded.updated_at
        """, (user_id, name, city, region, country, lat, lon, now, now))
        c.commit()

def get_user(user_id: str) -> Optional[Dict]:
    with conn() as c:
        row = c.execute(
            "SELECT id, name, city, region, country, lat, lon FROM users WHERE id=?",
            (user_id,)
        ).fetchone()
    if not row:
        return None
    keys = ["id", "name", "city", "region", "country", "lat", "lon"]
    return dict(zip(keys, row))
