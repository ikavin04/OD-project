"""
Quick setup to ensure test account exists
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app, db, Student

def ensure_test_account():
    with app.app_context():
        # Check if student already exists
        existing_student = Student.query.filter_by(email='24ucs153kavin@kgkite.ac.in').first()
        if existing_student:
            print("✅ Test student exists")
            return
        
        # Create test student
        student = Student(
            roll_number='24UCS153',
            email='24ucs153kavin@kgkite.ac.in',
            name='Kavin Test Student',
            department='Computer Science and Engineering',
            year=2,
            semester=3,
            phone_number='9876543210'
        )
        student.set_password('Kgkite@1234')
        
        try:
            db.session.add(student)
            db.session.commit()
            print("✅ Test student created")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    ensure_test_account()