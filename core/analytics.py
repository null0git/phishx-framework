import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from sqlalchemy import func
from app import db
from models import CapturedCredential, SessionLog, Campaign

class Analytics:
    """Analytics and reporting for phishing campaigns"""
    
    def __init__(self):
        pass
    
    def get_capture_statistics(self):
        """Get overall capture statistics"""
        total_credentials = CapturedCredential.query.count()
        total_sessions = SessionLog.query.count()
        unique_ips = db.session.query(func.count(func.distinct(CapturedCredential.ip_address))).scalar()
        
        # Get recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_credentials = CapturedCredential.query.filter(
            CapturedCredential.captured_at >= yesterday
        ).count()
        
        return {
            'total_credentials': total_credentials,
            'total_sessions': total_sessions,
            'unique_ips': unique_ips,
            'recent_captures': recent_credentials
        }
    
    def get_capture_timeline(self, days=30):
        """Get capture timeline data"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        credentials = CapturedCredential.query.filter(
            CapturedCredential.captured_at >= start_date
        ).all()
        
        # Group by day
        timeline = defaultdict(int)
        for cred in credentials:
            day = cred.captured_at.strftime('%Y-%m-%d')
            timeline[day] += 1
        
        # Fill missing days with 0
        current_date = start_date
        while current_date <= datetime.utcnow():
            day = current_date.strftime('%Y-%m-%d')
            if day not in timeline:
                timeline[day] = 0
            current_date += timedelta(days=1)
        
        # Convert to sorted list
        sorted_timeline = []
        for day in sorted(timeline.keys()):
            sorted_timeline.append({
                'date': day,
                'captures': timeline[day]
            })
        
        return sorted_timeline
    
    def get_location_statistics(self):
        """Get location-based statistics"""
        credentials = CapturedCredential.query.filter(
            CapturedCredential.country.isnot(None)
        ).all()
        
        country_stats = Counter([cred.country for cred in credentials if cred.country])
        city_stats = Counter([f"{cred.city}, {cred.country}" for cred in credentials if cred.city and cred.country])
        
        return {
            'countries': dict(country_stats.most_common(10)),
            'cities': dict(city_stats.most_common(10))
        }
    
    def get_browser_statistics(self):
        """Get browser and OS statistics"""
        credentials = CapturedCredential.query.filter(
            CapturedCredential.user_agent.isnot(None)
        ).all()
        
        browsers = []
        operating_systems = []
        
        for cred in credentials:
            if cred.user_agent:
                browser_info = self.parse_user_agent(cred.user_agent)
                browsers.append(browser_info['browser'])
                operating_systems.append(browser_info['os'])
        
        browser_stats = Counter(browsers)
        os_stats = Counter(operating_systems)
        
        return {
            'browsers': dict(browser_stats.most_common(10)),
            'operating_systems': dict(os_stats.most_common(10))
        }
    
    def get_campaign_performance(self):
        """Get campaign performance metrics"""
        campaigns = Campaign.query.all()
        
        performance = []
        for campaign in campaigns:
            credentials_count = CapturedCredential.query.filter_by(campaign_id=campaign.id).count()
            sessions_count = SessionLog.query.filter_by(campaign_id=campaign.id).count()
            unique_ips = db.session.query(func.count(func.distinct(SessionLog.ip_address))).filter_by(campaign_id=campaign.id).scalar()
            
            # Calculate conversion rate
            conversion_rate = (credentials_count / sessions_count * 100) if sessions_count > 0 else 0
            
            performance.append({
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'total_visits': sessions_count,
                'credentials_captured': credentials_count,
                'unique_visitors': unique_ips,
                'conversion_rate': round(conversion_rate, 2),
                'is_active': campaign.is_active
            })
        
        return sorted(performance, key=lambda x: x['credentials_captured'], reverse=True)
    
    def get_hourly_activity(self):
        """Get hourly activity distribution"""
        credentials = CapturedCredential.query.all()
        
        hourly_stats = defaultdict(int)
        for cred in credentials:
            hour = cred.captured_at.hour
            hourly_stats[hour] += 1
        
        # Convert to list with all 24 hours
        activity = []
        for hour in range(24):
            activity.append({
                'hour': hour,
                'captures': hourly_stats[hour]
            })
        
        return activity
    
    def parse_user_agent(self, user_agent):
        """Parse user agent string to extract browser and OS info"""
        user_agent = user_agent.lower()
        
        # Browser detection
        if 'chrome' in user_agent:
            browser = 'Chrome'
        elif 'firefox' in user_agent:
            browser = 'Firefox'
        elif 'safari' in user_agent and 'chrome' not in user_agent:
            browser = 'Safari'
        elif 'edge' in user_agent:
            browser = 'Edge'
        elif 'opera' in user_agent:
            browser = 'Opera'
        else:
            browser = 'Other'
        
        # OS detection
        if 'windows' in user_agent:
            os = 'Windows'
        elif 'macintosh' in user_agent or 'mac os' in user_agent:
            os = 'macOS'
        elif 'linux' in user_agent:
            os = 'Linux'
        elif 'android' in user_agent:
            os = 'Android'
        elif 'iphone' in user_agent or 'ipad' in user_agent:
            os = 'iOS'
        else:
            os = 'Other'
        
        return {
            'browser': browser,
            'os': os
        }
    
    def generate_report(self, campaign_id=None):
        """Generate comprehensive analytics report"""
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'overview': self.get_capture_statistics(),
            'timeline': self.get_capture_timeline(),
            'locations': self.get_location_statistics(),
            'browsers': self.get_browser_statistics(),
            'campaigns': self.get_campaign_performance(),
            'hourly_activity': self.get_hourly_activity()
        }
        
        if campaign_id:
            # Add campaign-specific data
            campaign = Campaign.query.get(campaign_id)
            if campaign:
                campaign_credentials = CapturedCredential.query.filter_by(campaign_id=campaign_id).all()
                campaign_sessions = SessionLog.query.filter_by(campaign_id=campaign_id).all()
                
                report['campaign_specific'] = {
                    'campaign_id': campaign_id,
                    'campaign_name': campaign.name,
                    'total_credentials': len(campaign_credentials),
                    'total_sessions': len(campaign_sessions),
                    'credentials_by_day': self.get_campaign_timeline(campaign_id),
                    'top_countries': self.get_campaign_locations(campaign_id)
                }
        
        return report
    
    def get_campaign_timeline(self, campaign_id, days=30):
        """Get timeline for specific campaign"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        credentials = CapturedCredential.query.filter(
            CapturedCredential.campaign_id == campaign_id,
            CapturedCredential.captured_at >= start_date
        ).all()
        
        timeline = defaultdict(int)
        for cred in credentials:
            day = cred.captured_at.strftime('%Y-%m-%d')
            timeline[day] += 1
        
        return dict(timeline)
    
    def get_campaign_locations(self, campaign_id):
        """Get location stats for specific campaign"""
        credentials = CapturedCredential.query.filter(
            CapturedCredential.campaign_id == campaign_id,
            CapturedCredential.country.isnot(None)
        ).all()
        
        country_stats = Counter([cred.country for cred in credentials if cred.country])
        return dict(country_stats.most_common(5))
