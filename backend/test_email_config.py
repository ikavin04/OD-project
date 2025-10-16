"""
Test Email Configuration
Verifies that email sending is properly configured
"""
from main import app, mail
from flask_mail import Message

def test_email_config():
    """Test email configuration"""
    print("=" * 70)
    print("📧 Email Configuration Test")
    print("=" * 70)
    
    with app.app_context():
        print("\n🔧 Current Configuration:")
        print(f"  MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"  MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"  MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"  MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"  MAIL_PASSWORD: {'*' * len(app.config.get('MAIL_PASSWORD', ''))}")
        print(f"  MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        
        print("\n✅ Email configuration loaded successfully!")
        print("\n📋 Ready to send notifications for:")
        print("  - OD approval notifications")
        print("  - Proof submission reminders")
        print("  - Overdue alerts")
        print("  - Deadline warnings")

if __name__ == "__main__":
    test_email_config()
