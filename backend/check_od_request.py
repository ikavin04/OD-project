#!/usr/bin/env python3
from main import app, db, ODRequest, ODStatus, ProofStatus

def check_od_request():
    with app.app_context():
        print("=== Checking OD Request ===")
        
        # Check all OD requests
        requests = ODRequest.query.all()
        print(f"\nTotal OD Requests: {len(requests)}")
        
        for req in requests:
            print(f"\n--- OD Request ID: {req.id} ---")
            print(f"Event Name: {req.event_name}")
            print(f"Student ID: {req.student_id}")
            print(f"Status: {req.status}")
            print(f"Proof Submission Status: {req.proof_submission_status}")
            print(f"Attendance proof filename: {req.attendance_proof_filename}")
            print(f"Approved: {req.approved_at}")
            
        # Check specific request 15
        od_request = ODRequest.query.get(15)
        if od_request:
            print(f"\n=== OD Request 15 Details ===")
            print(f"ID: {od_request.id}")
            print(f"Event Name: {od_request.event_name}")
            print(f"Status: {od_request.status} (Expected: {ODStatus.APPROVED})")
            print(f"Student ID: {od_request.student_id}")
            print(f"Attendance proof filename: {od_request.attendance_proof_filename}")
            print(f"Proof submission status: {od_request.proof_submission_status}")
            print(f"Is Approved: {od_request.status == ODStatus.APPROVED}")
            print(f"Already has proof: {bool(od_request.attendance_proof_filename)}")
        else:
            print("\n❌ OD Request 15 not found")

if __name__ == "__main__":
    check_od_request()