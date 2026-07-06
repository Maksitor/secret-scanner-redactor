from fastapi import FastAPI
from pydantic import BaseModel
from scanner import scan_text

app = FastAPI(title="Secret Scanner & Redactor")

class ScanRequest(BaseModel):
    text: str

class Finding(BaseModel):
    type: str
    value: str
    start: int
    end: int
    entropy: float | None = None

class ScanResponse(BaseModel):
    findings: list[Finding]

@app.get("/")
async def root():
    return {"message": "Secret Scanner API is running"}

@app.post("/scan", response_model=ScanResponse)
async def scan(request: ScanRequest):
    results = scan_text(request.text)
    # Konvertujemo u listu Finding objekata; za entropiju koristimo None ako nema
    findings = [Finding(**r) for r in results]
    return ScanResponse(findings=findings)