"""
Proof Deadline Reminder System
Sends automated email reminders to students 2 days before their attendance proof or certificate deadlines
Run this script daily via cron job or task scheduler
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    'postgresql://postgres:Manisha14@localhost:5432/OD'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT') or 587)
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'vijayarajm2308@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or 'khbtrvvazhskyguu'
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER') or 'vijayarajm2308@gmail.com'

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# Import models (simplified versions for this script)
import enum

class ProofStatus(enum.Enum):
    NOT_SUBMITTED = "NOT_SUBMITTED"
    attendance_pending = "attendance_pending"
    ATTENDANCE_SUBMITTED = "ATTENDANCE_SUBMITTED"
    certificate_pending = "certificate_pending"
    certificate_submitted = "certificate_submitted"
    COMPLETED = "COMPLETED"

class ODStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    year = db.Column(db.Integer)
    semester = db.Column(db.Integer)

class ODRequest(db.Model):
    __tablename__ = 'od_requests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    event_name = db.Column(db.String(200))
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)
    status = db.Column(db.Enum(ODStatus))
    proof_submission_status = db.Column(db.Enum(ProofStatus))
    attendance_proof_deadline = db.Column(db.DateTime(timezone=True))
    certificate_deadline = db.Column(db.DateTime(timezone=True))
    attendance_proof_submitted_at = db.Column(db.DateTime(timezone=True))
    certificate_submitted_at = db.Column(db.DateTime(timezone=True))
    approved_at = db.Column(db.DateTime(timezone=True))
    
    student = db.relationship('Student', backref='od_requests')

def send_attendance_proof_reminder(student, od_request, days_remaining):
    """Send attendance proof deadline reminder email"""
    subject = f"Reminder: Attendance Proof Deadline - {od_request.event_name}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
        <div style="background: linear-gradient(135deg, #ff9800, #f57c00); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 28px;">KGISL College</h1>
            <h2 style="margin: 10px 0 0 0; font-size: 20px;">Attendance Proof Deadline Reminder</h2>
        </div>
        
        <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="color: #ff9800; margin-top: 0;">Dear {student.name},</h3>
            
            <p style="font-size: 16px; color: #333; line-height: 1.6;">
                This is a reminder that your attendance proof submission deadline is approaching.
            </p>
            
            <div style="background-color: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ff9800;">
                <h4 style="margin: 0 0 15px 0; color: #333;">Event Details:</h4>
                <ul style="margin: 0; padding-left: 20px; color: #555;">
                    <li><strong>Event:</strong> {od_request.event_name}</li>
                    <li><strong>Event Date:</strong> {od_request.from_date.strftime('%d %B %Y')} to {od_request.to_date.strftime('%d %B %Y')}</li>
                    <li><strong>OD Approved On:</strong> {od_request.approved_at.strftime('%d %B %Y')}</li>
                </ul>
            </div>
            
            <div style="background-color: #ffebee; padding: 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #f44336;">
                <h4 style="margin: 0 0 10px 0; color: #c62828;">URGENT - Action Required</h4>
                <p style="margin: 0; color: #c62828; font-size: 16px; font-weight: bold;">
                    Deadline: {od_request.attendance_proof_deadline.strftime('%d %B %Y at %I:%M %p')}
                </p>
                <p style="margin: 10px 0 0 0; color: #d32f2f;">
                    Only {days_remaining} days remaining to submit your attendance proof!
                </p>
            </div>
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #1976d2;">What to Submit:</h4>
                <ul style="margin: 0; padding-left: 20px; color: #0d47a1;">
                    <li>Event brochure/pamphlet showing the dates</li>
                    <li>OR Live photo from the event venue</li>
                    <li>OR Any official document proving your attendance</li>
                </ul>
            </div>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #856404;">Important Notes:</h4>
                <ul style="margin: 0; padding-left: 20px; color: #856404;">
                    <li>You cannot apply for new ODs until this proof is submitted</li>
                    <li>Late submissions may not be accepted</li>
                    <li>Login to your student portal to upload the proof</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <p style="font-size: 14px; color: #666; margin-bottom: 10px;">
                    Login to submit your proof:
                </p>
                <a href="http://localhost:3000/student/proofs" 
                   style="display: inline-block; padding: 12px 30px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Submit Attendance Proof
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px; margin: 30px 0 0 0; text-align: center;">
                Best regards,<br>
                <strong>OD Management System</strong><br>
                KGISL College
            </p>
        </div>
    </div>
    """
    
    try:
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[student.email],
            html=html_content
        )
        mail.send(msg)
        print(f"Attendance proof reminder sent to {student.name} ({student.email})")
        return True
    except Exception as e:
        print(f"Failed to send email to {student.email}: {str(e)}")
        return False

