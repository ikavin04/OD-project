"""
OD Management System - Single Backend File
Complete Flask application with all functionality in one file
"""

import os
import sys
import uuid
import hashlib
import json
import enum
import logging
from datetime import datetime, date, timedelta, timezone
from typing import Optional, List, Dict, Any

# Flask and extensions
from flask import Flask, request, jsonify, send_file, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, create_refresh_token, get_jwt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:Manisha14@localhost:5432/OD'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'vijayarajm2308@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'khbtrvvazhskyguu'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'vijayarajm2308@gmail.com'
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # Pagination
    POSTS_PER_PAGE = 20

# ============================================================================
# APPLICATION SETUP
# ============================================================================

app = Flask(__name__)
app.config.from_object(Config)

# Explicitly set mail configuration to ensure it's not overridden
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'vijayarajm2308@gmail.com'
app.config['MAIL_PASSWORD'] = 'khbtrvvazhskyguu'
app.config['MAIL_DEFAULT_SENDER'] = 'vijayarajm2308@gmail.com'
app.config['MAIL_DEBUG'] = True
app.config['MAIL_SUPPRESS_SEND'] = False

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app, 
    origins=["http://localhost:3003", "http://localhost:3002", "http://localhost:3001", "http://localhost:3000", "http://127.0.0.1:3003", "http://127.0.0.1:3002", "http://127.0.0.1:3001", "http://127.0.0.1:3000"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    expose_headers=["Content-Type", "Authorization"]
)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

