from app import db
from .enums import ODStatus, ODType, ProofStatus
from datetime import datetime, timezone, timedelta
import json

class ODRequest(db.Model):
    __tablename__ = 'od_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'))
    
    # OD Details
    event_name = db.Column(db.String(200), nullable=False)
    event_description = db.Column(db.Text)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    od_type = db.Column(db.Enum(ODType), nullable=False)
    college_name = db.Column(db.String(200))  # For intra-college events
    host_institution = db.Column(db.String(200))  # For inter-college events
    venue = db.Column(db.String(200))
    location_type = db.Column(db.String(50))  # within_state or out_of_state
    
    # Application File
    application_filename = db.Column(db.String(255), nullable=False)
    application_original_name = db.Column(db.String(255), nullable=False)
    application_file_path = db.Column(db.String(500), nullable=False)
    application_file_size = db.Column(db.Integer)
    application_mime_type = db.Column(db.String(100))
    application_file_hash = db.Column(db.String(64), unique=True)
    
    # Status and Approval
    status = db.Column(db.Enum(ODStatus), default=ODStatus.PENDING, nullable=False)
    approval_comments = db.Column(db.Text)
    approved_at = db.Column(db.DateTime(timezone=True))
    
    # Proof Submission
    proof_submission_status = db.Column(db.Enum(ProofStatus), default=ProofStatus.NOT_SUBMITTED)
    
    # Deadline tracking
    attendance_proof_deadline = db.Column(db.DateTime(timezone=True))
    certificate_submission_deadline = db.Column(db.DateTime(timezone=True))
    
    # Attendance Proof
    attendance_proof_filename = db.Column(db.String(255))
    attendance_proof_original_name = db.Column(db.String(255))
    attendance_proof_file_path = db.Column(db.String(500))
    attendance_proof_file_size = db.Column(db.Integer)
    attendance_proof_mime_type = db.Column(db.String(100))
    attendance_proof_file_hash = db.Column(db.String(64))
    attendance_proof_submitted_at = db.Column(db.DateTime(timezone=True))
    
    # Certificate
    certificate_filename = db.Column(db.String(255))
    certificate_original_name = db.Column(db.String(255))
    certificate_file_path = db.Column(db.String(500))
    certificate_file_size = db.Column(db.Integer)
    certificate_mime_type = db.Column(db.String(100))
    certificate_file_hash = db.Column(db.String(64))
    certificate_submitted_at = db.Column(db.DateTime(timezone=True))
    
    # OCR Validation (stored as JSON)
    ocr_validation_result = db.Column(db.Text)  # JSON string
    
    # Timestamps
    last_reminder_sent = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_student_status', 'student_id', 'status'),
        db.Index('idx_date_range', 'from_date', 'to_date'),
        db.Index('idx_od_type', 'od_type'),
    )
    
    def set_ocr_validation(self, validation_data):
        """Store OCR validation results as JSON"""
        self.ocr_validation_result = json.dumps(validation_data)
    
    def get_ocr_validation(self):
        """Retrieve OCR validation results from JSON"""
        if self.ocr_validation_result:
            return json.loads(self.ocr_validation_result)
        return None
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary, optionally including sensitive data"""
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'faculty_id': self.faculty_id,
            'event_name': self.event_name,
            'event_description': self.event_description,
            'from_date': self.from_date.isoformat() if self.from_date else None,
            'to_date': self.to_date.isoformat() if self.to_date else None,
            'od_type': self.od_type.value if self.od_type else None,
            'college_name': self.college_name,
            'host_institution': self.host_institution,
            'venue': self.venue,
            'location_type': self.location_type,
            'status': self.status.value if self.status else None,
            'approval_comments': self.approval_comments,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'proof_submission_status': self.proof_submission_status.value if self.proof_submission_status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include file information
        data['application_file'] = {
            'filename': self.application_original_name,
            'size': self.application_file_size,
            'mime_type': self.application_mime_type
        } if self.application_filename else None
        
        data['attendance_proof'] = {
            'filename': self.attendance_proof_original_name,
            'size': self.attendance_proof_file_size,
            'mime_type': self.attendance_proof_mime_type,
            'uploaded_at': self.attendance_proof_submitted_at.isoformat() if self.attendance_proof_submitted_at else None
        } if self.attendance_proof_filename else None
        
        data['certificate'] = {
            'filename': self.certificate_original_name,
            'size': self.certificate_file_size,
            'mime_type': self.certificate_mime_type,
            'uploaded_at': self.certificate_submitted_at.isoformat() if self.certificate_submitted_at else None
        } if self.certificate_filename else None
        
        # Include deadline information
        data['deadlines'] = {
            'attendance_proof_deadline': self.attendance_proof_deadline.isoformat() if self.attendance_proof_deadline else None,
            'certificate_deadline': self.certificate_submission_deadline.isoformat() if self.certificate_submission_deadline else None,
            'is_attendance_proof_overdue': self.is_attendance_proof_overdue,
            'is_certificate_overdue': self.is_certificate_overdue,
            'days_until_attendance_deadline': self.days_until_attendance_deadline,
            'days_until_certificate_deadline': self.days_until_certificate_deadline,
            'has_pending_proofs': self.has_pending_proofs
        }
        
        if include_sensitive:
            data['ocr_validation'] = self.get_ocr_validation()
            data['last_reminder_sent'] = self.last_reminder_sent.isoformat() if self.last_reminder_sent else None
        
        return data
    
    @property
    def is_proof_submission_allowed(self):
        """Check if proof submission is allowed"""
        if self.status != ODStatus.APPROVED:
            return False
        
        current_date = datetime.now().date()
        return current_date >= self.to_date
    
    def set_approval_deadlines(self):
        """Set deadlines when OD is approved"""
        if self.approved_at:
            # Attendance proof deadline: 3 days after approval
            self.attendance_proof_deadline = self.approved_at + timedelta(days=3)
    
    def set_certificate_deadline(self):
        """Set certificate deadline when attendance proof is submitted"""
        if self.attendance_proof_submitted_at:
            # Certificate deadline: 1 month (30 days) after attendance proof submission
            self.certificate_submission_deadline = self.attendance_proof_submitted_at + timedelta(days=30)
    
    @property
    def is_attendance_proof_overdue(self):
        """Check if attendance proof submission is overdue"""
        if not self.attendance_proof_deadline or self.attendance_proof_submitted_at:
            return False
        return datetime.now(timezone.utc) > self.attendance_proof_deadline
    
    @property
    def is_certificate_overdue(self):
        """Check if certificate submission is overdue"""
        if not self.certificate_submission_deadline or self.certificate_submitted_at:
            return False
        return datetime.now(timezone.utc) > self.certificate_submission_deadline
    
    @property
    def has_pending_proofs(self):
        """Check if student has pending proof submissions"""
        if self.status != ODStatus.APPROVED:
            return False
        
        # If attendance proof not submitted and deadline passed
        if not self.attendance_proof_submitted_at and self.is_attendance_proof_overdue:
            return True
        
        # If certificate not submitted and deadline passed
        if self.attendance_proof_submitted_at and not self.certificate_submitted_at and self.is_certificate_overdue:
            return True
        
        return False
    
    @property
    def days_until_attendance_deadline(self):
        """Get days remaining until attendance proof deadline"""
        if not self.attendance_proof_deadline or self.attendance_proof_submitted_at:
            return None
        
        delta = self.attendance_proof_deadline - datetime.now(timezone.utc)
        return delta.days if delta.days >= 0 else 0
    
    @property
    def days_until_certificate_deadline(self):
        """Get days remaining until certificate deadline"""
        if not self.certificate_submission_deadline or self.certificate_submitted_at:
            return None
        
        delta = self.certificate_submission_deadline - datetime.now(timezone.utc)
        return delta.days if delta.days >= 0 else 0
    
    @property
    def has_active_od_conflict(self):
        """Check if there's an active OD conflict for the same student"""
        return ODRequest.query.filter(
            ODRequest.student_id == self.student_id,
            ODRequest.id != self.id,
            ODRequest.status == ODStatus.APPROVED,
            db.or_(
                db.and_(ODRequest.from_date <= self.from_date, ODRequest.to_date >= self.from_date),
                db.and_(ODRequest.from_date <= self.to_date, ODRequest.to_date >= self.to_date),
                db.and_(ODRequest.from_date >= self.from_date, ODRequest.to_date <= self.to_date)
            )
        ).first() is not None