def send_certificate_reminder(student, od_request, days_remaining):
    """Send certificate deadline reminder email"""
    subject = f"Reminder: Certificate Submission Deadline - {od_request.event_name}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
        <div style="background: linear-gradient(135deg, #9c27b0, #7b1fa2); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 28px;">KGISL College</h1>
            <h2 style="margin: 10px 0 0 0; font-size: 20px;">Certificate Submission Deadline Reminder</h2>
        </div>
        
        <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="color: #9c27b0; margin-top: 0;">Dear {student.name},</h3>
            
            <p style="font-size: 16px; color: #333; line-height: 1.6;">
                This is a reminder that your participation certificate submission deadline is approaching.
            </p>
            
            <div style="background-color: #f3e5f5; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #9c27b0;">
                <h4 style="margin: 0 0 15px 0; color: #333;">Event Details:</h4>
                <ul style="margin: 0; padding-left: 20px; color: #555;">
                    <li><strong>Event:</strong> {od_request.event_name}</li>
                    <li><strong>Event Date:</strong> {od_request.from_date.strftime('%d %B %Y')} to {od_request.to_date.strftime('%d %B %Y')}</li>
                    <li><strong>Attendance Proof Submitted:</strong> {od_request.attendance_proof_submitted_at.strftime('%d %B %Y')}</li>
                </ul>
            </div>
            
            <div style="background-color: #ffebee; padding: 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #f44336;">
                <h4 style="margin: 0 0 10px 0; color: #c62828;">URGENT - Action Required</h4>
                <p style="margin: 0; color: #c62828; font-size: 16px; font-weight: bold;">
                    Deadline: {od_request.certificate_deadline.strftime('%d %B %Y at %I:%M %p')}
                </p>
                <p style="margin: 10px 0 0 0; color: #d32f2f;">
                    Only {days_remaining} days remaining to submit your participation certificate!
                </p>
            </div>
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #1976d2;">What to Submit:</h4>
                <ul style="margin: 0; padding-left: 20px; color: #0d47a1;">
                    <li>Official participation certificate from the event organizers</li>
                    <li>Certificate should clearly show your name and the event details</li>
                    <li>Scan or take a clear photo of the certificate</li>
                </ul>
            </div>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #856404;">Important Notes:</h4>
                <ul style="margin: 0; padding-left: 20px; color: #856404;">
                    <li>You cannot apply for new ODs until this certificate is submitted</li>
                    <li>This is the final step to complete your OD documentation</li>
                    <li>Late submissions may not be accepted</li>
                    <li>Login to your student portal to upload the certificate</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <p style="font-size: 14px; color: #666; margin-bottom: 10px;">
                    Login to submit your certificate:
                </p>
                <a href="http://localhost:3000/student/proofs" 
                   style="display: inline-block; padding: 12px 30px; background-color: #9c27b0; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Submit Certificate
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px; margin: 30px 0 0 0; text-align: center;">
                Best regards,<br>
                <strong>OD Management System</strong><br>
                KGISL College
            </p>
        </div>
    </div>
    """
    
    try:
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[student.email],
            html=html_content
        )
        mail.send(msg)
        print(f"Certificate reminder sent to {student.name} ({student.email})")
        return True
    except Exception as e:
        print(f"Failed to send email to {student.email}: {str(e)}")
        return False

def send_deadline_reminders():
    """
    Main function to check for upcoming deadlines and send reminders
    Sends reminders 2 days before the deadline
    """
    with app.app_context():
        print(f"\n{'='*80}")
        print(f"Proof Deadline Reminder System - {datetime.now().strftime('%d %B %Y %I:%M %p')}")
        print(f"{'='*80}\n")
        
        # Calculate the target date (2 days from now)
        now = datetime.now(timezone.utc)
        reminder_date_start = now + timedelta(days=2)
        reminder_date_end = reminder_date_start + timedelta(hours=23, minutes=59, seconds=59)
        
        print(f"Checking for deadlines on: {reminder_date_start.strftime('%d %B %Y')}")
        print(f"Time window: {reminder_date_start.strftime('%I:%M %p')} to {reminder_date_end.strftime('%I:%M %p')}\n")
        
        attendance_reminders_sent = 0
        certificate_reminders_sent = 0
        
        # Find OD requests with attendance proof deadline in 2 days
        print("Checking for attendance proof deadlines...")
        attendance_pending = ODRequest.query.filter(
            ODRequest.status == ODStatus.APPROVED,
            ODRequest.proof_submission_status == ProofStatus.attendance_pending,
            ODRequest.attendance_proof_deadline >= reminder_date_start,
            ODRequest.attendance_proof_deadline <= reminder_date_end
        ).all()
        
        print(f"Found {len(attendance_pending)} students with upcoming attendance proof deadlines\n")
        
        for od_request in attendance_pending:
            if od_request.student:
                days_remaining = (od_request.attendance_proof_deadline - now).days
                if send_attendance_proof_reminder(od_request.student, od_request, days_remaining):
                    attendance_reminders_sent += 1
        
        # Find OD requests with certificate deadline in 2 days
        print("\nChecking for certificate deadlines...")
        certificate_pending = ODRequest.query.filter(
            ODRequest.status == ODStatus.APPROVED,
            ODRequest.proof_submission_status == ProofStatus.certificate_pending,
            ODRequest.certificate_deadline >= reminder_date_start,
            ODRequest.certificate_deadline <= reminder_date_end
        ).all()
        
        print(f"Found {len(certificate_pending)} students with upcoming certificate deadlines\n")
        
        for od_request in certificate_pending:
            if od_request.student:
                days_remaining = (od_request.certificate_deadline - now).days
                if send_certificate_reminder(od_request.student, od_request, days_remaining):
                    certificate_reminders_sent += 1
        
        # Summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Attendance Proof Reminders Sent: {attendance_reminders_sent}")
        print(f"Certificate Reminders Sent: {certificate_reminders_sent}")
        print(f"Total Reminders Sent: {attendance_reminders_sent + certificate_reminders_sent}")
        print(f"{'='*80}\n")

if __name__ == '__main__':
    try:
        send_deadline_reminders()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        sys.exit(1)
