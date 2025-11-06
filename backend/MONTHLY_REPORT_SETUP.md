# Monthly OD Report Setup Guide

## Overview
The monthly OD report feature automatically generates and sends Excel reports to all faculty members containing student OD details and proof submission status.

## Features
- **Comprehensive Excel Report**: Includes student details, event information, proof status
- **Color-Coded Status**: Visual indicators for submitted/pending proofs
- **Summary Statistics**: Total ODs, pending proofs, completed submissions
- **Automated Email Delivery**: Sent to all active faculty members

## Manual Trigger

### Option 1: API Endpoint (Recommended for Testing)
Faculty or admin can trigger the report through the API:

**Endpoint**: `POST /api/reports/monthly-od-report`  
**Authentication**: JWT token required (faculty/hod/admin role)

**Example using curl**:
```bash
curl -X POST http://localhost:5000/api/reports/monthly-od-report \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response**:
```json
{
  "message": "Monthly report sent successfully",
  "sent_count": 5,
  "failed_count": 0,
  "total_recipients": 5
}
```

### Option 2: Python Script
Run the standalone script:
```bash
cd backend
python monthly_report.py
```

## Automated Monthly Scheduling

### Windows (Task Scheduler)

1. **Create a batch file** (`run_monthly_report.bat`):
```batch
@echo off
cd C:\od project\OD-pro\backend
call venv\Scripts\activate.bat
python monthly_report.py
```

2. **Schedule in Task Scheduler**:
   - Open Task Scheduler
   - Create Basic Task
   - Name: "OD Monthly Report"
   - Trigger: Monthly (First day of month, 9:00 AM)
   - Action: Start a program
   - Program: `C:\od project\OD-pro\backend\run_monthly_report.bat`

### Linux/Mac (Cron Job)

1. **Create shell script** (`run_monthly_report.sh`):
```bash
#!/bin/bash
cd /path/to/OD-pro/backend
source venv/bin/activate
python monthly_report.py
```

2. **Make executable**:
```bash
chmod +x run_monthly_report.sh
```

3. **Add to crontab** (runs 1st of every month at 9:00 AM):
```bash
crontab -e
```

Add line:
```
0 9 1 * * /path/to/OD-pro/backend/run_monthly_report.sh
```

## Report Contents

The Excel report includes:

### Main Data Columns:
1. **S.No** - Serial number
2. **Student Name** - Full name of student
3. **Roll Number** - Student roll number
4. **Department** - Student's department
5. **Event Name** - Name of the OD event
6. **Event Date** - Date of the event
7. **Status** - OD approval status
8. **Attendance Proof** - Submission status (color-coded)
9. **Certificate** - Submission status (color-coded)
10. **Pending Action** - What needs to be done

### Summary Section:
- Total Approved ODs
- Attendance Proofs Pending
- Certificates Pending
- Fully Completed ODs

### Color Coding:
- **Green**: Submitted ✓
- **Red**: Pending ✗
- **Yellow**: Action Required

## Email Configuration

Ensure these settings are configured in your `.env` or `main.py`:

```python
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-app-password'
MAIL_DEFAULT_SENDER = 'your-email@gmail.com'
```

## Troubleshooting

### Report not sending
1. Check email configuration
2. Verify faculty members are marked as active
3. Check mail server logs
4. Ensure openpyxl is installed: `pip install openpyxl==3.1.2`

### Excel file not generating
1. Verify database connection
2. Check if there are approved OD requests
3. Ensure write permissions in backend directory

### Faculty not receiving emails
1. Verify faculty email addresses
2. Check spam folder
3. Confirm faculty `is_active` status
4. Check email server quotas

## Customization

To modify the report:
1. Edit `monthly_report.py`
2. Update column headers in `headers` list
3. Modify color coding in cell formatting section
4. Customize email template HTML

## Support

For issues or questions, contact the system administrator.
