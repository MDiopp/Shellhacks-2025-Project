from typing import List

SEED_URLS: List[str] = [
    "https://example.com/city/agenda1.pdf",
    "https://example.com/county/agenda2.pdf",
]

async def discover_sources() -> List[str]:
    return SEED_URLS