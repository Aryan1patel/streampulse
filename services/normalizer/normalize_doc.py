from bs4 import BeautifulSoup
import re

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def normalize(raw_doc):
    return {
        "doc_id": f"{raw_doc['source']}-{hash(raw_doc['title'])}",
        "source": raw_doc["source"],
        "timestamp": raw_doc["timestamp"],
        "headline": raw_doc["title"],
        "body": clean_html(raw_doc["body"]),
        "url": raw_doc["url"],
        "source_type": raw_doc["raw_type"],
    }