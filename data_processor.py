import pandas as pd

class DataProcessor:
    def __init__(self, window_size=20):
        # Stores historical data for each stock using a dictionary of DataFrames
        self.stock_data_history = {} 
        self.window_size = window_size # For moving average calculation (e.g., 20-period SMA)

    def process_data(self, raw_data):
        """
        Processes raw stock data, adds it to history, and calculates technical indicators.
        """
        processed_stocks = {}
        for symbol, data in raw_data.items():
            if data is None:
                continue

            # Convert timestamp to datetime object immediately upon ingestion
            try:
                # Handle different timestamp formats from APIs
                timestamp_dt = pd.to_datetime(data['timestamp'])
            except ValueError:
                print(f"Warning: Could not parse timestamp '{data['timestamp']}' for {symbol}. Skipping.")
                continue

            # Initialize history for a new stock
            if symbol not in self.stock_data_history:
                self.stock_data_history[symbol] = pd.DataFrame(columns=['timestamp', 'close', 'volume', 'open', 'high', 'low'])
                self.stock_data_history[symbol].set_index('timestamp', inplace=True) # Set timestamp as index

            # Create a new row as a DataFrame
            new_row_data = {
                'open': data['open'],
                'high': data['high'],
                'low': data['low'],
                'close': data['close'],
                'volume': data['volume']
            }
            new_row_df = pd.DataFrame([new_row_data], index=[timestamp_dt])

            # Append the new row and keep only the most recent data
            # Ensure no duplicate timestamps (if API sends same data twice)
            if timestamp_dt in self.stock_data_history[symbol].index:
                # If timestamp exists, update it (or skip if data hasn't changed)
                # For simplicity, we'll replace the row if timestamp exists
                self.stock_data_history[symbol].loc[timestamp_dt] = new_row_data
            else:
                self.stock_data_history[symbol] = pd.concat([self.stock_data_history[symbol], new_row_df])
            
            # Keep only enough data for current calculations plus a buffer
            # We need window_size points for SMA. Keep slightly more for robustness.
            self.stock_data_history[symbol] = self.stock_data_history[symbol].tail(self.window_size * 3) 
            
            # Sort by index (timestamp) to ensure correct calculation
            self.stock_data_history[symbol].sort_index(inplace=True)

            df = self.stock_data_history[symbol]

            # Ensure we have enough data points to calculate moving averages
            if len(df) >= self.window_size:
                df['SMA'] = df['close'].rolling(window=self.window_size, min_periods=1).mean()
                df['StdDev'] = df['close'].rolling(window=self.window_size, min_periods=1).std()
                
                # Calculate percentage change from previous close
                # Use .iloc[-1] to get the latest close and .iloc[-2] for the previous one
                current_close = df['close'].iloc[-1]
                previous_close = df['close'].iloc[-2] if len(df) >= 2 else df['close'].iloc[-1]
                df['PriceChange'] = (current_close - previous_close)
                df['PercentageChange'] = (df['PriceChange'] / previous_close) if previous_close != 0 else 0
                
                # Volume change (percentage change from previous volume)
                current_volume = df['volume'].iloc[-1]
                previous_volume = df['volume'].iloc[-2] if len(df) >= 2 else df['volume'].iloc[-1]
                df['VolumeChange'] = (current_volume - previous_volume)
                df['PercentageVolumeChange'] = (df['VolumeChange'] / previous_volume) if previous_volume != 0 else 0

                # Get the latest processed data point with calculated indicators
                latest_processed = df.iloc[-1].to_dict()
                latest_processed['symbol'] = symbol
                processed_stocks[symbol] = latest_processed
            else:
                print(f"Not enough data for {symbol} to calculate moving averages (need at least {self.window_size} points). Currently have {len(df)}.")
                # You might return partial data or skip if not enough for anomaly detection
        return processed_stocks

# For testing this module independently
if __name__ == "__main__":
    dp = DataProcessor(window_size=5)
    
    # Simulate receiving data over time
    sample_data_stream = [
        {"symbol": "IBM", "timestamp": "2025-07-08 10:00:00", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000},
        {"symbol": "MSFT", "timestamp": "2025-07-08 10:00:00", "open": 200.0, "high": 202.0, "low": 199.0, "close": 201.5, "volume": 2000},
        
        {"symbol": "IBM", "timestamp": "2025-07-08 10:01:00", "open": 100.5, "high": 101.5, "low": 99.5, "close": 101.0, "volume": 1100},
        {"symbol": "MSFT", "timestamp": "2025-07-08 10:01:00", "open": 201.5, "high": 203.0, "low": 200.0, "close": 202.5, "volume": 2100},

        {"symbol": "IBM", "timestamp": "2025-07-08 10:02:00", "open": 101.0, "high": 102.0, "low": 100.0, "close": 101.2, "volume": 1200},
        {"symbol": "MSFT", "timestamp": "2025-07-08 10:02:00", "open": 202.5, "high": 204.0, "low": 201.0, "close": 203.5, "volume": 2200},

        {"symbol": "IBM", "timestamp": "2025-07-08 10:03:00", "open": 101.2, "high": 102.5, "low": 100.5, "close": 104.0, "volume": 3000}, # Potential anomaly
        {"symbol": "MSFT", "timestamp": "2025-07-08 10:03:00", "open": 203.5, "high": 205.0, "low": 202.0, "close": 204.0, "volume": 2300},

        {"symbol": "IBM", "timestamp": "2025-07-08 10:04:00", "open": 104.0, "high": 105.0, "low": 103.0, "close": 104.1, "volume": 1500},
        {"symbol": "MSFT", "timestamp": "2025-07-08 10:04:00", "open": 204.0, "high": 205.5, "low": 203.0, "close": 204.5, "volume": 2400},

        {"symbol": "IBM", "timestamp": "2025-07-08 10:05:00", "open": 104.1, "high": 106.0, "low": 103.5, "close": 107.0, "volume": 4500}, # Another potential anomaly
        {"symbol": "MSFT", "timestamp": "2025-07-08 10:05:00", "open": 204.5, "high": 206.0, "low": 203.5, "close": 205.0, "volume": 2500},
    ]

    print("--- Simulating data stream ---")
    current_raw_data = {}
    for i, data_point in enumerate(sample_data_stream):
        symbol = data_point['symbol']
        current_raw_data[symbol] = data_point # Update with latest for each symbol

        if (i + 1) % len(set([d['symbol'] for d in sample_data_stream])) == 0: # Process after all symbols get new data
            print(f"\n--- Processing step {i//len(set([d['symbol'] for d in sample_data_stream])) + 1} ---")
            processed = dp.process_data(current_raw_data)
            for sym, proc_data in processed.items():
                print(f"{sym}: Close={proc_data['close']:.2f}, SMA={proc_data.get('SMA', 'N/A'):.2f}, StdDev={proc_data.get('StdDev', 'N/A'):.2f}, %Change={proc_data.get('PercentageChange', 'N/A'):.2%}")
            current_raw_data = {} # Reset for next batch