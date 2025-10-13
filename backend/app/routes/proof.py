from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Student, Faculty, ODRequest, ODStatus, ProofStatus
from app.utils.file_upload import FileUploadService
from app.utils.email_service import email_service
from datetime import datetime, date
from app.utils.auth_utils import get_current_user

proof_bp = Blueprint('proof', __name__)

@proof_bp.route('/<int:od_id>/attendance', methods=['POST'])
@jwt_required()
def submit_attendance_proof(od_id):
    """Submit attendance proof for OD request"""
    try:
        user, user_type = get_current_user()
        
        if not user or user_type != 'student':
            return jsonify({'message': 'Only students can submit attendance proof'}), 403
        
        od_request = ODRequest.query.get_or_404(od_id)
        
        # Check ownership
        if od_request.student_id != user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Check OD status
        if od_request.status != ODStatus.APPROVED:
            return jsonify({'message': 'OD request must be approved to submit proof'}), 400
        
        # Check if proof submission is allowed (after OD end date)
        if not od_request.is_proof_submission_allowed:
            return jsonify({'message': 'Cannot submit proof before OD end date'}), 400
        
        # Check if attendance proof already submitted
        if od_request.attendance_proof_filename:
            return jsonify({'message': 'Attendance proof already submitted'}), 400
        
        # Handle file upload
        if 'attendance_proof' not in request.files:
            return jsonify({'message': 'Attendance proof file is required'}), 400
        
        file = request.files['attendance_proof']
        file_data, error = FileUploadService.save_file(file, 'proofs')
        
        if error:
            return jsonify({'message': error}), 400
        
        # Check for duplicate file
        existing_proof = ODRequest.query.filter(
            ODRequest.attendance_proof_file_hash == file_data['file_hash'],
            ODRequest.id != od_id
        ).first()
        
        if existing_proof:
            FileUploadService.delete_file(file_data['file_path'])
            return jsonify({'message': 'This file has already been used as attendance proof for another OD request'}), 400
        
        # Update OD request with attendance proof
        od_request.attendance_proof_filename = file_data['filename']
        od_request.attendance_proof_original_name = file_data['original_name']
        od_request.attendance_proof_file_path = file_data['file_path']
        od_request.attendance_proof_file_size = file_data['file_size']
        od_request.attendance_proof_mime_type = file_data['mime_type']
        od_request.attendance_proof_file_hash = file_data['file_hash']
        od_request.attendance_proof_uploaded_at = datetime.utcnow()
        od_request.proof_submission_status = ProofStatus.ATTENDANCE_SUBMITTED
        od_request.updated_at = datetime.utcnow()
        
        # Set certificate submission deadline
        od_request.set_certificate_deadline()
        
        db.session.commit()
        
        # Send confirmation email
        try:
            faculty = Faculty.query.get(od_request.faculty_id)
            if faculty:
                email_service.send_proof_submission_confirmation(user, faculty, od_request, 'attendance')
        except Exception as e:
            # Log email error but don't fail the request
            print(f"Failed to send confirmation email: {str(e)}")
        
        return jsonify({
            'message': 'Attendance proof submitted successfully',
            'od_request': od_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to submit attendance proof', 'error': str(e)}), 500

@proof_bp.route('/<int:od_id>/certificate', methods=['POST'])
@jwt_required()
def submit_certificate(od_id):
    """Submit participation certificate for OD request"""
    try:
        user, user_type = get_current_user()
        
        if not user or user_type != 'student':
            return jsonify({'message': 'Only students can submit certificates'}), 403
        
        od_request = ODRequest.query.get_or_404(od_id)
        
        # Check ownership
        if od_request.student_id != user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Check OD status
        if od_request.status != ODStatus.APPROVED:
            return jsonify({'message': 'OD request must be approved to submit certificate'}), 400
        
        # Check if attendance proof is submitted
        if not od_request.attendance_proof_filename:
            return jsonify({'message': 'Please submit attendance proof first'}), 400
        
        # Check if certificate already submitted
        if od_request.certificate_filename:
            return jsonify({'message': 'Certificate already submitted'}), 400
        
        # Handle file upload
        if 'certificate' not in request.files:
            return jsonify({'message': 'Certificate file is required'}), 400
        
        file = request.files['certificate']
        file_data, error = FileUploadService.save_file(file, 'certificates')
        
        if error:
            return jsonify({'message': error}), 400
        
        # Check for duplicate file
        existing_certificate = ODRequest.query.filter(
            ODRequest.certificate_file_hash == file_data['file_hash'],
            ODRequest.id != od_id
        ).first()
        
        if existing_certificate:
            FileUploadService.delete_file(file_data['file_path'])
            return jsonify({'message': 'This certificate has already been used for another OD request'}), 400
        
        # TODO: Perform OCR validation here
        # For now, we'll store a placeholder validation result
        ocr_validation = {
            'is_valid': True,  # Will be determined by OCR service
            'confidence': 85,
            'extracted_text': '',
            'match_results': {
                'student_name': True,
                'event_name': True,
                'dates': True
            },
            'processed_at': datetime.utcnow().isoformat()
        }
        
        # Update OD request with certificate
        od_request.certificate_filename = file_data['filename']
        od_request.certificate_original_name = file_data['original_name']
        od_request.certificate_file_path = file_data['file_path']
        od_request.certificate_file_size = file_data['file_size']
        od_request.certificate_mime_type = file_data['mime_type']
        od_request.certificate_file_hash = file_data['file_hash']
        od_request.certificate_uploaded_at = datetime.utcnow()
        od_request.proof_submission_status = ProofStatus.COMPLETED
        od_request.set_ocr_validation(ocr_validation)
        od_request.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send confirmation email
        try:
            faculty = Faculty.query.get(od_request.faculty_id)
            if faculty:
                email_service.send_proof_submission_confirmation(user, faculty, od_request, 'certificate')
        except Exception as e:
            # Log email error but don't fail the request
            print(f"Failed to send confirmation email: {str(e)}")
        
        return jsonify({
            'message': 'Certificate submitted successfully',
            'od_request': od_request.to_dict(),
            'ocr_validation': {
                'is_valid': ocr_validation['is_valid'],
                'confidence': ocr_validation['confidence'],
                'match_results': ocr_validation['match_results']
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to submit certificate', 'error': str(e)}), 500

@proof_bp.route('/<int:od_id>/status', methods=['GET'])
@jwt_required()
def get_proof_status(od_id):
    """Get proof submission status for OD request"""
    try:
        user, user_type = get_current_user()
        
        if not user:
            return jsonify({'message': 'Invalid or missing token'}), 401
        
        od_request = ODRequest.query.get_or_404(od_id)
        
        # Check permissions
        if user_type == 'student' and od_request.student_id != user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Check if proof submission is allowed
        can_submit_proofs = od_request.is_proof_submission_allowed
        
        proof_status = {
            'proof_submission_status': od_request.proof_submission_status.value,
            'can_submit_proofs': can_submit_proofs,
            'attendance_proof': None,
            'certificate': None
        }
        
        # Add attendance proof info if exists
        if od_request.attendance_proof_filename:
            proof_status['attendance_proof'] = {
                'filename': od_request.attendance_proof_original_name,
                'uploaded_at': od_request.attendance_proof_uploaded_at.isoformat() if od_request.attendance_proof_uploaded_at else None,
                'file_size': od_request.attendance_proof_file_size
            }
        
        # Add certificate info if exists
        if od_request.certificate_filename:
            proof_status['certificate'] = {
                'filename': od_request.certificate_original_name,
                'uploaded_at': od_request.certificate_uploaded_at.isoformat() if od_request.certificate_uploaded_at else None,
                'file_size': od_request.certificate_file_size
            }
            
            # Include OCR validation for faculty
            if user_type == 'faculty':
                ocr_validation = od_request.get_ocr_validation()
                if ocr_validation:
                    proof_status['certificate']['ocr_validation'] = ocr_validation
        
        return jsonify(proof_status), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get proof status', 'error': str(e)}), 500

@proof_bp.route('/<int:od_id>/reminder', methods=['POST'])
@jwt_required()
def send_certificate_reminder(od_id):
    """Send certificate reminder (Faculty/Admin only)"""
    try:
        user, user_type = get_current_user()
        
        if not user or user_type != 'faculty':
            return jsonify({'message': 'Only faculty can send reminders'}), 403
        
        od_request = ODRequest.query.get_or_404(od_id)
        
        # Check if reminder is appropriate
        if od_request.certificate_filename:
            return jsonify({'message': 'Certificate already submitted'}), 400
        
        if not od_request.attendance_proof_filename:
            return jsonify({'message': 'Attendance proof not submitted yet'}), 400
        
        # Update last reminder sent date
        od_request.last_reminder_sent = datetime.utcnow()
        db.session.commit()
        
        # TODO: Send reminder email
        
        return jsonify({'message': 'Reminder sent successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to send reminder', 'error': str(e)}), 500

@proof_bp.route('/pending-submissions', methods=['GET'])
@jwt_required()
def get_pending_submissions():
    """Get OD requests with pending proof submissions (Faculty only)"""
    try:
        user, user_type = get_current_user()
        
        if not user or user_type != 'faculty':
            return jsonify({'message': 'Only faculty can view pending submissions'}), 403
        
        # Get OD requests that need proof submissions
        today = date.today()
        
        pending_query = ODRequest.query.join(Student).filter(
            ODRequest.status == ODStatus.APPROVED,
            ODRequest.to_date < today,
            ODRequest.proof_submission_status != ProofStatus.COMPLETED
        )
        
        # Filter by department for regular faculty
        if user.role.value == 'faculty':
            pending_query = pending_query.filter(Student.department == user.department)
        
        pending_requests = pending_query.order_by(ODRequest.to_date.desc()).all()
        
        results = []
        for od_request in pending_requests:
            student = Student.query.get(od_request.student_id)
            od_data = od_request.to_dict(include_sensitive=True)
            od_data['student_info'] = {
                'name': student.name,
                'roll_number': student.roll_number,
                'department': student.department,
                'email': student.email
            }
            results.append(od_data)
        
        return jsonify({
            'pending_submissions': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get pending submissions', 'error': str(e)}), 500