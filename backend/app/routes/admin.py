from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import User, ScanRecord, ScamKeyword, ThreatPattern, SystemConfig
from app.utils.auth import get_current_admin
from app.config import settings
from app.services.awareness_service import awareness_service
import os
import json
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import func

router = APIRouter(dependencies=[Depends(get_current_admin)])

# Threshold Configuration Models
class ThresholdUpdate(BaseModel):
    low: float # Safe -> Suspicious (Default 0.3)
    high: float # Suspicious -> Scam (Default 0.7)

class ResourceUpdate(BaseModel):
    content: list

@router.get("/config/thresholds")
async def get_thresholds(db: Session = Depends(get_db)):
    config = db.query(SystemConfig).filter(SystemConfig.key == "analysis_thresholds").first()
    if not config:
        # Initialize default
        defaults = {"low": 0.3, "high": 0.7}
        config = SystemConfig(key="analysis_thresholds", value=defaults, description="Scan result thresholds")
        db.add(config)
        db.commit()
    return config.value

@router.put("/config/thresholds")
async def update_thresholds(data: ThresholdUpdate, db: Session = Depends(get_db)):
    config = db.query(SystemConfig).filter(SystemConfig.key == "analysis_thresholds").first()
    new_val = {"low": data.low, "high": data.high}
    if not config:
        config = SystemConfig(key="analysis_thresholds", value=new_val, description="Scan result thresholds")
        db.add(config)
    else:
        config.value = new_val
    db.commit()
    return {"message": "Thresholds updated successfully", "config": new_val}

import time
START_TIME = time.time()

@router.get("/system/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_scans = db.query(ScanRecord).count()
    scams_detected = db.query(ScanRecord).filter(ScanRecord.prediction == "scam").count()
    total_users = db.query(User).count()
    total_keywords = db.query(ScamKeyword).count()
    
    # Calculate System Health
    uptime_seconds = int(time.time() - START_TIME)
    uptime_str = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"
    
    # Active users (users who scanned in last 24h)
    yesterday = datetime.utcnow() - timedelta(days=1)
    active_users = db.query(func.count(func.distinct(ScanRecord.user_id))).filter(ScanRecord.created_at >= yesterday).scalar() or 0
    
    # Scam Rate Calculation
    scam_rate = round((scams_detected / total_scans * 100), 1) if total_scans > 0 else 0
    
    # Time-series data (Last 7 Days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_stats = db.query(
        func.date(ScanRecord.created_at).label('date'),
        func.count(ScanRecord.id).label('count')
    ).filter(ScanRecord.created_at >= seven_days_ago).group_by(func.date(ScanRecord.created_at)).all()
    
    history_data = [{"date": str(s.date), "count": s.count} for s in daily_stats]
    
    # Distribution of scan types
    type_distribution = db.query(
        ScanRecord.scan_type,
        func.count(ScanRecord.id)
    ).group_by(ScanRecord.scan_type).all()
    
    # Comparative growth (Last 24h vs Previous 24h)
    prev_day = yesterday - timedelta(days=1)
    scans_24h = db.query(ScanRecord).filter(ScanRecord.created_at >= yesterday).count()
    scans_prev_24h = db.query(ScanRecord).filter(ScanRecord.created_at >= prev_day, ScanRecord.created_at < yesterday).count()
    growth = scans_24h - scans_prev_24h
    
    return {
        "total_scans": total_scans,
        "scams_detected": scams_detected,
        "scam_rate": f"{scam_rate}%",
        "total_users": total_users,
        "active_users": active_users,
        "active_rules": total_keywords,
        "uptime": uptime_str,
        "health": "99.9%",
        "growth_24h": f"+{growth}" if growth >= 0 else str(growth),
        "trends": history_data,
        "distribution": {t[0]: t[1] for t in type_distribution}
    }

@router.get("/logs")
async def get_scan_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(ScanRecord).order_by(ScanRecord.created_at.desc()).limit(limit).all()
    return {
        "logs": [{
            "time": l.created_at.strftime("%I:%M %p"),
            "type": l.scan_type.capitalize(),
            "preview": (l.input_data[:50] + "...") if len(l.input_data) > 50 else l.input_data,
            "prediction": l.prediction,
            "confidence": f"{round(l.confidence * 100)}%",
            "status": "scam" if l.prediction == "scam" else "pending" if l.prediction == "suspicious" else "safe"
        } for l in logs]
    }

@router.get("/users")
async def get_users_list(limit: int = 20, db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).limit(limit).all()
    return {
        "users": [{
            "name": u.username,
            "email": u.email,
            "role": u.role,
            "joined": u.created_at.strftime("%b %Y"),
            "status": "Online", # Placeholder
            "count": db.query(ScanRecord).filter(ScanRecord.user_id == u.id).count()
        } for u in users]
    }

@router.get("/patterns")
async def get_patterns(db: Session = Depends(get_db)):
    patterns = db.query(ThreatPattern).all()
    return {"patterns": patterns}

@router.post("/patterns")
async def create_pattern(data: dict, db: Session = Depends(get_db)):
    new_p = ThreatPattern(
        pattern_type=data.get("type", "keyword"),
        value=data.get("value"),
        risk_score=data.get("risk", 0.2),
        description=data.get("description", "Admin added pattern")
    )
    db.add(new_p)
    db.commit()
    # Reload engine memory
    from app.services.pattern_service import pattern_service
    pattern_service.load_from_db(db)
    return {"message": "Dynamic pattern added and deployed."}

@router.get("/keywords")
async def get_keywords(db: Session = Depends(get_db)):
    keywords = db.query(ScamKeyword).all()
    return {"keywords": [k.keyword for k in keywords]}

@router.post("/keywords")
async def add_keyword(data: dict, db: Session = Depends(get_db)):
    kw = data.get("keyword")
    if kw:
        db_kw = ScamKeyword(keyword=kw)
        db.add(db_kw)
        db.commit()
        # Sync with pattern engine
        from app.services.pattern_service import pattern_service
        pattern_service.load_from_db(db)
    return {"message": "Keyword added."}

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
