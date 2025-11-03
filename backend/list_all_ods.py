#!/usr/bin/env python3
"""
List all OD requests in the database
"""
from main import app, db, ODRequest

def list_all_od_requests():
    with app.app_context():
        print("=== All OD Requests in Database ===")
        
        # Get all OD requests
        all_requests = ODRequest.query.all()
        
        if not all_requests:
            print("❌ No OD requests found in database")
            return
        
        print(f"📊 Total OD requests: {len(all_requests)}")
        print()
        
        # Group by student ID
        student_requests = {}
        for req in all_requests:
            if req.student_id not in student_requests:
                student_requests[req.student_id] = []
            student_requests[req.student_id].append(req)
        
        # Display by student
        for student_id, requests in student_requests.items():
            print(f"👤 Student ID: {student_id} ({len(requests)} requests)")
            for req in requests:
                print(f"   - ID: {req.id}, Event: {req.event_name}, Status: {req.status}, Proof Status: {req.proof_submission_status}")
            print()

if __name__ == "__main__":
    list_all_od_requests()