# ================================================
# FILE: run.py
# PURPOSE: Main entry point to start the Flask application
# ================================================
import os
from app import create_app
from app.config import logger

# Create the Flask app instance using the app factory
app = create_app()

if __name__ == '__main__':
    # Use environment variables for configuration, with defaults
    port = int(os.environ.get("PORT", 10000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ['true', '1']
    
    logger.info(f"Starting Unified Flask API server on host {host} and port {port}")
    app.run(host=host, port=port, debug=debug_mode)
