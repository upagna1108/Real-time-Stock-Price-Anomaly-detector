import os

# API Keys
# It's highly recommended to store API keys in a .env file and load them
# via python-dotenv, rather than hardcoding them here.
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# Stocks to monitor (add/remove as desired)
STOCKS = ["IBM"] # Example stocks

# Anomaly thresholds
PRICE_CHANGE_THRESHOLD = 0.03  # 3% change within the interval
STD_DEV_MULTIPLIER = 2.5       # 2.5 standard deviations from SMA
# You can add more thresholds here, e.g., for volume spikes