# ----------------------------------------------------
# 🔥 STREAMPULSE NEWS SOURCE CONFIGURATION
# ----------------------------------------------------

# 📌 Basic RSS Feeds (Latest News)
RSS_LATEST = [
    "https://www.moneycontrol.com/rss/latestnews.xml",
    "https://economictimes.indiatimes.com/feeds/newsdefaultfeeds.cms",
    "https://www.reuters.com/tools/rss",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html"
]

# 📌 Trending Feeds (HTML pages — scraped later)
TRENDING_SOURCES = {
    "moneycontrol_trending": "https://www.moneycontrol.com/news/trending-news/",
    "economic_times_trending": "https://economictimes.indiatimes.com/mostread.cms",
    "reuters_most_read": "https://www.reuters.com/world/",
    "cnbc_most_popular": "https://www.cnbc.com/world/?region=world"
}

# 📌 Government Feeds (to be used later)
GOV_SOURCES = {
    "rbi_press": "https://rbi.org.in/scripts/BS_PressReleaseDisplay.aspx",
    "sebi_news": "https://www.sebi.gov.in/sebiweb/home/list/1/7/0/press-releases"
}

# 📌 Twitter queries (snscrape)
TWITTER_QUERIES = [
    "Finance India",
    "Nifty 50",
    "Sensex",
    "RBI",
    "Breaking news India",
    "Scam",
    "Explosion",
    "Policy"
]

# 🚀 Combined (if any service needs all)
ALL_SOURCES = {
    "rss_latest": RSS_LATEST,
    "trending": TRENDING_SOURCES,
    "gov": GOV_SOURCES,
    "twitter": TWITTER_QUERIES
}