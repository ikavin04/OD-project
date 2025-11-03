"""
Check OD Request File Path
"""
from main import app, db, ODRequest
import os

with app.app_context():
    req = ODRequest.query.get(15)
    
    if req:
        print(f"\nOD Request ID: {req.id}")
        print(f"Event Name: {req.event_name}")
        print(f"Application File Path: {req.application_file_path}")
        print(f"Application Filename: {req.application_filename}")
        print(f"Application Original Name: {req.application_original_name}")
        
        if req.application_file_path:
            full_path = os.path.abspath(req.application_file_path)
            print(f"\nFull Path: {full_path}")
            print(f"File Exists: {os.path.exists(full_path)}")
            
            if not os.path.exists(full_path):
                # Check if file exists in uploads folder
                upload_path = os.path.join('uploads', 'od-applications', req.application_filename)
                print(f"\nAlternative Path: {upload_path}")
                print(f"Alternative Exists: {os.path.exists(upload_path)}")
        else:
            print("\nNo file path stored!")
    else:
        print(f"OD Request with ID 15 not found!")
