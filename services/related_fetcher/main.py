from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from related_fetcher.fetchers.moneycontrol import fetch_moneycontrol
from related_fetcher.fetchers.economictimes import fetch_economictimes
from related_fetcher.fetchers.financialexpress import fetch_financialexpress
from related_fetcher.fetchers.reuters import fetch_reuters
from related_fetcher.fetchers.cnbc import fetch_cnbc
from related_fetcher.fetchers.rbi import fetch_rbi
from related_fetcher.fetchers.sebi import fetch_sebi
from related_fetcher.fetchers.twitter import fetch_twitter
from related_fetcher.fetchers.market import fetch_market_data
from related_fetcher.fetchers.gnews import fetch_gnews
from related_fetcher.fetchers.newsdata import fetch_newsdata
from related_fetcher.fetchers.newsapi import fetch_newsapi
from related_fetcher.fetchers.worldnews import fetch_worldnews
from related_fetcher.fetchers.google_news import fetch_google_news

app = FastAPI(title="StreamPulse Related Info Fetcher")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/fetch_related")
def fetch_related(headline: str, keywords: str = None, is_business: bool = None):
    """
    Fetch related articles based on headline and/or keywords
    
    Args:
        headline: Original news headline
        keywords: Comma-separated keywords from keyword_extractor (optional, improves search)
        is_business: Whether this is business/finance news (optional, auto-detected if not provided)
    """
    results = []
    
    # Use keywords if provided, otherwise use headline
    # Keywords from keyword_extractor give better search results
    search_query = keywords if keywords else headline
    
    print(f"📰 Original headline: {headline}")
    if keywords:
        print(f"🔑 Using keywords: {keywords}")
    else:
        print(f"⚠️  No keywords provided, using full headline")
    
    # Auto-detect if business news if not specified
    if is_business is None:
        business_keywords = {'bank', 'stock', 'shares', 'market', 'profit', 'revenue', 'earnings', 
                            'quarter', 'financial', 'investment', 'trading', 'equity', 'dividend',
                            'ipo', 'merger', 'acquisition', 'nifty', 'sensex', 'bse', 'nse'}
        text_to_check = (keywords if keywords else headline).lower()
        is_business = any(keyword in text_to_check for keyword in business_keywords)
    
    # Choose fetchers based on news type
    if is_business:
        # For business news: use all financial sources + general news APIs
        fetchers = [
            fetch_google_news,  # Google News via SerpAPI - most comprehensive
            fetch_gnews,  # GNews API - fast and reliable
            fetch_newsdata,  # NewsData.io API
            fetch_newsapi,  # NewsAPI - India focused
            fetch_worldnews,  # World News API - India focused
            fetch_moneycontrol,
            fetch_financialexpress,
            fetch_economictimes,
            fetch_rbi,
            fetch_sebi,
            fetch_reuters,
            fetch_cnbc,
        ]
    else:
        # For non-business news: use general news sources
        # Skip finance-specific sites (RBI, SEBI, Moneycontrol tags)
        # But keep general news sites (Reuters, CNBC have general news sections)
        fetchers = [
            fetch_google_news,  # Google News via SerpAPI - most comprehensive
            fetch_gnews,  # GNews API - general news
            fetch_newsdata,  # NewsData.io API - general news
            fetch_newsapi,  # NewsAPI - India general news
            fetch_worldnews,  # World News API - India general news
            fetch_reuters,  # Reuters has general news
            fetch_cnbc,  # CNBC has general news
        ]
    
    print(f"🔍 Search query: {search_query}")
    print(f"📰 News type: {'Business/Finance' if is_business else 'General'}")
    print(f"🎯 Using {len(fetchers)} sources")
    
    # Fetch from all sources in parallel using the search query (keywords or headline)
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetcher, search_query): fetcher for fetcher in fetchers}
        for future in as_completed(futures):
            fetcher_name = futures[future].__name__
            try:
                result = future.result(timeout=5)
                if result:
                    results += result
                    print(f"✓ {fetcher_name}: {len(result)} results")
                else:
                    print(f"✗ {fetcher_name}: No results")
            except TimeoutError:
                print(f"✗ {fetcher_name}: TIMEOUT")
            except Exception as e:
                print(f"✗ {fetcher_name}: ERROR - {str(e)[:100]}")
    
    # Market data (quick lookup) - use keywords if available for better symbol detection
    try:
        market = fetch_market_data(search_query)
    except Exception as e:
        print(f"✗ fetch_market_data: ERROR - {e}")
        market = []

    return {
        "headline": headline,
        "keywords_used": keywords,
        "search_query": search_query,
        "related_news": results,
        "market": market
    }