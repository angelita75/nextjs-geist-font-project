from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from database import db
from admin import admin_bp
from models import Incident, User, DiaryEntry
from datetime import datetime

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    pending_incidents = Incident.query.filter_by(approved=False).order_by(Incident.timestamp.desc()).all()
    
    # Get additional stats for dashboard
    today = datetime.utcnow().date()
    approved_count = Incident.query.filter_by(approved=True).filter(
        db.func.date(Incident.timestamp) == today
    ).count()
    total_users = User.query.count()
    total_diaries = DiaryEntry.query.count()
    
    return render_template('admin/dashboard.html', 
                         incidents=pending_incidents,
                         approved_count=approved_count,
                         total_users=total_users,
                         total_diaries=total_diaries)

@admin_bp.route('/approve_incident/<int:incident_id>', methods=['POST'])
@login_required
@admin_required
def approve_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    incident.approved = True
    db.session.commit()
    
    # Trigger alert task
    try:
        from tasks import send_incident_alert
        send_incident_alert.delay(incident_id)
        flash('Incident approved and alerts are being sent.')
    except Exception as e:
        flash(f'Incident approved, but alert sending failed: {str(e)}')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reject_incident/<int:incident_id>', methods=['POST'])
@login_required
@admin_required
def reject_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    db.session.delete(incident)
    db.session.commit()
    flash('Incident rejected and deleted.')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/health')
def health_check():
    # Enhanced health check endpoint
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        
        # Check basic stats
        user_count = User.query.count()
        incident_count = Incident.query.count()
        diary_count = DiaryEntry.query.count()
        
        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'stats': {
                'users': user_count,
                'incidents': incident_count,
                'diaries': diary_count
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
