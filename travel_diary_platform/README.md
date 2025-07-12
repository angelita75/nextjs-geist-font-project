# Travel Diary Platform

A comprehensive Flask-based web application for travelers to share their experiences, report safety incidents, and stay informed about travel risks through real-time alerts and interactive maps.

## 🌟 Features

### Core Functionality
- **User Authentication**: Secure signup, login, and profile management with Flask-Login
- **Travel Diary System**: Create, edit, and share travel stories with safety tips
- **Incident Reporting**: Report safety incidents with photo uploads and location details
- **Real-time Risk Mapping**: Interactive Google Maps integration showing verified incident locations
- **Alert System**: WhatsApp and email notifications for approved safety incidents
- **Admin Dashboard**: Moderation panel for incident approval and platform management

### Technical Features
- **Modern UI**: Bootstrap 5 responsive design with custom CSS
- **Background Processing**: Celery integration for alert dispatching
- **API Endpoints**: RESTful API for risk data consumption
- **SSL Support**: Self-signed certificates for development
- **Comprehensive Testing**: Unit tests for authentication and API endpoints
- **Docker Support**: Complete containerization with docker-compose

## 🏗️ Architecture

```
travel_diary_platform/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # SQLAlchemy database models
├── tasks.py              # Celery background tasks
├── setup.py              # Automated setup script
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker configuration
├── generate_certs.py     # SSL certificate generator
│
├── auth/                 # Authentication blueprint
├── diary/                # Travel diary blueprint
├── incidents/            # Incident reporting blueprint
├── alerts/               # Alerts and mapping blueprint
├── admin/                # Admin dashboard blueprint
│
├── templates/            # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── auth/
│   ├── diary/
│   ├── incidents/
│   ├── alerts/
│   ├── admin/
│   └── errors/
│
├── static/               # Static assets
│   ├── css/main.css
│   ├── js/main.js
│   └── uploads/          # User uploaded files
│
└── tests/                # Unit tests
    ├── test_auth.py
    └── test_api.py
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Redis (for Celery background tasks)
- Google Maps API key
- Twilio account (optional, for WhatsApp alerts)
- SMTP email server credentials

### Automated Setup
```bash
# Clone or download the project
cd travel_diary_platform

# Run the automated setup script
python setup.py

# Install dependencies
pip install -r requirements.txt

# Update .env file with your credentials
# Edit .env file with your API keys

# Run the application
python app.py
```

### Manual Setup

1. **Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Configuration**
Create a `.env` file with the following variables:
```env
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
DATABASE_URL=sqlite:///app.db

# Twilio (WhatsApp alerts)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_FROM=whatsapp:+1234567890

# Email (SMTP fallback)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password

# Google Maps
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

4. **Generate SSL Certificates**
```bash
python generate_certs.py
```

5. **Initialize Database**
```bash
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

6. **Create Admin User**
```bash
flask shell
>>> from models import User, Preference
>>> from werkzeug.security import generate_password_hash
>>> admin = User(username='admin', email='admin@example.com', password_hash=generate_password_hash('admin123'), is_admin=True)
>>> db.session.add(admin)
>>> pref = Preference(user_id=admin.id, alert_via_email=True, email='admin@example.com')
>>> db.session.add(pref)
>>> db.session.commit()
>>> exit()
```

## 🐳 Docker Deployment

### Development with Docker Compose
```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment
For production, update the docker-compose.yml:
- Use PostgreSQL instead of SQLite
- Set proper environment variables
- Use production WSGI server (gunicorn)
- Configure proper SSL certificates
- Set up reverse proxy (nginx)

## 🧪 Testing

