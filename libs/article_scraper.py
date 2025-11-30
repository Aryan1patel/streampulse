"""
Article content scraper for extracting full text from news URLs
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional
import re

def clean_text(text: str) -> str:
    """Clean extracted text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,;!?-]', '', text)
    return text.strip()

def scrape_moneycontrol(url: str) -> Optional[str]:
    """Scrape article content from Moneycontrol"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Moneycontrol article content is in div with class 'content_wrapper'
        article_div = soup.find('div', class_='content_wrapper')
        if not article_div:
            article_div = soup.find('div', class_='article_content')
        
        if article_div:
            paragraphs = article_div.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs])
            return clean_text(content)
        
        return None
    except Exception as e:
        print(f"Error scraping Moneycontrol: {e}")
        return None

def scrape_economictimes(url: str) -> Optional[str]:
    """Scrape article content from Economic Times"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ET uses 'artText' class
        article_div = soup.find('div', class_='artText')
        if article_div:
            paragraphs = article_div.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs])
            return clean_text(content)
        
        return None
    except Exception as e:
        print(f"Error scraping Economic Times: {e}")
        return None

def scrape_livemint(url: str) -> Optional[str]:
    """Scrape article content from Livemint"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Livemint uses article tag
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs])
            return clean_text(content)
        
        return None
    except Exception as e:
        print(f"Error scraping Livemint: {e}")
        return None

def scrape_generic(url: str) -> Optional[str]:
    """Generic scraper for other news sites"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try common article containers
        article = soup.find('article') or soup.find('div', class_=re.compile(r'article|content|story'))
        
        if article:
            paragraphs = article.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs if len(p.get_text()) > 50])
            return clean_text(content)
        
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_article(url: str, source: str = None) -> Optional[str]:
    """
    Scrape article content based on source
    
    Args:
        url: Article URL
        source: Source name (e.g., 'Moneycontrol', 'Economic Times')
        
    Returns:
        Full article content or None if failed
    """
    if not url:
        return None
    
    url_lower = url.lower()
    
    # Route to specific scraper based on URL or source
    if 'moneycontrol' in url_lower or (source and 'moneycontrol' in source.lower()):
        return scrape_moneycontrol(url)
    elif 'economictimes' in url_lower or (source and 'economic times' in source.lower()):
        return scrape_economictimes(url)
    elif 'livemint' in url_lower or (source and 'livemint' in source.lower()):
        return scrape_livemint(url)
    else:
        return scrape_generic(url)
