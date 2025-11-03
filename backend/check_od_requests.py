import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import app, db, ODRequest, Student
from datetime import datetime

with app.app_context():
    print("\n=== Checking OD Requests ===\n")
    
    # Get all OD requests
    all_requests = ODRequest.query.all()
    print(f"Total OD Requests: {len(all_requests)}\n")
    
    for req in all_requests:
        student = Student.query.get(req.student_id)
        print(f"ID: {req.id}")
        print(f"Student: {student.name if student else 'Unknown'} (ID: {req.student_id})")
        print(f"Status: {req.status}")
        print(f"Event Name: {req.event_name}")
        print(f"From: {req.from_date} To: {req.to_date}")
        print(f"Attendance Proof: {'✅ Submitted' if req.attendance_proof_filename else '❌ Not submitted'}")
        print(f"Certificate: {'✅ Submitted' if req.certificate_filename else '❌ Not submitted'}")
        print(f"Created: {req.created_at}")
        print("-" * 60)
    
    # Count by status
    approved = ODRequest.query.filter_by(status='approved').count()
    pending = ODRequest.query.filter_by(status='pending').count()
    rejected = ODRequest.query.filter_by(status='rejected').count()
    
    print(f"\n📊 Summary:")
    print(f"Approved: {approved}")
    print(f"Pending: {pending}")
    print(f"Rejected: {rejected}")
