"""
Complete Example: PostgreSQL Database Storage for Images
This is a working example showing how to store files directly in PostgreSQL
"""

# Required imports
from flask import Flask, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required
from werkzeug.utils import secure_filename
import hashlib

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/od_management'
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this in production

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Example ODRequest model with BYTEA fields for file storage
class ODRequest(db.Model):
    __tablename__ = 'od_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Application file stored as binary data
    application_filename = db.Column(db.String(255))
    application_file_data = db.Column(db.LargeBinary)  # Stores actual image bytes
    application_mime_type = db.Column(db.String(100))
    application_file_size = db.Column(db.Integer)
    
    # Attendance proof stored as binary data
    attendance_proof_filename = db.Column(db.String(255))
    attendance_proof_data = db.Column(db.LargeBinary)  # For attendance proof
    attendance_proof_mime_type = db.Column(db.String(100))
    attendance_proof_file_size = db.Column(db.Integer)
    
    # Certificate stored as binary data
    certificate_filename = db.Column(db.String(255))
    certificate_data = db.Column(db.LargeBinary)  # For certificates
    certificate_mime_type = db.Column(db.String(100))
    certificate_file_size = db.Column(db.Integer)

# Modified save_file function to store in database:
def save_file_to_db(file, od_request, file_type):
    """Save file directly to database as binary data"""
    
    # Read file content
    file_content = file.read()
    file.seek(0)  # Reset file pointer
    
    # Store in database based on type
    if file_type == 'application':
        od_request.application_file_data = file_content
        od_request.application_filename = secure_filename(file.filename)
        od_request.application_mime_type = file.content_type
        od_request.application_file_size = len(file_content)
    
    elif file_type == 'attendance':
        od_request.attendance_proof_data = file_content
        od_request.attendance_proof_filename = secure_filename(file.filename)
        od_request.attendance_proof_mime_type = file.content_type
        od_request.attendance_proof_file_size = len(file_content)
    
    elif file_type == 'certificate':
        od_request.certificate_data = file_content
        od_request.certificate_filename = secure_filename(file.filename)
        od_request.certificate_mime_type = file.content_type
        od_request.certificate_file_size = len(file_content)
    
    # Calculate hash for deduplication
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    db.session.commit()
    return True

# Route to serve images from database:
@app.route('/api/od-requests/<int:request_id>/image/<file_type>')
@jwt_required()
def serve_image_from_db(request_id, file_type):
    """Serve image directly from database"""
    
    od_request = ODRequest.query.get_or_404(request_id)
    
    if file_type == 'application' and od_request.application_file_data:
        return Response(
            od_request.application_file_data,
            mimetype=od_request.application_mime_type,
            headers={
                'Content-Disposition': f'inline; filename="{od_request.application_filename}"'
            }
        )
    
    elif file_type == 'attendance' and od_request.attendance_proof_data:
        return Response(
            od_request.attendance_proof_data,
            mimetype=od_request.attendance_proof_mime_type,
            headers={
                'Content-Disposition': f'inline; filename="{od_request.attendance_proof_filename}"'
            }
        )
    
    elif file_type == 'certificate' and od_request.certificate_data:
        return Response(
            od_request.certificate_data,
            mimetype=od_request.certificate_mime_type,
            headers={
                'Content-Disposition': f'inline; filename="{od_request.certificate_filename}"'
            }
        )
    
    return jsonify({'error': 'File not found'}), 404

# Create tables
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)