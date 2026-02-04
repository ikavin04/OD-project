"""
ImgBB & Catbox File Upload Helper
- ImgBB: For images (JPG, PNG) - Free API with permanent links
- Catbox.moe: For PDFs and documents - Free, no API key needed
"""

import os
import requests
import base64
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Get ImgBB API key from environment
IMGBB_API_KEY = os.environ.get('IMGBB_API_KEY', '')
IMGBB_UPLOAD_URL = 'https://api.imgbb.com/1/upload'
CATBOX_UPLOAD_URL = 'https://catbox.moe/user/api.php'


def upload_image_to_imgbb(file_path: str) -> Optional[str]:
    """
    Upload image to ImgBB and return permanent view link.
    
    Args:
        file_path: Local path to image file (JPG, PNG, etc.)
    
    Returns:
        Direct view URL or None if upload fails
    """
    if not IMGBB_API_KEY:
        logger.error("IMGBB_API_KEY not set in environment")
        return None
    
    try:
        # Read and encode image as base64
        with open(file_path, 'rb') as file:
            image_data = base64.b64encode(file.read()).decode('utf-8')
        
        # Upload to ImgBB
        payload = {
            'key': IMGBB_API_KEY,
            'image': image_data,
            'name': os.path.basename(file_path)
        }
        
        response = requests.post(IMGBB_UPLOAD_URL, data=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('success'):
            view_url = result['data']['url']
            logger.info(f"✓ Uploaded image to ImgBB: {view_url}")
            return view_url
        else:
            logger.error(f"ImgBB upload failed: {result}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to upload image to ImgBB: {e}")
        return None


def upload_pdf_to_catbox(file_path: str) -> Optional[str]:
    """
    Upload PDF/document to Catbox.moe and return permanent download link.
    
    Args:
        file_path: Local path to PDF or document file
    
    Returns:
        Direct download URL or None if upload fails
    """
    try:
        # Upload to Catbox.moe
        with open(file_path, 'rb') as file:
            files = {
                'fileToUpload': (os.path.basename(file_path), file)
            }
            data = {
                'reqtype': 'fileupload'
            }
            
            response = requests.post(CATBOX_UPLOAD_URL, files=files, data=data, timeout=60)
            response.raise_for_status()
            
            # Catbox returns the direct URL as plain text
            download_url = response.text.strip()
            
            if download_url.startswith('http'):
                logger.info(f"✓ Uploaded PDF to Catbox: {download_url}")
                return download_url
            else:
                logger.error(f"Catbox upload failed: {download_url}")
                return None
                
    except Exception as e:
        logger.error(f"Failed to upload PDF to Catbox: {e}")
        return None


def upload_file(file_path: str) -> Optional[str]:
    """
    Smart upload: Images to ImgBB, PDFs to Catbox.
    
    Args:
        file_path: Local path to file
    
    Returns:
        Public view/download URL or None if upload fails
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Route to appropriate service
    if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        return upload_image_to_imgbb(file_path)
    elif file_ext in ['.pdf', '.doc', '.docx']:
        return upload_pdf_to_catbox(file_path)
    else:
        logger.warning(f"Unsupported file type: {file_ext}, trying Catbox")
        return upload_pdf_to_catbox(file_path)
