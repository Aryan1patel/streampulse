import subprocess
import json
from related_fetcher.utils.clean import clean_text, normalize_output

def fetch_twitter(query, limit=20):
    try:
        cmd = f"snscrape --jsonl twitter-search '{query} since:2025-11-10' | head -n {limit}"
        result = subprocess.check_output(cmd, shell=True).decode().split("\n")
    except:
        return []

    out = []

    for line in result:
        if not line.strip():
            continue

        obj = json.loads(line)
        text = clean_text(obj.get("content", ""))

        item = normalize_output({
            "source": "Twitter",
            "title": text,
            "link": obj.get("url")
        })

        if item: out.append(item)

    return out