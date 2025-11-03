#!/usr/bin/env python3
"""
Make application_file_path nullable for database storage
"""
from main import app, db
from sqlalchemy import text

def make_file_path_nullable():
    with app.app_context():
        print("🔄 Making file path columns nullable for database storage...")
        
        try:
            # Make application_file_path nullable
            print("➕ Altering application_file_path to be nullable...")
            db.session.execute(text("ALTER TABLE od_requests ALTER COLUMN application_file_path DROP NOT NULL;"))
            print("✅ application_file_path is now nullable")
            
            # Commit the changes
            db.session.commit()
            print("✅ Database schema updated successfully")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            # This might fail if already nullable, which is fine
            print("Note: Column might already be nullable")

if __name__ == "__main__":
    make_file_path_nullable()