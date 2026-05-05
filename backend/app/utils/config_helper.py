from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.schema import SystemConfig
from app.utils.logger import logger
import time

class ConfigHelper:
    _cache = {}
    _last_checked = 0
    _ttl = 60 # 1 minute cache

    @classmethod
    def get_thresholds(cls):
        """Fetches 'analysis_thresholds' with a simple TTL cache."""
        now = time.time()
        if "thresholds" in cls._cache and (now - cls._last_checked) < cls._ttl:
            return cls._cache["thresholds"]

        try:
            db = SessionLocal()
            config = db.query(SystemConfig).filter(SystemConfig.key == "analysis_thresholds").first()
            if config:
                cls._cache["thresholds"] = config.value
            else:
                # Default fallback
                cls._cache["thresholds"] = {"low": 0.3, "high": 0.7}
            
            cls._last_checked = now
            db.close()
            return cls._cache["thresholds"]
        except Exception as e:
            logger.error(f"Failed to fetch dynamic thresholds: {str(e)}")
            return {"low": 0.3, "high": 0.7}

config_helper = ConfigHelper()
