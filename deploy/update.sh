#!/bin/bash

# Update Script for OD Management System
# Safely updates the application with zero downtime

set -e

APP_DIR="/var/www/od-management"
APP_USER="odapp"
BACKUP_DIR="$APP_DIR/backups"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should NOT be run as root"
   exit 1
fi

print_status "Starting OD Management System update..."

# Create backup
DATE=$(date +%Y%m%d_%H%M%S)
print_status "Creating backup..."
mkdir -p $BACKUP_DIR

# Backup database
pg_dump od_management > $BACKUP_DIR/pre_update_$DATE.sql

# Backup current application
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz -C $APP_DIR backend frontend

print_status "Pulling latest changes..."
git pull origin main

print_status "Updating backend dependencies..."
cd $APP_DIR/backend
source venv/bin/activate
pip install -r requirements.txt

print_status "Running database migrations (if any)..."
python -c "
import sys
sys.path.append('.')
from main import app, db
with app.app_context():
    db.create_all()
    print('Database updated successfully')
"

print_status "Building frontend..."
cd $APP_DIR/frontend
npm install
npm run build

print_status "Restarting services..."
pm2 reload od-backend

print_status "Testing application..."
if curl -f -s http://localhost:5000/api/health >/dev/null; then
    print_status "Backend health check passed"
else
    print_error "Backend health check failed!"
    print_warning "Rolling back..."
    # Restore backup
    tar -xzf $BACKUP_DIR/app_backup_$DATE.tar.gz -C $APP_DIR
    pm2 reload od-backend
    print_error "Update failed and rolled back"
    exit 1
fi

print_status "Update completed successfully!"
print_status "Application is running normally"

# Clean old backups (keep last 5)
find $BACKUP_DIR -name "app_backup_*.tar.gz" -type f | sort -r | tail -n +6 | xargs rm -f
find $BACKUP_DIR -name "pre_update_*.sql" -type f | sort -r | tail -n +6 | xargs rm -f

print_status "Old backups cleaned up"
print_status "Update process completed! 🎉"