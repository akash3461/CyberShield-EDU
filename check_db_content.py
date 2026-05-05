import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import SessionLocal
from app.models.schema import AwarenessContent

db = SessionLocal()
try:
    contents = db.query(AwarenessContent).all()
    print(f"Total awareness content: {len(contents)}")
    for c in contents:
        print(f"ID: {c.id}, Title: {c.title}")
finally:
    db.close()
