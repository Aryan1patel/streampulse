# services/ingestors/trending_ingestor/scraping.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import feedparser
import os
import json
import urllib.request

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0 Safari/537.36"
}

# API Keys
GNEWS_API_KEY = "3efca6db8791fc18ce266a4801974bac"
NEWSDATA_API_KEY = "pub_9aebd96f4f1e4f2cb1eb8a6b2f928aaa"
NEWSAPI_KEY = "a46c3d6427d54778882898c2b4d85dc0"
WORLDNEWS_API_KEY = "effecce0233f4782a4f7e34aa7e75d40"



# ============================================================================
# 🟢 0. NEWS APIs (GNews & NewsData.io)
# ============================================================================
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
        # Get all Indian news - filter.py will handle filtering
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
        # Get top headlines from India - all categories, filter.py will handle filtering
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
        
        # WorldNewsAPI returns {top_news: [...], language: "en"}
        top_news = data.get("top_news", [])
        
        articles = []
        for news_item in top_news[:10]:  # Get top 10
            # Each item has: {news: [{...}, {...}]}
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





# ============================================================================
# 🟢 1. MONEYCONTROL TRENDING (Indian Finance)
# ============================================================================
def fetch_moneycontrol_api():
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



# 3efca6db8791fc18ce266a4801974bac



def fetch_gnews_api():
    token = os.getenv("GNEWS_API_KEY")
    if not token:
        raise Exception("GNEWS_API_KEY is missing")

    url = f"https://gnews.io/api/v4/top-headlines?category=business&lang=en&country=in&token={token}"

    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()

    return [
        {
            "source": "gnews_api",
            "title": a["title"],
            "link": a["url"]
        }
        for a in data.get("articles", [])
    ]




# def fetch_reddit_api():
#     auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
#     data = {"grant_type": "client_credentials"}
#     headers = {"User-Agent": "streampulse-news/0.1"}

#     token = requests.post("https://www.reddit.com/api/v1/access_token",
#                           auth=auth, data=data, headers=headers).json()["access_token"]

#     headers["Authorization"] = f"bearer {token}"

#     r = requests.get("https://oauth.reddit.com/r/news/hot", headers=headers)

#     return [
#         {
#             "source": "reddit_api",
#             "title": post["data"]["title"],
#             "link": post["data"]["url"]
#         }
#         for post in r.json()["data"]["children"]
#     ]

# ============================================================================
# 🟢 2. FINANCIAL EXPRESS (Indian breaking/market news)
# ============================================================================
def fetch_financial_express():
    url = "https://www.financialexpress.com/latest-news/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    items = []
    for a in soup.select("div.listing a"):
        title = a.get_text(strip=True)
        href = a.get("href")
        if title and href:
            items.append({
                "source": "financial_express",
                "title": title,
                "link": href
            })
    return items[:20]


# ============================================================================
# 🟡 3. LIVEMINT LATEST (Very strong for India)
# ============================================================================
def fetch_livemint_latest():
    url = "https://www.livemint.com/latest-news"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    items = []
    for a in soup.select("h2 a, h3 a"):
        title = a.get_text(strip=True)
        href = a.get("href")
        if not title or not href:
            continue

        link = urljoin("https://www.livemint.com", href)
        items.append({
            "source": "livemint_latest",
            "title": title,
            "link": link
        })
    return items[:20]


# ============================================================================
# 🟡 4. TIMES OF INDIA TRENDING (India breaking events)
# ============================================================================
def fetch_times_of_india_trending():
    url = "https://timesofindia.indiatimes.com/briefs"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    items = []
    for a in soup.select("span.w_tle a"):
        title = a.get_text(strip=True)
        href = a.get("href")

        if not title or not href:
            continue

        link = urljoin("https://timesofindia.indiatimes.com", href)
        items.append({
            "source": "toi_trending",
            "title": title,
            "link": link
        })
    return items[:20]


# ============================================================================
# 🟡 5. INDIA TODAY BREAKING NEWS (Blast, crime, govt actions)
# ============================================================================
def fetch_india_today_breaking():
    url = "https://www.indiatoday.in/top-stories"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    items = []
    for a in soup.select("div.catagory-listing a"):
        title = a.get_text(strip=True)
        href = a.get("href")
        if not title or not href:
            continue

        link = urljoin("https://www.indiatoday.in", href)
        items.append({
            "source": "india_today_breaking",
            "title": title,
            "link": link
        })
    return items[:20]


# ============================================================================
# 🟡 6. HINDUSTAN TIMES LATEST (Politics, policy, India news)
# ============================================================================
def fetch_hindustan_times_latest():
    url = "https://www.hindustantimes.com/business"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    items = []
    for a in soup.select("h3 a, h2 a"):
        title = a.get_text(strip=True)
        href = a.get("href")

        if not title or not href:
            continue

        link = urljoin("https://www.hindustantimes.com", href)
        items.append({
            "source": "hindustan_times_latest",
            "title": title,
            "link": link
        })
    return items[:20]


# ============================================================================
# 🔵 7. REUTERS HOT (RSS → global)
# ============================================================================
def fetch_reuters_hot():
    feed_url = "https://www.reuters.com/rssFeed/topNews"
    feed = feedparser.parse(feed_url)

    items = []
    for entry in feed.entries[:20]:
        items.append({
            "source": "reuters_hot",
            "title": entry.title,
            "link": entry.link
        })
    return items


# ============================================================================
# 🔵 8. CNBC POPULAR (global/market)
# ============================================================================
def fetch_cnbc_popular():
    url = "https://www.cnbc.com/world/?region=world"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    items = []

    for a in soup.select("a.Card-title, a.featured-card__title"):
        title = a.get_text(strip=True)
        href = a.get("href")
        if title and href:
            items.append({
                "source": "cnbc_popular",
                "title": title,
                "link": urljoin("https://www.cnbc.com", href)
            })

    for a in soup.select("div.MostPopularNews-container a"):
        title = a.get_text(strip=True)
        href = a.get("href")
        if title and href:
            items.append({
                "source": "cnbc_popular",
                "title": title,
                "link": urljoin("https://www.cnbc.com", href)
            })

    # remove duplicates
    unique = []
    seen = set()
    for i in items:
        if i["title"] not in seen:
            seen.add(i["title"])
            unique.append(i)

    return unique[:30]