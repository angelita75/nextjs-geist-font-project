import os
from celery import Celery
from flask import current_app
from app import create_app, db
from config import Config
from models import User, Incident, Alert, Preference
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize Celery
celery = Celery('travel_diary_platform')
celery.conf.update(
    broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

def make_celery(app):
    """Create Celery instance with Flask app context"""
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

@celery.task
def send_incident_alert(incident_id):
    """Send alerts to users when an incident is approved"""
    try:
        app = create_app()
        with app.app_context():
            incident = Incident.query.get(incident_id)
            if not incident or not incident.approved:
                return {'status': 'error', 'message': 'Incident not found or not approved'}
            
            # Get all users who want alerts
            users_with_alerts = User.query.join(Preference).filter(
                (Preference.alert_via_whatsapp == True) | 
                (Preference.alert_via_email == True)
            ).all()
            
            alert_message = f"""
🚨 TRAVEL SAFETY ALERT 🚨

Location: {incident.location}
Category: {incident.category.title()}
Description: {incident.description[:200]}{'...' if len(incident.description) > 200 else ''}

Stay safe and be aware of your surroundings.

- Travel Diary Platform
            """.strip()
            
            sent_count = 0
            failed_count = 0
            
            for user in users_with_alerts:
                try:
                    pref = user.preferences
                    
                    # Send WhatsApp alert if enabled
                    if pref.alert_via_whatsapp and pref.whatsapp_number:
                        success = send_whatsapp_alert(pref.whatsapp_number, alert_message)
                        if success:
                            sent_count += 1
                        else:
                            failed_count += 1
                    
                    # Send email alert if enabled (or as fallback)
                    elif pref.alert_via_email and pref.email:
                        success = send_email_alert(pref.email, 
                                                 f"Safety Alert: {incident.location}", 
                                                 alert_message)
                        if success:
                            sent_count += 1
                        else:
                            failed_count += 1
                    
                    # Log the alert
                    alert_record = Alert(
                        user_id=user.id,
                        message=alert_message
                    )
                    db.session.add(alert_record)
                    
                except Exception as e:
                    print(f"Error sending alert to user {user.id}: {str(e)}")
                    failed_count += 1
            
            db.session.commit()
            
            return {
                'status': 'success',
                'sent': sent_count,
                'failed': failed_count,
                'incident_id': incident_id
            }
            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def send_whatsapp_alert(phone_number, message):
    """Send WhatsApp alert using Twilio"""
    try:
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        whatsapp_from = os.environ.get('TWILIO_WHATSAPP_FROM')
        
        if not all([account_sid, auth_token, whatsapp_from]):
            print("Twilio credentials not configured")
            return False
        
        client = Client(account_sid, auth_token)
        
        # Ensure phone number has country code
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        message = client.messages.create(
            body=message,
            from_=whatsapp_from,
            to=f'whatsapp:{phone_number}'
        )
        
        print(f"WhatsApp alert sent: {message.sid}")
        return True
        
    except Exception as e:
        print(f"Error sending WhatsApp alert: {str(e)}")
        return False

def send_email_alert(email, subject, message):
    """Send email alert using SMTP"""
    try:
        smtp_server = os.environ.get('MAIL_SERVER')
        smtp_port = int(os.environ.get('MAIL_PORT', 587))
        smtp_username = os.environ.get('MAIL_USERNAME')
        smtp_password = os.environ.get('MAIL_PASSWORD')
        use_tls = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
        
        if not all([smtp_server, smtp_username, smtp_password]):
            print("SMTP credentials not configured")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(message, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        if use_tls:
            server.starttls()
        server.login(smtp_username, smtp_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(smtp_username, email, text)
        server.quit()
        
        print(f"Email alert sent to: {email}")
        return True
        
    except Exception as e:
        print(f"Error sending email alert: {str(e)}")
        return False

@celery.task
def cleanup_old_alerts():
    """Clean up old alert records (run daily)"""
    try:
        app = create_app()
        with app.app_context():
            from datetime import datetime, timedelta
            
            # Delete alerts older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            old_alerts = Alert.query.filter(Alert.sent_at < cutoff_date).all()
            
            count = len(old_alerts)
            for alert in old_alerts:
                db.session.delete(alert)
            
            db.session.commit()
            
            return {'status': 'success', 'deleted': count}
            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@celery.task
def generate_safety_report():
    """Generate weekly safety report (run weekly)"""
    try:
        app = create_app()
        with app.app_context():
            from datetime import datetime, timedelta
            
            # Get incidents from the past week
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_incidents = Incident.query.filter(
                Incident.timestamp >= week_ago,
                Incident.approved == True
            ).all()
            
            # Group by category
            categories = {}
            for incident in recent_incidents:
                if incident.category not in categories:
                    categories[incident.category] = []
                categories[incident.category].append(incident)
            
            # Generate report
            report = f"""
WEEKLY SAFETY REPORT
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

Total Incidents This Week: {len(recent_incidents)}

BREAKDOWN BY CATEGORY:
"""
            
            for category, incidents in categories.items():
                report += f"\n{category.upper()}: {len(incidents)} incidents\n"
                for incident in incidents[:3]:  # Show top 3 per category
                    report += f"  - {incident.location}: {incident.description[:100]}...\n"
            
            report += f"\n\nFor more details, visit the Travel Diary Platform safety map."
            
            # Here you could send this report to admins or save it
            print("Weekly safety report generated:")
            print(report)
            
            return {'status': 'success', 'incidents_count': len(recent_incidents)}
            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# Periodic task configuration
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'cleanup-old-alerts': {
        'task': 'tasks.cleanup_old_alerts',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'generate-safety-report': {
        'task': 'tasks.generate_safety_report',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Monday at 9 AM
    },
}

if __name__ == '__main__':
    # For testing tasks directly
    app = create_app()
    celery = make_celery(app)
    celery.start()
