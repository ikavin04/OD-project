# 📧 Automated Email System

## Overview
The OD Management System now includes **fully automated email scheduling** using APScheduler. Emails are sent automatically when the Flask backend is running - no manual intervention or Windows Task Scheduler needed!

---

## 🚀 How It Works

When you start the Flask backend (`python main.py`), the scheduler automatically starts in the background and runs these tasks:

### 1. **Student Proof Deadline Reminders** ⏰
- **Schedule**: Every day at **9:00 AM**
- **Recipients**: Students with upcoming deadlines
- **Timing**: Sends reminders **2 days before** the deadline
- **Types**:
  - Attendance proof reminders (3-day deadline)
  - Certificate submission reminders (1-month deadline)

### 2. **Monthly Faculty Reports** 📊
- **Schedule**: **Last day of every month** at **11:00 PM**
- **Recipients**: All faculty members (Faculty, HOD, Admin)
- **Content**: Excel report with OD proof submission status
- **Attachment**: Monthly OD report with student submission details

---

## ✅ What Emails Are Sent

### **For Students:**
1. **Immediate Emails** (sent instantly):
   - OD Request Approval ✓
   - OD Request Rejection ✗

2. **Scheduled Reminder Emails** (automated):
   - Attendance proof deadline reminder (2 days before)
   - Certificate deadline reminder (2 days before)

### **For Faculty:**
1. **Monthly Reports** (automated):
   - Comprehensive Excel report on last day of month
   - Contains all OD requests and proof submission status

---

## 📋 Configuration

### Change Email Send Times

Edit `main.py` in the scheduler configuration section:

```python
# Daily reminders at 9:00 AM
scheduler.add_job(
    func=send_proof_deadline_reminders_job,
    trigger=CronTrigger(hour=9, minute=0),  # Change hour/minute here
    ...
)

# Monthly reports on last day at 11:00 PM
scheduler.add_job(
    func=send_monthly_faculty_reports_job,
    trigger=CronTrigger(day='last', hour=23, minute=0),  # Change day/hour/minute here
    ...
)
```

### Common Schedule Examples:
- `hour=8, minute=30` → 8:30 AM
- `hour=17, minute=0` → 5:00 PM
- `day=1, hour=9` → 1st of month at 9:00 AM
- `day='last', hour=18` → Last day of month at 6:00 PM

---

## 🔧 Technical Details

- **Scheduler**: APScheduler (BackgroundScheduler)
- **Email Service**: Flask-Mail with SMTP (Gmail)
- **Automatic Start**: Scheduler starts when Flask app starts
- **Automatic Shutdown**: Scheduler stops when Flask app stops
- **Error Handling**: All jobs have try-catch to prevent crashes

---

## 🎯 Requirements

1. Flask backend must be **running** for emails to be sent
2. Valid SMTP credentials configured in `.env` file
3. Database must be accessible
4. APScheduler package installed (`pip install APScheduler`)

---

## 🚨 Important Notes

- **No Windows Task Scheduler needed** - everything runs inside Flask
- **No manual execution required** - fully automatic
- **Logs are silent** - no console spam (print statements removed)
- **Production ready** - runs in background without blocking the app
- **Works on all platforms** - Windows, Linux, Mac

---

## 🧪 Testing

To test if scheduler is working:
1. Start the Flask backend: `python main.py`
2. Check that the app starts without errors
3. Scheduled jobs will run automatically at their specified times

To manually test email functions without waiting:
- Use the existing `/api/reports/monthly-od-report` endpoint for faculty reports

---

## 📞 Support

If emails are not being sent:
1. Check SMTP credentials in `.env` file
2. Verify Flask backend is running
3. Check email server allows SMTP connections
4. Verify student/faculty email addresses are correct in database

---

**Email scheduling is now fully automated! 🎉**
