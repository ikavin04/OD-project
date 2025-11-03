"""
Check faculty accounts in database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app, db, Faculty

def check_faculty():
    with app.app_context():
        faculties = Faculty.query.all()
        
        if not faculties:
            print("❌ No faculty accounts found in database")
            return
        
        print(f"✅ Found {len(faculties)} faculty account(s):")
        print("-" * 80)
        for faculty in faculties:
            print(f"ID: {faculty.id}")
            print(f"Employee ID: {faculty.employee_id}")
            print(f"Email: {faculty.email}")
            print(f"Name: {faculty.name}")
            print(f"Department: {faculty.department}")
            print(f"Role: {faculty.role.value}")
            print(f"Active: {faculty.is_active}")
            print("-" * 80)

if __name__ == "__main__":
    check_faculty()
