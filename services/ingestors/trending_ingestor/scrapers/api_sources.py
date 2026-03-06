"""
API-based News Sources
Fetches news from various news APIs (GNews, NewsData, NewsAPI, WorldNews)
"""
import requests
import json
import urllib.request
import os

# API Keys
GNEWS_API_KEY = "3efca6db8791fc18ce266a4801974bac"
NEWSDATA_API_KEY = "pub_9aebd96f4f1e4f2cb1eb8a6b2f928aaa"
NEWSAPI_KEY = "a46c3d6427d54778882898c2b4d85dc0"
WORLDNEWS_API_KEY = "effecce0233f4782a4f7e34aa7e75d40"


def fetch_gnews_trending():
    """Fetch trending news from GNews API"""
    try:
        url = f"https://gnews.io/api/v4/top-headlines?lang=en&country=in&max=10&apikey={GNEWS_API_KEY}"
        
        with urllib.request.urlopen(url, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            articles = data.get("articles", [])
            
            return [
                {
                    "source": f"gnews_{article.get('source', {}).get('name', 'unknown')}",
                    "title": article.get("title", ""),
                    "link": article.get("url", "")
                }
                for article in articles if article.get("title") and article.get("url")
            ]
    except Exception as e:
        print(f"❌ GNews API failed: {e}")
        return []


def fetch_newsdata_trending():
    """Fetch trending news from NewsData.io API - India focus"""
    try:
        url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&country=in&language=en"
        
        response = requests.get(url, timeout=8)
        if response.status_code != 200:
            print(f"❌ NewsData API returned status {response.status_code}")
            return []
        
        data = response.json()
        articles = data.get("results", [])
        
        return [
            {
                "source": f"newsdata_{article.get('source_id', 'unknown')}",
                "title": article.get("title", ""),
                "link": article.get("link", "")
            }
            for article in articles[:10] if article.get("title") and article.get("link")
        ]
    except Exception as e:
        print(f"❌ NewsData API failed: {e}")
        return []


def fetch_newsapi_trending():
    """Fetch top headlines from NewsAPI - India focus"""
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&pageSize=20&apiKey={NEWSAPI_KEY}"
        
        response = requests.get(url, timeout=8)
        if response.status_code != 200:
            print(f"❌ NewsAPI returned status {response.status_code}")
            return []
        
        data = response.json()
        if data.get("status") != "ok":
            print(f"❌ NewsAPI error: {data.get('message', 'Unknown error')}")
            return []
        
        articles = data.get("articles", [])
        
        return [
            {
                "source": f"newsapi_{article.get('source', {}).get('name', 'unknown')}",
                "title": article.get("title", ""),
                "link": article.get("url", "")
            }
            for article in articles if article.get("title") and article.get("url")
        ]
    except Exception as e:
        print(f"❌ NewsAPI failed: {e}")
        return []


def fetch_worldnews_trending():
    """Fetch top news from World News API - India focus"""
    try:
        url = f"https://api.worldnewsapi.com/top-news?source-country=in&language=en&api-key={WORLDNEWS_API_KEY}"
        
        response = requests.get(url, timeout=8)
        if response.status_code != 200:
            print(f"❌ WorldNewsAPI returned status {response.status_code}")
            return []
        
        data = response.json()
        top_news = data.get("top_news", [])
        
        articles = []
        for news_item in top_news[:10]:
            news_list = news_item.get("news", [])
            for article in news_list:
                title = article.get("title")
                link = article.get("url")
                if title and link:
                    articles.append({
                        "source": "worldnews_india",
                        "title": title,
                        "link": link
                    })
        
        return articles[:10]
    except Exception as e:
        print(f"❌ WorldNewsAPI failed: {e}")
        return []


def fetch_moneycontrol_api():
    """Fetch from MoneyControl API"""
    urls = [
        "https://mc-api-j0rn.onrender.com/api/business_news",
        "https://mc-api-j0rn.onrender.com/api/latest_news",
        "https://mc-api-j0rn.onrender.com/api/news"
    ]

    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()

            items = []
            for a in data:
                title = a.get("Title")
                link = a.get("Link")
                if title and link:
                    items.append({
                        "source": "moneycontrol_api",
                        "title": title,
                        "link": link
                    })

            if items:
                return items[:20]

        except Exception as e:
            print(f"❌ Moneycontrol API failed: {url} -> {e}")

    return []
