"""
Indian News Sources
Scrapes news from major Indian news websites
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0 Safari/537.36"
}


def fetch_financial_express():
    """Fetch from Financial Express"""
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


def fetch_livemint_latest():
    """Fetch from LiveMint"""
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


def fetch_times_of_india_trending():
    """Fetch from Times of India"""
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


def fetch_india_today_breaking():
    """Fetch from India Today"""
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


def fetch_hindustan_times_latest():
    """Fetch from Hindustan Times"""
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
