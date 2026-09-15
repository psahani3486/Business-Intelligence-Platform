import pandas as pd
import xgboost as xgb
import mlflow
import os
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import numpy as np
from backend.database import execute_query

def train_forecasting_model():
    """Trains an XGBoost model for revenue forecasting."""
    print("Training Sales Forecasting Model...")
    
    # Get features from DuckDB
    df = execute_query("SELECT * FROM features_forecasting ORDER BY ds")
    
    if df is None or len(df) == 0:
        print("Error: No data found in features_forecasting")
        return None
    
    # Handle NaN values created by lag (first 30 days will have NaNs for lag_30)
    df = df.dropna().reset_index(drop=True)
    
    # Features and target
    features = ['lag_1', 'lag_7', 'lag_30', 'day_of_week', 'month']
    X = df[features]
    y = df['y']
    
    # Train/Test split (last 30 days for testing)
    train_size = len(df) - 30
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
    
    # Start MLflow run
    with mlflow.start_run(run_name="revenue_forecasting"):
        model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        # Log parameters
        mlflow.log_params(model.get_params())
        
        # Train model
        model.fit(X_train, y_train)
        
        # Predict and evaluate
        predictions = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mape = mean_absolute_percentage_error(y_test, predictions)
        
        # Log metrics
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mape", mape)
        
        print(f"Forecasting Model Trained. RMSE: {rmse:.2f}, MAPE: {mape:.2f}")
        
        # Log model
        mlflow.xgboost.log_model(model, "forecasting_model")
        
    return model

if __name__ == "__main__":
    train_forecasting_model()
