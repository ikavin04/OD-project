"""
Database Initialization Script
Creates all database tables based on SQLAlchemy models
"""

from main import app, db

def init_database():
    """Initialize the database by creating all tables"""
    with app.app_context():
        try:
            # Drop all existing tables (WARNING: This will delete all data)
            print("🗑️  Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            print("📊 Creating database tables...")
            db.create_all()
            
            print("✅ Database initialized successfully!")
            print("\nTables created:")
            print("  - students")
            print("  - faculty")
            print("  - od_requests")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            raise

if __name__ == '__main__':
    init_database()
