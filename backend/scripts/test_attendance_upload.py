#!/usr/bin/env python3
"""
End-to-end test: create an approved OD for a test student, then upload an
attendance proof via HTTP to verify the API and UI contract.

Requirements:
- Backend must be running on http://localhost:5000
- Uses the test student created by ensure_test_account.py
"""
import base64
import sys
import pathlib
import io
import os
import time
import requests

from datetime import date, datetime, timezone

# Ensure we can import backend modules
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Local backend
BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000/api")
STUDENT_EMAIL = os.environ.get("TEST_STUDENT_EMAIL", "24ucs153kavin@kgkite.ac.in")
STUDENT_PASSWORD = os.environ.get("TEST_STUDENT_PASSWORD", "Kgkite@1234")

# 1x1 PNG (transparent)
_PNG_1x1_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAnsB+vQG1Z0AAAAASUVORK5CYII="
)


def login_student():
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    return data["access_token"]


def upload_attendance_proof(od_id, token):
    png_bytes = base64.b64decode(_PNG_1x1_BASE64)
    files = {"attendance_proof": ("test.png", io.BytesIO(png_bytes), "image/png")}
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{BASE_URL}/od-requests/{od_id}/submit-attendance-proof",
        files=files,
        headers=headers,
        timeout=20,
    )
    print("Upload status:", r.status_code)
    try:
        print("Response:", r.json())
    except Exception:
        print(r.text)
    r.raise_for_status()


def verify_list(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/od-requests", headers=headers, timeout=10)
    print("List status:", r.status_code)
    data = r.json()
    for item in data.get("od_requests", []):
        if item.get("attendance_proof"):
            print(f"OD {item['id']} has attendance_proof: {item['attendance_proof'].get('filename')}")
        else:
            print(f"OD {item['id']} has no attendance_proof")


if __name__ == "__main__":
    print("Logging in as test student...")
    token = login_student()
    print("Got token (truncated):", token[:16], "...")

    # Find an approved OD via API
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/od-requests", headers=headers, timeout=10)
    r.raise_for_status()
    od_list = r.json().get("od_requests", [])
    approved = [od for od in od_list if od.get("status") == "approved"]
    if not approved:
        raise SystemExit("No approved OD found for the test student. Approve one in the UI or DB and retry.")
    od_id = approved[0]["id"]
    print("Using approved OD ID:", od_id)

    print("Uploading attendance proof...")
    upload_attendance_proof(od_id, token)

    time.sleep(0.5)
    print("Verifying list response...")
    verify_list(token)
