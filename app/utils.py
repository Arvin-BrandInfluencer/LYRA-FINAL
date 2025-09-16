# ================================================
# FILE: app/utils.py
# PURPOSE: Shared helper functions
# ================================================
from .config import HARDCODED_RATES

def convert_to_eur(amount, currency):
    """Converts a given amount from a specified currency to EUR."""
    if amount is None:
        return 0.0
    rate = HARDCODED_RATES.get(str(currency).upper(), 1.0)
    return float(amount) / rate if rate != 0 else 0.0
