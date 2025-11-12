import time
import feedparser
from libs.kafka_producer import create_producer, send_kafka
from rss_sources import RSS_LATEST
import os

\

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "news_raw")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 20))


def normalize(entry, src):
    return {
        "source": src,
        "title": entry.get("title"),
        "body": entry.get("summary"),
        "link": entry.get("link"),
        "timestamp": entry.get("published"),
        "raw_type": "rss"
    }


def run():
    print("Starting ingestor...")

    # create producer with retry logic
    producer = create_producer(BOOTSTRAP)

    while True:
        print("Fetching RSS feeds...")
        for rss in RSS_LATEST:
            feed = feedparser.parse(rss)
            for entry in feed.entries[:5]:
                doc = normalize(entry, rss)
                send_kafka(producer, TOPIC, doc)
                print("➡ sent:", doc["title"])
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()