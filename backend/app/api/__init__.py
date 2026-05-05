from app.api import text_detection, url_detection, pdf_analysis, ocr_detection

api_router = APIRouter()

# Register detection modules
api_router.include_router(text_detection.router, prefix="/text", tags=["text"])
api_router.include_router(url_detection.router, prefix="/url", tags=["url"])
api_router.include_router(pdf_analysis.router, prefix="/pdf", tags=["pdf"])
api_router.include_router(ocr_detection.router, prefix="/ocr", tags=["ocr"])
