import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise SystemExit("GOOGLE_API_KEY missing! Check your .env file.")

genai.configure(api_key=api_key)


models = [
    m for m in genai.list_models()
    if "generateContent" in getattr(m, "supported_generation_methods", [])
]
for m in models:
    print(m.name)
