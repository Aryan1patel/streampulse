kafka-topics --create --topic news_raw --bootstrap-server kafka:9092
kafka-topics --create --topic news_cleaned --bootstrap-server kafka:9092
kafka-topics --create --topic threads_ready --bootstrap-server kafka:9092