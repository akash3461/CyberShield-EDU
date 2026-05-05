from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root@127.0.0.1/cybershield")

engine = create_engine(DATABASE_URL)

def fix_schema():
    print(f"Connecting to database: {DATABASE_URL}")
    with engine.connect() as conn:
        # Check users table columns
        result = conn.execute(text("SHOW COLUMNS FROM users"))
        columns = [row[0] for row in result]
        print(f"Current columns in 'users': {columns}")
        
        # Add missing columns
        if 'xp' not in columns:
            print("Adding 'xp' column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN xp INT DEFAULT 0"))
        
        if 'level' not in columns:
            print("Adding 'level' column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN level INT DEFAULT 1"))
            
        if 'badges' not in columns:
            print("Adding 'badges' column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN badges JSON"))
        
        conn.commit()
        print("Schema update complete.")

if __name__ == "__main__":
    try:
        fix_schema()
    except Exception as e:
        print(f"Error fixing schema: {e}")
