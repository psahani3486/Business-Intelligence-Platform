import pandas as pd
import xgboost as xgb
import mlflow
import shap
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from backend.database import execute_query
import joblib

def train_churn_model():
    """Trains a churn prediction model and computes SHAP values."""
    print("Training Churn Prediction Model...")
    
    # Load data from DuckDB
    df = execute_query("SELECT * FROM telco_churn")
    
    if df is None or len(df) == 0:
        print("Error: No data found in telco_churn table")
        return None

    # Preprocessing
    # Drop columns that shouldn't be features
    cols_to_drop = ['customerid', 'count', 'country', 'state', 'city', 'zip_code', 'lat_long', 'latitude', 'longitude', 'churn_label', 'churn_score', 'cltv', 'churn_reason']
    features = [c for c in df.columns if c not in cols_to_drop]
    
    X = df[features].copy()
    y = df['churn_value'].astype(int) # This is 1 for Yes, 0 for No
    
    # Encode categorical variables
    label_encoders = {}
    for col in X.select_dtypes(include=['object', 'category']).columns:
        le = LabelEncoder()
        # Handle potential NaNs before encoding
        X[col] = X[col].astype(str)
        X[col] = le.fit_transform(X[col])
        label_encoders[col] = le
        
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    import os
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "./mlruns")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("BI_Platform_Models")
    
    with mlflow.start_run(run_name="telco_churn"):
        model = xgb.XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=4,
            eval_metric='logloss',
            random_state=42
        )
        
        mlflow.log_params(model.get_params())
        
        model.fit(X_train, y_train)
        
        # Evaluate
        preds = model.predict(X_test)
        preds_proba = model.predict_proba(X_test)[:, 1]
        
        metrics = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds),
            "recall": recall_score(y_test, preds),
            "f1": f1_score(y_test, preds),
            "roc_auc": roc_auc_score(y_test, preds_proba)
        }
        
        for name, val in metrics.items():
            mlflow.log_metric(name, val)
            
        print(f"Churn Model Trained. ROC AUC: {metrics['roc_auc']:.2f}")
        
        # Log model
        mlflow.xgboost.log_model(model, "churn_model")
        
        # Save LabelEncoders for inference
        # In a real setup, we'd log this as an artifact to MLflow or a model registry
        os.makedirs(os.path.join(os.path.dirname(__file__), 'artifacts'), exist_ok=True)
        joblib.dump(label_encoders, os.path.join(os.path.dirname(__file__), 'artifacts/churn_encoders.joblib'))
        
    return model

if __name__ == "__main__":
    train_churn_model()
