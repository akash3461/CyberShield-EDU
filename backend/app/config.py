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
        # Default origins for development if not specified in .env
        default_origins = "http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000,http://localhost:5173"
        origins = os.getenv("ALLOWED_ORIGINS", default_origins)
        
        if origins == "*":
            # WARNING: In production with allow_credentials=True, this will cause CORS errors.
            self.ALLOWED_ORIGINS = [o.strip() for o in default_origins.split(",") if o.strip()]
        else:
            # Robust split that handles "['a', 'b']" or "a,b"
            clean_origins = origins.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
            self.ALLOWED_ORIGINS = [o.strip() for o in clean_origins.split(",") if o.strip()]
    
    # Scam Detection Config - Tiered for nuanced analysis
    SCAM_KEYWORDS_HIGH: list = [
        "registration fee", "security deposit", "processing fee",
        "pay for internship", "urgent payment", "bank transfer",
        "send money", "crypto payment", "fees jama", "jama karwaein",
        "paise bhejein", "advans", "security jama"
    ]
    SCAM_KEYWORDS_MEDIUM: list = [
        "whatsapp", "telegram", "limited seats", "selected",
        "immediate joining", "gpa boost", "congratulations",
        "mubarak ho", "inam mila", "select ho gaye", "jeeti hai",
        "inbox aayein", "jaldi karein"
    ]
    SCAM_KEYWORDS_CONTEXT: list = [
        "internship", "job", "offer", "scholarship", "recruitment",
        "career", "hiring", "student", "naukri", "mulazmat"
    ]
    
    @property
    def SCAM_KEYWORDS(self) -> list:
        return self.SCAM_KEYWORDS_HIGH + self.SCAM_KEYWORDS_MEDIUM + self.SCAM_KEYWORDS_CONTEXT
    
    # URL Detection Config
    HIGH_RISK_TLDS: list = [".xyz", ".top", ".pw", ".zip", ".click", ".link", ".bid", ".loan"]
    
    SUSPICIOUS_URL_KEYWORDS_HIGH: list = ["login", "verify", "secure", "account", "update", "banking", "auth", "portal"]
    SUSPICIOUS_URL_KEYWORDS_LOW: list = ["internship", "job", "career", "scholarship", "free", "pay", "student", "offer"]
    
    @property
    def SUSPICIOUS_URL_KEYWORDS(self) -> list:
        return self.SUSPICIOUS_URL_KEYWORDS_HIGH + self.SUSPICIOUS_URL_KEYWORDS_LOW
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
