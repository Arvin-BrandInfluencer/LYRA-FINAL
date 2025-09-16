# ================================================
# FILE: tests_backend/conftest.py
# PURPOSE: Fixtures for pytest
# ================================================
import pytest
from app import create_app

@pytest.fixture(scope='module')
def test_client():
    """Create a Flask test client for the application."""
    flask_app = create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client
