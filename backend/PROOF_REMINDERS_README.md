# Automated Proof Deadline Reminder System

## Overview
This system automatically sends email reminders to students **2 days before** their attendance proof or certificate submission deadlines.

## Files
- `proof_deadline_reminders.py` - Main Python script that checks deadlines and sends emails
- `run_proof_reminders.bat` - Windows batch file to run the script easily

## How It Works
1. The script runs and checks all approved OD requests
2. Finds students who have deadlines in exactly 2 days
3. Sends customized reminder emails for:
   - **Attendance Proof** - For students who haven't submitted attendance proof
   - **Participation Certificate** - For students who haven't submitted certificates

## Email Content
The reminder emails include:
- Event details (name, dates)
- Exact deadline date and time
- Days remaining
- What documents to submit
- Direct link to submission portal
- NO emojis (as requested)

## Manual Testing
To test the system manually:
```bash
cd backend
python proof_deadline_reminders.py
```

## Setting Up Daily Automation

### Option 1: Windows Task Scheduler (Recommended for Windows)

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Basic Task**
3. Name: "OD Proof Deadline Reminders"
4. Trigger: **Daily** at a specific time (e.g., 9:00 AM)
5. Action: **Start a program**
   - Program: `C:\path\to\OD-project\backend\run_proof_reminders.bat`
6. Click **Finish**

**Recommended Schedule:** Run daily at 9:00 AM

### Option 2: Linux/Mac Cron Job

Add to crontab:
```bash
# Run daily at 9:00 AM
0 9 * * * cd /path/to/OD-project/backend && python proof_deadline_reminders.py
```

Edit crontab:
```bash
crontab -e
```

## Configuration
The script uses the same email configuration as the main application:
- Email server: Gmail SMTP
- Credentials from `.env` file or hardcoded defaults
- Sender: vijayarajm2308@gmail.com

## Deadline Logic
- **Attendance Proof Deadline:** 3 days after OD approval
- **Certificate Deadline:** 1 month after attendance proof submission
- **Reminder Sent:** Exactly 2 days before deadline

## Example Scenarios

### Scenario 1: Attendance Proof
- OD approved: Jan 10, 2026 at 10:00 AM
- Deadline: Jan 13, 2026 at 10:00 AM
- Reminder sent: Jan 11, 2026 (when script runs)

### Scenario 2: Certificate
- Attendance proof submitted: Jan 15, 2026
- Deadline: Feb 15, 2026
- Reminder sent: Feb 13, 2026 (when script runs)

## Monitoring
When the script runs, it outputs:
- Number of students found with upcoming deadlines
- Email sending status for each student
- Summary of total reminders sent

## Troubleshooting

### No emails sent?
1. Check if there are any students with deadlines in exactly 2 days
2. Verify email credentials in `.env` file
3. Check mail server settings
4. Review script output for error messages

### Emails going to spam?
- Add sender email to recipient's contacts
- Check Gmail "Less secure apps" settings
- Consider using App Passwords instead of regular password

## Dependencies
All required packages are already in `requirements.txt`:
- Flask
- Flask-SQLAlchemy
- Flask-Mail
- python-dotenv

## Security Notes
- Keep your `.env` file secure
- Never commit email passwords to git
- Consider using environment variables for production
- Use App Passwords for Gmail accounts with 2FA enabled
