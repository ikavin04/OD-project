from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Student, Faculty, ODRequest, ODStatus, ODType, ProofStatus
from app.utils.file_upload import FileUploadService
from datetime import datetime, date
from app.utils.auth_utils import get_current_user
import os

od_bp = Blueprint('od', __name__)

def get_current_user_od():
    """Get current user from JWT token"""
    return get_current_user()

@od_bp.route('/request', methods=['POST'])
@jwt_required()
def create_od_request():
    """Create a new OD request (Student only)"""
    try:
        user, user_type = get_current_user_od()
        if not user or not user_type:
            return jsonify({'message': 'Invalid or missing token'}), 401
        
        if user_type != 'student':
            return jsonify({'message': 'Only students can create OD requests'}), 403
        
        # Check if student has any pending or approved OD requests
        existing_od = ODRequest.query.filter_by(
            student_id=user.id,
            status=ODStatus.PENDING
        ).first()
        
        if existing_od:
            return jsonify({'message': 'You already have a pending OD request'}), 400
        
        # Get form data
        data = request.form.to_dict()
        
        # Validate required fields
        required_fields = ['event_name', 'from_date', 'to_date', 'od_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate dates
        try:
            from_date = datetime.strptime(data['from_date'], '%Y-%m-%d').date()
            to_date = datetime.strptime(data['to_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate date logic
        today = date.today()
        if from_date < today:
            return jsonify({'message': 'OD start date cannot be in the past'}), 400
        
        if to_date < from_date:
            return jsonify({'message': 'OD end date cannot be before start date'}), 400
        
        # Validate OD type
        try:
            od_type = ODType(data['od_type'])
        except ValueError:
            return jsonify({'message': 'Invalid OD type'}), 400
        
        # Validate location type for inter-college events only
        location_type = None
        if od_type == ODType.INTER_COLLEGE_COIMBATORE:
            # Automatically set to within_state for Coimbatore events
            location_type = 'within_state'
        elif od_type == ODType.INTER_COLLEGE_OTHERS:
            if not data.get('location_type'):
                return jsonify({'message': 'Location type is required for inter-college events'}), 400
            
            valid_location_types = ['within_state', 'out_of_state']
            if data.get('location_type') not in valid_location_types:
                return jsonify({'message': 'Invalid location type. Must be within_state or out_of_state'}), 400
            
            location_type = data['location_type']
        
        # Validate college/institution based on OD type
        if od_type == ODType.INTRA_COLLEGE:
            if not data.get('college_name'):
                return jsonify({'message': 'College name is required for intra-college events'}), 400
        elif od_type in [ODType.INTER_COLLEGE_COIMBATORE, ODType.INTER_COLLEGE_OTHERS]:
            if not data.get('host_institution'):
                return jsonify({'message': 'Host institution is required for inter-college events'}), 400
        
        # Check for conflicting approved OD requests
        conflicting_od = ODRequest.query.filter(
            ODRequest.student_id == user.id,
            ODRequest.status == ODStatus.APPROVED,
            db.or_(
                db.and_(ODRequest.from_date <= from_date, ODRequest.to_date >= from_date),
                db.and_(ODRequest.from_date <= to_date, ODRequest.to_date >= to_date),
                db.and_(ODRequest.from_date >= from_date, ODRequest.to_date <= to_date)
            )
        ).first()
        
        if conflicting_od:
            return jsonify({
                'message': f'You have a conflicting approved OD request from {conflicting_od.from_date} to {conflicting_od.to_date}'
            }), 400
        
        # Handle file upload (permission document)
        if 'application_file' not in request.files:
            return jsonify({'message': 'Permission document is required'}), 400
        
        file = request.files['application_file']
        file_data, error = FileUploadService.save_file(file, 'permissions')
        
        if error:
            return jsonify({'message': error}), 400
        
        # Check for duplicate file
        existing_file = ODRequest.query.filter_by(
            application_file_hash=file_data['file_hash']
        ).first()
        
        if existing_file:
            # Delete the uploaded file since it's a duplicate
            FileUploadService.delete_file(file_data['file_path'])
            return jsonify({'message': 'This document has already been used for another OD request'}), 400
        
        # Create OD request
        od_request = ODRequest(
            student_id=user.id,
            event_name=data['event_name'],
            event_description=data.get('event_description'),
            from_date=from_date,
            to_date=to_date,
            od_type=od_type,
            college_name=data.get('college_name'),
            host_institution=data.get('host_institution'),
            venue=data.get('venue'),
            location_type=location_type,
            application_filename=file_data['filename'],
            application_original_name=file_data['original_name'],
            application_file_path=file_data['file_path'],
            application_file_size=file_data['file_size'],
            application_mime_type=file_data['mime_type'],
            application_file_hash=file_data['file_hash'],
            status=ODStatus.PENDING,
            proof_submission_status=ProofStatus.NOT_SUBMITTED
        )
        
        db.session.add(od_request)
        db.session.commit()
        
        return jsonify({
            'message': 'OD request submitted successfully',
            'od_request': od_request.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create OD request', 'error': str(e)}), 500

@od_bp.route('/my-requests', methods=['GET'])
@jwt_required()
def get_my_od_requests():
    """Get student's OD requests"""
    try:
        user, user_type = get_current_user()
        if not user or not user_type:
            return jsonify({'message': 'Invalid or missing token'}), 401
        
        if user_type != 'student':
            return jsonify({'message': 'Only students can view their OD requests'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status')
        
        # Build query
        query = ODRequest.query.filter_by(student_id=user.id)
        
        if status_filter:
            try:
                status = ODStatus(status_filter)
                query = query.filter_by(status=status)
            except ValueError:
                return jsonify({'message': 'Invalid status filter'}), 400
        
        # Order by creation date (newest first)
        query = query.order_by(ODRequest.created_at.desc())
        
        # Paginate
        od_requests = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'od_requests': [od.to_dict() for od in od_requests.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': od_requests.total,
                'pages': od_requests.pages,
                'has_next': od_requests.has_next,
                'has_prev': od_requests.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get OD requests', 'error': str(e)}), 500

@od_bp.route('/<int:od_id>', methods=['GET'])
@jwt_required()
def get_od_request(od_id):
    """Get specific OD request details"""
    try:
        user, user_type = get_current_user_od()
        if not user or not user_type:
            return jsonify({'message': 'Invalid or missing token'}), 401
        
        od_request = ODRequest.query.get_or_404(od_id)
        
        # Check permissions
        if user_type == 'student' and od_request.student_id != user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Include sensitive data for faculty
        include_sensitive = user_type == 'faculty'
        
        return jsonify({
            'od_request': od_request.to_dict(include_sensitive=include_sensitive)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get OD request', 'error': str(e)}), 500

@od_bp.route('/<int:od_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_od_request(od_id):
    """Cancel OD request (Student only, only pending requests)"""
    try:
        user, user_type = get_current_user_od()
        if not user or not user_type:
            return jsonify({'message': 'Invalid or missing token'}), 401
        
        if user_type != 'student':
            return jsonify({'message': 'Only students can cancel their OD requests'}), 403
        
        od_request = ODRequest.query.get_or_404(od_id)
        
        if od_request.student_id != user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        if od_request.status != ODStatus.PENDING:
            return jsonify({'message': 'Only pending OD requests can be cancelled'}), 400
        
        # Delete the OD request and associated file
        FileUploadService.delete_file(od_request.application_file_path)
        db.session.delete(od_request)
        db.session.commit()
        
        return jsonify({'message': 'OD request cancelled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to cancel OD request', 'error': str(e)}), 500

@od_bp.route('/download/<int:od_id>/<file_type>', methods=['GET'])
@jwt_required()
def download_file(od_id, file_type):
    """Download OD request files"""
    try:
        user, user_type = get_current_user_od()
        if not user or not user_type:
            return jsonify({'message': 'Invalid or missing token'}), 401
        
        od_request = ODRequest.query.get_or_404(od_id)
        
        # Check permissions
        if user_type == 'student' and od_request.student_id != user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Get file path based on type
        file_path = None
        filename = None
        
        if file_type == 'application':
            file_path = od_request.application_file_path
            filename = od_request.application_original_name
        elif file_type == 'attendance_proof':
            file_path = od_request.attendance_proof_file_path
            filename = od_request.attendance_proof_original_name
        elif file_type == 'certificate':
            file_path = od_request.certificate_file_path
            filename = od_request.certificate_original_name
        else:
            return jsonify({'message': 'Invalid file type'}), 400
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'message': 'File not found'}), 404
        
        from flask import send_file
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'message': 'Failed to download file', 'error': str(e)}), 500