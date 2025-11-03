#!/usr/bin/env python3
"""
Delete all OD requests for a specific student ID
"""
from main import app, db, ODRequest

def delete_student_od_requests(student_id):
    with app.app_context():
        print(f"=== Deleting OD Requests for Student ID: {student_id} ===")
        
        # Find all OD requests for this student
        od_requests = ODRequest.query.filter_by(student_id=student_id).all()
        
        if not od_requests:
            print(f"❌ No OD requests found for student ID {student_id}")
            return
        
        print(f"📊 Found {len(od_requests)} OD requests for student ID {student_id}")
        
        # List all requests before deletion
        for od_request in od_requests:
            print(f"  - ID: {od_request.id}, Event: {od_request.event_name}, Status: {od_request.status}")
        
        # Confirm deletion
        print(f"\n🗑️  Deleting {len(od_requests)} OD requests...")
        
        # Delete all requests
        deleted_count = 0
        for od_request in od_requests:
            try:
                db.session.delete(od_request)
                deleted_count += 1
                print(f"  ✅ Deleted OD Request ID: {od_request.id} ({od_request.event_name})")
            except Exception as e:
                print(f"  ❌ Failed to delete OD Request ID: {od_request.id} - Error: {e}")
        
        # Commit the changes
        try:
            db.session.commit()
            print(f"\n✅ Successfully deleted {deleted_count} OD requests for student ID {student_id}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Failed to commit deletion: {e}")
        
        # Verify deletion
        remaining_requests = ODRequest.query.filter_by(student_id=student_id).all()
        print(f"📊 Remaining OD requests for student ID {student_id}: {len(remaining_requests)}")

if __name__ == "__main__":
    # Delete all OD requests for student ID 14 (Kavin Test Student)
    delete_student_od_requests(14)