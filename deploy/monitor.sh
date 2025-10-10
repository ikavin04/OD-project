#!/bin/bash

# OD Management System Monitoring Script
# Checks system health and sends alerts if needed

set -e

APP_DIR="/var/www/od-management"
LOG_FILE="$APP_DIR/logs/monitor.log"
ALERT_EMAIL="admin@yourdomain.com"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

check_service() {
    local service_name=$1
    if systemctl is-active --quiet $service_name; then
        log "✅ $service_name is running"
        return 0
    else
        log "❌ $service_name is not running"
        return 1
    fi
}

check_url() {
    local url=$1
    local expected_status=${2:-200}
    
    response=$(curl -s -o /dev/null -w "%{http_code}" $url)
    if [ "$response" = "$expected_status" ]; then
        log "✅ $url responded with $response"
        return 0
    else
        log "❌ $url responded with $response (expected $expected_status)"
        return 1
    fi
}

check_disk_space() {
    local threshold=${1:-80}
    usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ $usage -lt $threshold ]; then
        log "✅ Disk usage: ${usage}%"
        return 0
    else
        log "⚠️  Disk usage: ${usage}% (threshold: ${threshold}%)"
        return 1
    fi
}

check_memory() {
    local threshold=${1:-80}
    usage=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')
    
    if [ $usage -lt $threshold ]; then
        log "✅ Memory usage: ${usage}%"
        return 0
    else
        log "⚠️  Memory usage: ${usage}% (threshold: ${threshold}%)"
        return 1
    fi
}

check_database() {
    if sudo -u postgres psql -d od_management -c "SELECT 1;" >/dev/null 2>&1; then
        log "✅ Database connection successful"
        return 0
    else
        log "❌ Database connection failed"
        return 1
    fi
}

send_alert() {
    local subject=$1
    local message=$2
    
    if command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "$subject" $ALERT_EMAIL
        log "📧 Alert sent to $ALERT_EMAIL"
    else
        log "⚠️  Mail command not available, cannot send alert"
    fi
}

# Main monitoring logic
log "🔍 Starting system health check..."

ISSUES=0

# Check system services
if ! check_service "nginx"; then
    ((ISSUES++))
fi

if ! check_service "postgresql"; then
    ((ISSUES++))
fi

# Check application
if ! sudo -u odapp pm2 describe od-backend >/dev/null 2>&1; then
    log "❌ OD Backend process not running"
    ((ISSUES++))
else
    log "✅ OD Backend process is running"
fi

# Check URLs
if ! check_url "http://localhost:80"; then
    ((ISSUES++))
fi

if ! check_url "http://localhost:5000/api/health"; then
    ((ISSUES++))
fi

# Check system resources
if ! check_disk_space 80; then
    ((ISSUES++))
fi

if ! check_memory 80; then
    ((ISSUES++))
fi

# Check database
if ! check_database; then
    ((ISSUES++))
fi

# Check log file sizes
if [ -f "$APP_DIR/logs/backend.log" ]; then
    log_size=$(du -m "$APP_DIR/logs/backend.log" | cut -f1)
    if [ $log_size -gt 100 ]; then
        log "⚠️  Backend log file is large (${log_size}MB)"
    fi
fi

# Summary
if [ $ISSUES -eq 0 ]; then
    log "🎉 All checks passed - system is healthy"
    exit 0
else
    log "⚠️  Found $ISSUES issues"
    send_alert "OD Management System Alert" "System health check found $ISSUES issues. Check $LOG_FILE for details."
    exit 1
fi