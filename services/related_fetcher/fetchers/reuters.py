from related_fetcher.utils.request import safe_get
from related_fetcher.utils.clean import clean_text, normalize_output
from bs4 import BeautifulSoup

def fetch_reuters(query):
    url = f"https://www.reuters.com/site-search/?query={query.replace(' ', '+')}"
    html = safe_get(url)
    if not html: return []

    soup = BeautifulSoup(html, "lxml")
    out = []

    for a in soup.select("a.search-result-title"):
        title = clean_text(a.get_text())
        link = "https://www.reuters.com" + a["href"]

        item = normalize_output({
            "source": "Reuters",
            "title": title,
            "link": link
        })

        if item: out.append(item)

    return out