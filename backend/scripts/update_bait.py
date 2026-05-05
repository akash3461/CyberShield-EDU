import sys
import os
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.database import SessionLocal
from backend.app.models.schema import ThreatPattern

def update_bait_patterns():
    db = SessionLocal()
    try:
        bait_patterns = [
            # Keywords (Weighted heavier to catch 'Free-iNTERSHIP')
            ("internship", "keyword", 0.4, "Common student bait keyword"),
            ("intership", "keyword", 0.5, "Typosquatted variation of internship"),
            ("scholarship", "keyword", 0.4, "Financial aid bait"),
            ("free", "keyword", 0.2, "Urgency/Bait keyword"),
            ("offer", "keyword", 0.2, "Incentive bait"),
            ("win", "keyword", 0.3, "Sweepstakes bait"),
            ("prize", "keyword", 0.3, "Sweepstakes bait"),
            ("login", "keyword", 0.2, "Credential harvesting indicator"),
            ("fINDs", "keyword", 0.4, "Suspicious path keyword identified in testing")
        ]

        for val, ptype, risk, desc in bait_patterns:
            # Check if exists
            exists = db.query(ThreatPattern).filter(
                ThreatPattern.value == val, 
                ThreatPattern.pattern_type == ptype
            ).first()
            
            if not exists:
                new_p = ThreatPattern(
                    value=val,
                    pattern_type=ptype,
                    risk_score=risk,
                    description=desc,
                    is_active=True
                )
                db.add(new_p)
                print(f"Added pattern: {val}")
        
        db.commit()
        print("✅ Bait patterns successfully updated in database.")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_bait_patterns()
