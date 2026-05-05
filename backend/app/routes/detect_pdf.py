from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from typing import Optional
from app.services.pdf_analyzer import pdf_analyzer
from app.tasks import process_pdf_task
from app.utils.auth import get_current_user
from app.utils.logger import logger
from app.utils.limiter import limiter

router = APIRouter()

@router.post("/pdf")
@limiter.limit("5/minute")
async def detect_pdf(request: Request, file: UploadFile = File(...), current_user: Optional[dict] = Depends(get_current_user)):
    if not file.filename.lower().endswith('.pdf'):
        throw_msg = "Only PDF files are supported"
        logger.warning(throw_msg)
        raise HTTPException(status_code=400, detail=throw_msg)
        
    logger.info(f"Received PDF for analysis: {file.filename}")
    
    try:
        content = await file.read()
        # Trigger background task
        task = process_pdf_task.delay(
            content, 
            file.filename, 
            user_id=current_user.get("id") if current_user else None
        )
        return {"task_id": task.id, "status": "processing", "message": "Analysis started in background"}
    except Exception as e:
        logger.error(f"PDF detection route failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during PDF document analysis")
    finally:
        await file.close()
