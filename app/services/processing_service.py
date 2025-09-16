# ================================================
# FILE: app/services/processing_service.py
# PURPOSE: Handles all DataFrame processing and transformations
# ================================================
import pandas as pd
import math
import traceback
from typing import Dict, Any
from app.config import logger, MONTH_ORDER
from app.utils import convert_to_eur

def process_dashboard_data(all_data: list, market_filter: str):
    """Processes raw data from the dashboard view."""
    if not all_data:
        return {"kpi_summary": {}, "monthly_detail": []}

    df = pd.DataFrame(all_data)
    numeric_cols = ['year', 'target_budget_clean', 'actual_spend_clean', 'target_conversions_clean', 'actual_conversions_clean']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    if market_filter == "Nordics":
        df['target_budget_eur'] = df.apply(lambda row: convert_to_eur(row['target_budget_clean'], row['currency']), axis=1)
        df['actual_spend_eur'] = df.apply(lambda row: convert_to_eur(row['actual_spend_clean'], row['currency']), axis=1)
        monthly_agg = df.groupby('month').agg(
            target_budget_clean=('target_budget_eur', 'sum'),
            actual_spend_clean=('actual_spend_eur', 'sum'),
            target_conversions_clean=('target_conversions_clean', 'sum'),
            actual_conversions_clean=('actual_conversions_clean', 'sum')
        ).reset_index()
        monthly_agg['region'], monthly_agg['currency'] = 'Nordics', 'EUR'
        df = monthly_agg

    kpi = {
        'target_budget': int(df['target_budget_clean'].sum()), 
        'actual_spend': int(df['actual_spend_clean'].sum()),
        'target_conversions': int(df['target_conversions_clean'].sum()), 
        'actual_conversions': int(df['actual_conversions_clean'].sum())
    }
    kpi['actual_cac'] = float(kpi['actual_spend'] / kpi['actual_conversions']) if kpi['actual_conversions'] > 0 else 0.0
    
    df.fillna(0, inplace=True)
    df.replace([float('inf'), -float('inf')], 0, inplace=True)
    df['month_order'] = df['month'].map(MONTH_ORDER)
    df = df.sort_values('month_order').drop(columns=['month_order'])
    
    return {"source": "dashboard", "kpi_summary": kpi, "monthly_detail": df.to_dict(orient='records')}

def route_analytics_processing(df: pd.DataFrame, payload: Dict[str, Any]):
    """Cleans the analytics DataFrame and routes it to the correct processing function."""
    numeric_cols = ['total_budget_clean', 'actual_conversions_clean', 'views_clean', 'views', 'clicks_clean', 'clicks', 'ctr_clean', 'cvr_clean']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['views'] = df['views_clean'].where(df['views_clean'] > 0, df['views'])
    df['clicks'] = df['clicks_clean'].where(df['clicks_clean'] > 0, df['clicks'])

    view = payload.get("view", "summary")
    filters = payload.get("filters", {})

    if "influencer_name" in filters:
        return _influencer_process_profile(df, filters.get("influencer_name"))
    if view == "summary":
        return _influencer_process_summary(df, payload)
    if view == "discovery_tiers":
        return _influencer_process_discovery_tiers(df, payload)
    if view == "monthly_breakdown":
        return _influencer_process_monthly_breakdown(df)
    if view == "custom_range_breakdown":
        return _influencer_process_custom_range_breakdown(df, payload)
    if view == "weekly_breakdown_by_number":
        return _influencer_process_weekly_breakdown_by_number(df, payload)
    
    return {"error": f"Invalid view '{view}'."}

