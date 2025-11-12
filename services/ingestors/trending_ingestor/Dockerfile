FROM python:3.10-slim

WORKDIR /app

# Install system deps for scraping
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev libxslt1-dev wget ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY services/ingestors/trending_ingestor/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy service code + shared libs
COPY services/ingestors/trending_ingestor /app/trending_ingestor
COPY libs /app/libs

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

ENV KAFKA_BOOTSTRAP="redpanda:9092"
ENV KAFKA_TOPIC="trending_raw"
ENV POLL_INTERVAL=30

CMD ["python", "trending_ingestor/main.py"]