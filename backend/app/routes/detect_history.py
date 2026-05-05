from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.schema import ScanRecord, User
from app.utils.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ScanHistoryItem(BaseModel):
    id: int
    scan_type: str
    input_data: Optional[str] = "No data recorded"
    prediction: str
    confidence: Optional[float] = 0.0
    reasoning: Optional[list] = []
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
    
    user_id = current_user.get("id")
    if not user_id:
        # Fallback to lookup by username if id is missing in token
        user = db.query(User).filter(User.username == current_user.get("sub")).first()
        if user:
            user_id = user.id
            
    if not user_id:
         raise HTTPException(status_code=404, detail="User not found")

    history = db.query(ScanRecord).filter(
        ScanRecord.user_id == user_id
    ).order_by(ScanRecord.created_at.desc()).all()
    
    return history
