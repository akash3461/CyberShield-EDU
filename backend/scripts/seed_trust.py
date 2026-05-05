import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime

# Add the app directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, engine, Base
from app.models.schema import VerifiedProvider

def seed_trusted_entities():
    db: Session = SessionLocal()
    
    trusted_list = [
        {
            "name": "LinkedIn Career Portal",
            "official_url": "linkedin.com",
            "category": "career_portal",
            "security_tips": "LinkedIn is a verified partner. Always ensure you are on the official linkedin.com domain before entering credentials."
        },
        {
            "name": "Lever ATS System",
            "official_url": "lever.co",
            "category": "ats_system",
            "security_tips": "Lever is a high-trust Application Tracking System used by major tech firms. Verified for institutional safety."
        },
        {
            "name": "Greenhouse Software",
            "official_url": "greenhouse.io",
            "category": "ats_system",
            "security_tips": "Greenhouse is a verified institutional hiring platform. High signal integrity."
        },
        {
            "name": "Indeed Job Search",
            "official_url": "indeed.com",
            "category": "career_portal",
            "security_tips": "Indeed is a verified partner. Look for the Indeed 'Verified' badge on individual job postings as well."
        },
        {
            "name": "Handshake (University Partner)",
            "official_url": "joinhandshake.com",
            "category": "university_partner",
            "security_tips": "Official university career partner. Highly trusted for student internships."
        },
        {
            "name": "Glassdoor Reviews",
            "official_url": "glassdoor.com",
            "category": "career_portal",
            "security_tips": "Verified source for company reviews and job listings."
        }
    ]

    try:
        for entry in trusted_list:
            # Check if exists
            exists = db.query(VerifiedProvider).filter(VerifiedProvider.official_url == entry["official_url"]).first()
            if not exists:
                new_provider = VerifiedProvider(
                    name=entry["name"],
                    official_url=entry["official_url"],
                    category=entry["category"],
                    security_tips=entry["security_tips"]
                )
                db.add(new_provider)
                print(f"SEED: Adding {entry['name']} to Shield of Trust")
        
        db.commit()
        print("\nSHIELD OF TRUST: Seeding Complete. 🧪🛡️")
    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_trusted_entities()
