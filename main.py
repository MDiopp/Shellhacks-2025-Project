from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os, io, re
import httpx
import pdfplumber
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

# Storage (your existing helpers)
from storage import CivicDoc, save_doc, get_feed

# Agents (robust extract/summarize)
from civic_agents.extract import extract_text_from_bytes, sniff_content_type
from civic_agents.summarizer import summarize_text

# If you still need direct URL fetch helpers below
PDF_HINT = re.compile(r"\.pdf($|\?)", re.I)

# --- App setup ---
load_dotenv()  # ensure .env is loaded for downstream modules
app = FastAPI()

@app.get("/")
def root():
    return {"ok": True, "service": "civic-assistant"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Utilities ----------
async def fetch_url_bytes(url: str) -> tuple[bytes, str]:
    async with httpx.AsyncClient(follow_redirects=True, timeout=25) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.content, r.headers.get("content-type", "") or ""

def extract_text_from_pdf(data: bytes) -> str:
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    return "\n\n".join(pages).strip()

def extract_text_from_html(data: bytes) -> str:
    soup = BeautifulSoup(data, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.extract()
    return " ".join(soup.get_text(" ").split()).strip()

def civicdoc_from_item(item: dict, source_label: Optional[str]) -> CivicDoc:
    """
    Map the summarizer output (title, highlights, why_matters, etc.) into your CivicDoc schema.
    Adjust mappings any time you refine the summarizer format.
    """
    title = item.get("title") or "Civic Update"
    tl_dr = item.get("why_matters") or ""
    highlights = item.get("highlights") or []
    what_changes = highlights[:3]                      # heuristic
    what_residents_should_know = highlights            # reuse for now
    actions_for_residents = []                         # none yet (can prompt for these later)
    tags = []                                          # tagging comes later
    uncertainty = 0.3                                  # default; can be model-estimated later

    return CivicDoc(
        url=source_label or item.get("source_url"),
        title=title,
        tl_dr=tl_dr,
        what_changes=what_changes,
        what_residents_should_know=what_residents_should_know,
        actions_for_residents=actions_for_residents,
        tags=tags,
        uncertainty=uncertainty,
        fetched_at=datetime.utcnow().isoformat(),
    )

# ---------- API models ----------
class SummarizeRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
    neighborhood: Optional[str] = None

# ---------- Routes ----------
@app.post("/summarize")
async def summarize_json(req: SummarizeRequest):
    """
    JSON-only endpoint:
      { "url": "...", "text": "...", "neighborhood": "..." }
    """
    # Quick stub to validate wiring without hitting Gemini
    if req.text and req.text.startswith("[TEST]"):
        return {
            "saved": True,
            "item": {
                "title": "Civic Update (test)",
                "date": "2025-01-01",
                "location": None,
                "highlights": ["Stub path OK"],
                "why_matters": "Endpoint and JSON binding are good.",
                "source_url": None,
                "created_at": "2025-01-01T00:00:00Z",
                "entities": [],
                "body": req.text,
            }
        }

    if not (req.url or req.text):
        raise HTTPException(status_code=400, detail="Provide url or text")

    # Get raw text
    source_label = None
    if req.url:
        data, ctype = await fetch_url_bytes(req.url)
        if "pdf" in ctype.lower() or PDF_HINT.search(req.url):
            doc_text = extract_text_from_pdf(data)
        else:
            doc_text = extract_text_from_html(data)
        source_label = req.url
    else:
        doc_text = req.text or ""
        source_label = "raw_text"

    if not doc_text or len(doc_text.strip()) < 20:
        raise HTTPException(status_code=422, detail="Not enough text extracted to summarize.")

    # Summarize with the robust agent
    item = await summarize_text(doc_text, source_url=(req.url or None))

    # Save to your feed storage
    civic_doc = civicdoc_from_item(item, source_label)
    save_doc(civic_doc)

    return {"saved": True, "item": item}

@app.post("/summarize/upload")
async def summarize_upload(
    file: UploadFile = File(...),
    neighborhood: Optional[str] = Form(None),
):
    """
    Multipart upload endpoint for PDFs.
    """
    raw = await file.read()
    ctype = sniff_content_type(file.filename, file.content_type)
    text = await extract_text_from_bytes(raw, ctype)

    if not text or len(text.strip()) < 20:
        raise HTTPException(status_code=422, detail="Not enough text extracted to summarize.")

    item = await summarize_text(text, source_url=None)

    civic_doc = civicdoc_from_item(item, file.filename or "uploaded.pdf")
    save_doc(civic_doc)

    return {"saved": True, "item": item}

@app.get("/feed")
def feed():
    return {"items": get_feed()}

# Keep your agent endpoint as-is if your coordinator.run_once signature fits.
# If run_once now expects a store, we can adapt it—just tell me which storage you prefer.
from civic_agents.coordinator import run_once as agent_run_once

@app.post("/agent/run-once")
async def run_once_endpoint():
    await agent_run_once()
    return {"status": "ok"}
