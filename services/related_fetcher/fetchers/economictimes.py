from related_fetcher.utils.request import safe_get
from related_fetcher.utils.clean import clean_text, normalize_output
from bs4 import BeautifulSoup

def fetch_economictimes(query):
    url = f"https://economictimes.indiatimes.com/topic/{query.replace(' ', '-')}"
    html = safe_get(url)
    if not html: return []

    soup = BeautifulSoup(html, "lxml")
    out = []

    for div in soup.select(".content p"):  
        title = clean_text(div.get_text())
        link_elem = div.find_parent("a")
        link = link_elem["href"] if link_elem else None

        if not title or not link:
            continue

        item = normalize_output({
            "source": "EconomicTimes",
            "title": title,
            "link": "https://economictimes.indiatimes.com" + link
        }, query=query)

        if item: out.append(item)

    return out