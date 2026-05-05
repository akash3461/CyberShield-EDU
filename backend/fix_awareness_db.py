import sys
import os
import json

# Add the backend directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models.schema import AwarenessContent

def fix_schema_and_seed():
    db = SessionLocal()
    try:
        print("Checking awareness_content table schema...")
        # Check if columns exist
        with engine.connect() as conn:
            result = conn.execute(text("SHOW COLUMNS FROM awareness_content"))
            columns = [row[0] for row in result]
            
            if 'path_id' not in columns:
                print("Adding 'path_id' column...")
                conn.execute(text("ALTER TABLE awareness_content ADD COLUMN path_id VARCHAR(50) NULL"))
            
            if 'path_order' not in columns:
                print("Adding 'path_order' column...")
                conn.execute(text("ALTER TABLE awareness_content ADD COLUMN path_order INT DEFAULT 0"))
            
            conn.commit()
            print("Schema check/update completed.")

        # Seed data if empty
        count = db.query(AwarenessContent).count()
        if count == 0:
            print("Seeding awareness_content with initial data...")
            
            # Load from resources if possible
            resources_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'educational_resources.json')
            if os.path.exists(resources_path):
                with open(resources_path, 'r') as f:
                    data = json.load(f)
                
                # Create modules from scam_types
                for idx, scam in enumerate(data.get('scam_types', [])):
                    module = AwarenessContent(
                        category="Threat Type",
                        title=scam['type'],
                        description=f"Detailed guide on identifying {scam['type']}.",
                        difficulty="Beginner",
                        link="#",
                        examples=json.dumps(scam['red_flags']),
                        path_id=f"scam-{idx}",
                        path_order=idx
                    )
                    db.add(module)
                
                # Create modules from quick_tips
                for idx, tip in enumerate(data.get('quick_tips', [])):
                    module = AwarenessContent(
                        category="Pro Tip",
                        title=tip['title'],
                        description=tip['content'],
                        difficulty="Easy",
                        link="#",
                        examples=json.dumps(["Look for official domains", "Never pay upfront"]),
                        path_id=f"tip-{idx}",
                        path_order=idx + 10
                    )
                    db.add(module)
                
                db.commit()
                print(f"Successfully seeded {len(data.get('scam_types', [])) + len(data.get('quick_tips', []))} modules.")
            else:
                print(f"Resources file not found at {resources_path}")
        else:
            print(f"Table already has {count} entries. Skipping seeding.")

    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_schema_and_seed()
