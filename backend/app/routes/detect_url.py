from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import ScanRecord
from app.services.url_detector import url_detector
from app.utils.auth import get_current_user
from app.utils.logger import logger
from app.utils.sanitizer import sanitizer
from app.utils.gamification import gamification_service
from app.utils.limiter import limiter

router = APIRouter()

class URLRequest(BaseModel):
    url: str

@router.post("/url")
@limiter.limit("5/minute")
async def detect_url(input_data: URLRequest, request: Request, db: Session = Depends(get_db), current_user: Optional[dict] = Depends(get_current_user)):
    # Sanitize URL
    input_data.url = sanitizer.sanitize_url(input_data.url)
    if "blocked:" in input_data.url:
        raise HTTPException(status_code=400, detail="Invalid or unsafe URL protocol detected.")

    if not input_data.url:
        throw_msg = "URL input cannot be empty"
        logger.warning(throw_msg)
        raise HTTPException(status_code=400, detail=throw_msg)
        
    logger.info(f"Received URL for analysis: {input_data.url}")
    
    try:
        result = await url_detector.analyze(input_data.url)
        
        # Log to DB
        new_record = ScanRecord(
            scan_type="url",
            input_data=input_data.url[:500],
            prediction=result["prediction"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            user_id=current_user.get("id") if current_user else None
        )
        db.add(new_record)
        db.commit()
        
        # Award XP
        if current_user:
            gamification_service.award_xp(db, current_user.get("id"), 15)
            
        return result
    except Exception as e:
        logger.error(f"URL detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during URL analysis")
