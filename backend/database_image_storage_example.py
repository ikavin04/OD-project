# Example: Adding BYTEA field to store images directly in PostgreSQL

# Add this to your ODRequest model:
application_file_data = db.Column(db.LargeBinary)  # Stores actual image bytes
attendance_proof_data = db.Column(db.LargeBinary)  # For attendance proof
certificate_data = db.Column(db.LargeBinary)  # For certificates

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
    
    # Calculate hash for deduplication
    import hashlib
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
    
    return jsonify({'error': 'File not found'}), 404