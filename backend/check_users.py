import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import app, db, Student, Faculty
from datetime import datetime

with app.app_context():
    print("\n=== Checking Users in Database ===\n")
    
    # Get all students
    students = Student.query.all()
    print(f"📚 Students ({len(students)} found):")
    for student in students:
        print(f"  ID: {student.id}")
        print(f"  Name: {student.name}")
        print(f"  Email: {student.email}")
        print(f"  Roll Number: {student.roll_number}")
        print(f"  Department: {student.department}")
        print(f"  Active: {student.is_active}")
        print("  " + "="*50)
    
    print(f"\n👩‍🏫 Faculty ({Faculty.query.count()} found):")
    faculty = Faculty.query.all()
    for fac in faculty:
        print(f"  ID: {fac.id}")
        print(f"  Name: {fac.name}")
        print(f"  Email: {fac.email}")
        print(f"  Employee ID: {fac.employee_id}")
        print(f"  Role: {fac.role}")
        print(f"  Active: {fac.is_active}")
        print("  " + "="*50)