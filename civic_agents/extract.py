import io
import re
from typing import Literal
import httpx
import pdfplumber
from bs4 import BeautifulSoup

ContentType = Literal["application/pdf", "text/html", "text/plain"]

async def fetch_and_extract(url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        ctype = r.headers.get("content-type", "").split(";")[0].lower()
        return await extract_text_from_bytes(r.content, sniff_content_type(url, ctype))

async def extract_text_from_bytes(data: bytes, content_type: ContentType) -> str:
    if content_type == "application/pdf":
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(pages)
    elif content_type == "text/html":
        soup = BeautifulSoup(data, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.extract()
        text = soup.get_text(" ")
        return _normalize(text)
    else:
        return _normalize(data.decode(errors="ignore"))

def sniff_content_type(name_or_url: str | None, header_ctype: str | None) -> ContentType:
    if header_ctype and "pdf" in header_ctype:
        return "application/pdf"
    if name_or_url and name_or_url.lower().endswith(".pdf"):
        return "application/pdf"
    if header_ctype and "html" in header_ctype:
        return "text/html"
    return "text/plain"

def _normalize(t: str) -> str:
    t = re.sub(r"\s+", " ", t)
    return t.strip()