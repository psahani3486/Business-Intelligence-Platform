import logging
import pandas as pd
from sklearn.ensemble import IsolationForest
import mlflow
import numpy as np
from backend.database import execute_query

logger = logging.getLogger(__name__)

def train_anomaly_model(table_name: str, model_name: str, target_col: str = 'y', features: list = None, contamination: float = 0.05):
    """Trains an Isolation Forest for detecting anomalous days."""
    logger.info(f"Training Anomaly Detection Model: {model_name} from {table_name}...")
    
    df = execute_query(f"SELECT * FROM {table_name}")
    
    if df is None or len(df) == 0:
        logger.error(f"Error: No data found in {table_name}")
        return None
        
    df = df.dropna().reset_index(drop=True)
    
    if features is None:
        features = ['y', 'lag_1', 'lag_7', 'day_of_week']
        
    # Ensure features exist
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        print(f"Error: Missing features {missing_features} in {table_name}")
        return None
        
    X = df[features]
    
    with mlflow.start_run(run_name=model_name):
        model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
        
        mlflow.log_params(model.get_params())
        model.fit(X)
        
        predictions = model.predict(X)
        anomaly_count = (predictions == -1).sum()
        
        mlflow.log_metric("anomalies_detected_in_train", int(anomaly_count))
        
        print(f"{model_name} Trained. Found {anomaly_count} anomalies in training data.")
        
        mlflow.sklearn.log_model(model, model_name)
        
    return model

def train_all_anomaly_models():
    models = {}
    # 1. Revenue
    models['revenue'] = train_anomaly_model("features_forecasting", "anomaly_model_revenue", target_col='y', features=['y', 'lag_1', 'lag_7', 'day_of_week'])
    # 2. Inventory
    models['inventory'] = train_anomaly_model("features_inventory", "anomaly_model_inventory", target_col='y', features=['y', 'lag_1', 'lag_7', 'day_of_week'])
    # 3. Traffic (DAU)
    models['traffic'] = train_anomaly_model("features_customer_metrics_daily", "anomaly_model_traffic", target_col='dau', features=['dau', 'lag_1_dau', 'day_of_week'])
    # 4. Orders
    models['orders'] = train_anomaly_model("features_orders_daily", "anomaly_model_orders", target_col='y', features=['y', 'lag_1', 'lag_7', 'day_of_week'])
    # 5. Fraud (Canceled Orders & Freight)
    models['fraud'] = train_anomaly_model("features_fraud_daily", "anomaly_model_fraud", target_col='y', features=['y', 'freight', 'lag_1', 'lag_7', 'day_of_week'])
    
    return models

if __name__ == "__main__":
    import os
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "./mlruns")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("BI_Platform_Models")
    train_all_anomaly_models()
