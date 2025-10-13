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

@od_bp.route('/can-apply', methods=['GET'])
@jwt_required()
def can_apply_for_od():
    """Check if student can apply for new OD"""
    try:
        user, user_type = get_current_user_od()
        if not user or not user_type:
            return jsonify({'message': 'Invalid or missing token'}), 401
        
        if user_type != 'student':
            return jsonify({'message': 'Only students can check OD application eligibility'}), 403
        
        # Check for pending OD requests
        pending_od = ODRequest.query.filter_by(
            student_id=user.id,
            status=ODStatus.PENDING
        ).first()
        
        if pending_od:
            return jsonify({
                'can_apply': False,
                'reason': 'pending_od',
                'message': 'You already have a pending OD request',
                'blocking_od': pending_od.to_dict()
            }), 200
        
        # Check for overdue proof submissions
        current_time = datetime.now()
        overdue_proofs = ODRequest.query.filter(
            ODRequest.student_id == user.id,
            ODRequest.status == ODStatus.APPROVED,
            db.or_(
                # Missing attendance proof after deadline
                db.and_(
                    ODRequest.attendance_proof_deadline.isnot(None),
                    ODRequest.attendance_proof_deadline < current_time,
                    ODRequest.attendance_proof_uploaded_at.is_(None)
                ),
                # Missing certificate after deadline
                db.and_(
                    ODRequest.certificate_submission_deadline.isnot(None),
                    ODRequest.certificate_submission_deadline < current_time,
                    ODRequest.certificate_uploaded_at.is_(None),
                    ODRequest.attendance_proof_uploaded_at.isnot(None)
                )
            )
        ).all()
        
        if overdue_proofs:
            return jsonify({
                'can_apply': False,
                'reason': 'overdue_proofs',
                'message': 'You have overdue proof submissions that must be completed before applying for new ODs',
                'overdue_submissions': [
                    {
                        'od_id': od.id,
                        'event_name': od.event_name,
                        'missing_proofs': [
                            'attendance_proof' if (od.attendance_proof_deadline and 
                                                 od.attendance_proof_deadline < current_time and 
                                                 not od.attendance_proof_uploaded_at) else None,
                            'certificate' if (od.certificate_submission_deadline and 
                                            od.certificate_submission_deadline < current_time and 
                                            not od.certificate_uploaded_at and 
                                            od.attendance_proof_uploaded_at) else None
                        ]
                    }
                    for od in overdue_proofs
                ]
            }), 200
        
        return jsonify({
            'can_apply': True,
            'message': 'You can apply for a new OD request'
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to check OD application eligibility', 'error': str(e)}), 500

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
        
        # Check if student has any pending proof submissions
        pending_proofs = ODRequest.query.filter(
            ODRequest.student_id == user.id,
            ODRequest.status == ODStatus.APPROVED,
            db.or_(
                # Missing attendance proof after deadline
                db.and_(
                    ODRequest.attendance_proof_deadline.isnot(None),
                    ODRequest.attendance_proof_deadline < datetime.now(),
                    ODRequest.attendance_proof_uploaded_at.is_(None)
                ),
                # Missing certificate after deadline
                db.and_(
                    ODRequest.certificate_submission_deadline.isnot(None),
                    ODRequest.certificate_submission_deadline < datetime.now(),
                    ODRequest.certificate_uploaded_at.is_(None),
                    ODRequest.attendance_proof_uploaded_at.isnot(None)
                )
            )
        ).first()
        
        if pending_proofs:
            return jsonify({
                'message': 'You cannot apply for new OD requests until all pending proof submissions are completed',
                'pending_od_id': pending_proofs.id,
                'pending_od_event': pending_proofs.event_name,
                'blocking_reason': 'overdue_proofs'
            }), 400
        
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
            # For intra-college events, use host_institution or default to college name
            if not data.get('host_institution'):
                return jsonify({'message': 'Host institution is required for intra-college events'}), 400
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
            college_name=data.get('host_institution') if od_type == ODType.INTRA_COLLEGE else None,
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
        
        # Handle both absolute and relative paths
        if not file_path:
            return jsonify({'message': 'File path not found'}), 404
        
        # If path is not absolute, make it relative to the backend directory
        if not os.path.isabs(file_path):
            from flask import current_app
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            file_path = os.path.join(backend_dir, file_path)
        
        if not os.path.exists(file_path):
            return jsonify({'message': f'File not found: {file_path}'}), 404
        
        from flask import send_file
        
        # Get the mimetype for the file
        mimetype = None
        if file_type == 'application':
            mimetype = od_request.application_mime_type
        elif file_type == 'attendance_proof':
            mimetype = od_request.attendance_proof_mime_type
        elif file_type == 'certificate':
            mimetype = od_request.certificate_mime_type
        
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({'message': 'Failed to download file', 'error': str(e)}), 500


@od_bp.route('/view/<int:od_id>/<file_type>')
@jwt_required()
def view_file(od_id, file_type):
    """View OD request files in browser (not as download)"""
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
        
        # Handle both absolute and relative paths
        if not file_path:
            return jsonify({'message': 'File path not found'}), 404
        
        # If path is not absolute, make it relative to the backend directory
        if not os.path.isabs(file_path):
            from flask import current_app
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            file_path = os.path.join(backend_dir, file_path)
        
        if not os.path.exists(file_path):
            return jsonify({'message': f'File not found: {file_path}'}), 404
        
        from flask import send_file
        
        # Get the mimetype for the file
        mimetype = None
        if file_type == 'application':
            mimetype = od_request.application_mime_type
        elif file_type == 'attendance_proof':
            mimetype = od_request.attendance_proof_mime_type
        elif file_type == 'certificate':
            mimetype = od_request.certificate_mime_type
        
        # Send file for viewing (not as attachment)
        return send_file(
            file_path, 
            as_attachment=False,  # This is the key difference!
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({'message': 'Failed to view file', 'error': str(e)}), 500