"""
Quick setup to ensure test account exists
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app, db, Student

def ensure_test_account():
    with app.app_context():
        students_to_create = [
            {
                'roll_number': '24UCS153',
                'email': '24ucs153kavin@kgkite.ac.in',
                'name': 'Kavin Test Student',
                'department': 'Computer Science and Engineering',
                'year': 2,
                'semester': 3,
                'phone_number': '9876543210',
                'password': 'Kgkite@1234'
            },
            {
                'roll_number': '24UCS158',
                'email': '24ucs158manisha@kgkite.ac.in',
                'name': 'Manisha',
                'department': 'Computer Science and Engineering',
                'year': 2,
                'semester': 3,
                'phone_number': '9876543211',
                'password': 'Kgkite@1234'
            }
        ]
        
        for student_data in students_to_create:
            # Check if student already exists
            existing_student = Student.query.filter_by(email=student_data['email']).first()
            if existing_student:
                print(f"[OK] Student {student_data['roll_number']} ({student_data['name']}) already exists")
                continue
            
            # Create student
            student = Student(
                roll_number=student_data['roll_number'],
                email=student_data['email'],
                name=student_data['name'],
                department=student_data['department'],
                year=student_data['year'],
                semester=student_data['semester'],
                phone_number=student_data['phone_number']
            )
            student.set_password(student_data['password'])
            
            try:
                db.session.add(student)
                db.session.commit()
                print(f"[OK] Student {student_data['roll_number']} ({student_data['name']}) created successfully")
            except Exception as e:
                db.session.rollback()
                print(f"[ERROR] Error creating {student_data['roll_number']}: {str(e)}")

if __name__ == "__main__":
    ensure_test_account()