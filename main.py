from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, io, pdfplumber, re
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai
from storage import CivicDoc, save_doc, get_feed
from datetime import datetime
from agents.coordinator import run_once as agent_run_once


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummaryOut(BaseModel):
    title: str
    tl_dr: str
    what_changes: list[str]
    what_residents_should_know: list[str]
    actions_for_residents: list[str]
    tags: list[str]
    uncertainty: float


PDF_HINT = re.compile(r"\.pdf($|\?)", re.I)


async def fetch_url_bytes(url: str) -> tuple[bytes, str]:
    async with httpx.AsyncClient(follow_redirects=True, timeout=25) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.content, r.headers.get("content-type", "")


def extract_text_from_pdf(data: bytes) -> str:
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    return "\n\n".join(pages).strip()


def extract_text_from_html(data: bytes) -> str:
    soup = BeautifulSoup(data, "html.parser")
    for t in soup(["script", "style", "noscript"]): t.extract()
    return " ".join(soup.get_text(" ").split()).strip()


def build_prompt(doc_text: str) -> str:
    doc_text = doc_text[:20000]  
    return f"""
You are a civic explainer. Input is a local government document (agenda/minutes/notice/news).
Write CLEAR, neutral output at an 8th-grade level. Return the following sections (no extra chatter):

1) Title (<= 80 chars)
2) TL;DR (2–3 sentences)
3) What’s changing (3–5 bullets)
4) What residents should know (3–5 bullets)
5) Actions for residents (max 3)
6) Tags (3 from: housing, zoning, transportation, public_safety, education, environment, finance, taxation, elections)
7) Uncertainty (0.0–1.0; higher if details are unclear)

Document:
\"\"\"{doc_text}\"\"\"
"""

async def summarize_with_gemini(text: str) -> SummaryOut:
    model = genai.GenerativeModel("gemini-1.5-pro")
    resp = await model.generate_content_async(build_prompt(text))
    raw = (resp.text or "").strip()


@app.post("/summarize", response_model=SummaryOut)
async def summarize(
    url: str | None = Form(default=None),
    text: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    neighborhood: str | None = Form(default=None),
):
    
    if not any([url, text, file]):
        raise HTTPException(status_code=400, detail="Provide url, text, or file.")

    
    if url:
        data, ctype = await fetch_url_bytes(url)         
        if "pdf" in ctype.lower() or PDF_HINT.search(url):
            doc_text = extract_text_from_pdf(data)
        else:
            doc_text = extract_text_from_html(data)
        source_label = url                          
    elif text:
        doc_text = text
        source_label = "raw_text"
    else:
        if file.content_type not in ("application/pdf",) and not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF uploads supported for files.")
        data = await file.read()
        doc_text = extract_text_from_pdf(data)
        source_label = file.filename or "uploaded.pdf"

    if not doc_text or len(doc_text.strip()) < 20:
        raise HTTPException(status_code=422, detail="Not enough text extracted to summarize.")

    summary = await summarize_with_gemini(doc_text)

    civic_doc = CivicDoc(
        url=source_label,
        title=summary.title,
        tl_dr=summary.tl_dr,
        what_changes=summary.what_changes,
        what_residents_should_know=summary.what_residents_should_know,
        actions_for_residents=summary.actions_for_residents,
        tags=summary.tags,
        uncertainty=summary.uncertainty,
        fetched_at=datetime.utcnow().isoformat(),
    )
    save_doc(civic_doc)

    return summary


@app.get("/feed")
def feed():
    return {"items": get_feed()}


@app.post("/agent/run-once")
async def run_once_endpoint():
    await agent_run_once()   #
    return {"status": "ok"}