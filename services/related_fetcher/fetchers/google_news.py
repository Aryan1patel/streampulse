# services/related_fetcher/fetchers/google_news.py

import requests
from related_fetcher.utils.clean import normalize_output

SERPAPI_KEY = "4c9efbb6d4374ae982fcbf31a5d4045e280c4a96e4eee98000f75beb16296a80"

def fetch_google_news(query: str):
    """Fetch related articles from Google News via SerpAPI"""
    try:
        # Clean up query - replace commas with spaces
        clean_query = query.replace(',', ' ')
        
        # SerpAPI Google News endpoint
        url = f"https://serpapi.com/search.json?engine=google_news&q={clean_query}&gl=us&hl=en&api_key={SERPAPI_KEY}"
        
        print(f"Google News: Fetching from SerpAPI with query: {clean_query[:50]}...")
        response = requests.get(url, timeout=10)
        print(f"Google News: Response status {response.status_code}")
        
        if response.status_code != 200:
            print(f"Google News: Error status code {response.status_code}")
            return []
        
        data = response.json()
        
        # Check for API errors
        if "error" in data:
            print(f"Google News: API error - {data.get('error')}")
            return []
        
        # Get news results
        news_results = data.get("news_results", [])
        print(f"Google News: Found {len(news_results)} articles")
        
        results = []
        for article in news_results:
            if article.get("title") and article.get("link"):
                item = {
                    "source": f"google_news_{article.get('source', {}).get('name', 'unknown')}",
                    "title": article.get("title", ""),
                    "link": article.get("link", "")
                }
                normalized = normalize_output(item)
                if normalized:
                    results.append(normalized)
        
        print(f"Google News: Returning {len(results)} normalized results")
        return results[:15]  # Limit to 15 results
        
    except Exception as e:
        print(f"Google News error: {e}")
        return []
