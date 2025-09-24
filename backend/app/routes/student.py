from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Student, ODRequest, ODStatus, ProofStatus
from datetime import datetime, date
from app.utils.auth_utils import get_current_user

student_bp = Blueprint('student', __name__)

def get_current_student():
    """Get current student from JWT token"""
    user, user_type = get_current_user()
    if user_type == 'student':
        return user
    return None

@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_student_dashboard():
    """Get student dashboard with stats and recent activity"""
    try:
        student = get_current_student()
        if not student:
            return jsonify({'message': 'Access denied'}), 403
        
        # Get OD request statistics
        total_requests = ODRequest.query.filter_by(student_id=student.id).count()
        pending_requests = ODRequest.query.filter_by(
            student_id=student.id, 
            status=ODStatus.PENDING
        ).count()
        approved_requests = ODRequest.query.filter_by(
            student_id=student.id, 
            status=ODStatus.APPROVED
        ).count()
        rejected_requests = ODRequest.query.filter_by(
            student_id=student.id, 
            status=ODStatus.REJECTED
        ).count()
        
        # Check for active OD (approved and current/future dates)
        today = date.today()
        active_od = ODRequest.query.filter(
            ODRequest.student_id == student.id,
            ODRequest.status == ODStatus.APPROVED,
            ODRequest.to_date >= today
        ).first()
        
        # Check for pending proof submissions
        pending_proofs = ODRequest.query.filter(
            ODRequest.student_id == student.id,
            ODRequest.status == ODStatus.APPROVED,
            ODRequest.to_date < today,
            ODRequest.proof_submission_status != ProofStatus.COMPLETED
        ).count()
        
        # Get recent OD requests (last 5)
        recent_requests = ODRequest.query.filter_by(
            student_id=student.id
        ).order_by(ODRequest.created_at.desc()).limit(5).all()
        
        return jsonify({
            'student': student.to_dict(),
            'stats': {
                'total_requests': total_requests,
                'pending_requests': pending_requests,
                'approved_requests': approved_requests,
                'rejected_requests': rejected_requests,
                'pending_proofs': pending_proofs
            },
            'active_od': active_od.to_dict() if active_od else None,
            'recent_requests': [od.to_dict() for od in recent_requests]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get dashboard', 'error': str(e)}), 500

@student_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get student profile"""
    try:
        student = get_current_student()
        if not student:
            return jsonify({'message': 'Access denied'}), 403
        
        return jsonify({'student': student.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get profile', 'error': str(e)}), 500

@student_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update student profile (limited fields)"""
    try:
        student = get_current_student()
        if not student:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Only allow updating certain fields
        updatable_fields = ['phone_number']
        
        for field in updatable_fields:
            if field in data:
                if field == 'phone_number':
                    phone = data[field]
                    if phone and not phone.isdigit() or len(phone) != 10:
                        return jsonify({'message': 'Invalid phone number format'}), 400
                setattr(student, field, data[field])
        
        student.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'student': student.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile', 'error': str(e)}), 500

@student_bp.route('/check-availability', methods=['POST'])
@jwt_required()
def check_od_availability():
    """Check if student can submit OD for given dates"""
    try:
        student = get_current_student()
        if not student:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        
        if not data.get('from_date') or not data.get('to_date'):
            return jsonify({'message': 'Both from_date and to_date are required'}), 400
        
        try:
            from_date = datetime.strptime(data['from_date'], '%Y-%m-%d').date()
            to_date = datetime.strptime(data['to_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Check for conflicts
        conflicts = ODRequest.query.filter(
            ODRequest.student_id == student.id,
            ODRequest.status.in_([ODStatus.PENDING, ODStatus.APPROVED]),
            db.or_(
                db.and_(ODRequest.from_date <= from_date, ODRequest.to_date >= from_date),
                db.and_(ODRequest.from_date <= to_date, ODRequest.to_date >= to_date),
                db.and_(ODRequest.from_date >= from_date, ODRequest.to_date <= to_date)
            )
        ).all()
        
        is_available = len(conflicts) == 0
        
        return jsonify({
            'is_available': is_available,
            'conflicts': [
                {
                    'id': conflict.id,
                    'event_name': conflict.event_name,
                    'from_date': conflict.from_date.isoformat(),
                    'to_date': conflict.to_date.isoformat(),
                    'status': conflict.status.value
                }
                for conflict in conflicts
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to check availability', 'error': str(e)}), 500

@student_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change student password"""
    try:
        student = get_current_student()
        if not student:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'message': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not student.check_password(data['current_password']):
            return jsonify({'message': 'Current password is incorrect'}), 400
        
        # Validate new password
        new_password = data['new_password']
        if len(new_password) < 6:
            return jsonify({'message': 'New password must be at least 6 characters long'}), 400
        
        # Update password
        student.set_password(new_password)
        student.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to change password', 'error': str(e)}), 500