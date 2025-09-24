# OD Management System - Flask Backend# OD Management System - Backend



A comprehensive Flask-based backend API for the OD (On Duty) Management System with PostgreSQL database.A comprehensive backend API for the On Duty (OD) Management System built with Node.js, Express, and MongoDB.



## Features## Features



- **Authentication**: JWT-based authentication with separate login for students and faculty- **Dual Authentication System**: Separate login systems for students and faculty/admin

- **Role-based Access**: Student, Faculty, HOD, Admin roles with appropriate permissions- **Role-Based Access Control**: Faculty, HOD, and Admin roles with different permissions

- **Database**: PostgreSQL with SQLAlchemy ORM- **Two-Step OD Workflow**: OD request submission followed by proof submission

- **File Upload**: Secure file handling for OD applications, proofs, and certificates- **OCR Integration**: Automatic text extraction from certificates for validation

- **OCR Processing**: Automatic certificate validation using Tesseract OCR- **Email Notifications**: Automated notifications for all stakeholders

- **Email Notifications**: Automated emails for confirmations, reminders, and status updates- **File Upload Security**: Secure file handling with validation and duplicate prevention

- **Security**: Rate limiting, input validation, and secure file storage- **Comprehensive API**: RESTful API with proper error handling and validation



## Tech Stack## Tech Stack



- **Framework**: Flask 2.3.3- **Runtime**: Node.js

- **Database**: PostgreSQL with SQLAlchemy- **Framework**: Express.js

- **Authentication**: Flask-JWT-Extended- **Database**: MongoDB with Mongoose ODM

- **Email**: Flask-Mail- **Authentication**: JWT (JSON Web Tokens)

- **OCR**: Tesseract.js via pytesseract- **File Upload**: Multer

- **File Processing**: Pillow, PyPDF2- **OCR**: Tesseract.js

- **Validation**: Marshmallow- **Email**: Nodemailer

- **Security**: Flask-Limiter, Flask-CORS- **Validation**: Express Validator

- **Security**: Helmet, CORS, Rate Limiting

## Project Structure

## Installation

```

backend/1. **Clone the repository**

├── app/   ```bash

│   ├── __init__.py          # Flask app factory   git clone <repository-url>

│   ├── models/              # Database models   cd od-management-system/backend

│   │   ├── __init__.py   ```

│   │   ├── user.py          # Student and Faculty models

│   │   └── od_request.py    # OD Request model2. **Install dependencies**

│   ├── routes/              # API routes   ```bash

│   │   ├── auth.py          # Authentication endpoints   npm install

│   │   ├── student.py       # Student-specific routes   ```

│   │   ├── faculty.py       # Faculty/Admin routes

│   │   ├── od.py           # OD request routes3. **Environment Setup**

│   │   └── proof.py        # Proof submission routes   ```bash

│   ├── services/           # Business logic   cp .env.example .env

│   └── utils/              # Utility functions   ```

├── migrations/             # Database migrations   

├── uploads/               # File uploads   Update the `.env` file with your configuration:

├── config.py             # Configuration settings   ```env

├── requirements.txt      # Python dependencies   NODE_ENV=development

├── run.py               # Application entry point   PORT=5000

└── .env.example         # Environment variables template   MONGODB_URI=mongodb://localhost:27017/od-management

```   JWT_SECRET=your-super-secret-jwt-key-here

   JWT_EXPIRES_IN=7d

## Setup Instructions   

   # Email Configuration

### 1. Prerequisites   EMAIL_HOST=smtp.gmail.com

   EMAIL_PORT=587

- Python 3.8+   EMAIL_USER=your-email@gmail.com

- PostgreSQL 12+   EMAIL_PASS=your-app-password

- Tesseract OCR   EMAIL_FROM=OD Management System <your-email@gmail.com>

   

### 2. Install Dependencies   # File Upload

   MAX_FILE_SIZE=5242880

```bash   FRONTEND_URL=http://localhost:3000

# Create virtual environment   ```

python -m venv venv

4. **Start the server**

# Activate virtual environment   ```bash

# On Windows:   # Development mode

venv\Scripts\activate   npm run dev

# On macOS/Linux:   

source venv/bin/activate   # Production mode

   npm start

# Install dependencies   ```

pip install -r requirements.txt

```## API Endpoints



### 3. Database Setup### Authentication Routes (`/api/auth`)



```sql- `POST /student/register` - Register new student

-- Create database and user- `POST /student/login` - Student login

CREATE DATABASE od_development;- `POST /faculty/register` - Register new faculty

CREATE USER od_user WITH PASSWORD 'od_password';- `POST /faculty/login` - Faculty login

GRANT ALL PRIVILEGES ON DATABASE od_development TO od_user;- `POST /logout` - Logout

```

### Student Routes (`/api/student`)

### 4. Environment Configuration

- `GET /dashboard` - Get student dashboard data

```bash- `GET /profile` - Get student profile

# Copy environment template- `PUT /profile` - Update student profile

cp .env.example .env

### Faculty Routes (`/api/faculty`)

# Edit .env file with your configuration

```- `GET /dashboard` - Get faculty dashboard

- `GET /students` - Get students list

### 5. Initialize Database- `GET /reports` - Get OD reports and analytics

- `GET /profile` - Get faculty profile

```bash- `PUT /profile` - Update faculty profile

# Set Flask app- `POST /manage-user` - Manage user accounts (Admin only)