def _influencer_process_summary(df: pd.DataFrame, payload: dict):
    """Processes data for the summary view."""
    grouped = df.groupby('influencer_name').apply(lambda x: pd.Series({
        'campaign_count': int(len(x)),
        'total_conversions': int(x['actual_conversions_clean'].sum()),
        'total_views': int(x['views'].sum()),
        'total_clicks': int(x['clicks'].sum()),
        'markets': list(x['market'].unique()),
        'assets': list(x['asset'].dropna().unique()),
        'total_spend_eur': float(sum(convert_to_eur(row['total_budget_clean'], row['currency']) for _, row in x.iterrows())),
        'avg_ctr': float(x[x['ctr_clean'] > 0]['ctr_clean'].mean()),
        'avg_cvr': float(x[x['cvr_clean'] > 0]['cvr_clean'].mean())
    })).reset_index()
    
    grouped['effective_cac_eur'] = (grouped['total_spend_eur'] / grouped['total_conversions']).fillna(0).replace([float('inf'), -float('inf')], 0)
    grouped.fillna({'avg_ctr': 0, 'avg_cvr': 0}, inplace=True)
    
    if sort_config := payload.get("sort"):
        grouped = grouped.sort_values(by=sort_config.get("by", "total_spend_eur"), ascending=sort_config.get("order", "desc") == "asc")
        
    return {"source": "influencer_summary", "count": len(grouped), "items": grouped.to_dict(orient='records')}

def _influencer_process_discovery_tiers(df: pd.DataFrame, payload: dict):
    """Processes data for the discovery tiers view."""
    summary_result = _influencer_process_summary(df, {})
    if not summary_result.get("items"): return {"gold": [], "silver": [], "bronze": []}
    
    grouped = pd.DataFrame(summary_result["items"])
    if grouped.empty: return {"gold": [], "silver": [], "bronze": []}
    
    zero_cac = grouped[grouped['effective_cac_eur'] <= 0]
    ranked = grouped[grouped['effective_cac_eur'] > 0].sort_values(by='effective_cac_eur', ascending=True)
    count = len(ranked)
    
    top_third_index, mid_third_index = math.ceil(count / 3), math.ceil(count * 2 / 3)
    gold_df, silver_df = ranked.iloc[:top_third_index], ranked.iloc[top_third_index:mid_third_index]
    bronze_df = pd.concat([ranked.iloc[mid_third_index:], zero_cac])
    
    all_tiers = {
        "gold": gold_df.to_dict(orient='records'),
        "silver": silver_df.to_dict(orient='records'),
        "bronze": bronze_df.to_dict(orient='records')
    }
    
    if requested_tier := payload.get("filters", {}).get("tier"):
        if requested_tier.lower() in all_tiers:
            return {"source": "discovery_tier_specific", "tier": requested_tier, "items": all_tiers[requested_tier.lower()]}
            
    return {"source": "discovery_tiers", **all_tiers}

def _influencer_process_monthly_breakdown(df: pd.DataFrame):
    """Processes data for the monthly breakdown view."""
    if df.empty or 'month' not in df.columns: return {"monthly_data": []}
    df = df.dropna(subset=['month'])
    results = []
    
    for month_name, month_df in df.groupby('month'):
        total_spend_eur = float(sum(convert_to_eur(row['total_budget_clean'], row['currency']) for _, row in month_df.iterrows()))
        total_conversions = int(month_df['actual_conversions_clean'].sum())
        
        summary = {
            'total_spend_eur': total_spend_eur,
            'total_conversions': total_conversions,
            'avg_cac_eur': total_spend_eur / total_conversions if total_conversions > 0 else 0.0,
            'influencer_count': int(month_df['influencer_name'].nunique())
        }
        
        details = month_df[['influencer_name', 'market', 'currency', 'total_budget_clean', 'actual_conversions_clean']].rename(columns={'total_budget_clean': 'budget_local', 'actual_conversions_clean': 'conversions'})
        details['cac_local'] = (details['budget_local'] / details['conversions']).fillna(0).replace([float('inf'), -float('inf')], 0)
        results.append({'month': month_name, 'summary': summary, 'details': details.to_dict(orient='records')})
        
    results.sort(key=lambda x: MONTH_ORDER.get(x['month'], 99))
    return {"source": "monthly_breakdown", "monthly_data": results}

