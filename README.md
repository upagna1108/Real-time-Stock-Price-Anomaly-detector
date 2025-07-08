# Real-time-Stock-Price-Anomaly-detector
Feature Engineering: Modify data_processor.py to calculate new features (price changes, rolling stats, etc.) from raw price data, turning it into a format suitable for ML.

Model Integration: In anomaly_detector.py, introduce IsolationForest (from scikit-learn). It will learn "normal" patterns from accumulated features.

Training & Prediction: anomaly_detector.py will first fit the model (train it) when enough historical features are gathered, then use it to predict if new data points are anomalous.

Orchestration: main.py will now call data_processor to get features and then pass them to anomaly_detector for ML-based anomaly detection.

Install scikit-learn (and upgrade pandas) in your venv.
