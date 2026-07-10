from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scanner import scan_text, scan_with_ai
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()  # ucitaj .env fajl

app = FastAPI(title="Secret Scanner & Redactor")

# CORS – dozvoli React frontend sa porta 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    text: str

class Finding(BaseModel):
    type: str
    value: str
    start: int
    end: int
    entropy: Optional[float] = None
    score: Optional[float] = None

class ScanResponse(BaseModel):
    findings: List[Finding]

@app.get("/")
async def root():
    return {"message": "Secret Scanner API is running"}

@app.post("/scan", response_model=ScanResponse)
async def scan(request: ScanRequest):
    findings = scan_text(request.text)
    # ai_findings = scan_with_ai(request.text)   # privremeno isključen AI
    ai_findings = []                            # prazna lista dok ne rešimo mrežu
    all_findings = findings + ai_findings
    all_findings.sort(key=lambda x: x["start"])
    result = [Finding(**f) for f in all_findings]
    return ScanResponse(findings=result)