FROM python:3.10-slim

WORKDIR /app

COPY services/keyword_extractor/requirements.txt .
RUN pip install --default-timeout=100 --retries 5 -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

COPY services/keyword_extractor /app/keyword_extractor
COPY libs /app/libs
COPY data /app/data

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "keyword_extractor.main:app", "--host", "0.0.0.0", "--port", "7002"]