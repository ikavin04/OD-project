"""
Update faculty account to match login page
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app, db, Faculty

def update_faculty():
    with app.app_context():
        # Get existing faculty
        faculty = Faculty.query.filter_by(employee_id='FAC001').first()
        
        if not faculty:
            print("❌ Faculty not found")
            return
        
        # Update email and name to match login page
        faculty.email = 'dr.rajesh@kgkite.ac.in'
        faculty.name = 'Dr. Rajesh Kumar'
        faculty.set_password('Faculty@123')
        
        try:
            db.session.commit()
            print("✅ Faculty account updated successfully")
            print(f"   Email: {faculty.email}")
            print(f"   Name: {faculty.name}")
            print(f"   Password: Faculty@123")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_faculty()
