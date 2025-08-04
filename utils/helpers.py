import re
import json
import requests
from urllib.parse import urlparse
from user_agents import parse

def get_client_ip(request):
    """Get real client IP address"""
    # Check for X-Forwarded-For header (proxy/load balancer)
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    
    # Check for X-Real-IP header (nginx)
    if 'X-Real-IP' in request.headers:
        return request.headers['X-Real-IP']
    
    # Check for CF-Connecting-IP (Cloudflare)
    if 'CF-Connecting-IP' in request.headers:
        return request.headers['CF-Connecting-IP']
    
    # Fallback to remote_addr
    return request.remote_addr

def get_geolocation(ip_address):
    """Get geolocation data for IP address"""
    if not ip_address or ip_address in ['127.0.0.1', 'localhost']:
        return {
            'country': 'Local',
            'city': 'Local',
            'latitude': 0,
            'longitude': 0
        }
    
    try:
        # Using ip-api.com (free service)
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {
                    'country': data.get('country', ''),
                    'city': data.get('city', ''),
                    'latitude': data.get('lat', 0),
                    'longitude': data.get('lon', 0),
                    'region': data.get('regionName', ''),
                    'timezone': data.get('timezone', '')
                }
    except Exception as e:
        print(f"[GEO] Error getting location for {ip_address}: {e}")
    
    return {
        'country': 'Unknown',
        'city': 'Unknown',
        'latitude': 0,
        'longitude': 0
    }

def parse_user_agent(user_agent_string):
    """Parse user agent string to extract browser and OS info"""
    try:
        user_agent = parse(user_agent_string)
        return {
            'browser': f"{user_agent.browser.family} {user_agent.browser.version_string}",
            'os': f"{user_agent.os.family} {user_agent.os.version_string}",
            'device': user_agent.device.family,
            'is_mobile': user_agent.is_mobile,
            'is_tablet': user_agent.is_tablet,
            'is_bot': user_agent.is_bot
        }
    except:
        return {
            'browser': 'Unknown',
            'os': 'Unknown',
            'device': 'Unknown',
            'is_mobile': False,
            'is_tablet': False,
            'is_bot': False
        }

def validate_url(url):
    """Validate if URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    return filename

def extract_domain(url):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return ''

def generate_phish_url(base_url, campaign_id, use_path=True):
    """Generate phishing URL for campaign"""
    if use_path:
        return f"{base_url}/phish/campaign_{campaign_id}"
    else:
        # For different port deployment
        port = 5000 + campaign_id
        return f"{base_url.replace(':5000', f':{port}')}"

def mask_sensitive_data(data, fields=['password', 'token', 'secret']):
    """Mask sensitive fields in data for logging"""
    if isinstance(data, dict):
        masked = data.copy()
        for field in fields:
            if field in masked:
                masked[field] = '*' * len(str(masked[field]))
        return masked
    return data

def format_timestamp(timestamp):
    """Format timestamp for display"""
    return timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')

def calculate_campaign_success_rate(total_visits, captured_credentials):
    """Calculate campaign success rate"""
    if total_visits == 0:
        return 0
    return (captured_credentials / total_visits) * 100

def generate_campaign_id():
    """Generate unique campaign identifier"""
    import uuid
    return str(uuid.uuid4())[:8]

def is_suspicious_ip(ip_address):
    """Check if IP address is suspicious (basic implementation)"""
    suspicious_ranges = [
        '10.',      # Private network
        '192.168.', # Private network
        '172.',     # Private network
        '127.',     # Localhost
    ]
    
    for range_prefix in suspicious_ranges:
        if ip_address.startswith(range_prefix):
            return True
    
    return False

def extract_form_fields(html_content):
    """Extract form fields from HTML content"""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_content, 'html.parser')
    fields = []
    
    forms = soup.find_all('form')
    for form in forms:
        inputs = form.find_all(['input', 'select', 'textarea'])
        for input_field in inputs:
            field_info = {
                'name': input_field.get('name', ''),
                'type': input_field.get('type', 'text'),
                'placeholder': input_field.get('placeholder', ''),
                'required': input_field.has_attr('required')
            }
            fields.append(field_info)
    
    return fields

def detect_2fa_forms(html_content):
    """Detect if HTML contains 2FA forms"""
    keywords = [
        'two-factor', 'two factor', '2fa', 'verification code',
        'authenticator', 'sms code', 'verification', 'confirm'
    ]
    
    html_lower = html_content.lower()
    return any(keyword in html_lower for keyword in keywords)

def generate_qr_code(data):
    """Generate QR code for data (placeholder)"""
    # In production, use qrcode library
    return f"QR_CODE_DATA: {data}"

def compress_data(data):
    """Compress data for storage"""
    import gzip
    import json
    
    if isinstance(data, dict):
        data = json.dumps(data)
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return gzip.compress(data)

def decompress_data(compressed_data):
    """Decompress data"""
    import gzip
    import json
    
    decompressed = gzip.decompress(compressed_data)
    
    try:
        # Try to parse as JSON
        return json.loads(decompressed.decode('utf-8'))
    except:
        # Return as string
        return decompressed.decode('utf-8')
