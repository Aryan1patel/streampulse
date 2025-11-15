from fastapi import FastAPI
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

app = FastAPI(title="StreamPulse Related Info Fetcher")

@app.get("/fetch_related")
def fetch_related(headline: str):
    results = []
    
    # Fetch from all sources in parallel
    fetchers = [
        fetch_gnews,  # GNews API - fast and reliable
        fetch_newsdata,  # NewsData.io API
        fetch_moneycontrol,
        fetch_financialexpress,
        fetch_economictimes,
        fetch_rbi,
        fetch_sebi,
        fetch_reuters,
        fetch_cnbc,
    ]
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetcher, headline): fetcher for fetcher in fetchers}
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
    
    # Market data (quick lookup)
    try:
        market = fetch_market_data(headline)
    except Exception as e:
        print(f"✗ fetch_market_data: ERROR - {e}")
        market = []

    return {
        "headline": headline,
        "related_news": results,
        "market": market
    }