from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os, io, re
import httpx
import pdfplumber
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
from storage.users import upsert_user, get_user
import json, os, pathlib
from civic_agents.discovery import discover_sources_from
from civic_agents.coordinator import process_link   
from storage.users import get_user                  




from storage import CivicDoc, save_doc, get_feed


from civic_agents.extract import extract_text_from_bytes, sniff_content_type
from civic_agents.summarizer import summarize_text


PDF_HINT = re.compile(r"\.pdf($|\?)", re.I)


load_dotenv()  
app = FastAPI()


CITY_SOURCES_PATH = pathlib.Path("city_sources.json")

def _load_city_sources() -> dict:
    try:
        with CITY_SOURCES_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _norm(s: str) -> str:
    return "".join((s or "").split()).replace(".", "").replace("-", "")

def _seeds_for_user(user: dict) -> list[str]:
    data = _load_city_sources()   # <-- freshly read each call

    city = user.get("city") or ""
    region = (user.get("region") or "").upper()
    country = (user.get("country") or "US").upper()

    keys_to_try = [
        f"{_norm(city)},{region},{country}",
        f"{_norm(city)},{region},US",
        f"{_norm(city)},{region}",
    ]
    for k in keys_to_try:
        seeds = data.get(k)
        if seeds:
            return seeds

    # fallback to ENV
    raw = os.getenv("CIVIC_SOURCE_URLS", "")
    seeds = []
    for line in raw.splitlines():
        for part in line.split(","):
            u = part.strip()
            if u.startswith("http"):
                seeds.append(u)
    return seeds


@app.post("/agent/run-for-me")
async def run_for_me(user_id: str = "demo", limit_per_site: int = 10):
    user = get_user(user_id)
    if not user or not user.get("city"):
        return {"error": "Set your location first with POST /me/location"}

    seeds = _seeds_for_user(user)
    if not seeds:
        return {"error": f"No seeds found for {user.get('city')},{user.get('region')},{user.get('country')}. "
                         f"Add to city_sources.json or set CIVIC_SOURCE_URLS."}

    urls = await discover_sources_from(seeds, limit_per_site=limit_per_site)
    results = []
    for u in urls:
        try:
            item = await process_link(u)   # fetch → extract → summarize → save
            results.append(item)
        except Exception as e:
            results.append({"source_url": u, "error": str(e)})

    return {
        "user": {"city": user.get("city"), "region": user.get("region"), "country": user.get("country")},
        "seeds_used": seeds,
        "discovered": len(results),
        "ok": sum(1 for r in results if "error" not in r),
        "errors": [r for r in results if "error" in r][:5],
        "preview": [
            {"title": r.get("title"), "source_url": r.get("source_url")}
            for r in results if "error" not in r
        ][:8],
    }



class LocationIn(BaseModel):
    city: str
    region: Optional[str] = ""
    country: Optional[str] = "US"
    lat: Optional[float] = None
    lon: Optional[float] = None


@app.get("/")
def root():
    return {"ok": True, "service": "civic-assistant"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    title = item.get("title") or "Civic Update"
    tl_dr = item.get("why_matters") or ""
    highlights = item.get("highlights") or []
    what_changes = highlights[:3]                      
    what_residents_should_know = highlights            
    actions_for_residents = []                         
    tags = []                                          
    uncertainty = 0.3                                 

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

    item = await summarize_text(doc_text, source_url=(req.url or None))

    civic_doc = civicdoc_from_item(item, source_label)
    save_doc(civic_doc)

    return {"saved": True, "item": item}

@app.post("/summarize/upload")
async def summarize_upload(
    file: UploadFile = File(...),
    neighborhood: Optional[str] = Form(None),
):

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


# main.py
from civic_agents.coordinator import run_once as agent_run_once

@app.post("/agent/run-once")
async def run_once_endpoint():
    items = await agent_run_once()   # returns list of item dicts (or error dicts)
    # show a small preview; the full items are typically long
    return {
        "discovered": len(items),
        "ok": sum(1 for x in items if "error" not in x),
        "errors": [x for x in items if "error" in x][:3],
        "preview": [ {"title": x.get("title"), "source_url": x.get("source_url")} for x in items if "error" not in x ][:5]
    }


@app.get("/me")
async def get_me(user_id: str = "demo"):
    user = get_user(user_id)
    if not user:
        return {"ok": False, "error": "User not found"}
    return {"ok": True, **user}

@app.post("/me/location")
async def set_location(loc: LocationIn, request: Request, user_id: str = "demo"):
    upsert_user(
        user_id,
        city=loc.city,
        region=loc.region,
        country=loc.country,
        lat=loc.lat,
        lon=loc.lon,
    )
    return {"ok": True, "user_id": user_id, "city": loc.city, "region": loc.region, "country": loc.country}


@app.get("/debug/city-sources-keys")
def debug_city_keys():
    return {"keys": list(_load_city_sources().keys())[:200]}


def save_doc(doc: CivicDoc):
    with conn() as c:
        c.execute(
            "INSERT INTO feed (url, title, content, user_id) VALUES (?, ?, ?, ?)",
            (doc.url, doc.title, doc.content, doc.user_id),
        )
        c.commit()
