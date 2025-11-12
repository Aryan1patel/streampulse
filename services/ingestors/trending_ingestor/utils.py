# services/ingestors/trending_ingestor/utils.py
import hashlib
from datetime import datetime
from dateutil import tz


def _id_for(item: dict) -> str:
    text = (item.get('title') or '') + '|' + (item.get('link') or '')
    return hashlib.sha1(text.encode('utf-8')).hexdigest()


def normalize_item(item: dict) -> dict:
    out = {}
    out['id'] = _id_for(item)
    out['source'] = item.get('source')
    out['title'] = (item.get('title') or '').strip()
    out['link'] = item.get('link')
    out['fetched_at'] = datetime.now(tz=tz.tzlocal()).isoformat()
    return out


def dedupe_items(items: list, seen_set: set, keep_max=50):
    unique = []
    for it in items:
        uid = _id_for(it)
        if uid in seen_set:
            continue
        seen_set.add(uid)
        unique.append(it)
    # keep seen_set bounded
    while len(seen_set) > keep_max * 10:
        try:
            seen_set.pop()
        except KeyError:
            break
    return unique