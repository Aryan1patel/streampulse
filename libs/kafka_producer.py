from kafka import KafkaProducer
import json
import time

def create_producer(bootstrap):
    for attempt in range(15):
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                api_version=(0, 10),
                request_timeout_ms=5000,
                retry_backoff_ms=200
            )
            print("✔ Kafka producer connected!")
            return producer
        except Exception as e:
            print(f"❌ Kafka not ready, retrying ({attempt+1}/15)...")
            time.sleep(2)
    raise Exception("Kafka not available after retries")

def send_kafka(producer, topic, value):
    producer.send(topic, value)