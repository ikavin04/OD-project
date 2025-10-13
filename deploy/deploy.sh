#!/bin/bash

# OD Management System - Main Deployment Script
# Deploys the complete application stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/od-management"
APP_USER="odapp"
DOMAIN="${1:-localhost}"
DB_NAME="od_management"
DB_USER="od_user"
DB_PASSWORD="OD_secure_2024!"

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if setup script was run
if [ ! -d "$APP_DIR" ]; then
    print_error "Server setup not completed. Please run ./setup_server.sh first"
    exit 1
fi

print_header "Starting OD Management System Deployment"

print_status "Stopping existing services..."
pm2 delete od-backend 2>/dev/null || true
pm2 delete od-frontend 2>/dev/null || true

print_status "Creating deployment directory structure..."
sudo -u $APP_USER mkdir -p $APP_DIR/{backend,frontend,logs,uploads}

print_status "Deploying backend..."
sudo -u $APP_USER cp -r backend/* $APP_DIR/backend/
cd $APP_DIR/backend

# Create virtual environment
print_status "Setting up Python virtual environment..."
sudo -u $APP_USER python3 -m venv venv
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install gunicorn psycopg2-binary"

# Create production environment file
print_status "Configuring backend environment..."
sudo -u $APP_USER cat > $APP_DIR/backend/.env << EOF
# Production Environment Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Database Configuration
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME

# Email Configuration (Update with your SMTP settings)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# File Upload Configuration
UPLOAD_FOLDER=$APP_DIR/uploads
MAX_CONTENT_LENGTH=16777216

# Security
CORS_ORIGINS=https://$DOMAIN,http://$DOMAIN

# Logging
LOG_LEVEL=INFO
LOG_FILE=$APP_DIR/logs/app.log
EOF

print_status "Setting up database tables..."
cd $APP_DIR/backend
sudo -u $APP_USER bash -c "source venv/bin/activate && python -c '
import sys
sys.path.append(\".\")
from main import app, db
with app.app_context():
    db.create_all()
    print(\"Database tables created successfully\")
'"

print_status "Deploying frontend..."
cd $APP_DIR
sudo -u $APP_USER cp -r frontend/* $APP_DIR/frontend/

# Update frontend API URL for production
sudo -u $APP_USER sed -i "s|http://localhost:5000|https://$DOMAIN|g" $APP_DIR/frontend/src/config/api.js 2>/dev/null || true
sudo -u $APP_USER find $APP_DIR/frontend/src -name "*.js" -o -name "*.jsx" -exec sed -i "s|http://localhost:5000|https://$DOMAIN|g" {} \; 2>/dev/null || true

cd $APP_DIR/frontend
sudo -u $APP_USER npm install
sudo -u $APP_USER npm run build

print_status "Configuring Nginx..."
cat > /etc/nginx/sites-available/od-management << EOF
# OD Management System Nginx Configuration

upstream backend {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;

    # Root directory for static files
    root $APP_DIR/frontend/dist;
    index index.html;

    # Handle API requests
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' 'https://$DOMAIN' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
        
        if (\$request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' 'https://$DOMAIN';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }

    # Handle file uploads
    location /uploads/ {
        alias $APP_DIR/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Handle static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files \$uri =404;
    }

    # Handle React routing
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Security
    location ~ /\. {
        deny all;
        return 404;
    }

    # Logs
    access_log /var/log/nginx/od-management.access.log;
    error_log /var/log/nginx/od-management.error.log;
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/od-management /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

print_status "Setting up process management with PM2..."
sudo -u $APP_USER cat > $APP_DIR/ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'od-backend',
      cwd: '$APP_DIR/backend',
      script: 'venv/bin/gunicorn',
      args: '--config gunicorn.conf.py main:app',
      env: {
        NODE_ENV: 'production'
      },
      error_file: '$APP_DIR/logs/backend-error.log',
      out_file: '$APP_DIR/logs/backend-out.log',
      log_file: '$APP_DIR/logs/backend.log',
      time: true
    }
  ]
};
EOF

# Create Gunicorn configuration
sudo -u $APP_USER cat > $APP_DIR/backend/gunicorn.conf.py << EOF
# Gunicorn configuration for OD Management System

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "$APP_DIR/logs/gunicorn-access.log"
errorlog = "$APP_DIR/logs/gunicorn-error.log"
loglevel = "info"
access_log_format = '%h %l %u %t "%r" %s %b "%{Referer}i" "%{User-agent}i"'

# Process naming
proc_name = 'od-management-backend'

# Server mechanics
daemon = False
pidfile = '$APP_DIR/backend/gunicorn.pid'
user = 'odapp'
group = 'www-data'
tmp_upload_dir = None

# SSL (uncomment when SSL is configured)
# keyfile = "/path/to/ssl/key.pem"
# certfile = "/path/to/ssl/cert.pem"
EOF

print_status "Starting services..."
cd $APP_DIR
sudo -u $APP_USER pm2 start ecosystem.config.js
sudo -u $APP_USER pm2 save

# Setup PM2 startup script
env PATH=\$PATH:/usr/bin pm2 startup systemd -u $APP_USER --hp /home/$APP_USER

print_status "Setting up log rotation..."
cat > /etc/logrotate.d/od-management << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0644 $APP_USER www-data
    postrotate
        sudo -u $APP_USER pm2 reload od-backend
    endscript
}
EOF

print_status "Setting up backup script..."
sudo -u $APP_USER cat > $APP_DIR/backup.sh << 'EOF'
#!/bin/bash
# Database backup script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/www/od-management/backups"
mkdir -p $BACKUP_DIR

# Database backup
pg_dump od_management > $BACKUP_DIR/database_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "database_*.sql" -mtime +7 -delete

echo "Backup completed: database_$DATE.sql"
EOF

chmod +x $APP_DIR/backup.sh

# Add to crontab for daily backups
(crontab -u $APP_USER -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh") | crontab -u $APP_USER -

print_status "Deployment completed successfully!"
print_header "Deployment Summary"

echo "✅ Backend deployed and running on port 5000"
echo "✅ Frontend built and served by Nginx"
echo "✅ Database configured and tables created"
echo "✅ PM2 process management configured"
echo "✅ Automatic backups configured (daily at 2 AM)"
echo "✅ Log rotation configured"
echo ""
echo "🌐 Application URL: http://$DOMAIN"
echo "📊 PM2 monitoring: sudo -u $APP_USER pm2 monit"
echo "📝 Logs: $APP_DIR/logs/"
echo ""
print_warning "Important: Update the following in $APP_DIR/backend/.env:"
echo "1. Email configuration (MAIL_USERNAME, MAIL_PASSWORD)"
echo "2. Review security settings"
echo ""
print_status "For SSL setup, run: ./setup_ssl.sh $DOMAIN"
echo ""
print_status "Deployment complete! Your OD Management System is now live! 🎉"