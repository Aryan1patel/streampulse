# services/related_fetcher/fetchers/worldnews.py

import requests
from related_fetcher.utils.clean import normalize_output

WORLDNEWS_API_KEY = "effecce0233f4782a4f7e34aa7e75d40"

def fetch_worldnews(query: str):
    """Fetch related articles from World News API - India focus"""
    try:
        # Search for news articles matching the query
        url = f"https://api.worldnewsapi.com/search-news?text={query}&source-countries=in&language=en&number=10&api-key={WORLDNEWS_API_KEY}"
        
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return []
        
        data = response.json()
        news_articles = data.get("news", [])
        
        results = []
        for article in news_articles:
            if article.get("title") and article.get("url"):
                item = {
                    "source": "worldnews_india",
                    "title": article.get("title", ""),
                    "link": article.get("url", "")
                }
                normalized = normalize_output(item)
                if normalized:
                    results.append(normalized)
        
        return results
    except Exception as e:
        print(f"WorldNews API error: {e}")
        return []
