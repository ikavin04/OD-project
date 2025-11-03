#!/usr/bin/env python3
from main import app, db, ODRequest

def check_api_response():
    with app.app_context():
        # Get OD request 15
        od_request = ODRequest.query.get(15)
        if od_request:
            print("=== OD Request 15 API Response ===")
            print(f"Raw attendance_proof_filename: {od_request.attendance_proof_filename}")
            print(f"Raw attendance_proof_original_name: {od_request.attendance_proof_original_name}")
            
            # Get the to_dict output
            api_data = od_request.to_dict()
            print(f"\nAPI Response attendance_proof: {api_data.get('attendance_proof')}")
            print(f"API Response certificate: {api_data.get('certificate')}")
            print(f"API Response proof_submission_status: {api_data.get('proof_submission_status')}")
            
            import json
            print(f"\nFull API Response:")
            print(json.dumps(api_data, indent=2, default=str))
        else:
            print("OD Request 15 not found")

if __name__ == "__main__":
    check_api_response()