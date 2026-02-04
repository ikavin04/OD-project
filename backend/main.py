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
import mimetypes
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, create_refresh_token, get_jwt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# OCR and image processing
from PIL import Image
import pytesseract
import io

# ImgBB & Catbox file upload integration
from imgbb_catbox_helper import upload_file

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
    resources={r"/api/*": {"origins": ["http://localhost:3003", "http://localhost:3002", "http://localhost:3001", "http://localhost:3000", "http://127.0.0.1:3003", "http://127.0.0.1:3002", "http://127.0.0.1:3001", "http://127.0.0.1:3000"]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials", "X-Google-Access-Token"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    expose_headers=["Content-Type", "Content-Disposition", "Authorization"],
    send_wildcard=False,
    always_send=True
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
    INTRA_COLLEGE = "INTRA_COLLEGE"
    INTER_COLLEGE_WITHIN_TN = "INTER_COLLEGE_WITHIN_TN"
    INTER_COLLEGE_COIMBATORE = "INTER_COLLEGE_COIMBATORE"
    INTER_COLLEGE_OTHERS = "INTER_COLLEGE_OTHERS"

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
    section = db.Column(db.String(10))  # A, B, etc.
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
            'section': self.section,
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
    
    # Faculty Type and Class Assignment
    faculty_type = db.Column(db.String(50))  # 'Advisor', 'Mentor', 'Class Handling'
    assigned_year = db.Column(db.Integer)  # 2, 3, 4 for year assignment
    assigned_section = db.Column(db.String(10))  # 'A', 'B', etc.
    
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
            'faculty_type': self.faculty_type,
            'assigned_year': self.assigned_year,
            'assigned_section': self.assigned_section,
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
    
    # Google Drive fields for OD letter/application
    application_drive_file_id = db.Column(db.String(255))
    application_drive_link = db.Column(db.String(500))
    
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
    
    # Google Drive fields for attendance proof
    attendance_proof_drive_file_id = db.Column(db.String(255))
    attendance_proof_drive_link = db.Column(db.String(500))
    
    # Certificate file - Stored in Database
    certificate_filename = db.Column(db.String(255))
    certificate_original_name = db.Column(db.String(255))
    certificate_file_data = db.Column(db.LargeBinary)  # Store actual file in DB
    certificate_file_size = db.Column(db.Integer)
    certificate_mime_type = db.Column(db.String(100))
    certificate_submitted_at = db.Column(db.DateTime(timezone=True))
    
    # Google Drive fields for certificate
    certificate_drive_file_id = db.Column(db.String(255))
    certificate_drive_link = db.Column(db.String(500))
    
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
            'application_drive_link': self.application_drive_link,  # ImgBB/Catbox link
            'status': self.status.value if self.status else None,
            'approval_comments': self.approval_comments,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'proof_submission_status': self.proof_submission_status.value if self.proof_submission_status else None,
            'attendance_proof_deadline': self.attendance_proof_deadline.isoformat() if self.attendance_proof_deadline else None,
            'certificate_deadline': self.certificate_deadline.isoformat() if self.certificate_deadline else None,
            'attendance_proof_file': attendance_proof_file,
            'attendance_proof_drive_link': self.attendance_proof_drive_link,  # ImgBB/Catbox link
            'attendance_proof_submitted_at': self.attendance_proof_submitted_at.isoformat() if self.attendance_proof_submitted_at else None,
            'certificate_file': certificate_file,
            'certificate_drive_link': self.certificate_drive_link,  # ImgBB/Catbox link
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
        subject = f"OD Request {status.title()} - {od_request.event_name}"
        
        # Create HTML email content
        if status == "approved":
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
                <div style="background: linear-gradient(135deg, #28a745, #20c997); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">KGISL College</h1>
                    <h2 style="margin: 10px 0 0 0; font-size: 20px;">OD Request Approved</h2>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: #28a745; margin-top: 0;">Great News, {student_name}!</h3>
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">Your On-Duty request has been <strong style="color: #28a745;">APPROVED</strong>.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                        <h4 style="margin: 0 0 15px 0; color: #333;">Request Details:</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #555;">
                            <li><strong>Event:</strong> {od_request.event_name}</li>
                            <li><strong>Duration:</strong> {od_request.from_date} to {od_request.to_date}</li>
                            <li><strong>Institution:</strong> {od_request.host_institution or od_request.college_name or 'N/A'}</li>
                            <li><strong>Status:</strong> <span style="color: #28a745; font-weight: bold;">APPROVED</span></li>
                        </ul>
                    </div>
                    
                    {f'<div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;"><h4 style="margin: 0 0 10px 0; color: #1976d2;">Faculty Comments:</h4><p style="margin: 0; font-style: italic; color: #333;">"{comments}"</p></div>' if comments else ''}
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #ffeaa7;">
                        <h4 style="margin: 0 0 10px 0; color: #856404;">Important - Proof Submission Requirements:</h4>
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
                    <h1 style="margin: 0; font-size: 28px;">KGISL College</h1>
                    <h2 style="margin: 10px 0 0 0; font-size: 20px;">OD Request Update</h2>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: #dc3545; margin-top: 0;">Dear {student_name},</h3>
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">Your On-Duty request has been reviewed and <strong style="color: #dc3545;">rejected</strong>.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc3545;">
                        <h4 style="margin: 0 0 15px 0; color: #333;">Request Details:</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #555;">
                            <li><strong>Event:</strong> {od_request.event_name}</li>
                            <li><strong>Duration:</strong> {od_request.from_date} to {od_request.to_date}</li>
                            <li><strong>Institution:</strong> {od_request.host_institution or od_request.college_name or 'N/A'}</li>
                            <li><strong>Status:</strong> <span style="color: #dc3545; font-weight: bold;">REJECTED</span></li>
                        </ul>
                    </div>
                    
                    {f'<div style="background-color: #f8d7da; padding: 15px; border-radius: 8px; margin: 20px 0;"><h4 style="margin: 0 0 10px 0; color: #721c24;">Faculty Comments:</h4><p style="margin: 0; font-style: italic; color: #721c24;">"{comments}"</p></div>' if comments else ''}
                    
                    <div style="background-color: #d1ecf1; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #b8daff;">
                        <h4 style="margin: 0 0 10px 0; color: #0c5460;">What to do next:</h4>
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
        print(f"Email sent successfully to {student_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email to {student_email}: {str(e)}")
        # Log in DEMO MODE
        print(f"DEMO MODE - Email would be sent:")
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
    """Save uploaded file directly to database and upload to ImgBB/Catbox for public links"""
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
    
    # Prefer browser-provided content type; fall back to guess by file extension
    guessed_type = mimetypes.guess_type(filename)[0]
    mime_type = file.content_type or guessed_type or 'application/octet-stream'
    
    # Save to temp file for uploading to ImgBB/Catbox
    temp_file_path = None
    public_url = None
    
    try:
        # Create temp file
        temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_hash}_{filename}")
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)
        
        # Upload to ImgBB (images) or Catbox (PDFs)
        public_url = upload_file(temp_file_path)
        
        if public_url:
            print(f"✓ File uploaded successfully: {public_url}")
        else:
            print(f"⚠ File upload failed, continuing without public link")
            
    except Exception as e:
        print(f"⚠ File upload error: {e}")
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass

    return {
        'filename': f"{file_hash}_{filename}",
        'original_name': filename,
        'file_data': file_content,  # Binary data for database
        'file_size': len(file_content),
        'mime_type': mime_type,
        'file_hash': file_hash,
        'public_url': public_url  # ImgBB or Catbox link
    }

