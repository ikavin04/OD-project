#!/bin/bash

# Quick Deployment Script for OD Management System
# Run this after server setup to get your application running quickly

set -e

DOMAIN="${1:-your-domain.com}"
EMAIL="${2:-admin@$DOMAIN}"

echo "🚀 OD Management System Quick Deployment"
echo "========================================"
echo "Domain: $DOMAIN"
echo "Admin Email: $EMAIL"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Check if running as regular user
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should NOT be run as root"
   echo "Please run: ./deploy/quick-deploy.sh your-domain.com"
   exit 1
fi

# Step 1: Deploy application
print_step "Deploying OD Management System..."
if [ -f "./deploy/deploy.sh" ]; then
    chmod +x ./deploy/deploy.sh
    ./deploy/deploy.sh $DOMAIN
    print_success "Application deployed"
else
    echo "❌ Deploy script not found. Make sure you're in the project root directory."
    exit 1
fi

# Step 2: Update environment variables
print_step "Updating environment configuration..."
APP_DIR="/var/www/od-management"
if [ -f "$APP_DIR/backend/.env" ]; then
    # Generate secure keys
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_KEY=$(openssl rand -hex 32)
    
    # Update .env file
    sudo -u odapp sed -i "s/your-secret-key-here-use-openssl-rand-hex-32/$SECRET_KEY/" $APP_DIR/backend/.env
    sudo -u odapp sed -i "s/your-jwt-secret-key-here-use-openssl-rand-hex-32/$JWT_KEY/" $APP_DIR/backend/.env
    sudo -u odapp sed -i "s/https:\/\/yourdomain.com/https:\/\/$DOMAIN/" $APP_DIR/backend/.env
    
    print_success "Environment variables updated"
else
    echo "⚠️  Environment file not found, please configure manually"
fi

# Step 3: Test deployment
print_step "Testing deployment..."
sleep 5

if curl -f -s http://localhost:5000/api/health >/dev/null; then
    print_success "Backend is running"
else
    echo "❌ Backend health check failed"
fi

if curl -f -s http://localhost >/dev/null; then
    print_success "Frontend is accessible"
else
    echo "❌ Frontend not accessible"
fi

# Step 4: Set up SSL (if domain is not localhost)
if [ "$DOMAIN" != "localhost" ] && [ "$DOMAIN" != "your-domain.com" ]; then
    print_step "Setting up SSL certificate..."
    if [ -f "./deploy/setup_ssl.sh" ]; then
        chmod +x ./deploy/setup_ssl.sh
        sudo ./deploy/setup_ssl.sh $DOMAIN
        print_success "SSL configured"
    else
        echo "⚠️  SSL setup script not found"
    fi
fi

# Step 5: Set up monitoring
print_step "Setting up monitoring..."
if [ -f "./deploy/monitor.sh" ]; then
    chmod +x ./deploy/monitor.sh
    # Add to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/deploy/monitor.sh") | crontab -
    print_success "Monitoring configured"
fi

echo ""
echo "🎉 Deployment Complete!"
echo "======================="
echo ""
echo "Your OD Management System is now running:"
echo ""
if [ "$DOMAIN" != "localhost" ] && [ "$DOMAIN" != "your-domain.com" ]; then
    echo "🌐 Application URL: https://$DOMAIN"
    echo "🔒 SSL Certificate: Configured"
else
    echo "🌐 Application URL: http://$DOMAIN"
    echo "🔒 SSL Certificate: Not configured (localhost)"
fi
echo ""
echo "📊 Management Commands:"
echo "  - Check status: pm2 status"
echo "  - View logs: pm2 logs od-backend"
echo "  - Restart app: pm2 restart od-backend"
echo "  - Monitor: pm2 monit"
echo ""
echo "📋 Next Steps:"
echo "  1. Update email configuration in $APP_DIR/backend/.env"
echo "  2. Test login functionality at your domain"
echo "  3. Configure DNS if needed"
echo "  4. Review security settings"
echo ""
echo "📞 Demo Credentials:"
echo "  Student: 24ucs153kavin@kgkite.ac.in / Kgkite@1234"
echo "  Faculty: dr.rajesh@kgkite.ac.in / Faculty@123"
echo ""
print_success "Your OD Management System is ready for use! 🚀"