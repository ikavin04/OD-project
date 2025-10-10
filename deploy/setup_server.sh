#!/bin/bash

# OD Management System - Server Setup Script
# This script sets up a Ubuntu/Debian server for deployment

set -e

echo "🚀 Setting up server for OD Management System deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Updating system packages..."
apt update && apt upgrade -y

print_status "Installing system dependencies..."
apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    fail2ban

print_status "Installing Python 3.9+..."
apt install -y python3 python3-pip python3-venv python3-dev

print_status "Installing Node.js 18+..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

print_status "Installing PostgreSQL..."
apt install -y postgresql postgresql-contrib postgresql-client libpq-dev

print_status "Installing Nginx..."
apt install -y nginx

print_status "Installing PM2 globally..."
npm install -g pm2

print_status "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

print_status "Starting and enabling services..."
systemctl start postgresql
systemctl enable postgresql
systemctl start nginx
systemctl enable nginx

print_status "Creating application user..."
if ! id "odapp" &>/dev/null; then
    useradd -m -s /bin/bash odapp
    usermod -aG www-data odapp
fi

print_status "Creating application directory..."
mkdir -p /var/www/od-management
chown odapp:www-data /var/www/od-management
chmod 755 /var/www/od-management

print_status "Setting up PostgreSQL database..."
sudo -u postgres psql << EOF
-- Create database if not exists
SELECT 'CREATE DATABASE od_management' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'od_management')\gexec

-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'od_user') THEN
        CREATE USER od_user WITH PASSWORD 'OD_secure_2024!';
    END IF;
END
\$\$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE od_management TO od_user;
ALTER USER od_user CREATEDB;
EOF

print_status "Configuring PostgreSQL for application access..."
PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '\d+\.\d+' | head -1)
PG_CONFIG_DIR="/etc/postgresql/$PG_VERSION/main"

# Update pg_hba.conf to allow local connections
if ! grep -q "local   od_management   od_user" "$PG_CONFIG_DIR/pg_hba.conf"; then
    echo "local   od_management   od_user                         md5" >> "$PG_CONFIG_DIR/pg_hba.conf"
fi

# Update postgresql.conf
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" "$PG_CONFIG_DIR/postgresql.conf"

# Restart PostgreSQL
systemctl restart postgresql

print_status "Setting up log directories..."
mkdir -p /var/log/od-management
chown odapp:www-data /var/log/od-management

print_status "Installing Python packages globally needed for deployment..."
pip3 install --upgrade pip setuptools wheel

print_status "Configuring Nginx..."
# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

print_status "Setting up fail2ban for security..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s
EOF

systemctl enable fail2ban
systemctl start fail2ban

print_status "Setting up automatic security updates..."
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

print_status "Server setup completed successfully!"
print_warning "Important notes:"
echo "1. Database created: od_management"
echo "2. Database user: od_user (password: OD_secure_2024!)"
echo "3. Application directory: /var/www/od-management"
echo "4. Application user: odapp"
echo "5. Firewall enabled (SSH and HTTP/HTTPS allowed)"
echo ""
print_status "Next steps:"
echo "1. Run the deployment script: ./deploy.sh"
echo "2. Configure your domain DNS to point to this server"
echo "3. Set up SSL with: ./setup_ssl.sh your-domain.com"
echo ""
print_status "System is ready for deployment! 🎉"