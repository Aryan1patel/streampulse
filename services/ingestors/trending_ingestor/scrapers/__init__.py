"""
News Scraping Orchestrator
Imports and exposes all scraper functions from organized modules
"""
from .api_sources import (
    fetch_gnews_trending,
    fetch_newsdata_trending,
    fetch_newsapi_trending,
    fetch_worldnews_trending,
    fetch_moneycontrol_api
)

from .indian_sources import (
    fetch_financial_express,
    fetch_livemint_latest,
    fetch_times_of_india_trending,
    fetch_india_today_breaking,
    fetch_hindustan_times_latest
)

from .global_sources import (
    fetch_reuters_hot,
    fetch_cnbc_popular
)

# Export all scraper functions
__all__ = [
    # API sources
    'fetch_gnews_trending',
    'fetch_newsdata_trending',
    'fetch_newsapi_trending',
    'fetch_worldnews_trending',
    'fetch_moneycontrol_api',
    # Indian sources
    'fetch_financial_express',
    'fetch_livemint_latest',
    'fetch_times_of_india_trending',
    'fetch_india_today_breaking',
    'fetch_hindustan_times_latest',
    # Global sources
    'fetch_reuters_hot',
    'fetch_cnbc_popular'
]
