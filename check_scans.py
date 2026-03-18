import sys
import os
import json

# Add backend to path relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(script_dir, 'backend')
sys.path.append(backend_dir)

from app.database import SessionLocal
from app.models.schema import ScanRecord, User

db = SessionLocal()
try:
    print("--- Users ---")
    users = db.query(User).all()
    for u in users:
        print(f"ID: {u.id}, Username: {u.username}, Role: {u.role}")
    
    print("\n--- Scans ---")
    scans = db.query(ScanRecord).all()
    print(f"Total scans: {len(scans)}")
    for s in scans:
        # Avoid printing huge input_data
        preview = (s.input_data[:50] + '...') if len(s.input_data) > 50 else s.input_data
        print(f"ID: {s.id}, UserID: {s.user_id}, Type: {s.scan_type}, Result: {s.prediction}, Data: {preview}")
finally:
    db.close()
