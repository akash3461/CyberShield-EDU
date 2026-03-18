from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.schema import ScanRecord, User
from app.utils.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ScanHistoryItem(BaseModel):
    id: int
    scan_type: str
    input_data: str
    prediction: str
    confidence: float
    reasoning: list
    created_at: datetime

    class Config:
        orm_mode = True

@router.get("/history", response_model=List[ScanHistoryItem])
async def get_scan_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch the scan history for the currently authenticated user.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    history = db.query(ScanRecord).filter(
        ScanRecord.user_id == current_user.get("id")
    ).order_by(ScanRecord.created_at.desc()).all()
    
    return history
