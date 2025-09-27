import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing GOOGLE_API_KEY in environment")

genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-1.5-pro"

SYSTEM_PROMPT = (
    "You are a civic brief writer. Read the text and produce a concise, plain-language summary "
    "for local residents. Include: title, date (if found), location, 3-6 bullet highlights, and "
    "why-it-matters in one short paragraph. Keep neutral tone."
)

async def summarize_text(text: str, source_url: Optional[str] = None) -> Dict[str, Any]:
    # Simple call with a structured response expectation
    model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=SYSTEM_PROMPT)
    prompt = (
        "Return JSON with keys: title, date, location, highlights (list), why_matters.\n"
        "Text to summarize:\n" + text[:100_000]  # cap to avoid huge prompts
    )
    resp = await model.generate_content_async(prompt)

    # Try to parse JSON; if it fails, fallback to plain
    import json
    payload: Dict[str, Any]
    try:
        payload = json.loads(resp.text)
    except Exception:
        payload = {
            "title": (resp.text.split("\n")[0] or "Civic Update").strip(),
            "date": None,
            "location": None,
            "highlights": [line.strip("- •") for line in resp.text.split("\n")[:5] if line.strip()],
            "why_matters": resp.text,
        }

    return {
        "title": payload.get("title") or "Civic Update",
        "date": payload.get("date") or datetime.utcnow().date().isoformat(),
        "location": payload.get("location"),
        "highlights": payload.get("highlights") or [],
        "why_matters": payload.get("why_matters"),
        "source_url": source_url,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "entities": [],  # could add NER later
        "body": text[:4000],  # raw excerpt for now
    }
