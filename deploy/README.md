# OD Management System - Production Deployment Guide

This guide will help you deploy the OD Management System to a production server without Docker.

## 🏗️ Deployment Architecture

```
Production Server
├── Frontend (React) - Served by Nginx
├── Backend (Flask) - Served by Gunicorn + Nginx
└── Database (PostgreSQL)
```

## 📋 Prerequisites

### Server Requirements
- Ubuntu 20.04+ / CentOS 8+ / Similar Linux distribution
- Minimum 2GB RAM, 2 CPU cores
- 20GB disk space
- Root or sudo access

### Required Software
- Python 3.9+
- Node.js 18+
- PostgreSQL 13+
- Nginx
- PM2 (for process management)

## 🚀 Quick Deployment

1. **Prepare your server:**
   ```bash
   chmod +x deploy/setup_server.sh
   sudo ./deploy/setup_server.sh
   ```

2. **Deploy the application:**
   ```bash
   chmod +x deploy/deploy.sh
   ./deploy/deploy.sh
   ```

3. **Configure SSL (recommended):**
   ```bash
   sudo ./deploy/setup_ssl.sh your-domain.com
   ```

## 📁 Deployment Files

- `setup_server.sh` - Initial server setup and dependencies
- `deploy.sh` - Main deployment script
- `nginx.conf` - Nginx configuration
- `gunicorn.conf.py` - Gunicorn WSGI server configuration
- `ecosystem.config.js` - PM2 process configuration
- `setup_ssl.sh` - SSL/TLS setup with Let's Encrypt

## 🔧 Manual Deployment Steps

If you prefer manual deployment, follow these steps:

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib nginx

# Install PM2
sudo npm install -g pm2
```

### 2. Database Setup
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE od_management;
CREATE USER od_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE od_management TO od_user;
\q
```

### 3. Backend Deployment
```bash
# Create application directory
sudo mkdir -p /var/www/od-management
sudo chown $USER:$USER /var/www/od-management

# Copy backend files
cp -r backend/* /var/www/od-management/backend/
cd /var/www/od-management/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Update environment variables
cp .env.example .env
# Edit .env with production values
```

### 4. Frontend Deployment
```bash
# Copy frontend files
cp -r frontend/* /var/www/od-management/frontend/
cd /var/www/od-management/frontend

# Install dependencies and build
npm install
npm run build

# Copy build to nginx directory
sudo cp -r dist/* /var/www/html/
```

### 5. Nginx Configuration
```bash
# Copy nginx configuration
sudo cp deploy/nginx.conf /etc/nginx/sites-available/od-management
sudo ln -s /etc/nginx/sites-available/od-management /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart nginx
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Start Services
```bash
# Start backend with PM2
cd /var/www/od-management
pm2 start deploy/ecosystem.config.js

# Save PM2 configuration
pm2 save
pm2 startup
```

## 🔒 Security Considerations

1. **Environment Variables**: Never commit `.env` files with production secrets
2. **Firewall**: Configure UFW to allow only necessary ports (80, 443, 22)
3. **SSL/TLS**: Always use HTTPS in production
4. **Database**: Use strong passwords and restrict access
5. **Updates**: Keep all software updated regularly

## 📊 Monitoring

- **Application Logs**: `pm2 logs`
- **Nginx Logs**: `/var/log/nginx/`
- **System Resources**: `pm2 monit`

## 🔄 Updates

To update the application:
```bash
./deploy/update.sh
```

## 🆘 Troubleshooting

### Common Issues

1. **Permission Denied**: Check file permissions and ownership
2. **Database Connection**: Verify PostgreSQL is running and credentials are correct
3. **Port Conflicts**: Ensure ports 80, 443, 5000 are available
4. **Nginx Errors**: Check `/var/log/nginx/error.log`

### Support

For deployment issues, check:
- Application logs: `pm2 logs od-backend`
- System logs: `journalctl -u nginx`
- Database logs: `sudo tail -f /var/log/postgresql/postgresql-13-main.log`

## 📞 Contact

If you need help with deployment, please provide:
- Server OS and version
- Error messages
- Relevant log files