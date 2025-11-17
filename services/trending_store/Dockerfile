FROM python:3.10-slim

WORKDIR /app

COPY services/trending_store/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/api_gateway /app/services/api_gateway
COPY services/trending_store /app/trending_store

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

CMD ["python", "trending_store/main.py"]