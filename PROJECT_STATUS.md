# OD Management System - Single Backend File

## 🎯 Current Structure
```
OD-project/
├── backend/
│   ├── main.py              ⭐ SINGLE BACKEND FILE (complete system)
│   ├── requirements.txt     📦 Dependencies
│   ├── .env                🔒 Environment variables
│   ├── uploads/            📁 File uploads
│   └── venv/               🐍 Python virtual environment
├── frontend/
│   └── (React application)
└── .vscode/
    └── settings.json       ⚙️ VS Code configuration
```

## 🚀 Quick Start

### Backend (Port 5000)
```bash
cd backend
& "C:/od project/.venv/Scripts/Activate.ps1"
python main.py
```

### Frontend (Port 3001)
```bash
cd frontend  
npm run dev
```

## ✅ What Works
- ✅ Single file backend (`main.py`)
- ✅ Student registration & login
- ✅ Faculty login & OD approval/rejection  
- ✅ File upload & download
- ✅ Email notifications
- ✅ JWT authentication
- ✅ PostgreSQL database
- ✅ CORS enabled for frontend

## 🛠️ VS Code Setup
1. Open project folder in VS Code
2. Select Python interpreter: `./backend/venv/Scripts/python.exe`
3. All functionality is in `backend/main.py`

## 📧 Email Configuration
- Gmail SMTP configured
- HTML email templates included
- DEMO mode fallback available

## 🗄️ Database
- PostgreSQL database "OD"
- Clean slate (no test data)
- Ready for real accounts

---
**Note:** All old `app/` directory files have been removed and consolidated into `main.py`