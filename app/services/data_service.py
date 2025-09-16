# ================================================
# FILE: app/services/data_service.py
# PURPOSE: Handles all data fetching and database interactions
# ================================================
import traceback
import pandas as pd
from typing import Dict, Any
from app import supabase
from app.config import logger, TARGET_VIEW_NAME, CAMPAIGN_VIEW_NAME, NORDIC_COUNTRIES
from . import processing_service

def get_dashboard_data(payload: Dict[str, Any]):
    """Fetches and processes data for the dashboard source."""
    logger.info("Starting dashboard data processing from view.")
    try:
        filters = payload.get("filters", {})
        market_filter, year_filter = filters.get("market"), filters.get("year")
        
        query = supabase.from_(TARGET_VIEW_NAME).select('*')
        if year_filter and year_filter != "All":
            query = query.eq('year', int(year_filter))
        if market_filter and market_filter != "All":
            if market_filter == "Nordics":
                query = query.in_('region', NORDIC_COUNTRIES)
            else:
                query = query.eq('region', market_filter)
        
        res = query.execute()
        all_data = res.data if res.data else []
        
        return processing_service.process_dashboard_data(all_data, market_filter)
    except Exception as e:
        logger.error(f"Dashboard query from view failed: {e}\n{traceback.format_exc()}")
        return {"error": f"Dashboard query failed: {str(e)}"}

def get_analytics_data(payload: Dict[str, Any]):
    """Fetches data for the analytics source and routes to processing."""
    logger.info("Starting analytics data request from view.")
    try:
        filters = payload.get("filters", {})
        query = supabase.from_(CAMPAIGN_VIEW_NAME).select("*")

        if influencer_name := filters.get("influencer_name"):
            query = query.ilike('influencer_name', f'%{influencer_name.strip()}%')
        if year_str := filters.get("year", "All"):
            if year_str != "All":
                query = query.eq('year', int(year_str))
        if market := filters.get("market", "All"):
            if market != "All":
                markets_to_filter = NORDIC_COUNTRIES if market == "Nordics" else [market]
                query = query.in_('market', markets_to_filter)
        if month := filters.get("month", "All"):
            if month != "All":
                query = query.eq('month', month)
        if week_number := filters.get("week_number"):
            if week_number != "All":
                try:
                    query = query.eq('wk_clean', int(week_number))
                    logger.info(f"Applied week number filter: {week_number}")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid week_number filter value: {week_number}. Must be an integer.")

        response = query.execute()
        if not response.data:
            logger.warning(f"No data found in view matching filters: {filters}")
            return {"items": [], "count": 0}
            
        logger.success(f"Fetched {len(response.data)} filtered records from view.")
        df = pd.DataFrame(response.data)
        
        return processing_service.route_analytics_processing(df, payload)
    except Exception as e:
        logger.error(f"Analytics request from view failed: {e}\n{traceback.format_exc()}")
        return {"error": f"Influencer Analytics query failed: {str(e)}"}
