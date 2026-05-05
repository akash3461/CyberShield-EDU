from sqlalchemy.orm import Session
from app.models.schema import User, ScanRecord
from app.utils.logger import logger

class GamificationService:
    def award_xp(self, db: Session, user_id: int, amount: int):
        """
        Awards XP to a user and handles leveling up.
        """
        if not user_id:
            return
            
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return
                
            user.xp += amount
            # Level Calculation: floor(XP / 100) + 1
            new_level = (user.xp // 100) + 1
            
            if new_level > user.level:
                logger.info(f"User {user.username} leveled up to {new_level}!")
                user.level = new_level
                
            db.commit()
            
            # Milestone check
            new_badges = self.check_milestones(db, user_id)
            
            return {
                "xp_gained": amount,
                "total_xp": user.xp,
                "current_level": user.level,
                "rank": self.get_rank_title(user.level),
                "new_badges": new_badges
            }
        except Exception as e:
            logger.error(f"Error awarding XP: {str(e)}")
            db.rollback()
            return None

    def get_rank_title(self, level: int) -> str:
        """Pillar 6: Rank Hierarchy"""
        if level <= 2: return "Cyber Scout"
        if level <= 5: return "Forensic Guardian"
        if level <= 10: return "Cyber Sentinel"
        return "Grand Protector"

    def check_milestones(self, db: Session, user_id: int) -> list:
        user = db.query(User).filter(User.id == user_id).first()
        if not user: return []

        earned_now = []
        
        # 📊 Milestone 1: First Response
        count_all = db.query(ScanRecord).filter(ScanRecord.user_id == user_id).count()
        if count_all >= 1 and "First Response" not in user.badges:
            if self.award_badge(db, user_id, "First Response"):
                earned_now.append("First Response")

        # Phishing Hunter (10 URL)
        count_url = db.query(ScanRecord).filter(ScanRecord.user_id == user_id, ScanRecord.scan_type == "url").count()
        if count_url >= 10 and "Phishing Hunter" not in user.badges:
            if self.award_badge(db, user_id, "Phishing Hunter"):
                earned_now.append("Phishing Hunter")

        return earned_now

    def award_badge(self, db: Session, user_id: int, badge_name: str):
        """
        Awards a badge to a user if they don't already have it.
        """
        if not user_id:
            return
            
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.badges:
                # Initialize empty badges if None
                if user and user.badges is None:
                    user.badges = []
                
            if user and badge_name not in user.badges:
                current_badges = list(user.badges)
                current_badges.append(badge_name)
                user.badges = current_badges
                db.commit()
                logger.info(f"User {user.username} earned badge: {badge_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error awarding badge: {str(e)}")
            db.rollback()
            return False

gamification_service = GamificationService()
