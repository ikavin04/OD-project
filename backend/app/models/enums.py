"""
Enumerations for the OD Management System
"""
import enum

class UserRole(enum.Enum):
    """User roles in the system"""
    STUDENT = "student"
    FACULTY = "faculty"
    HOD = "hod"
    ADMIN = "admin"

class ODStatus(enum.Enum):
    """OD request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ODType(enum.Enum):
    """Types of OD requests"""
    INTRA_COLLEGE = "intra_college"
    INTER_COLLEGE_COIMBATORE = "inter_college_coimbatore"
    INTER_COLLEGE_OTHERS = "inter_college_others"

class ProofStatus(enum.Enum):
    """Proof submission status"""
    NOT_SUBMITTED = "NOT_SUBMITTED"
    attendance_pending = "attendance_pending"  # Within 3 days after approval
    ATTENDANCE_SUBMITTED = "ATTENDANCE_SUBMITTED"
    certificate_pending = "certificate_pending"  # Within 1 month after attendance
    certificate_submitted = "certificate_submitted"
    COMPLETED = "COMPLETED"