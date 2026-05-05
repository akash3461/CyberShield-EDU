import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import SessionLocal
from app.models.schema import AwarenessContent

db = SessionLocal()
try:
    contents = db.query(AwarenessContent).all()
    print(f"Total awareness content: {len(contents)}")
    for c in contents:
        # Manually construct dict if needed, or check attributes
        data = {
            "id": c.id,
            "category": c.category,
            "title": c.title,
            "description": c.description,
            "difficulty": c.difficulty,
            "link": c.link,
            "examples": c.examples
        }
        print(json.dumps(data, indent=2))
finally:
    db.close()
