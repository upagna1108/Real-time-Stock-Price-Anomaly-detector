import pandas as pd
from config import PRICE_CHANGE_THRESHOLD, STD_DEV_MULTIPLIER

class AnomalyDetector:
    def detect_anomalies(self, processed_data):
        anomalies = []
        for symbol, data in processed_data.items():
            # Ensure required data points exist for calculations
            if not isinstance(data, dict): # Check if data is a dictionary
                print(f"Skipping anomaly detection for {symbol}: Invalid data format.")
                continue

            # Critical data points for anomaly detection
            current_close = data.get('close')
            sma = data.get('SMA')
            std_dev = data.get('StdDev')
            percentage_change = data.get('PercentageChange')
            timestamp = data.get('timestamp')

            if current_close is None or timestamp is None:
                print(f"Skipping anomaly detection for {symbol}: Missing critical price or timestamp data.")
                continue

            # Anomaly Rule 1: Sudden Price Change
            if percentage_change is not None and abs(percentage_change) >= PRICE_CHANGE_THRESHOLD:
                anomalies.append({
                    "symbol": symbol,
                    "type": "Sudden Price Change",
                    "description": f"Price changed by {percentage_change:.2%} in the last interval.",
                    "current_price": current_close,
                    "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(timestamp, pd.Timestamp) else str(timestamp)
                })

            # Anomaly Rule 2: Significant Deviation from Moving Average (Volatility Spike)
            if sma is not None and std_dev is not None and std_dev > 0: # Avoid division by zero
                deviation = abs(current_close - sma) / std_dev
                if deviation >= STD_DEV_MULTIPLIER:
                    anomalies.append({
                        "symbol": symbol,
                        "type": "Significant Deviation from SMA",
                        "description": f"Price is {deviation:.2f} standard deviations away from its {data.get('SMA_window_size', 'N/A')}-period SMA.",
                        "current_price": current_close,
                        "SMA": sma,
                        "StdDev": std_dev,
                        "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(timestamp, pd.Timestamp) else str(timestamp)
                    })
            elif std_dev == 0 and abs(current_close - sma) > 0: # Special case for no StdDev but price moved
                 anomalies.append({
                    "symbol": symbol,
                    "type": "Price Movement with Zero Volatility",
                    "description": "Price moved but standard deviation is zero (insufficient historical data or constant price).",
                    "current_price": current_close,
                    "SMA": sma,
                    "StdDev": std_dev,
                    "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(timestamp, pd.Timestamp) else str(timestamp)
                })

            # You can add more anomaly rules here (e.g., volume spikes)
            # if 'PercentageVolumeChange' in data and data['PercentageVolumeChange'] is not None:
            #     VOLUME_SPIKE_THRESHOLD = 2.0 # e.g., 200% increase
            #     if data['PercentageVolumeChange'] >= VOLUME_SPIKE_THRESHOLD:
            #         anomalies.append({
            #             "symbol": symbol,
            #             "type": "Volume Spike",
            #             "description": f"Volume increased by {data['PercentageVolumeChange']:.2%}.",
            #             "current_volume": data['volume'],
            #             "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(timestamp, pd.Timestamp) else str(timestamp)
            #         })

        return anomalies

# For testing this module independently
if __name__ == "__main__":
    ad = AnomalyDetector()
    # Create some dummy processed data that would trigger anomalies
    sample_processed_data = {
        "IBM": {
            "symbol": "IBM",
            "timestamp": pd.to_datetime("2025-07-08 10:05:00"),
            "close": 105.0,
            "volume": 1500,
            "SMA": 100.0,
            "StdDev": 1.5,
            "PriceChange": 5.0,
            "PercentageChange": 0.05 # 5% change, higher than threshold
        },
        "MSFT": {
            "symbol": "MSFT",
            "timestamp": pd.to_datetime("2025-07-08 10:05:00"),
            "close": 208.0, # This would be 2.5 std devs from 201 with 2.0 std dev
            "volume": 2200,
            "SMA": 201.0,
            "StdDev": 2.0, # Let's say normal std dev is 2.0
            "PriceChange": 7.0,
            "PercentageChange": 0.03 # Exactly 3% change
        },
        "GOOGL": { # No anomaly
            "symbol": "GOOGL",
            "timestamp": pd.to_datetime("2025-07-08 10:05:00"),
            "close": 150.0,
            "volume": 500,
            "SMA": 150.5,
            "StdDev": 0.2,
            "PriceChange": -0.5,
            "PercentageChange": -0.003
        }
    }
    anomalies = ad.detect_anomalies(sample_processed_data)
    print("Detected anomalies:", anomalies)