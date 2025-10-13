#!/bin/bash

# SSL Setup Script with Let's Encrypt
# Sets up HTTPS for the OD Management System

set -e

DOMAIN="$1"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

if [ -z "$DOMAIN" ]; then
    print_error "Usage: $0 <domain>"
    print_error "Example: $0 od.example.com"
    exit 1
fi

print_status "Setting up SSL for domain: $DOMAIN"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Installing Certbot..."
apt update
apt install -y certbot python3-certbot-nginx

print_status "Obtaining SSL certificate..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

print_status "Updating Nginx configuration for SSL..."
cat > /etc/nginx/sites-available/od-management << EOF
# OD Management System Nginx Configuration with SSL

upstream backend {
    server 127.0.0.1:5000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
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
    root /var/www/od-management/frontend/dist;
    index index.html;

    # Handle API requests
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        
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
        alias /var/www/od-management/uploads/;
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

print_status "Testing Nginx configuration..."
nginx -t

print_status "Reloading Nginx..."
systemctl reload nginx

print_status "Setting up automatic SSL renewal..."
# Create renewal script
cat > /etc/cron.d/certbot << EOF
# Automatic SSL renewal for OD Management System
0 2 * * * root certbot renew --quiet --nginx --post-hook "systemctl reload nginx"
EOF

print_status "Testing SSL certificate..."
if curl -f -s https://$DOMAIN >/dev/null; then
    print_status "SSL setup completed successfully!"
    echo ""
    echo "✅ HTTPS enabled for $DOMAIN"
    echo "✅ HTTP requests automatically redirect to HTTPS"
    echo "✅ SSL certificate will auto-renew"
    echo "✅ Security headers configured"
    echo ""
    echo "🌐 Your application is now available at: https://$DOMAIN"
    echo ""
    print_status "SSL Grade Test: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
else
    print_warning "SSL setup completed, but HTTPS test failed"
    print_warning "Please check your DNS configuration and try again"
fi