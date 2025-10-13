# 🚀 OD Management System Deployment Checklist

## Pre-Deployment Requirements

### Server Requirements
- [ ] Ubuntu 20.04+ / CentOS 8+ / Similar Linux distribution
- [ ] Minimum 2GB RAM, 2 CPU cores
- [ ] 20GB available disk space
- [ ] Root or sudo access
- [ ] Domain name pointed to server IP (for SSL)

### Local Preparation
- [ ] All code committed and pushed to repository
- [ ] Environment variables configured
- [ ] Database migrations tested locally
- [ ] Frontend builds without errors
- [ ] All tests passing

## Deployment Steps

### 1. Server Setup
```bash
# Make scripts executable
chmod +x deploy/*.sh

# Run server setup (as root)
sudo ./deploy/setup_server.sh
```

**Checklist:**
- [ ] All dependencies installed
- [ ] PostgreSQL running and configured
- [ ] Nginx installed and running
- [ ] PM2 installed globally
- [ ] Application user created
- [ ] Firewall configured
- [ ] Database and user created

### 2. Application Deployment
```bash
# Deploy application
./deploy/deploy.sh yourdomain.com
```

**Checklist:**
- [ ] Backend files copied and configured
- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] Database tables created
- [ ] Frontend built and copied
- [ ] Nginx configured
- [ ] PM2 processes started
- [ ] Services running correctly

### 3. SSL Setup (Recommended)
```bash
# Setup SSL with Let's Encrypt
sudo ./deploy/setup_ssl.sh yourdomain.com
```

**Checklist:**
- [ ] SSL certificate obtained
- [ ] HTTPS redirect configured
- [ ] Security headers added
- [ ] Auto-renewal configured

### 4. Configuration

#### Update Environment Variables
Edit `/var/www/od-management/backend/.env`:
- [ ] Update email configuration (MAIL_USERNAME, MAIL_PASSWORD)
- [ ] Verify database connection string
- [ ] Set production SECRET_KEY and JWT_SECRET_KEY
- [ ] Update CORS_ORIGINS with your domain

#### Test Configuration
- [ ] Backend health check: `curl https://yourdomain.com/api/health`
- [ ] Frontend loads: `https://yourdomain.com`
- [ ] Login functionality works
- [ ] Email notifications work
- [ ] File uploads work

## Post-Deployment

### Security Hardening
- [ ] Change default database password
- [ ] Configure fail2ban
- [ ] Set up regular security updates
- [ ] Review firewall rules
- [ ] Enable SSH key authentication
- [ ] Disable password authentication

### Monitoring Setup
- [ ] Set up monitoring cron job: `crontab -e`
  ```
  */5 * * * * /var/www/od-management/deploy/monitor.sh
  ```
- [ ] Configure log rotation
- [ ] Set up backup schedule
- [ ] Configure alerts (email/Slack)

### Performance Optimization
- [ ] Enable Gzip compression (included in nginx config)
- [ ] Configure caching headers
- [ ] Optimize database indexes
- [ ] Set up CDN for static files (optional)

## Testing Checklist

### Functionality Tests
- [ ] Student registration works
- [ ] Faculty registration works
- [ ] Login/logout functionality
- [ ] OD request submission
- [ ] OD request approval
- [ ] Email notifications sent
- [ ] File upload/download
- [ ] Password reset functionality

### Performance Tests
- [ ] Page load times < 3 seconds
- [ ] API response times < 1 second
- [ ] Database queries optimized
- [ ] Memory usage stable

### Security Tests
- [ ] HTTPS enforced
- [ ] SQL injection protection
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Rate limiting active
- [ ] File upload restrictions

## Maintenance

### Daily Tasks
- [ ] Check application logs: `pm2 logs`
- [ ] Monitor system resources: `pm2 monit`
- [ ] Verify backups completed

### Weekly Tasks
- [ ] Review error logs
- [ ] Check disk space usage
- [ ] Update system packages: `sudo apt update && sudo apt upgrade`
- [ ] Review security logs

### Monthly Tasks
- [ ] Review SSL certificate expiration
- [ ] Database maintenance and optimization
- [ ] Review backup retention
- [ ] Security audit

## Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check PM2 status
pm2 status

# Check logs
pm2 logs od-backend

# Restart application
pm2 restart od-backend
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
sudo -u postgres psql -d od_management -c "SELECT 1;"

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

#### Nginx Issues
```bash
# Check nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

#### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew --dry-run

# Check SSL configuration
openssl s_client -connect yourdomain.com:443
```

## Emergency Procedures

### Application Rollback
```bash
# Use the update script with rollback
./deploy/update.sh --rollback
```

### Database Restore
```bash
# Restore from backup
pg_dump od_management > /tmp/current_backup.sql
psql od_management < /var/www/od-management/backups/database_YYYYMMDD_HHMMSS.sql
```

### Complete System Recovery
```bash
# Restore application from backup
cd /var/www/od-management
tar -xzf backups/app_backup_YYYYMMDD_HHMMSS.tar.gz
pm2 restart od-backend
```

## Support Contacts

- **System Administrator**: your-admin@domain.com
- **Developer**: your-dev@domain.com
- **Emergency**: your-emergency-contact

## Documentation Links

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PM2 Documentation](https://pm2.keymetrics.io/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

**Deployment Date**: ___________
**Deployed By**: ___________
**Version**: ___________
**Domain**: ___________