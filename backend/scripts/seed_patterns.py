import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from datetime import datetime

# Add project root and backend folder to sys.path to handle nested imports
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
project_root = os.path.dirname(backend_dir)

sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

from backend.app.models.schema import ThreatPattern
from backend.app.config import settings

def seed_patterns():
    # Use the database URL from settings
    engine = create_engine(settings.DATABASE_URL)
    session = Session(engine)

    patterns = [
        # 1. High-Risk TLDs (Heuristics 2.0)
        {"type": "tld", "value": ".top", "score": 0.4, "desc": "High-risk TLD often used for fleeting phishing infrastructure"},
        {"type": "tld", "value": ".xyz", "score": 0.3, "desc": "Commonly abused TLD for bulk spam and malicious redirects"},
        {"type": "tld", "value": ".pw", "score": 0.5, "desc": "TLD frequently associated with botnets and phishing"},
        {"type": "tld", "value": ".zip", "score": 0.6, "desc": "Deceptive TLD that mimics a file extension"},
        {"type": "tld", "value": ".click", "score": 0.4, "desc": "Common in low-quality ad-tracking and phishing"},
        
        # 2. Suspicious URL Keywords
        {"type": "keyword", "value": "secure-login-portal", "score": 0.7, "desc": "Commonly used in spoofed university login pages"},
        {"type": "keyword", "value": "verify-account-now", "score": 0.6, "desc": "Urgent verification bait"},
        {"type": "keyword", "value": "office365-update", "score": 0.8, "desc": "Targeting student email credentials"},
        
        # 3. Text-Based Scam Patterns (Regex)
        {"type": "regex", "value": r"registration\s*fee|security\s*deposit", "score": 0.9, "desc": "Direct monetary request in an internship/scholarship context"},
        {"type": "regex", "value": r"whatsapp\s*only|contact\s*on\s*telegram", "score": 0.7, "desc": "Redirection to unmonitored chat platforms"},
        {"type": "regex", "value": r"earn\s*\$\d{3,}\s*per\s*day|passive\s*income", "score": 0.8, "desc": "Unrealistic financial promises for students"},
    ]

    print(f"Seeding {len(patterns)} patterns into '{settings.DATABASE_URL}'...")
    
    count = 0
    for p in patterns:
        # Check if already exists
        existing = session.query(ThreatPattern).filter_by(value=p["value"]).first()
        if not existing:
            new_pattern = ThreatPattern(
                pattern_type=p["type"],
                value=p["value"],
                risk_score=p["score"],
                description=p["desc"],
                is_active=True
            )
            session.add(new_pattern)
            count += 1
            
    session.commit()
    print(f"Successfully added {count} new patterns. Total patterns: {len(patterns)}")
    session.close()

if __name__ == "__main__":
    seed_patterns()
