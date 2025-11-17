import json
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from datetime import datetime

from services.api_gateway.db import SessionLocal
from services.api_gateway.models import TrendingNews

KAFKA_BOOTSTRAP = "redpanda:9092"
TOPIC = "trending_clean"

def save_to_db(item):
    db: Session = SessionLocal()
    try:
        news = TrendingNews(
            id=item["id"],
            title=item["title"],
            link=item["link"],
            source=item["source"],
            fetched_at=datetime.fromisoformat(item.get("timestamp", item.get("fetched_at", datetime.utcnow().isoformat())))
        )
        db.merge(news)       # upsert
        db.commit()
    except Exception as e:
        print("DB ERROR:", e)
    finally:
        db.close()

def main():
    print("📥 trending_store listening...")

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        group_id="trending_store",
        auto_offset_reset="Earliest"
    )

    for message in consumer:
        item = message.value
        print("📝 storing:", item["title"])
        save_to_db(item)

if __name__ == "__main__":
    main()