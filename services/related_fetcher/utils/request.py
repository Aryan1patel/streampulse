import requests
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]

def safe_get(url, retries=2, json=False):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
    }

    for _ in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=6)
            if r.status_code == 200:
                return r.json() if json else r.text
        except:
            time.sleep(1)
    return None