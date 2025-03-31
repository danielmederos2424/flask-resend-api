from waitress import serve
import os
import logging
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

app = create_app()

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('run')

    # Get port from environment or use default
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))

    # Check environment
    if os.environ.get('FLASK_ENV') == 'development':
        # Use Flask's development server in development mode
        logger.info(f"Starting Flask development server on port {port}...")
        app.run(
            host=os.environ.get('FLASK_RUN_HOST', '0.0.0.0'),
            port=port,
            debug=bool(os.environ.get('FLASK_DEBUG', False))
        )
    else:
        # Use Waitress in production
        logger.info(f"Starting Waitress production server on port {port}...")
        threads = int(os.environ.get('WAITRESS_THREADS', 4))
        connections = int(os.environ.get('WAITRESS_CONNECTIONS', 1000))
        channel_timeout = int(os.environ.get('WAITRESS_CHANNEL_TIMEOUT', 300))

        logger.info(f"Waitress config: threads={threads}, connections={connections}, channel_timeout={channel_timeout}")

        serve(
            app,
            host=os.environ.get('FLASK_RUN_HOST', '0.0.0.0'),
            port=port,
            threads=threads,
            connection_limit=connections,
            channel_timeout=channel_timeout
        )
