# Flask Resend API

A lightweight Flask API that uses the Resend service to send emails from contact forms.

## Features

- Simple REST API endpoint for sending emails
- Modern, responsive email templates
- Input validation and sanitization
- Rate limiting to prevent abuse
- Security headers and best practices
- Easy deployment with Docker

## Getting Started

### Prerequisites

- Python 3.7+
- Docker (for container deployment)
- Resend API key (get one at [resend.com](https://resend.com))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/danielmederos2424/flask-resend-api.git
cd flask-resend-api
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file


5. Edit the `.env` file with your Resend API key and other settings:
```
FLASK_APP=run.py
FLASK_ENV=development  # Change to 'production' for production deployment
FLASK_DEBUG=1  # Set to 0 in production
RESEND_API_KEY=your_resend_api_key_here
SENDER_EMAIL=noreply@yourdomain.com
SECRET_KEY=your_secret_key_here  # Generate a strong secret key
```

### Running Locally

```bash
python run.py
```

The API will be available at `http://localhost:5000`.

### Docker Deployment

Build and run the Docker container:

```bash
docker build -t flask-resend-api .
docker run -p 5000:5000 --env-file .env flask-resend-api
```



## API Usage

### Send Email

**Endpoint**: `POST /api/contact`

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "sender@example.com",
  "phone": "123-456-7890",  // Optional
  "message": "Hello, I would like to inquire about your services.",
  "recipient_email": "recipient@example.com"
}
```

**Response (Success)**:
```json
{
  "success": true,
  "message": "Email sent successfully",
  "id": "email-id-from-resend"
}
```

**Response (Error)**:
```json
{
  "error": "Error message here"
}
```

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2023-10-01T12:00:00.000Z",
  "version": "1.0.0"
}
```

## Security Features

- Input validation and sanitization
- Rate limiting (10 requests per minute per IP)
- CORS protection
- Security headers:
  - Content-Security-Policy
  - X-Content-Type-Options
  - X-Frame-Options
  - X-XSS-Protection
- Proxy support

## Customization

### Email Template

The email template can be modified in the `utils.py` file. It uses HTML and CSS for styling.

### Rate Limiting

Rate limiting settings can be adjusted in the `routes.py` file:

```python
@main_bp.route('/api/contact', methods=['POST'])
@rate_limit(max_requests=10, window=60)  # Adjust values as needed
def send_email():
    # ...
```


## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Resend](https://resend.com)
- [Waitress](https://docs.pylonsproject.org/projects/waitress)

## Contact

Created by Daniel Mederos - reach out at [danielmederos2424@gmail.com](mailto:danielmederos2424@gmail.com)

Powered by [WebGraphix](https://www.webgraphix.online)