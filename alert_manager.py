class AlertManager:
    def send_alert(self, anomaly_info):
        """Prints the anomaly details to the console and logs it."""
        print("\n" + "="*40)
        print("!!! REAL-TIME ANOMALY DETECTED !!!")
        print("="*40)
        for key, value in anomaly_info.items():
            print(f"- {key.replace('_', ' ').title()}: {value}")
        print("="*40 + "\n")

        self.log_alert(anomaly_info)

    def log_alert(self, anomaly_info):
        """Logs anomaly information to a file."""
        log_file_path = "anomaly_log.txt"
        try:
            with open(log_file_path, "a") as f:
                f.write(f"[{anomaly_info.get('timestamp', 'N/A')}] ANOMALY: Symbol={anomaly_info.get('symbol', 'N/A')}, Type='{anomaly_info.get('type', 'N/A')}', Description='{anomaly_info.get('description', 'N/A')}'\n")
            print(f"Anomaly logged to {log_file_path}")
        except IOError as e:
            print(f"Error writing to log file {log_file_path}: {e}")

    # You can add methods for other alert types (email, SMS, Discord, etc.)
    # def send_email_alert(self, anomaly_info):
    #     # Implement email sending logic here using smtplib
    #     pass

    # def send_slack_alert(self, anomaly_info):
    #     # Implement Slack webhook logic here
    #     pass

if __name__ == "__main__":
    am = AlertManager()
    sample_anomaly = {
        "symbol": "IBM",
        "type": "Sudden Price Change",
        "description": "Price changed by 4.50% in the last interval.",
        "current_price": 105.0,
        "timestamp": "2025-07-08 10:05:00"
    }
    am.send_alert(sample_anomaly)
    
    sample_anomaly_2 = {
        "symbol": "MSFT",
        "type": "Significant Deviation from SMA",
        "description": "Price is 3.12 standard deviations away from its 20-period SMA.",
        "current_price": 210.0,
        "SMA": 200.0,
        "StdDev": 3.2,
        "timestamp": "2025-07-08 10:06:00"
    }
    am.send_alert(sample_anomaly_2)