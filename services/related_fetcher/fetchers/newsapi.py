# services/related_fetcher/fetchers/newsapi.py

import requests
from datetime import datetime, timedelta
from related_fetcher.utils.clean import normalize_output

NEWSAPI_KEY = "268ee36f658d4320befb56d617542118"

def fetch_newsapi(query: str):
    """Fetch related articles from NewsAPI using everything endpoint with date filtering"""
    try:
        # Get today's date for filtering recent articles
        today = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Clean up query - replace commas with spaces for better matching
        clean_query = query.replace(',', ' ')
        
        # Use everything endpoint with date filtering and popularity sorting
        url = f"https://newsapi.org/v2/everything?q={clean_query}&from={from_date}&to={today}&sortBy=popularity&language=en&pageSize=15&apiKey={NEWSAPI_KEY}"
        
        print(f"NewsAPI: Fetching from {url[:100]}...")
        response = requests.get(url, timeout=5)
        print(f"NewsAPI: Response status {response.status_code}")
        
        if response.status_code != 200:
            print(f"NewsAPI: Error status code {response.status_code}")
            return []
        
        data = response.json()
        if data.get("status") != "ok":
            print(f"NewsAPI: Bad status - {data.get('status')}, message: {data.get('message', 'N/A')}")
            return []
        
        articles = data.get("articles", [])
        print(f"NewsAPI: Found {len(articles)} articles")
        
        results = []
        for article in articles:
            if article.get("title") and article.get("url"):
                item = {
                    "source": f"newsapi_{article.get('source', {}).get('name', 'unknown')}",
                    "title": article.get("title", ""),
                    "link": article.get("url", "")
                }
                normalized = normalize_output(item)
                if normalized:
                    results.append(normalized)
        
        print(f"NewsAPI: Returning {len(results)} normalized results")
        return results
    except Exception as e:
        print(f"NewsAPI error: {e}")
        return []
