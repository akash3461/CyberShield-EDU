import asyncio
from app.celery_app import celery_app
from app.services.image_ocr import image_ocr
from app.services.pdf_analyzer import pdf_analyzer
from app.database import SessionLocal
from app.models.schema import ScanRecord
from app.utils.logger import logger
from app.utils.gamification import gamification_service

@celery_app.task(name="process_image_task")
def process_image_task(file_content, filename, user_id=None):
    logger.info(f"Background task: Processing image {filename}")
    try:
        # Run the heavy analysis using asyncio.run
        result = asyncio.run(image_ocr.analyze(file_content, filename))
        
        if result.get("prediction") == "error":
            return result
            
        # Log to DB
        db = SessionLocal()
        try:
            new_record = ScanRecord(
                scan_type="image",
                input_data=filename,
                prediction=result.get("prediction", "unknown"),
                confidence=result.get("confidence", 0.0),
                reasoning=result.get("reasoning", []),
                user_id=user_id
            )
            db.add(new_record)
            db.commit()
        finally:
            db.close()
            
        return result
    except Exception as e:
        logger.error(f"Async image task failed: {str(e)}")
        return {"error": str(e)}

@celery_app.task(name="process_pdf_task")
def process_pdf_task(file_content, filename, user_id=None):
    logger.info(f"Background task: Processing PDF {filename}")
    try:
        # Run the heavy analysis using asyncio.run
        result = asyncio.run(pdf_analyzer.analyze(file_content, filename))
        
        if result.get("prediction") == "error":
            return result
            
        # Log to DB
        db = SessionLocal()
        try:
            new_record = ScanRecord(
                scan_type="pdf",
                input_data=filename,
                prediction=result.get("prediction", "unknown"),
                confidence=result.get("confidence", 0.0),
                reasoning=result.get("reasoning", []),
                user_id=user_id
            )
            db.add(new_record)
            db.commit()
        finally:
            db.close()
            
        return result
    except Exception as e:
        logger.error(f"Async PDF task failed: {str(e)}")
        return {"error": str(e)}
