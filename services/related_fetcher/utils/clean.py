import re
from bs4 import BeautifulSoup

BAD_KEYWORDS = [
    "bollywood", "actor", "actress", "cricket", "wedding",
    "marriage", "tv show", "trailer", "film", "series", "entertainment"
]

# Generic navigation/category titles to filter out
GENERIC_TITLES = [
    "stock insights", "markets", "ipo news", "personal finance", "gold pulse",
    "market news", "top stories", "latest news", "breaking news", "trending",
    "more news", "related articles", "read more", "click here", "view all",
    "home", "about", "contact", "privacy policy", "terms", "subscribe"
]

def clean_html(html):
    try:
        return BeautifulSoup(html, "lxml").get_text(" ", strip=True)
    except:
        return html

def clean_text(text):
    if not text: return ""

    text = clean_html(text)
    text = re.sub(r"[^\w\s.,:%()$₹+-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def is_irrelevant(t):
    t = t.lower()
    # Filter bad keywords
    if any(bad in t for bad in BAD_KEYWORDS):
        return True
    # Filter generic navigation titles
    if any(generic == t for generic in GENERIC_TITLES):
        return True
    # Filter very short titles (likely navigation items)
    if len(t) < 20:
        return True
    return False

def is_relevant_to_query(title, query):
    """Check if article title is relevant to the search query"""
    if not query or not title:
        return True  # Default to true if no query provided
    
    title_lower = title.lower()
    query_lower = query.lower()
    
    # Extract important keywords from query (words > 3 chars, skip common words)
    stop_words = {'the', 'and', 'for', 'with', 'from', 'that', 'this', 'after', 'news', 'says', 'today'}
    query_words = [w for w in re.findall(r'\b\w+\b', query_lower) if len(w) > 3 and w not in stop_words]
    
    if not query_words:
        return True
    
    # Check if at least 30% of query keywords appear in title
    # This allows for partial matches but filters out completely irrelevant content
    matches = sum(1 for word in query_words if word in title_lower)
    relevance_ratio = matches / len(query_words)
    
    return relevance_ratio >= 0.3  # At least 30% of keywords must match

def normalize_output(item, query=None):
    item["title"] = clean_text(item.get("title", ""))

    if is_irrelevant(item["title"]):
        return None
    
    # Check relevance to query if provided
    if query and not is_relevant_to_query(item["title"], query):
        return None

    return item