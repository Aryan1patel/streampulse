# services/ingestors/news_ingestor/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Install requirements
COPY services/ingestors/news_ingestor/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy service code
COPY services/ingestors/news_ingestor /app/news_ingestor

# Copy shared libs
COPY libs /app/libs

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

ENV KAFKA_BOOTSTRAP="redpanda:9092"
ENV KAFKA_TOPIC="news_raw"
ENV POLL_INTERVAL="20"

CMD ["python", "news_ingestor/main.py"]