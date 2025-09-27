from typing import List, Dict, Any
from .discovery import discover_sources
from .extract import fetch_and_extract
from .summarizer import summarize_text

async def process_link(url: str, store) -> Dict[str, Any]:
    raw_text = await fetch_and_extract(url)
    item = await summarize_text(raw_text, source_url=url)
    store.add(item)
    return item

async def run_once(store) -> List[Dict[str, Any]]:
    """Run discovery → extract → summarize → publish once."""
    urls = await discover_sources()
    results: List[Dict[str, Any]] = []
    for url in urls:
        try:
            item = await process_link(url, store)
            results.append(item)
        except Exception as e:
            results.append({"source_url": url, "error": str(e)})
    return results
