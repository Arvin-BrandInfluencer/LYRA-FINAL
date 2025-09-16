# ================================================
# FILE: app/routes.py
# PURPOSE: Defines all API endpoints for the application
# ================================================
import traceback
from flask import current_app as app
from flask import request, jsonify
from .config import logger
from .services import data_service

@app.route('/api/influencer/query', methods=['POST'])
def handle_influencer_query():
    """Main query endpoint that routes requests based on the 'source' parameter."""
    try:
        payload = request.get_json(silent=True)
        if not payload:
            logger.warning("Received request with invalid or missing JSON payload.")
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        source = payload.get("source")
        logger.info(f"Routing request for source: '{source}'")

        if source == "dashboard":
            result = data_service.get_dashboard_data(payload)
        elif source == "influencer_analytics":
            result = data_service.get_analytics_data(payload)
        else:
            logger.warning(f"Received invalid source: {source}")
            result = {"error": f"Invalid 'source'. Must be 'dashboard' or 'influencer_analytics'."}
        
        if "error" in result:
            # Errors from services are already logged, so just return
            return jsonify(result), 400
        
        return jsonify(result)

    except Exception as e:
        logger.critical(f"An unhandled exception occurred in handle_influencer_query: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500

@app.route('/')
def health_check():
    """Provides a simple health check endpoint."""
    return jsonify({"status": "healthy", "message": "Unified Brand Influence Query API is running."})
