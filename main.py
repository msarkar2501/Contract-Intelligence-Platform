from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import io
from agent_orchestrator import load_pdf, extract_step, analyze_step

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    contract_text: str
    extracted_result: dict
    party_role: Optional[str] = None

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    file_bytes = await file.read()
    contract_text = load_pdf(io.BytesIO(file_bytes))

    if not contract_text.strip():
        raise HTTPException(status_code = 400, 
                            detail = "Couldn't read text from this PDF."
                        )

    extracted_result = extract_step(contract_text)

    return {"contract_text": contract_text, "extracted_result": extracted_result}

@app.post("/analyze")
def analyze(payload: AnalyzeRequest):
    result = analyze_step(payload.contract_text, payload.extracted_result, payload.party_role)
    return result