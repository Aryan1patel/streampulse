import re
from bs4 import BeautifulSoup

BAD_KEYWORDS = [
    "bollywood", "actor", "actress", "cricket", "wedding",
    "marriage", "tv show", "trailer", "film", "series", "entertainment"
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
    return any(bad in t for bad in BAD_KEYWORDS)

def normalize_output(item):
    item["title"] = clean_text(item.get("title", ""))

    if is_irrelevant(item["title"]):
        return None

    return item