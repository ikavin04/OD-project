"""
Quick setup to ensure test faculty account exists
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app, db, Faculty, UserRole

def ensure_faculty_account():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if faculty already exists
        existing_faculty = Faculty.query.filter_by(email='dr.rajesh@kgkite.ac.in').first()
        if existing_faculty:
            print("✅ Test faculty exists")
            print(f"   Email: {existing_faculty.email}")
            print(f"   Name: {existing_faculty.name}")
            return
        
        # Create test faculty
        faculty = Faculty(
            employee_id='FAC001',
            email='dr.rajesh@kgkite.ac.in',
            name='Dr. Rajesh Kumar',
            department='Computer Science and Engineering',
            phone_number='9876543210',
            role=UserRole.FACULTY
        )
        faculty.set_password('Faculty@123')
        
        try:
            db.session.add(faculty)
            db.session.commit()
            print("✅ Test faculty created successfully")
            print(f"   Email: dr.rajesh@kgkite.ac.in")
            print(f"   Password: Faculty@123")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating faculty: {str(e)}")

if __name__ == "__main__":
    ensure_faculty_account()
