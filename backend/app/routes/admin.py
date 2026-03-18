from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import ScanRecord, ScamKeyword
from app.utils.auth import get_current_admin
from app.config import settings
from app.services.awareness_service import awareness_service
import os
import json
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import func

router = APIRouter(dependencies=[Depends(get_current_admin)])

class KeywordUpdate(BaseModel):
    keyword: str

class ResourceUpdate(BaseModel):
    content: dict

@router.get("/system/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_scans = db.query(ScanRecord).count()
    scams_detected = db.query(ScanRecord).filter(ScanRecord.prediction == "scam").count()
    total_keywords = db.query(ScamKeyword).count()
    
    # Calculate time-series data for the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_stats = db.query(
        func.date(ScanRecord.created_at).label('date'),
        func.count(ScanRecord.id).label('count')
    ).filter(ScanRecord.created_at >= seven_days_ago).group_by(func.date(ScanRecord.created_at)).all()
    
    # Format for frontend (Chart.js)
    history_data = [{"date": str(s.date), "count": s.count} for s in daily_stats]
    
    # Scan type distribution
    type_distribution = db.query(
        ScanRecord.scan_type,
        func.count(ScanRecord.id)
    ).group_by(ScanRecord.scan_type).all()
    
    type_data = {t[0]: t[1] for t in type_distribution}
    
    return {
        "total_scans": total_scans,
        "scams_detected": scams_detected,
        "active_models": 4,
        "active_rules": total_keywords,
        "system_status": "Healthy",
        "trends": history_data,
        "distribution": type_data
    }

@router.get("/keywords")
async def get_keywords(db: Session = Depends(get_db)):
    keywords = db.query(ScamKeyword).all()
    # If table is empty, fall back to settings for initial load
    if not keywords and settings.SCAM_KEYWORDS:
        for kw in settings.SCAM_KEYWORDS:
            new_kw = ScamKeyword(keyword=kw)
            db.add(new_kw)
        db.commit()
        keywords = db.query(ScamKeyword).all()

    return {
        "total_keywords": len(keywords),
        "keywords": [kw.keyword for kw in keywords]
    }

@router.post("/keywords")
async def update_keywords(data: dict, db: Session = Depends(get_db)):
    new_keyword = data.get("keyword")
    if new_keyword:
        existing = db.query(ScamKeyword).filter(ScamKeyword.keyword == new_keyword).first()
        if not existing:
            db_kw = ScamKeyword(keyword=new_keyword)
            db.add(db_kw)
            db.commit()
    return {"message": "Keywords updated successfully"}

@router.post("/resources")
async def update_resources(data: ResourceUpdate):
    try:
        path = os.path.join(settings.BASE_DIR, "..", "data", "educational_resources.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data.content, f, indent=2)
        # Reload service content
        awareness_service.content = data.content
        return {"message": "Educational resources updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
