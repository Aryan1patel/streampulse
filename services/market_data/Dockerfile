FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/market_data/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/market_data /app/market_data

# Expose port
EXPOSE 7003

# Run the service
CMD ["uvicorn", "market_data.main:app", "--host", "0.0.0.0", "--port", "7003"]
