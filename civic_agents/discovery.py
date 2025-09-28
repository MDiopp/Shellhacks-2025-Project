import re
from typing import List, Set
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
import os


DEFAULT_SEEDS: List[str] = [
    "https://www.orlando.gov/Our-Government/Mayor-City-Council/City-Council-Meetings",
    "https://www.orangecountyfl.net/OpenGovernment/BoardofCountyCommissioners/Agenda.aspx",
    ""
]

KEYWORDS = re.compile(r"(agenda|minutes|packet|meeting|notice|public\s*hearing)", re.I)
PDF_HINT = re.compile(r"\.pdf($|\?)", re.I)

def _seeds_from_env() -> List[str]:
    raw = os.getenv("CIVIC_SOURCE_URLS", "")
    if not raw.strip():
        return DEFAULT_SEEDS
    return [s.strip() for s in raw.split(",") if s.strip()]

async def _fetch_html(url: str, client: httpx.AsyncClient) -> str:
    r = await client.get(url, timeout=30, follow_redirects=True)
    r.raise_for_status()
    try:
        return r.text
    except Exception:
        return r.content.decode(errors="ignore")

def _clean_and_filter_links(html: str, base: str, limit: int) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.extract()

    links: List[str] = []
    seen: Set[str] = set()
    base_netloc = urlparse(base).netloc

    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        if not href:
            continue
        text = (a.get_text(" ") or "").strip()

        abs_url = urljoin(base, href)
        if urlparse(abs_url).netloc and base_netloc and urlparse(abs_url).netloc != base_netloc:
            if not PDF_HINT.search(abs_url):
                continue

        if PDF_HINT.search(abs_url) or KEYWORDS.search(href) or KEYWORDS.search(text):
            if abs_url not in seen:
                seen.add(abs_url)
                links.append(abs_url)
                if len(links) >= limit:
                    break
    return links

async def discover_sources(limit_per_site: int = 10, max_sites: int = 5) -> List[str]:
    seeds = _seeds_from_env()[:max_sites]
    found: List[str] = []
    seen: Set[str] = set()

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for seed in seeds:
            try:
                html = await _fetch_html(seed, client)
                urls = _clean_and_filter_links(html, seed, limit_per_site)
                for u in urls:
                    if u not in seen:
                        seen.add(u)
                        found.append(u)
            except Exception as e:
                print(f"[discovery] Failed {seed}: {e!r}")
                continue
    return found


from typing import List, Set
import httpx

async def discover_sources_from(seeds: List[str], limit_per_site: int = 10, max_sites: int = 5) -> List[str]:
    if not seeds:
        return []
    seeds = [s for s in seeds if isinstance(s, str) and s.lower().startswith(("http://", "https://"))][:max_sites]

    found: List[str] = []
    seen: Set[str] = set()

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for seed in seeds:
            try:
                html = await _fetch_html(seed, client)         
                urls = _clean_and_filter_links(html, seed, limit_per_site)  
                for u in urls:
                    if u not in seen:
                        seen.add(u)
                        found.append(u)
            except Exception as e:
                print(f"[discovery] Failed {seed}: {e!r}")
                continue
    return found


async def discover_sources(limit_per_site: int = 10, max_sites: int = 5) -> List[str]:
    seeds = _seeds_from_env() if "_seeds_from_env" in globals() else []
    return await discover_sources_from(seeds, limit_per_site=limit_per_site, max_sites=max_sites)
