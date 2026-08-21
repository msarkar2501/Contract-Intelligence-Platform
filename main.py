from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import io

from openai import RateLimitError, OpenAIError

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from agent_orchestrator import load_pdf, extract_step, analyze_step

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB — plenty for a contract PDF, cheap to enforce

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
@limiter.limit("5/hour")
async def extract(request: Request, file: UploadFile = File(...)):
    file_bytes = await file.read()

    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large. This demo caps uploads at 10MB.")

    contract_text = load_pdf(io.BytesIO(file_bytes))
    if not contract_text.strip():
        raise HTTPException(status_code=400, detail="Couldn't read text from this PDF.")

    try:
        extracted_result = extract_step(contract_text)
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Gemini's free-tier daily limit is hit. Try again later.")
    except (RuntimeError, OpenAIError) as e:
        raise HTTPException(status_code=502, detail=f"Extraction failed: {e}")

    return {"contract_text": contract_text, "extracted_result": extracted_result}


@app.post("/analyze")
@limiter.limit("5/hour")
def analyze(request: Request, payload: AnalyzeRequest):
    try:
        result = analyze_step(payload.contract_text, payload.extracted_result, payload.party_role)
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Gemini's free-tier daily limit is hit. Try again later.")
    except (RuntimeError, OpenAIError) as e:
        raise HTTPException(status_code=502, detail=f"Analysis failed: {e}")

    return result