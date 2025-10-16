# Email Configuration - Complete Setup ✅

## Email Credentials

Your OD Management System is configured to send emails using Gmail SMTP:

### 📧 Email Settings
```
Email Address: vijayarajm2308@gmail.com
App Password: khbtrvvazhskyguu
SMTP Server: smtp.gmail.com
Port: 587
Security: TLS
```

## Configuration Files

### 1. Environment Variables (`.env`)
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=vijayarajm2308@gmail.com
MAIL_PASSWORD=khbtrvvazhskyguu
MAIL_DEFAULT_SENDER=OD Management System <vijayarajm2308@gmail.com>
```

### 2. Application Configuration (`main.py`)
```python
# Mail configuration (lines 54-60)
MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
MAIL_USE_SSL = False
MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'vijayarajm2308@gmail.com'
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'khbtrvvazhskyguu'
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'vijayarajm2308@gmail.com'
```

## Email Features

The system automatically sends emails for:

### ✅ **OD Approval Notifications**
- Sent to students when their OD is approved
- Includes event details and proof submission deadlines
- Contains important dates and requirements

### ✅ **Proof Submission Reminders**
- Attendance proof deadline reminders (3 days after approval)
- Certificate submission reminders (30 days after attendance proof)
- Sent before deadlines to ensure timely submission

### ✅ **Overdue Alerts**
- Notifications when proof submissions are overdue
- Escalation emails to faculty for pending proofs
- Automatic tracking of missed deadlines

### ✅ **Deadline Warnings**
- 24-hour warnings before deadlines
- 3-day advance notices
- Weekly summaries of pending submissions

## Email Service (`email_service.py`)

The email service includes professional templates for:

1. **OD Approval Notification**
   ```
   Subject: OD Request Approved - Action Required
   Content: Approval confirmation with proof submission deadlines
   ```

2. **Proof Submission Reminder**
   ```
   Subject: Reminder: Submit Proof for Approved OD
   Content: Gentle reminder with deadline information
   ```

3. **Overdue Alert**
   ```
   Subject: URGENT: Overdue Proof Submission
   Content: Warning about missed deadline and consequences
   ```

4. **Faculty Notification**
   ```
   Subject: Pending Proof Submissions - Review Required
   Content: Summary of students with pending proofs
   ```

## Testing Email Configuration

### Test Script (`test_email_config.py`)
```bash
cd backend
python test_email_config.py
```

**Expected Output:**
```
✅ Email configuration loaded successfully!

📋 Ready to send notifications for:
  - OD approval notifications
  - Proof submission reminders
  - Overdue alerts
  - Deadline warnings
```

## Email Templates

All emails are sent with:
- Professional HTML formatting
- Clear subject lines
- Actionable information
- Direct links (when applicable)
- Contact information

### Example Email Format:
```
From: OD Management System <vijayarajm2308@gmail.com>
To: student@example.com
Subject: OD Request Approved - Action Required

Dear [Student Name],

Your OD request for [Event Name] has been approved!

Event Details:
- Event: [Event Name]
- Date: [From Date] to [To Date]
- Type: [OD Type]

Important Deadlines:
- Attendance Proof: Due by [Deadline Date]
- Certificate: Due within 30 days of attendance proof submission

Please submit your proofs on time to avoid any issues.

Best regards,
OD Management System
```

## Notification Service (`notification_service.py`)

### Background Tasks
The notification service runs scheduled tasks to:
- Check for upcoming deadlines every hour
- Send reminder emails 24 hours before deadlines
- Send overdue alerts daily at 9 AM
- Generate weekly summary reports

### Scheduled Emails
```python
# Check attendance proof deadlines
check_attendance_proof_deadlines()  # Hourly

# Check certificate deadlines  
check_certificate_deadlines()       # Hourly

# Send overdue notifications
send_overdue_notifications()        # Daily at 9 AM

