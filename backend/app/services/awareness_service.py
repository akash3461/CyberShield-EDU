import json
import os
from app.utils.logger import logger
from app.config import settings

from sqlalchemy.orm import Session
from app.models.schema import AwarenessContent
from app.utils.logger import logger

class AwarenessService:
    def get_all_content(self, db: Session):
        try:
            return db.query(AwarenessContent).all()
        except Exception as e:
            logger.error(f"Failed to fetch educational resources from DB: {str(e)}")
            return []

    def get_category(self, db: Session, category_name: str):
        return db.query(AwarenessContent).filter(AwarenessContent.category == category_name).all()

awareness_service = AwarenessService()
