"""
Global News Sources
Scrapes news from international sources (Reuters, CNBC)
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import feedparser

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0 Safari/537.36"
}


def fetch_reuters_hot():
    """Fetch from Reuters RSS feed"""
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


def fetch_cnbc_popular():
    """Fetch from CNBC"""
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

    # Remove duplicates
    unique = []
    seen = set()
    for i in items:
        if i["title"] not in seen:
            seen.add(i["title"])
            unique.append(i)

    return unique[:30]
