from fastapi import APIRouter, HTTPException, Request, Depends, UploadFile, File, Form
from typing import Optional
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
from app.database import get_db
from app.models.schema import ScamReport
from app.utils.logger import logger
from app.utils.limiter import limiter

router = APIRouter()

# Ensure uploads directory exists
UPLOAD_DIR = "uploads/reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/reports")
@limiter.limit("3/minute")
async def report_scam(
    request: Request,
    company_name: str = Form(...),
    description: str = Form(...),
    is_anonymous: bool = Form(True),
    evidence: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    logger.info(f"Received scam report for company: {company_name}")
    
    evidence_path = None
    if evidence:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{evidence.filename.replace(' ', '_')}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        try:
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(evidence.file, buffer)
            evidence_path = filepath
            logger.info(f"Evidence uploaded to {evidence_path}")
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            # Continue without file if upload fails, or raise error? 
            # Let's raise error for now to ensure data integrity
            raise HTTPException(status_code=500, detail="Failed to upload evidence file")

    try:
        new_report = ScamReport(
            company_name=company_name,
            description=description,
            is_anonymous=is_anonymous,
            evidence_path=evidence_path,
            status="pending"
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        
        return {
            "status": "success",
            "message": "Scam report submitted successfully",
            "report_id": new_report.id
        }
    except Exception as e:
        logger.error(f"Database save failed: {str(e)}")
        # If DB fails but file was uploaded, we might want to clean up the file
        if evidence_path and os.path.exists(evidence_path):
            os.remove(evidence_path)
        raise HTTPException(status_code=500, detail="Failed to save scam report")
        
@router.get("/recent")
async def get_recent_reports(db: Session = Depends(get_db)):
    """Fetch recent scam reports for the ticker."""
    reports = db.query(ScamReport).order_by(ScamReport.id.desc()).limit(5).all()
    return [{"company_name": r.company_name, "description": r.description} for r in reports]

