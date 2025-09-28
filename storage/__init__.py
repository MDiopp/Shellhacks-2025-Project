# storage/__init__.py

from typing import List, Optional, Dict
from .db import conn
from .feed import save_doc, get_feed
from .users import upsert_user, get_user

class CivicDoc:
    def __init__(
        self,
        url: str,
        title: str,
        tl_dr: str,
        what_changes: Optional[List[str]] = None,
        what_residents_should_know: Optional[List[str]] = None,
        actions_for_residents: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        uncertainty: float = 0.0,
        fetched_at: Optional[str] = None,
    ):
        self.url = url
        self.title = title
        self.tl_dr = tl_dr
        self.what_changes = what_changes or []
        self.what_residents_should_know = what_residents_should_know or []
        self.actions_for_residents = actions_for_residents or []
        self.tags = tags or []
        self.uncertainty = uncertainty
        self.fetched_at = fetched_at

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "title": self.title,
            "tl_dr": self.tl_dr,
            "what_changes": self.what_changes,
            "what_residents_should_know": self.what_residents_should_know,
            "actions_for_residents": self.actions_for_residents,
            "tags": self.tags,
            "uncertainty": self.uncertainty,
            "fetched_at": self.fetched_at,
        }
