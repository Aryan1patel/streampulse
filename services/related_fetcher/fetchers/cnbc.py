from related_fetcher.utils.request import safe_get
from related_fetcher.utils.clean import clean_text, normalize_output
from bs4 import BeautifulSoup

def fetch_cnbc(query):
    url = f"https://www.cnbc.com/search/?query={query.replace(' ', '+')}"
    html = safe_get(url)
    if not html: return []

    soup = BeautifulSoup(html, "lxml")
    out = []

    for a in soup.select("a.Card-title"):
        title = clean_text(a.get_text())
        link = a["href"]

        item = normalize_output({
            "source": "CNBC",
            "title": title,
            "link": link
        })

        if item: out.append(item)

    return out