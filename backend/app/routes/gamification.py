from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.schema import User, ScanRecord
from app.utils.auth import get_current_user
from app.utils.gamification import gamification_service

router = APIRouter(tags=["Gamification"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/profile")
def get_user_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Pillar 6: Academy Profile Dossier.
    Returns comprehensive stats, badges, and rank for the student.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student account not found")

    # Recalculate stats
    count_all = db.query(ScanRecord).filter(ScanRecord.user_id == user.id).count()
    count_url = db.query(ScanRecord).filter(ScanRecord.user_id == user.id, ScanRecord.scan_type == "url").count()
    count_img = db.query(ScanRecord).filter(ScanRecord.user_id == user.id, ScanRecord.scan_type == "image").count()
    count_pdf = db.query(ScanRecord).filter(ScanRecord.user_id == user.id, ScanRecord.scan_type == "pdf").count()

    # Calculate Level Progress
    next_level_xp = user.level * 100
    current_level_base = (user.level - 1) * 100
    points_in_level = user.xp - current_level_base
    progress_percent = min(100, max(0, (points_in_level / 100) * 100))

    return {
        "username": user.username,
        "email": user.email,
        "xp": user.xp,
        "level": user.level,
        "rank": gamification_service.get_rank_title(user.level),
        "badges": user.badges or [],
        "stats": {
            "total_scans": count_all,
            "url_scans": count_url,
            "image_scans": count_img,
            "pdf_scans": count_pdf
        },
        "next_level_xp": next_level_xp,
        "progress_percent": round(progress_percent, 1)
    }
