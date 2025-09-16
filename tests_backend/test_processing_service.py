# ================================================
# FILE: tests_backend/test_processing_service.py
# PURPOSE: Tests for the data transformation logic
# ================================================
import pandas as pd
from app.services import processing_service

def test_process_dashboard_data():
    """Test basic aggregation for dashboard data."""
    raw_data = [
        {'month': 'Jan', 'region': 'UK', 'currency': 'GBP', 'target_budget_clean': 850, 'actual_spend_clean': 425, 'target_conversions_clean': 100, 'actual_conversions_clean': 50},
        {'month': 'Feb', 'region': 'UK', 'currency': 'GBP', 'target_budget_clean': 850, 'actual_spend_clean': 850, 'target_conversions_clean': 100, 'actual_conversions_clean': 120}
    ]
    result = processing_service.process_dashboard_data(raw_data, "UK")
    
    assert result['kpi_summary']['target_budget'] == 1700
    assert result['kpi_summary']['actual_spend'] == 1275
    assert result['kpi_summary']['actual_conversions'] == 170
    assert result['kpi_summary']['actual_cac'] == 7.5
    assert len(result['monthly_detail']) == 2
    assert result['monthly_detail'][0]['month'] == 'Jan'

def test_process_dashboard_data_nordics():
    """Test Nordics aggregation which involves currency conversion."""
    raw_data = [
        {'month': 'Jan', 'region': 'Sweden', 'currency': 'SEK', 'target_budget_clean': 1130, 'actual_spend_clean': 1130, 'target_conversions_clean': 10, 'actual_conversions_clean': 5}, # 100 EUR
        {'month': 'Jan', 'region': 'Norway', 'currency': 'NOK', 'target_budget_clean': 1150, 'actual_spend_clean': 0, 'target_conversions_clean': 10, 'actual_conversions_clean': 0} # 100 EUR
    ]
    result = processing_service.process_dashboard_data(raw_data, "Nordics")
    
    # All values should be aggregated and in EUR
    assert result['kpi_summary']['target_budget'] == 200
    assert result['kpi_summary']['actual_spend'] == 100
    assert result['kpi_summary']['actual_conversions'] == 5
    assert result['monthly_detail'][0]['currency'] == 'EUR'
    assert len(result['monthly_detail']) == 1

def test_influencer_process_summary():
    """Test the summary processing logic."""
    raw_data = [
        {'influencer_name': 'A', 'currency': 'GBP', 'total_budget_clean': 85, 'actual_conversions_clean': 10, 'views': 1000, 'clicks': 50, 'market': 'UK', 'asset': 'Reel', 'ctr_clean': 0.05, 'cvr_clean': 0.2}, # 100 EUR
        {'influencer_name': 'A', 'currency': 'EUR', 'total_budget_clean': 50, 'actual_conversions_clean': 10, 'views': 1000, 'clicks': 100, 'market': 'FR', 'asset': 'Story', 'ctr_clean': 0.10, 'cvr_clean': 0.1}
    ]
    df = pd.DataFrame(raw_data)
    result = processing_service._influencer_process_summary(df, {})
    
    item = result['items'][0]
    assert result['count'] == 1
    assert item['influencer_name'] == 'A'
    assert item['campaign_count'] == 2
    assert item['total_conversions'] == 20
    assert item['total_spend_eur'] == 150
    assert item['effective_cac_eur'] == 7.5
    assert item['avg_ctr'] == 0.075

def test_process_custom_range_breakdown():
    """Test custom date range filtering."""
    raw_data = [
        {'live_date_clean': '2025-03-10', 'total_budget_clean': 100, 'actual_conversions_clean': 10, 'currency': 'EUR', 'influencer_name': 'A'},
        {'live_date_clean': '2025-03-15', 'total_budget_clean': 200, 'actual_conversions_clean': 15, 'currency': 'EUR', 'influencer_name': 'B'},
        {'live_date_clean': '2025-04-01', 'total_budget_clean': 300, 'actual_conversions_clean': 20, 'currency': 'EUR', 'influencer_name': 'C'}
    ]
    df = pd.DataFrame(raw_data)
    payload = {"filters": {"date_from": "2025-03-01", "date_to": "2025-03-31"}}
    
    result = processing_service._influencer_process_custom_range_breakdown(df, payload)
    
    assert len(result['details']) == 2
    assert result['summary']['total_spend_eur'] == 300
    assert result['summary']['total_conversions'] == 25
