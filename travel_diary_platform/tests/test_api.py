import pytest
import json
from app import create_app, db
from models import User, Incident, DiaryEntry
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('adminpass'),
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def regular_user(app):
    """Create a regular user for testing."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass')
        )
        db.session.add(user)
        db.session.commit()
        return user

def test_risks_api_empty(client):
    """Test risks API with no incidents."""
    response = client.get('/alerts/api/risks')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_risks_api_with_approved_incidents(client, app, regular_user):
    """Test risks API with approved incidents."""
    with app.app_context():
        # Create approved incident
        incident = Incident(
            user_id=regular_user.id,
            location='Test Location',
            category='theft',
            description='Test incident description',
            approved=True
        )
        db.session.add(incident)
        db.session.commit()
        incident_id = incident.id
    
    response = client.get('/alerts/api/risks')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 1
    
    risk = data[0]
    assert risk['id'] == incident_id
    assert risk['location'] == 'Test Location'
    assert risk['category'] == 'theft'
    assert risk['description'] == 'Test incident description'
    assert 'timestamp' in risk

def test_risks_api_excludes_unapproved_incidents(client, app, regular_user):
    """Test that risks API excludes unapproved incidents."""
    with app.app_context():
        # Create unapproved incident
        incident = Incident(
            user_id=regular_user.id,
            location='Test Location',
            category='theft',
            description='Test incident description',
            approved=False
        )
        db.session.add(incident)
        db.session.commit()
    
    response = client.get('/alerts/api/risks')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_health_check_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/admin/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'status' in data
    assert 'database' in data
    assert 'stats' in data
    assert 'timestamp' in data

def test_index_page_loads(client):
    """Test that index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Travel Diary Platform' in response.data

def test_diary_list_page(client):
    """Test diary list page."""
    response = client.get('/diary/all')
    assert response.status_code == 200
    assert b'Travel Diaries' in response.data

def test_incidents_list_page(client):
    """Test incidents list page."""
    response = client.get('/incidents/list')
    assert response.status_code == 200
    assert b'Safety Incident Reports' in response.data

def test_map_page(client):
    """Test safety map page."""
    response = client.get('/alerts/map')
    assert response.status_code == 200
    assert b'Safety Risk Map' in response.data

def test_admin_dashboard_requires_admin(client, regular_user):
    """Test that admin dashboard requires admin privileges."""
    # Login as regular user
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    response = client.get('/admin/dashboard')
    assert response.status_code == 302  # Redirect due to lack of admin privileges

def test_create_diary_requires_login(client):
    """Test that creating diary requires login."""
    response = client.get('/diary/create')
    assert response.status_code == 302  # Redirect to login

def test_report_incident_requires_login(client):
    """Test that reporting incident requires login."""
    response = client.get('/incidents/report')
    assert response.status_code == 302  # Redirect to login

def test_404_error_page(client):
    """Test 404 error page."""
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    assert b'Page Not Found' in response.data

def test_risks_api_json_format(client, app, regular_user):
    """Test that risks API returns proper JSON format."""
    with app.app_context():
        incident = Incident(
            user_id=regular_user.id,
            location='Paris, France',
            category='scam',
            description='Tourist scam near Eiffel Tower',
            approved=True
        )
        db.session.add(incident)
        db.session.commit()
    
    response = client.get('/alerts/api/risks')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    
    if len(data) > 0:
        risk = data[0]
        required_fields = ['id', 'location', 'category', 'description', 'timestamp']
        for field in required_fields:
            assert field in risk
