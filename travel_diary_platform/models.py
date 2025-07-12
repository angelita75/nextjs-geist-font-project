from datetime import datetime
from flask_login import UserMixin
from database import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    preferences = db.relationship('Preference', backref='user', uselist=False)
    diaries = db.relationship('DiaryEntry', backref='author', lazy='dynamic')
    incidents = db.relationship('Incident', backref='reporter', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Preference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    alert_via_whatsapp = db.Column(db.Boolean, default=False)
    alert_via_email = db.Column(db.Boolean, default=True)
    whatsapp_number = db.Column(db.String(20))
    email = db.Column(db.String(120))

class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(140), nullable=False)
    body = db.Column(db.Text, nullable=False)
    safety_tips = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='diary', lazy='dynamic')
    likes = db.relationship('Like', backref='diary', lazy='dynamic')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diary_id = db.Column(db.Integer, db.ForeignKey('diary_entry.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user = db.relationship('User', backref='comments')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diary_id = db.Column(db.Integer, db.ForeignKey('diary_entry.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    location = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo_filename = db.Column(db.String(255))
    approved = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
