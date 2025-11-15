from related_fetcher.utils.request import safe_get
from related_fetcher.utils.clean import normalize_output
from bs4 import BeautifulSoup

def fetch_rbi(query):
    url = "https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"
    html = safe_get(url)
    if not html: return []

    soup = BeautifulSoup(html, "lxml")
    out = []

    for tr in soup.select("table tr"):
        a = tr.find("a")
        if not a: continue

        title = a.get_text().strip()
        if query.lower() not in title.lower(): continue

        link = "https://rbi.org.in" + a["href"]

        item = normalize_output({
            "source": "RBI",
            "title": title,
            "link": link
        })

        if item: out.append(item)

    return out