import logging
import pandas as pd
import xgboost as xgb
import mlflow
import os
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from backend.database import execute_query

logger = logging.getLogger(__name__)

def train_advanced_forecast_model(table_name: str, model_name: str, target_col: str = 'y', features: list = None):
    """Trains an XGBoost model for time series forecasting."""
    logger.info(f"Training {model_name} from {table_name} (Target: {target_col})...")
    
    if features is None:
        features = ['lag_1', 'lag_7', 'day_of_week']
        
    df = execute_query(f"SELECT * FROM {table_name} ORDER BY ds")
    
    if df is None or len(df) == 0:
        logger.error(f"Error: No data found in {table_name}")
        return None
    
    df = df.dropna().reset_index(drop=True)
    
    # Ensure features exist
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        print(f"Error: Missing features {missing_features} in {table_name}")
        return None
        
    X = df[features]
    y = df[target_col]
    
    train_size = len(df) - 30
    if train_size <= 0:
        print("Not enough data to train.")
        return None
        
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
    
    with mlflow.start_run(run_name=model_name):
        model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=4,
            random_state=42
        )
        
        mlflow.log_params(model.get_params())
        model.fit(X_train, y_train)
        
        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        
        print(f"{model_name} Trained. RMSE: {rmse:.2f}, MAE: {mae:.2f}")
        mlflow.xgboost.log_model(model, model_name)
        
    return model

def train_inventory_model():
    return train_advanced_forecast_model("features_inventory", "inventory_forecast_model")

def train_customer_growth_models():
    models = {}
    table = "features_customer_metrics_daily"
    # New Customers
    models['new_customers'] = train_advanced_forecast_model(
        table, "customer_growth_new_xgb", target_col="new_customers", 
        features=["lag_1_new", "lag_7_new", "day_of_week"]
    )
    # Returning Customers
    models['returning_customers'] = train_advanced_forecast_model(
        table, "customer_growth_returning_xgb", target_col="returning_customers", 
        features=["lag_1_returning", "lag_7_returning", "day_of_week"]
    )
    # MAU
    models['mau'] = train_advanced_forecast_model(
        table, "customer_growth_mau_xgb", target_col="mau", 
        features=["lag_1_dau", "day_of_week"] # MAU relies heavily on recent DAU
    )
    # Growth Rate
    models['growth_rate'] = train_advanced_forecast_model(
        table, "customer_growth_rate_xgb", target_col="growth_rate", 
        features=["lag_1_new", "lag_1_returning", "day_of_week"]
    )
    return models

if __name__ == "__main__":
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "./mlruns")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("BI_Platform_Models")
    train_inventory_model()
    train_customer_growth_models()
