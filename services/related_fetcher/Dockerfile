FROM python:3.10-slim

WORKDIR /app

COPY services/related_fetcher/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/related_fetcher /app/related_fetcher
COPY libs /app/libs

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "related_fetcher.main:app", "--host", "0.0.0.0", "--port", "7000"]