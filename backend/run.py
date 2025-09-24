from app import create_app, db
from app.models import Student, Faculty, ODRequest
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask application
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'Student': Student,
        'Faculty': Faculty,
        'ODRequest': ODRequest
    }

@app.cli.command("init-db")
def init_db_command():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")

@app.cli.command("create-admin")
def create_admin_command():
    """Create an admin user"""
    from app.models.user import UserRole
    
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)