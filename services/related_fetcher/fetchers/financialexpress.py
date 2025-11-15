from related_fetcher.utils.request import safe_get
from related_fetcher.utils.clean import clean_text, normalize_output
from bs4 import BeautifulSoup

def fetch_financialexpress(query):
    url = f"https://www.financialexpress.com/?s={query.replace(' ', '+')}"
    html = safe_get(url)
    if not html: return []

    soup = BeautifulSoup(html, "lxml")
    out = []

    for h2 in soup.select("h2 a"):
        title = clean_text(h2.get_text())
        link = h2["href"]

        item = normalize_output({
            "source": "FinancialExpress",
            "title": title,
            "link": link
        })

        if item: out.append(item)

    return out