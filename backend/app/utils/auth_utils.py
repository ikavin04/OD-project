from flask_jwt_extended import get_jwt_identity
from typing import Optional, Tuple
from app.models import Student, Faculty, UserRole

def get_current_user() -> Tuple[Optional[Student | Faculty], Optional[str]]:
    """
    Parses JWT identity string and fetches the current user from the database.

    Identity format: "student:<id>" or "faculty:<id>[:<role>]"
    
    Returns:
        A tuple of (user_object, user_type_string) or (None, None) if invalid.
    """
    identity = get_jwt_identity()
    if not identity or not isinstance(identity, str):
        return None, None

    parts = identity.split(":")
    if len(parts) < 2:
        return None, None

    user_type = parts[0]
    try:
        user_id = int(parts[1])
    except (ValueError, TypeError):
        return None, None

    if user_type == 'student':
        user = Student.query.get(user_id)
        return (user, 'student') if user else (None, None)
    
    if user_type == 'faculty':
        user = Faculty.query.get(user_id)
        return (user, 'faculty') if user else (None, None)

    return None, None

