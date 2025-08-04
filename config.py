import os
from datetime import timedelta

class Config:
    """Application configuration"""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'phishx-secret-key-change-in-production')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///phishx.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
    # Phishing configuration
    DEFAULT_PHISH_PORT = 5000
    MAX_CONCURRENT_CAMPAIGNS = 50
    SESSION_TIMEOUT_HOURS = 24
    
    # Proxy configuration
    PROXY_TIMEOUT = 30
    MAX_PROXY_REDIRECTS = 5
    
    # Notification configuration
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
    DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
    
    # Security configuration
    BCRYPT_LOG_ROUNDS = 12
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Analytics configuration
    ANALYTICS_RETENTION_DAYS = 365
    ENABLE_GEOLOCATION = True
    GEOLOCATION_API_KEY = os.environ.get('GEOLOCATION_API_KEY')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/phishx.log')
    
    # API configuration
    API_RATE_LIMIT = '100 per hour'
    API_KEY = os.environ.get('API_KEY')
    
    # Encryption configuration
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'default-encryption-key')
    
    # Template configuration
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    CUSTOM_TEMPLATE_FOLDER = os.path.join(TEMPLATE_FOLDER, 'phishing')
    
    # Email configuration (for notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Advanced features configuration
    ENABLE_2FA_BYPASS = True
    ENABLE_REVERSE_PROXY = True
    ENABLE_SESSION_HIJACKING = True
    ENABLE_REAL_TIME_NOTIFICATIONS = True
    
    # AI and ML configuration
    ENABLE_AI_EVASION = os.environ.get('ENABLE_AI_EVASION', 'false').lower() == 'true'
    AI_MODEL_PATH = os.environ.get('AI_MODEL_PATH', 'models/')
    
    # Post-quantum cryptography
    ENABLE_QUANTUM_RESISTANT = os.environ.get('ENABLE_QUANTUM_RESISTANT', 'false').lower() == 'true'
    
    # Docker configuration
    DOCKER_ENABLED = os.environ.get('DOCKER_ENABLED', 'false').lower() == 'true'
    CONTAINER_NAME = os.environ.get('CONTAINER_NAME', 'phishx')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
