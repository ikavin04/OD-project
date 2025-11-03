#!/usr/bin/env python3
"""
Test creating an OD request to reproduce the 500 error
"""
from main import app, db, ODRequest, Student
from werkzeug.datastructures import FileStorage
import io

def test_od_creation():
    with app.app_context():
        print("🧪 Testing OD Request Creation...")
        
        # Get a student
        student = Student.query.first()
        if not student:
            print("❌ No students found")
            return
        
        print(f"👤 Using student: {student.name} (ID: {student.id})")
        
        # Create a test file
        test_file_content = b"Test file content for OD application"
        test_file = FileStorage(
            stream=io.BytesIO(test_file_content),
            filename="test_application.pdf",
            content_type="application/pdf"
        )
        
        # Test the save_file_to_database function
        from main import save_file_to_database
        
        print("🔄 Testing file save to database...")
        try:
            file_info = save_file_to_database(test_file)
            if file_info:
                print("✅ File save successful")
                print(f"   - Filename: {file_info['filename']}")
                print(f"   - Size: {file_info['file_size']} bytes")
                print(f"   - Hash: {file_info['file_hash']}")
            else:
                print("❌ File save failed")
                return
        except Exception as e:
            print(f"❌ File save error: {e}")
            return
        
        # Test creating ODRequest object
        print("🔄 Testing ODRequest creation...")
        try:
            from datetime import date
            from app.models.enums import ODType
            
            od_request = ODRequest(
                student_id=student.id,
                event_name="Test Event",
                event_description="Test Description",
                from_date=date(2025, 11, 5),
                to_date=date(2025, 11, 6),
                od_type=ODType.INTER_COLLEGE_COIMBATORE,
                host_institution="Test Institution",
                venue="Test Venue",
                location_type="within_state",
                application_filename=file_info['filename'],
                application_original_name=file_info['original_name'],
                application_file_path=f"database://{file_info['filename']}",  # Indicate database storage
                application_file_data=file_info['file_data'],
                application_file_size=file_info['file_size'],
                application_mime_type=file_info['mime_type'],
                application_file_hash=file_info['file_hash']
            )
            
            print("✅ ODRequest object created successfully")
            
            # Test saving to database
            print("🔄 Testing database save...")
            db.session.add(od_request)
            db.session.commit()
            
            print(f"✅ ODRequest saved successfully with ID: {od_request.id}")
            
            # Test to_dict method
            print("🔄 Testing to_dict method...")
            result = od_request.to_dict()
            print("✅ to_dict method successful")
            
            # Clean up
            db.session.delete(od_request)
            db.session.commit()
            print("🧹 Test data cleaned up")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ ODRequest creation error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_od_creation()