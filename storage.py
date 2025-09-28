from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List
import hashlib

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

_FEED: List[CivicDoc] = []  
_SEEN: set[str] = set()      

def _hash_key(url: str, length: int | None = None) -> str:
    base = f"{url}:{length or 0}"
    return hashlib.sha256(base.encode()).hexdigest()

def already_seen(url: str, length: int | None) -> bool:
    h = _hash_key(url, length)
    if h in _SEEN:
        return True
    _SEEN.add(h)
    return False

def save_doc(doc: CivicDoc):
    _FEED.insert(0, doc)  
    if len(_FEED) > 100:  
        _FEED.pop()

def get_feed() -> list[dict]:
    return [asdict(d) for d in _FEED]
