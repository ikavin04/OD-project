import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import app, db
from datetime import datetime

# Campus-Scale Database Optimizations

with app.app_context():
    print("🏫 Setting up Campus-Scale Database Optimizations...")
    
    # Create database indexes for better performance
    index_queries = [
        # Student indexes
        "CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);",
        "CREATE INDEX IF NOT EXISTS idx_students_roll_number ON students(roll_number);",
        "CREATE INDEX IF NOT EXISTS idx_students_department ON students(department);",
        "CREATE INDEX IF NOT EXISTS idx_students_active ON students(is_active);",
        
        # OD Request indexes
        "CREATE INDEX IF NOT EXISTS idx_od_requests_student_id ON od_requests(student_id);",
        "CREATE INDEX IF NOT EXISTS idx_od_requests_status ON od_requests(status);",
        "CREATE INDEX IF NOT EXISTS idx_od_requests_created_at ON od_requests(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_od_requests_from_date ON od_requests(from_date);",
        "CREATE INDEX IF NOT EXISTS idx_od_requests_faculty_id ON od_requests(faculty_id);",
        
        # Faculty indexes
        "CREATE INDEX IF NOT EXISTS idx_faculty_email ON faculty(email);",
        "CREATE INDEX IF NOT EXISTS idx_faculty_department ON faculty(department);",
        "CREATE INDEX IF NOT EXISTS idx_faculty_role ON faculty(role);",
        
        # File hash index for deduplication
        "CREATE INDEX IF NOT EXISTS idx_od_requests_file_hash ON od_requests(application_file_hash);",
        
        # Composite indexes for common queries
        "CREATE INDEX IF NOT EXISTS idx_od_requests_student_status ON od_requests(student_id, status);",
        "CREATE INDEX IF NOT EXISTS idx_od_requests_status_created ON od_requests(status, created_at);",
    ]
    
    for query in index_queries:
        try:
            db.session.execute(query)
            print(f"✅ {query.split()[5]}")  # Extract index name
        except Exception as e:
            print(f"❌ Failed to create index: {e}")
    
    db.session.commit()
    print("\n🚀 Database optimized for campus-scale usage!")
    
    # Add database connection pooling settings info
    print("\n📊 Recommended PostgreSQL Settings for Campus:")
    print("max_connections = 200")
    print("shared_buffers = 256MB")
    print("effective_cache_size = 1GB")
    print("work_mem = 4MB")
    print("maintenance_work_mem = 64MB")
    print("checkpoint_completion_target = 0.9")
    print("wal_buffers = 16MB")
    print("default_statistics_target = 100")