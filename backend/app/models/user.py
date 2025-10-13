"""
User models for the OD Management System
"""
from app import db
from .enums import UserRole
from datetime import datetime, timezone

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Student Details
    student_id = db.Column(db.String(20), unique=True, nullable=False)  # Roll number
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Academic Details
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    section = db.Column(db.String(10))
    batch = db.Column(db.String(20))
    
    # Contact Information
    phone = db.Column(db.String(15))
    parent_phone = db.Column(db.String(15))
    
    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    od_requests = db.relationship('ODRequest', backref='student', lazy=True)
    
    def to_dict(self):
        """Convert student to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'year': self.year,
            'section': self.section,
            'batch': self.batch,
            'phone': self.phone,
            'parent_phone': self.parent_phone,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Faculty(db.Model):
    __tablename__ = 'faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Faculty Details
    faculty_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Academic Details
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100))  # Professor, Assistant Professor, etc.
    role = db.Column(db.Enum(UserRole), default=UserRole.FACULTY, nullable=False)
    
    # Contact Information
    phone = db.Column(db.String(15))
    office_location = db.Column(db.String(100))
    
    # Permissions
    can_approve_intra_college = db.Column(db.Boolean, default=True)
    can_approve_inter_college = db.Column(db.Boolean, default=False)
    is_hod = db.Column(db.Boolean, default=False)
    
    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    approved_requests = db.relationship('ODRequest', backref='approving_faculty', lazy=True)
    
    def to_dict(self):
        """Convert faculty to dictionary"""
        return {
            'id': self.id,
            'faculty_id': self.faculty_id,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'designation': self.designation,
            'role': self.role.value if self.role else None,
            'phone': self.phone,
            'office_location': self.office_location,
            'can_approve_intra_college': self.can_approve_intra_college,
            'can_approve_inter_college': self.can_approve_inter_college,
            'is_hod': self.is_hod,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def can_approve_od_type(self):
        """Check what types of OD this faculty can approve"""
        from .enums import ODType
        
        if self.is_hod:
            return [ODType.INTRA_COLLEGE, ODType.INTER_COLLEGE_COIMBATORE, ODType.INTER_COLLEGE_OTHERS]
        elif self.can_approve_inter_college:
            return [ODType.INTRA_COLLEGE, ODType.INTER_COLLEGE_COIMBATORE, ODType.INTER_COLLEGE_OTHERS]
        elif self.can_approve_intra_college:
            return [ODType.INTRA_COLLEGE]
        else:
            return []