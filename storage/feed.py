# storage/feed.py
# storage/feed.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from .db import conn, ensure_schema


ensure_schema()


with conn() as c:
    c.executescript("""
    CREATE TABLE IF NOT EXISTS civic_docs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT,
      url TEXT,
      title TEXT,
      tl_dr TEXT,
      what_changes TEXT,                 -- JSON string
      what_residents_should_know TEXT,   -- JSON string
      actions_for_residents TEXT,        -- JSON string
      tags TEXT,                         -- JSON string
      uncertainty REAL,
      fetched_at TEXT
    );
    """)
    c.commit()

@dataclass
class CivicDoc:
    url: str
    title: str
    tl_dr: str
    what_changes: List[str]
    what_residents_should_know: List[str]
    actions_for_residents: List[str]
    tags: List[str]
    uncertainty: float
    fetched_at: str
    user_id: Optional[str] = None

    @staticmethod
    def from_item(item: Dict[str, Any], user_id: Optional[str] = None) -> "CivicDoc":
        return CivicDoc(
            url=item.get("source_url") or item.get("url") or "",
            title=item.get("title") or "Civic Update",
            tl_dr=item.get("why_matters") or item.get("what_happened") or "",
            what_changes=item.get("highlights") or item.get("impacts") or [],
            what_residents_should_know=item.get("highlights") or item.get("impacts") or [],
            actions_for_residents=item.get("actions") or [],
            tags=item.get("tags") or [],
            uncertainty=float(item.get("uncertainty", 0.3)),
            fetched_at=item.get("fetched_at") or datetime.utcnow().isoformat(),
            user_id=user_id,
        )

def _dump_json(x: Any) -> str:
    import json
    return json.dumps(x, ensure_ascii=False)

def _load_json(s: Optional[str]) -> Any:
    import json
    return json.loads(s or "[]")

def save_doc(doc: CivicDoc) -> int:
    with conn() as c:
        cur = c.execute("""
        INSERT INTO civic_docs
        (user_id, url, title, tl_dr, what_changes, what_residents_should_know,
         actions_for_residents, tags, uncertainty, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc.user_id, doc.url, doc.title, doc.tl_dr,
            _dump_json(doc.what_changes),
            _dump_json(doc.what_residents_should_know),
            _dump_json(doc.actions_for_residents),
            _dump_json(doc.tags),
            doc.uncertainty, doc.fetched_at
        ))
        c.commit()
        return int(cur.lastrowid)

def get_feed(user_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    q = "SELECT user_id, url, title, tl_dr, what_changes, what_residents_should_know, actions_for_residents, tags, uncertainty, fetched_at FROM civic_docs"
    args: List[Any] = []
    if user_id:
        q += " WHERE user_id = ?"
        args.append(user_id)
    q += " ORDER BY id DESC LIMIT ?"
    args.append(limit)

    with conn() as c:
        rows = c.execute(q, tuple(args)).fetchall()

    out = []
    for r in rows:
        (uid, url, title, tl_dr, wc, wrsk, act, tags, un, ts) = r
        out.append({
            "user_id": uid,
            "url": url,
            "title": title,
            "tl_dr": tl_dr,
            "what_changes": _load_json(wc),
            "what_residents_should_know": _load_json(wrsk),
            "actions_for_residents": _load_json(act),
            "tags": _load_json(tags),
            "uncertainty": un,
            "fetched_at": ts,
        })
    return out
