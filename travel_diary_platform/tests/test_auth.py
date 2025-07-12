import pytest
from app import create_app, db
from models import User, Preference
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
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

def test_signup_page(client):
    """Test that signup page loads correctly."""
    response = client.get('/auth/signup')
    assert response.status_code == 200
    assert b'Create Account' in response.data

def test_login_page(client):
    """Test that login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Welcome Back' in response.data

def test_user_signup(client, app):
    """Test user registration."""
    response = client.post('/auth/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123'
    })
    
    # Should redirect after successful signup
    assert response.status_code == 302
    
    # Check user was created
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'
        
        # Check default preferences were created
        pref = Preference.query.filter_by(user_id=user.id).first()
        assert pref is not None
        assert pref.alert_via_email == True

def test_user_login(client, app):
    """Test user login."""
    # Create a test user
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpassword123')
        )
        db.session.add(user)
        db.session.commit()
    
    # Test login
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword123'
    })
    
    # Should redirect after successful login
    assert response.status_code == 302

def test_invalid_login(client):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    
    # Should stay on login page
    assert response.status_code == 302
    # Follow redirect to see the flash message
    response = client.post('/auth/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b'Invalid username or password' in response.data

def test_duplicate_username(client, app):
    """Test signup with duplicate username."""
    # Create a test user
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpassword123')
        )
        db.session.add(user)
        db.session.commit()
    
    # Try to create another user with same username
    response = client.post('/auth/signup', data={
        'username': 'testuser',
        'email': 'different@example.com',
        'password': 'testpassword123'
    }, follow_redirects=True)
    
    assert b'Username already exists' in response.data

def test_duplicate_email(client, app):
    """Test signup with duplicate email."""
    # Create a test user
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpassword123')
        )
        db.session.add(user)
        db.session.commit()
    
    # Try to create another user with same email
    response = client.post('/auth/signup', data={
        'username': 'differentuser',
        'email': 'test@example.com',
        'password': 'testpassword123'
    }, follow_redirects=True)
    
    assert b'Email already registered' in response.data

def test_profile_access_requires_login(client):
    """Test that profile page requires login."""
    response = client.get('/auth/profile')
    assert response.status_code == 302  # Redirect to login

def test_logout(client, app):
    """Test user logout."""
    # Create and login a test user
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpassword123')
        )
        db.session.add(user)
        db.session.commit()
    
    # Login
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword123'
    })
    
    # Logout
    response = client.get('/auth/logout')
    assert response.status_code == 302  # Redirect after logout
    
    # Should not be able to access profile after logout
    response = client.get('/auth/profile')
    assert response.status_code == 302  # Redirect to login
