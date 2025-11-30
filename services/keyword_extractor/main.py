from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from keyword_extractor.extractor import extract_keywords, SYMBOLS
import sys
sys.path.append('/app')
from libs.article_scraper import scrape_article

app = FastAPI(title="StreamPulse Keyword Extractor")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/keywords")
def get_keywords(headline: str, url: str = None, source: str = None):
    """
    Extract keywords from headline and optionally from full article content
    
    Args:
        headline: Article headline (always used)
        url: Article URL (optional, for scraping full content)
        source: Source name (optional, helps scraper choose right parser)
    """
    article_content = None
    
    # If URL provided, try to scrape full article
    if url:
        try:
            article_content = scrape_article(url, source)
            print(f"✅ Scraped {len(article_content) if article_content else 0} chars from {source or url}")
        except Exception as e:
            print(f"❌ Failed to scrape article: {e}")
    
    # Extract keywords (will use article_content if available, otherwise just headline)
    all_keywords = extract_keywords(headline, content=article_content)
    
    # Separate companies from other keywords  
    # SYMBOLS keys are lowercase, so we need to check lowercase version
    companies = [kw for kw in all_keywords if kw.lower() in SYMBOLS]
    keywords = [kw for kw in all_keywords if kw.lower() not in SYMBOLS]
    
    return {
        "headline": headline,
        "url": url,
        "content_length": len(article_content) if article_content else 0,
        "keywords": {
            "all_keywords": all_keywords,
            "companies": companies,
            "keywords": keywords
        }
    }