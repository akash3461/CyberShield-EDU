from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from typing import Optional
from app.services.audio_detector_service import audio_detector
from app.utils.auth import get_current_user
from app.utils.logger import logger
from app.utils.limiter import limiter

router = APIRouter()

@router.post("/audio")
@limiter.limit("3/minute")
async def detect_audio(request: Request, file: UploadFile = File(...), current_user: Optional[dict] = Depends(get_current_user)):
    # Validate file extension
    allowed_extensions = {".mp3", ".wav", ".m4a", ".ogg"}
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        throw_msg = f"Unsupported audio format. Allowed: {', '.join(allowed_extensions)}"
        logger.warning(throw_msg)
        raise HTTPException(status_code=400, detail=throw_msg)
        
    logger.info(f"Received audio for Vishing analysis: {file.filename}")
    
    try:
        content = await file.read()
        result = await audio_detector.analyze_audio(content, file.filename)
        return result
    except Exception as e:
        logger.error(f"Audio detection route failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during audio vishing analysis")
    finally:
        await file.close()
