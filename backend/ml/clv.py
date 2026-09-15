import pandas as pd
import xgboost as xgb
import mlflow
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from backend.database import execute_query

def train_clv_model():
    """Trains a regression model to predict Customer Lifetime Value."""
    print("Training CLV Model...")
    
    # We will use the features_clv table.
    # Normally CLV predicts FUTURE value based on PAST value.
    # For this demo, we'll try to predict total_spend based on recency and order count
    # to show the mechanics, even though it's somewhat circular in this simplified dataset.
    
    df = execute_query("SELECT * FROM features_clv")
    
    if df is None or len(df) == 0:
        print("Error: No data found in features_clv")
        return None
        
    df = df.dropna()
    
    # Features and Target
    features = ['total_orders', 'avg_order_value', 'recency_days']
    X = df[features]
    y = df['total_spend']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    import os
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "./mlruns")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("BI_Platform_Models")
    
    with mlflow.start_run(run_name="clv_prediction"):
        model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=4,
            random_state=42
        )
        
        mlflow.log_params(model.get_params())
        model.fit(X_train, y_train)
        
        preds = model.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        
        print(f"CLV Model Trained. RMSE: {rmse:.2f}, R2: {r2:.2f}")
        
        mlflow.xgboost.log_model(model, "clv_model")
        
    return model

if __name__ == "__main__":
    train_clv_model()
