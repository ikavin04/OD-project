"""
Database Migration Script - Move files from filesystem to PostgreSQL
This script will migrate existing file storage from filesystem to database BYTEA fields
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import app, db, ODRequest
from sqlalchemy import text

def migrate_files_to_database():
    """Migrate all existing files from filesystem to PostgreSQL"""
    
    with app.app_context():
        print("🔄 Starting file migration from filesystem to PostgreSQL...")
        
        # First, let's add the new columns if they don't exist
        try:
            # Check if columns exist, if not add them
            db.session.execute(text("""
                ALTER TABLE od_requests 
                ADD COLUMN IF NOT EXISTS application_file_data BYTEA,
                ADD COLUMN IF NOT EXISTS attendance_proof_file_data BYTEA,
                ADD COLUMN IF NOT EXISTS certificate_file_data BYTEA;
            """))
            db.session.commit()
            print("✅ Database schema updated with BYTEA columns")
        except Exception as e:
            print(f"Schema update error (might already exist): {e}")
            db.session.rollback()
        
        # Get all OD requests
        od_requests = ODRequest.query.all()
        print(f"📊 Found {len(od_requests)} OD requests to migrate")
        
        migrated_count = 0
        error_count = 0
        
        for od_request in od_requests:
            try:
                # Migrate application file
                if hasattr(od_request, 'application_file_path') and od_request.application_file_path:
                    if os.path.exists(od_request.application_file_path):
                        with open(od_request.application_file_path, 'rb') as f:
                            od_request.application_file_data = f.read()
                        print(f"✅ Migrated application file for OD {od_request.id}")
                    else:
                        print(f"⚠️ Application file not found: {od_request.application_file_path}")
                
                # Migrate attendance proof file
                if hasattr(od_request, 'attendance_proof_file_path') and od_request.attendance_proof_file_path:
                    if os.path.exists(od_request.attendance_proof_file_path):
                        with open(od_request.attendance_proof_file_path, 'rb') as f:
                            od_request.attendance_proof_file_data = f.read()
                        print(f"✅ Migrated attendance proof for OD {od_request.id}")
                
                # Migrate certificate file
                if hasattr(od_request, 'certificate_file_path') and od_request.certificate_file_path:
                    if os.path.exists(od_request.certificate_file_path):
                        with open(od_request.certificate_file_path, 'rb') as f:
                            od_request.certificate_file_data = f.read()
                        print(f"✅ Migrated certificate for OD {od_request.id}")
                
                migrated_count += 1
                
            except Exception as e:
                print(f"❌ Error migrating OD {od_request.id}: {e}")
                error_count += 1
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n🎉 Migration completed!")
            print(f"✅ Successfully migrated: {migrated_count} OD requests")
            print(f"❌ Errors: {error_count}")
            
            # Show storage info
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total_requests,
                    COUNT(application_file_data) as app_files,
                    COUNT(attendance_proof_file_data) as attendance_files,
                    COUNT(certificate_file_data) as certificate_files,
                    pg_size_pretty(SUM(LENGTH(application_file_data))) as app_size,
                    pg_size_pretty(SUM(LENGTH(attendance_proof_file_data))) as attendance_size,
                    pg_size_pretty(SUM(LENGTH(certificate_file_data))) as certificate_size
                FROM od_requests;
            """)).fetchone()
            
            print(f"\n📊 Database Storage Summary:")
            print(f"  Total OD Requests: {result[0]}")
            print(f"  Application Files: {result[1]} ({result[4] or '0 bytes'})")
            print(f"  Attendance Proofs: {result[2]} ({result[5] or '0 bytes'})")
            print(f"  Certificates: {result[3]} ({result[6] or '0 bytes'})")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Failed to commit changes: {e}")

if __name__ == "__main__":
    migrate_files_to_database()