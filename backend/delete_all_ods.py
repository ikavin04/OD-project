#!/usr/bin/env python3
"""
Delete ALL OD requests from the database
"""
from main import app, db, ODRequest

def delete_all_od_requests():
    with app.app_context():
        print("=== Deleting ALL OD Requests ===")
        
        # Get all OD requests
        all_requests = ODRequest.query.all()
        
        if not all_requests:
            print("❌ No OD requests found in database")
            return
        
        print(f"📊 Found {len(all_requests)} OD requests")
        
        # List all requests before deletion
        for req in all_requests:
            print(f"  - ID: {req.id}, Student: {req.student_id}, Event: {req.event_name}, Status: {req.status}")
        
        print(f"\n🗑️  Deleting all {len(all_requests)} OD requests...")
        
        # Delete all requests
        deleted_count = 0
        for req in all_requests:
            try:
                db.session.delete(req)
                deleted_count += 1
                print(f"  ✅ Deleted OD Request ID: {req.id} ({req.event_name})")
            except Exception as e:
                print(f"  ❌ Failed to delete OD Request ID: {req.id} - Error: {e}")
        
        # Commit the changes
        try:
            db.session.commit()
            print(f"\n✅ Successfully deleted {deleted_count} OD requests")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Failed to commit deletion: {e}")
        
        # Verify deletion
        remaining_requests = ODRequest.query.all()
        print(f"📊 Remaining OD requests in database: {len(remaining_requests)}")
        
        if len(remaining_requests) == 0:
            print("✅ Database is now clean - no OD requests remaining")

if __name__ == "__main__":
    delete_all_od_requests()