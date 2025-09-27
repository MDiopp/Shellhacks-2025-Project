import os, json, asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai

MAX_CHARS = 100_000

def _get_model(model_name: Optional[str] = None):
    # Load .env and read env vars at call time
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY in environment (.env)")
    genai.configure(api_key=api_key)

    # 👇 pick model now (after .env is loaded)
    name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    return genai.GenerativeModel(
        model_name=name,
        system_instruction=(
            "You are a civic brief writer. Read the text and produce a concise, plain-language summary "
            "for local residents. Include: title, date (if found), location, 3-6 bullet highlights, and "
            "why-it-matters in one short paragraph. Keep neutral tone."
        ),
        generation_config={
            "temperature": 0.2,
            "response_mime_type": "application/json",
        },
    )

async def summarize_text(text: str, source_url: Optional[str] = None) -> Dict[str, Any]:
    prompt = (
        "Return JSON with keys: title, date, location, highlights (list), why_matters.\n"
        "Text to summarize:\n" + (text or "")[:MAX_CHARS]
    )
    # Use model from env at runtime
    model = _get_model()

    try:
        resp = await asyncio.to_thread(model.generate_content, prompt)
        raw = (getattr(resp, "text", None) or "").strip()
    except Exception as e:
        # try fallback model from env
        fb = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-1.5-flash")
        print("Gemini call failed on primary:", repr(e), " → trying fallback:", fb)
        resp = await asyncio.to_thread(_get_model(fb).generate_content, prompt)
        raw = (getattr(resp, "text", None) or "").strip()

    try:
        payload = json.loads(raw)
    except Exception:
        payload = {
            "title": (raw.split("\n")[0] or "Civic Update").strip(),
            "date": None, "location": None,
            "highlights": [ln.strip("- •") for ln in raw.split("\n")[:5] if ln.strip()],
            "why_matters": raw,
        }

    return {
        "title": payload.get("title") or "Civic Update",
        "date": payload.get("date") or datetime.utcnow().date().isoformat(),
        "location": payload.get("location"),
        "highlights": payload.get("highlights") or [],
        "why_matters": payload.get("why_matters"),
        "source_url": source_url,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "entities": [],
        "body": (text or "")[:4000],
    }
