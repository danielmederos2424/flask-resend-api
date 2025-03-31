import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY')

    # Security Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)

    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

    # Environment
    ENV = os.environ.get('FLASK_ENV', 'production')

    # Security headers
    CONTENT_SECURITY_POLICY = "default-src 'self'"
    X_CONTENT_TYPE_OPTIONS = "nosniff"
    X_FRAME_OPTIONS = "SAMEORIGIN"
    X_XSS_PROTECTION = "1; mode=block"
