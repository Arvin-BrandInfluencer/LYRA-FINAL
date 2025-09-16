# ================================================
# FILE: app/config.py
# PURPOSE: Centralized constants and configuration
# ================================================
import os
import sys
from loguru import logger

# --- Logger Configuration ---
# Configure once here and import it everywhere else
logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", colorize=True)

# --- Database View Names ---
CAMPAIGN_VIEW_NAME = 'all_influencer_campaigns'
TARGET_VIEW_NAME = 'all_market_targets'

# --- Business Logic Constants ---
NORDIC_COUNTRIES = ['Sweden', 'Norway', 'Denmark']
HARDCODED_RATES = {"EUR": 1.0, "GBP": 0.85, "SEK": 11.30, "NOK": 11.50, "DKK": 7.46}
MONTH_ORDER = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
