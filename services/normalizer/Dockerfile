FROM python:3.10-slim

WORKDIR /app

COPY services/normalizer/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY libs /app/libs
COPY services/normalizer /app/normalizer

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

CMD ["python", "normalizer/main.py"]