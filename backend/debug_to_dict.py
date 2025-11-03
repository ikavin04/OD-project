#!/usr/bin/env python3
from main import app, db, ODRequest

def debug_to_dict():
    with app.app_context():
        # Get OD request 15
        od_request = ODRequest.query.get(15)
        if od_request:
            print("=== Debug to_dict method ===")
            print(f"attendance_proof_filename: {repr(od_request.attendance_proof_filename)}")
            print(f"Bool check: {bool(od_request.attendance_proof_filename)}")
            print(f"attendance_proof_original_name: {repr(od_request.attendance_proof_original_name)}")
            print(f"attendance_proof_submitted_at: {repr(od_request.attendance_proof_submitted_at)}")
            
            # Manually create the attendance_proof dict
            if od_request.attendance_proof_filename:
                attendance_proof_dict = {
                    'filename': od_request.attendance_proof_original_name,
                    'size': od_request.attendance_proof_file_size,
                    'mime_type': od_request.attendance_proof_mime_type,
                    'uploaded_at': od_request.attendance_proof_submitted_at.isoformat() if od_request.attendance_proof_submitted_at else None
                }
                print(f"attendance_proof dict: {attendance_proof_dict}")
            else:
                print("attendance_proof_filename is falsy")

if __name__ == "__main__":
    debug_to_dict()