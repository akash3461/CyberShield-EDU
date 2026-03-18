import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseModel):
    APP_NAME: str = os.getenv("APP_NAME", "CyberShield EDU")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Security & CORS
    SECRET_KEY: str = os.getenv("SECRET_KEY", "placeholder-key-for-dev")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Parse ALLOWED_ORIGINS from string like "http://localhost:5173,http://localhost:3000"
    ALLOWED_ORIGINS: list = []

    def __init__(self, **values):
        super().__init__(**values)
        origins = os.getenv("ALLOWED_ORIGINS", "*")
        if origins == "*":
            self.ALLOWED_ORIGINS = ["*"]
        else:
            # Robust split that handles "['a', 'b']" or "a,b"
            clean_origins = origins.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
            self.ALLOWED_ORIGINS = [o.strip() for o in clean_origins.split(",") if o.strip()]
    
    # Scam Detection Config
    SCAM_KEYWORDS: list = [
        "registration fee", "security deposit", "processing fee",
        "whatsapp", "telegram", "pay for internship", "limited seats",
        "congratulations", "selected", "immediate joining", "gpa boost",
        "free certificate", "urgent payment"
    ]
    
    # URL Detection Config
    HIGH_RISK_TLDS: list = [".xyz", ".top", ".pw", ".zip", ".click", ".link", ".bid", ".loan"]
    SUSPICIOUS_URL_KEYWORDS: list = [
        "login", "verify", "secure", "account", "update", "banking", 
        "internship", "job", "career", "scholarship", "free", "pay", 
        "portal", "student", "auth"
    ]
    TRUSTED_DOMAINS: list = [".edu", ".gov", ".ac.in", ".edu.in", "google.com", "microsoft.com", "github.com"]
    POPULAR_DOMAINS: list = ["google.com", "facebook.com", "amazon.com", "apple.com", "microsoft.com", "netflix.com", "github.com", "linkedin.com"]

    # Path Configuration
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH: str = os.path.join(BASE_DIR, "app", "models")

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:password@localhost/cybershield")
    
    # Celery & Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

    # External APIs
    URLSCAN_API_KEY: str = os.getenv("URLSCAN_API_KEY", "")

settings = Settings()
