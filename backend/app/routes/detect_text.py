from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import ScanRecord, User
from app.utils.gamification import gamification_service
from app.services.text_detector import text_detector
from app.utils.auth import get_current_user
from app.utils.logger import logger
from app.utils.sanitizer import sanitizer
from app.utils.limiter import limiter

router = APIRouter()

class TextRequest(BaseModel):
    text: str

@router.post("/text")
@limiter.limit("5/minute")
async def detect_text(input_data: TextRequest, request: Request, db: Session = Depends(get_db), current_user: Optional[dict] = Depends(get_current_user)):
    # Sanitize input
    input_data.text = sanitizer.clean_text(input_data.text)
    
    if not input_data.text:
        throw_msg = "Text input cannot be empty"
        logger.warning(throw_msg)
        raise HTTPException(status_code=400, detail=throw_msg)
        
    logger.info(f"Received text for analysis: {input_data.text[:100]}...")
    
    try:
        result = await text_detector.analyze(input_data.text)
        
        # Log to DB
        new_record = ScanRecord(
            scan_type="text",
            input_data=input_data.text[:500],
            prediction=result["prediction"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            user_id=current_user.get("id") if current_user else None
        )
        db.add(new_record)
        db.commit()
        
        # Award XP
        if current_user:
            gamification_service.award_xp(db, current_user.get("id"), 10)
        
        return result
    except Exception as e:
        logger.error(f"Text detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during text analysis")
