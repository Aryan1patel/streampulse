from related_fetcher.utils.request import safe_get
from related_fetcher.utils.clean import normalize_output
from bs4 import BeautifulSoup

def fetch_sebi(query):
    url = "https://www.sebi.gov.in/media/press-releases.html"
    html = safe_get(url)
    if not html: return []

    soup = BeautifulSoup(html, "lxml")
    out = []

    for h3 in soup.select("h3 a"):
        title = h3.get_text().strip()
        if query.lower() not in title.lower(): continue

        link = "https://www.sebi.gov.in" + h3["href"]

        item = normalize_output({
            "source": "SEBI",
            "title": title,
            "link": link
        })

        if item: out.append(item)

    return out