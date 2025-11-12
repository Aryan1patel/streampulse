# services/ingestors/trending_ingestor/main.py

import time
import os

from libs.kafka_producer import create_producer, send_kafka
from trending_ingestor.filters import is_market_impacting
from trending_ingestor.scraping import (
    # fetch_moneycontrol_api,  # API down
    # fetch_gnews_api,  # API quota exceeded
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
# ALL NEWS SOURCES (India + Global)
# ------------------------------------------------------
SOURCES = [
    # ❌ Removed: fetch_gnews_api,  # 403 - API quota exceeded
    # ❌ Removed: fetch_moneycontrol_api,  # 500 - API server down
    fetch_financial_express,
    fetch_livemint_latest,
    fetch_times_of_india_trending,
    fetch_india_today_breaking,
    fetch_hindustan_times_latest,
    fetch_reuters_hot,
    fetch_cnbc_popular,
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
        print("⚡ Fetching trending news...")

        collected_items = []

        # ---- Fetch from all sources ----
        for fn in SOURCES:
            try:
                items = fn()
                if items:
                    collected_items.extend(items)
            except Exception as e:
                print(f"❌ Source failed: {fn.__name__} -> {e}")

        # ---- Normalize and dedupe ----
        normalized = [normalize_item(i) for i in collected_items]
        unique_items = dedupe_items(normalized, seen_titles)

        # ---- Filter for ONLY strong market-impact news ----
        final_items = [item for item in unique_items if is_market_impacting(item["title"])]

        # ---- Publish to Kafka ----
        for item in final_items:
            try:
                send_kafka(producer, TOPIC, item)
                print("➡ TRENDING:", item.get("title"))
            except Exception as e:
                print("❌ Kafka send failed:", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()