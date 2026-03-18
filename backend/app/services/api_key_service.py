import hashlib
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.schema import ApiKey
from app.utils.logger import logger

class ApiKeyService:
    def generate_key_pair(self, user_id: int, name: str, db: Session):
        """Generates a raw key for the user and stores the hash in the DB."""
        raw_key = f"cs_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_key(raw_key)
        
        new_key = ApiKey(
            user_id=user_id,
            key_hash=key_hash,
            name=name
        )
        db.add(new_key)
        db.commit()
        db.refresh(new_key)
        
        return raw_key, new_key

    def validate_key(self, raw_key: str, db: Session):
        """Checks if a raw key is valid, active, and within rate limits."""
        key_hash = self._hash_key(raw_key)
        key_record = db.query(ApiKey).filter(ApiKey.key_hash == key_hash, ApiKey.is_active == True).first()
        
        if key_record:
            # Check for daily reset
            now = datetime.now(timezone.utc)
            if key_record.last_reset:
                # Ensure last_reset is offset-aware for comparison if it comes from DB without it
                last_reset = key_record.last_reset.replace(tzinfo=timezone.utc) if not key_record.last_reset.tzinfo else key_record.last_reset
                if now - last_reset > timedelta(days=1):
                    key_record.uses_count = 0
                    key_record.last_reset = now
            
            if key_record.uses_count >= key_record.rate_limit:
                return "RATE_LIMITED"

            key_record.uses_count += 1
            db.commit()
            return key_record
        return None

    def get_user_keys(self, user_id: int, db: Session):
        return db.query(ApiKey).filter(ApiKey.user_id == user_id).all()

    def revoke_key(self, key_id: int, user_id: int, db: Session):
        key = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == user_id).first()
        if key:
            key.is_active = False
            db.commit()
            return True
        return False

    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()

api_key_service = ApiKeyService()
