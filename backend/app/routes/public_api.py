from fastapi import APIRouter, Depends, Header, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.api_key_service import api_key_service
from app.services.text_detector import text_detector
from app.services.url_detector import url_detector
from pydantic import BaseModel

router = APIRouter()
X_API_KEY = APIKeyHeader(name="X-API-Key")

class TextScanRequest(BaseModel):
    text: str

class URLScanRequest(BaseModel):
    url: str

async def get_api_key_client(
    api_key: str = Security(X_API_KEY), 
    db: Session = Depends(get_db),
    x_sandbox: bool = Header(False, alias="X-Sandbox")
):
    if x_sandbox:
        return "SANDBOX"

    client = api_key_service.validate_key(api_key, db)
    if client == "RATE_LIMITED":
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Daily limit reached.")
    if not client:
        raise HTTPException(status_code=401, detail="Invalid or inactive API Key")
    return client

@router.post("/detect/text")
async def public_detect_text(
    request: TextScanRequest, 
    client = Depends(get_api_key_client)
):
    """Public endpoint for text scam detection."""
    if client == "SANDBOX":
        return {
            "prediction": "scam",
            "confidence": 0.99,
            "reasoning": {"indicators": ["SANDBOX_MODE_ENABLED", "Simulated suspicious pattern"]},
            "status": "sandbox"
        }
        
    result = await text_detector.analyze(request.text)
    return result

@router.post("/detect/url")
async def public_detect_url(
    request: URLScanRequest, 
    client = Depends(get_api_key_client)
):
    """Public endpoint for URL scam detection."""
    if client == "SANDBOX":
        return {
            "prediction": "safe",
            "confidence": 1.0,
            "reasoning": {"indicators": ["SANDBOX_MODE_ENABLED"]},
            "status": "sandbox"
        }

    result = await url_detector.analyze(request.url)
    return result
