"""
Authentication utilities for the OD Management System
"""
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import Student, Faculty
from functools import wraps

def get_current_user():
    """Get the current authenticated user"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        if not current_user_id:
            return None
            
        user_type = current_user_id.get('type')
        user_id = current_user_id.get('id')
        
        if user_type == 'student':
            return Student.query.get(user_id)
        elif user_type == 'faculty':
            return Faculty.query.get(user_id)
        else:
            return None
            
    except Exception as e:
        return None

def jwt_required_with_user(f):
    """Decorator that requires JWT authentication and injects current user"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_current_user()
            
            if not current_user:
                return jsonify({'error': 'Invalid user'}), 401
                
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
    
    return decorated

def faculty_required(f):
    """Decorator that requires faculty authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_current_user()
            
            if not current_user or not isinstance(current_user, Faculty):
                return jsonify({'error': 'Faculty access required'}), 403
                
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
    
    return decorated

def student_required(f):
    """Decorator that requires student authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_current_user()
            
            if not current_user or not isinstance(current_user, Student):
                return jsonify({'error': 'Student access required'}), 403
                
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
    
    return decorated