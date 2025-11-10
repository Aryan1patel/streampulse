from kafka import KafkaConsumer
import json

def consume(topic):
    consumer = KafkaConsumer(
    topic,
    bootstrap_servers="redpanda:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id=None,                     # <-- disable consumer group
    auto_offset_reset="earliest",      # <-- read from beginning
    enable_auto_commit=False           # <-- don't store offsets
)

    for msg in consumer:
        yield msg.value