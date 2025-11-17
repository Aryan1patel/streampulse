FROM python:3.10-slim

WORKDIR /app

COPY services/api_gateway/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/api_gateway /app/services/api_gateway

ENV PYTHONPATH="/app"

CMD ["uvicorn", "services.api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]