# Flask Backend Setup Guide

## Prerequisites

1. **Python 3.8+**
2. **PostgreSQL 12+** 
3. **Git**

## Quick Start

### 1. PostgreSQL Setup

Make sure PostgreSQL is installed and running. The database 'OD' should already exist with your credentials:

- **Username:** postgres
- **Password:** Kavin04  
- **Database:** OD

If the database doesn't exist, create it:

```sql
-- Connect to PostgreSQL as postgres user
CREATE DATABASE "OD";
```

### 2. Set up Python Environment

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# The database is already configured for:
# DATABASE_URL=postgresql://postgres:Kavin04@localhost:5432/OD
# No changes needed unless you want to modify email settings
```

### 4. Initialize Database

```bash
# Run database initialization script
python init_db.py
```

### 5. Start the Application

```bash
# Start Flask development server
python run.py
```

The API will be available at: `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/student/register` - Student registration
- `POST /api/auth/student/login` - Student login  
- `POST /api/auth/faculty/login` - Faculty/Admin login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

### Student Dashboard
- `GET /api/student/dashboard` - Get dashboard stats
- `GET /api/student/profile` - Get profile
- `PUT /api/student/profile` - Update profile
- `POST /api/student/check-availability` - Check OD availability
- `POST /api/student/change-password` - Change password

### OD Requests
- `POST /api/od/request` - Submit OD request (with file upload)
- `GET /api/od/my-requests` - Get student's OD requests
- `GET /api/od/<id>` - Get specific OD request
- `POST /api/od/<id>/cancel` - Cancel pending OD request
- `GET /api/od/download/<id>/<file_type>` - Download files

### Faculty Panel
- `GET /api/faculty/od-requests` - Get OD requests for review
- `POST /api/faculty/od-requests/<id>/approve` - Approve OD request
- `POST /api/faculty/od-requests/<id>/reject` - Reject OD request
- `GET /api/faculty/dashboard/stats` - Get dashboard statistics
- `GET /api/faculty/departments` - Get departments list

### Proof Submission
- `POST /api/proof/<id>/attendance` - Submit attendance proof
- `POST /api/proof/<id>/certificate` - Submit participation certificate
- `GET /api/proof/<id>/status` - Get proof submission status
- `POST /api/proof/<id>/reminder` - Send certificate reminder
- `GET /api/proof/pending-submissions` - Get pending submissions

## Default Login Credentials

After running `init_db.py`, you can use these credentials:

**Admin:**
- Email: admin@college.edu
- Password: admin123

**Faculty:**
- Email: faculty@college.edu  
- Password: faculty123

**HOD:**
- Email: hod@college.edu
- Password: hod123

**Student:**
- Email: student@college.edu
- Roll Number: CS2021001
- Password: student123

## File Upload Configuration

- **Allowed Types:** PNG, JPG, JPEG, PDF
- **Max File Size:** 16MB
- **Upload Folders:**
  - `uploads/od-applications/` - OD application files
  - `uploads/proofs/` - Attendance proof files  
  - `uploads/certificates/` - Participation certificates

## Features Implemented

✅ **Authentication & Authorization**
- JWT-based authentication
- Role-based access control (Student, Faculty, HOD, Admin)
- Separate login systems for students and faculty
- Password hashing and validation

✅ **OD Request Workflow**
- Student OD request submission with file upload
- Date validation and conflict checking
- Faculty approval/rejection with comments
- File duplicate prevention

✅ **Proof Submission System**
- Attendance proof upload (mandatory)
- Participation certificate upload (optional)
- File validation and duplicate prevention
- Proof submission timeline enforcement

✅ **Faculty Management**
- Department-based access control
- OD request review and approval
- Dashboard with statistics
- Search and filter functionality

✅ **Security Features**
- File type validation using python-magic
- SHA-256 file hashing for duplicate detection
- SQL injection prevention with SQLAlchemy
- Rate limiting and CORS protection
- Secure file upload handling

## Testing the API

You can test the API using tools like Postman or curl:

```bash
# Student Registration
curl -X POST http://localhost:5000/api/auth/student/register \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "CS2021002", 
    "email": "test@college.edu",
    "password": "password123",
    "name": "Test Student",
    "department": "Computer Science",
    "year": 2,
    "semester": 3
  }'

# Student Login
curl -X POST http://localhost:5000/api/auth/student/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "test@college.edu",
    "password": "password123"
  }'
```

## Next Steps

1. ✅ Flask backend with all core features
2. 🚧 Email notification system (In Progress)
3. 🚧 OCR certificate validation (In Progress)  
4. ⏳ React frontend (Next)
5. ⏳ Production deployment setup