from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import get_current_user
from app.utils.gamification import gamification_service
from pydantic import BaseModel

router = APIRouter()

class RewardRequest(BaseModel):
    xp_amount: int
    reason: str

@router.post("/reward")
async def award_educational_xp(
    request: RewardRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Awards educational XP for completing simulations and scenarios.
    Ensures XP is persisted to the database and synced with user profile.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Identity Resolution
    user_id = current_user.get("id")
    if not user_id:
        # Fallback to lookup by username if id is missing in token
        from app.models.schema import User
        user = db.query(User).filter(User.username == current_user.get("sub")).first()
        if user:
            user_id = user.id

    if not user_id:
        raise HTTPException(status_code=404, detail="User account not found")

    # Reward Security: Limit maximum reward per call to prevent abuse
    if request.xp_amount > 150:
        raise HTTPException(status_code=400, detail="Reward amount exceeds forensic ceiling")

    # Apply Reward
    try:
        result = gamification_service.award_xp(db, user_id, request.xp_amount)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to award XP in the database")
            
        return {
            "status": "success",
            "xp_gained": request.xp_amount,
            "total_xp": result.get("total_xp"),
            "current_level": result.get("current_level"),
            "reason": request.reason
        }
    except Exception as e:
        logger.error(f"Reward Execution Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal reward failure: {str(e)}")
