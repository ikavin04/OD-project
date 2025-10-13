#!/usr/bin/env python3
"""
Database migration script to add proof submission deadline fields
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def add_deadline_columns():
    """Add deadline tracking columns to od_requests table"""
    app = create_app()
    
    with app.app_context():
        try:
            # For SQLite/PostgreSQL compatibility, use SQLAlchemy inspector
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('od_requests')]
            
            if 'attendance_proof_deadline' not in columns:
                print("Adding attendance_proof_deadline column...")
                db.session.execute(text(
                    "ALTER TABLE od_requests ADD COLUMN attendance_proof_deadline TIMESTAMP"
                ))
                
            if 'certificate_submission_deadline' not in columns:
                print("Adding certificate_submission_deadline column...")
                db.session.execute(text(
                    "ALTER TABLE od_requests ADD COLUMN certificate_submission_deadline TIMESTAMP"
                ))
            
            db.session.commit()
            print("✓ Database migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {str(e)}")
            return False
            
    return True

if __name__ == "__main__":
    print("Running database migration...")
    success = add_deadline_columns()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)