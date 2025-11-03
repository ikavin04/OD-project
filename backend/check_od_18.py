#!/usr/bin/env python3
"""
Check OD request 18 details to see attendance proof status
"""
from main import app, db, ODRequest

def check_od_18():
    with app.app_context():
        od = ODRequest.query.get(18)
        if od:
            print(f"=== OD Request 18 ===")
            print(f"Event: {od.event_name}")
            print(f"Status: {od.status}")
            print(f"Proof Status: {od.proof_submission_status}")
            print(f"Attendance proof filename: {od.attendance_proof_filename}")
            print(f"Attendance proof submitted at: {od.attendance_proof_submitted_at}")
            print(f"Certificate filename: {od.certificate_filename}")
            
            # Check to_dict output
            print(f"\n=== API Response ===")
            data = od.to_dict()
            print(f"attendance_proof: {data.get('attendance_proof')}")
            print(f"certificate: {data.get('certificate')}")
        else:
            print("OD 18 not found")

if __name__ == "__main__":
    check_od_18()