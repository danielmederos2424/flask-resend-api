import time
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify
import resend
import os
from app.utils import validate_email
from functools import wraps

# Create blueprint
main_bp = Blueprint('main', __name__)


# Rate limiting implementation
class IPRateLimiter:
    def __init__(self):
        self.ip_limits = {}
        self.lock = threading.Lock()
        self.cleanup_interval = 3600  # Cleanup old entries every hour
        self.last_cleanup = time.time()

    def is_rate_limited(self, ip, max_requests=30, window=60):
        """
        Check if an IP is rate limited

        Args:
            ip (str): The IP address
            max_requests (int): Maximum number of requests in the time window
            window (int): Time window in seconds

        Returns:
            bool: True if rate limited, False otherwise
        """
        current_time = time.time()

        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup()

        with self.lock:
            # Initialize if new IP
            if ip not in self.ip_limits:
                self.ip_limits[ip] = []

            # Remove requests outside the window
            self.ip_limits[ip] = [t for t in self.ip_limits[ip] if current_time - t < window]

            # Check if rate limited
            if len(self.ip_limits[ip]) >= max_requests:
                return True

            # Add current request timestamp
            self.ip_limits[ip].append(current_time)
            return False

    def _cleanup(self):
        """Remove old entries to prevent memory growth"""
        current_time = time.time()
        with self.lock:
            for ip in list(self.ip_limits.keys()):
                # Remove IPs with no recent requests (older than 1 day)
                if all(current_time - t > 86400 for t in self.ip_limits[ip]):
                    del self.ip_limits[ip]

            self.last_cleanup = current_time


# Create rate limiter instance
ip_rate_limiter = IPRateLimiter()


# Rate limiting decorator
def rate_limit(max_requests=30, window=60):
    """
    Rate limiting decorator

    Args:
        max_requests (int): Maximum number of requests in the time window
        window (int): Time window in seconds
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr

            # Whitelist for internal/development IPs
            whitelist = {'127.0.0.1', '::1', '172.17.0.1'}
            if ip in whitelist:
                return f(*args, **kwargs)

            # Check if rate limited
            if ip_rate_limiter.is_rate_limited(ip, max_requests, window):
                return jsonify({
                    "error": "Rate limit exceeded",
                    "message": f"Maximum of {max_requests} requests per {window} seconds allowed."
                }), 429

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Main API route for contact form submissions
@main_bp.route('/api/contact', methods=['POST'])
@rate_limit(max_requests=10, window=60)
def send_email():
    # Get API key
    api_key = os.environ.get('RESEND_API_KEY')

    # Check if API key is available
    if not api_key:
        print("ERROR: RESEND_API_KEY environment variable is not set")
        return jsonify({"error": "API configuration error"}), 500

    # Get data from request
    data = request.json

    # Basic validation
    required_fields = ['name', 'email', 'message', 'recipient_email']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Validate email formats
    if not validate_email(data['email']):
        return jsonify({"error": "Invalid sender email format"}), 400

    if not validate_email(data['recipient_email']):
        return jsonify({"error": "Invalid recipient email format"}), 400

    try:
        # Get email template from utils
        from app.utils import get_email_template

        # Set the API key
        resend.api_key = api_key

        # Send email using Resend with the HTML template
        params = {
            "from": f"Contact Form <{os.environ.get('SENDER_EMAIL')}>",
            "to": [data['recipient_email']],
            "subject": f"New contact form submission from {data['name']}",
            "html": get_email_template(data)
        }

        # Send the email
        email = resend.Emails.send(params)

        return jsonify({
            "success": True,
            "message": "Email sent successfully",
            "id": email["id"]
        }), 200

    except Exception as e:
        # Log the error with more details
        print(f"ERROR sending email: {str(e)}")
        print(f"Type of error: {type(e).__name__}")
        # Return error response
        return jsonify({"error": str(e)}), 500
    

# Health check endpoint
@main_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200
