import requests
import time
from config import ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY # Import from config

class APIClient:
    def __init__(self, api_source="alpha_vantage"):
        self.api_source = api_source
        if self.api_source == "alpha_vantage":
            self.api_key = ALPHA_VANTAGE_API_KEY
            self.base_url = "https://www.alphavantage.co/query"
            self.rate_limit_delay = 15 # Alpha Vantage free tier is 5 calls per minute
        elif self.api_source == "finnhub":
            self.api_key = FINNHUB_API_KEY
            self.base_url = "https://finnhub.io/api/v1"
            self.rate_limit_delay = 1 # Finnhub free tier is 30 calls/sec for some endpoints
        else:
            raise ValueError("Unsupported API source. Choose 'alpha_vantage' or 'finnhub'.")

    def get_stock_data(self, symbol, interval='1min'):
        if not self.api_key:
            print(f"Error: {self.api_source} API key not set. Please check your .env file.")
            return None

        data = None
        if self.api_source == "alpha_vantage":
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "apikey": self.api_key,
                "outputsize": "compact" # Get only the most recent 100 data points
            }
            try:
                r = requests.get(self.base_url, params=params)
                r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                raw_data = r.json()
                
                if "Time Series (1min)" in raw_data:
                    # Get the latest data point
                    latest_timestamp = list(raw_data["Time Series (1min)"].keys())[0]
                    latest_data = raw_data["Time Series (1min)"][latest_timestamp]
                    data = {
                        "symbol": symbol,
                        "timestamp": latest_timestamp,
                        "open": float(latest_data["1. open"]),
                        "high": float(latest_data["2. high"]),
                        "low": float(latest_data["3. low"]),
                        "close": float(latest_data["4. close"]),
                        "volume": int(latest_data["5. volume"])
                    }
                elif "Error Message" in raw_data:
                    print(f"Alpha Vantage API Error for {symbol}: {raw_data['Error Message']}")
                elif "Note" in raw_data:
                     # This is often for rate limit warnings
                    print(f"Alpha Vantage API Note/Warning for {symbol}: {raw_data['Note']}")
                else:
                    print(f"Unexpected Alpha Vantage API response for {symbol}: {raw_data}")

            except requests.exceptions.RequestException as e:
                print(f"Alpha Vantage API request failed for {symbol}: {e}")
            except ValueError as e:
                print(f"Error parsing Alpha Vantage data for {symbol}: {e}")
        
        elif self.api_source == "finnhub":
            # Finnhub provides real-time quotes, not historical intraday like AV for free tier
            # For this project, a single quote might be enough if you want very real-time updates.
            # However, to calculate moving averages, you need a series of points.
            # Finnhub's free tier for intraday candles (like AV's 1min) is often limited.
            # Let's use a simple quote for real-time price, but note it won't support MAs directly from this endpoint.
            params = {
                "symbol": symbol,
                "token": self.api_key
            }
            try:
                r = requests.get(f"{self.base_url}/quote", params=params)
                r.raise_for_status()
                raw_data = r.json()
                if raw_data and raw_data.get('c'): # 'c' is current price
                    data = {
                        "symbol": symbol,
                        "timestamp": pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S'), # Finnhub quote lacks timestamp
                        "open": raw_data.get('o'),
                        "high": raw_data.get('h'),
                        "low": raw_data.get('l'),
                        "close": raw_data.get('c'),
                        "volume": raw_data.get('pc') # 'pc' is previous close, no volume in free quote
                    }
                else:
                    print(f"Finnhub API: No current price for {symbol} or unexpected response: {raw_data}")
            except requests.exceptions.RequestException as e:
                print(f"Finnhub API request failed for {symbol}: {e}")

        return data

    def fetch_stock_data_for_symbols(self, symbols):
        all_data = {}
        for symbol in symbols:
            data = self.get_stock_data(symbol)
            if data:
                all_data[symbol] = data
            # Respect rate limits
            time.sleep(self.rate_limit_delay)
        return all_data

# For testing this module independently
if __name__ == "__main__":
    import pandas as pd # Import here for local testing only
    from dotenv import load_dotenv
    load_dotenv() # Load API keys from .env

    # Test Alpha Vantage
    print("--- Testing Alpha Vantage ---")
    av_client = APIClient(api_source="alpha_vantage")
    data_av = av_client.fetch_stock_data_for_symbols(["IBM", "MSFT"])
    print(data_av)
    
    # Test Finnhub (Note: Finnhub free tier may not have 1min candles, only quotes)
    # The current implementation of get_stock_data for finnhub fetches a single quote.
    # To use it for MA calculations, you'd need a different finnhub endpoint or accumulate data points.
    print("\n--- Testing Finnhub (Quote Only) ---")
    finnhub_client = APIClient(api_source="finnhub")
    data_fh = finnhub_client.fetch_stock_data_for_symbols(["AAPL", "GOOGL"])
    print(data_fh)