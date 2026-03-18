from fastapi import FastAPI, Request
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.utils.limiter import limiter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes import detect_text, detect_url, detect_pdf, detect_image, detect_audio, detect_history, quiz, admin, auth, tasks, scam_report, public_api
from app.config import settings
from app.utils.logger import logger

from slowapi import _rate_limit_exceeded_handler
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend for student scam detection platform",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {exc} | Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Our team has been notified."},
    )

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(detect_text.router, prefix=f"{settings.API_V1_STR}/detect", tags=["detection"])
app.include_router(detect_url.router, prefix=f"{settings.API_V1_STR}/detect", tags=["detection"])
app.include_router(detect_pdf.router, prefix=f"{settings.API_V1_STR}/detect", tags=["detection"])
app.include_router(detect_image.router, prefix=f"{settings.API_V1_STR}/detect", tags=["detection"])
app.include_router(detect_audio.router, prefix=f"{settings.API_V1_STR}/detect", tags=["detection"])
app.include_router(detect_history.router, prefix=f"{settings.API_V1_STR}/detect", tags=["detection"])
app.include_router(quiz.router, prefix=f"{settings.API_V1_STR}/awareness", tags=["awareness"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(tasks.router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])
app.include_router(scam_report.router, prefix=f"{settings.API_V1_STR}/report", tags=["reporting"])
app.include_router(public_api.router, prefix=f"{settings.API_V1_STR}/public", tags=["developer"])

from app.services.awareness_service import awareness_service

from app.database import engine, Base, get_db
from app.models import schema
from sqlalchemy.orm import Session
from fastapi import Depends

# Create tables on startup
Base.metadata.create_all(bind=engine)

@app.get("/", tags=["Health"])
async def root():
    return {"message": "CyberShield EDU API is running", "version": "1.0.0"}

@app.get("/awareness", tags=["Awareness"])
async def get_awareness_content(db: Session = Depends(get_db)):
    """Return educational content and wellness tips for students."""
    content_list = awareness_service.get_all_content(db)
    return content_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
