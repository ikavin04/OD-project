from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Student, Faculty, ODRequest, ODStatus, ODType, ProofStatus, UserRole
from datetime import datetime, timezone
from app.utils.auth_utils import get_current_user
from sqlalchemy import or_, and_

faculty_bp = Blueprint('faculty', __name__)

def get_current_faculty():
    """Get current faculty user from JWT token"""
    user, user_type = get_current_user()
    if user_type == 'faculty':
        return user
    return None

def check_faculty_permission(faculty, required_roles=None):
    """Check if faculty has required permissions"""
    if not faculty:
        return False
    
    if required_roles is None:
        required_roles = [UserRole.FACULTY, UserRole.HOD, UserRole.ADMIN]
    
    return faculty.role in required_roles

@faculty_bp.route('/od-requests', methods=['GET'])
@jwt_required()
def get_od_requests():
    """Get OD requests for faculty review"""
    try:
        faculty = get_current_faculty()
        if not faculty:
            return jsonify({'message': 'Access denied'}), 403
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status')
        department_filter = request.args.get('department')
        od_type_filter = request.args.get('od_type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        search = request.args.get('search')
        
        # Build base query with student details
        query = ODRequest.query.join(Student).add_columns(
            Student.name, Student.roll_number, Student.department
        )
        
        # Apply filters
        if status_filter:
            try:
                status = ODStatus(status_filter)
                query = query.filter(ODRequest.status == status)
            except ValueError:
                return jsonify({'message': 'Invalid status filter'}), 400
        
        if department_filter:
            query = query.filter(Student.department == department_filter)
        elif faculty.role == UserRole.FACULTY:
            # Faculty can only see requests from their department
            query = query.filter(Student.department == faculty.department)
        
        if od_type_filter:
            try:
                od_type = ODType(od_type_filter)
                query = query.filter(ODRequest.od_type == od_type)
            except ValueError:
                return jsonify({'message': 'Invalid OD type filter'}), 400
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(ODRequest.from_date >= date_from_obj)
            except ValueError:
                return jsonify({'message': 'Invalid date_from format'}), 400
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(ODRequest.to_date <= date_to_obj)
            except ValueError:
                return jsonify({'message': 'Invalid date_to format'}), 400
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Student.name.ilike(search_term),
                    Student.roll_number.ilike(search_term),
                    ODRequest.event_name.ilike(search_term),
                    ODRequest.host_institution.ilike(search_term),
                    ODRequest.college_name.ilike(search_term)
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(ODRequest.created_at.desc())
        
        # Paginate
        od_requests = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Format results
        results = []
        for od_request, student_name, roll_number, department in od_requests.items:
            od_data = od_request.to_dict(include_sensitive=True)
            od_data['student_info'] = {
                'name': student_name,
                'roll_number': roll_number,
                'department': department
            }
            results.append(od_data)
        
        return jsonify({
            'od_requests': results,
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

@faculty_bp.route('/od-requests/<int:od_id>/approve', methods=['POST'])
@jwt_required()
def approve_od_request(od_id):
    """Approve an OD request"""
    try:
        faculty = get_current_faculty()
        if not faculty:
            return jsonify({'message': 'Access denied'}), 403
        
        od_request = ODRequest.query.get_or_404(od_id)
        
        if od_request.status != ODStatus.PENDING:
            return jsonify({'message': 'Only pending OD requests can be approved'}), 400
        
        # Check if faculty can approve requests from this department
        student = Student.query.get(od_request.student_id)
        if faculty.role == UserRole.FACULTY and student.department != faculty.department:
            return jsonify({'message': 'You can only approve requests from your department'}), 403
        
        # Get approval comments
        data = request.get_json() or {}
        comments = data.get('comments', '')
        
        # Update OD request
        od_request.status = ODStatus.APPROVED
        od_request.faculty_id = faculty.id
        od_request.approval_comments = comments
        od_request.approved_at = datetime.now(timezone.utc)
        od_request.updated_at = datetime.now(timezone.utc)
        
        # Set proof submission deadlines
        od_request.set_approval_deadlines()
        
        db.session.commit()
        
        # TODO: Send approval email notification to student
        
        return jsonify({
            'message': 'OD request approved successfully',
            'od_request': od_request.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to approve OD request', 'error': str(e)}), 500

@faculty_bp.route('/od-requests/<int:od_id>/reject', methods=['POST'])
@jwt_required()
def reject_od_request(od_id):
    """Reject an OD request"""
    try:
        faculty = get_current_faculty()
        if not faculty:
            return jsonify({'message': 'Access denied'}), 403
        
        od_request = ODRequest.query.get_or_404(od_id)
        
        if od_request.status != ODStatus.PENDING:
            return jsonify({'message': 'Only pending OD requests can be rejected'}), 400
        
        # Check if faculty can reject requests from this department
        student = Student.query.get(od_request.student_id)
        if faculty.role == UserRole.FACULTY and student.department != faculty.department:
            return jsonify({'message': 'You can only reject requests from your department'}), 403
        
        # Get rejection comments (required)
        data = request.get_json() or {}
        comments = data.get('comments', '').strip()
        
        if not comments:
            return jsonify({'message': 'Rejection comments are required'}), 400
        
        # Update OD request
        od_request.status = ODStatus.REJECTED
        od_request.faculty_id = faculty.id
        od_request.approval_comments = comments
        od_request.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        # TODO: Send rejection email notification to student
        
        return jsonify({
            'message': 'OD request rejected successfully',
            'od_request': od_request.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to reject OD request', 'error': str(e)}), 500

@faculty_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for faculty"""
    try:
        faculty = get_current_faculty()
        if not faculty:
            return jsonify({'message': 'Access denied'}), 403
        
        # Base query - filter by department for faculty role
        if faculty.role == UserRole.FACULTY:
            base_query = ODRequest.query.join(Student).filter(
                Student.department == faculty.department
            )
        else:
            base_query = ODRequest.query
        
        # Get statistics
        total_requests = base_query.count()
        pending_requests = base_query.filter(ODRequest.status == ODStatus.PENDING).count()
        approved_requests = base_query.filter(ODRequest.status == ODStatus.APPROVED).count()
        rejected_requests = base_query.filter(ODRequest.status == ODStatus.REJECTED).count()
        
        # Proof submission statistics
        pending_proofs = base_query.filter(
            ODRequest.status == ODStatus.APPROVED,
            ODRequest.proof_submission_status == ProofStatus.NOT_SUBMITTED
        ).count()
        
        partial_proofs = base_query.filter(
            ODRequest.status == ODStatus.APPROVED,
            ODRequest.proof_submission_status == ProofStatus.ATTENDANCE_SUBMITTED
        ).count()
        
        completed_proofs = base_query.filter(
            ODRequest.status == ODStatus.APPROVED,
            ODRequest.proof_submission_status == ProofStatus.COMPLETED
        ).count()
        
        # Recent activity (last 7 days)
        from datetime import date, timedelta
        week_ago = date.today() - timedelta(days=7)
        recent_requests = base_query.filter(
            ODRequest.created_at >= week_ago
        ).count()
        
        return jsonify({
            'stats': {
                'total_requests': total_requests,
                'pending_requests': pending_requests,
                'approved_requests': approved_requests,
                'rejected_requests': rejected_requests,
                'pending_proofs': pending_proofs,
                'partial_proofs': partial_proofs,
                'completed_proofs': completed_proofs,
                'recent_requests': recent_requests
            },
            'faculty_info': faculty.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get dashboard stats', 'error': str(e)}), 500

@faculty_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """Get list of departments (for HOD/Admin)"""
    try:
        faculty = get_current_faculty()
        if not faculty:
            return jsonify({'message': 'Access denied'}), 403
        
        if faculty.role == UserRole.FACULTY:
            # Faculty can only see their own department
            return jsonify({'departments': [faculty.department]}), 200
        
        # HOD/Admin can see all departments
        departments = db.session.query(Student.department).distinct().all()
        department_list = [dept[0] for dept in departments]
        
        return jsonify({'departments': department_list}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get departments', 'error': str(e)}), 500