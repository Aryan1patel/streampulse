import requests
from related_fetcher.utils.clean import normalize_output

NEWSDATA_API_KEY = "pub_9aebd96f4f1e4f2cb1eb8a6b2f928aaa"

def fetch_newsdata(query, max_results=10):
    """Fetch news from NewsData.io API"""
    try:
        # NewsData.io latest news endpoint with filters
        url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&q={query}&country=in,us&language=en&category=business,politics,top,world"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            print(f"NewsData API returned status {response.status_code}")
            return []
        
        data = response.json()
        articles = data.get("results", [])
        
        results = []
        for article in articles[:max_results]:
            source_name = article.get("source_id", "Unknown")
            item = normalize_output({
                "source": f"NewsData - {source_name}",
                "title": article.get("title", ""),
                "link": article.get("link", ""),
                "description": article.get("description", "")
            })
            if item:
                results.append(item)
        
        return results
        
    except Exception as e:
        print(f"NewsData API error: {e}")
        return []
