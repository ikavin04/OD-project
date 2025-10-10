# 🚀 OD Management System - Complete Deployment Package

This package contains everything you need to deploy your OD Management System to a production server **without Docker**.

## 📦 What's Included

### Deployment Scripts
- `setup_server.sh` - Initial server setup and dependencies installation
- `deploy.sh` - Main application deployment script
- `quick-deploy.sh` - One-command deployment for quick setup
- `setup_ssl.sh` - SSL/HTTPS configuration with Let's Encrypt
- `update.sh` - Safe application updates with rollback capability
- `monitor.sh` - System health monitoring script

### Configuration Files
- `nginx.conf` - Production Nginx configuration
- `od-management.service` - Systemd service file (alternative to PM2)
- `.env.production` - Production environment template
- `requirements-production.txt` - Python dependencies for production
- `ecosystem.config.js` - PM2 process configuration

### Documentation
- `DEPLOYMENT_CHECKLIST.md` - Complete deployment checklist
- `README.md` - This file with deployment instructions

## 🚀 Quick Start (Recommended)

For a fast deployment on a fresh Ubuntu server:

```bash
# 1. Setup server (run as root)
sudo ./deploy/setup_server.sh

# 2. Deploy application (run as regular user)
./deploy/quick-deploy.sh your-domain.com

# That's it! Your application is now running.
```

## 📋 Detailed Deployment Steps

### Prerequisites
- Ubuntu 20.04+ / CentOS 8+ server
- Domain name pointed to your server
- Root access to the server

### Step 1: Server Preparation
```bash
# Upload your project to the server
scp -r OD-project/ user@your-server:/home/user/

# SSH into your server
ssh user@your-server
cd OD-project

# Make scripts executable
chmod +x deploy/*.sh
```

### Step 2: Server Setup
```bash
# Run server setup (installs all dependencies)
sudo ./deploy/setup_server.sh
```

This script will:
- ✅ Install Python, Node.js, PostgreSQL, Nginx
- ✅ Configure firewall and security
- ✅ Create database and application user
- ✅ Set up directory structure

### Step 3: Deploy Application
```bash
# Deploy your application
./deploy/deploy.sh your-domain.com
```

This script will:
- ✅ Deploy backend with virtual environment
- ✅ Build and deploy frontend
- ✅ Configure Nginx
- ✅ Start services with PM2
- ✅ Set up logging and monitoring

### Step 4: Configure SSL (Optional but Recommended)
```bash
# Set up HTTPS with Let's Encrypt
sudo ./deploy/setup_ssl.sh your-domain.com
```

### Step 5: Configure Application
Edit the environment file:
```bash
sudo nano /var/www/od-management/backend/.env
```

Update these important settings:
- Email configuration (MAIL_USERNAME, MAIL_PASSWORD)
- Domain settings (CORS_ORIGINS)
- Security keys (auto-generated but verify)

### Step 6: Test Deployment
```bash
# Check application health
curl https://your-domain.com/api/health

# Check PM2 status
pm2 status

# View logs
pm2 logs od-backend
```

## 🔧 Management Commands

### Application Management
```bash
# Check status
pm2 status

# View logs
pm2 logs od-backend

# Restart application
pm2 restart od-backend

# Monitor resources
pm2 monit
```

### System Management
```bash
# Check Nginx status
sudo systemctl status nginx

# Check database
sudo systemctl status postgresql

# View application logs
tail -f /var/www/od-management/logs/app.log
```

### Updates
```bash
# Update application safely
./deploy/update.sh
```

## 📊 Monitoring

The deployment includes automatic monitoring:
- Health checks every 5 minutes
- Automatic email alerts for issues
- Log rotation to prevent disk full
- Daily database backups

View monitoring logs:
```bash
tail -f /var/www/od-management/logs/monitor.log
```

## 🔒 Security Features

Your deployment includes:
- ✅ HTTPS with automatic SSL renewal
- ✅ Firewall configuration (UFW)
- ✅ Fail2ban for intrusion prevention
- ✅ Security headers in Nginx
- ✅ Rate limiting on API endpoints
- ✅ Secure file upload restrictions

## 🗂️ File Structure

After deployment, your application will be located at:
```
/var/www/od-management/
├── backend/           # Flask application
├── frontend/         # React application (built)
├── uploads/          # User uploaded files
├── logs/            # Application logs
├── backups/         # Database backups
└── deploy/          # Deployment scripts
```

## 🆘 Troubleshooting

### Common Issues

1. **Application won't start**
   ```bash
   pm2 logs od-backend
   # Check the error logs for specific issues
   ```

2. **Database connection failed**
   ```bash
   sudo -u postgres psql -d od_management -c "SELECT 1;"
   # Test database connectivity
   ```

3. **Nginx configuration error**
   ```bash
   sudo nginx -t
   # Test Nginx configuration
   ```

4. **SSL certificate issues**
   ```bash
   sudo certbot certificates
   # Check certificate status
   ```

### Getting Help

If you encounter issues:
1. Check the logs in `/var/www/od-management/logs/`
2. Review the `DEPLOYMENT_CHECKLIST.md`
3. Use the monitoring script: `./deploy/monitor.sh`

## 🔄 Backup and Recovery

### Automatic Backups
- Database: Daily at 2 AM
- Application: Before each update
- Logs: Rotated weekly

### Manual Backup
```bash
# Create backup
/var/www/od-management/backup.sh

# List backups
ls -la /var/www/od-management/backups/
```

### Recovery
```bash
# Restore database
psql od_management < /var/www/od-management/backups/database_YYYYMMDD_HHMMSS.sql

# Restore application
tar -xzf /var/www/od-management/backups/app_backup_YYYYMMDD_HHMMSS.tar.gz -C /var/www/od-management/
pm2 restart od-backend
```

## 📈 Performance Optimization

Your deployment is optimized for production:
- ✅ Gzip compression enabled
- ✅ Static file caching
- ✅ Database connection pooling
- ✅ Process management with PM2
- ✅ Rate limiting for API protection

## 🎯 Demo Credentials

Your application comes with pre-configured demo accounts:
- **Student**: `24ucs153kavin@kgkite.ac.in` / `Kgkite@1234`
- **Faculty**: `dr.rajesh@kgkite.ac.in` / `Faculty@123`

## 📞 Support

For deployment support, provide:
- Server OS and version
- Error messages from logs
- Output of `pm2 status` command
- Nginx error logs if applicable

---

**🎉 Congratulations! Your OD Management System is ready for production use!**

Visit your application at: `https://your-domain.com`