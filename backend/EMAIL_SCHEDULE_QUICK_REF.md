# 📧 Automated Email Schedule - Quick Reference

## 🎯 What Happens Automatically

### **STUDENTS Receive:**
| Email Type | When Sent | Trigger |
|------------|-----------|---------|
| ✅ OD Approved | **Immediately** | Faculty approves request |
| ❌ OD Rejected | **Immediately** | Faculty rejects request |
| ⏰ Attendance Reminder | **Daily at 9:00 AM** | 2 days before attendance proof deadline |
| ⏰ Certificate Reminder | **Daily at 9:00 AM** | 2 days before certificate deadline |

### **FACULTY Receive:**
| Email Type | When Sent | Content |
|------------|-----------|---------|
| 📊 Monthly Report | **Last day of month at 11:00 PM** | Excel file with all OD proof status |

---

## 🚀 How to Use

### **1. Start Backend (Starts Scheduler Automatically)**
```bash
cd backend
python main.py
```
✅ Scheduler starts automatically  
✅ Jobs run at scheduled times  
✅ No additional setup needed  

### **2. Stop Backend (Stops Scheduler Automatically)**
```bash
Ctrl + C
```
✅ Scheduler shuts down gracefully  
✅ All jobs stop  

---

## ⚙️ Configuration Files

### **Email Settings** (`.env`)
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### **Schedule Times** (`main.py` - lines ~2340-2360)
```python
# Daily reminders at 9:00 AM
trigger=CronTrigger(hour=9, minute=0)

# Monthly reports on last day at 11:00 PM  
trigger=CronTrigger(day='last', hour=23, minute=0)
```

---

## 🔍 How to Verify It's Working

### **Check Scheduler Status:**
1. Start the backend
2. Look for no errors on startup
3. Jobs will run automatically at scheduled times

### **Test Emails Without Waiting:**
- Approval/Rejection emails work immediately when faculty takes action
- For reminders: Create test OD with deadlines 2 days away
- For monthly reports: Use existing manual endpoint

---

## ⚠️ Important Notes

✅ **No Windows Task Scheduler needed**  
✅ **No cron jobs needed**  
✅ **No manual execution required**  
✅ **Works on Windows, Linux, Mac**  
❌ Backend must be running for emails to send  
❌ Stop backend = scheduler stops  

---

## 🎊 Summary

**Just start your Flask backend and everything works automatically!**

- Reminders sent daily at 9 AM
- Monthly reports sent on last day of month
- Approval/rejection emails sent instantly

**No additional setup. No scheduled tasks. Just run the app! 🎉**
