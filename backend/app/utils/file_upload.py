"""
File upload utilities for the OD Management System
"""
import os
import hashlib
import uuid
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

class FileUploadService:
    """Service for handling file uploads"""
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_file_hash(file_data):
        """Generate MD5 hash of file content"""
        return hashlib.md5(file_data).hexdigest()
    
    @staticmethod
    def generate_unique_filename(original_filename):
        """Generate a unique filename while preserving extension"""
        if original_filename:
            name, ext = os.path.splitext(original_filename)
            unique_name = f"{uuid.uuid4().hex}{ext}"
            return secure_filename(unique_name)
        return None
    
    @staticmethod
    def save_file(file, folder_name, allowed_extensions=None):
        """
        Save uploaded file to specified folder
        
        Args:
            file: FileStorage object from request.files
            folder_name: Subfolder name under UPLOAD_FOLDER
            allowed_extensions: Set of allowed extensions (optional)
        
        Returns:
            dict: File information or None if error
        """
        if not file or file.filename == '':
            return None
        
        # Check file extension
        if allowed_extensions:
            if not FileUploadService.allowed_file_custom(file.filename, allowed_extensions):
                return None
        elif not FileUploadService.allowed_file(file.filename):
            return None
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return None
        
        # Generate unique filename
        original_filename = file.filename
        unique_filename = FileUploadService.generate_unique_filename(original_filename)
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        folder_path = os.path.join(upload_folder, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(folder_path, unique_filename)
        full_path = os.path.join(os.getcwd(), file_path)
        
        try:
            file.save(full_path)
            
            # Get file hash
            with open(full_path, 'rb') as f:
                file_hash = FileUploadService.get_file_hash(f.read())
            
            return {
                'filename': unique_filename,
                'original_name': original_filename,
                'file_path': file_path,
                'full_path': full_path,
                'file_size': file_size,
                'mime_type': file.content_type,
                'file_hash': file_hash,
                'uploaded_at': datetime.utcnow()
            }
        
        except Exception as e:
            # Clean up if save failed
            if os.path.exists(full_path):
                os.remove(full_path)
            return None
    
    @staticmethod
    def allowed_file_custom(filename, allowed_extensions):
        """Check if file extension is in custom allowed extensions"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def delete_file(file_path):
        """Delete a file from the filesystem"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            pass
        return False
    
    @staticmethod
    def validate_image_file(file):
        """Validate that uploaded file is a valid image"""
        if not file:
            return False
        
        image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        return FileUploadService.allowed_file_custom(file.filename, image_extensions)
    
    @staticmethod
    def validate_document_file(file):
        """Validate that uploaded file is a valid document"""
        if not file:
            return False
        
        doc_extensions = {'pdf', 'doc', 'docx', 'txt'}
        return FileUploadService.allowed_file_custom(file.filename, doc_extensions)