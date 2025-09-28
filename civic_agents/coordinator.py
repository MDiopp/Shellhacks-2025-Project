# civic_agents/coordinator.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from .discovery import discover_sources
from .extract import fetch_and_extract
from .summarizer import summarize_text

# Use your storage helpers so results show up in /feed
from storage import CivicDoc, save_doc

def _map_to_civicdoc(item: Dict[str, Any], source_label: Optional[str]) -> CivicDoc:
    """Map summarizer output to your CivicDoc schema."""
    title = item.get("title") or "Civic Update"
    tl_dr = item.get("why_matters") or ""
    highs = item.get("highlights") or []
    return CivicDoc(
        url=source_label or item.get("source_url"),
        title=title,
        tl_dr=tl_dr,
        what_changes=highs[:3],
        what_residents_should_know=highs,
        actions_for_residents=[],     # can prompt for actions later
        tags=[],                      # tagging later
        uncertainty=0.3,              # default for now
        fetched_at=datetime.utcnow().isoformat(),
    )

async def process_link(url: str) -> Dict[str, Any]:
    """Fetch → extract → summarize → save; return the saved item payload."""
    text = await fetch_and_extract(url)
    item = await summarize_text(text, source_url=url)
    # persist to feed
    civic_doc = _map_to_civicdoc(item, url)
    save_doc(civic_doc)
    return item

async def run_once(limit_per_site: int = 10) -> List[Dict[str, Any]]:
    """Discover new sources and process them; return list of item dicts or error records."""
    urls = await discover_sources(limit_per_site=limit_per_site)
    results: List[Dict[str, Any]] = []
    for u in urls:
        try:
            item = await process_link(u)
            results.append(item)
        except Exception as e:
            results.append({"source_url": u, "error": str(e)})
    return results