# Debug: Print actual mail configuration
print(f"🔧 Mail Configuration Debug:")
print(f"   MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
print(f"   MAIL_PASSWORD: {'*' * len(app.config.get('MAIL_PASSWORD', '')) if app.config.get('MAIL_PASSWORD') else 'None'}")
print(f"   MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")

mail = Mail(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================================================
# ENUMS
# ============================================================================

class UserRole(enum.Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    HOD = "hod"
    ADMIN = "admin"

class ODStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ODType(enum.Enum):
    INTRA_COLLEGE = "intra_college"
    INTER_COLLEGE_COIMBATORE = "inter_college_coimbatore"
    INTER_COLLEGE_OTHERS = "inter_college_others"

class ProofStatus(enum.Enum):
    NOT_SUBMITTED = "NOT_SUBMITTED"
    attendance_pending = "attendance_pending"  # Within 3 days after approval
    ATTENDANCE_SUBMITTED = "ATTENDANCE_SUBMITTED"
    certificate_pending = "certificate_pending"  # Within 1 month after attendance
    certificate_submitted = "certificate_submitted"
    COMPLETED = "COMPLETED"

# ============================================================================
# DATABASE MODELS
# ============================================================================

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(15))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    od_requests = db.relationship('ODRequest', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'roll_number': self.roll_number,
            'email': self.email,
            'name': self.name,
            'department': self.department,
            'year': self.year,
            'semester': self.semester,
            'phone_number': self.phone_number,
            'role': 'student',
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Faculty(db.Model):
    __tablename__ = 'faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15))
    role = db.Column(db.Enum(UserRole), default=UserRole.FACULTY, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    od_requests = db.relationship('ODRequest', backref='faculty', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'email': self.email,
            'name': self.name,
            'department': self.department,
            'phone_number': self.phone_number,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

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
    
    # Application File - Stored in Database
    application_filename = db.Column(db.String(255), nullable=False)
    application_original_name = db.Column(db.String(255), nullable=False)
    application_file_data = db.Column(db.LargeBinary, nullable=False)  # Store actual file in DB
    application_file_size = db.Column(db.Integer)
    application_mime_type = db.Column(db.String(100))
    application_file_hash = db.Column(db.String(64), unique=True)
    
    # Status and Approval
    status = db.Column(db.Enum(ODStatus), default=ODStatus.PENDING, nullable=False)
    approval_comments = db.Column(db.Text)
    approved_at = db.Column(db.DateTime(timezone=True))
    
    # Proof Submission
    proof_submission_status = db.Column(db.Enum(ProofStatus), default=ProofStatus.NOT_SUBMITTED)
    
    # Proof submission deadlines
    attendance_proof_deadline = db.Column(db.DateTime(timezone=True))  # 3 days after approval
    certificate_deadline = db.Column(db.DateTime(timezone=True))  # 1 month after attendance submission
    
    # Attendance proof file - Stored in Database
    attendance_proof_filename = db.Column(db.String(255))
    attendance_proof_original_name = db.Column(db.String(255))
    attendance_proof_file_data = db.Column(db.LargeBinary)  # Store actual file in DB
    attendance_proof_file_size = db.Column(db.Integer)
    attendance_proof_mime_type = db.Column(db.String(100))
    attendance_proof_submitted_at = db.Column(db.DateTime(timezone=True))
    
    # Certificate file - Stored in Database
    certificate_filename = db.Column(db.String(255))
    certificate_original_name = db.Column(db.String(255))
    certificate_file_data = db.Column(db.LargeBinary)  # Store actual file in DB
    certificate_file_size = db.Column(db.Integer)
    certificate_mime_type = db.Column(db.String(100))
    certificate_submitted_at = db.Column(db.DateTime(timezone=True))
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        # Create application_file object if file exists in database
        application_file = None
        if self.application_filename and self.application_file_data:
            application_file = {
                'filename': self.application_original_name or self.application_filename,
                'size': self.application_file_size or 0,
                'mime_type': self.application_mime_type or 'application/octet-stream',
                'has_file_data': True,  # Indicate file is stored in database
                'file_id': self.id  # Use for download endpoint
            }
        
        # Create attendance proof file object if file exists in database
        attendance_proof_file = None
        if self.attendance_proof_filename and self.attendance_proof_file_data:
            attendance_proof_file = {
                'filename': self.attendance_proof_original_name or self.attendance_proof_filename,
                'size': self.attendance_proof_file_size or 0,
                'mime_type': self.attendance_proof_mime_type or 'application/octet-stream',
                'has_file_data': True,  # Indicate file is stored in database
                'file_id': self.id  # Use for download endpoint
            }
        # Frontend compatibility alias
        attendance_proof = None
        if attendance_proof_file:
            attendance_proof = {
                'filename': attendance_proof_file['filename'],
                'size': attendance_proof_file['size'],
                'mime_type': attendance_proof_file['mime_type'],
                'uploaded_at': self.attendance_proof_submitted_at.isoformat() if self.attendance_proof_submitted_at else None
            }
        
        # Create certificate file object if file exists in database
        certificate_file = None
        if self.certificate_filename and self.certificate_file_data:
            certificate_file = {
                'filename': self.certificate_original_name or self.certificate_filename,
                'size': self.certificate_file_size or 0,
                'mime_type': self.certificate_mime_type or 'application/octet-stream',
                'has_file_data': True,  # Indicate file is stored in database
                'file_id': self.id  # Use for download endpoint
            }
        # Frontend compatibility alias
        certificate = None
        if certificate_file:
            certificate = {
                'filename': certificate_file['filename'],
                'size': certificate_file['size'],
                'mime_type': certificate_file['mime_type'],
                'uploaded_at': self.certificate_submitted_at.isoformat() if self.certificate_submitted_at else None
            }
        
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
            'application_filename': self.application_filename,
            'application_original_name': self.application_original_name,
            'application_file': application_file,  # New: Complete file info for frontend
            'status': self.status.value if self.status else None,
            'approval_comments': self.approval_comments,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'proof_submission_status': self.proof_submission_status.value if self.proof_submission_status else None,
            'attendance_proof_deadline': self.attendance_proof_deadline.isoformat() if self.attendance_proof_deadline else None,
            'certificate_deadline': self.certificate_deadline.isoformat() if self.certificate_deadline else None,
            'attendance_proof_file': attendance_proof_file,
            'attendance_proof_submitted_at': self.attendance_proof_submitted_at.isoformat() if self.attendance_proof_submitted_at else None,
            'certificate_file': certificate_file,
            'certificate_submitted_at': self.certificate_submitted_at.isoformat() if self.certificate_submitted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'student': self.student.to_dict() if self.student else None
        }

        # Add compatibility fields used by the current frontend
        data['attendance_proof'] = attendance_proof
        data['certificate'] = certificate
        data['deadlines'] = {
            'attendance_proof_deadline': data['attendance_proof_deadline'],
            'certificate_deadline': data['certificate_deadline']
        }
        return data

# ============================================================================
# EMAIL SERVICE
# ============================================================================

def send_od_status_email(student_email: str, student_name: str, od_request: ODRequest, 
                        status: str, faculty_name: str, comments: str = "") -> bool:
    """Send email notification for OD request status update"""
    try:
        # Create email subject
        status_emoji = "✅" if status == "approved" else "❌"
        subject = f"{status_emoji} OD Request {status.title()} - {od_request.event_name}"
        
        # Create HTML email content
        if status == "approved":
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
                <div style="background: linear-gradient(135deg, #28a745, #20c997); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">🎓 KGISL College</h1>
                    <h2 style="margin: 10px 0 0 0; font-size: 20px;">OD Request Approved</h2>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: #28a745; margin-top: 0;">🎉 Great News, {student_name}!</h3>
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">Your On-Duty request has been <strong style="color: #28a745;">APPROVED</strong>.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                        <h4 style="margin: 0 0 15px 0; color: #333;">📋 Request Details:</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #555;">
                            <li><strong>Event:</strong> {od_request.event_name}</li>
                            <li><strong>Duration:</strong> {od_request.from_date} to {od_request.to_date}</li>
                            <li><strong>Institution:</strong> {od_request.host_institution or od_request.college_name or 'N/A'}</li>
                            <li><strong>Status:</strong> <span style="color: #28a745; font-weight: bold;">✅ APPROVED</span></li>
                        </ul>
                    </div>
                    
                    {f'<div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;"><h4 style="margin: 0 0 10px 0; color: #1976d2;">👩‍🏫 Faculty Comments:</h4><p style="margin: 0; font-style: italic; color: #333;">"{comments}"</p></div>' if comments else ''}
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #ffeaa7;">
                        <h4 style="margin: 0 0 10px 0; color: #856404;">🎯 Important - Proof Submission Requirements:</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #856404;">
                            <li><strong>Step 1:</strong> Submit attendance proof (event brochure/live photo) within <strong>3 days</strong> after approval</li>
                            <li><strong>Step 2:</strong> Submit participation certificate within <strong>1 month</strong> after attendance proof</li>
                            <li><strong>Important:</strong> You cannot apply for new ODs until all proofs are submitted</li>
                            <li>Login to your student portal to upload proof documents</li>
                        </ul>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; margin: 30px 0 0 0; text-align: center;">
                        Best regards,<br>
                        <strong>{faculty_name}</strong><br>
                        Faculty Team, KGISL College
                    </p>
                </div>
            </div>
            """
        else:
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
                <div style="background: linear-gradient(135deg, #dc3545, #c82333); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">🎓 KGISL College</h1>
                    <h2 style="margin: 10px 0 0 0; font-size: 20px;">OD Request Update</h2>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: #dc3545; margin-top: 0;">Dear {student_name},</h3>
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">Your On-Duty request has been reviewed and <strong style="color: #dc3545;">rejected</strong>.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc3545;">
                        <h4 style="margin: 0 0 15px 0; color: #333;">📋 Request Details:</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #555;">
                            <li><strong>Event:</strong> {od_request.event_name}</li>
                            <li><strong>Duration:</strong> {od_request.from_date} to {od_request.to_date}</li>
                            <li><strong>Institution:</strong> {od_request.host_institution or od_request.college_name or 'N/A'}</li>
                            <li><strong>Status:</strong> <span style="color: #dc3545; font-weight: bold;">❌ REJECTED</span></li>
                        </ul>
                    </div>
                    
                    {f'<div style="background-color: #f8d7da; padding: 15px; border-radius: 8px; margin: 20px 0;"><h4 style="margin: 0 0 10px 0; color: #721c24;">👩‍🏫 Faculty Comments:</h4><p style="margin: 0; font-style: italic; color: #721c24;">"{comments}"</p></div>' if comments else ''}
                    
                    <div style="background-color: #d1ecf1; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #b8daff;">
                        <h4 style="margin: 0 0 10px 0; color: #0c5460;">📝 What to do next:</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #0c5460;">
                            <li>Review the feedback provided</li>
                            <li>Modify your request if possible</li>
                            <li>Resubmit with alternative dates</li>
                        </ul>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; margin: 30px 0 0 0; text-align: center;">
                        For questions, contact the faculty office.<br><br>
                        Best regards,<br>
                        <strong>{faculty_name}</strong><br>
                        Faculty Team, KGISL College
                    </p>
                </div>
            </div>
            """
        
        # Create and send email
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[student_email],
            html=html_content
        )
        
        mail.send(msg)
        print(f"✅ Email sent successfully to {student_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {student_email}: {str(e)}")
        # Log in DEMO MODE
        print(f"📧 DEMO MODE - Email would be sent:")
        print(f"   To: {student_email}")
        print(f"   Subject: {subject}")
        print(f"   Status: {status}")
        print(f"   Faculty: {faculty_name}")
        return False

# ============================================================================
# FILE HANDLING
# ============================================================================

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_file_to_database(file):
    """Save uploaded file directly to database and return file info"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Read file content
    file_content = file.read()
    file.seek(0)  # Reset file pointer for any other operations
    
    # Generate file hash for deduplication
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Generate secure filename
    filename = secure_filename(file.filename)
    
    return {
        'filename': f"{file_hash}_{filename}",
        'original_name': filename,
        'file_data': file_content,  # Binary data for database
        'file_size': len(file_content),
        'mime_type': file.content_type or 'application/octet-stream',
        'file_hash': file_hash
    }

# Legacy function for backward compatibility (now redirects to database storage)
def save_file(file, upload_folder="uploads"):
    """Legacy function - now saves to database instead of file system"""
    return save_file_to_database(file)

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/auth/student/register', methods=['POST'])
@limiter.limit("5 per minute")
def student_register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['roll_number', 'email', 'password', 'name', 'department', 'year', 'semester']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if student already exists
    if Student.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if Student.query.filter_by(roll_number=data['roll_number']).first():
        return jsonify({'error': 'Roll number already registered'}), 400
    
    # Create new student
    student = Student(
        roll_number=data['roll_number'],
        email=data['email'],
        name=data['name'],
        department=data['department'],
        year=int(data['year']),
        semester=int(data['semester']),
        phone_number=data.get('phone_number')
    )
    student.set_password(data['password'])
    
    try:
        db.session.add(student)
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(
            identity={'id': student.id, 'email': student.email, 'role': 'student'}
        )
        
        return jsonify({
            'message': 'Student registered successfully',
            'access_token': access_token,
            'user': student.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/student/login', methods=['POST'])
@limiter.limit("10 per minute")
def student_login():
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    student = Student.query.filter_by(email=data['email']).first()
    
    if not student or not student.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not student.is_active:
        return jsonify({'error': 'Account is deactivated'}), 401
    
    # Update last login
    student.last_login = datetime.now(timezone.utc)
    db.session.commit()
    
    # Create tokens
    access_token = create_access_token(
        identity={'id': student.id, 'email': student.email, 'role': 'student'}
    )
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': student.to_dict()
    }), 200

@app.route('/api/auth/faculty/login', methods=['POST'])
@limiter.limit("10 per minute")
def faculty_login():
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    faculty = Faculty.query.filter_by(email=data['email']).first()
    
    if not faculty or not faculty.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not faculty.is_active:
        return jsonify({'error': 'Account is deactivated'}), 401
    
    # Update last login
    faculty.last_login = datetime.now(timezone.utc)
    db.session.commit()
    
    # Create tokens
    access_token = create_access_token(
        identity={'id': faculty.id, 'email': faculty.email, 'role': faculty.role.value}
    )
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': faculty.to_dict()
    }), 200

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def general_login():
    """General login route that detects user type automatically"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data['email']
    password = data['password']
    
    # Try student login first
    student = Student.query.filter_by(email=email).first()
    if student and student.check_password(password):
        if not student.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        student.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(
            identity=str(student.id),
            additional_claims={'role': 'student', 'email': student.email}
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': student.to_dict()
        }), 200
    
    # Try faculty login
    faculty = Faculty.query.filter_by(email=email).first()
    if faculty and faculty.check_password(password):
        if not faculty.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        faculty.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(
            identity=str(faculty.id),
            additional_claims={'role': faculty.role.value, 'email': faculty.email}
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': faculty.to_dict()
        }), 200
    
    # No valid user found
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information from token"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] == 'student':
        user = Student.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({
            'user': user.to_dict(),
            'role': 'student'
        }), 200
    else:
        user = Faculty.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({
            'user': user.to_dict(),
            'role': claims['role']
        }), 200

# ============================================================================
# OD REQUEST ROUTES
# ============================================================================

@app.route('/api/od-requests', methods=['POST'])
@jwt_required()
def create_od_request():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] != 'student':
        return jsonify({'error': 'Only students can create OD requests'}), 403
    
    # Check if student has any pending proof submissions
    pending_proofs = ODRequest.query.filter(
        ODRequest.student_id == user_id,
        ODRequest.status == ODStatus.APPROVED,
        ODRequest.proof_submission_status.in_([
            ProofStatus.attendance_pending,
            ProofStatus.ATTENDANCE_SUBMITTED,
            ProofStatus.certificate_pending
        ])
    ).first()
    
    if pending_proofs:
        if pending_proofs.proof_submission_status == ProofStatus.attendance_pending:
            deadline = pending_proofs.attendance_proof_deadline
            proof_type = "attendance proof (event brochure or live photo)"
        elif pending_proofs.proof_submission_status in [ProofStatus.ATTENDANCE_SUBMITTED, ProofStatus.certificate_pending]:
            deadline = pending_proofs.certificate_deadline
            proof_type = "participation certificate"
        
        return jsonify({
            'error': f'You have pending {proof_type} submission for event "{pending_proofs.event_name}". Please submit your proof by {deadline.strftime("%d-%m-%Y %H:%M")} before applying for new ODs.',
            'pending_request': pending_proofs.to_dict()
        }), 400
    
    # Get form data
    data = request.form
    file = request.files.get('application_file')
    
    if not file:
        return jsonify({'error': 'Application file is required'}), 400
    
    # Validate required fields
    required_fields = ['event_name', 'from_date', 'to_date', 'od_type']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Save file to database
    file_info = save_file_to_database(file)
    if not file_info:
        return jsonify({'error': 'Invalid file format'}), 400
    
    # Create OD request
    od_request = ODRequest(
        student_id=user_id,
        event_name=data['event_name'],
        event_description=data.get('event_description'),
        from_date=datetime.strptime(data['from_date'], '%Y-%m-%d').date(),
        to_date=datetime.strptime(data['to_date'], '%Y-%m-%d').date(),
        od_type=ODType(data['od_type']),
        college_name=data.get('college_name'),
        host_institution=data.get('host_institution'),
        venue=data.get('venue'),
        location_type=data.get('location_type'),
        application_filename=file_info['filename'],
        application_original_name=file_info['original_name'],
        application_file_data=file_info['file_data'],  # Store binary data
        application_file_size=file_info['file_size'],
        application_mime_type=file_info['mime_type'],
        application_file_hash=file_info['file_hash']
    )
    
    try:
        db.session.add(od_request)
        db.session.commit()
        
        return jsonify({
            'message': 'OD request created successfully',
            'od_request': od_request.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create OD request'}), 500

@app.route('/api/od-requests', methods=['GET'])
@jwt_required()
def get_od_requests():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] == 'student':
        # Students see only their own requests
        od_requests = ODRequest.query.filter_by(student_id=user_id).all()
    else:
        # Faculty/Admin see all requests
        od_requests = ODRequest.query.all()
    
    # Refresh all objects to ensure we have latest data
    for od in od_requests:
        db.session.refresh(od)
    
    return jsonify({
        'od_requests': [od.to_dict() for od in od_requests]
    }), 200

# Faculty-specific endpoint (alias for the same functionality)
@app.route('/api/faculty/od-requests', methods=['GET'])
@jwt_required()
def get_faculty_od_requests():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    # Only faculty can access this endpoint
    if claims['role'] not in ['faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Faculty see all requests
    od_requests = ODRequest.query.all()
    
    return jsonify({
        'od_requests': [od.to_dict() for od in od_requests]
    }), 200

# Student-specific endpoint (alias for the same functionality)
@app.route('/api/student/od-requests', methods=['GET'])
@jwt_required()
def get_student_od_requests():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    # Only students can access this endpoint
    if claims['role'] != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    # Students see only their own requests
    od_requests = ODRequest.query.filter_by(student_id=user_id).all()
    
    # Refresh to ensure latest values
    for od in od_requests:
        db.session.refresh(od)
    
    return jsonify({
        'od_requests': [od.to_dict() for od in od_requests]
    }), 200

# Student OD request submission endpoint
@app.route('/api/student/od-request', methods=['POST'])
@jwt_required()
def submit_student_od_request():
    # This is an alias to the main OD request creation endpoint
    return create_od_request()

# Student profile endpoint
@app.route('/api/student/profile', methods=['GET'])
@jwt_required()
def get_student_profile():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.get(user_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify({'student': student.to_dict()}), 200

# Faculty profile endpoint
@app.route('/api/faculty/profile', methods=['GET'])
@jwt_required()
def get_faculty_profile():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] not in ['faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    faculty = Faculty.query.get(user_id)
    if not faculty:
        return jsonify({'error': 'Faculty not found'}), 404
    
    return jsonify({'faculty': faculty.to_dict()}), 200

# Faculty approval endpoint
@app.route('/api/faculty/od-requests/<int:request_id>/approve', methods=['POST'])
@jwt_required()
def faculty_approve_od_request(request_id):
    # This is an alias to the main approval endpoint
    return approve_od_request(request_id)

# Faculty rejection endpoint
@app.route('/api/faculty/od-requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def faculty_reject_od_request(request_id):
    # This is an alias to the main rejection endpoint
    return reject_od_request(request_id)

@app.route('/api/od-requests/<int:request_id>/approve', methods=['POST'])
@jwt_required()
def approve_od_request(request_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] not in ['faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    od_request = ODRequest.query.get_or_404(request_id)
    data = request.get_json()
    
    # Update request
    od_request.status = ODStatus.APPROVED
    od_request.approval_comments = data.get('comments', '')
    od_request.faculty_id = user_id
    od_request.approved_at = datetime.now(timezone.utc)
    
    # Set proof submission deadlines
    # Attendance proof deadline: 3 days after approval
    od_request.attendance_proof_deadline = datetime.now(timezone.utc) + timedelta(days=3)
    od_request.proof_submission_status = ProofStatus.attendance_pending
    
    try:
        db.session.commit()
        
        # Send email notification
        faculty = Faculty.query.get(user_id)
        print(f"📧 Sending approval email to {od_request.student.email}")
        email_sent = send_od_status_email(
            student_email=od_request.student.email,
            student_name=od_request.student.name,
            od_request=od_request,
            status='approved',
            faculty_name=faculty.name,
            comments=od_request.approval_comments
        )
        print(f"📧 Email sent result: {email_sent}")
        
        return jsonify({
            'message': 'OD request approved successfully. Student must submit attendance proof within 3 days.',
            'od_request': od_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to approve request'}), 500

@app.route('/api/od-requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_od_request(request_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] not in ['faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    od_request = ODRequest.query.get_or_404(request_id)
    data = request.get_json()
    
    # Update request
    od_request.status = ODStatus.REJECTED
    od_request.approval_comments = data.get('comments', '')
    od_request.faculty_id = user_id
    od_request.approved_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        # Send email notification
        faculty = Faculty.query.get(user_id)
        print(f"📧 Sending rejection email to {od_request.student.email}")
        email_sent = send_od_status_email(
            student_email=od_request.student.email,
            student_name=od_request.student.name,
            od_request=od_request,
            status='rejected',
            faculty_name=faculty.name,
            comments=od_request.approval_comments
        )
        print(f"📧 Email sent result: {email_sent}")
        
        return jsonify({
            'message': 'OD request rejected successfully',
            'od_request': od_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reject request'}), 500

@app.route('/api/od-requests/<int:request_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_od_request(request_id):
    current_user = get_jwt_identity()
    
    od_request = ODRequest.query.get_or_404(request_id)
    
    # Check permissions
    if current_user['role'] == 'student' and od_request.student_id != current_user['id']:
        return jsonify({'error': 'Access denied'}), 403
    elif current_user['role'] not in ['student', 'faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Delete associated file
        if os.path.exists(od_request.application_file_path):
            os.remove(od_request.application_file_path)
        
        db.session.delete(od_request)
        db.session.commit()
        
        return jsonify({'message': 'OD request deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete request'}), 500

@app.route('/api/od-requests/<int:request_id>/file')
@jwt_required()
def view_od_file(request_id):
    od_request = ODRequest.query.get_or_404(request_id)
    
    if not os.path.exists(od_request.application_file_path):
        abort(404)
    
    return send_file(
        od_request.application_file_path,
        as_attachment=False,
        download_name=od_request.application_original_name
    )

@app.route('/api/od-requests/<int:request_id>/download')
@jwt_required()
def download_od_file(request_id):
    od_request = ODRequest.query.get_or_404(request_id)
    
    if not os.path.exists(od_request.application_file_path):
        abort(404)
    
    return send_file(
        od_request.application_file_path,
        as_attachment=True,
        download_name=od_request.application_original_name
    )

@app.route('/api/od/view/<int:request_id>/<string:file_type>')
@jwt_required()
def view_od_application_file(request_id, file_type):
    """View OD application file from database"""
    od_request = ODRequest.query.get_or_404(request_id)
    
    # Serve file from database
    if file_type == 'application' and od_request.application_file_data:
        return Response(
            od_request.application_file_data,
            mimetype=od_request.application_mime_type or 'application/octet-stream',
            headers={
                'Content-Disposition': f'inline; filename="{od_request.application_original_name}"',
                'Content-Length': str(len(od_request.application_file_data))
            }
        )
    elif file_type in ['attendance', 'attendance_proof'] and od_request.attendance_proof_file_data:
        return Response(
            od_request.attendance_proof_file_data,
            mimetype=od_request.attendance_proof_mime_type or 'application/octet-stream',
            headers={
                'Content-Disposition': f'inline; filename="{od_request.attendance_proof_original_name}"',
                'Content-Length': str(len(od_request.attendance_proof_file_data))
            }
        )
    elif file_type == 'certificate' and od_request.certificate_file_data:
        return Response(
            od_request.certificate_file_data,
            mimetype=od_request.certificate_mime_type or 'application/octet-stream',
            headers={
                'Content-Disposition': f'inline; filename="{od_request.certificate_original_name}"',
                'Content-Length': str(len(od_request.certificate_file_data))
            }
        )
    
    return jsonify({'error': 'File not found in database'}), 404

@app.route('/api/od/download/<int:request_id>/<string:file_type>')
@jwt_required()
def download_od_application_file(request_id, file_type):
    """Download OD application file (for frontend compatibility)"""
    od_request = ODRequest.query.get_or_404(request_id)
    
    # Check if file exists - try multiple paths
    file_path = None
    if od_request.application_file_path:
        # Try the stored path first
        if os.path.exists(od_request.application_file_path):
            file_path = od_request.application_file_path
        else:
            # Try absolute path
            abs_path = os.path.abspath(od_request.application_file_path)
            if os.path.exists(abs_path):
                file_path = abs_path
            # Try with od-applications subfolder
            elif os.path.exists(os.path.join('uploads', 'od-applications', od_request.application_filename)):
                file_path = os.path.join('uploads', 'od-applications', od_request.application_filename)
            # Try uploads root with just filename
            elif os.path.exists(os.path.join('uploads', od_request.application_filename)):
                file_path = os.path.join('uploads', od_request.application_filename)
    
    if not file_path:
        print(f"File not found for OD request {request_id}")
        print(f"  Stored path: {od_request.application_file_path}")
        print(f"  Filename: {od_request.application_filename}")
        return jsonify({'error': 'File not found'}), 404
    
    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=od_request.application_original_name,
            mimetype=od_request.application_mime_type or 'application/octet-stream'
        )
    except Exception as e:
        print(f"Error serving file: {str(e)}")
        return jsonify({'error': 'Failed to serve file'}), 500

# ============================================================================
# UTILITY ROUTES
# ============================================================================

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with helpful message"""
    return jsonify({
        'message': 'OD Management System Backend API',
        'status': 'running',
        'frontend_url': 'http://localhost:3000',
        'api_docs': 'This is the backend API. Please access the frontend at http://localhost:3000',
        'version': '1.0.0'
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/api/od-requests/<int:request_id>/submit-attendance-proof', methods=['POST'])
@jwt_required()
def submit_attendance_proof(request_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] != 'student':
        return jsonify({'error': 'Only students can submit proof'}), 403
    
    od_request = ODRequest.query.get_or_404(request_id)
    
    # Check if this is the student's request
    if od_request.student_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if request is approved
    if od_request.status != ODStatus.APPROVED:
        return jsonify({'error': 'OD request must be approved first'}), 400
    
    # Check if attendance proof is already submitted
    existing_attendance_proof = any([
        od_request.attendance_proof_filename,
        od_request.attendance_proof_original_name,
        od_request.attendance_proof_file_data,
        od_request.attendance_proof_submitted_at
    ])

    if existing_attendance_proof:
        db.session.refresh(od_request)
        return jsonify({
            'message': 'Attendance proof already submitted',
            'od_request': od_request.to_dict()
        }), 200
    
    # Set default status if not set
    if od_request.proof_submission_status == ProofStatus.NOT_SUBMITTED:
        od_request.proof_submission_status = ProofStatus.attendance_pending
        # Set deadline if not set
        if not od_request.attendance_proof_deadline:
            od_request.attendance_proof_deadline = datetime.now(timezone.utc) + timedelta(days=3)
    
    # Get uploaded file
    file = request.files.get('attendance_proof')
    if not file:
        return jsonify({'error': 'Attendance proof file is required'}), 400
    
    # Save file to database
    file_info = save_file_to_database(file)
    if not file_info:
        return jsonify({'error': 'Invalid file format'}), 400
    
    # Update OD request with attendance proof
    od_request.attendance_proof_filename = file_info['filename']
    od_request.attendance_proof_original_name = file_info['original_name']
    od_request.attendance_proof_file_data = file_info['file_data']  # Store binary data
    od_request.attendance_proof_file_size = file_info['file_size']
    od_request.attendance_proof_mime_type = file_info['mime_type']
    od_request.attendance_proof_submitted_at = datetime.now(timezone.utc)
    
    # Update status and set certificate deadline (1 month from now)
    od_request.proof_submission_status = ProofStatus.certificate_pending
    od_request.certificate_submission_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    
    try:
        db.session.commit()
        db.session.refresh(od_request)
        
        return jsonify({
            'message': 'Attendance proof submitted successfully. Please submit participation certificate within 1 month.',
            'od_request': od_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to submit attendance proof'}), 500

@app.route('/api/od-requests/<int:request_id>/submit-certificate', methods=['POST'])
@jwt_required()
def submit_certificate(request_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    od_request = ODRequest.query.get_or_404(request_id)
    
    role = claims.get('role')
    try:
        print(f"[DEBUG] submit_certificate: role={role}, user_id={user_id}, request_id={request_id}")
    except Exception:
        pass
    # Permission rules:
    # - Students can submit for their own request
    # - Faculty/HOD/Admin can submit on behalf of the student (e.g., assisted upload)
    if role == 'student':
        if od_request.student_id != user_id:
            return jsonify({'error': 'Access denied: student mismatch'}), 403
    elif role not in ['faculty', 'hod', 'admin']:
        return jsonify({'error': f'Access denied: role {role} not permitted'}), 403
    
    # Check if request is approved
    if od_request.status != ODStatus.APPROVED:
        return jsonify({'error': 'OD request must be approved first'}), 400
    
    # Check if attendance proof is submitted
    if not od_request.attendance_proof_filename:
        return jsonify({'error': 'Please submit attendance proof first'}), 400
    
    # Check if certificate is already submitted
    if od_request.certificate_filename or od_request.certificate_file_data or od_request.certificate_submitted_at:
        # Return 200 with existing data to mirror attendance proof behavior
        db.session.refresh(od_request)
        return jsonify({
            'message': 'Certificate already submitted',
            'od_request': od_request.to_dict()
        }), 200
    
    # Get uploaded file
    file = request.files.get('certificate')
    if not file:
        return jsonify({'error': 'Certificate file is required'}), 400
    
    # Save file to database
    file_info = save_file_to_database(file)
    if not file_info:
        return jsonify({'error': 'Invalid file format'}), 400
    
    # Update OD request with certificate
    od_request.certificate_filename = file_info['filename']
    od_request.certificate_original_name = file_info['original_name']
    od_request.certificate_file_data = file_info['file_data']  # Store binary data
    od_request.certificate_file_size = file_info['file_size']
    od_request.certificate_mime_type = file_info['mime_type']
    od_request.certificate_submitted_at = datetime.now(timezone.utc)
    
    # Update status to completed
    od_request.proof_submission_status = ProofStatus.COMPLETED
    
    try:
        db.session.commit()
        db.session.refresh(od_request)
        
        return jsonify({
            'message': 'Certificate submitted successfully. Your OD process is now complete!',
            'od_request': od_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to submit certificate'}), 500

@app.route('/api/od/<int:request_id>/view-attendance-proof', methods=['GET'])
@jwt_required()
def view_attendance_proof(request_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    od_request = ODRequest.query.get_or_404(request_id)
    
    # Check permissions
    if claims['role'] == 'student' and od_request.student_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    elif claims['role'] not in ['student', 'faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if file exists in database
    if not od_request.attendance_proof_file_data:
        return jsonify({'error': 'Attendance proof not found'}), 404
    
    try:
        # Serve file from database
        from io import BytesIO
        return send_file(
            BytesIO(od_request.attendance_proof_file_data),
            mimetype=od_request.attendance_proof_mime_type,
            as_attachment=False,
            download_name=od_request.attendance_proof_original_name
        )
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve file: {str(e)}'}), 500

@app.route('/api/od/<int:request_id>/download-attendance-proof', methods=['GET'])
@jwt_required()
def download_attendance_proof(request_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    od_request = ODRequest.query.get_or_404(request_id)
    
    # Check permissions
    if claims['role'] == 'student' and od_request.student_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    elif claims['role'] not in ['student', 'faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if file exists in database
    if not od_request.attendance_proof_file_data:
        return jsonify({'error': 'Attendance proof not found'}), 404
    
    try:
        # Serve file from database
        from io import BytesIO
        return send_file(
            BytesIO(od_request.attendance_proof_file_data),
            mimetype=od_request.attendance_proof_mime_type,
            as_attachment=True,
            download_name=od_request.attendance_proof_original_name
        )
    except Exception as e:
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500

@app.route('/api/od/<int:request_id>/view-certificate', methods=['GET'])
@jwt_required()
def view_certificate(request_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    od_request = ODRequest.query.get_or_404(request_id)
    
    # Check permissions
    if claims['role'] == 'student' and od_request.student_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    elif claims['role'] not in ['student', 'faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if file exists in database
    if not od_request.certificate_file_data:
        return jsonify({'error': 'Certificate not found'}), 404
    
    try:
        # Serve file from database
        from io import BytesIO
        return send_file(
            BytesIO(od_request.certificate_file_data),
            mimetype=od_request.certificate_mime_type,
            as_attachment=False,
            download_name=od_request.certificate_original_name
        )
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve file: {str(e)}'}), 500

@app.route('/api/od/<int:request_id>/download-certificate', methods=['GET'])
@jwt_required()
def download_certificate(request_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    od_request = ODRequest.query.get_or_404(request_id)
    
    # Check permissions
    if claims['role'] == 'student' and od_request.student_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    elif claims['role'] not in ['student', 'faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if file exists in database
    if not od_request.certificate_file_data:
        return jsonify({'error': 'Certificate not found'}), 404
    
    try:
        # Serve file from database
        from io import BytesIO
        return send_file(
            BytesIO(od_request.certificate_file_data),
            mimetype=od_request.certificate_mime_type,
            as_attachment=True,
            download_name=od_request.certificate_original_name
        )
    except Exception as e:
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()
    
    if current_user['role'] not in ['faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    stats = {
        'total_students': Student.query.count(),
        'total_faculty': Faculty.query.count(),
        'total_requests': ODRequest.query.count(),
        'pending_requests': ODRequest.query.filter_by(status=ODStatus.PENDING).count(),
        'approved_requests': ODRequest.query.filter_by(status=ODStatus.APPROVED).count(),
        'rejected_requests': ODRequest.query.filter_by(status=ODStatus.REJECTED).count()
    }
    
    return jsonify(stats), 200

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

@app.cli.command("init-db")
def init_db_command():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")

@app.cli.command("create-admin")
def create_admin_command():
    """Create an admin user"""
    admin = Faculty(
        employee_id='ADMIN001',
        email='admin@college.edu',
        name='System Administrator',
        department='Administration',
        role=UserRole.ADMIN
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    db.session.commit()
    print("Admin user created! Email: admin@college.edu, Password: admin123")

# ============================================================================
# CORS HANDLERS
# ============================================================================

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Authorization,Content-Type")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', "true")
        return response

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded'}), 429

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    print("🚀 OD Management System Backend Server Starting...")
    print("📧 Email notifications enabled")
    print("🔐 JWT authentication active")
    print("📁 File upload configured")
    print("🌐 CORS enabled for frontend")
    
    app.run(debug=True, host='0.0.0.0', port=5000)