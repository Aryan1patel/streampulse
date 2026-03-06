from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

app = FastAPI(title="StreamPulse Market Data Service")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StockRequest(BaseModel):
    symbol: str
    days: Optional[int] = 30

class PricePoint(BaseModel):
    date: str
    price: float
    volume: int

@app.get("/")
def root():
    return {
        "service": "StreamPulse Market Data",
        "status": "running",
        "endpoints": [
            "/stock/{symbol}",
            "/price/{symbol}",
            "/volatility/{symbol}",
            "/batch"
        ]
    }

@app.get("/stock/{symbol}")
def get_stock_data(symbol: str, days: int = 60):
    """
    Get comprehensive stock data for a symbol
    
    Args:
        symbol: Stock symbol (e.g., RELIANCE.NS for Indian stocks)
        days: Number of days of historical data (default 30)
    
    Returns:
        {
            "symbol": str,
            "current_price": float,
            "price_change": float,
            "price_change_pct": float,
            "volatility_30d": float,
            "volume": int,
            "avg_volume": int,
            "beta": float,
            "price_history": [...],
            "returns_30d": float
        }
    """
    try:
        # Add .NS suffix for Indian stocks if not present
        if not any(suffix in symbol.upper() for suffix in ['.NS', '.BO', '.BSE']):
            ticker_symbol = f"{symbol.upper()}.NS"
        else:
            ticker_symbol = symbol.upper()
        
        ticker = yf.Ticker(ticker_symbol)
        
        # Get historical data
        hist = ticker.history(period=f"{days}d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")
        
        # Calculate metrics
        current_price = float(hist['Close'].iloc[-1])
        prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price * 100) if prev_price != 0 else 0
        
        # Volatility (standard deviation of returns)
        returns = hist['Close'].pct_change().dropna()
        volatility = float(returns.std() * np.sqrt(252) * 100)  # Annualized volatility %
        
        # Volume metrics
        current_volume = int(hist['Volume'].iloc[-1])
        avg_volume = int(hist['Volume'].mean())
        
        # Returns
        returns_30d = ((current_price - float(hist['Close'].iloc[0])) / float(hist['Close'].iloc[0]) * 100) if len(hist) > 0 else 0
        
        # Price history for charts
        price_history = [
            {
                "date": str(date.date()),
                "price": float(row['Close']),
                "volume": int(row['Volume'])
            }
            for date, row in hist.iterrows()
        ]
        
        # Beta (correlation with Nifty 50)
        beta = calculate_beta(ticker_symbol, days)
        
        return {
            "symbol": symbol.upper(),
            "ticker": ticker_symbol,
            "current_price": round(current_price, 2),
            "price_change": round(price_change, 2),
            "price_change_pct": round(price_change_pct, 2),
            "volatility_30d": round(volatility, 2),
            "volume": current_volume,
            "avg_volume": avg_volume,
            "beta": round(beta, 2),
            "returns_30d": round(returns_30d, 2),
            "price_history": price_history,  # Return full fetched history
            "data_points": len(hist)
        }
        
    except Exception as e:
        print(f"❌ Error fetching stock data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/price/{symbol}")
def get_current_price(symbol: str):
    """Get just the current price for a symbol"""
    try:
        if not any(suffix in symbol.upper() for suffix in ['.NS', '.BO']):
            ticker_symbol = f"{symbol.upper()}.NS"
        else:
            ticker_symbol = symbol.upper()
        
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        current_price = float(hist['Close'].iloc[-1])
        
        return {
            "symbol": symbol.upper(),
            "price": round(current_price, 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/volatility/{symbol}")
def get_volatility(symbol: str, days: int = 30):
    """Calculate volatility for a stock"""
    try:
        if not any(suffix in symbol.upper() for suffix in ['.NS', '.BO']):
            ticker_symbol = f"{symbol.upper()}.NS"
        else:
            ticker_symbol = symbol.upper()
        
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=f"{days}d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        returns = hist['Close'].pct_change().dropna()
        volatility = float(returns.std() * np.sqrt(252) * 100)
        
        return {
            "symbol": symbol.upper(),
            "volatility": round(volatility, 2),
            "period_days": days,
            "annualized": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch")
def get_batch_stocks(symbols: List[str], days: int = 30):
    """Get data for multiple stocks at once"""
    results = {}
    
    for symbol in symbols:
        try:
            data = get_stock_data(symbol, days)
            results[symbol] = data
        except Exception as e:
            results[symbol] = {"error": str(e)}
    
    return results


def calculate_beta(symbol: str, days: int = 30) -> float:
    """Calculate beta (correlation with Nifty 50)"""
    try:
        # Get stock data
        stock = yf.Ticker(symbol)
        stock_hist = stock.history(period=f"{days}d")
        
        # Get Nifty 50 data
        nifty = yf.Ticker("^NSEI")
        nifty_hist = nifty.history(period=f"{days}d")
        
        if stock_hist.empty or nifty_hist.empty:
            return 1.0  # Default beta
        
        # Calculate returns
        stock_returns = stock_hist['Close'].pct_change().dropna()
        nifty_returns = nifty_hist['Close'].pct_change().dropna()
        
        # Align dates
        aligned = pd.DataFrame({
            'stock': stock_returns,
            'nifty': nifty_returns
        }).dropna()
        
        if len(aligned) < 2:
            return 1.0
        
        # Calculate beta (covariance / variance)
        covariance = aligned['stock'].cov(aligned['nifty'])
        variance = aligned['nifty'].var()
        
        beta = covariance / variance if variance != 0 else 1.0
        
        return float(beta)
        
    except Exception as e:
        print(f"⚠️ Beta calculation error: {e}")
        return 1.0  # Default beta


@app.get("/index/{index_name}")
def get_index_data(index_name: str = "nifty", days: int = 30):
    """
    Get Indian market index data
    
    Args:
        index_name: nifty | sensex | banknifty
        days: Number of days of history
    """
    index_symbols = {
        'nifty': '^NSEI',
        'sensex': '^BSESN',
        'banknifty': '^NSEBANK'
    }
    
    symbol = index_symbols.get(index_name.lower())
    if not symbol:
        raise HTTPException(status_code=400, detail=f"Unknown index: {index_name}")
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"{days}d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data for {index_name}")
        
        current = float(hist['Close'].iloc[-1])
        prev = float(hist['Close'].iloc[0])
        change = ((current - prev) / prev * 100) if prev != 0 else 0
        
        return {
            "index": index_name.upper(),
            "current": round(current, 2),
            "change_pct": round(change, 2),
            "period_days": days,
            "history": [
                {
                    "date": str(date.date()),
                    "value": float(row['Close'])
                }
                for date, row in hist.iterrows()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
