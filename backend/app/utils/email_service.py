import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
import os
from flask import current_app
import logging

class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        self.college_name = os.getenv('COLLEGE_NAME', 'Your College')
        
    def send_email(self, to_email, subject, body, is_html=False):
        """Send email to recipient"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logging.warning("SMTP credentials not configured. Email not sent.")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logging.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_proof_overdue_notification(self, student, faculty, od_request, proof_type='attendance'):
        """Send notification for overdue proof submission"""
        try:
            # Determine deadline and proof type details
            if proof_type == 'attendance':
                deadline = od_request.attendance_proof_deadline
                proof_name = "Attendance Proof (Event Brochure/Live Photo)"
                deadline_period = "3 days after OD approval"
            else:  # certificate
                deadline = od_request.certificate_submission_deadline
                proof_name = "Participation Certificate"
                deadline_period = "1 month after attendance proof submission"
            
            # Format deadline
            deadline_str = deadline.strftime('%B %d, %Y at %I:%M %p') if deadline else "N/A"
            
            # Email to student
            student_subject = f"URGENT: Overdue Proof Submission - OD Request #{od_request.id}"
            student_body = f"""
Dear {student.name},

This is an urgent reminder that your proof submission for OD Request #{od_request.id} is OVERDUE.

OD Details:
- Event: {od_request.event_name}
- Event Dates: {od_request.from_date} to {od_request.to_date}
- OD Type: {od_request.od_type.value.replace('_', ' ').title()}

Required Submission: {proof_name}
Original Deadline: {deadline_str}
Deadline Period: {deadline_period}

IMPORTANT: You cannot apply for new OD requests until all proof documents are submitted.

Action Required:
1. Log in to your student portal immediately
2. Upload the required {proof_name.lower()}
3. Ensure the document is clear and contains all necessary information

If you are facing any technical issues or have valid reasons for the delay, please contact your faculty advisor immediately.

Faculty Contact: {faculty.name} ({faculty.email})

Best regards,
{self.college_name}
OD Management System
"""
            
            # Email to faculty
            faculty_subject = f"Student Overdue Proof Submission Alert - {student.name} (OD #{od_request.id})"
            faculty_body = f"""
Dear {faculty.name},

This is to inform you that a student from your department has an overdue proof submission.

Student Details:
- Name: {student.name}
- Roll Number: {student.roll_number}
- Department: {student.department}
- Email: {student.email}

OD Details:
- OD Request ID: #{od_request.id}
- Event: {od_request.event_name}
- Event Dates: {od_request.from_date} to {od_request.to_date}
- Approved Date: {od_request.approved_at.strftime('%B %d, %Y') if od_request.approved_at else 'N/A'}

Overdue Submission: {proof_name}
Original Deadline: {deadline_str}

The student has been notified about the overdue submission. Please follow up with the student if necessary.

You can view the complete OD details and submission status in the faculty portal.

Best regards,
{self.college_name}
OD Management System
"""
            
            # Send emails
            student_sent = self.send_email(student.email, student_subject, student_body)
            faculty_sent = self.send_email(faculty.email, faculty_subject, faculty_body)
            
            return student_sent and faculty_sent
            
        except Exception as e:
            logging.error(f"Failed to send overdue notification: {str(e)}")
            return False
    
    def send_deadline_reminder(self, student, faculty, od_request, proof_type='attendance', days_remaining=1):
        """Send reminder notification before deadline"""
        try:
            # Determine deadline and proof type details
            if proof_type == 'attendance':
                deadline = od_request.attendance_proof_deadline
                proof_name = "Attendance Proof (Event Brochure/Live Photo)"
                deadline_period = "3 days after OD approval"
            else:  # certificate
                deadline = od_request.certificate_submission_deadline
                proof_name = "Participation Certificate"
                deadline_period = "1 month after attendance proof submission"
            
            # Format deadline
            deadline_str = deadline.strftime('%B %d, %Y at %I:%M %p') if deadline else "N/A"
            
            # Email to student
            student_subject = f"Reminder: {proof_name} Due in {days_remaining} Day{'s' if days_remaining != 1 else ''} - OD #{od_request.id}"
            student_body = f"""
Dear {student.name},

This is a friendly reminder that your proof submission deadline is approaching.

OD Details:
- Event: {od_request.event_name}
- Event Dates: {od_request.from_date} to {od_request.to_date}
- OD Request ID: #{od_request.id}

Required Submission: {proof_name}
Deadline: {deadline_str}
Days Remaining: {days_remaining}

Action Required:
1. Log in to your student portal
2. Upload the required {proof_name.lower()}
3. Ensure the document is clear and complete

Important Notes:
- Late submissions may affect future OD applications
- You cannot apply for new ODs until all proofs are submitted
- Contact your faculty advisor if you need assistance

Faculty Contact: {faculty.name} ({faculty.email})

Best regards,
{self.college_name}
OD Management System
"""
            
            # Send email to student
            return self.send_email(student.email, student_subject, student_body)
            
        except Exception as e:
            logging.error(f"Failed to send deadline reminder: {str(e)}")
            return False
    
    def send_proof_submission_confirmation(self, student, faculty, od_request, proof_type='attendance'):
        """Send confirmation when proof is submitted"""
        try:
            # Determine proof type details
            if proof_type == 'attendance':
                proof_name = "Attendance Proof"
                next_step = "Now you need to submit your participation certificate within 1 month."
            else:  # certificate
                proof_name = "Participation Certificate"
                next_step = "Your OD proof submission process is now complete!"
            
            # Email to student
            student_subject = f"Proof Submission Confirmed - {proof_name} for OD #{od_request.id}"
            student_body = f"""
Dear {student.name},

Your {proof_name.lower()} has been successfully submitted for OD Request #{od_request.id}.

OD Details:
- Event: {od_request.event_name}
- Event Dates: {od_request.from_date} to {od_request.to_date}

Submission Details:
- Proof Type: {proof_name}
- Submitted On: {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p')}
- Status: Received Successfully

Next Steps: {next_step}

You can check your submission status anytime through the student portal.

Best regards,
{self.college_name}
OD Management System
"""
            
            # Send email to student
            return self.send_email(student.email, student_subject, student_body)
            
        except Exception as e:
            logging.error(f"Failed to send submission confirmation: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()