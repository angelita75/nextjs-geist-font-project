#!/usr/bin/env python3
"""
Setup script for Travel Diary Platform
"""
import os
import sys
import subprocess
from app import create_app, db
from models import User, Preference
from werkzeug.security import generate_password_hash

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_database():
    """Initialize the database."""
    print("🔄 Setting up database...")
    app = create_app()
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@traveldiary.com',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True
                )
                db.session.add(admin)
                
                # Create admin preferences
                admin_pref = Preference(
                    user_id=admin.id,
                    alert_via_email=True,
                    email='admin@traveldiary.com'
                )
                db.session.add(admin_pref)
                
                db.session.commit()
                print("✅ Admin user created (username: admin, password: admin123)")
            else:
                print("✅ Admin user already exists")
                
            print("✅ Database setup completed successfully")
            return True
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False

def generate_ssl_certificates():
    """Generate SSL certificates for development."""
    print("🔄 Generating SSL certificates...")
    try:
        if not os.path.exists('certs'):
            os.makedirs('certs')
        
        # Check if certificates already exist
        if os.path.exists('certs/cert.pem') and os.path.exists('certs/key.pem'):
            print("✅ SSL certificates already exist")
            return True
        
        # Try to run the certificate generation script
        import generate_certs
        generate_certs.generate_self_signed_cert()
        return True
    except Exception as e:
        print(f"❌ SSL certificate generation failed: {e}")
        print("You can run the app without SSL by modifying app.py")
        return False

def create_directories():
    """Create necessary directories."""
    print("🔄 Creating directories...")
    directories = [
        'static/uploads',
        'certs',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directories created successfully")
    return True

def setup_environment():
    """Create .env file template."""
    print("🔄 Setting up environment file...")
    env_template = """# Travel Diary Platform Environment Variables

# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
DATABASE_URL=sqlite:///app.db

# Twilio Configuration (for WhatsApp alerts)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_FROM=whatsapp:+1234567890

# Email Configuration (SMTP fallback)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password

# Google Maps API
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Celery Configuration (for background tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_template)
        print("✅ .env file created - please update with your actual credentials")
    else:
        print("✅ .env file already exists")
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up Travel Diary Platform...")
    print("=" * 50)
    
    success = True
    
    # Create directories
    success &= create_directories()
    
    # Setup environment
    success &= setup_environment()
    
    # Generate SSL certificates
    success &= generate_ssl_certificates()
    
    # Setup database
    success &= setup_database()
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update the .env file with your actual API keys and credentials")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the application: python app.py")
        print("4. Visit https://localhost:5000 in your browser")
        print("\nDefault admin credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nFor production deployment, please:")
        print("- Change the admin password")
        print("- Use a proper database (PostgreSQL/MySQL)")
        print("- Set up proper SSL certificates")
        print("- Configure a production WSGI server (gunicorn)")
    else:
        print("❌ Setup completed with some errors")
        print("Please check the error messages above and resolve them manually")
        sys.exit(1)

if __name__ == "__main__":
    main()
