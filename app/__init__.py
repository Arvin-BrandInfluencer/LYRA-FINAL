# ================================================
# FILE: app/__init__.py
# PURPOSE: Flask application factory and initialization
# ================================================
import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from supabase import create_client, Client
from .config import logger  # Import the configured logger

# Load environment variables from .env file
load_dotenv()

# Global Supabase client, initialized once
supabase: Client = None

def init_supabase_client():
    """Initializes and returns the Supabase client."""
    global supabase
    if supabase is None:
        try:
            url: str = os.environ.get("SUPABASE_URL")
            key: str = os.environ.get("SUPABASE_KEY")
            if not url or not key:
                logger.critical("Supabase URL and Key must be set in the .env file.")
                sys.exit(1)
            supabase = create_client(url, key)
            logger.success("Successfully connected to Supabase.")
        except Exception as e:
            logger.critical(f"Failed to connect to Supabase. Check credentials. Error: {e}")
            sys.exit(1)
    return supabase

def create_app():
    """Application factory function."""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize extensions
    init_supabase_client()

    with app.app_context():
        # Import and register routes/blueprints
        from . import routes
        
    return app
