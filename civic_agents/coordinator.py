from typing import List, Dict, Any, Optional
from datetime import datetime
from .discovery import discover_sources
from .extract import fetch_and_extract
from .summarizer import summarize_text


from storage import CivicDoc, save_doc


from typing import List, Dict, Any, Optional
from datetime import datetime

from .extract import fetch_and_extract
from .summarizer import summarize_text


from storage.feed import CivicDoc, save_doc


def _map_to_civicdoc(item: Dict[str, Any], source_label: Optional[str], user_id: str) -> CivicDoc:
  
    title = item.get("title") or "Civic Update"
    tl_dr = item.get("why_matters") or ""
    highs = item.get("highlights") or []
    return CivicDoc(
        url=source_label or item.get("source_url"),
        title=title,
        tl_dr=tl_dr,
        what_changes=highs[:3],
        what_residents_should_know=highs,
        actions_for_residents=[],
        tags=[],
        uncertainty=0.3,
        fetched_at=datetime.utcnow().isoformat(),
        user_id=user_id,  
    )

async def process_link(url: str, user_id: str = "demo") -> Dict[str, Any]:
    text = await fetch_and_extract(url)
    item = await summarize_text(text, source_url=url)
    civic_doc = _map_to_civicdoc(item, url, user_id)
    save_doc(civic_doc)
    item["source_url"] = url
    return item

async def run_once(urls: List[str], user_id: str = "demo") -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for u in urls:
        try:
            item = await process_link(u, user_id=user_id)  
            results.append(item)
        except Exception as e:
            results.append({"source_url": u, "error": str(e)})
    return results
