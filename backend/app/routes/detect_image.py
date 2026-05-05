from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from typing import Optional
from app.services.image_detector_service import image_detector
from app.utils.auth import get_current_user
from app.utils.logger import logger
from app.utils.limiter import limiter

router = APIRouter()

@router.post("/image")
@limiter.limit("5/minute")
async def detect_image(request: Request, file: UploadFile = File(...), current_user: Optional[dict] = Depends(get_current_user)):
    # Validate file extension
    allowed_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        throw_msg = f"Unsupported image format. Allowed: {', '.join(allowed_extensions)}"
        logger.warning(throw_msg)
        raise HTTPException(status_code=400, detail=throw_msg)
        
    logger.info(f"Received image for OCR analysis: {file.filename}")
    
    try:
        content = await file.read()
        # Perform deep forensic & OCR analysis
        result = await image_detector.analyze(content, filename=file.filename)
        return result
    except Exception as e:
        logger.error(f"Image detection route failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during image OCR analysis")
    finally:
        await file.close()
