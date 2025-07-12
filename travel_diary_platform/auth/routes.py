from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from auth import auth_bp
from models import User, Preference

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('diary.view_diaries'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('auth.signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('auth.signup'))
        user = User(username=username, email=email,
                    password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        # Create default preferences
        pref = Preference(user_id=user.id, alert_via_email=True)
        db.session.add(pref)
        db.session.commit()
        flash('Account created successfully. Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('auth/signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('diary.view_diaries'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('diary.view_diaries'))
        flash('Invalid username or password.')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    pref = current_user.preferences
    if request.method == 'POST':
        alert_via_whatsapp = 'alert_via_whatsapp' in request.form
        alert_via_email = 'alert_via_email' in request.form
        whatsapp_number = request.form.get('whatsapp_number')
        email = request.form.get('email')
        pref.alert_via_whatsapp = alert_via_whatsapp
        pref.alert_via_email = alert_via_email
        pref.whatsapp_number = whatsapp_number
        pref.email = email
        db.session.commit()
        flash('Preferences updated.')
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile.html', pref=pref)
