# ================================================
# FILE: tests_backend/test_routes.py
# PURPOSE: Tests for the API endpoints in routes.py
# ================================================
import json

def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.get('/')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_handle_influencer_query_dashboard_success(test_client, mocker):
    """Test a successful dashboard query."""
    # Mock the service layer function
    mock_data = {"kpi_summary": {"target_budget": 1000}, "monthly_detail": []}
    mocker.patch('app.services.data_service.get_dashboard_data', return_value=mock_data)

    payload = {"source": "dashboard", "filters": {"market": "UK", "year": 2025}}
    response = test_client.post('/api/influencer/query', data=json.dumps(payload), content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['kpi_summary']['target_budget'] == 1000

def test_handle_influencer_query_analytics_success(test_client, mocker):
    """Test a successful analytics query."""
    mock_data = {"source": "influencer_summary", "count": 1, "items": [{"influencer_name": "Test Influencer"}]}
    mocker.patch('app.services.data_service.get_analytics_data', return_value=mock_data)

    payload = {"source": "influencer_analytics", "view": "summary", "filters": {}}
    response = test_client.post('/api/influencer/query', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 200
    assert response.json['count'] == 1

def test_handle_influencer_query_invalid_source(test_client):
    """Test request with an invalid source."""
    payload = {"source": "invalid_source"}
    response = test_client.post('/api/influencer/query', data=json.dumps(payload), content_type='application/json')
    
    assert response.status_code == 400
    assert "Invalid 'source'" in response.json['error']

def test_handle_influencer_query_no_payload(test_client):
    """Test request with no JSON payload."""
    response = test_client.post('/api/influencer/query', content_type='application/json')
    
    assert response.status_code == 400
    assert response.json['error'] == 'Invalid JSON payload'

def test_handle_influencer_query_service_error(test_client, mocker):
    """Test how the route handles an error from the service layer."""
    mocker.patch('app.services.data_service.get_dashboard_data', return_value={"error": "Database connection failed"})
    
    payload = {"source": "dashboard", "filters": {}}
    response = test_client.post('/api/influencer/query', data=json.dumps(payload), content_type='application/json')
    
    assert response.status_code == 400
    assert response.json['error'] == 'Database connection failed'
