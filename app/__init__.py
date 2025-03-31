from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import logging
from datetime import datetime


def create_app():
    # Create the Flask app
    app = Flask(__name__)

    # Configure app from environment variables
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['RESEND_API_KEY'] = os.environ.get('RESEND_API_KEY')
    app.config['SENDER_EMAIL'] = os.environ.get('SENDER_EMAIL')

    # Security configurations
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # CORS configuration
    CORS(app, resources={r"/*": {"origins": os.environ.get('CORS_ORIGINS', '*')}})

    # Fix for running behind proxy server
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Setup logging
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    # Log application start
    app.logger.info(f"Application started with environment: {os.environ.get('FLASK_ENV', 'production')}")

    return app
