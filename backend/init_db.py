#!/usr/bin/env python3
"""
Database initialization script for OD Management System
Run this script to create the PostgreSQL database and tables with sample data.
"""

from app import create_app, db
from app.models import Student, Faculty, UserRole
from werkzeug.security import generate_password_hash
import os

def init_database():
    """Initialize database with tables and sample data"""
    
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Check if admin already exists
        existing_admin = Faculty.query.filter_by(email='admin@college.edu').first()
        if not existing_admin:
            # Create admin user
            admin = Faculty(
                employee_id='ADMIN001',
                email='admin@college.edu',
                name='System Administrator',
                department='Administration',
                role=UserRole.ADMIN,
                is_active=True
            )
            admin.set_password('Admin@2025!Secure')
            
            db.session.add(admin)
            print("✅ Admin user created!")
        else:
            print("⚠️  Admin user already exists")
        
        # Create sample faculty
        existing_faculty = Faculty.query.filter_by(email='faculty@college.edu').first()
        if not existing_faculty:
            faculty = Faculty(
                employee_id='FAC001',
                email='faculty@college.edu',
                name='Dr. John Smith',
                department='Computer Science',
                role=UserRole.FACULTY,
                is_active=True
            )
            faculty.set_password('Faculty@2025!Pass')
            
            db.session.add(faculty)
            print("✅ Sample faculty created!")
        else:
            print("⚠️  Sample faculty already exists")
        
        # Create sample HOD
        existing_hod = Faculty.query.filter_by(email='hod@college.edu').first()
        if not existing_hod:
            hod = Faculty(
                employee_id='HOD001',
                email='hod@college.edu',
                name='Dr. Jane Doe',
                department='Computer Science',
                role=UserRole.HOD,
                is_active=True
            )
            hod.set_password('HOD@2025!Secure')
            
            db.session.add(hod)
            print("✅ Sample HOD created!")
        else:
            print("⚠️  Sample HOD already exists")
        
        # Create sample student
        existing_student = Student.query.filter_by(email='student@college.edu').first()
        if not existing_student:
            student = Student(
                roll_number='CS2021001',
                email='student@college.edu',
                name='Alice Johnson',
                department='Computer Science',
                year=3,
                semester=5,
                phone_number='1234567890',
                is_active=True
            )
            student.set_password('Student@2025!Pass')
            
            db.session.add(student)
            print("✅ Sample student created!")
        else:
            print("⚠️  Sample student already exists")
        
        try:
            db.session.commit()
            print("\n🎉 Database initialization completed successfully!")
            print("\n📋 Default Login Credentials:")
            print("=" * 50)
            print("Admin:")
            print("  Email: admin@college.edu")
            print("  Password: Admin@2025!Secure")
            print("\nFaculty:")
            print("  Email: faculty@college.edu")
            print("  Password: Faculty@2025!Pass")
            print("\nHOD:")
            print("  Email: hod@college.edu")
            print("  Password: HOD@2025!Secure")
            print("\nStudent:")
            print("  Email: student@college.edu")
            print("  Roll Number: CS2021001")
            print("  Password: Student@2025!Pass")
            print("=" * 50)
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during database commit: {e}")
            return False
    
    return True

if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    if init_database():
        print("\n✅ Ready to start the Flask application!")
        print("Run: python run.py")
    else:
        print("\n❌ Database initialization failed!")
        exit(1)