# Legacy function for backward compatibility (now redirects to database storage)
def save_file(file, upload_folder="uploads"):
    """Legacy function - now saves to database instead of file system"""
    return save_file_to_database(file)

def validate_certificate_with_ocr(file_data, mime_type):
    """
    Validate certificate using OCR to detect certificate-related keywords
    Returns: (is_valid: bool, confidence_score: float, extracted_text: str)
    """
    try:
        # Check if file is an image
        if not mime_type.startswith('image/'):
            print(f"OCR Debug: Not an image file, mime_type: {mime_type}")
            # Still allow non-image files (like PDFs) to pass
            return True, 50.0, "Non-image file - validation bypassed"
        
        # Load image from binary data
        image = Image.open(io.BytesIO(file_data))
        print(f"OCR Debug: Image loaded successfully, size: {image.size}, mode: {image.mode}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            print(f"OCR Debug: Image converted to RGB")
        
        # Check if Tesseract is installed
        try:
            # Perform OCR
            extracted_text = pytesseract.image_to_string(image).lower()
            print(f"OCR Debug: Text extraction successful, length: {len(extracted_text)}")
            print(f"OCR Debug: Extracted text: {extracted_text[:300]}")
        except pytesseract.TesseractNotFoundError:
            print("WARNING: Tesseract OCR not installed. Allowing all certificates to pass.")
            return True, 100.0, "OCR not available - all certificates allowed"
        except Exception as ocr_error:
            print(f"OCR Debug: OCR extraction failed with error: {str(ocr_error)}")
            # If OCR fails for any reason, allow the upload
            return True, 75.0, f"OCR failed but allowing upload: {str(ocr_error)}"
        
        # Define certificate keywords (case insensitive) - expanded list
        certificate_keywords = [
            'certificate',
            'certify',
            'certification',
            'awarded',
            'presented',
            'participation',
            'achievement',
            'completion',
            'recognition',
            'honor',
            'honours',
            'excellence',
            'participant',
            'successfully completed',
            'hereby certify',
            'this is to certify',
            'conferred',
            'granted',
            'bestowed',
            'diploma',
            'degree',
            'qualified',
            'accomplished',
            'merit',
            'distinguished',
            'performance',
            'event',
            'workshop',
            'seminar',
            'conference',
            'competition',
            'contest',
            'training',
            'course',
            'program',
            'programme',
            'symposium',
            'hackathon',
            'project',
            'internship',
            'winner',
            'first',
            'second',
            'third',
            'prize',
            'award',
            'appreciation',
            'grateful',
            'acknowledge',
            'commend',
            'congratulate',
            'startup',
            'company',
            'organization',
            'institution',
            'future'
        ]
        
        # Count keyword matches
        found_keywords = [keyword for keyword in certificate_keywords if keyword in extracted_text]
        matches = len(found_keywords)
        
        print(f"OCR Debug: Found {matches} keywords: {found_keywords[:10]}")  # Show first 10 matches
        
        # Calculate confidence score (0-100) - very lenient
        confidence_score = min((matches / 1) * 50, 100) if matches > 0 else 0
        
        # EXTREMELY lenient validation - almost always allow
        is_valid = True  # Default to valid
        
        # Only reject if absolutely no relevant content is detected
        if matches == 0 and len(extracted_text.strip()) > 20:
            # Check for any text that might indicate this is a document
            basic_indicators = ['name', 'date', '2024', '2025', '2026', 'to', 'from', 'for', 'the', 'of']
            basic_matches = sum(1 for indicator in basic_indicators if indicator in extracted_text)
            
            if basic_matches < 2:
                is_valid = False
                confidence_score = 0
                print(f"OCR Debug: Rejecting - no keywords and minimal text indicators")
            else:
                confidence_score = 25  # Low but valid
                print(f"OCR Debug: Allowing based on basic text indicators: {basic_matches}")
        elif matches == 0 and len(extracted_text.strip()) <= 20:
            # Very short text - probably OCR failed, allow it
            is_valid = True
            confidence_score = 50
            print(f"OCR Debug: Very short text detected, likely OCR issue - allowing upload")
        
        print(f"OCR Debug: Final result - Valid: {is_valid}, Confidence: {confidence_score}%")
        
        return is_valid, confidence_score, extracted_text[:500]  # Limit text for logging
        
    except Exception as e:
        print(f"OCR validation error: {str(e)}")
        print(f"OCR Debug: Exception occurred, allowing upload to prevent blocking valid certificates")
        # Allow upload on any errors (fail open to not block legitimate uploads)
        return True, 100.0, f"Validation error but allowing upload: {str(e)}"

def get_student_year_folder(student_year):
    """Convert student year (2, 3, 4) to folder name ('2nd year', '3rd year', '4th year')"""
    year_mapping = {
        1: '1st year',
        2: '2nd year',
        3: '3rd year',
        4: '4th year'
    }
    return year_mapping.get(student_year, f'{student_year}th year')

def get_student_class_folder(department, section):
    """Convert department and section to class folder name (e.g., 'CSE A', 'CSE B')"""
    if not section:
        section = 'A'  # Default to section A if not specified
    
    # Normalize department name to short form
    if department:
        dept_mapping = {
            'Computer Science and Engineering': 'CSE',
            'Information Technology': 'IT',
            'Electronics and Communication Engineering': 'ECE',
            'Mechanical Engineering': 'MECH',
            'Civil Engineering': 'CIVIL',
            'CSE': 'CSE',  # Already short form
            'IT': 'IT',    # Already short form
            'ECE': 'ECE',  # Already short form
        }
        department = dept_mapping.get(department, department)
    
    return f"{department} {section}".upper()

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
    
    # Debug: Check all student's OD requests
    all_requests = ODRequest.query.filter_by(student_id=user_id).all()
    print(f"[DEBUG] Student {user_id} has {len(all_requests)} total OD requests:")
    for req in all_requests:
        print(f"  - Event: {req.event_name}, Status: {req.status.name}, Proof Status: {req.proof_submission_status.name if req.proof_submission_status else 'None'}")
    
    # Check if student has any pending proof submissions (excluding completed/certificate_submitted)
    pending_proofs = ODRequest.query.filter(
        ODRequest.student_id == user_id,
        ODRequest.status == ODStatus.APPROVED,
        ODRequest.proof_submission_status.notin_([
            ProofStatus.COMPLETED,
            ProofStatus.certificate_submitted
        ])
    ).first()
    
    print(f"[DEBUG] Pending proofs query result: {pending_proofs}")
    
    if pending_proofs:
        print(f"[DEBUG] Blocking new OD - Pending proof status: {pending_proofs.proof_submission_status.name}")
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
    
    # Prevent duplicate OD submissions using the same permission letter
    # The database enforces a unique constraint on application_file_hash.
    # Catch this early and return a clear message instead of a 500.
    existing_by_hash = ODRequest.query.filter(
        ODRequest.application_file_hash == file_info['file_hash']
    ).first()
    if existing_by_hash:
        return jsonify({
            'error': 'OD exists already: the same permission letter (PDF) was used before.',
            'hint': 'Upload a fresh permission letter PDF or modify details.',
            'existing_request': existing_by_hash.to_dict()
        }), 409
    
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
        application_file_hash=file_info['file_hash'],
        application_drive_link=file_info.get('public_url')  # ImgBB/Catbox link
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
        print(f"[ERROR] Failed to create OD request: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to create OD request: {str(e)}'}), 500

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
    
    # Get filter parameters from query string
    year_filter = request.args.get('year', type=int)
    section_filter = request.args.get('section', type=str)
    status_filter = request.args.get('status', type=str)
    
    # Build query - Faculty see all requests
    query = ODRequest.query.join(Student)
    
    # Apply filters
    if year_filter:
        query = query.filter(Student.year == year_filter)
    
    if section_filter:
        query = query.filter(Student.section == section_filter)
    
    if status_filter:
        query = query.filter(ODRequest.status == ODStatus[status_filter.upper()])
    
    od_requests = query.order_by(ODRequest.created_at.desc()).all()
    
    return jsonify({
        'od_requests': [od.to_dict() for od in od_requests],
        'filters': {
            'year': year_filter,
            'section': section_filter,
            'status': status_filter
        }
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

# Debug endpoint to check student's OD status
@app.route('/api/student/od-status', methods=['GET'])
@jwt_required()
def get_student_od_status():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get all student's OD requests
    all_requests = ODRequest.query.filter_by(student_id=user_id).all()
    
    # Get pending proof submissions
    pending_proofs = ODRequest.query.filter(
        ODRequest.student_id == user_id,
        ODRequest.status == ODStatus.APPROVED,
        ODRequest.proof_submission_status.in_([
            ProofStatus.attendance_pending,
            ProofStatus.ATTENDANCE_SUBMITTED,
            ProofStatus.certificate_pending
        ])
    ).all()
    
    return jsonify({
        'total_requests': len(all_requests),
        'all_requests': [
            {
                'id': od.id,
                'event_name': od.event_name,
                'status': od.status.name,
                'proof_status': od.proof_submission_status.name if od.proof_submission_status else 'None',
                'created_at': od.created_at.isoformat() if od.created_at else None
            } for od in all_requests
        ],
        'pending_proofs': [
            {
                'id': od.id,
                'event_name': od.event_name,
                'status': od.status.name,
                'proof_status': od.proof_submission_status.name,
                'attendance_deadline': od.attendance_proof_deadline.isoformat() if od.attendance_proof_deadline else None,
                'certificate_deadline': od.certificate_deadline.isoformat() if od.certificate_deadline else None
            } for od in pending_proofs
        ],
        'can_create_new_od': len(pending_proofs) == 0
    }), 200

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

@app.route('/api/faculty/profile', methods=['PUT'])
@jwt_required()
def update_faculty_profile():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims['role'] not in ['faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    faculty = Faculty.query.get(user_id)
    if not faculty:
        return jsonify({'error': 'Faculty not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'faculty_type' in data:
        # Validate faculty type
        if data['faculty_type'] not in ['Advisor', 'Mentor', 'Class Handling', None, '']:
            return jsonify({'error': 'Invalid faculty type. Must be Advisor, Mentor, or Class Handling'}), 400
        faculty.faculty_type = data['faculty_type'] if data['faculty_type'] else None
    
    if 'assigned_year' in data:
        # Validate year (2, 3, 4)
        if data['assigned_year'] not in [2, 3, 4, None, '']:
            return jsonify({'error': 'Invalid year. Must be 2, 3, or 4'}), 400
        faculty.assigned_year = data['assigned_year'] if data['assigned_year'] else None
    
    if 'assigned_section' in data:
        # Validate section (A, B)
        if data['assigned_section'] and data['assigned_section'] not in ['A', 'B']:
            return jsonify({'error': 'Invalid section. Must be A or B'}), 400
        faculty.assigned_section = data['assigned_section'] if data['assigned_section'] else None
    
    if 'phone_number' in data:
        faculty.phone_number = data['phone_number']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'faculty': faculty.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

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

# Faculty Excel Export with File Links
@app.route('/api/faculty/export/od-reports', methods=['GET'])
@jwt_required()
def export_faculty_od_reports():
    """Export OD reports with file links to Excel"""
    from flask import request as flask_request
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from io import BytesIO
    from datetime import datetime
    
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    # Only faculty can access this endpoint
    if claims['role'] not in ['faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get filter parameters from query string
    year_filter = flask_request.args.get('year', type=int)
    section_filter = flask_request.args.get('section', type=str)
    status_filter = flask_request.args.get('status', type=str)
    
    # Build query
    query = ODRequest.query.join(Student)
    
    # Apply filters
    if year_filter:
        query = query.filter(Student.year == year_filter)
    if section_filter:
        query = query.filter(Student.section == section_filter)
    if status_filter:
        query = query.filter(ODRequest.status == ODStatus[status_filter.upper()])
    
    od_requests = query.order_by(ODRequest.created_at.desc()).all()
    
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "OD Reports"
    
    # Title and info
    now = datetime.now()
    ws.merge_cells('A1:Z1')  # Extended to Z to cover all columns
    title_cell = ws['A1']
    title_cell.value = f"KGiSL Institute - OD Reports ({now.strftime('%B %Y')})"
    title_cell.font = Font(size=16, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    ws.merge_cells('A2:Z2')
    info_cell = ws['A2']
    info_cell.value = f"Generated: {now.strftime('%d-%m-%Y %I:%M %p')}"
    info_cell.font = Font(size=10, italic=True)
    info_cell.alignment = Alignment(horizontal='center')
    
    # Column headers - 25 total
    headers = [
        'S.No', 'Student Name', 'Roll Number', 'Year', 'Section', 'Department',
        'Event Name', 'Event Description', 'Institution', 'Venue', 'OD Type',
        'From Date', 'To Date', 'OD Status', 'Proof Status',
        'Attendance Submitted', 'Attendance Date', 'Certificate Submitted', 'Certificate Date',
        'Approval Comments', 'Approved Date', 'Application Date',
        'Application Link', 'Attendance Link', 'Certificate Link'
    ]
    
    # Write headers in row 4
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF", size=11)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                           top=Side(style='thin'), bottom=Side(style='thin'))
    
    # Data rows starting from row 5
    for i, od_req in enumerate(od_requests, 1):
        row = 4 + i
        student = od_req.student
        
        # Calculate proof status
        if od_req.attendance_proof_filename and od_req.certificate_filename:
            proof_status = "Complete"
        elif od_req.attendance_proof_filename:
            proof_status = "Attendance Only"
        else:
            proof_status = "Pending"
        
        # OD Type
        od_type_map = {
            'intra_college': 'Intra-College',
            'inter_college_within_tn': 'Inter College-Within TN',
            'inter_college_outside_tn': 'Inter College-Outside TN'
        }
        od_type = od_type_map.get(od_req.od_type.value if hasattr(od_req.od_type, 'value') else str(od_req.od_type), 'N/A')
        
        # Row data - 25 values
        row_data = [
            i,  # S.No
            student.name if student else "N/A",
            student.roll_number if student else "N/A",
            student.year if student else "N/A",
            student.section if student else "N/A",
            student.department if student else "N/A",
            od_req.event_name or "N/A",
            od_req.event_description or "N/A",
            od_req.host_institution or "N/A",
            od_req.venue or "N/A",
            od_type,
            od_req.from_date.strftime('%d-%m-%Y') if od_req.from_date else "N/A",
            od_req.to_date.strftime('%d-%m-%Y') if od_req.to_date else "N/A",
            od_req.status.name.title() if hasattr(od_req.status, 'name') else str(od_req.status),
            proof_status,
            "Yes" if od_req.attendance_proof_filename else "No",
            od_req.attendance_proof_submitted_at.strftime('%d-%m-%Y') if od_req.attendance_proof_submitted_at else "N/A",
            "Yes" if od_req.certificate_filename else "No",
            od_req.certificate_submitted_at.strftime('%d-%m-%Y') if od_req.certificate_submitted_at else "N/A",
            od_req.approval_comments or "N/A",
            od_req.approved_at.strftime('%d-%m-%Y') if od_req.approved_at else "N/A",
            od_req.created_at.strftime('%d-%m-%Y') if od_req.created_at else "N/A",
            od_req.application_drive_link or "Not Available",
            od_req.attendance_proof_drive_link or "Not Available",
            od_req.certificate_drive_link or "Not Available"
        ]
        
        # Write data
        for col, value in enumerate(row_data, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.alignment = Alignment(horizontal='center' if col == 1 else 'left', vertical='center')
            cell.border = Border(left=Side(style='thin'), right=Side(style='thin'),
                               top=Side(style='thin'), bottom=Side(style='thin'))
            
            # Color coding
            if col == 16 and value == "Yes":  # Attendance
                cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
            elif col == 18 and value == "Yes":  # Certificate
                cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
            elif col in [23, 24, 25] and value != "Not Available":  # Links
                cell.fill = PatternFill(start_color="E1F5FE", end_color="E1F5FE", fill_type="solid")
                cell.font = Font(color="01579B", underline='single')
    
    # Set column widths
    widths = [8, 25, 15, 8, 10, 30, 35, 40, 35, 25, 25, 15, 15, 12, 22, 25, 22, 22, 25, 30, 18, 18, 50, 50, 50]
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + i)].width = width
    
    # Save to BytesIO
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    # Generate filename
    filter_text = ""
    if year_filter:
        filter_text += f"_Year{year_filter}"
    if section_filter:
        filter_text += f"_Section{section_filter}"
    if status_filter:
        filter_text += f"_{status_filter.title()}"
    
    filename = f"OD_Reports_with_Links{filter_text}_{now.strftime('%Y%m%d')}.xlsx"
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

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
        print(f"Sending approval email to {od_request.student.email}")
        email_sent = send_od_status_email(
            student_email=od_request.student.email,
            student_name=od_request.student.name,
            od_request=od_request,
            status='approved',
            faculty_name=faculty.name,
            comments=od_request.approval_comments
        )
        print(f"Email sent result: {email_sent}")
        
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
        print(f"Sending rejection email to {od_request.student.email}")
        email_sent = send_od_status_email(
            student_email=od_request.student.email,
            student_name=od_request.student.name,
            od_request=od_request,
            status='rejected',
            faculty_name=faculty.name,
            comments=od_request.approval_comments
        )
        print(f"Email sent result: {email_sent}")
        
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
        # Resolve the most accurate MIME type
        resolved_mime = od_request.application_mime_type or mimetypes.guess_type(od_request.application_original_name or '')[0] or 'application/octet-stream'
        return Response(
            od_request.application_file_data,
            mimetype=resolved_mime,
            headers={
                'Content-Disposition': f'inline; filename="{od_request.application_original_name}"',
                'Content-Length': str(len(od_request.application_file_data))
            }
        )
    elif file_type in ['attendance', 'attendance_proof'] and od_request.attendance_proof_file_data:
        resolved_mime = od_request.attendance_proof_mime_type or mimetypes.guess_type(od_request.attendance_proof_original_name or '')[0] or 'application/octet-stream'
        return Response(
            od_request.attendance_proof_file_data,
            mimetype=resolved_mime,
            headers={
                'Content-Disposition': f'inline; filename="{od_request.attendance_proof_original_name}"',
                'Content-Length': str(len(od_request.attendance_proof_file_data))
            }
        )
    elif file_type == 'certificate' and od_request.certificate_file_data:
        resolved_mime = od_request.certificate_mime_type or mimetypes.guess_type(od_request.certificate_original_name or '')[0] or 'application/octet-stream'
        return Response(
            od_request.certificate_file_data,
            mimetype=resolved_mime,
            headers={
                'Content-Disposition': f'inline; filename="{od_request.certificate_original_name}"',
                'Content-Length': str(len(od_request.certificate_file_data))
            }
        )
    
    return jsonify({'error': 'File not found in database'}), 404

@app.route('/api/od/download/<int:request_id>/<string:file_type>')
@jwt_required()
def download_od_application_file(request_id, file_type):
    """Download OD files from database"""
    od_request = ODRequest.query.get_or_404(request_id)
    
    # Serve file from database based on file type
    from io import BytesIO
    
    if file_type == 'application' and od_request.application_file_data:
        return send_file(
            BytesIO(od_request.application_file_data),
            mimetype=od_request.application_mime_type or 'application/octet-stream',
            as_attachment=True,
            download_name=od_request.application_original_name
        )
    elif file_type in ['attendance', 'attendance_proof'] and od_request.attendance_proof_file_data:
        return send_file(
            BytesIO(od_request.attendance_proof_file_data),
            mimetype=od_request.attendance_proof_mime_type or 'application/octet-stream',
            as_attachment=True,
            download_name=od_request.attendance_proof_original_name
        )
    elif file_type == 'certificate' and od_request.certificate_file_data:
        return send_file(
            BytesIO(od_request.certificate_file_data),
            mimetype=od_request.certificate_mime_type or 'application/octet-stream',
            as_attachment=True,
            download_name=od_request.certificate_original_name
        )
    
    return jsonify({'error': 'File not found in database'}), 404

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
    od_request.attendance_proof_drive_link = file_info.get('public_url')  # ImgBB/Catbox link
    
    # Update status and set certificate deadline (1 month from now)
    od_request.proof_submission_status = ProofStatus.certificate_pending
    od_request.certificate_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    
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
    
    # Check certificate submission deadline (1 month from attendance proof submission)
    if od_request.certificate_deadline:
        deadline = od_request.certificate_deadline
        if datetime.now(timezone.utc) > deadline:
            return jsonify({
                'error': 'Certificate submission deadline has passed',
                'message': f'The deadline for certificate submission was {deadline.strftime("%d-%m-%Y %H:%M")}. You had 1 month from attendance proof submission. Please contact your faculty for further assistance.',
                'deadline': deadline.isoformat()
            }), 400
    
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
    
    # Perform OCR validation on certificate (very lenient for students, can be overridden by faculty)
    is_valid, confidence_score, extracted_text = validate_certificate_with_ocr(
        file_info['file_data'], 
        file_info['mime_type']
    )
    
    # EXTREMELY lenient validation - almost never reject
    # Allow faculty/admin to bypass validation completely
    validation_bypass = role in ['faculty', 'hod', 'admin']
    
    # Only reject in very rare cases and only for students
    if not is_valid and not validation_bypass:
        print(f"Certificate validation failed for request {request_id}")
        print(f"Confidence: {confidence_score}%, Text preview: {extracted_text[:200]}")
        
        # Even more helpful error message
        return jsonify({
            'error': 'File validation issue',
            'message': 'The system had difficulty processing your file. This might be due to:\n\n• Image quality or format issues\n• OCR processing limitations\n\nPlease try:\n1. Taking a clearer photo with good lighting\n2. Using a different image format (JPG/PNG)\n3. Contacting your faculty for assistance\n\nYour faculty can help upload the certificate manually.',
            'confidence_score': round(confidence_score, 2),
            'extracted_text_preview': extracted_text[:100] if extracted_text else "No text detected",
            'help': 'Contact faculty if this issue persists - they can bypass this validation.'
        }), 400
    
    # Log successful validation
    if is_valid:
        print(f"Certificate validation PASSED for request {request_id}")
        print(f"Confidence: {confidence_score}%, Role: {role}")
        if validation_bypass:
            print(f"Validation bypassed for {role} user")
    
    print(f"Certificate validated successfully - Confidence: {confidence_score}%")
    
    # Update OD request with certificate
    od_request.certificate_filename = file_info['filename']
    od_request.certificate_original_name = file_info['original_name']
    od_request.certificate_file_data = file_info['file_data']  # Store binary data
    od_request.certificate_file_size = file_info['file_size']
    od_request.certificate_mime_type = file_info['mime_type']
    od_request.certificate_submitted_at = datetime.now(timezone.utc)
    od_request.certificate_drive_link = file_info.get('public_url')  # ImgBB/Catbox link
    
    # Update status to certificate_submitted (completed)
    od_request.proof_submission_status = ProofStatus.certificate_submitted
    
    try:
        db.session.commit()
        db.session.refresh(od_request)
        
        return jsonify({
            'message': 'Certificate submitted successfully and validated! Your OD process is now complete.',
            'validation_info': f'Certificate validated with {round(confidence_score, 1)}% confidence',
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

@app.after_request
def after_request(response):
    """Add CORS headers to all responses including file downloads"""
    origin = request.headers.get('Origin')
    allowed_origins = ["http://localhost:3003", "http://localhost:3002", "http://localhost:3001", "http://localhost:3000", "http://127.0.0.1:3003", "http://127.0.0.1:3002", "http://127.0.0.1:3001", "http://127.0.0.1:3000"]
    
    # Always add CORS headers for allowed origins
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Access-Control-Allow-Credentials'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Content-Disposition, Authorization'
    elif not origin:
        # If no origin header, allow for local testing
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Access-Control-Allow-Credentials'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Content-Disposition, Authorization'
    
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
# MONTHLY REPORT ROUTE
# ============================================================================

@app.route('/api/reports/monthly-od-report', methods=['POST'])
@jwt_required()
def trigger_monthly_report():
    """Manually trigger monthly OD report generation and send to faculty"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    # Only faculty/admin can trigger reports
    if claims['role'] not in ['faculty', 'hod', 'admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        from monthly_report import send_monthly_report_to_faculty
        
        sent_count, failed_count = send_monthly_report_to_faculty(
            app, db, Student, ODRequest, Faculty, ProofStatus, mail
        )
        
        return jsonify({
            'message': 'Monthly report sent successfully',
            'sent_count': sent_count,
            'failed_count': failed_count,
            'total_recipients': sent_count + failed_count
        }), 200
        
    except Exception as e:
        print(f"Error generating monthly report: {str(e)}")
        return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500

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