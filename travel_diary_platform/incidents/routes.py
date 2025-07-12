import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from database import db
from incidents import incidents_bp
from models import Incident

UPLOAD_FOLDER = 'travel_diary_platform/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@incidents_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report_incident():
    if request.method == 'POST':
        location = request.form['location']
        category = request.form['category']
        description = request.form['description']
        photo = request.files.get('photo')
        filename = None
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            # Ensure upload directory exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            photo.save(os.path.join(UPLOAD_FOLDER, filename))
        incident = Incident(user_id=current_user.id, location=location, category=category,
                            description=description, photo_filename=filename)
        db.session.add(incident)
        db.session.commit()
        flash('Incident reported successfully. Awaiting admin approval.')
        return redirect(url_for('incidents.report_incident'))
    return render_template('incidents/report.html')

@incidents_bp.route('/list')
@login_required
def list_incidents():
    incidents = Incident.query.order_by(Incident.timestamp.desc()).all()
    return render_template('incidents/list.html', incidents=incidents)