def _influencer_process_custom_range_breakdown(df: pd.DataFrame, payload: dict):
    """Processes data for a custom date range."""
    logger.info("Starting custom range breakdown processing.")
    try:
        filters = payload.get("filters", {})
        date_from, date_to = filters.get("date_from"), filters.get("date_to")

        if not date_from or not date_to: return {"error": "'date_from' and 'date_to' filters are required."}
        if 'live_date_clean' not in df.columns: return {"error": "'live_date_clean' column is not available."}

        df['live_date_clean'] = pd.to_datetime(df['live_date_clean'], errors='coerce')
        df.dropna(subset=['live_date_clean'], inplace=True)

        mask = (df['live_date_clean'] >= pd.to_datetime(date_from)) & (df['live_date_clean'] <= pd.to_datetime(date_to))
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            logger.warning(f"No data found for the date range {date_from} to {date_to}")
            return {"summary": {}, "details": []}

        total_spend_eur = float(sum(convert_to_eur(row['total_budget_clean'], row['currency']) for _, row in filtered_df.iterrows()))
        total_conversions = int(filtered_df['actual_conversions_clean'].sum())

        summary = {
            'total_spend_eur': total_spend_eur,
            'total_conversions': total_conversions,
            'avg_cac_eur': total_spend_eur / total_conversions if total_conversions > 0 else 0.0,
            'influencer_count': int(filtered_df['influencer_name'].nunique())
        }

        details = filtered_df[['influencer_name', 'market', 'currency', 'total_budget_clean', 'actual_conversions_clean', 'live_date_clean']].rename(columns={'total_budget_clean': 'budget_local', 'actual_conversions_clean': 'conversions', 'live_date_clean': 'live_date'})
        details['cac_local'] = (details['budget_local'] / details['conversions']).fillna(0).replace([float('inf'), -float('inf')], 0)
        details['live_date'] = details['live_date'].dt.strftime('%Y-%m-%d')

        return {"source": "custom_range_breakdown", "date_range": {"from": date_from, "to": date_to}, "summary": summary, "details": details.to_dict(orient='records')}
    except Exception as e:
        logger.error(f"Custom range breakdown failed: {e}\n{traceback.format_exc()}")
        return {"error": f"Custom range breakdown failed: {str(e)}"}

def _influencer_process_weekly_breakdown_by_number(df: pd.DataFrame, payload: dict):
    """Processes data for a specific week number (already filtered)."""
    logger.info("Starting weekly breakdown by number processing.")
    try:
        filters = payload.get("filters", {})
        week_number = filters.get("week_number")

        if df.empty:
            logger.warning(f"No data found for week number {week_number} after initial filtering.")
            return {"summary": {}, "details": []}
        
        total_spend_eur = float(sum(convert_to_eur(row['total_budget_clean'], row['currency']) for _, row in df.iterrows()))
        total_conversions = int(df['actual_conversions_clean'].sum())

        summary = {
            'total_spend_eur': total_spend_eur,
            'total_conversions': total_conversions,
            'avg_cac_eur': total_spend_eur / total_conversions if total_conversions > 0 else 0.0,
            'influencer_count': int(df['influencer_name'].nunique())
        }

        details = df[['influencer_name', 'market', 'currency', 'total_budget_clean', 'actual_conversions_clean', 'live_date_clean', 'wk_clean']].rename(columns={'total_budget_clean': 'budget_local', 'actual_conversions_clean': 'conversions', 'live_date_clean': 'live_date', 'wk_clean': 'week_number'})
        details['cac_local'] = (details['budget_local'] / details['conversions']).fillna(0).replace([float('inf'), -float('inf')], 0)
        details['live_date'] = pd.to_datetime(details['live_date'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        return {"source": "weekly_breakdown_by_number", "week_number": week_number, "summary": summary, "details": details.to_dict(orient='records')}
    except Exception as e:
        logger.error(f"Weekly breakdown by number failed: {e}\n{traceback.format_exc()}")
        return {"error": f"Weekly breakdown by number failed: {str(e)}"}

def _influencer_process_profile(df: pd.DataFrame, influencer_name: str):
    """Processes data for a single influencer profile view."""
    influencer_df = df.copy()
    influencer_df['cac_local'] = (influencer_df['total_budget_clean'] / influencer_df['actual_conversions_clean']).fillna(0).replace([float('inf'), -float('inf')], 0)
    influencer_df['ctr'] = (influencer_df['clicks'] / influencer_df['views']).fillna(0).replace([float('inf'), -float('inf')], 0)
    
    if 'month' in influencer_df.columns:
        influencer_df['month_order'] = influencer_df['month'].map(MONTH_ORDER)
        influencer_df = influencer_df.sort_values(by=['year', 'month_order'])
        
    return {"source": "influencer_detail", "campaigns": influencer_df.to_dict(orient='records')}
