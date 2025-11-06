"""
File upload utilities for the OD Management System
"""
import os
import hashlib
import uuid
import io
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
MIN_IMAGE_DIMENSION = 50  # Minimum width/height in pixels
MAX_IMAGE_DIMENSION = 4096  # Maximum width/height in pixels
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
            tuple: (dict, str) - (File information or None, error message if any)
        """
        if not file or file.filename == '':
            return None, "No file provided"
        
        # Special handling for image files
        if folder_name in ['certificates', 'proofs']:
            is_valid, error_msg = FileUploadService.validate_image_file(file)
            if not is_valid:
                return None, error_msg
        else:
            # Check file extension for non-image files
            if allowed_extensions:
                if not FileUploadService.allowed_file_custom(file.filename, allowed_extensions):
                    return None, "Invalid file type"
            elif not FileUploadService.allowed_file(file.filename):
                return None, "Invalid file type"
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return None, f"File too large. Maximum size: {MAX_FILE_SIZE/(1024*1024)}MB"
        elif file_size == 0:
            return None, "File is empty"
        
        # Special handling for image uploads
        if folder_name in ['certificates', 'proofs']:
            is_valid, error_msg = FileUploadService.validate_image_file(file)
            if not is_valid:
                return None, error_msg

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
        """
        Validate that uploaded file is a valid image with acceptable dimensions
        Returns: (bool, str) - (is_valid, error_message)
        """
        if not file:
            return False, "No file provided"
        
        image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not FileUploadService.allowed_file_custom(file.filename, image_extensions):
            return False, "Invalid image format. Allowed formats: PNG, JPG, JPEG, GIF"
        
        try:
            # Read the image using PIL
            image_data = file.read()
            file.seek(0)  # Reset file pointer after reading
            
            if len(image_data) == 0:
                return False, "Empty file"
                
            img = Image.open(io.BytesIO(image_data))
            
            # Check image dimensions
            width, height = img.size
            if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
                return False, f"Image too small. Minimum dimensions: {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION} pixels"
                
            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                return False, f"Image too large. Maximum dimensions: {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION} pixels"
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    @staticmethod
    def validate_document_file(file):
        """Validate that uploaded file is a valid document"""
        if not file:
            return False
        
        doc_extensions = {'pdf', 'doc', 'docx', 'txt'}
        return FileUploadService.allowed_file_custom(file.filename, doc_extensions)