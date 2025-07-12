import os
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from database import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from auth.routes import auth_bp
    from diary.routes import diary_bp
    from incidents.routes import incidents_bp
    from alerts.routes import alerts_bp
    from admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(diary_bp, url_prefix='/diary')
    app.register_blueprint(incidents_bp, url_prefix='/incidents')
    app.register_blueprint(alerts_bp, url_prefix='/alerts')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Fix for proxy headers (if behind proxy)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    @app.route('/')
    def index():
        from models import DiaryEntry, Incident, User
        
        # Get recent content for homepage
        recent_diaries = DiaryEntry.query.order_by(DiaryEntry.timestamp.desc()).limit(3).all()
        recent_incidents = Incident.query.filter_by(approved=True).order_by(Incident.timestamp.desc()).limit(3).all()
        
        # Get stats for homepage
        stats = {
            'total_diaries': DiaryEntry.query.count(),
            'total_incidents': Incident.query.filter_by(approved=True).count(),
            'total_users': User.query.count()
        }
        
        return render_template('index.html', 
                             recent_diaries=recent_diaries,
                             recent_incidents=recent_incidents,
                             stats=stats)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    # Run without SSL for demo (can be enabled later with proper certificates)
    app.run(host='0.0.0.0', port=8000, debug=True)
