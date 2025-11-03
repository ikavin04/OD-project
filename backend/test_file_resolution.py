"""
Test File Path Resolution
"""
from main import app, db, ODRequest
import os

with app.app_context():
    req = ODRequest.query.get(15)
    
    if req:
        print(f"\nTesting file path resolution for OD Request {req.id}")
        print(f"Stored path: {req.application_file_path}")
        print(f"Filename: {req.application_filename}")
        
        # Try multiple paths
        file_path = None
        
        # Try the stored path first
        if os.path.exists(req.application_file_path):
            file_path = req.application_file_path
            print(f"\n✅ Found at stored path: {file_path}")
        else:
            print(f"\n❌ Not found at stored path")
            
            # Try absolute path
            abs_path = os.path.abspath(req.application_file_path)
            if os.path.exists(abs_path):
                file_path = abs_path
                print(f"✅ Found at absolute path: {file_path}")
            else:
                print(f"❌ Not found at absolute path: {abs_path}")
            
            # Try with od-applications subfolder
            od_app_path = os.path.join('uploads', 'od-applications', req.application_filename)
            if os.path.exists(od_app_path):
                file_path = od_app_path
                print(f"✅ Found in od-applications: {file_path}")
            else:
                print(f"❌ Not found in od-applications: {od_app_path}")
            
            # Try uploads root with just filename
            upload_path = os.path.join('uploads', req.application_filename)
            if os.path.exists(upload_path):
                file_path = upload_path
                print(f"✅ Found in uploads root: {file_path}")
            else:
                print(f"❌ Not found in uploads root: {upload_path}")
        
        if file_path:
            print(f"\n🎉 File resolved to: {file_path}")
        else:
            print(f"\n❌ File not found anywhere!")
            
            # List what files are in uploads
            print("\nFiles in uploads folder:")
            if os.path.exists('uploads'):
                for file in os.listdir('uploads'):
                    if os.path.isfile(os.path.join('uploads', file)):
                        print(f"  - {file}")
    else:
        print("OD Request 15 not found!")
