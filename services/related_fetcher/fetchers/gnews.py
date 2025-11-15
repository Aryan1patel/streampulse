import json
import urllib.request
from related_fetcher.utils.clean import normalize_output

GNEWS_API_KEY = "3efca6db8791fc18ce266a4801974bac"

def fetch_gnews(query, max_results=10):
    """Fetch news from GNews API"""
    try:
        # GNews supports complex queries with operators
        url = f"https://gnews.io/api/v4/search?q={urllib.parse.quote(query)}&lang=en&country=in&max={max_results}&apikey={GNEWS_API_KEY}"
        
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            articles = data.get("articles", [])
            
            results = []
            for article in articles:
                item = normalize_output({
                    "source": f"GNews - {article.get('source', {}).get('name', 'Unknown')}",
                    "title": article.get("title", ""),
                    "link": article.get("url", ""),
                    "description": article.get("description", "")
                })
                if item:
                    results.append(item)
            
            return results
            
    except Exception as e:
        print(f"GNews API error: {e}")
        return []
