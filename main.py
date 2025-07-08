import time
import schedule # pip install schedule
from dotenv import load_dotenv # pip install python-dotenv

# Import modules from your project
from config import STOCKS # Your list of stocks to monitor
from api_client import APIClient # Your API client
from data_processor import DataProcessor # Your data processor
from anomaly_detector import AnomalyDetector # Your anomaly detector
from alert_manager import AlertManager # Your alert manager

# Load environment variables (e.g., API keys) from a .env file
load_dotenv()

# --- Configuration ---
# Choose your API source: "alpha_vantage" or "finnhub"
# Note: Finnhub free tier usually provides quotes, not 1-min candles for MA.
# Alpha Vantage free tier provides 1-min candles but has stricter rate limits.
API_SOURCE = "alpha_vantage"
# How often to check for new data (in seconds).
# Be mindful of your chosen API's rate limits!
# Alpha Vantage: max 5 calls/minute -> minimum 12 seconds per call
# If monitoring multiple stocks with AV, adjust the total interval or per-stock delay.
# E.g., if you have 4 stocks and 15s delay per call, total is 60s per loop.
SCHEDULE_INTERVAL_SECONDS = 75 # Check every 60 seconds

# --- Initialize Modules ---
# Initialize API client with chosen source
api_client = APIClient(api_source=API_SOURCE) 
# Data processor (window_size for moving averages)
# A window size of 20 means it needs 20 data points to calculate a full SMA.
# If your interval is 1 minute, this means 20 minutes of data.
data_processor = DataProcessor(window_size=20) 
anomaly_detector = AnomalyDetector()
alert_manager = AlertManager()

def monitor_stocks():
    """
    Main monitoring function executed periodically by the scheduler.
    """
    print(f"\n[{time.ctime()}] --- Starting a new monitoring cycle ---")
    print(f"Fetching data for: {STOCKS} using {API_SOURCE}...")

    # 1. Fetch Raw Data
    raw_data = api_client.fetch_stock_data_for_symbols(STOCKS)
    if not raw_data:
        print("No raw data fetched. Skipping this cycle.")
        return

    # 2. Process and Validate Data
    processed_data = data_processor.process_data(raw_data)
    if not processed_data:
        print("No data processed (insufficient history?). Skipping anomaly detection.")
        return

    # 3. Detect Anomalies
    anomalies = anomaly_detector.detect_anomalies(processed_data)

    # 4. Generate Alerts
    if anomalies:
        print(f"Anomalies detected for this cycle ({len(anomalies)}):")
        for anomaly in anomalies:
            alert_manager.send_alert(anomaly)
    else:
        print("No anomalies detected in this cycle.")

    print(f"[{time.ctime()}] --- Monitoring cycle finished ---")


if __name__ == "__main__":
    print("------------------------------------------------")
    print("Real-time Stock Price Anomaly Detector Started")
    print("------------------------------------------------")
    print(f"Monitoring stocks: {STOCKS}")
    print(f"Data source: {API_SOURCE}")
    print(f"Checking every {SCHEDULE_INTERVAL_SECONDS} seconds.")
    print("Press Ctrl+C to stop the monitor.")

    # Schedule the monitoring function to run at the specified interval
    schedule.every(SCHEDULE_INTERVAL_SECONDS).seconds.do(monitor_stocks)

    # Initial run to fetch some data right away
    monitor_stocks() 

    # Keep the script running to allow the scheduler to work
    while True:
        try:
            schedule.run_pending()
            time.sleep(1) # Sleep briefly to avoid busy-waiting and consume CPU
        except KeyboardInterrupt:
            print("\nMonitor stopped by user (Ctrl+C). Exiting.")
            break
        except Exception as e:
            print(f"An unexpected error occurred in the main loop: {e}")
            print("Restarting monitoring after 5 seconds...")
            time.sleep(5) # Wait a bit before retrying the loop