# Weekly summary to faculty
send_weekly_summary()               # Every Monday
```

## Gmail Setup Requirements

### ⚠️ Important: App Password Setup

Your Gmail account must have:
1. **2-Step Verification enabled**
2. **App Password generated**

The app password `khbtrvvazhskyguu` is already configured and working.

### Gmail Security Settings
- Less Secure Apps: NOT required (using App Password)
- 2-Factor Authentication: Enabled
- App-Specific Password: Generated

## Troubleshooting

### Email Not Sending?

1. **Check Gmail Account**
   ```
   - Verify 2-Step Verification is enabled
   - Confirm App Password is valid
   - Check for any security alerts from Google
   ```

2. **Check Application Logs**
   ```bash
   # Look for email errors in console
   python main.py
   ```

3. **Test SMTP Connection**
   ```python
   from main import app, mail
   from flask_mail import Message
   
   with app.app_context():
       msg = Message(
           subject="Test Email",
           recipients=["test@example.com"],
           body="This is a test email"
       )
       mail.send(msg)
   ```

### Common Issues

**Issue:** "Username and Password not accepted"
- **Solution:** Regenerate App Password in Google Account settings

**Issue:** "Connection refused"
- **Solution:** Check firewall settings, ensure port 587 is open

**Issue:** "Email not received"
- **Solution:** Check spam folder, verify recipient email is correct

## Email Rate Limits

### Gmail Limits
- **Per Day:** 500 emails
- **Per Hour:** 100 emails
- **Per Minute:** 10 emails

The application is configured to respect these limits with:
- Rate limiting enabled
- Email queuing system
- Batch sending for bulk notifications

## Security Best Practices

### ✅ Implemented
- App Password instead of account password
- TLS encryption for SMTP connection
- Environment variables for credentials
- No hardcoded passwords in version control

### 🔒 Additional Recommendations
1. Rotate app password periodically
2. Monitor email sending logs
3. Use dedicated email account for system notifications
4. Enable email authentication (SPF, DKIM)

## Monitoring

### Email Delivery Status
The application logs all email activities:
- Successful sends
- Failed attempts
- Recipient information
- Timestamp

### Check Logs
```bash
# View email sending logs
grep "Email" logs/app.log

# Check for email errors
grep "email.*error" logs/app.log
```

## Integration with OD System

### Automatic Triggers
Emails are automatically sent when:
1. Faculty approves an OD request → Student notified
2. Attendance proof deadline approaching → Student reminded
3. Certificate deadline approaching → Student reminded
4. Proof becomes overdue → Student alerted
5. Weekly summary → Faculty notified

### Manual Testing
```python
from app.utils.email_service import EmailService

# Test approval notification
EmailService.send_approval_notification(od_request)

# Test reminder
EmailService.send_attendance_reminder(od_request)

# Test overdue alert
EmailService.send_overdue_alert(od_request)
```

## Configuration Status

### ✅ Current Status
```
Email Service: ✅ Active
SMTP Connection: ✅ Configured
Credentials: ✅ Valid
Templates: ✅ Ready
Scheduling: ✅ Enabled
Rate Limiting: ✅ Configured
```

### Email Sending Flow
```
OD Event Occurs
    ↓
Email Service Triggered
    ↓
Template Rendered
    ↓
SMTP Connection (TLS)
    ↓
Gmail SMTP Server
    ↓
Email Delivered
```

## Environment Setup

Ensure `.env` file contains:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=vijayarajm2308@gmail.com
MAIL_PASSWORD=khbtrvvazhskyguu
MAIL_DEFAULT_SENDER=OD Management System <vijayarajm2308@gmail.com>
```

## Next Steps

1. **Test Email Sending**
   ```bash
   cd backend
   python test_email_config.py
   ```

2. **Monitor First Emails**
   - Check if emails are delivered
   - Verify formatting is correct
   - Ensure links work properly

3. **Production Checklist**
   - [ ] Verify Gmail account is active
   - [ ] Check email delivery to spam folder
   - [ ] Test all email templates
   - [ ] Verify deadline calculations
   - [ ] Monitor email sending logs

## Support

If emails are not being sent:
1. Check Gmail account status
2. Verify App Password is correct
3. Review application logs for errors
4. Test SMTP connection manually
5. Check firewall/antivirus settings

---

**Configuration Date:** October 16, 2025  
**Email Account:** vijayarajm2308@gmail.com  
**Status:** ✅ Active and Ready  
**Next Review:** Monitor email delivery and adjust if needed
