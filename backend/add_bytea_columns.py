#!/usr/bin/env python3
"""
Add missing BYTEA columns for complete database storage
"""
from main import app, db
from sqlalchemy import text

def add_missing_bytea_columns():
    with app.app_context():
        print("🔄 Adding missing BYTEA columns for complete database storage...")
        
        try:
            # Check if columns already exist
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'od_requests' 
                AND column_name IN ('application_file_data', 'attendance_proof_file_data', 'certificate_file_data')
                ORDER BY column_name;
            """))
            
            existing_columns = [row[0] for row in result]
            print(f"📊 Existing BYTEA columns: {existing_columns}")
            
            # Add application_file_data if missing
            if 'application_file_data' not in existing_columns:
                print("➕ Adding application_file_data column...")
                db.session.execute(text("ALTER TABLE od_requests ADD COLUMN application_file_data BYTEA;"))
                print("✅ Added application_file_data column")
            else:
                print("✅ application_file_data column already exists")
            
            # Add attendance_proof_file_data if missing
            if 'attendance_proof_file_data' not in existing_columns:
                print("➕ Adding attendance_proof_file_data column...")
                db.session.execute(text("ALTER TABLE od_requests ADD COLUMN attendance_proof_file_data BYTEA;"))
                print("✅ Added attendance_proof_file_data column")
            else:
                print("✅ attendance_proof_file_data column already exists")
            
            # Add certificate_file_data if missing
            if 'certificate_file_data' not in existing_columns:
                print("➕ Adding certificate_file_data column...")
                db.session.execute(text("ALTER TABLE od_requests ADD COLUMN certificate_file_data BYTEA;"))
                print("✅ Added certificate_file_data column")
            else:
                print("✅ certificate_file_data column already exists")
            
            # Commit the changes
            db.session.commit()
            print("✅ Database schema updated successfully")
            
            # Verify the columns were added
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'od_requests' 
                AND column_name LIKE '%file_data'
                ORDER BY column_name;
            """))
            
            final_columns = [row[0] for row in result]
            print(f"📊 Final BYTEA columns: {final_columns}")
            
            if len(final_columns) == 3:
                print("🎉 All BYTEA columns are now present!")
            else:
                print("⚠️  Some columns may be missing")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding columns: {e}")
            raise

if __name__ == "__main__":
    add_missing_bytea_columns()