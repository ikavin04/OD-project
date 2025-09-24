# OD Management System - Project Instructions

This is a comprehensive OD (On Duty) Management System built with:
- **Backend**: Node.js with Express.js
- **Frontend**: React.js 
- **Database**: MongoDB
- **Authentication**: JWT-based with role-based access control
- **File Processing**: OCR for certificate validation
- **Notifications**: Email system for reminders and updates

## Project Structure
```
od-management-system/
├── backend/              # Node.js Express API
├── frontend/             # React.js application
├── shared/               # Shared utilities and types
└── docs/                 # Documentation
```

## Key Features
- Separate authentication for students and faculty/admin
- Two-step OD workflow (Request → Proof submission)
- OCR-based certificate validation
- Role-based access control
- Email notification system
- File upload security
- Duplicate prevention

## Development Guidelines
- Follow REST API conventions
- Implement proper error handling
- Use TypeScript for type safety
- Implement comprehensive logging
- Follow security best practices