export FLASK_APP=run.py

### OD Management Routes (`/api/od`)

# Initialize database

flask init-db- `POST /request` - Submit new OD request

- `POST /:id/proofs` - Submit proofs for approved OD

# Create admin user- `GET /my-requests` - Get student's OD requests

flask create-admin- `GET /all` - Get all OD requests (Faculty)

```- `PUT /:id/review` - Approve/reject OD request

- `GET /:id` - Get single OD request details

### 6. Run Application

### File Upload Routes (`/api/upload`)

```bash

# Development mode- `POST /single` - Upload single file

python run.py- `POST /ocr` - Upload file and extract text

- `GET /file/:filename` - Serve uploaded files

# Or using Flask CLI- `DELETE /file/:filename` - Delete uploaded file

flask run --host=0.0.0.0 --port=5000- `GET /validate-duplicate/:hash` - Check for duplicate files

```

## Database Models

## API Endpoints

### Student Model

### Authentication- Personal information (name, roll number, email, department)

- `POST /api/auth/student/register` - Student registration- Academic details (year, semester)

- `POST /api/auth/student/login` - Student login- Authentication credentials

- `POST /api/auth/faculty/login` - Faculty/Admin login- Activity tracking

- `POST /api/auth/refresh` - Refresh access token

- `GET /api/auth/me` - Get current user info### Faculty Model

- `POST /api/auth/logout` - Logout- Personal information (name, employee ID, email, department)

- Role-based permissions (Faculty, HOD, Admin)

### OD Requests (Coming Next)- Approval capabilities

- `POST /api/od/request` - Submit OD request- Activity tracking

- `GET /api/od/my-requests` - Get student's OD requests

- `PUT /api/od/:id/approve` - Approve OD request### ODRequest Model

- `PUT /api/od/:id/reject` - Reject OD request- Student information

- Event details (name, dates, type, description)

### Proof Submission (Coming Next)- Institution information

- `POST /api/proof/:id/attendance` - Submit attendance proof- File attachments (OD application, proofs, certificates)

- `POST /api/proof/:id/certificate` - Submit certificate- OCR validation results

- `GET /api/proof/:id/status` - Get proof status- Approval workflow tracking



## Environment Variables## Key Features



```env### OCR Integration

FLASK_APP=run.py- Automatic text extraction from images and PDFs

FLASK_ENV=development- Certificate validation against OD request details

SECRET_KEY=your-secret-key- Confidence scoring and validation status

DATABASE_URL=postgresql://od_user:od_password@localhost:5432/od_development- Support for JPEG, PNG, and PDF formats

JWT_SECRET_KEY=jwt-secret-key

MAIL_SERVER=smtp.gmail.com### Email Notifications

MAIL_USERNAME=your-email@gmail.com- Student confirmations and reminders

MAIL_PASSWORD=your-app-password- Faculty notifications for new requests and proof submissions

TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe- Approval/rejection notifications with comments

```- Automated reminder system for pending proofs



## Testing### Security Features

- JWT-based authentication

```bash- Role-based access control

# Run tests (when implemented)- File upload validation and size limits

python -m pytest- Duplicate file prevention

- Request rate limiting

# Run with coverage- Security headers with Helmet

python -m pytest --cov=app

```### File Management

- Organized file storage structure

## Deployment- Secure file serving with authentication

- File hash generation for duplicate prevention

For production deployment, use a WSGI server like Gunicorn:- Support for multiple file types



```bash## Development

# Install Gunicorn

pip install gunicorn### Project Structure

```

# Run with Gunicornbackend/

gunicorn -w 4 -b 0.0.0.0:5000 run:app├── src/

```│   ├── controllers/     # Route handlers

│   ├── middleware/      # Custom middleware

## Development Status│   ├── models/         # Database models

│   ├── routes/         # API routes

- ✅ Project structure and configuration│   ├── services/       # Business logic services

- ✅ Database models (Student, Faculty, ODRequest)│   ├── utils/          # Utility functions

- ✅ Authentication system with JWT│   └── server.js       # Main application file

- ✅ Student and Faculty login/registration├── uploads/            # File upload directories

- 🚧 OD request workflow (In Progress)│   ├── od-applications/

- 🚧 Proof submission system (In Progress)│   ├── proofs/

- ⏳ Email notifications (Planned)│   └── certificates/

- ⏳ OCR validation (Planned)├── package.json

- ⏳ Faculty/Admin dashboard (Planned)└── README.md

```

## Next Steps

### Available Scripts

1. Complete OD request workflow implementation- `npm start` - Start production server

2. Build proof submission system with OCR- `npm run dev` - Start development server with nodemon

3. Implement email notification service- `npm test` - Run tests

4. Create faculty/admin management endpoints- `npm run build` - No build step required for Node.js

5. Add comprehensive security features

6. Build React frontend components### Environment Variables
See `.env.example` for all required environment variables.

## Deployment

1. **Set environment to production**
   ```env
   NODE_ENV=production
   ```

2. **Configure database connection**
   ```env
   MONGODB_URI=mongodb://your-mongodb-url/od-management
   ```

3. **Set up email service**
   Configure SMTP settings for email notifications

4. **File storage**
   Ensure upload directories have proper permissions

5. **Security**
   - Use strong JWT secret
   - Configure CORS for your frontend domain
   - Set up proper SSL/HTTPS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.