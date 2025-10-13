from datetime import datetime, timezone, timedelta
from app import db
from app.models import ODRequest, Student, Faculty, ODStatus, ProofStatus
from app.utils.email_service import email_service
import logging

class NotificationService:
    """Service to handle overdue proof notifications"""
    
    @staticmethod
    def check_and_send_overdue_notifications():
        """Check for overdue proof submissions and send notifications"""
        try:
            current_time = datetime.now(timezone.utc)
            notifications_sent = 0
            
            # Find OD requests with overdue attendance proofs
            overdue_attendance = ODRequest.query.filter(
                ODRequest.status == ODStatus.APPROVED,
                ODRequest.attendance_proof_deadline.isnot(None),
                ODRequest.attendance_proof_deadline < current_time,
                ODRequest.attendance_proof_uploaded_at.is_(None),
                db.or_(
                    ODRequest.last_reminder_sent.is_(None),
                    ODRequest.last_reminder_sent < (current_time - timedelta(days=1))  # Don't spam daily
                )
            ).all()
            
            for od_request in overdue_attendance:
                try:
                    student = Student.query.get(od_request.student_id)
                    faculty = Faculty.query.get(od_request.faculty_id)
                    
                    if student and faculty:
                        success = email_service.send_proof_overdue_notification(
                            student, faculty, od_request, 'attendance'
                        )
                        
                        if success:
                            od_request.last_reminder_sent = current_time
                            notifications_sent += 1
                            logging.info(f"Sent overdue attendance notification for OD {od_request.id}")
                        
                except Exception as e:
                    logging.error(f"Failed to send overdue attendance notification for OD {od_request.id}: {str(e)}")
            
            # Find OD requests with overdue certificates
            overdue_certificates = ODRequest.query.filter(
                ODRequest.status == ODStatus.APPROVED,
                ODRequest.certificate_submission_deadline.isnot(None),
                ODRequest.certificate_submission_deadline < current_time,
                ODRequest.certificate_uploaded_at.is_(None),
                ODRequest.attendance_proof_uploaded_at.isnot(None),  # Must have attendance proof
                db.or_(
                    ODRequest.last_reminder_sent.is_(None),
                    ODRequest.last_reminder_sent < (current_time - timedelta(days=1))
                )
            ).all()
            
            for od_request in overdue_certificates:
                try:
                    student = Student.query.get(od_request.student_id)
                    faculty = Faculty.query.get(od_request.faculty_id)
                    
                    if student and faculty:
                        success = email_service.send_proof_overdue_notification(
                            student, faculty, od_request, 'certificate'
                        )
                        
                        if success:
                            od_request.last_reminder_sent = current_time
                            notifications_sent += 1
                            logging.info(f"Sent overdue certificate notification for OD {od_request.id}")
                        
                except Exception as e:
                    logging.error(f"Failed to send overdue certificate notification for OD {od_request.id}: {str(e)}")
            
            # Commit all reminder timestamp updates
            db.session.commit()
            
            logging.info(f"Overdue notification check completed. Sent {notifications_sent} notifications.")
            return notifications_sent
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to check overdue notifications: {str(e)}")
            return 0
    
    @staticmethod
    def send_deadline_reminders():
        """Send reminder notifications 1 day before deadlines"""
        try:
            current_time = datetime.now(timezone.utc)
            tomorrow = current_time + timedelta(days=1)
            notifications_sent = 0
            
            # Find attendance proof deadlines due tomorrow
            attendance_reminders = ODRequest.query.filter(
                ODRequest.status == ODStatus.APPROVED,
                ODRequest.attendance_proof_deadline.between(current_time, tomorrow),
                ODRequest.attendance_proof_uploaded_at.is_(None),
                db.or_(
                    ODRequest.last_reminder_sent.is_(None),
                    ODRequest.last_reminder_sent < (current_time - timedelta(hours=12))
                )
            ).all()
            
            for od_request in attendance_reminders:
                try:
                    student = Student.query.get(od_request.student_id)
                    faculty = Faculty.query.get(od_request.faculty_id)
                    
                    if student and faculty:
                        days_remaining = max(1, (od_request.attendance_proof_deadline - current_time).days)
                        success = email_service.send_deadline_reminder(
                            student, faculty, od_request, 'attendance', days_remaining
                        )
                        
                        if success:
                            od_request.last_reminder_sent = current_time
                            notifications_sent += 1
                            logging.info(f"Sent attendance deadline reminder for OD {od_request.id}")
                        
                except Exception as e:
                    logging.error(f"Failed to send attendance reminder for OD {od_request.id}: {str(e)}")
            
            # Find certificate deadlines due tomorrow
            certificate_reminders = ODRequest.query.filter(
                ODRequest.status == ODStatus.APPROVED,
                ODRequest.certificate_submission_deadline.between(current_time, tomorrow),
                ODRequest.certificate_uploaded_at.is_(None),
                ODRequest.attendance_proof_uploaded_at.isnot(None),
                db.or_(
                    ODRequest.last_reminder_sent.is_(None),
                    ODRequest.last_reminder_sent < (current_time - timedelta(hours=12))
                )
            ).all()
            
            for od_request in certificate_reminders:
                try:
                    student = Student.query.get(od_request.student_id)
                    faculty = Faculty.query.get(od_request.faculty_id)
                    
                    if student and faculty:
                        days_remaining = max(1, (od_request.certificate_submission_deadline - current_time).days)
                        success = email_service.send_deadline_reminder(
                            student, faculty, od_request, 'certificate', days_remaining
                        )
                        
                        if success:
                            od_request.last_reminder_sent = current_time
                            notifications_sent += 1
                            logging.info(f"Sent certificate deadline reminder for OD {od_request.id}")
                        
                except Exception as e:
                    logging.error(f"Failed to send certificate reminder for OD {od_request.id}: {str(e)}")
            
            # Commit all reminder timestamp updates
            db.session.commit()
            
            logging.info(f"Deadline reminder check completed. Sent {notifications_sent} reminders.")
            return notifications_sent
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to send deadline reminders: {str(e)}")
            return 0
    
    @staticmethod
    def get_students_with_pending_proofs():
        """Get list of students who have pending proof submissions"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Students with overdue or pending proofs
            pending_students = db.session.query(
                Student.id,
                Student.name,
                Student.roll_number,
                Student.department,
                Student.email,
                db.func.count(ODRequest.id).label('pending_count')
            ).join(ODRequest).filter(
                ODRequest.status == ODStatus.APPROVED,
                db.or_(
                    # Overdue attendance proof
                    db.and_(
                        ODRequest.attendance_proof_deadline < current_time,
                        ODRequest.attendance_proof_uploaded_at.is_(None)
                    ),
                    # Overdue certificate
                    db.and_(
                        ODRequest.certificate_submission_deadline < current_time,
                        ODRequest.certificate_uploaded_at.is_(None),
                        ODRequest.attendance_proof_uploaded_at.isnot(None)
                    )
                )
            ).group_by(
                Student.id, Student.name, Student.roll_number, 
                Student.department, Student.email
            ).all()
            
            return [
                {
                    'student_id': row.id,
                    'name': row.name,
                    'roll_number': row.roll_number,
                    'department': row.department,
                    'email': row.email,
                    'pending_count': row.pending_count
                }
                for row in pending_students
            ]
            
        except Exception as e:
            logging.error(f"Failed to get students with pending proofs: {str(e)}")
            return []

# Global notification service instance
notification_service = NotificationService()