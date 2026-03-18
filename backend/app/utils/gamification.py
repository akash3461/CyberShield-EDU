from sqlalchemy.orm import Session
from app.models.schema import User
from app.utils.logger import logger

class GamificationService:
    @staticmethod
    def award_xp(db: Session, user_id: int, amount: int):
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
                # Could add level-up logic here (e.g. badges)
                
            db.commit()
            return {
                "xp_gained": amount,
                "total_xp": user.xp,
                "current_level": user.level
            }
        except Exception as e:
            logger.error(f"Error awarding XP: {str(e)}")
            db.rollback()
            return None

    @staticmethod
    def award_badge(db: Session, user_id: int, badge_name: str):
        """
        Awards a badge to a user if they don't already have it.
        """
        if not user_id:
            return
            
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return
                
            if badge_name not in user.badges:
                # Need to handle JSON column properly
                current_badges = list(user.badges) if user.badges else []
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
