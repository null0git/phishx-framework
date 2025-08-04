# PhishX Framework

## Overview

PhishX Framework is an advanced Python-based phishing simulation platform designed for cybersecurity professionals to conduct authorized security testing and penetration testing. The application provides comprehensive phishing campaign management with features including multi-campaign support, real-time analytics, credential capture, session hijacking simulation, and 2FA bypass testing. Built with Flask and SQLAlchemy, it offers both a web interface for campaign management and API endpoints for external integrations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework Architecture
- **Flask Application**: Main web framework with blueprint-based modular architecture
- **Blueprint Organization**: Separated into admin (management interface), phish (victim-facing pages), and api (RESTful endpoints) modules
- **Template System**: Jinja2 templating with built-in phishing page templates for popular platforms (Facebook, Google, Instagram, Microsoft)
- **Static Asset Management**: CSS and JavaScript organized for dashboard analytics and general application functionality

### Database Layer
- **SQLAlchemy ORM**: Database abstraction layer with declarative base model
- **Multi-database Support**: Configurable to use SQLite (default), PostgreSQL, MySQL, or MongoDB
- **Core Models**: User authentication, Campaign management, PhishingTemplate storage, CapturedCredential logging, and SessionLog tracking
- **Database Configuration**: Connection pooling with 300-second recycle time and pre-ping enabled for reliability

### Authentication & Security
- **Flask-Login**: Session-based user authentication with secure password hashing
- **BCRYPT Encryption**: 12-round password hashing for user credentials
- **Session Management**: Custom session tracking with UUID-based session IDs and 24-hour timeout
- **CSRF Protection**: WTF-CSRF enabled for form security
- **Encryption Utilities**: PBKDF2-based key derivation for sensitive data encryption using Fernet symmetric encryption

### Core Engine Components
- **Reverse Proxy Engine**: Evilginx-style proxy system for real-time session hijacking and 2FA bypass simulation
- **Session Manager**: Tracks user sessions with activity logging and timeout management
- **Template Manager**: Handles upload, extraction, and management of phishing page templates with ZIP file support
- **Analytics Engine**: Real-time data processing for campaign statistics, capture timelines, and geolocation analysis

### Data Processing & Analytics
- **Real-time Dashboard**: Chart.js-powered analytics with capture statistics and timeline visualization
- **GeoIP Integration**: IP-based location tracking using ip-api.com service
- **User Agent Parsing**: Device and browser fingerprinting for enhanced analytics
- **Export Functionality**: CSV and JSON export capabilities for captured data

### Notification System
- **Multi-platform Alerts**: Integrated support for Telegram, Slack, and Discord webhook notifications
- **Real-time Notifications**: Instant alerts for credential captures, 2FA tokens, and campaign status changes
- **Configurable Thresholds**: Customizable notification triggers and message formatting

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework with SQLAlchemy integration
- **Flask-Login**: User session management and authentication
- **SQLAlchemy**: Database ORM with multi-database support
- **Werkzeug**: WSGI utilities and security helpers including ProxyFix middleware

### Security & Cryptography
- **cryptography**: Fernet symmetric encryption and PBKDF2 key derivation
- **bcrypt**: Password hashing for user authentication

### HTTP & Networking
- **requests**: HTTP client library for proxy functionality and external API calls
- **user-agents**: User agent string parsing for analytics

### Data Processing & Parsing
- **BeautifulSoup4**: HTML parsing and manipulation for template injection
- **zipfile**: Template archive handling and extraction

### Frontend & Visualization
- **Bootstrap 5**: UI framework with dark theme support
- **Chart.js**: JavaScript charting library for analytics dashboard
- **Font Awesome**: Icon library for user interface elements
- **DataTables**: Enhanced table functionality with sorting and filtering
- **Leaflet**: Interactive maps for geolocation visualization

### External Services
- **ip-api.com**: Geolocation service for IP address tracking (free tier)
- **Telegram Bot API**: Real-time notifications via Telegram
- **Slack Webhooks**: Team notifications through Slack integration
- **Discord Webhooks**: Community notifications via Discord

### Development & Deployment
- **Docker**: Containerization support with docker-compose configuration
- **ProxyFix**: WSGI middleware for handling reverse proxy headers
- **Environment Configuration**: 12-factor app pattern with environment variable configuration