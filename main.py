from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, io, pdfplumber, re
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai
app = FastAPI()

@app.get("/")
def root():
    return {"hello": "world"}

