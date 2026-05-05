from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.schema import QuizQuestion
from app.utils.auth import get_current_user
from app.utils.gamification import gamification_service
from pydantic import BaseModel
import random

router = APIRouter()

class QuizItem(BaseModel):
    id: int
    content: str
    content_type: str
    is_scam: bool
    explanation: str

    class Config:
        orm_mode = True

@router.get("/questions", response_model=List[QuizItem])
async def get_quiz_questions(limit: int = 5, db: Session = Depends(get_db)):
    """
    Get a random set of quiz questions from the forensic library.
    """
    questions = db.query(QuizQuestion).all()
    
    if not questions:
        raise HTTPException(
            status_code=404, 
            detail="Forensic library is empty. Please run the seed script: backend/scripts/seed_quiz.py"
        )

    # Randomize and limit
    return random.sample(questions, min(len(questions), limit))

@router.post("/submit")
async def submit_quiz(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Awards XP for completing a quiz.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Award 50 XP for completion
    user_id = current_user.get("id")
    if not user_id:
        # Fallback to lookup by username if id is missing in token
        from app.models.schema import User
        user = db.query(User).filter(User.username == current_user.get("sub")).first()
        if user:
            user_id = user.id

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    gamification_service.award_xp(db, user_id, 50)
    
    return {"message": "Quiz completed, XP awarded!", "xp_gained": 50}
