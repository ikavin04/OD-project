# OCR Certificate Validation Setup Guide

## Overview
The OD Management System now includes OCR (Optical Character Recognition) validation for certificate uploads. This feature automatically detects if an uploaded certificate is valid by scanning for certificate-related keywords.

## How It Works

When a student uploads a certificate, the system:
1. **Extracts text** from the image using Tesseract OCR
2. **Scans for keywords** like "certificate", "participation", "awarded", "completion", etc.
3. **Calculates confidence** based on keyword matches
4. **Validates** the certificate (requires at least 1 keyword match)
5. **Rejects invalid uploads** with a clear error message

## Installation Instructions

### Windows

1. **Download Tesseract OCR:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

2. **Install Tesseract:**
   - Run the installer
   - **Important:** During installation, note the installation path (e.g., `C:\Program Files\Tesseract-OCR`)
   - Check "Add to PATH" option if available

3. **Add to PATH (if not done automatically):**
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click Edit
   - Click "New" and add: `C:\Program Files\Tesseract-OCR`
   - Click OK on all windows

4. **Verify Installation:**
   ```bash
   tesseract --version
   ```

5. **Alternative: Configure in Code**
   If you don't want to modify PATH, add this to `main.py` after imports:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
tesseract --version
```

### macOS

```bash
brew install tesseract
tesseract --version
```

## Testing OCR Setup

Run the test script:
```bash
cd backend
python test_ocr.py
```

Expected output:
```
✓ Tesseract OCR version: 5.x.x
✓ OCR is properly configured
✓ Creating test image with certificate text...
✓ OCR test successful

Certificate validation is ready to use!
```

## Features

### Keyword Detection
The system looks for these certificate-related keywords:
- certificate, certify, certification
- awarded, presented
- participation, participant
- achievement, completion
- recognition, honor, excellence
- "successfully completed"
- "hereby certify"
- "this is to certify"

### Confidence Scoring
- **100%**: 3+ keywords detected
- **66%**: 2 keywords detected
- **33%**: 1 keyword detected
- **0%**: No keywords (certificate rejected)

### Validation Requirements
- Minimum 1 keyword required for validation to pass
- Image files only (JPEG, PNG, etc.)
- Clear, readable text in the certificate

## Error Handling

### If Tesseract is Not Installed
The system gracefully handles missing Tesseract:
- Prints a warning in the console
- **Allows uploads without validation** (fail-safe mode)
- Shows installation instructions

### If OCR Fails
- Logs the error
- **Allows the upload** (prevents blocking legitimate certificates)
- Admin should check manually

## Production Deployment

For production servers:

1. **Install Tesseract** on your server:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-eng
   
   # CentOS/RHEL
   sudo yum install tesseract
   ```

2. **Verify installation:**
   ```bash
   which tesseract
   tesseract --version
   ```

3. **Restart your Flask application**

## Troubleshooting

### "Tesseract is not installed or it's not in your PATH"
- Ensure Tesseract is installed
- Check PATH environment variable
- Restart your terminal/IDE after installation
- Use direct path configuration in code

### "Low confidence score for valid certificates"
- Ensure certificate image is clear and high resolution
- Check if text is readable (not too small, blurry, or distorted)
- Consider adjusting keyword list for specific certificate types

### "Valid certificates being rejected"
- Add more relevant keywords to the `certificate_keywords` list
- Reduce minimum keyword requirement from 1 to 0 (not recommended)
- Check OCR output in console logs for debugging

## Advanced Configuration

### Custom Keywords
Edit `main.py` and modify the `certificate_keywords` list in the `validate_certificate_with_ocr` function:

```python
certificate_keywords = [
    'certificate',
    'your_custom_keyword',
    # Add more keywords specific to your certificates
]
```

### Adjust Confidence Threshold
Modify the validation logic:
```python
# Current: Require at least 1 keyword
is_valid = matches >= 1

# Stricter: Require at least 2 keywords
is_valid = matches >= 2
```

## API Response

### Successful Upload (Valid Certificate)
```json
{
  "message": "Certificate submitted successfully. Your OD process is now complete!",
  "od_request": {...}
}
```

### Rejected Upload (Invalid Certificate)
```json
{
  "error": "Invalid certificate detected",
  "message": "The uploaded file does not appear to be a valid certificate. Please upload a clear image of your participation certificate.",
  "confidence_score": 0.0
}
```

## Benefits

1. **Fraud Prevention**: Reduces fake certificate uploads
2. **Quality Control**: Ensures uploaded certificates are readable
3. **Automatic Validation**: No manual checking required for obvious cases
4. **User Feedback**: Clear error messages guide students to upload correct files
5. **Graceful Degradation**: Works even if OCR is unavailable

## Notes

- OCR works best with **clear, high-resolution images**
- **Scanned certificates** work better than photos
- **PDF certificates** are not supported by this validation (only images)
- The system is designed to **fail open** (allow uploads on errors) to prevent blocking legitimate certificates