### Run Unit Tests
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=. tests/
```

### Test Coverage
The test suite covers:
- User authentication (signup, login, logout)
- API endpoints (/api/risks, /health)
- Access control and permissions
- Error handling (404, 500)
- Database operations

## 📱 Usage Guide

### For Travelers
1. **Sign Up**: Create an account to access all features
2. **Write Diary**: Share your travel experiences and safety tips
3. **View Map**: Check the interactive safety map before traveling
4. **Report Incidents**: Help others by reporting safety concerns
5. **Set Alerts**: Configure WhatsApp or email notifications

### For Administrators
1. **Access Dashboard**: Login with admin credentials
2. **Review Reports**: Moderate incident reports for accuracy
3. **Approve/Reject**: Control what appears on the public map
4. **Monitor System**: Use health check endpoint for system status

## 🔧 API Documentation

### GET /alerts/api/risks
Returns approved incident data as JSON.

**Response Format:**
```json
[
  {
    "id": 1,
    "location": "Times Square, New York",
    "category": "theft",
    "description": "Pickpocketing incident near subway entrance",
    "timestamp": "2024-01-15T10:30:00"
  }
]
```

### GET /admin/health
System health check endpoint.

**Response Format:**
```json
{
  "status": "ok",
  "database": "connected",
  "stats": {
    "users": 150,
    "incidents": 45,
    "diaries": 230
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🔐 Security Features

- **Password Hashing**: Werkzeug secure password hashing
- **Session Management**: Flask-Login secure session handling
- **CSRF Protection**: Built-in CSRF token validation
- **File Upload Security**: Secure filename handling and type validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **SSL/TLS**: HTTPS support with self-signed certificates for development

## 🌍 Internationalization

The platform is designed to be easily internationalized:
- Template structure supports multiple languages
- Database models include location fields for global use
- Time zones handled with UTC timestamps
- Currency and date formatting can be localized

## 🔄 Background Tasks

Celery handles asynchronous tasks:
- **Alert Dispatching**: Send WhatsApp/email notifications
- **Data Cleanup**: Remove old alert records
- **Report Generation**: Weekly safety summaries
- **Image Processing**: Optimize uploaded photos

### Start Celery Worker
```bash
celery -A tasks worker --loglevel=info
```

### Start Celery Beat (Scheduler)
```bash
celery -A tasks beat --loglevel=info
```

## 📊 Monitoring and Logging

### Health Monitoring
- `/admin/health` endpoint for system status
- Database connection testing
- Basic statistics reporting

### Logging
- Application logs in `logs/` directory
- Error tracking for debugging
- Performance monitoring capabilities

## 🚀 Production Deployment

### Recommended Production Stack
- **Web Server**: Nginx (reverse proxy)
- **WSGI Server**: Gunicorn
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **SSL**: Let's Encrypt certificates
- **Monitoring**: Prometheus + Grafana

### Environment Variables for Production
```env
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/traveldiary
SECRET_KEY=your-very-secure-secret-key
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Security Checklist for Production
- [ ] Change default admin password
- [ ] Use strong SECRET_KEY
- [ ] Configure proper SSL certificates
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Enable logging and monitoring
- [ ] Set up regular security updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write unit tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**SSL Certificate Errors**
```bash
# Regenerate certificates
python generate_certs.py
```

**Database Issues**
```bash
# Reset database
flask shell
>>> from app import db
>>> db.drop_all()
>>> db.create_all()
```

**Celery Connection Issues**
```bash
# Check Redis connection
redis-cli ping
```

### Getting Help
- Check the GitHub Issues page
- Review the test files for usage examples
- Consult the Flask and SQLAlchemy documentation

## 🎯 Roadmap

### Planned Features
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with travel booking APIs
- [ ] Machine learning for risk prediction
- [ ] Offline mode capabilities
- [ ] Social features (friend connections)
- [ ] Travel itinerary planning

### Performance Improvements
- [ ] Database query optimization
- [ ] Caching layer implementation
- [ ] CDN integration for static assets
- [ ] Image compression and optimization

---

**Built with ❤️ for the travel community**

Stay safe, travel smart, and share your adventures!
