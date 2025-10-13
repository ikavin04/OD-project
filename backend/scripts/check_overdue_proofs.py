#!/usr/bin/env python3
"""
Scheduled task script for checking overdue proof submissions
Run this script via cron or task scheduler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.utils.notification_service import notification_service
import logging
from datetime import datetime

def setup_logging():
    """Setup logging for the scheduled task"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'notification_scheduler.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_notification_checks():
    """Run all notification checks"""
    app = create_app()
    
    with app.app_context():
        logging.info("=" * 50)
        logging.info(f"Starting notification check at {datetime.now()}")
        
        try:
            # Send deadline reminders (1 day before)
            logging.info("Checking for deadline reminders...")
            reminder_count = notification_service.send_deadline_reminders()
            logging.info(f"Sent {reminder_count} deadline reminders")
            
            # Send overdue notifications
            logging.info("Checking for overdue submissions...")
            overdue_count = notification_service.check_and_send_overdue_notifications()
            logging.info(f"Sent {overdue_count} overdue notifications")
            
            # Get summary of students with pending proofs
            logging.info("Getting summary of pending proofs...")
            pending_students = notification_service.get_students_with_pending_proofs()
            logging.info(f"Found {len(pending_students)} students with pending proof submissions")
            
            if pending_students:
                logging.info("Students with pending proofs:")
                for student in pending_students:
                    logging.info(f"  - {student['name']} ({student['roll_number']}) - {student['pending_count']} pending")
            
            logging.info(f"Notification check completed successfully at {datetime.now()}")
            logging.info("=" * 50)
            
        except Exception as e:
            logging.error(f"Error during notification check: {str(e)}")
            logging.info("=" * 50)

if __name__ == "__main__":
    setup_logging()
    run_notification_checks()