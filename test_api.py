#!/usr/bin/env python3
"""
Quick test to check if attendance proof now appears in API response
"""

import requests
import json

# Test the API directly
try:
    # First login to get a token (assuming student credentials)
    login_response = requests.post('http://localhost:5000/api/auth/login', json={
        'email': '24ucs153kavin@kgkite.ac.in',
        'password': 'test123'
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        
        # Get OD requests
        headers = {'Authorization': f'Bearer {token}'}
        od_response = requests.get('http://localhost:5000/api/od-requests', headers=headers)
        
        if od_response.status_code == 200:
            data = od_response.json()
            
            # Find OD request 15
            od_15 = None
            for req in data.get('od_requests', []):
                if req['id'] == 15:
                    od_15 = req
                    break
            
            if od_15:
                print("=== OD Request 15 from API ===")
                print(f"ID: {od_15['id']}")
                print(f"Status: {od_15['status']}")
                print(f"Proof Status: {od_15['proof_submission_status']}")
                print(f"Attendance Proof: {od_15.get('attendance_proof')}")
                print(f"Certificate: {od_15.get('certificate')}")
            else:
                print("OD Request 15 not found in API response")
                print(f"Available IDs: {[req['id'] for req in data.get('od_requests', [])]}")
        else:
            print(f"Failed to get OD requests: {od_response.status_code}")
            print(od_response.text)
    else:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        
except Exception as e:
    print(f"Error: {e}")