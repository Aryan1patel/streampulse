#!/bin/bash
# Startup script: Train model if not exists, then start server

MODEL_PATH="/app/deep_dive_worker/lightgbm_model.txt"

# Skip training if not present - local fallbacks are used in ml_model.py
echo "🚀 Skipping startup training (using built-in models/fallbacks)..."

echo "✅ Starting deep_dive_worker service..."
python -m uvicorn deep_dive_worker.main:app --host 0.0.0.0 --port 7004
