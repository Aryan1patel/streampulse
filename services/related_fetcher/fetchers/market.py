import yfinance as yf

def fetch_market_data(query):
    # Example: Always return NIFTY + S&P500
    nifty = yf.Ticker("^NSEI").history("5d").to_dict()
    sp = yf.Ticker("^GSPC").history("5d").to_dict()
    return {
        "nifty": nifty,
        "sp500": sp
    }