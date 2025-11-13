# normalizer/main.py

import os
import time
import signal
from libs.kafka_consumer import consume        # <-- correct import
from libs.kafka_producer import create_producer, send_kafka
from clean_text import normalize_item
from dedupe import SeenStore

BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP', 'redpanda:9092')
CONSUMER_TOPIC = os.getenv('CONSUMER_TOPIC', 'trending_raw')
PRODUCER_TOPIC = os.getenv('PRODUCER_TOPIC', 'trending_clean')

running = True

def stop(signum, frame):
    global running
    running = False

signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)

def main():
    print("🚀 Starting normalizer...")
    print(f"📥 Listening to topic: {CONSUMER_TOPIC}")
    print(f"📤 Publishing to topic: {PRODUCER_TOPIC}")

    producer = create_producer(BOOTSTRAP)
    seen = SeenStore(ttl=3600)
    
    print("✅ Normalizer ready, waiting for messages...")

    # consume() gives you each message
    for msg in consume(CONSUMER_TOPIC):
        if not running:
            break

        try:
            normalized = normalize_item(msg)
            item_id = normalized["id"]

            if seen.already_seen(item_id):
                continue

            send_kafka(producer, PRODUCER_TOPIC, normalized)
            print("➡ normalized ->", normalized["title"])

        except Exception as e:
            print("❌ normalizer error:", e)
            time.sleep(1)

    print("Normalizer shutting down.")

if __name__ == "__main__":
    main()