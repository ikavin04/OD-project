import os
import hashlib
from werkzeug.utils import secure_filename
from flask import current_app
# import magic  # Commented out for Windows compatibility
from PIL import Image
import PyPDF2

class FileUploadService:
    """Service for handling file uploads with validation and security"""
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileUploadService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file_type(file_path):
        """Validate file type using file extension (fallback method)"""
        try:
            # For Windows compatibility, use file extension instead of python-magic
            file_ext = file_path.rsplit('.', 1)[1].lower()
            allowed_mime_types = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg', 
                'png': 'image/png',
                'pdf': 'application/pdf'
            }
            
            if file_ext in allowed_mime_types:
                return True, allowed_mime_types[file_ext]
            else:
                return False, None
                
        except Exception:
            return False, None
    
    @staticmethod
    def validate_image(file_path):
        """Validate image file"""
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_pdf(file_path):
        """Validate PDF file"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                # Check if PDF has at least one page
                return len(reader.pages) > 0
        except Exception:
            return False
    
    @staticmethod
    def generate_file_hash(file_path):
        """Generate SHA-256 hash of file for duplicate detection"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    @staticmethod
    def save_file(file, upload_type='general'):
        """
        Save uploaded file with validation
        upload_type: 'od-application', 'proof', 'certificate'
        """
        if not file or file.filename == '':
            return None, 'No file selected'
        
        # Check file extension
        if not FileUploadService.allowed_file(file.filename):
            return None, 'File type not allowed. Only PNG, JPG, JPEG, PDF are allowed.'
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > FileUploadService.MAX_FILE_SIZE:
            return None, f'File too large. Maximum size is {FileUploadService.MAX_FILE_SIZE // (1024*1024)}MB'
        
        if file_size == 0:
            return None, 'File is empty'
        
        # Create secure filename
        filename = secure_filename(file.filename)
        
        # Create unique filename with timestamp
        import time
        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        # Create upload directory
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], upload_type)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Validate file type after saving
        is_valid_type, mime_type = FileUploadService.validate_file_type(file_path)
        if not is_valid_type:
            os.remove(file_path)
            return None, 'Invalid file type detected'
        
        # Additional validation based on file type
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext in ['png', 'jpg', 'jpeg']:
            if not FileUploadService.validate_image(file_path):
                os.remove(file_path)
                return None, 'Invalid or corrupted image file'
        elif file_ext == 'pdf':
            if not FileUploadService.validate_pdf(file_path):
                os.remove(file_path)
                return None, 'Invalid or corrupted PDF file'
        
        # Generate file hash
        file_hash = FileUploadService.generate_file_hash(file_path)
        
        return {
            'filename': unique_filename,
            'original_name': filename,
            'file_path': file_path,
            'file_size': file_size,
            'mime_type': mime_type,
            'file_hash': file_hash
        }, None
    
    @staticmethod
    def delete_file(file_path):
        """Safely delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False