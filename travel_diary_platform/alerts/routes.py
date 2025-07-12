from flask import jsonify, request, render_template, current_app
from flask_login import login_required
from database import db
from alerts import alerts_bp
from models import Incident

@alerts_bp.route('/api/risks')
def api_risks():
    approved_incidents = Incident.query.filter_by(approved=True).all()
    risks = []
    for incident in approved_incidents:
        risks.append({
            'id': incident.id,
            'location': incident.location,
            'category': incident.category,
            'description': incident.description,
            'timestamp': incident.timestamp.isoformat()
        })
    return jsonify(risks)

@alerts_bp.route('/alerts')
@login_required
def alerts_page():
    # Placeholder for alerts management page
    return render_template('alerts/alerts.html')

@alerts_bp.route('/map')
def map_page():
    # Safety risk map page - accessible to all users
    return render_template('alerts/alerts.html')
