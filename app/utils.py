import re
import bleach
import json
import logging

logger = logging.getLogger('utils')


def validate_email(email):
    """
    Validate email format using regex
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_string(text, max_length=None):
    """
    Sanitize a string to prevent XSS and other injection attacks.
    """
    if text is None:
        return None

    # Convert to string if not already
    if not isinstance(text, str):
        text = str(text)

    # Clean the text using bleach
    cleaned = bleach.clean(text, strip=True)

    # Truncate if needed
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]

    return cleaned


def validate_request_data(data, required_fields=None):
    """
    Validate and sanitize request data

    Args:
        data (dict): The request data
        required_fields (list): List of required field names

    Returns:
        tuple: (valid: bool, result: dict) - Either sanitized data or error messages
    """
    # Check data type
    if not isinstance(data, dict):
        return False, {"error": "Invalid data format"}

    errors = {}

    # Check required fields
    if required_fields:
        for field in required_fields:
            if field not in data or not data[field]:
                errors[field] = f"Field '{field}' is required"

    # Return errors if any required fields are missing
    if errors:
        return False, {"errors": errors}

    # Sanitize all string values
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        else:
            sanitized[key] = value

    return True, sanitized


def get_email_template(data):
    """
    Generate a modern HTML email template with the contact form data
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contact Form Submission</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

            body {{
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #ffffff;
            }}

            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}

            .header {{
                padding: 20px;
                background-color: #4F46E5;
                color: white;
                border-radius: 8px 8px 0 0;
                text-align: center;
            }}

            .content {{
                padding: 30px;
            }}

            .field {{
                margin-bottom: 20px;
            }}

            .label {{
                font-weight: 700;
                color: #4F46E5;
                margin-bottom: 5px;
                display: block;
            }}

            .value {{
                font-size: 16px;
                line-height: 1.6;
                color: #333;
            }}

            .message-box {{
                background-color: #f3f4f6;
                border-left: 4px solid #4F46E5;
                padding: 15px;
                border-radius: 4px;
            }}

            .footer {{
                text-align: center;
                margin-top: 30px;
                color: #6b7280;
                font-size: 14px;
            }}

            .powered-by {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #9ca3af;
            }}

            .powered-by a {{
                color: #6b7280;
                text-decoration: none;
            }}

            .powered-by a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0;">New Contact Form Submission</h1>
            </div>

            <div class="content">
                <div class="field">
                    <div class="label">Name</div>
                    <div class="value">{data['name']}</div>
                </div>

                <div class="field">
                    <div class="label">Email</div>
                    <div class="value">{data['email']}</div>
                </div>

                {f'''
                <div class="field">
                    <div class="label">Phone</div>
                    <div class="value">{data['phone']}</div>
                </div>
                ''' if 'phone' in data else ''}

                <div class="field">
                    <div class="label">Message</div>
                    <div class="value message-box">{data['message'].replace(chr(10), '<br>')}</div>
                </div>
            </div>

            <div class="footer">
                <p>This email was sent automatically from your contact form.</p>
            </div>

            <div class="powered-by">
                <p>Powered by <a href="https://www.webgraphix.online" target="_blank">www.webgraphix.online</a></p>
            </div>
        </div>
    </body>
    </html>
    """


def log_request(request_data):
    """
    Log request information without sensitive data
    """
    # Create a copy to avoid modifying the original
    data_to_log = request_data.copy() if hasattr(request_data, 'copy') else {}

    # Remove sensitive information
    if isinstance(data_to_log, dict):
        if 'email' in data_to_log:
            data_to_log['email'] = f"{data_to_log['email'][:3]}...@redacted"
        if 'message' in data_to_log:
            data_to_log['message'] = f"{data_to_log['message'][:20]}..." if len(data_to_log['message']) > 20 else \
                data_to_log['message']

    # Log the sanitized data
    logger.info(f"Request data: {json.dumps(data_to_log)}")
