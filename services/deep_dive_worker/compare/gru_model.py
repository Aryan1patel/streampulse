import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GRUModel(nn.Module):
    def __init__(self, input_dim=5, hidden_dim=64, num_layers=2, output_dim=1):
        super(GRUModel, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        out, _ = self.gru(x, h0)
        out = self.fc(out[:, -1, :])
        return out

def predict_gru(price_history: List[float], features: Dict[str, Any]) -> List[float]:
    """
    Predict next 3 price moves using recursive forecasting
    """
    try:
        # Match Kaggle's 60-day window
        seq_len = 60
        
        if len(price_history) < seq_len:
            # Fallback for short history
            logger.warning(f"Short history for GRU: {len(price_history)} < {seq_len}. Using default 10-day fallback.")
            seq_len = 10
            if len(price_history) < 10:
                return [0.0, 0.0, 0.0]
            
        # Normalize prices
        prices = np.array(price_history)
        avg_price = np.mean(prices)
        std_price = np.std(prices) + 1e-6
        norm_prices = (prices - avg_price) / std_price
        
        # Static features
        sentiment_score = features.get('sentiment_score', 0.5)
        sentiment_dir = features.get('sentiment_direction', 0)
        volatility = features.get('volatility', 0.1)
        momentum = features.get('price_momentum', 0)
        sentiment_bias = features.get('sentiment_impact', 0) * 0.6
        
        # Load model architecture
        model = GRUModel(input_dim=5)
        model.eval()
        
        # Recursive prediction loop for 3 days
        predictions = []
        current_norm_prices = norm_prices.tolist()
        cumulative_move = 0.0
        
        for day in range(3):
            # ... prepare input ...
            seq = []
            test_window = current_norm_prices[-seq_len:]
            for p in test_window:
                seq.append([p, sentiment_score, sentiment_dir, volatility, momentum])
                
            input_tensor = torch.FloatTensor([seq]).reshape(1, seq_len, 5)
            with torch.no_grad():
                pred_raw = model(input_tensor).item()
                
            # Scale and add sentiment bias
            scaled_move = np.clip(pred_raw * 2.2, -3.0, 3.0)
            day_move = scaled_move + sentiment_bias
            
            # Update cumulative trajectory
            cumulative_move = ((1 + cumulative_move / 100.0) * (1 + day_move / 100.0) - 1) * 100
            predictions.append(round(float(cumulative_move), 2))
            
            # Update current_norm_prices for the next recursive step
            next_norm_price = current_norm_prices[-1] + (day_move / 100.0)
            current_norm_prices.append(next_norm_price)
            
        logger.info(f"GRU 3-Day Forecast: {predictions}")
        return predictions
        
    except Exception as e:
        logger.error(f"GRU prediction failed: {e}")
        return [0.0, 0.0, 0.0]
