from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from app.utils.auth_utils import get_current_user
from app import db
from app.models import Student, Faculty
from datetime import datetime, timezone
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/student/register', methods=['POST'])
def student_register():
    """Register a new student"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['roll_number', 'email', 'password', 'name', 'department', 'year', 'semester']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Check if student already exists
        if Student.query.filter_by(roll_number=data['roll_number']).first():
            return jsonify({'message': 'Student with this roll number already exists'}), 400
        
        if Student.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Student with this email already exists'}), 400
        
        # Validate year and semester
        if not (1 <= int(data['year']) <= 4):
            return jsonify({'message': 'Year must be between 1 and 4'}), 400
        
        if not (1 <= int(data['semester']) <= 8):
            return jsonify({'message': 'Semester must be between 1 and 8'}), 400
        
        # Create new student
        student = Student(
            roll_number=data['roll_number'].upper(),
            email=data['email'].lower(),
            name=data['name'],
            department=data['department'],
            year=int(data['year']),
            semester=int(data['semester']),
            phone_number=data.get('phone_number')
        )
        student.set_password(data['password'])
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'message': 'Student registered successfully',
            'student': student.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500

@auth_bp.route('/student/login', methods=['POST'])
def student_login():
    """Student login with email/roll number and password"""
    try:
        data = request.get_json()
        
        if not data.get('identifier') or not data.get('password'):
            return jsonify({'message': 'Email/Roll number and password are required'}), 400
        
        identifier = data['identifier']
        password = data['password']
        
        # Find student by email or roll number
        student = Student.query.filter(
            db.or_(
                Student.email == identifier.lower(),
                Student.roll_number == identifier.upper()
            )
        ).first()
        
        if not student or not student.check_password(password):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        if not student.is_active:
            return jsonify({'message': 'Account is deactivated'}), 401
        
        # Update last login
        student.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=f"student:{student.id}",
            fresh=True
        )
        refresh_token = create_refresh_token(
            identity=f"student:{student.id}"
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': student.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

@auth_bp.route('/faculty/login', methods=['POST'])
def faculty_login():
    """Faculty/Admin login"""
    try:
        data = request.get_json()
        
        if not data.get('identifier') or not data.get('password'):
            return jsonify({'message': 'Email/Employee ID and password are required'}), 400
        
        identifier = data['identifier']
        password = data['password']
        
        # Find faculty by email or employee ID
        faculty = Faculty.query.filter(
            db.or_(
                Faculty.email == identifier.lower(),
                Faculty.employee_id == identifier.upper()
            )
        ).first()
        
        if not faculty or not faculty.check_password(password):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        if not faculty.is_active:
            return jsonify({'message': 'Account is deactivated'}), 401
        
        # Update last login
        faculty.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=f"faculty:{faculty.id}:{faculty.role.value}",
            fresh=True
        )
        refresh_token = create_refresh_token(
            identity=f"faculty:{faculty.id}:{faculty.role.value}"
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': faculty.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_data = get_jwt_identity()
        
        # Create new access token
        access_token = create_access_token(
            identity=current_user_data,
            fresh=False
        )
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Token refresh failed', 'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_auth():
    """Get current user information"""
    try:
        user, user_type = get_current_user()
        if not user or not user_type:
            return jsonify({'message': 'Invalid token'}), 401

        return jsonify({
            'user': user.to_dict(),
            'type': user_type
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to get user info', 'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token removal)"""
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/login', methods=['POST'])
def general_login():
    """General login endpoint that handles both student and faculty login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('password'):
            return jsonify({'message': 'Password is required'}), 400
        
        user_type = data.get('user_type', 'student')  # Default to student
        
        if user_type == 'student':
            # Try to find student by email or roll number
            student = None
            if data.get('email'):
                student = Student.query.filter_by(email=data['email'].lower()).first()
            elif data.get('roll_number'):
                student = Student.query.filter_by(roll_number=data['roll_number'].upper()).first()
            
            if not student or not student.check_password(data['password']):
                return jsonify({'message': 'Invalid credentials'}), 401
            
            # Create tokens
            access_token = create_access_token(
                identity=f"student:{student.id}",
                fresh=True
            )
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': student.to_dict()
            }), 200
            
        elif user_type in ['faculty', 'hod', 'admin']:
            # Find faculty by email
            if not data.get('email'):
                return jsonify({'message': 'Email is required for faculty login'}), 400
            
            faculty = Faculty.query.filter_by(email=data['email'].lower()).first()
            
            if not faculty or not faculty.check_password(data['password']):
                return jsonify({'message': 'Invalid credentials'}), 401
            
            # Create tokens
            access_token = create_access_token(
                identity=f"faculty:{faculty.id}:{faculty.role.value}",
                fresh=True
            )
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': faculty.to_dict()
            }), 200
        
        else:
            return jsonify({'message': 'Invalid user type'}), 400
            
    except Exception as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile - alias for /me endpoint"""
    try:
        user, user_type = get_current_user()
        if not user or not user_type:
            return jsonify({'message': 'Invalid token'}), 401

        return jsonify(user.to_dict()), 200
    
    except Exception as e:
        return jsonify({'message': 'Failed to get user profile', 'error': str(e)}), 500