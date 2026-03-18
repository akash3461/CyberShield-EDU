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
    Get a random set of quiz questions.
    """
    questions = db.query(QuizQuestion).all()
    
    # If no questions, seed some basic ones
    if not questions:
        seed_questions = [
            {
                "content": "URGENT: Your account will be locked in 1 hour. Click here to verify your identity: http://secure-login-bank.com/verify",
                "content_type": "text",
                "is_scam": True,
                "explanation": "This is a classic phishing attack. Banks never create artificial urgency or ask for sensitive verification via unencrypted links.",
                "difficulty": "easy"
            },
            {
                "content": "Hi! I saw your profile and thought we could chat. Here is my photo: [IMG_SCAN_442.jpg]",
                "content_type": "text",
                "is_scam": True,
                "explanation": "Random messages from strangers with suspicious attachments are often used to distribute malware or social engineering scams.",
                "difficulty": "easy"
            },
            {
                "content": "Your package is waiting for delivery. Please pay the $1.99 shipping fee at http://tracking-post.net",
                "content_type": "text",
                "is_scam": True,
                "explanation": "Smishing (SMS Phishing) often uses small fees to trick you into entering card details on a fake site.",
                "difficulty": "medium"
            },
            {
                "content": "Official University Notice: The library will be closed this Sunday for maintenance. No action required.",
                "content_type": "text",
                "is_scam": False,
                "explanation": "This is a generic informative message with no suspicious links, requests for data, or urgency.",
                "difficulty": "easy"
            },
            {
                "content": "Congratulations! You've been selected as a finalist for the Apple Scholarship. Apply here: http://apple-schlarships.edu.org",
                "content_type": "text",
                "is_scam": True,
                "explanation": "Notice the typo in the URL ('schlarships'). Scammers often use slightly misspelled domains to look official.",
                "difficulty": "medium"
            }
        ]
        for q in seed_questions:
            db_q = QuizQuestion(**q)
            db.add(db_q)
        db.commit()
        questions = db.query(QuizQuestion).all()

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
    gamification_service.award_xp(db, current_user.get("id"), 50)
    
    return {"message": "Quiz completed, XP awarded!", "xp_gained": 50}
