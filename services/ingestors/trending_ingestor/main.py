# services/ingestors/trending_ingestor/main.py

import time
import os

from libs.kafka_producer import create_producer, send_kafka
from trending_ingestor.filters import is_market_impacting
from trending_ingestor.scraping import (
    fetch_gnews_trending,
    fetch_newsdata_trending,
    fetch_newsapi_trending,
    fetch_worldnews_trending,
    fetch_financial_express,
    fetch_livemint_latest,
    fetch_times_of_india_trending,
    fetch_india_today_breaking,
    fetch_hindustan_times_latest,
    fetch_reuters_hot,
    fetch_cnbc_popular,
)
from trending_ingestor.utils import dedupe_items, normalize_item


# ------------------------------------------------------
# ENV VARS
# ------------------------------------------------------
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "trending_raw")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))


# ------------------------------------------------------
# ALL NEWS SOURCES (India-focused)
# ------------------------------------------------------
SOURCES = [
    # 🟢 News APIs - Fast & Reliable (India-specific)
    fetch_newsapi_trending,  # NewsAPI.org - 100 requests/day
    fetch_worldnews_trending,  # WorldNewsAPI - India top news
    fetch_gnews_trending,
    fetch_newsdata_trending,
    # 🟢 Web Scraping - Indian Sources (Priority)
    fetch_financial_express,
    fetch_livemint_latest,
    fetch_times_of_india_trending,
    fetch_india_today_breaking,
    fetch_hindustan_times_latest,
    # Moneycontrol - Indian business news (commented out, no longer available in scraping.py)
    # Global sources - lower priority, may have US news
    # fetch_reuters_hot,
    # fetch_cnbc_popular,
]


# ------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------
def run():
    print("🔥 Starting Trending Ingestor...")

    producer = create_producer(BOOTSTRAP)
    print("✔ Kafka producer connected!")

    # store titles already sent (avoid duplicates)
    seen_titles = set()

    while True:
        print("\n⚡ Fetching trending news...")

        collected_items = []
        source_stats = {}  # Track count per source

        # ---- Fetch from all sources ----
        for fn in SOURCES:
            try:
                items = fn()
                if items:
                    collected_items.extend(items)
                    source_stats[fn.__name__] = len(items)
                else:
                    source_stats[fn.__name__] = 0
            except Exception as e:
                print(f"❌ Source failed: {fn.__name__} -> {e}")
                source_stats[fn.__name__] = 0

        # ---- Print source statistics ----
        print("\n📊 Source Statistics:")
        for source_name, count in sorted(source_stats.items(), key=lambda x: -x[1]):
            print(f"   {source_name}: {count} articles")
        print(f"   TOTAL COLLECTED: {len(collected_items)}")

        # ---- Normalize and dedupe ----
        normalized = [normalize_item(i) for i in collected_items]
        unique_items = dedupe_items(normalized, seen_titles)
        print(f"   After dedup: {len(unique_items)}")

        # ---- Filter for ONLY strong market-impact news ----
        final_items = [item for item in unique_items if is_market_impacting(item["title"])]
        print(f"   After market filter: {len(final_items)}")

        # ---- Publish to Kafka ----
        sent_count = 0
        for item in final_items:
            try:
                send_kafka(producer, TOPIC, item)
                print("➡ TRENDING:", item.get("title"))
                sent_count += 1
            except Exception as e:
                print("❌ Kafka send failed:", e)
        
        print(f"✅ Sent {sent_count} articles to Kafka\n")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()