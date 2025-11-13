import re
import hashlib
from datetime import datetime
from dateutil import parser as dparser

def clean_title(t: str) -> str:
    t = t or ""
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"[^\x20-\x7E]", "", t)   # remove emojis/non-ascii
    return t

def make_id(obj: dict) -> str:
    key = (obj.get("source", "") + obj.get("title", "") + obj.get("link", "")).encode()
    return hashlib.sha1(key).hexdigest()

CATEGORY_MAP = {
    "markets": ["nifty","sensex","ipo","fii","stocks","market","earnings"],
    "policy": ["rbi","sebi","budget","tariff","sanction","export","import"],
    "company": ["acquisition","fraud","scam","ceo","merger","layoff"],
    "tech": ["ai","chip","gpu","semiconductor","cyber"],
    "geopolitics": ["china","pakistan","russia","war","missile"],
}

def detect_category(title: str):
    t = title.lower()
    for cat, keywords in CATEGORY_MAP.items():
        if any(kw in t for kw in keywords):
            return cat
    return "other"

def parse_time(ts):
    if not ts:
        return datetime.utcnow().isoformat()
    try:
        return dparser.parse(ts).isoformat()
    except:
        return datetime.utcnow().isoformat()

def normalize_item(raw: dict):
    title = raw.get("title") or raw.get("raw_title") or ""
    link = raw.get("link") or ""
    source = raw.get("source") or "unknown"

    cleaned = clean_title(title)
    ts = parse_time(raw.get("fetched_at"))

    return {
        "id": make_id({"title": cleaned, "link": link, "source": source}),
        "title": cleaned,
        "raw_title": title,
        "link": link,
        "source": source,
        "timestamp": ts,
        "category": detect_category(cleaned),
    }